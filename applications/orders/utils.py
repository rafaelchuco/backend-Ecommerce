from .models import Order

def get_user_orders(user):
    """
    Retorna todas las órdenes del usuario.
    """
    return Order.objects.filter(user=user).order_by('-created_at')

