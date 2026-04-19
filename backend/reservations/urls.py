from django.urls import path

from .views import (
    AppointmentTypeListView,
    ReservationDetailView,
    ReservationListCreateView,
    VisitCancelView,
    VisitDetailView,
    VisitListView,
    VisitNoteUpdateView,
    VisitStatusUpdateView,
)

urlpatterns = [
    path(
        "v1/appointment-types",
        AppointmentTypeListView.as_view(),
        name="appointment-type-list",
    ),
    path("v1/reservations", ReservationListCreateView.as_view(), name="reservation-list"),
    path(
        "v1/reservations/<uuid:series_id>",
        ReservationDetailView.as_view(),
        name="reservation-detail",
    ),
    path("v1/visits", VisitListView.as_view(), name="visit-list"),
    path("v1/visits/<uuid:appointment_id>", VisitDetailView.as_view(), name="visit-detail"),
    path(
        "v1/visits/<uuid:appointment_id>/status",
        VisitStatusUpdateView.as_view(),
        name="visit-status",
    ),
    path(
        "v1/visits/<uuid:appointment_id>/note",
        VisitNoteUpdateView.as_view(),
        name="visit-note",
    ),
    path(
        "v1/visits/<uuid:appointment_id>/cancel",
        VisitCancelView.as_view(),
        name="visit-cancel",
    ),
]
