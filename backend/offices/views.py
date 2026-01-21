from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Localization, Office
from .serializers import LocalizationSerializer, OfficeSerializer


class LocalizationViewSet(ReadOnlyModelViewSet):
    queryset = Localization.objects.prefetch_related("offices").all()
    serializer_class = LocalizationSerializer
    permission_classes = [AllowAny]


class OfficeViewSet(ReadOnlyModelViewSet):
    queryset = Office.objects.select_related("localization").all()
    serializer_class = OfficeSerializer
    permission_classes = [AllowAny]
