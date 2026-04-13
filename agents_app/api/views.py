import json
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from agents_app.agents import app_ideation_agent, planner_agent
from agents_app.api.models import Session, Interaction, ToolExecution, PendingAction
from agents_app.api.serializers import (
    SessionSerializer,
    InteractionSerializer,
    ToolExecutionSerializer,
    PendingActionSerializer,
    InteractionInputSerializer
)
from agents_app.orchestrator import CopilotOrchestrator
from agents_app.utils import safe_json_parse, extract_text_from_run

User = get_user_model()

class CopilotStartAPIView(APIView):
    """
    Endpoint inicial do Copilot.
    Apenas inicia a conversa.
    """

    def get(self, request):
        return Response({
            "message": "Fala BitDev, qual aplicação vamos fazer hoje?"
        })

class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all().order_by("-last_interaction_at")
    serializer_class = SessionSerializer

    @action(detail=True, methods=["post"], serializer_class=InteractionInputSerializer)
    def interact(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_input = serializer.validated_data["prompt"]

        orchestrator = CopilotOrchestrator(
            workspace_path=settings.WORKSPACE_PATH
        )

        result = orchestrator.run(
            session_id=pk,
            user_input=user_input
        )

        return Response(result)


class InteractionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Interaction.objects.all().order_by("-created_at")
    serializer_class = InteractionSerializer


class ToolExecutionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ToolExecution.objects.all()
    serializer_class = ToolExecutionSerializer


class PendingActionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PendingAction.objects.all()
    serializer_class = PendingActionSerializer

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        pending = self.get_object()

        orchestrator = CopilotOrchestrator(
            workspace_path=settings.WORKSPACE_PATH
        )

        orchestrator.session_workspace = orchestrator._ensure_session_workspace(pending.session.id)
        orchestrator._ensure_tool_broker(
            session_id=pending.session.id,
            user_id=getattr(pending.session, "created_by_user_id", None),
        )
        result = orchestrator.execute_tools(
            {
                "tools": [{
                    "name": pending.tool_name,
                    "args": pending.tool_input
                }]
            },
            approved=True,
        )

        for execution_record in orchestrator.tool_broker.get_execution_log():
            if pending.interaction_id:
                ToolExecution.objects.create(
                    interaction=pending.interaction,
                    tool_name=execution_record.tool_name,
                    input_payload=execution_record.args,
                    output_payload=execution_record.result or {},
                )

        has_error = any(item.get("status") != "success" for item in result)
        pending.delete()

        return Response({
            "status": "executed" if not has_error else "execution_error",
            "result": result
        })

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        pending = self.get_object()
        pending.delete()

        return Response({
            "status": "rejected"
        })




class IdeationAPIView(APIView):
    """
    Interpreta a ideia do usuário e cria automaticamente uma Session.
    """

    def post(self, request):
        user_prompt = request.data.get("prompt")

        if not user_prompt:
            return Response(
                {"error": "prompt is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ⚠️ temporário — depois vem auth real
        user = User.objects.first()
        if not user:
            return Response(
                {"error": "No user found. Create a user first."},
                status=status.HTTP_400_BAD_REQUEST
            )

        output = app_ideation_agent.run(user_prompt)
        raw_text = output.content if hasattr(output, "content") else str(output)
        try:
            ideation = json.loads(raw_text)
        except json.JSONDecodeError:
            # If we couldn't parse JSON, coerce into a minimal dict so Session.context
            # is always a JSON-serializable object. Preserve raw output in `raw_ideation`.
            ideation = {
                "app_name": (user_prompt.split('\n', 1)[0][:30] if user_prompt else "App"),
                "category": "unspecified",
                "description": raw_text.strip().replace('\n', ' '),
                "suggested_stack": {
                    "backend": "fastapi",
                    "frontend": "html_css_js",
                    "database": "postgres"
                },
                "raw_ideation": raw_text,
            }

        # Normalize ideation to ensure required keys exist and context is JSON-serializable
        app_name = ideation.get("app_name") or (user_prompt.split('\n', 1)[0][:30] if user_prompt else "App")
        category = ideation.get("category") or "unspecified"
        description_text = ideation.get("description") or raw_text.strip().replace('\n', ' ')
        suggested_stack = ideation.get("suggested_stack") or {
            "backend": "fastapi",
            "frontend": "html_css_js",
            "database": "postgres",
        }

        # Ensure suggested_stack has recommended/options shape if model returned the new format
        if isinstance(suggested_stack, dict):
            # if the shape is {backend: {recommended: ...}} extract recommended values when possible
            backend_field = suggested_stack.get("backend")
            if isinstance(backend_field, dict) and "recommended" in backend_field:
                suggested_stack_backend = backend_field.get("recommended")
            else:
                suggested_stack_backend = backend_field

            frontend_field = suggested_stack.get("frontend")
            if isinstance(frontend_field, dict) and "recommended" in frontend_field:
                suggested_stack_frontend = frontend_field.get("recommended")
            else:
                suggested_stack_frontend = frontend_field

            # rebuild minimal suggested_stack
            suggested_stack = {
                "backend": suggested_stack_backend or "fastapi",
                "frontend": suggested_stack_frontend or "html_css_js",
                "database": "postgres",
            }

        # 🔥 CRIAÇÃO DA SESSION — always save `context` as a JSON-serializable dict
        session = Session.objects.create(
            user=user,
            title=app_name,
            context={
                "category": category,
                "description": description_text,
                "suggested_stack": suggested_stack,
                "original_prompt": user_prompt,
            }
        )

        return Response(
            {
                "session_id": session.id,
                "ideation": ideation
            },
            status=status.HTTP_201_CREATED
        )


class SessionStartAPIView(APIView):

    def post(self, request, session_id):
        session = Session.objects.get(id=session_id)

        context = session.context

        planner_output = planner_agent.run(
            f"""
                Project name: {session.title}
                
                Context:
                {json.dumps(context, indent=2)}
                
                Plan the initial project structure.
                """
        )

        raw = extract_text_from_run(planner_output)

        plan = safe_json_parse(raw)

        # Workspace
        base_path = Path(settings.WORKSPACE_PATH) / "sessions" / f"session_{session.id}"
        base_path.mkdir(parents=True, exist_ok=True)

        progress = []

        if "structure" in plan and isinstance(plan["structure"], dict):
            for root, dirs in plan["structure"].items():
                root_path = base_path / root
                root_path.mkdir(exist_ok=True)
                progress.append(f"Created {root}/")

                for d in dirs:
                    (root_path / d).mkdir(exist_ok=True)
                    progress.append(f"Created {root}/{d}/")
        elif "execution_plan" in plan and isinstance(plan["execution_plan"], list):
            created_dirs = set()
            for step in plan["execution_plan"]:
                for output_path in step.get("outputs", []):
                    output = Path(output_path)
                    parent = output.parent if output.suffix else output
                    if not str(parent) or str(parent) == ".":
                        continue
                    target = base_path / parent
                    if target not in created_dirs:
                        target.mkdir(parents=True, exist_ok=True)
                        created_dirs.add(target)
                        progress.append(f"Created {target.relative_to(base_path)}/")
        else:
            return Response(
                {"error": "Planner returned unsupported schema"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {
                "message": "Iniciando as tasks...",
                "progress": progress,
                "project_path": str(base_path.resolve()),
                "next_steps": plan.get("next_steps") or [
                    step.get("title")
                    for step in plan.get("execution_plan", [])
                    if isinstance(step, dict) and step.get("title")
                ]
            },
            status=status.HTTP_200_OK
        )


class CopilotAPIView(APIView):
    """
    Entrada única do usuário (prompt → projeto criado)
    """

    def post(self, request):
        prompt = request.data.get("prompt")
        if not prompt:
            return Response(
                {"error": "prompt é obrigatório"},
                status=400
            )

        # 1. Ideation
        ideation_raw = app_ideation_agent.run(prompt)
        ideation_text = extract_text_from_run(ideation_raw)
        ideation = safe_json_parse(ideation_text)

        # 2. Define o usuário (pega o autenticado ou o primeiro do banco para evitar erro)
        user = request.user if request.user.is_authenticated else User.objects.first()

        if not user:
            return Response(
                {"error": "Nenhum usuário encontrado no sistema para atribuir a sessão."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. Cria sessão
        session = Session.objects.create(
            title=ideation["app_name"],
            context={
                **ideation,
                "original_prompt": prompt
            },
            user=user
        )

        # 4. Start (planner + tools)
        orchestrator = CopilotOrchestrator(
            workspace_path=settings.WORKSPACE_PATH
        )

        start_result = orchestrator.start(session.id)

        return Response({
            "message": "Iniciando as tasks...",
            "session_id": session.id,
            "ideation": ideation,
            **start_result
        })
