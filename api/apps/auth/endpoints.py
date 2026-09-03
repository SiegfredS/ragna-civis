from django.urls import reverse

REGISTER_URL = reverse("auth:register")
LOGIN_URL = reverse("auth:login")
LOGOUT_URL = reverse("auth:logout")
LOGOUT_ALL_URL = reverse("auth:logout-all")
