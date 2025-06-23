#!/usr/bin/env python
"""
Script to create test users with proper password hashing
Run this with: python manage.py shell < create_test_users.py
"""

from users.models import User
from django.contrib.auth.hashers import make_password

# Clear existing test users (optional)
User.objects.filter(email__endswith='@gmail.com').delete()

print("Creating test users...")

# Students
students = [
    {'email': 'student1@gmail.com', 'username': 'student1', 'first_name': 'Alice', 'last_name': 'Johnson', 'student_id': 'STU2024001', 'department': 'Computer Science'},
    {'email': 'student2@gmail.com', 'username': 'student2', 'first_name': 'Bob', 'last_name': 'Smith', 'student_id': 'STU2024002', 'department': 'Information Technology'},
    {'email': 'student3@gmail.com', 'username': 'student3', 'first_name': 'Carol', 'last_name': 'Williams', 'student_id': 'STU2024003', 'department': 'Software Engineering'},
]

for student_data in students:
    user = User.objects.create_user(
        email=student_data['email'],
        username=student_data['username'],
        password='password123',
        first_name=student_data['first_name'],
        last_name=student_data['last_name'],
        role='student',
        student_id=student_data['student_id'],
        department=student_data['department'],
        phone_number='+1234567000'
    )
    print(f"Created student: {user.email}")

# Staff
staff_members = [
    {'email': 'staff1@gmail.com', 'username': 'staff1', 'first_name': 'Diana', 'last_name': 'Brown', 'department': 'Library Services'},
    {'email': 'staff2@gmail.com', 'username': 'staff2', 'first_name': 'Edward', 'last_name': 'Davis', 'department': 'Academic Support'},
    {'email': 'staff3@gmail.com', 'username': 'staff3', 'first_name': 'Fiona', 'last_name': 'Wilson', 'department': 'Student Services'},
]

for staff_data in staff_members:
    user = User.objects.create_user(
        email=staff_data['email'],
        username=staff_data['username'],
        password='password123',
        first_name=staff_data['first_name'],
        last_name=staff_data['last_name'],
        role='staff',
        department=staff_data['department'],
        phone_number='+1234567000',
        is_staff=True
    )
    print(f"Created staff: {user.email}")

# ICT Users
ict_users = [
    {'email': 'ict1@gmail.com', 'username': 'ict1', 'first_name': 'George', 'last_name': 'Miller', 'department': 'IT Department'},
    {'email': 'ict2@gmail.com', 'username': 'ict2', 'first_name': 'Helen', 'last_name': 'Garcia', 'department': 'IT Support'},
    {'email': 'ict3@gmail.com', 'username': 'ict3', 'first_name': 'Ivan', 'last_name': 'Martinez', 'department': 'System Administration'},
]

for ict_data in ict_users:
    user = User.objects.create_user(
        email=ict_data['email'],
        username=ict_data['username'],
        password='password123',
        first_name=ict_data['first_name'],
        last_name=ict_data['last_name'],
        role='ict',
        department=ict_data['department'],
        phone_number='+1234567000',
        is_staff=True
    )
    print(f"Created ICT user: {user.email}")

print("\nAll users created successfully!")
print("You can now login with any email and password: password123")
