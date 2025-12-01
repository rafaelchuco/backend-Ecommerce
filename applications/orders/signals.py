from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Order, OrderStatusHistory, OrderItem
from applications.products.models import Product

@receiver(pre_save, sender=Order)
def calculate_totals(sender, instance, **kwargs):
    # Calcula subtotal sumando items
    if instance.pk is None:
        subtotal = 0
        for item in instance.items.all():
            subtotal += item.subtotal
        instance.subtotal = subtotal
        instance.tax = subtotal * 0.18  # 18% IVA ejemplo
        instance.total = subtotal + instance.shipping_cost + instance.tax - instance.discount
    # Se puede agregar más lógica

@receiver(post_save, sender=Order)
def create_status_history(sender, instance, created, **kwargs):
    if created:
        OrderStatusHistory.objects.create(
            order=instance,
            status=instance.status,
            comment='Orden creada',
            created_by=instance.user
        )

@receiver(post_save, sender=Order)
def update_stock(sender, instance, created, **kwargs):
    if created:
        for item in instance.items.all():
            product = item.product
            if product:
                product.stock = max(product.stock - item.quantity, 0)
                product.save()
