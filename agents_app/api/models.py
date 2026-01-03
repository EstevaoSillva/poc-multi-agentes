from django.conf import settings
from django.db import models
from simple_history.models import HistoricalRecords


class ModelBase(models.Model):
    id = models.BigAutoField(
        db_column='id',
        null=False,
        primary_key=True,
        verbose_name='Id'
    )
    created_at = models.DateTimeField(
        db_column='dt_created_at',
        auto_now_add=True,
        null=True,
        verbose_name='Created at'
    )
    modified_at = models.DateTimeField(
        db_column='dt_modified_at',
        auto_now=True,
        null=True,
        verbose_name='Modified at'
    )
    active = models.BooleanField(
        db_column='cs_active',
        null=False,
        default=True,
        verbose_name='Active',
    )

    class Meta:
        abstract = True
        managed = True


class Session(ModelBase):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='User',
    )
    context = models.JSONField(default=dict, blank=True)
    title = models.CharField(max_length=255, verbose_name='Title')
    last_interaction_at = models.DateTimeField(auto_now=True, verbose_name='Last_interaction_at')
    history = HistoricalRecords(table_name='"history"."session_history"')

    def __str__(self):
        return f"{self.user} - {self.title}"

    class Meta:
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["last_interaction_at"]),
        ]


class Interaction(ModelBase):
    class Intent(models.TextChoices):
        READ = "READ"
        GENERATE = "GENERATE"
        REVIEW = "REVIEW"
        MODIFY = "MODIFY"
        DELETE = "DELETE"
        UNKNOWN = "UNKNOWN"
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="interactions", verbose_name='Session')
    user_prompt = models.TextField(verbose_name='User prompt')
    intent = models.CharField(
        max_length=20,
        choices=Intent.choices,
        default=Intent.UNKNOWN,
        verbose_name='Intent'
    )
    planner_decision = models.JSONField()
    llm_response = models.TextField()
    history = HistoricalRecords(table_name='"history"."interaction_history"')

    class Meta:
        indexes = [
            models.Index(fields=["session"]),
            models.Index(fields=["intent"]),
            models.Index(fields=["created_at"]),
        ]


class ToolExecution(ModelBase):
    interaction = models.ForeignKey(
        Interaction,
        on_delete=models.CASCADE,
        related_name="tools",
        verbose_name = 'Interaction',
    )
    tool_name = models.CharField(max_length=100, verbose_name='Tool name',)
    input_payload = models.JSONField()
    output_payload = models.JSONField()
    history = HistoricalRecords(table_name='"history"."tool_execution_history"')


class PendingAction(ModelBase):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="pending_actions", verbose_name='Session')
    interaction = models.ForeignKey(
        Interaction, on_delete=models.CASCADE, null=True, blank=True, related_name="pending_actions", verbose_name='Interaction')

    tool_name = models.CharField(max_length=100, verbose_name='Tool name')
    tool_input = models.JSONField()
    description = models.TextField()

    confirmed = models.BooleanField(default=False)
    executed = models.BooleanField(default=False)
    history = HistoricalRecords(table_name='"history"."pending_action_history"')
