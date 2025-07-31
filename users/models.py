from django.contrib.auth.models import AbstractUser
from django.db import models
import os


def user_profile_picture_path(instance, filename):
    """Generate upload path for user profile pictures"""
    # Get file extension
    ext = filename.split('.')[-1]
    # Create filename using user ID
    filename = f'profile_{instance.id}.{ext}'
    return os.path.join('profile_pictures', filename)


class User(AbstractUser):
    """
    Custom User model with role-based access control
    """
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('staff', 'Staff'),
        ('ict', 'ICT'),
        ('super_admin', 'Super Admin'),
    ]
    
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='student')
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    student_id = models.CharField(max_length=20, blank=True, null=True, unique=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to=user_profile_picture_path,
        blank=True,
        null=True,
        help_text="Upload a profile picture (max 5MB, JPG/PNG)"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def profile_picture_url(self):
        """Get the full URL for the profile picture"""
        if self.profile_picture:
            return self.profile_picture.url
        return None

    def delete_old_profile_picture(self):
        """Delete the old profile picture file when updating"""
        if self.profile_picture:
            if os.path.isfile(self.profile_picture.path):
                os.remove(self.profile_picture.path)

    def save(self, *args, **kwargs):
        # If this is an update and profile picture is being changed
        if self.pk:
            try:
                old_user = User.objects.get(pk=self.pk)
                if old_user.profile_picture and old_user.profile_picture != self.profile_picture:
                    old_user.delete_old_profile_picture()
            except User.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    def has_role(self, role):
        """Check if user has a specific role"""
        return self.role == role

    def is_student(self):
        return self.role == 'student'

    def is_staff_member(self):
        return self.role == 'staff'

    def is_ict(self):
        return self.role == 'ict'

    def is_super_admin(self):
        return self.role == 'super_admin'

    def can_manage_tickets(self):
        """Check if user can manage tickets (staff, ICT, and super admin)"""
        return self.role in ['staff', 'ict', 'super_admin']

    def can_assign_tickets(self):
        """Check if user can assign tickets (ICT and super admin)"""
        return self.role in ['ict', 'super_admin']

    def can_manage_users(self):
        """Check if user can manage other users (super admin only)"""
        return self.role == 'super_admin'

    def can_view_all_tickets(self):
        """Check if user can view all tickets regardless of assignment"""
        return self.role in ['ict', 'super_admin']

    def can_delete_tickets(self):
        """Check if user can delete tickets (super admin only)"""
        return self.role == 'super_admin'
