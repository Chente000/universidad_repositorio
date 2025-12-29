from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator


class Comentario(models.Model):
    """
    Sistema de comentarios para trabajos de investigación
    """
    trabajo = models.ForeignKey(
        'trabajos.TrabajoInvestigacion',
        on_delete=models.CASCADE,
        related_name='comentarios',
        verbose_name='Trabajo'
    )
    usuario = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='comentarios',
        verbose_name='Usuario'
    )
    
    comentario = models.TextField(verbose_name='Comentario')
    calificacion = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Calificación (1-5)'
    )
    
    # Estados
    aprobado = models.BooleanField(default=True, verbose_name='Comentario Aprobado')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'comentarios'
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'
        ordering = ['-fecha_creacion']
        unique_together = ['trabajo', 'usuario']  # Un comentario por usuario por trabajo
    
    def __str__(self):
        return f"Comentario de {self.usuario.username} en {self.trabajo.titulo}"
    
    @property
    def estrellas(self):
        """Retorna una cadena de estrellas basada en la calificación"""
        return "★" * self.calificacion + "☆" * (5 - self.calificacion)


class CalificacionPromedio(models.Model):
    """
    Cache de calificaciones promedio para optimización
    """
    trabajo = models.OneToOneField(
        'trabajos.TrabajoInvestigacion',
        on_delete=models.CASCADE,
        related_name='calificacion_promedio',
        verbose_name='Trabajo'
    )
    
    promedio_calificacion = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        verbose_name='Promedio de Calificación'
    )
    total_comentarios = models.PositiveIntegerField(default=0, verbose_name='Total de Comentarios')
    distribucion_calificaciones = models.JSONField(default=dict, verbose_name='Distribución de Calificaciones')
    
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'calificacion_promedio'
        verbose_name = 'Calificación Promedio'
        verbose_name_plural = 'Calificaciones Promedio'
    
    def __str__(self):
        return f"Promedio de {self.trabajo.titulo}: {self.promedio_calificacion:.2f}"
    
    def actualizar_promedio(self):
        """Actualiza el promedio basado en los comentarios actuales"""
        comentarios = self.trabajo.comentarios.filter(aprobado=True)
        
        if comentarios.exists():
            total_calificacion = sum(c.calificacion for c in comentarios)
            self.total_comentarios = comentarios.count()
            self.promedio_calificacion = total_calificacion / self.total_comentarios
            
            # Calcular distribución
            distribucion = {}
            for i in range(1, 6):
                count = comentarios.filter(calificacion=i).count()
                distribucion[str(i)] = count
            self.distribucion_calificaciones = distribucion
        else:
            self.promedio_calificacion = 0.0
            self.total_comentarios = 0
            self.distribucion_calificaciones = {}
        
        self.save()


class ReporteDescarga(models.Model):
    """
    Registro de descargas para reportes y estadísticas
    """
    trabajo = models.ForeignKey(
        'trabajos.TrabajoInvestigacion',
        on_delete=models.CASCADE,
        related_name='reportes_descarga',
        verbose_name='Trabajo'
    )
    usuario = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='reportes_descarga',
        verbose_name='Usuario'
    )
    
    ip_address = models.GenericIPAddressField(verbose_name='Dirección IP')
    user_agent = models.TextField(blank=True, verbose_name='User Agent')
    fecha_descarga = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Descarga')
    
    class Meta:
        db_table = 'reporte_descarga'
        verbose_name = 'Reporte de Descarga'
        verbose_name_plural = 'Reportes de Descarga'
        ordering = ['-fecha_descarga']
        indexes = [
            models.Index(fields=['trabajo']),
            models.Index(fields=['usuario']),
            models.Index(fields=['fecha_descarga']),
        ]
    
    def __str__(self):
        return f"Descarga de {self.usuario.username} - {self.trabajo.titulo}"


class RetroalimentacionIA(models.Model):
    """
    Retroalimentación para mejorar el sistema de IA
    """
    trabajo = models.ForeignKey(
        'trabajos.TrabajoInvestigacion',
        on_delete=models.CASCADE,
        related_name='retroalimentacion_ia',
        verbose_name='Trabajo'
    )
    usuario = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='retroalimentacion_ia',
        verbose_name='Usuario'
    )
    
    # Feedback sobre la recomendación
    recomendacion_util = models.BooleanField(verbose_name='¿La recomendación fue útil?')
    coincidencia_contenido = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Coincidencia con el Contenido Buscado (1-5)'
    )
    precision_resumen = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Precisión del Resumen (1-5)'
    )
    utilidad_objetivos = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Utilidad de los Objetivos (1-5)'
    )
    
    comentarios_adicionales = models.TextField(blank=True, verbose_name='Comentarios Adicionales')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'retroalimentacion_ia'
        verbose_name = 'Retroalimentación IA'
        verbose_name_plural = 'Retroalimentación IA'
        ordering = ['-fecha_creacion']
        unique_together = ['trabajo', 'usuario']
    
    def __str__(self):
        return f"Feedback de {self.usuario.username} sobre {self.trabajo.titulo}"
    
    @property
    def puntuacion_total(self):
        """Calcula una puntuación total basada en todos los criterios"""
        return (self.coincidencia_contenido + self.precision_resumen + self.utilidad_objetivos) / 3