from constance import config
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ConfigSerializer


@extend_schema(responses=ConfigSerializer)
class ConfigView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(
            {
                "appointment_generation_days": config.APPOINTMENT_GENERATION_DAYS,
                "appointment_booking_days": config.APPOINTMENT_BOOKING_DAYS,
                "cancellation_window_hours": config.CANCELLATION_WINDOW_HOURS,
            }
        )
