from django.urls import path, include
from rest_framework.routers import DefaultRouter

from agents_app.api import views

# Cria um roteador e registra nossos viewsets.
router = DefaultRouter()
router.register(r'sessions', views.SessionViewSet)
router.register(r'interactions', views.InteractionViewSet)
router.register(r'tool-executions', views.ToolExecutionViewSet)
router.register(r'pending-actions', views.PendingActionViewSet)

# As URLs da API são determinadas automaticamente pelo roteador.
urlpatterns = [
    path('', include(router.urls)),
    path("ideation/", views.IdeationAPIView.as_view()),
]