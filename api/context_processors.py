from .models import Planilla

def municipios_list(request):
    """Context processor para hacer municipios_unicos disponible en todos los templates"""
    if request.user.is_authenticated and request.user.tipo_usuario == 'administrador':
        municipios = list(Planilla.objects.values_list('municipio', flat=True).distinct().order_by('municipio'))
        return {'municipios_unicos': municipios}
    return {'municipios_unicos': []}
