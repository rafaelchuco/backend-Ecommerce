# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, Address


class UserProfileInline(admin.StackedInline):
    """
    Inline para mostrar el perfil en el admin de User
    """
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil'
    fk_name = 'user'


class AddressInline(admin.TabularInline):
    """
    Inline para mostrar direcciones en el admin de User
    """
    model = Address
    extra = 0
    fields = ('label', 'address_line1', 'city', 'is_default')


class CustomUserAdmin(BaseUserAdmin):
    """
    Extender el admin de User para incluir perfil y direcciones
    """
    inlines = (UserProfileInline, AddressInline)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')


# Re-registrar UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin para UserProfile
    """
    list_display = ('user', 'phone', 'default_city', 'created_at')
    list_filter = ('created_at', 'default_country')
    search_fields = ('user__username', 'user__email', 'phone')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Información de Contacto', {
            'fields': ('phone', 'birth_date', 'avatar')
        }),
        ('Dirección por Defecto', {
            'fields': (
                'default_address_line1', 'default_address_line2',
                'default_city', 'default_state', 'default_postal_code', 'default_country'
            )
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """
    Admin para Address
    """
    list_display = ('label', 'user', 'city', 'is_default', 'created_at')
    list_filter = ('is_default', 'country', 'created_at')
    search_fields = ('user__username', 'label', 'city', 'address_line1')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Usuario', {
            'fields': ('user', 'label', 'is_default')
        }),
        ('Dirección', {
            'fields': (
                'address_line1', 'address_line2',
                'city', 'state', 'postal_code', 'country'
            )
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )