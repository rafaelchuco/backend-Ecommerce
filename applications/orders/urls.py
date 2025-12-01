from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OrderViewSet,
    validate_coupon,
    create_payment_intent,
    confirm_payment,
)

router = DefaultRouter()
router.register('', OrderViewSet, basename='orders')

urlpatterns = [
    path('validate-coupon/', validate_coupon, name='validate-coupon'),
    path('create-payment-intent/', create_payment_intent, name='create-payment-intent'),
    path('confirm-payment/', confirm_payment, name='confirm-payment'),
    path('', include(router.urls)),
]
