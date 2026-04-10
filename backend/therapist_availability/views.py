from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet
from users.permissions import IsTherapist

from .models import Therapist
from .serializers import TherapistSerializer


class TherapistViewSet(ReadOnlyModelViewSet):
    serializer_class = TherapistSerializer
    queryset = Therapist.objects.select_related("therapist", "office")
    permission_classes = [IsAuthenticated, IsTherapist]
