from rest_framework.routers import DefaultRouter

from .views import TherapistViewSet

router = DefaultRouter()
router.register("therapists", TherapistViewSet, basename="therapist")

urlpatterns = router.urls
