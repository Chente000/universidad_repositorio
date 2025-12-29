# backend/apps/trabajos/admin.py
from django.contrib import admin
from .models import TrabajoInvestigacion, ConfiguracionCarrera, LogActividades

@admin.register(TrabajoInvestigacion)
class TrabajoInvestigacionAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo_trabajo', 'estado', 'año', 'subido_por', 'fecha_subida')
    list_filter = ('estado', 'tipo_trabajo', 'carrera', 'año')
    search_fields = ('titulo', 'autores', 'resumen', 'subido_por__username')
    readonly_fields = ('tamaño_archivo', 'hash_md5', 'fecha_subida', 'total_descargas')
    
    # Acción para aprobar masivamente
    actions = ['aprobar_trabajos']

    
    @admin.action(description="Aprobar trabajos seleccionados")
    def aprobar_trabajos(self, request, queryset):
        for trabajo in queryset:
            trabajo.marcar_como_aprobado(request.user)
        
        self.message_user(
            request, 
            f"Se han aprobado {queryset.count()} trabajos con éxito."
        )

@admin.register(ConfiguracionCarrera)
class ConfiguracionCarreraAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'activa', 'superuser_especial_grado', 'superuser_pasantias')
    search_fields = ('nombre', 'codigo')
    list_editable = ('activa',)
    filter_horizontal = ('encargados_especial_grado', 'encargados_pasantias')

@admin.register(LogActividades)
class LogActividadesAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'usuario', 'accion', 'trabajo', 'ip_address')
    list_filter = ('accion', 'fecha')
    search_fields = ('usuario__username', 'descripcion')
    # Logs suelen ser de solo lectura para integridad
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False