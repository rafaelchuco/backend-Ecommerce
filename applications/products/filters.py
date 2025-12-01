import django_filters
from .models import Product, Category


class ProductFilter(django_filters.FilterSet):
    """
    Filtros avanzados para productos
    """
    # Filtros de texto
    name = django_filters.CharFilter(lookup_expr='icontains')
    search = django_filters.CharFilter(method='search_products')
    
    # Filtros de relaciones
    category = django_filters.CharFilter(field_name='category__slug')
    brand = django_filters.CharFilter(field_name='brand__slug')
    materials = django_filters.CharFilter(method='filter_by_materials')
    
    # Filtros de precio
    min_price = django_filters.NumberFilter(method='filter_min_price')
    max_price = django_filters.NumberFilter(method='filter_max_price')
    price_range = django_filters.RangeFilter(method='filter_price_range')
    
    # Filtros de características
    color = django_filters.CharFilter(lookup_expr='iexact')
    assembly_required = django_filters.BooleanFilter()
    
    # Filtros de estado
    is_featured = django_filters.BooleanFilter()
    is_new = django_filters.BooleanFilter()
    in_stock = django_filters.BooleanFilter(method='filter_in_stock')
    
    # Ordenamiento
    ordering = django_filters.OrderingFilter(
        fields=(
            ('price', 'price'),
            ('created_at', 'created_at'),
            ('name', 'name'),
            ('views_count', 'views'),
        )
    )
    
    class Meta:
        model = Product
        fields = ['category', 'brand', 'color', 'is_featured', 'is_new']
    
    def search_products(self, queryset, name, value):
        """
        Búsqueda general en nombre, descripción y SKU
        """
        return queryset.filter(
            models.Q(name__icontains=value) |
            models.Q(description__icontains=value) |
            models.Q(sku__icontains=value)
        )
    
    def filter_by_materials(self, queryset, name, value):
        """
        Filtrar por materiales (puede ser múltiple separado por comas)
        """
        materials = value.split(',')
        return queryset.filter(materials__name__in=materials).distinct()
    
    def filter_min_price(self, queryset, name, value):
        """
        Filtra productos con precio mayor o igual al valor
        """
        from django.db.models import Q, F
        return queryset.filter(
            Q(discount_price__gte=value, discount_price__isnull=False) |
            Q(price__gte=value, discount_price__isnull=True)
        )
    
    def filter_max_price(self, queryset, name, value):
        """
        Filtra productos con precio menor o igual al valor
        """
        from django.db.models import Q, F
        return queryset.filter(
            Q(discount_price__lte=value, discount_price__isnull=False) |
            Q(price__lte=value, discount_price__isnull=True)
        )
    
    def filter_price_range(self, queryset, name, value):
        """
        Filtra por rango de precio
        """
        if value:
            return self.filter_min_price(
                self.filter_max_price(queryset, name, value.stop),
                name,
                value.start
            )
        return queryset
    
    def filter_in_stock(self, queryset, name, value):
        """
        Filtra productos en stock
        """
        if value:
            return queryset.filter(stock__gt=0)
        return queryset


from django.db import models