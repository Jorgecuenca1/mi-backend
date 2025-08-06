# api/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Veterinario, Planilla, Mascota, Responsable

@admin.register(Veterinario)
class VeterinarioAdmin(UserAdmin):
    """Admin para veterinarios (usuarios)."""
    pass

@admin.register(Planilla)
class PlanillaAdmin(admin.ModelAdmin):
    """Admin para planillas asignadas a cada veterinario."""
    list_display = ('id', 'nombre', 'assigned_to', 'creada')
    list_filter = ('assigned_to', 'creada')
    search_fields = ('nombre', 'assigned_to__username')
    ordering = ('-creada',)

@admin.register(Responsable)
class ResponsableAdmin(admin.ModelAdmin):
    """Admin para responsables de mascotas."""
    list_display = ('id', 'nombre', 'telefono', 'finca', 'planilla', 'creado')
    list_filter = ('planilla', 'creado')
    search_fields = ('nombre', 'telefono', 'finca')
    ordering = ('-creado',)

@admin.register(Mascota)
class MascotaAdmin(admin.ModelAdmin):
    """Admin para las mascotas de cada responsable."""
    list_display = ('id', 'nombre', 'tipo', 'raza', 'color', 'responsable', 'latitud', 'longitud', 'creado')
    list_filter = ('tipo', 'raza', 'antecedente_vacunal', 'responsable', 'creado')
    search_fields = ('nombre', 'responsable__nombre')
    ordering = ('-creado',)
    readonly_fields = ('creado',)
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'tipo', 'raza', 'color', 'antecedente_vacunal', 'responsable')
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
            'fields': ('creado',),
            'classes': ('collapse',)
        }),
    )
