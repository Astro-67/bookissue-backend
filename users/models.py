from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model with role-based access control
    """
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('staff', 'Staff'),
        ('ict', 'ICT'),
    ]
    
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    student_id = models.CharField(max_length=20, blank=True, null=True, unique=True)
    department = models.CharField(max_length=100, blank=True, null=True)
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

    def has_role(self, role):
        """Check if user has a specific role"""
        return self.role == role

    def is_student(self):
        return self.role == 'student'

    def is_staff_member(self):
        return self.role == 'staff'

    def is_ict(self):
        return self.role == 'ict'

    def can_manage_tickets(self):
        """Check if user can manage tickets (staff and ICT)"""
        return self.role in ['staff', 'ict']

    def can_assign_tickets(self):
        """Check if user can assign tickets (ICT only)"""
        return self.role == 'ict'
