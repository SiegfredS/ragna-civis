from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.civic_assistant.views import CivicAssistantViewSet

app_name = "civic_assistant"

router = DefaultRouter()
router.register(r"civic-assistant", CivicAssistantViewSet, basename="civic-assistant")

urlpatterns = [
    path("", include(router.urls)),
]
