from django.db import models
from django.conf import settings


class Comment(models.Model):
    """
    Comment model for support tickets
    """
    ticket = models.ForeignKey(
        'tickets.Ticket',  # Use string reference instead of direct import
        on_delete=models.CASCADE, 
        related_name='comments',
        help_text="The ticket this comment belongs to"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='comments',
        help_text="The user who wrote this comment"
    )
    message = models.TextField(
        help_text="The comment content"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this comment was created"
    )

    class Meta:
        db_table = 'comments'
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ['-created_at']  # Show newest comments first

    def __str__(self):
        return f"Comment by {self.author.full_name} on {self.ticket.title}"

    @property
    def author_name(self):
        """Get the full name of the comment author"""
        return self.author.full_name

    @property
    def ticket_title(self):
        """Get the title of the associated ticket"""
        return self.ticket.title
