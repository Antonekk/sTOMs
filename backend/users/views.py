"""
Account and authentication views (Djoser + JWT) wrapped with throttling.
"""

from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# Djoser UserViewSet actions for anonymous requests
_ANON_SENSITIVE_ACTIONS = {
    "create": "user_register",
    "activation": "user_activation",
    "resend_activation": "user_email",
    "reset_password": "user_email",
    "reset_password_confirm": "user_password_confirm",
    "reset_username": "user_email",
    "reset_username_confirm": "user_password_confirm",
}

# Djoser UserViewSet actions for authenticated requests
_AUTHENTICATED_ACTIONS = {
    "me",
    "retrieve",
    "update",
    "partial_update",
    "destroy",
    "list",
    "set_password",
    "set_username",
}


class UserViewSet(DjoserUserViewSet):
    def get_throttles(self):
        if self.action in _ANON_SENSITIVE_ACTIONS:
            self.throttle_scope = _ANON_SENSITIVE_ACTIONS[self.action]
            return [ScopedRateThrottle()]
        if self.action in _AUTHENTICATED_ACTIONS:
            self.throttle_scope = "user_authenticated"
            return [ScopedRateThrottle()]
        return super().get_throttles()


# JWT authentication endpoints with throttling
class ThrottledTokenObtainPairView(TokenObtainPairView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"


class ThrottledTokenRefreshView(TokenRefreshView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "jwt_refresh"


class ThrottledTokenVerifyView(TokenVerifyView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "jwt_verify"
