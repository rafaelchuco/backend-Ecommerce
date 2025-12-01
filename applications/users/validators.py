from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import date


def validate_age(birth_date):
    """
    Valida que el usuario tenga al menos 18 años
    """
    if birth_date:
        today = date.today()
        age = today.year - birth_date.year - (
            (today.month, today.day) < (birth_date.month, birth_date.day)
        )
        if age < 18:
            raise ValidationError(
                _('Debes tener al menos 18 años para registrarte.')
            )


def validate_phone_number(value):
    """
    Validación adicional para números de teléfono
    """
    if value and not value.replace('+', '').isdigit():
        raise ValidationError(
            _('El número de teléfono solo debe contener dígitos y el símbolo +')
        )


def validate_password_simple(value):
    """
    Validador de contraseña más flexible que el de Django.
    Solo requiere que tenga al menos 6 caracteres.
    Útil para desarrollo y UX mejorada.
    """
    if len(value) < 6:
        raise ValidationError(
            _('La contraseña debe tener al menos 6 caracteres.'),
            code='password_too_short',
            params={'min_length': 6},
        )