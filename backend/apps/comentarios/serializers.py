from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.comentarios.models import Comentario, RetroalimentacionIA

Usuario = get_user_model()


class ComentarioCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear comentarios
    """
    class Meta:
        model = Comentario
        fields = ['trabajo', 'comentario', 'calificacion']
    
    def validate(self, attrs):
        usuario = self.context['request'].user
        trabajo = attrs['trabajo']
        
        # Verificar que el usuario puede comentar (debe estar autenticado)
        if not usuario.is_authenticated:
            raise serializers.ValidationError("Debes estar autenticado para comentar.")
        
        # Verificar que el trabajo puede ser comentado (debe estar aprobado)
        if not trabajo.puede_ser_descargado:
            raise serializers.ValidationError("No puedes comentar un trabajo no aprobado.")
        
        # Verificar que el usuario ya no haya comentado este trabajo
        if Comentario.objects.filter(trabajo=trabajo, usuario=usuario).exists():
            raise serializers.ValidationError("Ya has comentado este trabajo.")
        
        return attrs
    
    def create(self, validated_data):
        comentario = Comentario.objects.create(
            usuario=self.context['request'].user,
            **validated_data
        )
        
        # Actualizar el cache de calificación promedio
        from apps.comentarios.models import CalificacionPromedio
        try:
            promedio = comentario.trabajo.calificacion_promedio
        except CalificacionPromedio.DoesNotExist:
            promedio = CalificacionPromedio.objects.create(trabajo=comentario.trabajo)
        
        promedio.actualizar_promedio()
        
        return comentario


class ComentarioListSerializer(serializers.ModelSerializer):
    """
    Serializer para listar comentarios
    """
    usuario_nombre = serializers.CharField(source='usuario.get_full_name', read_only=True)
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)
    estrellas = serializers.CharField(read_only=True)
    
    class Meta:
        model = Comentario
        fields = [
            'id', 'usuario_nombre', 'usuario_username', 'comentario',
            'calificacion', 'estrellas', 'fecha_creacion'
        ]


class ComentarioUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para actualizar comentarios
    """
    class Meta:
        model = Comentario
        fields = ['comentario', 'calificacion']
    
    def validate(self, attrs):
        usuario = self.context['request'].user
        
        # Solo el autor del comentario puede editarlo
        if self.instance.usuario != usuario:
            raise serializers.ValidationError("Solo puedes editar tus propios comentarios.")
        
        return attrs
    
    def update(self, instance, validated_data):
        # Actualizar el comentario
        comentario = super().update(instance, validated_data)
        
        # Actualizar el cache de calificación promedio
        try:
            promedio = comentario.trabajo.calificacion_promedio
        except:
            promedio = None
        
        if promedio:
            promedio.actualizar_promedio()
        
        return comentario


class RetroalimentacionIACreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear retroalimentación de IA
    """
    class Meta:
        model = RetroalimentacionIA
        fields = [
            'trabajo', 'recomendacion_util', 'coincidencia_contenido',
            'precision_resumen', 'utilidad_objetivos', 'comentarios_adicionales'
        ]
    
    def validate(self, attrs):
        usuario = self.context['request'].user
        trabajo = attrs['trabajo']
        
        # Verificar que el usuario puede dar feedback (debe estar autenticado)
        if not usuario.is_authenticated:
            raise serializers.ValidationError("Debes estar autenticado para dar retroalimentación.")
        
        # Verificar que ya no haya dado feedback para este trabajo
        if RetroalimentacionIA.objects.filter(trabajo=trabajo, usuario=usuario).exists():
            raise serializers.ValidationError("Ya has dado retroalimentación para este trabajo.")
        
        return attrs
    
    def create(self, validated_data):
        return RetroalimentacionIA.objects.create(
            usuario=self.context['request'].user,
            **validated_data
        )


class RetroalimentacionIAListSerializer(serializers.ModelSerializer):
    """
    Serializer para listar retroalimentación de IA
    """
    usuario_nombre = serializers.CharField(source='usuario.get_full_name', read_only=True)
    puntuacion_total = serializers.FloatField(read_only=True)
    trabajo_titulo = serializers.CharField(source='trabajo.titulo', read_only=True)
    
    class Meta:
        model = RetroalimentacionIA
        fields = [
            'id', 'usuario_nombre', 'trabajo_titulo', 'recomendacion_util',
            'coincidencia_contenido', 'precision_resumen', 'utilidad_objetivos',
            'puntuacion_total', 'comentarios_adicionales', 'fecha_creacion'
        ]


class ReporteDescargaSerializer(serializers.Serializer):
    """
    Serializer para reportes de descarga
    """
    trabajo_id = serializers.IntegerField()
    ip_address = serializers.CharField()
    user_agent = serializers.CharField(required=False, allow_blank=True)
    
    def create(self, validated_data):
        from apps.comentarios.models import ReporteDescarga
        from apps.trabajos.models import TrabajoInvestigacion
        
        trabajo = TrabajoInvestigacion.objects.get(id=validated_data['trabajo_id'])
        
        # Crear el reporte
        reporte = ReporteDescarga.objects.create(
            trabajo=trabajo,
            usuario=self.context['request'].user,
            ip_address=validated_data['ip_address'],
            user_agent=validated_data.get('user_agent', '')
        )
        
        # Incrementar contador de descargas
        trabajo.incrementar_descargas()
        
        return reporte