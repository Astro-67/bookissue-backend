from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from tickets.models import Ticket
from comments.models import Comment
from .models import Notification

User = get_user_model()


@receiver(post_save, sender=Ticket)
def create_ticket_notifications(sender, instance, created, **kwargs):
    """
    Create notifications when:
    1. A new ticket is created (notify ICT team)
    2. A ticket status changes (notify ticket creator)
    3. A ticket is assigned (notify assigned ICT member)
    """
    if created:
        # 1. Notify ICT team about new ticket
        ict_users = User.objects.filter(role='ict')
        for ict_user in ict_users:
            Notification.create_notification(
                user=ict_user,
                title=f"New Ticket #{instance.id}",
                message=f"New ticket has been submitted by {instance.created_by.get_full_name()}.",
                notification_type='assignment',
                ticket_id=instance.id
            )
    else:
        # Check if status changed
        try:
            old_instance = Ticket.objects.get(pk=instance.pk)
            # Get the previous state from the database
            if hasattr(instance, '_old_status') and instance._old_status != instance.status:
                # 2. Notify ticket creator about status change
                status_display = instance.get_status_display()
                Notification.create_ticket_status_notification(
                    user=instance.created_by,
                    ticket=instance,
                    old_status=instance._old_status,
                    new_status=instance.status
                )
            
            # Check if assignment changed
            if hasattr(instance, '_old_assigned_to') and instance._old_assigned_to != instance.assigned_to:
                if instance.assigned_to:
                    # 4. Notify assigned ICT member
                    Notification.create_assignment_notification(
                        user=instance.assigned_to,
                        ticket=instance,
                        assigned_by=None  # We don't track who assigned it in this context
                    )
        except Ticket.DoesNotExist:
            pass


@receiver(pre_save, sender=Ticket)
def store_old_ticket_values(sender, instance, **kwargs):
    """Store old values before saving to detect changes"""
    if instance.pk:
        try:
            old_instance = Ticket.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
            instance._old_assigned_to = old_instance.assigned_to
        except Ticket.DoesNotExist:
            pass


@receiver(post_save, sender=Comment)
def create_comment_notifications(sender, instance, created, **kwargs):
    """
    Create notifications when:
    3. A comment is added to a ticket
    """
    if created:
        ticket = instance.ticket
        comment_author = instance.author_details
        
        # If ICT comments, notify ticket creator
        if comment_author.role == 'ict' and comment_author != ticket.created_by:
            Notification.create_comment_notification(
                user=ticket.created_by,
                comment=instance,
                commenter=comment_author
            )
        
        # If Student/Staff comments, notify ICT team
        elif comment_author.role in ['student', 'staff'] and comment_author != ticket.created_by:
            ict_users = User.objects.filter(role='ict')
            for ict_user in ict_users:
                if ict_user != comment_author:  # Don't notify the commenter
                    Notification.create_comment_notification(
                        user=ict_user,
                        comment=instance,
                        commenter=comment_author
                    )
        
        # Also notify ticket creator if they didn't write the comment
        if comment_author != ticket.created_by:
            Notification.create_comment_notification(
                user=ticket.created_by,
                comment=instance,
                commenter=comment_author
            )


@receiver(post_save, sender=User)
def create_user_notifications(sender, instance, created, **kwargs):
    """
    Create notifications when:
    5. A new user is created by Super Admin
    """
    if created:
        # 5. Notify new user about account creation
        Notification.create_notification(
            user=instance,
            title="Welcome to Book Issue Tracker",
            message="Your account has been created successfully. You can now access the system.",
            notification_type='general'
        )
