from django.db import models
from django.conf import settings


class Notification(models.Model):
    """
    Notification model for user notifications
    """
    NOTIFICATION_TYPES = [
        ('ticket_status', 'Ticket Status Change'),
        ('new_comment', 'New Comment'),
        ('assignment', 'Ticket Assigned'),
        ('new_ticket', 'New Ticket Created'),
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
    def create_ticket_status_notification(cls, user, ticket, old_status, new_status):
        """
        Create notification when ticket status changes
        """
        status_map = {
            'OPEN': 'Open',
            'IN_PROGRESS': 'In Progress', 
            'RESOLVED': 'Resolved'
        }
        
        old_status_display = status_map.get(old_status, old_status)
        new_status_display = status_map.get(new_status, new_status)
        
        if new_status == 'RESOLVED':
            title = f"Ticket #{ticket.id} Resolved"
            message = f"Your ticket '{ticket.title}' has been resolved."
        elif new_status == 'IN_PROGRESS':
            title = f"Ticket #{ticket.id} In Progress"
            message = f"Your ticket '{ticket.title}' is now being worked on."
        else:
            title = f"Ticket #{ticket.id} Status Updated"
            message = f"Your ticket '{ticket.title}' status changed to {new_status_display}."
            
        return cls.create_notification(
            user=user,
            title=title,
            message=message,
            notification_type='ticket_status',
            ticket_id=ticket.id
        )

    @classmethod
    def create_comment_notification(cls, user, comment, commenter):
        """
        Create notification when new comment is added
        """
        ticket = comment.ticket
        
        if commenter.role == 'ict':
            title = f"ICT Replied to Ticket #{ticket.id}"
            message = f"ICT has replied to your ticket '{ticket.title}'."
        else:
            title = f"New Comment on Ticket #{ticket.id}"
            message = f"{commenter.get_full_name()} has added a comment to ticket '{ticket.title}'."
        
        return cls.create_notification(
            user=user,
            title=title,
            message=message,
            notification_type='new_comment',
            ticket_id=ticket.id,
            comment_id=comment.id
        )

    @classmethod
    def create_assignment_notification(cls, user, ticket, assigned_by):
        """
        Create notification when ticket is assigned to ICT staff
        """
        return cls.create_notification(
            user=user,
            title=f"Ticket #{ticket.id} Assigned to You",
            message=f"You have been assigned to ticket '{ticket.title}' created by {ticket.created_by.get_full_name()}.",
            notification_type='assignment',
            ticket_id=ticket.id
        )
