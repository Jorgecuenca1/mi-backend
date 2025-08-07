from django import forms
from django.forms import inlineformset_factory
from .models import Responsable, Mascota

class ResponsableForm(forms.ModelForm):
    class Meta:
        model = Responsable
        fields = [
            'nombre', 'telefono', 'finca',
            'zona', 'nombre_zona', 'lote_vacuna'
        ]
        widgets = {
            'zona': forms.TextInput(attrs={'placeholder': 'Ej. Norte'}),
            'lote_vacuna': forms.TextInput(attrs={'placeholder': 'Ej. Lote 123'}),
        }

class MascotaForm(forms.ModelForm):
    class Meta:
        model = Mascota
        fields = [
            'nombre', 'tipo', 'raza', 'color',
            'antecedente_vacunal', 'latitud', 'longitud', 'foto'
        ]
        widgets = {
            'antecedente_vacunal': forms.CheckboxInput(),
        }

# InlineFormset: 3 formularios extra, puedes ajustar extra=N
MascotaFormSet = inlineformset_factory(
    Responsable, Mascota,
    form=MascotaForm,
    extra=3,
    can_delete=True
)
