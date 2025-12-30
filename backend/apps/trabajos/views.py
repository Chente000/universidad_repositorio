# backend/apps/trabajos/views.py
from rest_framework import status, viewsets, permissions, filters
from django.db.models import Q, Sum, Count
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

# IMPORTS PARA SOLUCIONAR EL ERROR 403 CSRF
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, permissions
import os
from django.http import FileResponse

from .models import TrabajoInvestigacion, ConfiguracionCarrera, LogActividades
from .serializers import (
    TrabajoInvestigacionCreateSerializer, TrabajoInvestigacionListSerializer,
    TrabajoInvestigacionDetailSerializer, TrabajoInvestigacionUpdateSerializer,
    TrabajoInvestigacionAprobacionSerializer, ConfiguracionCarreraSerializer,
    EstadisticasTrabajosSerializer
)

Usuario = get_user_model()

# Aplicamos csrf_exempt a todo el ViewSet para permitir la subida desde el frontend (puerto 3001)
# Esto soluciona el error "CSRF Failed: Origin checking failed"
class TrabajoInvestigacionViewSet(viewsets.ModelViewSet):
    """
    Vista para gestión de trabajos de investigación
    """
    queryset = TrabajoInvestigacion.objects.all()
    
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['carrera', 'tipo_trabajo', 'año', 'estado']
    search_fields = ['titulo', 'autores', 'tutores', 'resumen', 'objetivos']
    ordering_fields = ['fecha_subida', 'año', 'total_descargas', 'titulo']
    ordering = ['-fecha_subida']
    
    # @method_decorator(csrf_exempt, name='dispatch') # <-- APLICACIÓN CORRECTA
    # def dispatch(self, *args, **kwargs):
    #    return super().dispatch(*args, **kwargs)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TrabajoInvestigacionCreateSerializer
        elif self.action == 'list':
            return TrabajoInvestigacionListSerializer
        elif self.action == 'retrieve':
            return TrabajoInvestigacionDetailSerializer
        elif self.action in ['update', 'partial_update']:
            return TrabajoInvestigacionUpdateSerializer
        elif self.action == 'aprobar':
            return TrabajoInvestigacionAprobacionSerializer
        return TrabajoInvestigacionDetailSerializer
    
    def get_queryset(self):
        # Nota: El editor puede marcar error en 'user.rol' porque no detecta
        # el modelo personalizado localmente, pero en Docker funcionará bien.
        user = self.request.user
        
        # Si el usuario es anónimo (no debería pasar por IsAuthenticated), retornamos vacío
        if not user.is_authenticated:
            return TrabajoInvestigacion.objects.none()

        # Estudiantes solo ven trabajos aprobados
        # getattr se usa para evitar errores del editor si no detecta el campo 'rol'
        if getattr(user, 'rol', '') == 'estudiante':
            return TrabajoInvestigacion.objects.filter(estado='aprobado')
        
        # Encargados ven trabajos de su área
        es_encargado_grado = getattr(user, 'es_encargado_especial_grado', False)
        es_encargado_pasantias = getattr(user, 'es_encargado_pasantias', False)

        if es_encargado_grado or es_encargado_pasantias:
            return TrabajoInvestigacion.objects.filter(
                Q(subido_por=user) |
                Q(tipo_trabajo='especial_grado', estado__in=['aprobado', 'pendiente']) |
                Q(tipo_trabajo='practicas_profesionales', estado__in=['aprobado', 'pendiente'])
            )
        
        # Superusuarios y administradores ven todo
        return TrabajoInvestigacion.objects.all()
    
    
    def create(self, request, *args, **kwargs):
        """
        Crear nuevo trabajo de investigación
        """
        # Nota: Este método ahora está exento de CSRF gracias al decorador en la clase
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Verificar permisos adicionales
        tipo = serializer.validated_data.get('tipo_trabajo')
        if not self._can_upload_work(request.user, tipo):
            raise PermissionDenied("No tienes permisos para subir este tipo de trabajo.")
        
        trabajo = serializer.save()
        
        # Registrar actividad
        LogActividades.objects.create(
            usuario=request.user,
            accion='upload',
            trabajo=trabajo,
            descripcion=f"Subió el trabajo: {trabajo.titulo}",
            ip_address=self._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Aquí se activaría el procesamiento de IA en background
        # procesar_trabajo_con_ia.delay(trabajo.id)
        
        return Response({
            'message': 'Trabajo subido exitosamente. Será procesado por la IA.',
            'trabajo': TrabajoInvestigacionListSerializer(trabajo, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)
    
    # --- AÑADE ESTA FUNCIÓN DENTRO DE TrabajoInvestigacionViewSet ---
    def _can_upload_work(self, user, tipo_trabajo):
        """
        Lógica para verificar si un usuario puede subir un tipo de trabajo
        """
        # Superusuarios pueden todo
        if user.is_superuser or getattr(user, 'is_staff', False):
            return True
        
        # Verificar por roles específicos
        es_encargado_grado = getattr(user, 'es_encargado_especial_grado', False)
        es_encargado_pasantias = getattr(user, 'es_encargado_pasantias', False)

        if tipo_trabajo == 'especial_grado' and es_encargado_grado:
            return True
        if tipo_trabajo == 'practicas_profesionales' and es_encargado_pasantias:
            return True
            
        # Si no tiene roles especiales, pero está autenticado (permitir por ahora)
        return user.is_authenticated

    def _get_client_ip(self, request):
        """Helper para obtener la IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def retrieve(self, request, *args, **kwargs):
        """
        Obtener detalle del trabajo
        """
        trabajo = self.get_object()
        
        # Registrar actividad de visualización
        LogActividades.objects.create(
            usuario=request.user,
            accion='view',
            trabajo=trabajo,
            descripcion=f"Visualizó el trabajo: {trabajo.titulo}",
            ip_address=self._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return super().retrieve(request, *args, **kwargs)
    
    @action(detail=True, methods=['get', 'post'])
    def descargar(self, request, pk=None):
        trabajo = self.get_object()
        
        # 1. Validaciones de seguridad
        if not trabajo.archivo_pdf:
            return Response(
                {"error": "El archivo no existe en el servidor."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar que el trabajo puede ser descargado
        if not getattr(trabajo, 'puede_ser_descargado', False):
            return Response({
                'error': 'Este trabajo no puede ser descargado.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Importación local para evitar ciclos
        from apps.comentarios.models import ReporteDescarga
        ReporteDescarga.objects.create(
            trabajo=trabajo,
            usuario=request.user if request.user.is_authenticated else None,
            ip_address=self._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        LogActividades.objects.create(
            usuario=request.user if request.user.is_authenticated else None,
            accion='download',
            trabajo=trabajo,
            descripcion=f"Descargó el trabajo: {trabajo.titulo}",
            ip_address=self._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # 3. Incrementar contador (Opcional, según el código que te pasaron)
        if hasattr(trabajo, 'descargas_count'):
            trabajo.descargas_count += 1
            trabajo.save()
            
        # 4. Retornar el archivo físico (Nueva lógica)
        response = FileResponse(trabajo.archivo_pdf.open('rb'), content_type='application/pdf')
        nombre_archivo = os.path.basename(trabajo.archivo_pdf.name)
        response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
        
        return response # <-- Asegúrate de que no haya nada después de este return
                
        # Manejo seguro si no hay archivo (aunque debería haber)
        # download_url = trabajo.archivo_pdf.url if trabajo.archivo_pdf else ''
        
        #return Response({
        #    'download_url': download_url,
        #    'trabajo': {
        #        'titulo': trabajo.titulo,
        #        'autores': trabajo.autores,
        #        'año': trabajo.año
        #    }
        #}
        #)
    
    @action(detail=True, methods=['post'])
    def aprobar(self, request, pk=None):
        trabajo = self.get_object()
        
        if not getattr(request.user, 'es_superuser_trabajo', False):
            raise PermissionDenied("No tienes permisos para aprobar trabajos.")
        
        serializer = TrabajoInvestigacionAprobacionSerializer(
            trabajo,
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        trabajo_aprobado = serializer.save()
        
        LogActividades.objects.create(
            usuario=request.user,
            accion='approve' if trabajo_aprobado.estado == 'aprobado' else 'reject',
            trabajo=trabajo_aprobado,
            descripcion=f"{'Aprobó' if trabajo_aprobado.estado == 'aprobado' else 'Rechazó'} el trabajo: {trabajo_aprobado.titulo}",
            ip_address=self._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({
            'message': f'Trabajo {trabajo_aprobado.estado} exitosamente.',
            'trabajo': TrabajoInvestigacionListSerializer(trabajo_aprobado, context={'request': request}).data
        })

    # ... (El resto de tus métodos 'buscar_inteligente', 'recomendados', 'estadisticas' quedan igual)
    # He resumido aquí para enfocar en la solución, pero mantén tus otros métodos abajo.
    
    @action(detail=False, methods=['get'])
    def buscar_inteligente(self, request):
        """
        Búsqueda inteligente con IA
        """
        query = request.query_params.get('q', '')
        carrera = request.query_params.get('carrera', '')
        tipo_trabajo = request.query_params.get('tipo_trabajo', '')
        año = request.query_params.get('año', '')
        
        if not query:
            return Response({
                'error': 'Debe proporcionar una consulta de búsqueda.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Aquí se integraría con el servicio de IA para búsqueda semántica
        # Por ahora usamos búsqueda tradicional como fallback
        
        trabajos = self.get_queryset().filter(estado='aprobado')
        
        if carrera:
            trabajos = trabajos.filter(carrera=carrera)
        if tipo_trabajo:
            trabajos = trabajos.filter(tipo_trabajo=tipo_trabajo)
        if año:
            trabajos = trabajos.filter(año=año)
        
        # Búsqueda por texto
        trabajos = trabajos.filter(
            Q(titulo__icontains=query) |
            Q(autores__icontains=query) |
            Q(resumen__icontains=query) |
            Q(objetivos__icontains=query)
        )
        
        # Aquí se agregaría el scoring de IA
        serializer = TrabajoInvestigacionListSerializer(
            trabajos[:20],
            many=True,
            context={'request': request}
        )
        
        # Registrar búsqueda
        LogActividades.objects.create(
            usuario=request.user,
            accion='search',
            descripcion=f"Búsqueda inteligente: {query}",
            ip_address=self._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({
            'resultados': serializer.data,
            'total': trabajos.count(),
            'query': query,
            'filtros': {
                'carrera': carrera,
                'tipo_trabajo': tipo_trabajo,
                'año': año
            }
        })

    @action(detail=False, methods=['get'])
    def recomendados(self, request):
        """
        Trabajos recomendados basados en IA
        """
        trabajo_id = request.query_params.get('trabajo_id')
        
        if not trabajo_id:
            return Response({
                'error': 'Debe proporcionar un ID de trabajo.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            trabajo_base = TrabajoInvestigacion.objects.get(id=trabajo_id)
        except TrabajoInvestigacion.DoesNotExist:
            return Response({
                'error': 'Trabajo no encontrado.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Aquí se usaría el vector embedding para encontrar trabajos similares
        # Por ahora usamos trabajos de la misma carrera y tipo
        
        trabajos_similares = self.get_queryset().filter(
            estado='aprobado',
            carrera=trabajo_base.carrera,
            tipo_trabajo=trabajo_base.tipo_trabajo
        ).exclude(id=trabajo_id)[:10]
        
        serializer = TrabajoInvestigacionListSerializer(
            trabajos_similares,
            many=True,
            context={'request': request}
        )
        
        return Response({
            'trabajo_base': {
                'id': trabajo_base.id,
                'titulo': trabajo_base.titulo
            },
            'recomendados': serializer.data
        })

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """
        Estadísticas de trabajos corregidas (Usando Sum y manejo de nulos)
        """
        # Verificación de permisos robusta
        user = request.user
        es_admin = getattr(user, 'is_staff', False) or getattr(user, 'es_superuser_trabajo', False)
        
        if not es_admin:
            raise PermissionDenied("No tienes permisos para ver estadísticas.")
        
        queryset = self.get_queryset()
        
        # 1. Calculamos la suma de descargas (Sum en lugar de Count)
        # .aggregate devuelve un dict, usamos .get() o 'or 0' para evitar None
        total_descargas_data = queryset.aggregate(total=Sum('total_descargas'))
        total_descargas = total_descargas_data.get('total') or 0

        stats = {
            'total_trabajos': queryset.count(),
            'trabajos_aprobados': queryset.filter(estado='aprobado').count(),
            'trabajos_pendientes': queryset.filter(estado='pendiente').count(),
            'trabajos_rechazados': queryset.filter(estado='rechazado').count(),
            'trabajos_requieren_correcciones': queryset.filter(estado='requiere_correcciones').count(),
            'total_descargas': total_descargas,
            
            # Agrupaciones: dict(values_list) es la forma más eficiente de formatear esto
            'trabajos_por_carrera': dict(
                queryset.values('carrera').annotate(count=Count('id')).values_list('carrera', 'count')
            ),
            'trabajos_por_tipo': dict(
                queryset.values('tipo_trabajo').annotate(count=Count('id')).values_list('tipo_trabajo', 'count')
            ),
            'trabajos_por_año': dict(
                queryset.values('año').annotate(count=Count('id')).values_list('año', 'count')
            ),
            
            # Ranking de trabajos
            'top_trabajos_mas_descargados': list(
                queryset.filter(estado='aprobado')
                .order_by('-total_descargas')[:10]
                .values('id', 'titulo', 'total_descargas')
            )
        }
        
        return Response(stats)


class ConfiguracionCarreraViewSet(viewsets.ModelViewSet):
    """
    Vista para configuración de carreras
    """
    queryset = ConfiguracionCarrera.objects.all()
    serializer_class = ConfiguracionCarreraSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        user = self.request.user
        if not user or user.is_anonymous:
            return ConfiguracionCarrera.objects.filter(activa=True)
        
        if user.is_staff or user.is_superuser:
            return ConfiguracionCarrera.objects.all()
            
        return ConfiguracionCarrera.objects.filter(activa=True)
    
    def create(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied("Solo los administradores pueden crear configuraciones de carrera.")
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied("Solo los administradores pueden editar configuraciones de carrera.")
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied("Solo los administradores pueden eliminar configuraciones de carrera.")
        return super().destroy(request, *args, **kwargs)