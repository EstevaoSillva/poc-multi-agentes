from rest_framework import viewsets, permissions
from agents_app.api.models import Session, Interaction, ToolExecution, PendingAction
from agents_app.api.serializers import (
    SessionSerializer,
    InteractionSerializer,
    ToolExecutionSerializer,
    PendingActionSerializer
)

class SessionViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite visualizar ou editar sessões.
    """
    queryset = Session.objects.all().order_by('-last_interaction_at')
    serializer_class = SessionSerializer
    # Se quiser restringir acesso:
    # permission_classes = [permissions.IsAuthenticated]

class InteractionViewSet(viewsets.ModelViewSet):
    queryset = Interaction.objects.all().order_by('-created_at')
    serializer_class = InteractionSerializer

class ToolExecutionViewSet(viewsets.ModelViewSet):
    queryset = ToolExecution.objects.all()
    serializer_class = ToolExecutionSerializer

class PendingActionViewSet(viewsets.ModelViewSet):
    queryset = PendingAction.objects.all()
    serializer_class = PendingActionSerializer