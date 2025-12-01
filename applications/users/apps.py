from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'applications.users'
    verbose_name = 'Gestión de Usuarios'
    
    def ready(self):
        """
        Importa las señales cuando la app está lista
        """
        import applications.users.signals