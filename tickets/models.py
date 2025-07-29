from django.db import models
from django.conf import settings
import os


class Ticket(models.Model):
    """
    Ticket model for managing book issue reports
    """
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    screenshot = models.ImageField(
        upload_to='ticket_screenshots/',
        null=True,
        blank=True,
        help_text='Screenshot image of the problem (optional)'
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='OPEN'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_tickets'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='assigned_tickets',
        null=True,
        blank=True,
        default=None
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tickets'
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.id} - {self.title} ({self.status})"

    @property
    def is_open(self):
        return self.status == 'OPEN'

    @property
    def is_in_progress(self):
        return self.status == 'IN_PROGRESS'

    @property
    def is_resolved(self):
        return self.status == 'RESOLVED'

    def can_be_assigned_to(self, user):
        """Check if ticket can be assigned to a specific user"""
        return user.can_manage_tickets()

    def can_be_updated_by(self, user):
        """Check if ticket can be updated by a specific user"""
        # Creator can always update their own tickets
        if self.created_by == user:
            return True
        # Staff and ICT can update any ticket
        return user.can_manage_tickets()

    def can_be_assigned_by(self, user):
        """Check if user can assign this ticket"""
        return user.can_assign_tickets()
