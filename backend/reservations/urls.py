from django.urls import path

from .views import (
    AppointmentTypeListView,
    BookableSlotListView,
    BookableTimeOptionsView,
    ReservationDetailView,
    ReservationListCreateView,
    TherapistListView,
    VisitCancelView,
    VisitDetailView,
    VisitListView,
    VisitNoteUpdateView,
    VisitStatusUpdateView,
)

urlpatterns = [
    path(
        "appointment-types",
        AppointmentTypeListView.as_view(),
        name="appointment-type-list",
    ),
    path(
        "therapists",
        TherapistListView.as_view(),
        name="booking-therapist-list",
    ),
    path(
        "reservations/slots/time-options",
        BookableTimeOptionsView.as_view(),
        name="bookable-time-options",
    ),
    path(
        "reservations/slots",
        BookableSlotListView.as_view(),
        name="bookable-slot-list",
    ),
    path("reservations", ReservationListCreateView.as_view(), name="reservation-list"),
    path(
        "reservations/<uuid:series_id>",
        ReservationDetailView.as_view(),
        name="reservation-detail",
    ),
    path("visits", VisitListView.as_view(), name="visit-list"),
    path("visits/<uuid:appointment_id>", VisitDetailView.as_view(), name="visit-detail"),
    path(
        "visits/<uuid:appointment_id>/status",
        VisitStatusUpdateView.as_view(),
        name="visit-status",
    ),
    path(
        "visits/<uuid:appointment_id>/note",
        VisitNoteUpdateView.as_view(),
        name="visit-note",
    ),
    path(
        "visits/<uuid:appointment_id>/cancel",
        VisitCancelView.as_view(),
        name="visit-cancel",
    ),
]
