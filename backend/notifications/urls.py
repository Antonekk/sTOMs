from django.urls import path

from .views import (
    NotificationDetailView,
    NotificationListView,
    NotificationMarkAllReadView,
    NotificationMarkReadView,
)

urlpatterns = [
    path("v1/notifications", NotificationListView.as_view(), name="notification-list"),
    path(
        "v1/notifications/read",
        NotificationMarkAllReadView.as_view(),
        name="notification-mark-all-read",
    ),
    path(
        "v1/notifications/<uuid:notification_id>",
        NotificationDetailView.as_view(),
        name="notification-detail",
    ),
    path(
        "v1/notifications/<uuid:notification_id>/read",
        NotificationMarkReadView.as_view(),
        name="notification-mark-read",
    ),
]
