from rest_framework import permissions

class IsOwnerOfCart(permissions.BasePermission):
    """
    Permiso personalizado: El usuario solo puede acceder a su propio carrito.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            return obj.user == request.user
        # Para sesión anónima (carritos sin usuario asignado)
        session_id = request.session.session_key
        return obj.session_id == session_id

class IsOwnerOfWishlist(permissions.BasePermission):
    """
    Permiso personalizado: Solo el usuario dueño puede acceder a su wishlist.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
