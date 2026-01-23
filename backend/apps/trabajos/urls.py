# backend/apps/trabajos/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TrabajoInvestigacionViewSet, ConfiguracionCarreraViewSet

router = DefaultRouter()
# Esto registrará la ruta /api/v1/trabajos/

router.register(r'configuracion-carreras', ConfiguracionCarreraViewSet, basename='configuracion-carreras')

urlpatterns = [
    path('', include(router.urls)),
]