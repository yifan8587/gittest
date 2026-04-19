from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"users", views.UserViewSet, basename="user")

urlpatterns = [
    path("auth/login/", views.login, name="auth-login"),
    path("auth/register/", views.register, name="auth-register"),
    path("auth/me/", views.me, name="auth-me"),
    path("", include(router.urls)),
]
