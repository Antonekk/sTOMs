from django.urls import re_path
from djoser.views import UserViewSet
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

router = DefaultRouter()
router.register("users", UserViewSet, basename="user")

urlpatterns = [
    re_path(
        r"^jwt/create/?$",
        TokenObtainPairView.as_view(),
        name="jwt-create",
    ),
    re_path(
        r"^jwt/refresh/?$",
        TokenRefreshView.as_view(),
        name="jwt-refresh",
    ),
    re_path(
        r"^jwt/verify/?$",
        TokenVerifyView.as_view(),
        name="jwt-verify",
    ),
    *router.urls,
]
