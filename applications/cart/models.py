from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from applications.products.models import Product

class Cart(models.Model):
    """Carrito de compras"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts', null=True, blank=True, verbose_name='Usuario')
    session_id = models.CharField(max_length=255, null=True, blank=True, verbose_name='ID de Sesión')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Creado')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Actualizado')
    is_active = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        verbose_name = 'Carrito'
        verbose_name_plural = 'Carritos'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_id', 'is_active']),
        ]

    def __str__(self):
        if self.user:
            return f"Carrito de {self.user.username}"
        return f"Carrito anónimo ({self.session_id})"

    @property
    def total_price(self):
        total = sum(item.subtotal for item in self.items.all())
        return round(total, 2)

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def item_count(self):
        return self.items.count()

class CartItem(models.Model):
    """Item individual del carrito"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name='Carrito')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Producto')
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)], verbose_name='Cantidad')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='Agregado')

    class Meta:
        verbose_name = 'Item del Carrito'
        verbose_name_plural = 'Items del Carrito'
        unique_together = [('cart', 'product')]
        ordering = ['-added_at']
        indexes = [
            models.Index(fields=['cart', 'product']),
        ]

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    @property
    def subtotal(self):
        price = self.product.final_price
        return round(price * self.quantity, 2)

    @property
    def unit_price(self):
        return self.product.final_price

class Wishlist(models.Model):
    """Lista de deseos"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist', verbose_name='Usuario')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Producto')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='Agregado')
    notes = models.TextField(blank=True, null=True, verbose_name='Notas')

    class Meta:
        verbose_name = 'Lista de Deseos'
        verbose_name_plural = 'Listas de Deseos'
        unique_together = [('user', 'product')]
        ordering = ['-added_at']
        indexes = [
            models.Index(fields=['user', '-added_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
