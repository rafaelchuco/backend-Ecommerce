import django_filters
from .models import Order

class OrderFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name='status', lookup_expr='iexact')
    date_min = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    date_max = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    payment_method = django_filters.CharFilter(field_name='payment_method', lookup_expr='iexact')

    class Meta:
        model = Order
        fields = ['status', 'payment_method', 'date_min', 'date_max']
