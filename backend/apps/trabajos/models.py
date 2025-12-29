# backend/apps/trabajos/models.py
import os
import uuid
from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone


def archivo_pdf_upload_path(instance, filename):
    """Genera el path donde se guardará el archivo PDF"""
    # SOLUCIÓN: Si fecha_subida es None (porque es un objeto nuevo), usamos la fecha actual
    fecha_obj = instance.fecha_subida or timezone.now()
    fecha_str = fecha_obj.strftime('%Y/%m/%d')
    
    extension = filename.split('.')[-1]
    
    # Limpiamos el título para evitar caracteres extraños en el nombre del archivo
    titulo_limpio = "".join(c for c in instance.titulo if c.isalnum() or c in (' ', '_')).strip()
    nuevo_nombre = f"{titulo_limpio.replace(' ', '_')[:50]}_{uuid.uuid4().hex[:8]}.{extension}"
    
    return f"trabajos/{fecha_str}/{nuevo_nombre}"


class TrabajoInvestigacion(models.Model):
    """
    Modelo principal para trabajos de investigación
    """
    TIPO_TRABAJO = [
        ('especial_grado', 'Trabajo Especial de Grado'),
        ('practicas_profesionales', 'Prácticas Profesionales'),
    ]
    
    ESTADO_TRABAJO = [
        ('pendiente', 'Pendiente de Aprobación'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
        ('requiere_correcciones', 'Requiere Correcciones'),
    ]
    
    # Información básica del trabajo
    titulo = models.CharField(max_length=300, verbose_name='Título')
    autores = models.CharField(max_length=500, verbose_name='Autores')
    tutores = models.CharField(max_length=500, verbose_name='Tutores')
    carrera = models.ForeignKey(
        'ConfiguracionCarrera', # Usamos string para evitar importación circular
        on_delete=models.PROTECT, # Protege para que no borren carreras con trabajos
        verbose_name='Carrera'
    )
    tipo_trabajo = models.CharField(
        max_length=30,
        choices=TIPO_TRABAJO,
        verbose_name='Tipo de Trabajo'
    )
    año = models.PositiveIntegerField(verbose_name='Año')
    
    # Archivos
    archivo_pdf = models.FileField(
        upload_to=archivo_pdf_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        verbose_name='Archivo PDF'
    )
    
    # Contenido extraído por IA
    contenido_extraido = models.TextField(blank=True, verbose_name='Contenido Extraído')
    objetivos = models.TextField(blank=True, verbose_name='Objetivos')
    resumen = models.TextField(blank=True, verbose_name='Resumen')
    
    # Metadatos del archivo
    tamaño_archivo = models.PositiveIntegerField(verbose_name='Tamaño del Archivo (bytes)')
    hash_md5 = models.CharField(max_length=32, verbose_name='Hash MD5', blank=True)
    
    # Estados y aprobación
    estado = models.CharField(
        max_length=30,
        choices=ESTADO_TRABAJO,
        default='pendiente',
        verbose_name='Estado'
    )
    fecha_subida = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Subida')
    fecha_aprobacion = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Aprobación')
    
    # IA y recomendaciones
    embedding_vector = models.JSONField(null=True, blank=True, verbose_name='Vector de Embedding')
    similitud_trabajo = models.FloatField(default=0.0, verbose_name='Puntuación de Similitud')
    tags_ia = models.JSONField(default=list, blank=True, verbose_name='Tags Generados por IA')
    
    # Usuario que subió el trabajo
    subido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='trabajos_subidos',
        verbose_name='Subido por'
    )
    
    # Usuario que aprobó el trabajo
    aprobado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='trabajos_aprobados',
        verbose_name='Aprobado por'
    )
    
    # Contador de descargas
    total_descargas = models.PositiveIntegerField(default=0, verbose_name='Total Descargas')
    
    class Meta:
        db_table = 'trabajos_investigacion'
        verbose_name = 'Trabajo de Investigación'
        verbose_name_plural = 'Trabajos de Investigación'
        ordering = ['-fecha_subida']
        indexes = [
            models.Index(fields=['carrera']),
            models.Index(fields=['tipo_trabajo']),
            models.Index(fields=['estado']),
            models.Index(fields=['año']),
            models.Index(fields=['subido_por']),
        ]
    
    def __str__(self):
        return f"{self.titulo} ({self.año})"
    
    def save(self, *args, **kwargs):
        if self.archivo_pdf:
            self.tamaño_archivo = self.archivo_pdf.size
        super().save(*args, **kwargs)
    
    @property
    def archivo_url(self):
        """Retorna la URL del archivo PDF"""
        if self.archivo_pdf:
            return self.archivo_pdf.url
        return None
    
    @property
    def puede_ser_descargado(self):
        """Verifica si el trabajo puede ser descargado"""
        return self.estado == 'aprobado'
    
    def incrementar_descargas(self):
        """Incrementa el contador de descargas"""
        self.total_descargas += 1
        self.save(update_fields=['total_descargas'])
    
    def marcar_como_aprobado(self, usuario_aprobador):
        """Marca el trabajo como aprobado"""
        from django.utils import timezone
        self.estado = 'aprobado'
        self.aprobado_por = usuario_aprobador
        self.fecha_aprobacion = timezone.now()
        self.save()
    
    def marcar_como_rechazado(self, motivo=''):
        """Marca el trabajo como rechazado"""
        self.estado = 'rechazado'
        if motivo:
            self.resumen = f"{self.resumen}\n\nMotivo de rechazo: {motivo}"
        self.save()


class ConfiguracionCarrera(models.Model):
    """
    Configuración específica para cada carrera
    """
    nombre = models.CharField(max_length=100, verbose_name='Nombre de la Carrera')
    codigo = models.CharField(max_length=20, unique=True, verbose_name='Código')
    color = models.CharField(max_length=7, default='#1e3a8a', verbose_name='Color Hex')
    icono = models.CharField(max_length=50, blank=True, verbose_name='Icono')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    
    # Encargados de la carrera
    encargados_especial_grado = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='carreras_encargado_especial_grado',
        verbose_name='Encargados Trabajo Especial de Grado'
    )
    
    superuser_especial_grado = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='carreras_superuser_especial_grado',
        verbose_name='Super Usuario Trabajo Especial de Grado'
    )
    
    encargados_pasantias = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='carreras_encargado_pasantias',
        verbose_name='Encargados Prácticas Profesionales'
    )
    
    superuser_pasantias = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='carreras_superuser_pasantias',
        verbose_name='Super Usuario Prácticas Profesionales'
    )
    
    activa = models.BooleanField(default=True, verbose_name='Carrera Activa')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'configuracion_carrera'
        verbose_name = 'Configuración de Carrera'
        verbose_name_plural = 'Configuraciones de Carreras'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class LogActividades(models.Model):
    """
    Log de actividades del sistema para auditoría
    """
    ACCION_CHOICES = [
        ('upload', 'Subida de archivo'),
        ('download', 'Descarga de archivo'),
        ('approve', 'Aprobación'),
        ('reject', 'Rechazo'),
        ('delete', 'Eliminación'),
        ('login', 'Inicio de sesión'),
        ('search', 'Búsqueda'),
        ('comment', 'Comentario'),
        ('rate', 'Calificación'),
    ]
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Usuario'
    )
    accion = models.CharField(
        max_length=20,
        choices=ACCION_CHOICES,
        verbose_name='Acción'
    )
    trabajo = models.ForeignKey(
        TrabajoInvestigacion,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Trabajo'
    )
    descripcion = models.TextField(verbose_name='Descripción')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'log_actividades'
        verbose_name = 'Log de Actividad'
        verbose_name_plural = 'Logs de Actividades'
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['usuario']),
            models.Index(fields=['accion']),
            models.Index(fields=['fecha']),
        ]
    
    def __str__(self):
        return f"{self.usuario.username} - {self.get_accion_display()} - {self.fecha}"