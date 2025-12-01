from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartViewSet, WishlistViewSet

router = DefaultRouter()
router.register(r'wishlist', WishlistViewSet, basename='wishlist')

urlpatterns = [
    path('', CartViewSet.as_view({'get': 'list'}), name='cart-detail'),
    path('items/', CartViewSet.as_view({'post': 'add_item'}), name='cart-add-item'),
    path('<int:pk>/update/', CartViewSet.as_view({'put': 'update_item', 'patch': 'update_item'}), name='cart-update-item'),
    path('<int:pk>/remove/', CartViewSet.as_view({'delete': 'remove_item'}), name='cart-remove-item'),
    path('clear/', CartViewSet.as_view({'delete': 'clear_cart'}), name='cart-clear'),
    path('', include(router.urls)),
]
