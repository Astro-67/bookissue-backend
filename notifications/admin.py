from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Admin interface for Notification model
    """
    list_display = [
        'id', 'user', 'title', 'notification_type', 'is_read', 'created_at'
    ]
    list_filter = [
        'notification_type', 'is_read', 'created_at'
    ]
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name', 'title', 'message'
    ]
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'title', 'message', 'notification_type')
        }),
        ('Status', {
            'fields': ('is_read',)
        }),
        ('Related Objects', {
            'fields': ('ticket_id', 'comment_id'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} notifications marked as read.')
    mark_as_read.short_description = "Mark selected notifications as read"
    
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} notifications marked as unread.')
    mark_as_unread.short_description = "Mark selected notifications as unread"
