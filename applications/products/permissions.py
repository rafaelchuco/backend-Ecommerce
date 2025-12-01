from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permiso custom: lectura para todos, escritura solo para admin
    """
    def has_permission(self, request, view):
        # SAFE_METHODS = GET, HEAD, OPTIONS
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Solo admin puede crear/actualizar/eliminar
        return request.user and request.user.is_staff


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permiso para reviews: solo el dueño o admin puede editar/eliminar
    """
    def has_object_permission(self, request, view, obj):
        # Lectura permitida para todos
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Admin puede todo
        if request.user and request.user.is_staff:
            return True
        
        # El dueño puede editar su review
        return obj.user == request.user


class HasPurchasedProduct(permissions.BasePermission):
    """
    Permiso para crear reviews: solo usuarios que compraron el producto
    (Temporal: permitir a todos por ahora, luego integrar con órdenes)
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    # TODO: Implementar validación real cuando se integre con orders
    # def has_object_permission(self, request, view, obj):
    #     from orders.models import OrderItem
    #     return OrderItem.objects.filter(
    #         order__user=request.user,
    #         product=obj.product,
    #         order__status='delivered'
    #     ).exists()