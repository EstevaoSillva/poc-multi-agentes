from rest_framework import serializers
from agents_app.api.models import Session, Interaction, ToolExecution, PendingAction


class SerializerBase(serializers.HyperlinkedModelSerializer):
    # O HyperlinkedModelSerializer já adiciona o campo 'url' por padrão
    # Adicionamos o 'id' explicitamente pois ele não vem por padrão no Hyperlinked
    id = serializers.ReadOnlyField()

    class Meta:
        abstract = True

class SessionSerializer(SerializerBase):
    class Meta:
        model = Session
        fields = '__all__'
        # O DRF usará o nome da view '{model_name}-detail' para gerar a URL
        # Ex: 'session-detail'

class InteractionSerializer(SerializerBase):
    class Meta:
        model = Interaction
        fields = '__all__'

class ToolExecutionSerializer(SerializerBase):
    class Meta:
        model = ToolExecution
        fields = '__all__'

class PendingActionSerializer(SerializerBase):
    class Meta:
        model = PendingAction
        fields = '__all__'