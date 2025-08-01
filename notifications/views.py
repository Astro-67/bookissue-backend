from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Notification
from .serializers import (
    NotificationSerializer, 
    NotificationListSerializer, 
    MarkNotificationReadSerializer
)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for handling notifications
    - List user's notifications
    - Retrieve specific notification
    - Mark notifications as read
    - Get unread count
    """
    serializer_class = NotificationListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Return notifications for the current user only
        """
        return Notification.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action == 'retrieve':
            return NotificationSerializer
        return NotificationListSerializer

    @swagger_auto_schema(
        operation_description="Get count of unread notifications",
        responses={
            200: openapi.Response(
                description="Unread notification count",
                examples={
                    "application/json": {
                        "unread_count": 5
                    }
                }
            )
        }
    )
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """
        Get count of unread notifications for the current user
        """
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'unread_count': count})

    @swagger_auto_schema(
        operation_description="Mark notifications as read",
        request_body=MarkNotificationReadSerializer,
        responses={
            200: openapi.Response(
                description="Notifications marked as read successfully",
                examples={
                    "application/json": {
                        "message": "Notifications marked as read successfully",
                        "updated_count": 3
                    }
                }
            ),
            400: openapi.Response(description="Bad request")
        }
    )
    @action(detail=False, methods=['post'])
    def mark_read(self, request):
        """
        Mark one or more notifications as read
        If no specific IDs provided, mark all as read
        """
        serializer = MarkNotificationReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        notification_ids = serializer.validated_data.get('notification_ids')
        
        if notification_ids:
            # Mark specific notifications as read
            queryset = self.get_queryset().filter(
                id__in=notification_ids,
                is_read=False
            )
        else:
            # Mark all unread notifications as read
            queryset = self.get_queryset().filter(is_read=False)
        
        updated_count = queryset.update(is_read=True)
        
        return Response({
            'message': 'Notifications marked as read successfully',
            'updated_count': updated_count
        })

    @swagger_auto_schema(
        operation_description="Mark all notifications as read",
        responses={
            200: openapi.Response(
                description="All notifications marked as read successfully",
                examples={
                    "application/json": {
                        "message": "All notifications marked as read successfully",
                        "updated_count": 8
                    }
                }
            )
        }
    )
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """
        Mark all notifications as read for the current user
        """
        updated_count = self.get_queryset().filter(is_read=False).update(is_read=True)
        
        return Response({
            'message': 'All notifications marked as read successfully',
            'updated_count': updated_count
        })

    @swagger_auto_schema(
        operation_description="Get only unread notifications",
        responses={200: NotificationListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """
        Get only unread notifications for the current user
        """
        unread_notifications = self.get_queryset().filter(is_read=False)
        serializer = self.get_serializer(unread_notifications, many=True)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        """
        List notifications with optional filtering
        """
        queryset = self.get_queryset()
        
        # Optional filtering
        is_read = request.query_params.get('is_read')
        notification_type = request.query_params.get('type')
        
        if is_read is not None:
            is_read_bool = is_read.lower() in ('true', '1', 'yes')
            queryset = queryset.filter(is_read=is_read_bool)
        
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        
        # Pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
