# backend/apps/usuarios/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils import timezone
from apps.trabajos.models import ConfiguracionCarrera  # Ajusta la ruta según tu proyecto
from django.conf import settings



class Usuario(AbstractUser):
    """
    Modelo de usuario personalizado para la universidad
    """
    # Información personal
    cedula = models.CharField(
        max_length=10,
        unique=True,
        validators=[RegexValidator(r'^\d{7,10}$', 'La cédula debe tener entre 7 y 10 dígitos')],
        verbose_name='Cédula'
    )
    telefono = models.CharField(
        max_length=15,
        blank=True,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Formato de teléfono inválido')],
        verbose_name='Teléfono'
    )
    
    # Información académica/profesional
    carrera = models.ForeignKey(
        ConfiguracionCarrera, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Carrera"
    )
    
    # Roles y permisos específicos
    rol = models.CharField(
        max_length=30,
        choices=settings.USER_ROLES,  # Se llenará desde settings
        default='estudiante',
        verbose_name='Rol'
    )
    
    # Estados
    activo = models.BooleanField(default=True, verbose_name='Usuario Activo')
    verificado = models.BooleanField(default=False, verbose_name='Email Verificado')
    
    # Metadatos
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Registro')
    ultima_conexion = models.DateTimeField(null=True, blank=True, verbose_name='Última Conexión')
    
    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-fecha_registro']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.cedula})"
    
    def save(self, *args, **kwargs):
        # Actualizar última conexión si es un login
        if self.pk:
            Usuario.objects.filter(pk=self.pk).update(ultima_conexion=timezone.now())
        super().save(*args, **kwargs)
    
    @property
    def puede_subir_especial_grado(self):
        """Verifica si el usuario puede subir trabajos especiales de grado"""
        return self.rol in ['encargado_especial_grado', 'superuser_especial_grado', 'administrador']
    
    @property
    def puede_subir_pasantias(self):
        """Verifica si el usuario puede subir prácticas profesionales"""
        return self.rol in ['encargado_pasantias', 'superuser_pasantias', 'administrador']
    
    @property
    def es_superuser_trabajo(self):
        """Verifica si el usuario es superusuario de algún tipo de trabajo"""
        return self.rol in ['superuser_especial_grado', 'superuser_pasantias', 'administrador']
    
    @property
    def es_encargado_especial_grado(self):
        """Verifica si el usuario puede gestionar trabajos especiales de grado"""
        return self.rol in ['encargado_especial_grado', 'superuser_especial_grado', 'administrador']
    
    @property
    def es_encargado_pasantias(self):
        """Verifica si el usuario puede gestionar prácticas profesionales"""
        return self.rol in ['encargado_pasantias', 'superuser_pasantias', 'administrador']