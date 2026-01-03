import json

from agents_app.utils import extract_json
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from agents_app.agents.app_ideation_agent import app_ideation_agent
from agents_app.api.models import Session, Interaction, ToolExecution, PendingAction
from agents_app.api.serializers import (
    SessionSerializer,
    InteractionSerializer,
    ToolExecutionSerializer,
    PendingActionSerializer,
    InteractionInputSerializer,
    IdeationInputSerializer
)
from agents_app.orchestrator import CopilotOrchestrator


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
        serializer = IdeationInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_prompt = serializer.validated_data["prompt"]

        # 🔹 Executa o agente
        run_output = app_ideation_agent.run(user_prompt)

        # 🔹 Extrai texto
        try:
            try:
                ideation_result = extract_json(run_output.content)
            except Exception as e:
                return Response(
                    {
                        "error": "Failed to parse LLM JSON",
                        "raw_output": run_output.content,
                        "details": str(e),
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        except json.JSONDecodeError:
            return Response(
                {
                    "error": "LLM did not return valid JSON",
                    "raw_output": run_output.content
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # 🔹 Cria Session automaticamente
        session = Session.objects.create(
            title=ideation_result["app_name"],
            context={
                "category": ideation_result["category"],
                "description": ideation_result["description"],
                "suggested_stack": ideation_result["suggested_stack"],
                "original_prompt": user_prompt,
            }
        )

        return Response(
            {
                "session_id": session.id,
                "ideation": ideation_result
            },
            status=status.HTTP_201_CREATED
        )