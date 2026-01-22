from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .models import AppUser, Patient, Therapist
from .permissions import IsTherapist, PatientPermissions
from .serializers import PatientSerializer, TherapistSerializer


class PatientViewSet(ModelViewSet):
    serializer_class = PatientSerializer
    permission_classes = [PatientPermissions]

    def get_queryset(self):
        user = self.request.user

        if user.role == AppUser.Role.THERAPIST:
            return Patient.objects.all()

        return Patient.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TherapistViewSet(ReadOnlyModelViewSet):
    serializer_class = TherapistSerializer
    queryset = Therapist.objects.select_related("user", "office")
    permission_classes = [IsAuthenticated, IsTherapist]
