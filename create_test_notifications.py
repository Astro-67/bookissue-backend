#!/usr/bin/env python
"""
Test script to create sample notifications
Run with: python manage.py shell < create_test_notifications.py
"""

from django.contrib.auth import get_user_model
from notifications.models import Notification
from tickets.models import Ticket

User = get_user_model()

# Get or create test users
ict_user, created = User.objects.get_or_create(
    email='ict@test.com',
    defaults={
        'username': 'ict_admin',
        'first_name': 'ICT',
        'last_name': 'Admin',
        'role': 'ict'
    }
)

student_user, created = User.objects.get_or_create(
    email='student@test.com', 
    defaults={
        'username': 'test_student',
        'first_name': 'Test',
        'last_name': 'Student',
        'role': 'student'
    }
)

# Create test notifications
print("Creating test notifications...")

# Test notification 1: New ticket created
Notification.create_notification(
    user=ict_user,
    title="New Ticket #123",
    message="New ticket has been submitted by Test Student.",
    notification_type='assignment'
)

# Test notification 2: Ticket status changed
Notification.create_notification(
    user=student_user,
    title="Ticket #123 In Progress", 
    message="Your ticket 'WiFi Connection Issue' is now being worked on.",
    notification_type='ticket_status'
)

# Test notification 3: Comment added
Notification.create_notification(
    user=student_user,
    title="ICT Replied to Ticket #123",
    message="ICT has replied to your ticket 'WiFi Connection Issue'.",
    notification_type='new_comment'
)

# Test notification 4: Assignment
Notification.create_notification(
    user=ict_user,
    title="Ticket #124 Assigned to You",
    message="You have been assigned to ticket 'Printer Not Working' created by Jane Smith.",
    notification_type='assignment'
)

# Test notification 5: Welcome message
Notification.create_notification(
    user=student_user,
    title="Welcome to Book Issue Tracker",
    message="Your account has been created successfully. You can now access the system.",
    notification_type='general'
)

print(f"Created {Notification.objects.count()} notifications total")
print("Test notifications created successfully!")

# Display the notifications
print("\n--- ICT User Notifications ---")
for notif in Notification.objects.filter(user=ict_user):
    print(f"- {notif.title}: {notif.message}")

print("\n--- Student User Notifications ---") 
for notif in Notification.objects.filter(user=student_user):
    print(f"- {notif.title}: {notif.message}")
