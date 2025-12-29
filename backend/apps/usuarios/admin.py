# backend/apps/usuarios/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    # Campos que se ven en la lista principal
    list_display = ('cedula', 'username', 'email', 'rol', 'carrera', 'activo', 'is_staff')
    # Filtros laterales
    list_filter = ('rol', 'carrera', 'activo', 'verificado', 'is_staff')
    # Campos por los que puedes buscar
    search_fields = ('cedula', 'username', 'email', 'first_name', 'last_name')
    ordering = ('-fecha_registro',)

    # Cómo se ve el formulario al editar un usuario
    fieldsets = list(UserAdmin.fieldsets) + [
    ('Información Universitaria', {
        'fields': ('cedula', 'telefono', 'carrera', 'rol', 'activo', 'verificado')
    }),
]

    
    # Campos al crear un usuario nuevo
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Universitaria', {
            'fields': ('cedula', 'rol', 'carrera')
        }),
    )
    autocomplete_fields = ['carrera']
