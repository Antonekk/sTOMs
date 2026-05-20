from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification
from .serializers import NotificationSerializer


class NotificationPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 50


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = NotificationPagination

    @extend_schema(
        responses=NotificationSerializer(many=True),
        operation_id="v1_notifications_list",
    )
    def get(self, request):
        queryset = Notification.objects.filter(user=request.user).order_by("-creation_timestamp")
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = NotificationSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class NotificationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, request, notification_id):
        return get_object_or_404(
            Notification,
            id=notification_id,
            user=request.user,
        )

    @extend_schema(
        responses=NotificationSerializer,
        operation_id="v1_notifications_retrieve",
    )
    def get(self, request, notification_id):
        notification = self.get_object(request, notification_id)
        serializer = NotificationSerializer(notification)
        return Response(serializer.data)


class NotificationMarkReadView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=None,
        responses=NotificationSerializer,
        operation_id="v1_notifications_mark_read",
    )
    def patch(self, request, notification_id):
        notification = get_object_or_404(
            Notification,
            id=notification_id,
            user=request.user,
        )
        if not notification.is_read:
            notification.is_read = True
            notification.save(update_fields=["is_read"])
        return Response(NotificationSerializer(notification).data)


class NotificationMarkAllReadView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=None,
        responses={204: None},
        operation_id="v1_notifications_mark_all_read",
    )
    def patch(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response(status=status.HTTP_204_NO_CONTENT)
