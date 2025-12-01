from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.utils.text import slugify
from .models import Product, Category, Brand, ProductImage


@receiver(pre_save, sender=Product)
def generate_product_slug(sender, instance, **kwargs):
    """
    Genera slug automáticamente si no existe
    """
    if not instance.slug:
        base_slug = slugify(instance.name)
        slug = base_slug
        counter = 1
        
        while Product.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        instance.slug = slug


@receiver(pre_save, sender=Category)
def generate_category_slug(sender, instance, **kwargs):
    """
    Genera slug para categoría
    """
    if not instance.slug:
        base_slug = slugify(instance.name)
        slug = base_slug
        counter = 1
        
        while Category.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        instance.slug = slug


@receiver(pre_save, sender=Brand)
def generate_brand_slug(sender, instance, **kwargs):
    """
    Genera slug para marca
    """
    if not instance.slug:
        base_slug = slugify(instance.name)
        slug = base_slug
        counter = 1
        
        while Brand.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        instance.slug = slug


@receiver(post_save, sender=ProductImage)
def ensure_one_primary_image(sender, instance, created, **kwargs):
    """
    Asegura que solo una imagen sea primaria por producto
    """
    if instance.is_primary:
        ProductImage.objects.filter(
            product=instance.product
        ).exclude(id=instance.id).update(is_primary=False)
    
    # Si no hay imagen primaria, hacer esta la primaria
    if not ProductImage.objects.filter(
        product=instance.product,
        is_primary=True
    ).exists():
        instance.is_primary = True
        instance.save(update_fields=['is_primary'])