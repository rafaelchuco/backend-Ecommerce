from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Brand, Material, Product, ProductImage, ProductSpecification, Review


class ProductImageInline(admin.TabularInline):
    """
    Inline para gestionar imágenes de productos
    """
    model = ProductImage
    extra = 1
    fields = ('image', 'is_primary', 'alt_text', 'order')
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" />', obj.image.url)
        return "No hay imagen"
    image_preview.short_description = 'Vista previa'


class ProductSpecificationInline(admin.TabularInline):
    """
    Inline para especificaciones técnicas
    """
    model = ProductSpecification
    extra = 1
    fields = ('name', 'value', 'order')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin para categorías
    """
    list_display = ('name', 'parent', 'product_count_display', 'is_active', 'order', 'created_at')
    list_filter = ('is_active', 'parent', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at', 'product_count_display')
    list_editable = ('order', 'is_active')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'slug', 'description', 'image')
        }),
        ('Jerarquía', {
            'fields': ('parent',)
        }),
        ('Configuración', {
            'fields': ('is_active', 'order')
        }),
        ('Estadísticas', {
            'fields': ('product_count_display', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def product_count_display(self, obj):
        count = obj.product_count
        return format_html('<strong>{}</strong> productos', count)
    product_count_display.short_description = 'Productos'


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    """
    Admin para marcas
    """
    list_display = ('name', 'logo_preview', 'product_count_display', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'product_count_display', 'logo_preview_large')
    list_editable = ('is_active',)
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Logo', {
            'fields': ('logo', 'logo_preview_large')
        }),
        ('Configuración', {
            'fields': ('is_active',)
        }),
        ('Estadísticas', {
            'fields': ('product_count_display', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: contain;" />', obj.logo.url)
        return "Sin logo"
    logo_preview.short_description = 'Logo'
    
    def logo_preview_large(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="200" />', obj.logo.url)
        return "Sin logo"
    logo_preview_large.short_description = 'Vista previa del logo'
    
    def product_count_display(self, obj):
        count = obj.products.filter(is_active=True).count()
        return format_html('<strong>{}</strong> productos', count)
    product_count_display.short_description = 'Productos'


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    """
    Admin para materiales
    """
    list_display = ('name', 'product_count_display')
    search_fields = ('name', 'description')
    
    def product_count_display(self, obj):
        count = obj.products.filter(is_active=True).count()
        return format_html('<strong>{}</strong> productos', count)
    product_count_display.short_description = 'Productos'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Admin para productos
    """
    list_display = (
        'name', 'sku', 'category', 'brand', 'price_display', 
        'stock_display', 'is_featured', 'is_active', 'created_at'
    )
    list_filter = (
        'is_active', 'is_featured', 'is_new', 'category', 
        'brand', 'assembly_required', 'created_at'
    )
    search_fields = ('name', 'sku', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = (
        'created_at', 'updated_at', 'views_count', 
        'final_price_display', 'average_rating_display', 
        'review_count_display', 'stock_status'
    )
    list_editable = ('is_featured', 'is_active')
    filter_horizontal = ('materials',)
    inlines = [ProductImageInline, ProductSpecificationInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'slug', 'sku', 'description')
        }),
        ('Clasificación', {
            'fields': ('category', 'brand', 'materials')
        }),
        ('Precios', {
            'fields': ('price', 'discount_price', 'final_price_display')
        }),
        ('Inventario', {
            'fields': ('stock', 'min_stock', 'stock_status')
        }),
        ('Dimensiones y Peso', {
            'fields': ('width', 'height', 'depth', 'weight'),
            'classes': ('collapse',)
        }),
        ('Características', {
            'fields': ('color', 'warranty_months', 'assembly_required', 'assembly_time_minutes')
        }),
        ('Estados', {
            'fields': ('is_active', 'is_featured', 'is_new')
        }),
        ('Estadísticas', {
            'fields': ('views_count', 'average_rating_display', 'review_count_display', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_featured', 'unmark_as_featured', 'mark_as_active', 'mark_as_inactive']
    
    def price_display(self, obj):
        if obj.discount_price:
            return format_html(
                '<span style="text-decoration: line-through;">${}</span><br>'
                '<strong style="color: #e74c3c;">${}</strong> ({}% OFF)',
                obj.price, obj.discount_price, obj.discount_percentage
            )
        return format_html('<strong>${}</strong>', obj.price)
    price_display.short_description = 'Precio'
    
    def final_price_display(self, obj):
        return format_html('<strong>${}</strong>', obj.final_price)
    final_price_display.short_description = 'Precio Final'
    
    def stock_display(self, obj):
        if obj.stock == 0:
            color = '#e74c3c'  # rojo
            icon = '❌'
        elif obj.is_low_stock:
            color = '#f39c12'  # naranja
            icon = '⚠️'
        else:
            color = '#27ae60'  # verde
            icon = '✅'
        return format_html(
            '<span style="color: {};">{} <strong>{}</strong></span>',
            color, icon, obj.stock
        )
    stock_display.short_description = 'Stock'
    
    def stock_status(self, obj):
        if obj.stock == 0:
            return format_html('<span style="color: #e74c3c; font-weight: bold;">SIN STOCK</span>')
        elif obj.is_low_stock:
            return format_html('<span style="color: #f39c12; font-weight: bold;">STOCK BAJO</span>')
        return format_html('<span style="color: #27ae60; font-weight: bold;">EN STOCK</span>')
    stock_status.short_description = 'Estado del Stock'
    
    def average_rating_display(self, obj):
        rating = obj.average_rating
        stars = '⭐' * int(rating)
        return format_html('{} <strong>{}</strong>', stars, rating)
    average_rating_display.short_description = 'Rating Promedio'
    
    def review_count_display(self, obj):
        return format_html('<strong>{}</strong> reviews', obj.review_count)
    review_count_display.short_description = 'Reviews'
    
    # Actions personalizadas
    def mark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} productos marcados como destacados.')
    mark_as_featured.short_description = '⭐ Marcar como destacado'
    
    def unmark_as_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} productos desmarcados como destacados.')
    unmark_as_featured.short_description = '☆ Desmarcar como destacado'
    
    def mark_as_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} productos activados.')
    mark_as_active.short_description = '✅ Activar productos'
    
    def mark_as_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} productos desactivados.')
    mark_as_inactive.short_description = '❌ Desactivar productos'


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """
    Admin para imágenes de productos
    """
    list_display = ('product', 'image_preview', 'is_primary', 'order', 'created_at')
    list_filter = ('is_primary', 'created_at')
    search_fields = ('product__name', 'alt_text')
    list_editable = ('is_primary', 'order')
    readonly_fields = ('image_preview_large', 'created_at')
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="80" height="80" style="object-fit: cover;" />', obj.image.url)
        return "No hay imagen"
    image_preview.short_description = 'Vista previa'
    
    def image_preview_large(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="400" />', obj.image.url)
        return "No hay imagen"
    image_preview_large.short_description = 'Imagen'


@admin.register(ProductSpecification)
class ProductSpecificationAdmin(admin.ModelAdmin):
    """
    Admin para especificaciones
    """
    list_display = ('product', 'name', 'value', 'order')
    list_filter = ('product__category',)
    search_fields = ('product__name', 'name', 'value')
    list_editable = ('order',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Admin para reviews
    """
    list_display = (
        'product', 'user', 'rating_display', 'is_verified_purchase', 
        'is_approved', 'created_at'
    )
    list_filter = (
        'rating', 'is_verified_purchase', 'is_approved', 'created_at'
    )
    search_fields = ('product__name', 'user__username', 'title', 'comment')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_approved',)
    
    fieldsets = (
        ('Información de Review', {
            'fields': ('product', 'user', 'rating', 'title', 'comment')
        }),
        ('Estado', {
            'fields': ('is_verified_purchase', 'is_approved')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_reviews', 'disapprove_reviews']
    
    def rating_display(self, obj):
        stars = '⭐' * obj.rating
        return format_html('{} <strong>({})</strong>', stars, obj.rating)
    rating_display.short_description = 'Calificación'
    
    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} reviews aprobadas.')
    approve_reviews.short_description = '✅ Aprobar reviews'
    
    def disapprove_reviews(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} reviews desaprobadas.')
    disapprove_reviews.short_description = '❌ Desaprobar reviews'


# Personalizar el admin site
admin.site.site_header = 'Home Store - Administración'
admin.site.site_title = 'Home Store Admin'
admin.site.index_title = 'Panel de Control'