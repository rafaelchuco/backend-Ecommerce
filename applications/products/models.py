from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.db.models import Avg


class Category(models.Model):
    """
    Categorías de productos con soporte para subcategorías
    """
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories'
    )
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0, help_text="Orden de visualización")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def product_count(self):
        """Cuenta productos en esta categoría"""
        return self.products.filter(is_active=True).count()


class Brand(models.Model):
    """
    Marcas de productos
    """
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Material(models.Model):
    """
    Materiales de construcción de productos
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Material'
        verbose_name_plural = 'Materiales'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Producto principal del e-commerce
    """
    # Información básica
    name = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    sku = models.CharField(max_length=100, unique=True, help_text="Código único del producto")
    description = models.TextField()
    
    # Relaciones
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products'
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )
    materials = models.ManyToManyField(
        Material,
        blank=True,
        related_name='products'
    )
    
    # Precios
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    
    # Stock
    stock = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)]
    )
    min_stock = models.IntegerField(
        default=5,
        help_text="Stock mínimo para alertas"
    )
    
    # Dimensiones (importantes para muebles)
    width = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Ancho en cm"
    )
    height = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Alto en cm"
    )
    depth = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Profundidad en cm"
    )
    weight = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Peso en kg"
    )
    
    # Características
    color = models.CharField(max_length=50, blank=True)
    warranty_months = models.IntegerField(default=12)
    assembly_required = models.BooleanField(default=False)
    assembly_time_minutes = models.IntegerField(
        null=True,
        blank=True,
        help_text="Tiempo estimado de ensamblaje"
    )
    
    # Estados
    is_featured = models.BooleanField(default=False, help_text="Producto destacado")
    is_active = models.BooleanField(default=True)
    is_new = models.BooleanField(default=True, help_text="Producto nuevo")
    
    # Estadísticas
    views_count = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['sku']),
            models.Index(fields=['is_active', 'is_featured']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['category', 'is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def final_price(self):
        """Retorna el precio final (con descuento si aplica)"""
        return self.discount_price if self.discount_price else self.price
    
    @property
    def discount_percentage(self):
        """Calcula el porcentaje de descuento"""
        if self.discount_price and self.discount_price < self.price:
            return int(((self.price - self.discount_price) / self.price) * 100)
        return 0
    
    @property
    def is_in_stock(self):
        """Verifica si hay stock disponible"""
        return self.stock > 0
    
    @property
    def is_low_stock(self):
        """Verifica si el stock está bajo"""
        return 0 < self.stock <= self.min_stock
    
    @property
    def average_rating(self):
        """Calcula el rating promedio del producto"""
        avg = self.reviews.filter(is_approved=True).aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0
    
    @property
    def review_count(self):
        """Cuenta las reviews aprobadas"""
        return self.reviews.filter(is_approved=True).count()
    
    def increment_views(self):
        """Incrementa el contador de vistas"""
        self.views_count += 1
        self.save(update_fields=['views_count'])


class ProductImage(models.Model):
    """
    Imágenes del producto (múltiples imágenes por producto)
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='products/')
    is_primary = models.BooleanField(default=False)
    alt_text = models.CharField(max_length=200, blank=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Imagen de Producto'
        verbose_name_plural = 'Imágenes de Productos'
        ordering = ['order', 'created_at']
        indexes = [
            models.Index(fields=['product', 'is_primary']),
        ]
    
    def __str__(self):
        return f"{self.product.name} - Imagen {self.order}"
    
    def save(self, *args, **kwargs):
        # Si es la imagen primaria, desmarcar las demás
        if self.is_primary:
            ProductImage.objects.filter(
                product=self.product,
                is_primary=True
            ).update(is_primary=False)
        super().save(*args, **kwargs)


class ProductSpecification(models.Model):
    """
    Especificaciones técnicas del producto
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='specifications'
    )
    name = models.CharField(max_length=100, help_text="Nombre de la especificación")
    value = models.CharField(max_length=200, help_text="Valor de la especificación")
    order = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = 'Especificación'
        verbose_name_plural = 'Especificaciones'
        ordering = ['order', 'name']
    
    def __str__(self):
        return f"{self.product.name} - {self.name}: {self.value}"


class Review(models.Model):
    """
    Reviews y calificaciones de productos
    """
    RATING_CHOICES = [(i, i) for i in range(1, 6)]
    
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=200)
    comment = models.TextField()
    is_verified_purchase = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True, help_text="Moderación de reviews")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ['-created_at']
        unique_together = ('product', 'user')
        indexes = [
            models.Index(fields=['product', 'is_approved']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating}⭐)"
