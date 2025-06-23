from rest_framework import permissions


class IsOwnerOrCanManageTickets(permissions.BasePermission):
    """
    Custom permission to allow ticket owners to view/edit their tickets,
    and staff/ICT to manage any ticket.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Owner can always access their tickets
        if obj.created_by == request.user:
            return True
        
        # Staff and ICT can manage any ticket
        if request.user.can_manage_tickets():
            return True
        
        return False


class CanAssignTickets(permissions.BasePermission):
    """
    Permission for assigning tickets (ICT only)
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.can_assign_tickets()


class CanViewAllTickets(permissions.BasePermission):
    """
    Permission for viewing all tickets (staff and ICT)
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.can_manage_tickets()
