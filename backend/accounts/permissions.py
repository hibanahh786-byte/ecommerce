from rest_framework import permissions

class IsAdminRole(permissions.BasePermission):
    """
    Allows access only to users with role='ADMIN', staff, or superusers.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            (request.user.role == 'ADMIN' or request.user.is_staff or request.user.is_superuser)
        )

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Allows access to the owner of the object or an admin.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.role == 'ADMIN' or request.user.is_staff or request.user.is_superuser:
            return True
        # For Order model, obj.user is the owner
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return obj == request.user
