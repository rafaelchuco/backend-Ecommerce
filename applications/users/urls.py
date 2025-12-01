from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    UserRegistrationAPIView,
    LoginAPIView,  # <--- IMPORTANTE
    UserProfileViewSet,
    ChangePasswordAPIView,
    PasswordResetRequestAPIView,
    PasswordResetConfirmAPIView,
    AddressViewSet
)

router = DefaultRouter()
router.register('addresses', AddressViewSet, basename='address')

urlpatterns = [
    # Autenticación JWT Personalizada (ambos endpoints funcionan)
    path('login/', LoginAPIView.as_view(), name='user-login'),  # Para frontend
    path('token/', LoginAPIView.as_view(), name='user-token'),  # Para compatibilidad SimpleJWT
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Registro
    path('register/', UserRegistrationAPIView.as_view(), name='user-register'),
    
    # Perfil
    path('profile/', UserProfileViewSet.as_view({
        'get': 'list',
        'put': 'update',
        'patch': 'partial_update'
    }), name='user-profile'),
    
    # Contraseñas
    path('change-password/', ChangePasswordAPIView.as_view(), name='change-password'),
    path('reset-password/', PasswordResetRequestAPIView.as_view(), name='reset-password'),
    path('reset-password-confirm/', PasswordResetConfirmAPIView.as_view(), name='reset-password-confirm'),
    
    # Direcciones
    path('', include(router.urls)),
]
