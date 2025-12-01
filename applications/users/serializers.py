from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import UserProfile, Address
from .validators import validate_age, validate_password_simple

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Personalizamos el login para resolver el problema Username vs Email.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacemos campos opcionales para aceptar cualquier combinación
        self.fields['username'] = serializers.CharField(required=False)
        self.fields['email'] = serializers.EmailField(required=False)

    def validate(self, attrs):
        # 1. Recuperar lo que escribió el usuario (puede venir en 'username' o 'email')
        login_input = attrs.get('username') or attrs.get('email')
        password = attrs.get('password')

        # 2. Si parece un correo, buscamos el USERNAME REAL asociado a ese correo
        if login_input and '@' in str(login_input):
            try:
                user_obj = User.objects.get(email=login_input)
                # ¡AQUÍ ESTÁ LA MAGIA! Reemplazamos el email por el username real (ej: 'nene2550')
                attrs['username'] = user_obj.username
            except User.DoesNotExist:
                # Si no existe el correo, dejamos que falle normalmente más adelante
                pass
        
        # Limpieza: quitamos 'email' si existe para que la clase padre no se confunda
        if 'email' in attrs:
            del attrs['email']

        # 3. Ahora attrs tiene el username correcto (ej: 'nene2550') y la pass.
        # Llamamos a la validación original de SimpleJWT
        try:
            data = super().validate(attrs)
        except Exception as e:
            # Si falla aquí es contraseña incorrecta o usuario no activo
            raise serializers.ValidationError("Credenciales inválidas o cuenta inactiva.")

        # 4. Agregar datos del usuario a la respuesta para el frontend
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
        }
        
        return {
            'tokens': {
                'access': data['access'],
                'refresh': data['refresh']
            },
            'user': data['user']
        }


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password_simple], style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'}, label="Confirmar contraseña")
    email = serializers.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email ya está registrado.")
        return value.lower()
    
    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Este nombre de usuario ya existe.")
        return value
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    full_name = serializers.ReadOnlyField()
    has_default_address = serializers.ReadOnlyField()
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'phone', 'birth_date', 'avatar',
            'default_address_line1', 'default_address_line2',
            'default_city', 'default_state', 'default_postal_code', 'default_country',
            'has_default_address', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_birth_date(self, value):
        if value:
            try:
                validate_age(value)
            except DjangoValidationError as e:
                raise serializers.ValidationError(str(e))
        return value


class UserUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'birth_date', 'avatar',
            'default_address_line1', 'default_address_line2',
            'default_city', 'default_state', 'default_postal_code', 'default_country'
        ]
    
    def validate_birth_date(self, value):
        if value:
            try:
                validate_age(value)
            except DjangoValidationError as e:
                raise serializers.ValidationError(str(e))
        return value
    
    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        if user_data:
            user = instance.user
            user.first_name = user_data.get('first_name', user.first_name)
            user.last_name = user_data.get('last_name', user.last_name)
            user.save()
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class AddressSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    
    class Meta:
        model = Address
        fields = [
            'id', 'user', 'label', 'address_line1', 'address_line2',
            'city', 'state', 'postal_code', 'country', 'is_default',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_label(self, value):
        user = self.context['request'].user
        if self.instance:
            if Address.objects.filter(user=user, label__iexact=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("Ya tienes una dirección con esta etiqueta.")
        else:
            if Address.objects.filter(user=user, label__iexact=value).exists():
                raise serializers.ValidationError("Ya tienes una dirección con esta etiqueta.")
        return value


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password_simple], style={'input_type': 'password'})
    new_password2 = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'}, label="Confirmar nueva contraseña")
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("La contraseña actual es incorrecta.")
        return value
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "Las nuevas contraseñas no coinciden."})
        return attrs
    
    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No existe un usuario con este email.")
        return value.lower()


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password_simple], style={'input_type': 'password'})
    new_password2 = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "Las contraseñas no coinciden."})
        return attrs
