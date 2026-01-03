from rest_framework import serializers
from agents_app.api.models import Session, Interaction, ToolExecution, PendingAction


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'
        # O DRF usará o nome da view '{model_name}-detail' para gerar a URL
        # Ex: 'session-detail'


class InteractionInputSerializer(serializers.Serializer):
    user_prompt = serializers.CharField(
        help_text="Comando ou solicitação para o agente Copilot."
    )


class InteractionSerializer(serializers.ModelSerializer):
    user_prompt = serializers.CharField(help_text="Texto da sua solicitação para o agente.")
    class Meta:
        model = Interaction
        fields = '__all__'

class ToolExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ToolExecution
        fields = '__all__'

class PendingActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PendingAction
        fields = '__all__'


class IdeationInputSerializer(serializers.Serializer):
    prompt = serializers.CharField(
        help_text="Descreva a aplicação que você deseja criar."
    )