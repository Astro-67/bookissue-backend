from django.contrib import admin
from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'author_name', 'ticket_title', 'message_preview', 'created_at']
    list_filter = ['created_at', 'ticket__status', 'author__role']
    search_fields = ['message', 'author__first_name', 'author__last_name', 'ticket__title']
    readonly_fields = ['created_at']
    raw_id_fields = ['ticket', 'author']
    
    fieldsets = (
        (None, {'fields': ('ticket', 'author', 'message')}),
        ('Timestamps', {'fields': ('created_at',)}),
    )
    
    def message_preview(self, obj):
        """Show a preview of the comment message"""
        return obj.message[:50] + "..." if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message Preview'
    
    def author_name(self, obj):
        """Show the author's full name"""
        return obj.author.full_name
    author_name.short_description = 'Author'
    
    def ticket_title(self, obj):
        """Show the ticket title"""
        return obj.ticket.title
    ticket_title.short_description = 'Ticket'
