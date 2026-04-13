from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    AvailabilityListView,
    SelfScheduleOverrideDetailView,
    SelfScheduleOverrideView,
    SelfScheduleView,
    TherapistViewSet,
)

router = DefaultRouter()
router.register("therapists", TherapistViewSet, basename="therapist")

urlpatterns = [
    path(
        "therapists/self/schedule",
        SelfScheduleView.as_view(),
        name="therapist-self-schedule",
    ),
    path(
        "therapists/self/schedule/override",
        SelfScheduleOverrideView.as_view(),
        name="therapist-self-schedule-override",
    ),
    path(
        "therapists/self/schedule/override/<uuid:block_id>",
        SelfScheduleOverrideDetailView.as_view(),
        name="therapist-self-schedule-override-detail",
    ),
    path("availability", AvailabilityListView.as_view(), name="availability"),
    *router.urls,
]
