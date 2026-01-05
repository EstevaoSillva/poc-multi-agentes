import json
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from agents_app.agents.app_ideation_agent import app_ideation_agent
from agents_app.agents.planner_agent import planner_agent
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
        user_input = request.data.get("prompt")
        if not user_input:
            return Response(
                {"error": "O campo 'prompt' é obrigatório no corpo da requisição."},
                status=400
            )

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

        result = orchestrator.execute_tools({
            "tools": [{
                "name": pending.tool_name,
                "args": pending.tool_input
            }]
        })

        pending.delete()

        return Response({
            "status": "executed",
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
            return Response(
                {
                    "error": "LLM did not return valid JSON",
                    "raw_output": raw_text
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # 🔥 CRIAÇÃO DA SESSION
        session = Session.objects.create(
            user=user,
            title=ideation["app_name"],
            context={
                "category": ideation["category"],
                "description": ideation["description"],
                "suggested_stack": ideation["suggested_stack"],
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
        base_path = Path("workspace") / f"session_{session.id}"
        base_path.mkdir(parents=True, exist_ok=True)

        progress = []

        for root, dirs in plan["structure"].items():
            root_path = base_path / root
            root_path.mkdir(exist_ok=True)
            progress.append(f"Created {root}/")

            for d in dirs:
                (root_path / d).mkdir(exist_ok=True)
                progress.append(f"Created {root}/{d}/")

        return Response(
            {
                "message": "Iniciando as tasks...",
                "progress": progress,
                "project_path": str(base_path.resolve()),
                "next_steps": plan["next_steps"]
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