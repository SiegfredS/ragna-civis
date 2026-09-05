from django.contrib.auth import authenticate, password_validation
from django.contrib.auth.base_user import AbstractBaseUser
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.users.models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
    )

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "middle_name", "last_name", "password")
        extra_kwargs = {
            "email": {"required": True, "allow_null": False, "allow_blank": False},
            "middle_name": {"required": False},
        }

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(_("A user with that email already exists."))
        return value

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(_("A user with that username already exists."))
        return value

    def validate(self, attrs):
        user = User(
            username=attrs["username"],
            email=attrs["email"],
            first_name=attrs["first_name"],
            middle_name=attrs.get("middle_name", ""),
            last_name=attrs["last_name"],
        )
        try:
            password_validation.validate_password(password=attrs["password"], user=user)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": list(exc.messages)}) from exc
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    authenticated_user: AbstractBaseUser | None = None

    username = serializers.CharField(write_only=True)
    password = serializers.CharField(
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
    )

    default_error_messages = {
        "invalid_credentials": _("Unable to log in with provided credentials."),
        "missing_credentials": _('Must include "username" and "password".'),
    }

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        if not username or not password:
            raise serializers.ValidationError(self.error_messages["missing_credentials"], code="authorization")

        login_user = (
            User.objects.filter(Q(username__iexact=username) | Q(email__iexact=username)).only("username").first()
        )
        auth_username = login_user.username if login_user is not None else username

        user = authenticate(
            request=self.context.get("request"),
            username=auth_username,
            password=password,
        )

        if user is None:
            raise serializers.ValidationError(self.error_messages["invalid_credentials"], code="authorization")

        self.authenticated_user = user
        return attrs

    def get_authenticated_user(self) -> AbstractBaseUser:
        if self.authenticated_user is None:
            raise AssertionError("LoginSerializer must be validated before retrieving the authenticated user.")
        return self.authenticated_user
