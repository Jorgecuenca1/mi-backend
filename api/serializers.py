from rest_framework import serializers
from .models import Planilla, Mascota, Responsable

class ResponsableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Responsable
        fields = ['id', 'nombre', 'telefono', 'finca', 'planilla', 'zona', 'nombre_zona', 'lote_vacuna', 'creado']

class MascotaSerializer(serializers.ModelSerializer):
    latitud = serializers.DecimalField(max_digits=15, decimal_places=10, coerce_to_string=False)
    longitud = serializers.DecimalField(max_digits=15, decimal_places=10, coerce_to_string=False)
    
    class Meta:
        model = Mascota
        fields = ['id', 'nombre', 'tipo', 'raza', 'color', 'antecedente_vacunal', 'responsable', 'latitud', 'longitud', 'foto', 'creado']

class PlanillaSerializer(serializers.ModelSerializer):
    responsables = ResponsableSerializer(many=True, read_only=True)
    
    # Campos extra para compatibilidad con app móvil (MANTENER)
    usuario = serializers.SerializerMethodField()
    asignadoA = serializers.SerializerMethodField()
    asignado_a = serializers.SerializerMethodField()
    
    # NUEVOS CAMPOS: Múltiples asignaciones (opcionales para backend/admin)
    vacunadores_adicionales = serializers.StringRelatedField(many=True, read_only=True)
    tecnicos_adicionales = serializers.StringRelatedField(many=True, read_only=True)
    todos_vacunadores = serializers.SerializerMethodField()
    todos_tecnicos = serializers.SerializerMethodField()
    
    municipio = serializers.CharField()
    urbano_rural = serializers.CharField()
    centro_poblado_vereda_barrio = serializers.CharField()

    class Meta:
        model = Planilla
        fields = [
            'id', 'nombre', 'creada',
            'municipio', 'urbano_rural', 'centro_poblado_vereda_barrio',
            'responsables',
            # Compatibilidad app móvil (MANTENER)
            'usuario', 'asignadoA', 'asignado_a',
            # Nuevos campos para múltiples asignaciones
            'vacunadores_adicionales', 'tecnicos_adicionales',
            'todos_vacunadores', 'todos_tecnicos',
        ]

    def get_usuario(self, obj):
        return getattr(obj.assigned_to, 'username', None)

    def get_asignadoA(self, obj):
        return getattr(obj.assigned_to, 'username', None)

    def get_asignado_a(self, obj):
        return getattr(obj.assigned_to, 'username', None)
    
    def get_todos_vacunadores(self, obj):
        """Retorna lista con vacunador principal + adicionales"""
        vacunadores = []
        if obj.assigned_to:
            vacunadores.append(obj.assigned_to.username)
        vacunadores.extend([v.username for v in obj.vacunadores_adicionales.all()])
        return vacunadores
    
    def get_todos_tecnicos(self, obj):
        """Retorna lista con técnico principal + adicionales"""
        tecnicos = []
        if obj.tecnico_asignado:
            tecnicos.append(obj.tecnico_asignado.username)
        tecnicos.extend([t.username for t in obj.tecnicos_adicionales.all()])
        return tecnicos
