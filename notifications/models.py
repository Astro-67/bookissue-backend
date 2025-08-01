from django.db import models
from django.conf import settings


class Notification(models.Model):
    """
    Notification model for user notifications
    """
    NOTIFICATION_TYPES = [
        ('ticket_status_change', 'Ticket Status Change'),
        ('new_comment', 'New Comment'),
        ('ticket_assigned', 'Ticket Assigned'),
        ('ticket_created', 'Ticket Created'),
        ('general', 'General'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=30,
        choices=NOTIFICATION_TYPES,
        default='general'
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Optional: Link to related objects
    ticket_id = models.IntegerField(null=True, blank=True)
    comment_id = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'

    def __str__(self):
        return f"{self.user.email} - {self.title} ({'Read' if self.is_read else 'Unread'})"

    @classmethod
    def create_notification(cls, user, title, message, notification_type='general', ticket_id=None, comment_id=None):
        """
        Helper method to create notifications
        """
        return cls.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            ticket_id=ticket_id,
            comment_id=comment_id
        )

    @classmethod
    def create_ticket_status_notification(cls, ticket, old_status, new_status):
        """
        Create notification when ticket status changes
        """
        # Notify ticket creator
        if ticket.created_by:
            cls.create_notification(
                user=ticket.created_by,
                title=f"Ticket #{ticket.id} Status Updated",
                message=f"Your ticket '{ticket.title}' status changed from '{old_status}' to '{new_status}'",
                notification_type='ticket_status_change',
                ticket_id=ticket.id
            )
        
        # Notify assigned ICT staff if different from creator
        if ticket.assigned_to and ticket.assigned_to != ticket.created_by:
            cls.create_notification(
                user=ticket.assigned_to,
                title=f"Assigned Ticket #{ticket.id} Status Updated",
                message=f"Ticket '{ticket.title}' status changed from '{old_status}' to '{new_status}'",
                notification_type='ticket_status_change',
                ticket_id=ticket.id
            )

    @classmethod
    def create_comment_notification(cls, comment, ticket):
        """
        Create notification when new comment is added
        """
        # Notify ticket creator if they didn't create the comment
        if ticket.created_by and ticket.created_by != comment.created_by:
            cls.create_notification(
                user=ticket.created_by,
                title=f"New Comment on Ticket #{ticket.id}",
                message=f"New comment added to your ticket '{ticket.title}' by {comment.created_by.full_name}",
                notification_type='new_comment',
                ticket_id=ticket.id,
                comment_id=comment.id
            )
        
        # Notify assigned ICT staff if they didn't create the comment and are different from ticket creator
        if (ticket.assigned_to and 
            ticket.assigned_to != comment.created_by and 
            ticket.assigned_to != ticket.created_by):
            cls.create_notification(
                user=ticket.assigned_to,
                title=f"New Comment on Assigned Ticket #{ticket.id}",
                message=f"New comment added to ticket '{ticket.title}' by {comment.created_by.full_name}",
                notification_type='new_comment',
                ticket_id=ticket.id,
                comment_id=comment.id
            )

    @classmethod
    def create_assignment_notification(cls, ticket, assigned_to):
        """
        Create notification when ticket is assigned to ICT staff
        """
        if assigned_to:
            cls.create_notification(
                user=assigned_to,
                title=f"New Ticket Assigned #{ticket.id}",
                message=f"You have been assigned to ticket '{ticket.title}' created by {ticket.created_by.full_name}",
                notification_type='ticket_assigned',
                ticket_id=ticket.id
            )
