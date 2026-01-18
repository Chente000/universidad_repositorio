# backend/apps/usuarios/views.py
from datetime import timedelta
from django.utils import timezone
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import Usuario
from .serializers import (
    UsuarioRegistroSerializer, UsuarioLoginSerializer, UsuarioPerfilSerializer,
    UsuarioListSerializer, UsuarioUpdateSerializer, CambioPasswordSerializer
)

UsuarioModel = get_user_model()


class UsuarioRegistroView(viewsets.GenericViewSet):
    """
    Vista para registro de usuarios
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = UsuarioRegistroSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generar tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UsuarioPerfilSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class UsuarioLoginView(TokenObtainPairView):
    """
    Vista para login de usuarios
    """
    serializer_class = UsuarioLoginSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UsuarioPerfilSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    Vista para gestión de usuarios
    """
    queryset = Usuario.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['carrera', 'rol', 'activo']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'cedula']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return UsuarioListSerializer
        elif self.action == 'retrieve':
            return UsuarioPerfilSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return UsuarioUpdateSerializer
        return UsuarioPerfilSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        # 1. Si es superusuario o admin, ve absolutamente todo
        if user.is_superuser or user.is_staff:
            return Usuario.objects.all()
        
        # 2. EXCEPCIÓN PARA SUBIR TRABAJO: 
        # Si un encargado pide la lista de estudiantes, se los mostramos todos.
        rol_filtro = self.request.query_params.get('rol')
        if rol_filtro == 'estudiante' and (user.es_encargado_especial_grado or user.es_encargado_pasantias):
            return Usuario.objects.filter(rol='estudiante')

        # 3. Los estudiantes solo pueden ver su propio perfil
        if user.rol == 'estudiante':
            return Usuario.objects.filter(id=user.id)
        
        # 4. Filtro por defecto para encargados (ver su carrera)
        if user.es_encargado_especial_grado or user.es_encargado_pasantias:
            return Usuario.objects.filter(
                Q(carrera=user.carrera) | Q(id=user.id)
            )
        
        return Usuario.objects.all()
    
    @action(detail=False, methods=['post'])
    def cambiar_password(self, request):
        """
        Cambiar contraseña del usuario actual
        """
        serializer = CambioPasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'message': 'Contraseña actualizada exitosamente.'
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def perfil(self, request):
        """
        Obtener perfil del usuario actual
        """
        serializer = UsuarioPerfilSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def activar(self, request, pk=None):
        """
        Activar usuario (solo administradores)
        """
        if not request.user.is_staff:
            return Response({
                'error': 'No tienes permisos para activar usuarios.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        user = self.get_object()
        user.activo = True
        user.save()
        
        return Response({
            'message': f'Usuario {user.username} activado exitosamente.'
        })
    
    @action(detail=True, methods=['post'])
    def desactivar(self, request, pk=None):
        """
        Desactivar usuario (solo administradores)
        """
        if not request.user.is_staff:
            return Response({
                'error': 'No tienes permisos para desactivar usuarios.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        user = self.get_object()
        user.activo = False
        user.save()
        
        return Response({
            'message': f'Usuario {user.username} desactivado exitosamente.'
        })
    
    @action(detail=True, methods=['post'])
    def asignar_rol(self, request, pk=None):
        """
        Asignar rol a usuario (solo superusuarios)
        """
        if not request.user.is_superuser and not request.user.is_staff:
            return Response({
                'error': 'No tienes permisos para asignar roles.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        nuevo_rol = request.data.get('rol')
        if not nuevo_rol:
            return Response({
                'error': 'Debe especificar el rol.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = self.get_object()
        user.rol = nuevo_rol
        user.save()
        
        return Response({
            'message': f'Rol {nuevo_rol} asignado a {user.username} exitosamente.'
        })
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """
        Estadísticas de usuarios
        """
        if not request.user.is_staff:
            return Response({
                'error': 'No tienes permisos para ver estadísticas.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        from django.db.models import Count
        
        stats = {
            'total_usuarios': Usuario.objects.count(),
            'usuarios_activos': Usuario.objects.filter(activo=True).count(),
            'usuarios_inactivos': Usuario.objects.filter(activo=False).count(),
            'usuarios_por_rol': dict(
                Usuario.objects.values('rol').annotate(
                    count=Count('id')
                ).values_list('rol', 'count')
            ),
            'usuarios_por_carrera': dict(
                Usuario.objects.exclude(carrera__isnull=True).values('carrera').annotate(
                    count=Count('id')
                ).values_list('carrera', 'count')
            ),
            'registros_recientes': Usuario.objects.filter(
                fecha_registro__gte=timezone.now() - timedelta(days=30)
            ).count()
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def roles_disponibles(self, request):
        """
        Obtener roles disponibles
        """
        from universidad_repositorio.settings import USER_ROLES
        return Response(USER_ROLES)
    
    @action(detail=False, methods=['get'])
    def carreras_disponibles(self, request):
        """
        Obtener carreras disponibles
        """
        from universidad_repositorio.settings import CAREERS
        return Response(CAREERS)