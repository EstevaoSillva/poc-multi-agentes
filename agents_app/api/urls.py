from django.urls import path, include
from rest_framework.routers import DefaultRouter

from agents_app.api import views
from agents_app.api.views import SessionStartAPIView, CopilotAPIView

router = DefaultRouter()
router.register(r'sessions', views.SessionViewSet)
router.register(r'interactions', views.InteractionViewSet)
router.register(r'tool-executions', views.ToolExecutionViewSet)
router.register(r'pending-actions', views.PendingActionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path("ideation/", views.IdeationAPIView.as_view(), name="ideation"),
    path('copilot/start/', views.CopilotStartAPIView.as_view(), name='copilot-start'),
    path("sessions/<int:session_id>/start/", SessionStartAPIView.as_view()),
    path("copilot/", CopilotAPIView.as_view()),
]