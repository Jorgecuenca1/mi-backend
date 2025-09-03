# api/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Veterinario, Planilla, Mascota, Responsable

class NoLogMixin:
    """Mixin para deshabilitar el logging del admin y evitar errores de foreign key"""
    
    def log_addition(self, request, object, message):
        """Deshabilitar logging de adición"""
        pass
    
    def log_change(self, request, object, message):
        """Deshabilitar logging de cambios"""
        pass
    
    def log_deletion(self, request, object, object_repr):
        """Deshabilitar logging de eliminación"""
        pass

@admin.register(Veterinario)
class VeterinarioAdmin(NoLogMixin, UserAdmin):
    """Admin para veterinarios (usuarios)."""
    # Agregar tipo_usuario a los campos mostrados en la lista
    list_display = ('username','tipo_usuario',)
    list_filter = ('tipo_usuario',)
    
    # Personalizar los fieldsets para incluir tipo_usuario
    fieldsets = UserAdmin.fieldsets + (
        ('Información Veterinaria', {
            'fields': ('tipo_usuario',),
        }),
    )
    
    # También agregarlo a los campos para crear usuario
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Veterinaria', {
            'fields': ('tipo_usuario',),
        }),
    )

@admin.register(Planilla)
class PlanillaAdmin(NoLogMixin, admin.ModelAdmin):
    """Admin para municipios con asignaciones múltiples."""
    list_display = ('id', 'nombre', 'municipio', 'assigned_to', 'get_vacunadores_adicionales', 'get_tecnicos_adicionales', 'creada')
    list_filter = ('assigned_to', 'tecnico_asignado', 'urbano_rural', 'creada')
    search_fields = ('nombre', 'municipio', 'assigned_to__username', 'tecnico_asignado__username')
    ordering = ('-creada',)
    filter_horizontal = ('vacunadores_adicionales', 'tecnicos_adicionales')
    
    fieldsets = (
        ('Información del Municipio', {
            'fields': ('nombre', 'municipio')
        }),
        ('Asignación de Personal', {
            'fields': ('assigned_to', 'vacunadores_adicionales', 'tecnico_asignado', 'tecnicos_adicionales'),
            'description': 'Asigna vacunadores y técnicos a este municipio. Puedes asignar múltiples personas de cada tipo.'
        }),
        ('Ubicación', {
            'fields': ('urbano_rural', 'centro_poblado_vereda_barrio', 'zona'),
            'classes': ('collapse',)
        }),
        ('Información del Sistema', {
            'fields': ('creada',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('creada',)
    
    def get_vacunadores_adicionales(self, obj):
        """Muestra los vacunadores adicionales en la lista"""
        return ", ".join([v.username for v in obj.vacunadores_adicionales.all()[:3]])
    get_vacunadores_adicionales.short_description = 'Vacunadores Adicionales'
    
    def get_tecnicos_adicionales(self, obj):
        """Muestra los técnicos adicionales en la lista"""
        return ", ".join([t.username for t in obj.tecnicos_adicionales.all()[:3]])
    get_tecnicos_adicionales.short_description = 'Técnicos Adicionales'

@admin.register(Responsable)
class ResponsableAdmin(NoLogMixin, admin.ModelAdmin):
    """Admin para responsables de mascotas."""
    list_display = ('id', 'nombre', 'telefono', 'finca', 'planilla', 'zona', 'nombre_zona', 'lote_vacuna', 'created_by', 'creado')
    list_filter = ('planilla', 'zona', 'lote_vacuna', 'created_by', 'creado')
    search_fields = ('nombre', 'telefono', 'finca', 'zona', 'nombre_zona', 'lote_vacuna', 'created_by__username')
    ordering = ('-creado',)
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'telefono', 'finca', 'planilla')
        }),
        ('Control de Vacunación', {
            'fields': ('zona', 'nombre_zona', 'lote_vacuna'),
            'classes': ('collapse',)
        }),
        ('Información del Sistema', {
            'fields': ('created_by', 'creado'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_by', 'creado')

@admin.register(Mascota)
class MascotaAdmin(NoLogMixin, admin.ModelAdmin):
    """Admin para las mascotas de cada responsable."""
    list_display = ('id', 'nombre', 'tipo', 'raza', 'color', 'antecedente_vacunal', 'esterilizado', 'responsable', 'created_by', 'creado')
    list_filter = ('tipo', 'raza', 'antecedente_vacunal', 'esterilizado', 'responsable', 'created_by', 'creado')
    search_fields = ('nombre', 'responsable__nombre', 'created_by__username')
    ordering = ('-creado',)
    readonly_fields = ('created_by', 'creado')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'tipo', 'raza', 'color', 'antecedente_vacunal', 'esterilizado', 'responsable')
        }),
        ('Georreferenciación', {
            'fields': ('latitud', 'longitud'),
            'classes': ('collapse',)
        }),
        ('Foto', {
            'fields': ('foto',),
            'classes': ('collapse',)
        }),
        ('Información del Sistema', {
            'fields': ('created_by', 'creado'),
            'classes': ('collapse',)
        }),
    )
