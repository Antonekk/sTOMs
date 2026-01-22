from rest_framework.routers import DefaultRouter

from .views import PatientViewSet, TherapistViewSet

router = DefaultRouter()
router.register("patients", PatientViewSet, basename="patient")
router.register("therapists", TherapistViewSet, basename="therapist")

urlpatterns = router.urls
