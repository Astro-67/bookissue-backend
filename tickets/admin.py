from django.contrib import admin
from .models import Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'status', 'created_by', 'assigned_to', 'created_at')
    list_filter = ('status', 'created_at', 'updated_at', 'assigned_to')
    search_fields = ('title', 'description', 'created_by__email', 'created_by__first_name', 'created_by__last_name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {'fields': ('title', 'description', 'status')}),
        ('Assignment', {'fields': ('created_by', 'assigned_to')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('created_by', 'assigned_to')
