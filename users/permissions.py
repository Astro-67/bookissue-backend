from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj == request.user


class IsStudentUser(permissions.BasePermission):
    """
    Custom permission to only allow students.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_student()


class IsStaffUser(permissions.BasePermission):
    """
    Custom permission to only allow staff members.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff_member()


class IsICTUser(permissions.BasePermission):
    """
    Custom permission to only allow ICT users.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_ict()


class CanManageTickets(permissions.BasePermission):
    """
    Custom permission for users who can manage tickets (staff and ICT).
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.can_manage_tickets()


class CanAssignTickets(permissions.BasePermission):
    """
    Custom permission for users who can assign tickets (ICT only).
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.can_assign_tickets()


class IsStaffOrICT(permissions.BasePermission):
    """
    Custom permission to allow staff and ICT users.
    """

    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                (request.user.is_staff_member() or request.user.is_ict()))


class IsOwnerOrStaffOrICT(permissions.BasePermission):
    """
    Custom permission to allow owner, staff, or ICT users.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Owner can always access
        if hasattr(obj, 'user') and obj.user == request.user:
            return True
        if hasattr(obj, 'created_by') and obj.created_by == request.user:
            return True
        if obj == request.user:
            return True
        
        # Staff and ICT can access
        return request.user.is_staff_member() or request.user.is_ict()
