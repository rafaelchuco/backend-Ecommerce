from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permiso personalizado para permitir solo al dueño o admin
    """
    def has_object_permission(self, request, view, obj):
        # Admin puede ver todo
        if request.user and request.user.is_staff:
            return True
        
        # El dueño puede ver su propio objeto
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return obj == request.user


class IsOwner(permissions.BasePermission):
    """
    Permiso solo para el dueño
    """
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return obj == request.user