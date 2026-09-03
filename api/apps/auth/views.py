from typing import cast

from knox.views import LoginView as KnoxLoginView
from knox.views import LogoutAllView as KnoxLogoutAllView
from knox.views import LogoutView as KnoxLogoutView
from rest_framework.permissions import AllowAny

from apps.users.serializers import UserSerializer

from .serializers import LoginSerializer, RegisterSerializer


class RegisterView(KnoxLoginView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user = serializer.save()
        return super().post(request, *args, **kwargs)

    def get_post_response_data(self, request, token, instance):
        data = super().get_post_response_data(request, token, instance)
        data["user"] = UserSerializer(request.user, context={"request": request}).data
        return data


class LoginView(KnoxLoginView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = cast(LoginSerializer, LoginSerializer(data=request.data, context={"request": request}))
        serializer.is_valid(raise_exception=True)
        request.user = serializer.get_authenticated_user()
        return super().post(request, *args, **kwargs)

    def get_post_response_data(self, request, token, instance):
        data = super().get_post_response_data(request, token, instance)
        data["user"] = UserSerializer(request.user, context={"request": request}).data
        return data


class LogoutView(KnoxLogoutView):
    pass


class LogoutAllView(KnoxLogoutAllView):
    pass
