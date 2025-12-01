from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    """
    Permiso personalizado: solo el usuario dueño puede acceder o modificar la orden.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
