from django.urls import path

from .views import (
    NotificationDetailView,
    NotificationListView,
    NotificationMarkAllReadView,
    NotificationMarkReadView,
)

urlpatterns = [
    path("notifications", NotificationListView.as_view(), name="notification-list"),
    path(
        "notifications/read",
        NotificationMarkAllReadView.as_view(),
        name="notification-mark-all-read",
    ),
    path(
        "notifications/<uuid:notification_id>",
        NotificationDetailView.as_view(),
        name="notification-detail",
    ),
    path(
        "notifications/<uuid:notification_id>/read",
        NotificationMarkReadView.as_view(),
        name="notification-mark-read",
    ),
]
