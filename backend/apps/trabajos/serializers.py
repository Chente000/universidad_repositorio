# backend/apps/trabajos/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from apps.trabajos.models import TrabajoInvestigacion, ConfiguracionCarrera
from apps.comentarios.models import Comentario, CalificacionPromedio

Usuario = get_user_model()


class TrabajoInvestigacionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear trabajos de investigación
    """
    class Meta:
        model = TrabajoInvestigacion
        fields = [
            'titulo', 'autores', 'tutores', 'carrera', 'tipo_trabajo',
            'año', 'archivo_pdf'
        ]
    
    def validate(self, attrs):
        usuario = self.context['request'].user
        tipo_trabajo = attrs.get('tipo_trabajo')
        
        # Verificar permisos según el tipo de trabajo
        if tipo_trabajo == 'especial_grado':
            if not usuario.puede_subir_especial_grado:
                raise serializers.ValidationError(
                    "No tienes permisos para subir trabajos especiales de grado."
                )
        elif tipo_trabajo == 'practicas_profesionales':
            if not usuario.puede_subir_pasantias:
                raise serializers.ValidationError(
                    "No tienes permisos para subir prácticas profesionales."
                )
        
        return attrs
    
    def create(self, validated_data):
        with transaction.atomic():
            # Crear el trabajo
            trabajo = TrabajoInvestigacion.objects.create(
                subido_por=self.context['request'].user,
                **validated_data
            )
            
            # Aquí se activaría el procesamiento de IA en background
            # (esto se haría via Celery)
            
            return trabajo


class TrabajoInvestigacionListSerializer(serializers.ModelSerializer):
    """
    Serializer para listar trabajos de investigación
    """
    carrera_display = serializers.CharField(source='carrera.nombre', read_only=True)
    tipo_trabajo_display = serializers.CharField(source='get_tipo_trabajo_display', read_only=True)
    subido_por_nombre = serializers.CharField(source='subido_por.get_full_name', read_only=True)
    puede_descargar = serializers.SerializerMethodField()
    calificacion_promedio = serializers.SerializerMethodField()
    
    class Meta:
        model = TrabajoInvestigacion
        fields = [
            'id', 'titulo', 'autores', 'año', 'carrera', 'carrera_display',
            'tipo_trabajo', 'tipo_trabajo_display', 'fecha_subida',
            'subido_por_nombre', 'estado', 'total_descargas',
            'puede_descargar', 'calificacion_promedio'
        ]
    
    def get_puede_descargar(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.puede_ser_descargado
        return False
    
    def get_calificacion_promedio(self, obj):
        try:
            promedio = obj.calificacion_promedio
            return {
                'promedio': promedio.promedio_calificacion,
                'total_comentarios': promedio.total_comentarios
            }
        except CalificacionPromedio.DoesNotExist:
            return {'promedio': 0, 'total_comentarios': 0}


class TrabajoInvestigacionDetailSerializer(serializers.ModelSerializer):
    """
    Serializer para detalle de trabajos de investigación
    """
    carrera_display = serializers.CharField(source='carrera.nombre', read_only=True)
    tipo_trabajo_display = serializers.CharField(source='get_tipo_trabajo_display', read_only=True)
    subido_por_nombre = serializers.CharField(source='subido_por.get_full_name', read_only=True)
    aprobado_por_nombre = serializers.CharField(source='aprobado_por.get_full_name', read_only=True)
    puede_descargar = serializers.SerializerMethodField()
    calificacion_promedio = serializers.SerializerMethodField()
    comentarios = serializers.SerializerMethodField()
    
    class Meta:
        model = TrabajoInvestigacion
        fields = [
            'id', 'titulo', 'autores', 'tutores', 'año', 'carrera', 'carrera_display',
            'tipo_trabajo', 'tipo_trabajo_display', 'resumen', 'objetivos',
            'tags_ia', 'fecha_subida', 'fecha_aprobacion', 'estado',
            'subido_por_nombre', 'aprobado_por_nombre', 'total_descargas',
            'puede_descargar', 'calificacion_promedio', 'comentarios'
        ]
    
    def get_puede_descargar(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.puede_ser_descargado
        return False
    
    def get_calificacion_promedio(self, obj):
        try:
            promedio = obj.calificacion_promedio
            return {
                'promedio': promedio.promedio_calificacion,
                'total_comentarios': promedio.total_comentarios,
                'distribucion': promedio.distribucion_calificaciones
            }
        except CalificacionPromedio.DoesNotExist:
            return {
                'promedio': 0,
                'total_comentarios': 0,
                'distribucion': {}
            }
    
    def get_comentarios(self, obj):
        comentarios = obj.comentarios.filter(aprobado=True)[:5]  # Solo los últimos 5
        from apps.comentarios.serializers import ComentarioListSerializer
        return ComentarioListSerializer(comentarios, many=True, context=self.context).data


class TrabajoInvestigacionUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para actualizar trabajos de investigación
    """
    class Meta:
        model = TrabajoInvestigacion
        fields = [
            'titulo', 'autores', 'tutores', 'carrera', 'tipo_trabajo', 'año'
        ]
    
    def validate(self, attrs):
        usuario = self.context['request'].user
        trabajo = self.instance
        tipo_trabajo = attrs.get('tipo_trabajo', trabajo.tipo_trabajo)
        
        # Verificar permisos
        if not usuario.es_encargado_especial_grado and not usuario.es_encargado_pasantias:
            if trabajo.subido_por != usuario:
                raise serializers.ValidationError(
                    "Solo puedes editar tus propios trabajos."
                )
        
        # Verificar permisos específicos según tipo
        if tipo_trabajo == 'especial_grado':
            if not usuario.es_encargado_especial_grado:
                raise serializers.ValidationError(
                    "No tienes permisos para editar trabajos especiales de grado."
                )
        elif tipo_trabajo == 'practicas_profesionales':
            if not usuario.es_encargado_pasantias:
                raise serializers.ValidationError(
                    "No tienes permisos para editar prácticas profesionales."
                )
        
        return attrs


class TrabajoInvestigacionAprobacionSerializer(serializers.Serializer):
    """
    Serializer para aprobación/rechazo de trabajos
    """
    estado = serializers.ChoiceField(choices=['aprobado', 'rechazado', 'requiere_correcciones'])
    motivo = serializers.CharField(required=False, allow_blank=True)
    
    def validate_estado(self, value):
        usuario = self.context['request'].user
        
        # Verificar que el usuario tiene permisos para aprobar
        trabajo = self.instance
        if value == 'aprobado':
            if not usuario.es_superuser_trabajo:
                raise serializers.ValidationError(
                    "Solo los superusuarios pueden aprobar trabajos."
                )
        
        return value
    
    def save(self):
        trabajo = self.instance
        usuario = self.context['request'].user
        estado = self.validated_data['estado']
        motivo = self.validated_data.get('motivo', '')
        
        with transaction.atomic():
            if estado == 'aprobado':
                trabajo.marcar_como_aprobado(usuario)
            elif estado == 'rechazodo':
                trabajo.marcar_como_rechazado(motivo)
            elif estado == 'requiere_correcciones':
                trabajo.estado = 'requiere_correcciones'
                if motivo:
                    trabajo.resumen = f"{trabajo.resumen}\n\nCorrecciones requeridas: {motivo}"
                trabajo.save()
        
        return trabajo


class ConfiguracionCarreraSerializer(serializers.ModelSerializer):
    """
    Serializer para configuración de carreras
    """
    class Meta:
        model = ConfiguracionCarrera
        fields = [
            'id', 'nombre', 'codigo', 'color', 'icono', 'descripcion',
            'encargados_especial_grado', 'superuser_especial_grado',
            'encargados_pasantias', 'superuser_pasantias', 'activa'
        ]
    
    def create(self, validated_data):
        # Solo administradores pueden crear configuraciones
        usuario = self.context['request'].user
        if not usuario.is_staff:
            raise serializers.ValidationError("Solo los administradores pueden crear configuraciones de carrera.")
        return super().create(validated_data)


class EstadisticasTrabajosSerializer(serializers.Serializer):
    """
    Serializer para estadísticas de trabajos
    """
    total_trabajos = serializers.IntegerField()
    trabajos_aprobados = serializers.IntegerField()
    trabajos_pendientes = serializers.IntegerField()
    trabajos_rechazados = serializers.IntegerField()
    total_descargas = serializers.IntegerField()
    trabajos_por_carrera = serializers.DictField()
    trabajos_por_tipo = serializers.DictField()
    trabajos_por_año = serializers.DictField()
    top_trabajos_mas_descargados = serializers.ListField()
    top_trabajos_mejor_calificados = serializers.ListField()