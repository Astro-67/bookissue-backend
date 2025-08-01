from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for notification data
    """
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    time_ago = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'notification_type', 'is_read', 
            'created_at', 'ticket_id', 'comment_id', 'user_name', 'time_ago'
        ]
        read_only_fields = ['id', 'created_at', 'user_name', 'time_ago']

    def get_time_ago(self, obj):
        """
        Return human-readable time difference
        """
        from django.utils import timezone
        from django.utils.timesince import timesince
        
        return timesince(obj.created_at, timezone.now())


class NotificationListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing notifications
    """
    time_ago = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'notification_type', 'is_read', 
            'created_at', 'ticket_id', 'time_ago'
        ]

    def get_time_ago(self, obj):
        """
        Return human-readable time difference
        """
        from django.utils import timezone
        from django.utils.timesince import timesince
        
        return timesince(obj.created_at, timezone.now())


class MarkNotificationReadSerializer(serializers.Serializer):
    """
    Serializer for marking notifications as read
    """
    notification_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="List of notification IDs to mark as read. If not provided, all notifications will be marked as read."
    )
