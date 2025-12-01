from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Rutas de tus apps
    path('api/users/', include('applications.users.urls')),
    path('api/cart/', include('applications.cart.urls')),
    path('api/orders/', include('applications.orders.urls')),
    path('api/products/', include('applications.products.urls')),

    # Schema (archivo OpenAPI)
    path('schema/', SpectacularAPIView.as_view(), name='schema'),

    # Swagger UI
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Redoc (opcional)
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
