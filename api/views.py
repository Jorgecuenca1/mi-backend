from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import render
from django.db.models import Count, Q
import json
import base64
from django.core.files.base import ContentFile
from .models import Planilla, Mascota, Responsable
from .serializers import PlanillaSerializer, MascotaSerializer, ResponsableSerializer
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ResponsableForm, MascotaFormSet
from .models import Planilla
from django.contrib.auth.decorators import login_required
@login_required
def elegir_planilla(request):
    """
    Muestra las planillas asignadas al veterinario logueado
    para que elija en cuál va a agregar responsables y mascotas.
    """
    planillas = Planilla.objects.filter(assigned_to=request.user)
    return render(request, 'api/elegir_planilla.html', {
        'planillas': planillas
    })

def crear_responsable_con_mascotas(request, planilla_id):
    # 1) Obtén la planilla o 404
    planilla = get_object_or_404(Planilla, id=planilla_id)

    if request.method == 'POST':
        form = ResponsableForm(request.POST)
        formset = MascotaFormSet(request.POST, request.FILES)

        if form.is_valid() and formset.is_valid():
            # 2) Guarda Responsable
            responsable = form.save(commit=False)
            responsable.planilla = planilla
            responsable.save()

            # 3) Asocia el formset al responsable
            formset.instance = responsable
            formset.save()

            return redirect('detalle_planilla', pk=planilla.id)  # o a donde quieras
    else:
        form = ResponsableForm()
        formset = MascotaFormSet()

    return render(request, 'api/responsable_form.html', {
        'form': form,
        'formset': formset,
        'planilla': planilla
    })

class ResponsableViewSet(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, planilla_id=None):
        """GET: Lista responsables de una planilla específica"""
        if planilla_id:
            responsables = Responsable.objects.filter(planilla_id=planilla_id)
        else:
            responsables = Responsable.objects.all()
        return Response(ResponsableSerializer(responsables, many=True).data)
    
    def post(self, request, planilla_id=None):
        """POST: Crea un nuevo responsable con sus mascotas"""
        try:
            if planilla_id:
                planilla = Planilla.objects.get(id=planilla_id)
            else:
                planilla_id = request.data.get('planilla_id')
                planilla = Planilla.objects.get(id=planilla_id)
        except Planilla.DoesNotExist:
            return Response({'error': 'Planilla no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        
        # Crear responsable
        responsable_data = {
            'nombre': request.data.get('nombre'),
            'telefono': request.data.get('telefono'),
            'finca': request.data.get('finca'),
            'zona': request.data.get('zona', 'Sin especificar'),
            'nombre_zona': request.data.get('nombre_zona', 'Sin especificar'),
            'lote_vacuna': request.data.get('lote_vacuna', 'Sin especificar'),
            'planilla': planilla.id
        }
        
        responsable_serializer = ResponsableSerializer(data=responsable_data)
        if responsable_serializer.is_valid():
            responsable = responsable_serializer.save()
            
            # Crear mascotas si se proporcionan
            mascotas_data = request.data.get('mascotas', [])
            mascotas_creadas = []
            
            print(f"🔍 DEBUG: mascotas_data tipo: {type(mascotas_data)}")
            print(f"🔍 DEBUG: mascotas_data contenido (primeros 200 chars): {str(mascotas_data)[:200]}")
            
            # Si mascotas_data es un string, parsearlo como JSON
            if isinstance(mascotas_data, str):
                try:
                    mascotas_data = json.loads(mascotas_data)
                    print(f"✅ JSON parseado exitosamente. Tipo: {type(mascotas_data)}, Items: {len(mascotas_data)}")
                except json.JSONDecodeError:
                    print(f"❌ Error parseando JSON de mascotas: {mascotas_data}")
                    mascotas_data = []
            
            # Procesar cada mascota
            for i, mascota_data in enumerate(mascotas_data):
                print(f"🐕 Procesando mascota {i+1}: tipo {type(mascota_data)}")
                
                # Verificar si mascota_data es un diccionario
                if isinstance(mascota_data, dict):
                    # Hacer una copia del diccionario para evitar el error
                    mascota_data_copy = mascota_data.copy()
                    mascota_data_copy['responsable'] = responsable.id
                    
                    # DEBUG: Verificar foto
                    foto_base64 = mascota_data_copy.get('foto')
                    foto_index = mascota_data_copy.get('foto_index')
                    print(f"📸 Foto encontrada: {type(foto_base64)}, longitud: {len(str(foto_base64)) if foto_base64 else 0}")
                    print(f"📸 Foto_index encontrado: {foto_index}")
                    
                    # Procesar foto si existe
                    if foto_base64 and isinstance(foto_base64, str) and len(foto_base64) > 100:
                        try:
                            print("📸 Procesando foto base64...")
                            
                            # Remover el prefijo data:image si existe
                            if foto_base64.startswith('data:image'):
                                foto_base64 = foto_base64.split(',')[1]
                                print("📸 Prefijo data:image removido")
                            
                            # Decodificar base64
                            foto_data = base64.b64decode(foto_base64)
                            foto_file = ContentFile(foto_data, name=f'mascota_{mascota_data_copy.get("nombre", "sin_nombre")}.png')
                            mascota_data_copy['foto'] = foto_file
                            print(f"✅ Foto procesada para mascota: {mascota_data_copy.get('nombre')}")
                        except Exception as e:
                            print(f"❌ Error procesando foto: {e}")
                            mascota_data_copy.pop('foto', None)
                    else:
                        print(f"⚠️ Foto no válida o muy corta: {len(str(foto_base64)) if foto_base64 else 0} chars")
                        # Limpiar campos de foto para evitar errores
                        mascota_data_copy.pop('foto', None)
                        mascota_data_copy.pop('foto_index', None)
                    
                    mascota_serializer = MascotaSerializer(data=mascota_data_copy)
                    if mascota_serializer.is_valid():
                        mascota = mascota_serializer.save()
                        mascotas_creadas.append(mascota_serializer.data)
                        print(f"✅ Mascota {mascota.nombre} creada exitosamente")
                    else:
                        print(f"❌ Error en mascota serializer: {mascota_serializer.errors}")
                else:
                    print(f"❌ mascota_data no es un diccionario: {type(mascota_data)}, valor: {mascota_data}")
            
            response_data = responsable_serializer.data
            response_data['mascotas'] = mascotas_creadas
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response(responsable_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MascotaViewSet(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, responsable_id):
        """GET: Lista mascotas de un responsable específico"""
        try:
            mascotas = Mascota.objects.filter(responsable_id=responsable_id)
            return Response(MascotaSerializer(mascotas, many=True).data)
        except Responsable.DoesNotExist:
            return Response({'error': 'Responsable no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request, responsable_id):
        """POST: Crea una nueva mascota para un responsable"""
        try:
            responsable = Responsable.objects.get(id=responsable_id)
        except Responsable.DoesNotExist:
            return Response({'error': 'Responsable no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        mascota_data = request.data.copy()
        mascota_data['responsable'] = responsable_id
        
        serializer = MascotaSerializer(data=mascota_data)
        if serializer.is_valid():
            mascota = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mis_planillas(request):
    """Lista planillas filtradas por el usuario.

    Reglas:
    - Si viene ?usuario=<username>, filtra por ese username (útil para apps móviles).
    - En otro caso, filtra por el usuario autenticado (request.user).
    - Incluye planillas donde el usuario es asignado principal O adicional.
    """
    username = request.query_params.get('usuario') or request.user.username
    qs = Planilla.objects.all()
    if username:
        # Filtrar por asignaciones principales Y adicionales
        qs = qs.filter(
            Q(assigned_to__username=username) |  # Vacunador principal (compatibilidad app móvil)
            Q(vacunadores_adicionales__username=username) |  # Vacunadores adicionales
            Q(tecnico_asignado__username=username) |  # Técnico principal
            Q(tecnicos_adicionales__username=username)  # Técnicos adicionales
        ).distinct()
    return Response(PlanillaSerializer(qs, many=True).data)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def mascotas_planilla(request, pk):
    try:
        plan = Planilla.objects.get(pk=pk)
    except Planilla.DoesNotExist:
        return Response(status=404)

    if request.method == 'GET':
        return Response(MascotaSerializer(plan.mascotas.all(), many=True).data)

    # POST → crea mascota
    serializer = MascotaSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(planilla=plan)
    return Response(serializer.data, status=201)


def landing_page(request):
    """Vista para la landing page con estadísticas generales"""
    # Calcular estadísticas generales
    total_planillas = Planilla.objects.count()
    total_responsables = Responsable.objects.count()
    total_mascotas = Mascota.objects.count()
    # Todos están vacunados, el campo se refiere a tarjeta de vacunación previa
    mascotas_con_tarjeta_previa = Mascota.objects.filter(antecedente_vacunal=True).count()
    
    context = {
        'total_planillas': total_planillas,
        'total_responsables': total_responsables,
        'total_mascotas': total_mascotas,
        'mascotas_vacunadas': total_mascotas,  # Todos están vacunados
        'mascotas_con_tarjeta_previa': mascotas_con_tarjeta_previa,
    }
    
    return render(request, 'api/landing.html', context)


@login_required
def reportes_view(request):
    """Vista para reportes detallados por municipio - filtrada por rol de usuario"""
    user = request.user
    
    # Filtrar planillas según el rol del usuario
    if user.tipo_usuario == 'administrador':
        # Administradores ven todas las planillas
        planillas = Planilla.objects.select_related().prefetch_related('responsables__mascotas')
    elif user.tipo_usuario == 'tecnico':
        # Técnicos ven solo las planillas de sus municipios asignados
        planillas = Planilla.objects.filter(
            Q(tecnico_asignado=user) |
            Q(tecnicos_adicionales=user)
        ).select_related().prefetch_related('responsables__mascotas').distinct()
    elif user.tipo_usuario == 'vacunador':
        # Vacunadores ven solo sus planillas asignadas
        planillas = Planilla.objects.filter(
            Q(assigned_to=user) |
            Q(vacunadores_adicionales=user)
        ).select_related().prefetch_related('responsables__mascotas').distinct()
    else:
        planillas = Planilla.objects.none()
    
    # Diccionario para agrupar por municipio
    municipios_stats = {}
    
    for planilla in planillas:
        municipio = planilla.municipio
        if municipio not in municipios_stats:
            municipios_stats[municipio] = {
                'municipio': municipio,
                'total_mascotas': 0,
                'con_tarjeta_previa': 0,
                'sin_tarjeta_previa': 0,
                'zona_urbana': 0,
                'zona_rural': 0,
                'perros': 0,
                'gatos': 0,
                'responsables': 0,
                'planillas': 0,
            }
        
        # Contar planillas por municipio
        municipios_stats[municipio]['planillas'] += 1
        
        # Contar responsables y mascotas por planilla
        # Filtrar responsables según el rol del usuario
        if user.tipo_usuario == 'vacunador':
            # Vacunadores solo ven sus propios registros
            responsables = planilla.responsables.filter(created_by=user)
        else:
            # Técnicos y administradores ven todos los registros de la planilla
            responsables = planilla.responsables.all()
            
        for responsable in responsables:
            municipios_stats[municipio]['responsables'] += 1
            
            # Filtrar mascotas según el rol del usuario
            if user.tipo_usuario == 'vacunador':
                mascotas = responsable.mascotas.filter(created_by=user)
            else:
                mascotas = responsable.mascotas.all()
            
            for mascota in mascotas:
                municipios_stats[municipio]['total_mascotas'] += 1
                
                # Contar por tarjeta de vacunación previa (todos son vacunados ahora)
                if mascota.antecedente_vacunal:
                    municipios_stats[municipio]['con_tarjeta_previa'] += 1
                else:
                    municipios_stats[municipio]['sin_tarjeta_previa'] += 1
                
                # Contar por zona (basado en la planilla)
                if planilla.urbano_rural == 'urbano':
                    municipios_stats[municipio]['zona_urbana'] += 1
                else:
                    municipios_stats[municipio]['zona_rural'] += 1
                
                # Contar por tipo
                if mascota.tipo == 'perro':
                    municipios_stats[municipio]['perros'] += 1
                else:
                    municipios_stats[municipio]['gatos'] += 1
    
    # Calcular porcentajes de tarjetas previas
    reportes_municipio = []
    for stats in municipios_stats.values():
        if stats['total_mascotas'] > 0:
            porcentaje_tarjeta_previa = round((stats['con_tarjeta_previa'] / stats['total_mascotas']) * 100, 1)
        else:
            porcentaje_tarjeta_previa = 0
        
        stats['porcentaje_tarjeta_previa'] = porcentaje_tarjeta_previa
        reportes_municipio.append(stats)
    
    # Ordenar por municipio
    reportes_municipio.sort(key=lambda x: x['municipio'])
    
    # Calcular estadísticas generales
    total_municipios = len(municipios_stats)
    total_planillas = sum(stats['planillas'] for stats in municipios_stats.values())
    total_responsables = sum(stats['responsables'] for stats in municipios_stats.values())
    total_mascotas = sum(stats['total_mascotas'] for stats in municipios_stats.values())
    total_con_tarjeta = sum(stats['con_tarjeta_previa'] for stats in municipios_stats.values())
    total_sin_tarjeta = sum(stats['sin_tarjeta_previa'] for stats in municipios_stats.values())
    total_urbano = sum(stats['zona_urbana'] for stats in municipios_stats.values())
    total_rural = sum(stats['zona_rural'] for stats in municipios_stats.values())
    total_perros = sum(stats['perros'] for stats in municipios_stats.values())
    total_gatos = sum(stats['gatos'] for stats in municipios_stats.values())
    
    # Calcular porcentajes generales
    if total_mascotas > 0:
        porcentaje_general_tarjeta = round((total_con_tarjeta / total_mascotas) * 100, 1)
    else:
        porcentaje_general_tarjeta = 0
    
    context = {
        'reportes_municipio': reportes_municipio,
        'total_municipios': total_municipios,
        'total_planillas': total_planillas,
        'total_responsables': total_responsables,
        'total_mascotas': total_mascotas,
        'total_con_tarjeta': total_con_tarjeta,
        'total_sin_tarjeta': total_sin_tarjeta,
        'total_urbano': total_urbano,
        'total_rural': total_rural,
        'total_perros': total_perros,
        'total_gatos': total_gatos,
        'porcentaje_general_tarjeta': porcentaje_general_tarjeta,
    }
    
    return render(request, 'api/reportes.html', context)


from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import redirect

def login_view(request):
    """Vista para el inicio de sesión"""
    if request.user.is_authenticated:
        return redirect('dashboard_principal')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido, {user.username}!')
            return redirect('dashboard_principal')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    
    return render(request, 'api/login.html')


@login_required
def dashboard_principal(request):
    """Dashboard principal que redirije según el tipo de usuario"""
    user = request.user
    
    if user.tipo_usuario == 'administrador':
        # Administradores van a la landing page con estadísticas completas
        return redirect('landing')
    elif user.tipo_usuario == 'tecnico':
        # Técnicos van directamente a reportes (pueden ver todos los registros de sus municipios)
        return redirect('reportes')
    elif user.tipo_usuario == 'vacunador':
        # Vacunadores van a reportes (solo ven sus propios registros)
        return redirect('reportes')
    else:
        messages.error(request, 'Tipo de usuario no válido.')
        return redirect('login')


def logout_view(request):
    """Vista para cerrar sesión"""
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('login')


# ========== NUEVAS VISTAS CON PERMISOS POR TIPO DE USUARIO ==========

@login_required
def dashboard_vacunador(request):
    """Dashboard para vacunadores - Solo ven sus propias planillas, responsables y mascotas"""
    if request.user.tipo_usuario != 'vacunador':
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('login')
    
    # Planillas donde el usuario es vacunador principal O adicional
    planillas = Planilla.objects.filter(
        Q(assigned_to=request.user) |  # Vacunador principal
        Q(vacunadores_adicionales=request.user)  # Vacunador adicional
    ).distinct()
    
    responsables = Responsable.objects.filter(
        Q(planilla__assigned_to=request.user) |
        Q(planilla__vacunadores_adicionales=request.user)
    ).distinct()
    
    mascotas = Mascota.objects.filter(
        Q(responsable__planilla__assigned_to=request.user) |
        Q(responsable__planilla__vacunadores_adicionales=request.user)
    ).distinct()
    
    context = {
        'user_type': 'Vacunador',
        'planillas': planillas,
        'total_planillas': planillas.count(),
        'total_responsables': responsables.count(),
        'total_mascotas': mascotas.count(),
        'mascotas_con_tarjeta': mascotas.filter(antecedente_vacunal=True).count(),
    }
    
    return render(request, 'api/dashboard_usuario.html', context)


@login_required
def dashboard_tecnico(request):
    """Dashboard para técnicos - Solo ven planillas asignadas para revisar"""
    if request.user.tipo_usuario != 'tecnico':
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('login')
    
    # Planillas donde el usuario es técnico principal O adicional
    planillas = Planilla.objects.filter(
        Q(tecnico_asignado=request.user) |  # Técnico principal
        Q(tecnicos_adicionales=request.user)  # Técnico adicional
    ).distinct()
    
    responsables = Responsable.objects.filter(
        Q(planilla__tecnico_asignado=request.user) |
        Q(planilla__tecnicos_adicionales=request.user)
    ).distinct()
    
    mascotas = Mascota.objects.filter(
        Q(responsable__planilla__tecnico_asignado=request.user) |
        Q(responsable__planilla__tecnicos_adicionales=request.user)
    ).distinct()
    
    context = {
        'user_type': 'Técnico',
        'planillas': planillas,
        'total_planillas': planillas.count(),
        'total_responsables': responsables.count(),
        'total_mascotas': mascotas.count(),
        'mascotas_con_tarjeta': mascotas.filter(antecedente_vacunal=True).count(),
    }
    
    return render(request, 'api/dashboard_usuario.html', context)


@login_required
def dashboard_administrador(request):
    """Dashboard para administradores - Ven todo"""
    if request.user.tipo_usuario != 'administrador':
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('login')
    
    # Administradores ven todo
    planillas = Planilla.objects.all()
    responsables = Responsable.objects.all()
    mascotas = Mascota.objects.all()
    
    context = {
        'user_type': 'Administrador',
        'planillas': planillas,
        'total_planillas': planillas.count(),
        'total_responsables': responsables.count(),
        'total_mascotas': mascotas.count(),
        'mascotas_con_tarjeta': mascotas.filter(antecedente_vacunal=True).count(),
    }
    
    return render(request, 'api/dashboard_usuario.html', context)


@login_required
def dashboard_principal(request):
    """Vista principal que redirige según el tipo de usuario"""
    if request.user.tipo_usuario == 'administrador':
        return redirect('dashboard_administrador')
    elif request.user.tipo_usuario == 'vacunador':
        return redirect('dashboard_vacunador')
    elif request.user.tipo_usuario == 'tecnico':
        return redirect('dashboard_tecnico')
    else:
        messages.error(request, 'Tipo de usuario no válido.')
        return redirect('login') 