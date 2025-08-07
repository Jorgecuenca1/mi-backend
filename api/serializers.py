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
    
    class Meta:
        model = Planilla
        fields = ['id', 'nombre', 'creada', 'responsables']
