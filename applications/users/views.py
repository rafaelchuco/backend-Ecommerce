from django.shortcuts import render
from rest_framework import generics, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView  # <--- IMPORTANTE

from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from drf_spectacular.utils import extend_schema

from .models import UserProfile, Address
from .serializers import (
    MyTokenObtainPairSerializer,  # <--- Asegúrate de que este serializer exista en serializers.py
    UserRegistrationSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
    AddressSerializer,
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer
)
from .permissions import IsOwner, IsOwnerOrAdmin


# --- ESTA ES LA CLASE QUE TE FALTABA ---
@extend_schema(tags=['Users'])
class LoginAPIView(TokenObtainPairView):
    """
    Vista de login personalizada que usa nuestro serializer
    para aceptar email/username y devolver los datos del usuario.
    """
    serializer_class = MyTokenObtainPairSerializer


@extend_schema(tags=['Users'])
class UserRegistrationAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        refresh = RefreshToken.for_user(user)
        
        try:
            send_mail(
                subject='¡Bienvenido a Home Store!',
                message=f'Hola {user.first_name},\n\nGracias por registrarte.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
        except:
            pass
        
        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'message': 'Usuario registrado exitosamente'
        }, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Users'])
class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserProfileSerializer
    
    def get_object(self):
        return self.request.user.profile
    
    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        return Response({'detail': 'No permitido'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def destroy(self, request, *args, **kwargs):
        return Response({'detail': 'No permitido'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@extend_schema(tags=['Users'])
class ChangePasswordAPIView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]
    
    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Contraseña actualizada'}, status=status.HTTP_200_OK)


@extend_schema(tags=['Users'])
class PasswordResetRequestAPIView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # URL hardcodeada para evitar errores de configuración en desarrollo
        reset_url = f"http://localhost:3000/reset-password/{uid}/{token}/"
        
        try:
            send_mail(
                subject='Recuperación de contraseña',
                message=f'Para resetear tu clave: {reset_url}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            return Response({'message': 'Email enviado'}, status=status.HTTP_200_OK)
        except Exception:
            return Response({'error': 'Error enviando email'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(tags=['Users'])
class PasswordResetConfirmAPIView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]
    
    def post(self, request):
        uid = request.data.get('uid')
        token = request.data.get('token')
        
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'error': 'Token inválido'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not default_token_generator.check_token(user, token):
            return Response({'error': 'Token inválido'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({'message': 'Contraseña restablecida'}, status=status.HTTP_200_OK)


@extend_schema(tags=['Users'])
class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        address = self.get_object()
        address.is_default = True
        address.save()
        return Response({'message': 'Dirección predeterminada actualizada'}, status=status.HTTP_200_OK)
