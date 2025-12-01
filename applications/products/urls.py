from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet,
    BrandViewSet,
    MaterialViewSet,
    ProductViewSet,
    ReviewViewSet
)

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('brands', BrandViewSet, basename='brand')
router.register('materials', MaterialViewSet, basename='material')
router.register('reviews', ReviewViewSet, basename='review')
router.register('', ProductViewSet, basename='product')  # productos en la raíz

urlpatterns = [
    path('', include(router.urls)),
]