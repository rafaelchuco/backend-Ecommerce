from .models import Cart, CartItem

def get_or_create_cart(request):
    """
    Obtiene o crea un carrito según si está autenticado o es anónimo.
    """
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(
            user=request.user,
            is_active=True
        )
    else:
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        cart, created = Cart.objects.get_or_create(
            session_id=session_id,
            is_active=True
        )
    return cart

def merge_carts(user, session_id):
    """
    Fusiona un carrito anónimo con el del usuario.
    Se puede llamar tras login para juntar ambos carritos.
    """
    try:
        user_cart = Cart.objects.get(user=user, is_active=True)
    except Cart.DoesNotExist:
        user_cart = Cart.objects.create(user=user, is_active=True)
    try:
        anon_cart = Cart.objects.get(session_id=session_id, is_active=True, user__isnull=True)
        for item in anon_cart.items.all():
            cart_item, created = CartItem.objects.get_or_create(
                cart=user_cart,
                product=item.product,
                defaults={'quantity': item.quantity}
            )
            if not created:
                cart_item.quantity += item.quantity
                cart_item.save()
        anon_cart.delete()
    except Cart.DoesNotExist:
        pass
    return user_cart
