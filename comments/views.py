from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Comment
from .serializers import CommentSerializer, CommentCreateSerializer
from users.permissions import IsOwnerOrStaffOrICT


class CommentListCreateView(generics.ListCreateAPIView):
    """
    GET: List all comments for a specific ticket
    POST: Create a new comment for a specific ticket
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CommentCreateSerializer
        return CommentSerializer

    def get_queryset(self):
        from django.apps import apps
        Ticket = apps.get_model('tickets', 'Ticket')
        
        ticket_id = self.kwargs['ticket_id']
        ticket = get_object_or_404(Ticket, id=ticket_id)
        
        # Check if user can view this ticket's comments
        if (ticket.created_by == self.request.user or 
            ticket.assigned_to == self.request.user or
            self.request.user.can_manage_tickets()):
            return Comment.objects.filter(ticket=ticket).select_related('author', 'ticket')
        else:
            return Comment.objects.none()

    @swagger_auto_schema(
        operation_description="Get all comments for a specific ticket",
        manual_parameters=[
            openapi.Parameter('ticket_id', openapi.IN_PATH, description="ID of the ticket", type=openapi.TYPE_INTEGER)
        ],
        responses={
            200: CommentSerializer(many=True),
            404: "Ticket not found",
            403: "Permission denied"
        }
    )
    def get(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new comment for a specific ticket",
        request_body=CommentCreateSerializer,
        manual_parameters=[
            openapi.Parameter('ticket_id', openapi.IN_PATH, description="ID of the ticket", type=openapi.TYPE_INTEGER)
        ],
        responses={
            201: CommentSerializer,
            400: "Bad Request - Validation errors",
            404: "Ticket not found",
            403: "Permission denied"
        }
    )
    def post(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        from django.apps import apps
        Ticket = apps.get_model('tickets', 'Ticket')
        
        ticket_id = self.kwargs['ticket_id']
        ticket = get_object_or_404(Ticket, id=ticket_id)
        
        # Check if user can comment on this ticket
        if (ticket.created_by == self.request.user or 
            ticket.assigned_to == self.request.user or
            self.request.user.can_manage_tickets()):
            serializer.save(
                author=self.request.user,
                ticket=ticket
            )
        else:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You don't have permission to comment on this ticket.")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Return the created comment with full details
        comment_serializer = CommentSerializer(serializer.instance)
        return Response(comment_serializer.data, status=status.HTTP_201_CREATED)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve a specific comment
    PUT/PATCH: Update a comment (only by author or staff/ICT)
    DELETE: Delete a comment (only by author or staff/ICT)
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaffOrICT]

    def get_queryset(self):
        return Comment.objects.select_related('author', 'ticket')

    @swagger_auto_schema(
        operation_description="Get a specific comment",
        responses={
            200: CommentSerializer,
            404: "Comment not found",
            403: "Permission denied"
        }
    )
    def get(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update a comment (author or staff/ICT only)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING, description='Updated comment message')
            }
        ),
        responses={
            200: CommentSerializer,
            400: "Bad Request - Validation errors",
            404: "Comment not found",
            403: "Permission denied"
        }
    )
    def put(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete a comment (author or staff/ICT only)",
        responses={
            204: "Comment deleted successfully",
            404: "Comment not found",
            403: "Permission denied"
        }
    )
    def delete(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
