# api/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Veterinario, Planilla, Mascota, Responsable, RegistroPerdidas

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
    list_display = ('id', 'username', 'get_nombre_completo', 'get_municipio', 'get_assigned_to', 'get_vacunadores_adicionales', 'get_tecnicos_adicionales', 'tipo_usuario')
    list_filter = ('tipo_usuario',)
    
    def get_nombre_completo(self, obj):
        """Muestra el nombre completo del usuario"""
        return f"{obj.first_name} {obj.last_name}" if obj.first_name or obj.last_name else obj.username
    get_nombre_completo.short_description = 'Nombre'
    
    def get_municipio(self, obj):
        """Muestra los municipios donde el técnico está asignado"""
        if obj.tipo_usuario == 'tecnico':
            # Municipios donde es técnico principal
            municipios_principales = obj.planillas_asignadas.all()
            # Municipios donde es técnico adicional
            municipios_adicionales = obj.planillas_como_tecnico_adicional.all()
            
            municipios = []
            for m in municipios_principales:
                municipios.append(f"{m.nombre} (Principal)")
            for m in municipios_adicionales:
                municipios.append(m.nombre)
            return ", ".join(municipios[:3]) if municipios else "Sin asignar"
        return "-"
    get_municipio.short_description = 'Municipio'
    
    def get_assigned_to(self, obj):
        """Muestra el vacunador principal de los municipios donde el técnico trabaja"""
        if obj.tipo_usuario == 'tecnico':
            vacunadores = set()
            # De los municipios donde es técnico principal
            for planilla in obj.planillas_asignadas.all():
                if planilla.assigned_to:
                    vacunadores.add(planilla.assigned_to.username)
            # De los municipios donde es técnico adicional
            for planilla in obj.planillas_como_tecnico_adicional.all():
                if planilla.assigned_to:
                    vacunadores.add(planilla.assigned_to.username)
            return ", ".join(list(vacunadores)[:3]) if vacunadores else "Sin asignar"
        return "-"
    get_assigned_to.short_description = 'Assigned to'
    
    def get_vacunadores_adicionales(self, obj):
        """Muestra los vacunadores adicionales en los municipios del técnico"""
        if obj.tipo_usuario == 'tecnico':
            vacunadores = set()
            # De los municipios donde es técnico principal
            for planilla in obj.planillas_asignadas.all():
                for v in planilla.vacunadores_adicionales.all():
                    vacunadores.add(v.username)
            # De los municipios donde es técnico adicional
            for planilla in obj.planillas_como_tecnico_adicional.all():
                for v in planilla.vacunadores_adicionales.all():
                    vacunadores.add(v.username)
            return ", ".join(list(vacunadores)[:3]) if vacunadores else "-"
        return "-"
    get_vacunadores_adicionales.short_description = 'Vacunadores Adicionales'
    
    def get_tecnicos_adicionales(self, obj):
        """Muestra otros técnicos adicionales en los municipios del técnico"""
        if obj.tipo_usuario == 'tecnico':
            tecnicos = set()
            # De los municipios donde es técnico principal
            for planilla in obj.planillas_asignadas.all():
                for t in planilla.tecnicos_adicionales.all():
                    if t.username != obj.username:  # Excluir al técnico actual
                        tecnicos.add(t.username)
            # De los municipios donde es técnico adicional
            for planilla in obj.planillas_como_tecnico_adicional.all():
                for t in planilla.tecnicos_adicionales.all():
                    if t.username != obj.username:  # Excluir al técnico actual
                        tecnicos.add(t.username)
                # También incluir el técnico principal si no es él mismo
                if planilla.tecnico_asignado and planilla.tecnico_asignado.username != obj.username:
                    tecnicos.add(planilla.tecnico_asignado.username)
            return ", ".join(list(tecnicos)[:3]) if tecnicos else "-"
        return "-"
    get_tecnicos_adicionales.short_description = 'Técnicos Adicionales'
    
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
    list_display = ('id', 'nombre', 'municipio', 'assigned_to', 'tecnico_asignado', 'get_vacunadores_adicionales', 'get_tecnicos_adicionales', 'creada')
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

class ResponsableResource(resources.ModelResource):
    class Meta:
        model = Responsable
        fields = ('id', 'nombre', 'telefono', 'finca', 'planilla__nombre', 'zona', 'nombre_zona', 'lote_vacuna', 'created_by__username', 'creado')
        export_order = ('id', 'nombre', 'telefono', 'finca', 'planilla__nombre', 'zona', 'nombre_zona', 'lote_vacuna', 'created_by__username', 'creado')

@admin.register(Responsable)
class ResponsableAdmin(NoLogMixin, ImportExportModelAdmin):
    """Admin para responsables de mascotas."""
    resource_class = ResponsableResource
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

class MascotaResource(resources.ModelResource):
    class Meta:
        model = Mascota
        fields = ('id', 'nombre', 'tipo', 'raza', 'color', 'antecedente_vacunal', 'esterilizado', 'responsable__nombre', 'responsable__telefono', 'latitud', 'longitud', 'created_by__username', 'creado')
        export_order = ('id', 'nombre', 'tipo', 'raza', 'color', 'antecedente_vacunal', 'esterilizado', 'responsable__nombre', 'responsable__telefono', 'latitud', 'longitud', 'created_by__username', 'creado')

@admin.register(Mascota)
class MascotaAdmin(NoLogMixin, ImportExportModelAdmin):
    """Admin para las mascotas de cada responsable."""
    resource_class = MascotaResource
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


@admin.register(RegistroPerdidas)
class RegistroPerdidasAdmin(NoLogMixin, admin.ModelAdmin):
    """Admin para registros de pérdidas de vacunas."""
    list_display = ('id', 'cantidad', 'lote_vacuna', 'registrado_por', 'fecha_perdida', 'fecha_registro', 'sincronizado')
    list_filter = ('registrado_por', 'lote_vacuna', 'fecha_perdida', 'sincronizado')
    search_fields = ('lote_vacuna', 'motivo', 'registrado_por__username')
    ordering = ('-fecha_registro',)
    readonly_fields = ('fecha_registro', 'uuid_local')
    
    fieldsets = (
        ('Información de la Pérdida', {
            'fields': ('cantidad', 'lote_vacuna', 'motivo', 'fecha_perdida')
        }),
        ('Ubicación', {
            'fields': ('latitud', 'longitud'),
            'classes': ('collapse',)
        }),
        ('Evidencia', {
            'fields': ('foto',),
            'classes': ('collapse',)
        }),
        ('Información del Sistema', {
            'fields': ('registrado_por', 'fecha_registro', 'sincronizado', 'uuid_local'),
            'classes': ('collapse',)
        }),
    )
