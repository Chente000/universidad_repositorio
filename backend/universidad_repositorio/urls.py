# backend/universidad_repositorio/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.http import JsonResponse
from .health_views import health_check

# Importar viewsets
from apps.usuarios.views import UsuarioRegistroView, UsuarioLoginView, UsuarioViewSet
from apps.trabajos.views import TrabajoInvestigacionViewSet, ConfiguracionCarreraViewSet
from apps.trabajos.views import aplicar_ia_callback
from apps.comentarios.views import ComentarioViewSet, RetroalimentacionIAViewSet

# Crear router
router = DefaultRouter()

# Registrar viewsets
router.register(r'usuarios', UsuarioViewSet, basename='usuarios')
router.register(r'trabajos', TrabajoInvestigacionViewSet, basename='trabajos')
router.register(r'carreras', ConfiguracionCarreraViewSet, basename='carreras')
router.register(r'comentarios', ComentarioViewSet, basename='comentarios')
router.register(r'retroalimentacion-ia', RetroalimentacionIAViewSet, basename='retroalimentacion-ia')

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API v1
    # Callback directo desde el servicio de IA (fallback si router no expone la acción)
    path('api/v1/trabajos/<int:pk>/aplicar_ia/', aplicar_ia_callback, name='aplicar_ia_callback'),
    path('api/v1/', (include(router.urls))), # <-- CAMBIO CRÍTICO AQUÍ    
    # Autenticación
    path('api/v1/auth/register/', UsuarioRegistroView.as_view({'post': 'create'}), name='registro'),
    path('api/v1/auth/login/', UsuarioLoginView.as_view(), name='login'),
    path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Core API (nuevo)
    path('api/v1/core/', include('apps.api_v1.urls')),

    # Health check
    path('api/v1/health/', health_check, name='health'),
    # Callback directo desde el servicio de IA (fallback si router no expone la acción)
    path('api/v1/trabajos/<int:pk>/aplicar_ia/', aplicar_ia_callback, name='aplicar_ia_callback'),
]

# Servir archivos estáticos en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)