#!/usr/bin/env python
"""
Script to create test tickets with realistic data
Run this with: python manage.py shell < create_test_tickets.py
"""

from users.models import User
from tickets.models import Ticket
from comments.models import Comment
from django.utils import timezone
from datetime import timedelta
import random

print("Creating test tickets...")

# Get users
students = User.objects.filter(role='student')
staff_members = User.objects.filter(role='staff')
ict_users = User.objects.filter(role='ict')

if not students.exists():
    print("No students found! Please run create_test_users.py first.")
    exit()

# Clear existing test tickets (optional)
Ticket.objects.all().delete()

# Sample book titles and issues
book_issues = [
    {
        'title': 'Request for "Clean Code" by Robert Martin',
        'description': 'I need this book for my Software Engineering course project. The book covers best practices for writing maintainable code.'
    },
    {
        'title': 'Request for "JavaScript: The Good Parts"',
        'description': 'Required reading for Web Development course. Need it for the upcoming assignment on functional programming concepts.'
    },
    {
        'title': 'Request for "Design Patterns" by Gang of Four',
        'description': 'This book is essential for my Object-Oriented Programming course. I need to understand creational, structural, and behavioral patterns.'
    },
    {
        'title': 'Request for "Python Crash Course"',
        'description': 'Looking for this book to supplement my Python programming skills. It would help me with data structures and algorithms.'
    },
    {
        'title': 'Request for "Database Systems Concepts"',
        'description': 'Need this textbook for my Database Management course. It covers SQL, normalization, and transaction management.'
    },
    {
        'title': 'Request for "Computer Networks" by Tanenbaum',
        'description': 'Required for my Computer Networks course. Need to understand TCP/IP, OSI model, and network protocols.'
    },
    {
        'title': 'Request for "Algorithms" by Cormen',
        'description': 'This comprehensive book is needed for my Advanced Algorithms course. Covers sorting, searching, and graph algorithms.'
    },
    {
        'title': 'Request for "Operating System Concepts"',
        'description': 'Essential textbook for my Operating Systems course. Need to study process management, memory management, and file systems.'
    },
    {
        'title': 'Request for "Software Engineering: A Practitioner\'s Approach"',
        'description': 'Required reading for my Software Engineering course. Covers SDLC, project management, and quality assurance.'
    },
    {
        'title': 'Request for "Machine Learning Yearning" by Andrew Ng',
        'description': 'Want to learn about machine learning fundamentals and practical applications for my AI course project.'
    }
]

# Create tickets for each student
for student in students:
    # Each student gets 3-7 tickets
    num_tickets = random.randint(3, 7)
    
    for i in range(num_tickets):
        book_issue = random.choice(book_issues)
        
        # Random creation time (within last 30 days)
        days_ago = random.randint(1, 30)
        created_at = timezone.now() - timedelta(days=days_ago)
        
        # Determine status based on age
        if days_ago <= 2:
            status = 'OPEN'
            assigned_to = None
        elif days_ago <= 10:
            status = random.choice(['OPEN', 'IN_PROGRESS'])
            assigned_to = random.choice(list(ict_users)) if status == 'IN_PROGRESS' else None
        else:
            status = random.choice(['IN_PROGRESS', 'RESOLVED'])
            assigned_to = random.choice(list(ict_users))
        
        ticket = Ticket.objects.create(
            title=book_issue['title'],
            description=book_issue['description'],
            status=status,
            priority='MEDIUM',
            created_by=student,
            assigned_to=assigned_to,
            created_at=created_at,
            updated_at=created_at if status == 'OPEN' else created_at + timedelta(hours=random.randint(1, 48))
        )
        
        # Add some comments for older tickets
        if status in ['IN_PROGRESS', 'RESOLVED'] and random.choice([True, False]):
            # ICT user comment
            Comment.objects.create(
                ticket=ticket,
                user=assigned_to or random.choice(list(ict_users)),
                message=random.choice([
                    "I'm looking into this request. Will check book availability.",
                    "Book is available. Processing your request now.",
                    "Please come to the library counter to collect your book.",
                    "Request has been approved. Book is ready for pickup.",
                    "The book you requested is currently issued to another student. You'll be notified when it's available."
                ]),
                created_at=created_at + timedelta(hours=random.randint(1, 24))
            )
            
            # Sometimes student replies
            if random.choice([True, False]):
                Comment.objects.create(
                    ticket=ticket,
                    user=student,
                    message=random.choice([
                        "Thank you for the update!",
                        "When will the book be available?",
                        "I'll come to collect it today.",
                        "Can you please check again? I really need this book.",
                        "Is there an alternative book you can recommend?"
                    ]),
                    created_at=created_at + timedelta(hours=random.randint(25, 48))
                )

print(f"Created {Ticket.objects.count()} test tickets")
print(f"Created {Comment.objects.count()} test comments")

# Print summary
print("\nTicket Status Summary:")
for status in ['OPEN', 'IN_PROGRESS', 'RESOLVED']:
    count = Ticket.objects.filter(status=status).count()
    print(f"  {status}: {count} tickets")

print("\nTest data created successfully!")
print("Students now have realistic book request tickets with various statuses and comments.")
