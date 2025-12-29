# backend/apps/usuarios/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UsuarioRegistroView, UsuarioLoginView, UsuarioViewSet

router = DefaultRouter()
# El router gestionará las rutas automáticas como /auth/usuarios/perfil/
# Registramos el ViewSet con el prefijo 'usuarios'
router.register(r'usuarios', UsuarioViewSet, basename='usuarios')

urlpatterns = [
    # Login (Ruta: /api/v1/auth/login/)
    path('login/', UsuarioLoginView.as_view(), name='token_obtain_pair'),
    
    # Registro (Ruta: /api/v1/auth/register/)
    # Usamos UsuarioRegistroView que solo tiene el método 'create'
    path('register/', UsuarioRegistroView.as_view({'post': 'create'}), name='registro'),
    
    # Incluimos el router que ya contiene la acción 'perfil' 
    # (Ruta: /api/v1/auth/usuarios/perfil/)
    path('', include(router.urls)),
]