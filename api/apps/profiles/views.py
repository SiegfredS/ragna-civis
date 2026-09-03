from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.utils.views import ActionSerializerClassMixin

from .models import UserProfile
from .serializers import UserProfileSerializer


class UserProfileViewSet(  # pyright: ignore[reportIncompatibleMethodOverride]
    ActionSerializerClassMixin, viewsets.GenericViewSet
):
    queryset = UserProfile.objects.select_related("user")
    serializer_class = UserProfileSerializer
    action_serializers = {
        ActionSerializerClassMixin.DEFAULT: UserProfileSerializer,
        "me": UserProfileSerializer,
    }

    @action(detail=False, methods=["get"])
    def me(self, request):
        user_profile = UserProfile.objects.select_related("user").get(user=request.user)
        self.check_object_permissions(request, user_profile)
        serializer = self.get_serializer(user_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
