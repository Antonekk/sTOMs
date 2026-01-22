from rest_framework.routers import DefaultRouter

from .views import TherapistScheduleOverride, TherapistScheduleView

router = DefaultRouter()
router.register("schedule", TherapistScheduleView, basename="therapist-schedule")
router.register(
    "schedule/override",
    TherapistScheduleOverride,
    basename="therapist-schedule-override",
)

urlpatterns = router.urls
