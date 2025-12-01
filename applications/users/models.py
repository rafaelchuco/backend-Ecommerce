from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class UserProfile(models.Model):
    """
    Perfil extendido del usuario con información adicional
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    
    # Información de contacto
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="El número debe estar en formato: '+999999999'. Hasta 15 dígitos."
    )
    phone = models.CharField(
        validators=[phone_regex], 
        max_length=17, 
        blank=True
    )
    
    birth_date = models.DateField(null=True, blank=True)
    
    # Avatar
    avatar = models.ImageField(
        upload_to='avatars/', 
        blank=True, 
        null=True,
        help_text="Foto de perfil del usuario"
    )
    
    # Dirección por defecto
    default_address_line1 = models.CharField(max_length=300, blank=True)
    default_address_line2 = models.CharField(max_length=300, blank=True)
    default_city = models.CharField(max_length=100, blank=True)
    default_state = models.CharField(max_length=100, blank=True)
    default_postal_code = models.CharField(max_length=20, blank=True)
    default_country = models.CharField(max_length=100, default='Chile')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuarios'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Perfil de {self.user.username}"
    
    @property
    def full_name(self):
        """Retorna el nombre completo del usuario"""
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username
    
    @property
    def has_default_address(self):
        """Verifica si el usuario tiene dirección por defecto"""
        return bool(self.default_address_line1 and self.default_city)


class Address(models.Model):
    """
    Múltiples direcciones para un usuario
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='addresses'
    )
    
    label = models.CharField(
        max_length=50,
        help_text="Etiqueta de la dirección (ej: Casa, Trabajo)"
    )
    
    # Datos de la dirección
    address_line1 = models.CharField(max_length=300)
    address_line2 = models.CharField(max_length=300, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='Chile')
    
    # Dirección por defecto
    is_default = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Dirección'
        verbose_name_plural = 'Direcciones'
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        return f"{self.label} - {self.user.username}"
    
    def save(self, *args, **kwargs):
        """
        Si esta dirección se marca como default,
        desmarcar las demás direcciones del usuario
        """
        if self.is_default:
            Address.objects.filter(
                user=self.user, 
                is_default=True
            ).update(is_default=False)
        super().save(*args, **kwargs)