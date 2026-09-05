from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.profiles.views import UserProfileViewSet

app_name = "profiles"

router = DefaultRouter()
router.register(r"user-profiles", UserProfileViewSet, basename="user-profiles")

urlpatterns = [
    path("", include(router.urls)),
]
