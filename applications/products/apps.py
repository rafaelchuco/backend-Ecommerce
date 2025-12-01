from django.apps import AppConfig


class ProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'applications.products'
    verbose_name = 'Catálogo de Productos'
    
    def ready(self):
        """
        Importa las señales cuando la app está lista
        """
        import applications.products.signals
