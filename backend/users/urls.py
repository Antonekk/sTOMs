from django.urls import re_path
from rest_framework.routers import DefaultRouter

from .views import (
    ThrottledTokenObtainPairView,
    ThrottledTokenRefreshView,
    ThrottledTokenVerifyView,
    UserViewSet,
)

router = DefaultRouter()
router.register("users", UserViewSet, basename="user")

urlpatterns = [
    re_path(
        r"^jwt/create/?$",
        ThrottledTokenObtainPairView.as_view(),
        name="jwt-create",
    ),
    re_path(
        r"^jwt/refresh/?$",
        ThrottledTokenRefreshView.as_view(),
        name="jwt-refresh",
    ),
    re_path(
        r"^jwt/verify/?$",
        ThrottledTokenVerifyView.as_view(),
        name="jwt-verify",
    ),
    *router.urls,
]
