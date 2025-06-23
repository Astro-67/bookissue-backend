from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Ticket
from .serializers import (
    TicketSerializer,
    TicketCreateSerializer,
    TicketListSerializer
)
from .permissions import IsOwnerOrCanManageTickets, CanAssignTickets
from users.models import User


class TicketViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tickets
    """
    queryset = Ticket.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'assigned_to', 'created_by']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'status']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return TicketCreateSerializer
        elif self.action == 'list':
            return TicketListSerializer
        return TicketSerializer

    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['list', 'retrieve', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrCanManageTickets]
        else:
            permission_classes = [permissions.IsAuthenticated]
        
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """Filter queryset based on user role"""
        user = self.request.user
        
        if user.can_manage_tickets():
            # Staff and ICT can see all tickets
            return Ticket.objects.all()
        else:
            # Students can only see their own tickets
            return Ticket.objects.filter(created_by=user)

    @swagger_auto_schema(
        operation_description="Create a new ticket",
        responses={
            201: "Ticket created successfully",
            400: "Bad Request - Validation errors"
        }
    )
    def perform_create(self, serializer):
        """Auto-fill created_by with current user"""
        serializer.save(created_by=self.request.user)

    @swagger_auto_schema(
        operation_description="Assign ticket to a staff/ICT member",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'assigned_to_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='User ID to assign ticket to')
            }
        ),
        responses={
            200: "Ticket assigned successfully",
            400: "Bad Request",
            403: "Permission denied"
        }
    )
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, CanAssignTickets])
    def assign(self, request, pk=None):
        """Assign ticket to a user (ICT only)"""
        ticket = self.get_object()
        assigned_to_id = request.data.get('assigned_to_id')
        
        if assigned_to_id:
            try:
                assigned_user = User.objects.get(id=assigned_to_id)
                if not assigned_user.can_manage_tickets():
                    return Response(
                        {'error': 'User must be staff or ICT to be assigned tickets'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                ticket.assigned_to = assigned_user
            except User.DoesNotExist:
                return Response(
                    {'error': 'User not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            ticket.assigned_to = None
        
        ticket.save()
        serializer = TicketSerializer(ticket)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Update ticket status",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING, enum=['OPEN', 'IN_PROGRESS', 'RESOLVED'])
            }
        ),
        responses={
            200: "Status updated successfully",
            400: "Bad Request"
        }
    )
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update ticket status"""
        ticket = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in ['OPEN', 'IN_PROGRESS', 'RESOLVED']:
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ticket.status = new_status
        ticket.save()
        
        serializer = TicketSerializer(ticket)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Get tickets assigned to current user",
        responses={200: TicketListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_tickets(self, request):
        """Get tickets created by current user"""
        tickets = Ticket.objects.filter(created_by=request.user)
        serializer = TicketListSerializer(tickets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Get tickets assigned to current user",
        responses={200: TicketListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def assigned_to_me(self, request):
        """Get tickets assigned to current user (staff/ICT only)"""
        if not request.user.can_manage_tickets():
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        tickets = Ticket.objects.filter(assigned_to=request.user)
        serializer = TicketListSerializer(tickets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Get ticket statistics",
        responses={
            200: openapi.Response(
                description="Ticket statistics",
                examples={
                    "application/json": {
                        "total_tickets": 10,
                        "open_tickets": 5,
                        "in_progress_tickets": 3,
                        "resolved_tickets": 2,
                        "assigned_tickets": 8,
                        "unassigned_tickets": 2
                    }
                }
            )
        }
    )
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def stats(self, request):
        """Get ticket statistics"""
        if request.user.can_manage_tickets():
            # Staff and ICT see all stats
            queryset = Ticket.objects.all()
        else:
            # Students see only their stats
            queryset = Ticket.objects.filter(created_by=request.user)
        
        total_tickets = queryset.count()
        open_tickets = queryset.filter(status='OPEN').count()
        in_progress_tickets = queryset.filter(status='IN_PROGRESS').count()
        resolved_tickets = queryset.filter(status='RESOLVED').count()
        assigned_tickets = queryset.filter(assigned_to__isnull=False).count()
        unassigned_tickets = queryset.filter(assigned_to__isnull=True).count()
        
        return Response({
            'total_tickets': total_tickets,
            'open_tickets': open_tickets,
            'in_progress_tickets': in_progress_tickets,
            'resolved_tickets': resolved_tickets,
            'assigned_tickets': assigned_tickets,
            'unassigned_tickets': unassigned_tickets
        }, status=status.HTTP_200_OK)
