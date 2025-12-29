from django.urls import path, include

urlpatterns = [
    # Resultará en: /api/v1/auth/login/, /api/v1/auth/register/, etc.
    path('auth/', include('apps.usuarios.urls')),
    
    # Resultará en: /api/v1/trabajos/
    path('', include('apps.trabajos.urls')),
]