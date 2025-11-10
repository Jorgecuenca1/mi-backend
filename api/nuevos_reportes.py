# Nuevos reportes PDF para VetControl
# IMPORTANTE: Importar pdf_utils ANTES que ReportLab para compatibilidad Python 3.8
from . import pdf_utils

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from django.db.models import Q, Count
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from io import BytesIO
from datetime import datetime, date
from collections import defaultdict
from .models import Responsable, Mascota, Planilla


@login_required
def reporte_municipio_por_dia_pdf(request):
    """
    Reporte 1: Por Municipio organizado por Día
    Muestra todos los registros agrupados por municipio y luego por día
    """
    user = request.user
    if user.tipo_usuario != 'administrador':
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('login')

    # Obtener todas las mascotas con sus relaciones
    mascotas = Mascota.objects.select_related(
        'responsable__planilla', 'created_by'
    ).order_by('responsable__planilla__municipio', 'creado')

    # Agrupar por municipio y luego por día
    data_por_municipio = defaultdict(lambda: defaultdict(list))

    for mascota in mascotas:
        municipio = mascota.responsable.planilla.municipio
        fecha = mascota.creado.date() if hasattr(mascota.creado, 'date') else mascota.creado
        data_por_municipio[municipio][fecha].append(mascota)

    # Crear PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), rightMargin=30, leftMargin=30,
                          topMargin=30, bottomMargin=18)
    elements = []

    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=1
    )

    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#333333'),
        spaceAfter=12
    )

    # Título
    title = Paragraph("Reporte de Vacunación por Municipio (Organizado por Día)", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.3*inch))

    # Diccionario para totales estadísticos por municipio
    estadisticas_por_municipio = {}

    # Procesar cada municipio
    for municipio in sorted(data_por_municipio.keys()):
        # Subtítulo del municipio
        municipio_title = Paragraph(f"<b>Municipio: {municipio}</b>", subtitle_style)
        elements.append(municipio_title)
        elements.append(Spacer(1, 0.1*inch))

        dias = data_por_municipio[municipio]

        # Tabla para este municipio - organizada por días
        table_data_mun = [[
            'Fecha',
            'Perros\nUrbano',
            'Perros\nRural',
            'Total\nPerros',
            'Gatos\nUrbano',
            'Gatos\nRural',
            'Total\nGatos',
            'Total\nUrbano',
            'Total\nRural',
            'TOTAL'
        ]]

        # Inicializar contadores para este municipio
        stats = {
            'perros_urbano': 0, 'perros_rural': 0,
            'gatos_urbano': 0, 'gatos_rural': 0
        }

        for fecha in sorted(dias.keys()):
            mascotas_dia = dias[fecha]

            # Contadores para este día
            stats_dia = {
                'perros_urbano': 0, 'perros_rural': 0,
                'gatos_urbano': 0, 'gatos_rural': 0
            }

            for mascota in mascotas_dia:
                resp = mascota.responsable

                # Contabilizar para estadísticas
                zona = (resp.zona or '').lower().strip()
                es_urbano = zona == 'barrio'
                es_rural = zona in ['vereda', 'centro poblado']

                if mascota.tipo == 'perro':
                    if es_urbano:
                        stats_dia['perros_urbano'] += 1
                        stats['perros_urbano'] += 1
                    elif es_rural:
                        stats_dia['perros_rural'] += 1
                        stats['perros_rural'] += 1
                elif mascota.tipo == 'gato':
                    if es_urbano:
                        stats_dia['gatos_urbano'] += 1
                        stats['gatos_urbano'] += 1
                    elif es_rural:
                        stats_dia['gatos_rural'] += 1
                        stats['gatos_rural'] += 1

            # Agregar fila para este día
            total_perros_dia = stats_dia['perros_urbano'] + stats_dia['perros_rural']
            total_gatos_dia = stats_dia['gatos_urbano'] + stats_dia['gatos_rural']
            total_urbano_dia = stats_dia['perros_urbano'] + stats_dia['gatos_urbano']
            total_rural_dia = stats_dia['perros_rural'] + stats_dia['gatos_rural']
            total_dia = total_perros_dia + total_gatos_dia

            table_data_mun.append([
                fecha.strftime('%d/%m/%Y'),
                str(stats_dia['perros_urbano']),
                str(stats_dia['perros_rural']),
                str(total_perros_dia),
                str(stats_dia['gatos_urbano']),
                str(stats_dia['gatos_rural']),
                str(total_gatos_dia),
                str(total_urbano_dia),
                str(total_rural_dia),
                str(total_dia)
            ])

        # Agregar subtotal del municipio
        total_perros = stats['perros_urbano'] + stats['perros_rural']
        total_gatos = stats['gatos_urbano'] + stats['gatos_rural']
        total_urbano = stats['perros_urbano'] + stats['gatos_urbano']
        total_rural = stats['perros_rural'] + stats['gatos_rural']
        total_general = total_perros + total_gatos

        table_data_mun.append([
            f'SUBTOTAL {municipio}',
            str(stats['perros_urbano']),
            str(stats['perros_rural']),
            str(total_perros),
            str(stats['gatos_urbano']),
            str(stats['gatos_rural']),
            str(total_gatos),
            str(total_urbano),
            str(total_rural),
            str(total_general)
        ])

        # Crear tabla para este municipio
        table = Table(table_data_mun, colWidths=[1.5*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90e2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#90EE90')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.lightgrey])
        ]))

        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))

        # Guardar estadísticas del municipio
        estadisticas_por_municipio[municipio] = stats

    # TOTALES GENERALES
    elements.append(PageBreak())
    elements.append(Paragraph("<b>TOTALES GENERALES</b>", title_style))
    elements.append(Spacer(1, 0.2*inch))

    totales = {
        'perros_urbano': 0, 'perros_rural': 0,
        'gatos_urbano': 0, 'gatos_rural': 0
    }

    for stats in estadisticas_por_municipio.values():
        totales['perros_urbano'] += stats['perros_urbano']
        totales['perros_rural'] += stats['perros_rural']
        totales['gatos_urbano'] += stats['gatos_urbano']
        totales['gatos_rural'] += stats['gatos_rural']

    total_perros_final = totales['perros_urbano'] + totales['perros_rural']
    total_gatos_final = totales['gatos_urbano'] + totales['gatos_rural']
    total_urbano_final = totales['perros_urbano'] + totales['gatos_urbano']
    total_rural_final = totales['perros_rural'] + totales['gatos_rural']
    total_final = total_perros_final + total_gatos_final

    totales_table_data = [
        ['Perros Urbano', 'Perros Rural', 'Total Perros', 'Gatos Urbano', 'Gatos Rural', 'Total Gatos', 'Total Urbano', 'Total Rural', 'TOTAL'],
        [str(totales['perros_urbano']), str(totales['perros_rural']), str(total_perros_final),
         str(totales['gatos_urbano']), str(totales['gatos_rural']), str(total_gatos_final),
         str(total_urbano_final), str(total_rural_final), str(total_final)]
    ]

    totales_table = Table(totales_table_data, colWidths=[0.9*inch] * 9)
    totales_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ffd700')),
        ('GRID', (0, 0), (-1, -1), 2, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
    ]))

    elements.append(totales_table)

    # Construir PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_municipio_por_dia_{datetime.now().strftime("%Y%m%d")}.pdf"'
    response.write(pdf)
    return response


@login_required
def reporte_dia_por_municipio_pdf(request):
    """
    Reporte 2: Por Día organizado por Municipio
    Muestra todos los registros agrupados por día y luego por municipio
    """
    user = request.user
    if user.tipo_usuario != 'administrador':
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('login')

    # Obtener todas las mascotas con sus relaciones
    mascotas = Mascota.objects.select_related(
        'responsable__planilla', 'created_by'
    ).order_by('creado', 'responsable__planilla__municipio')

    # Agrupar por día y luego por municipio
    data_por_dia = defaultdict(lambda: defaultdict(list))

    for mascota in mascotas:
        fecha = mascota.creado.date() if hasattr(mascota.creado, 'date') else mascota.creado
        municipio = mascota.responsable.planilla.municipio
        data_por_dia[fecha][municipio].append(mascota)

    # Crear PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), rightMargin=30, leftMargin=30,
                          topMargin=30, bottomMargin=18)
    elements = []

    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=1
    )

    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#333333'),
        spaceAfter=12
    )

    # Título
    title = Paragraph("Reporte de Vacunación por Día (Organizado por Municipio)", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.3*inch))

    # Diccionario para totales estadísticos por día
    estadisticas_por_dia = {}

    # Procesar cada día
    for fecha in sorted(data_por_dia.keys()):
        # Subtítulo del día
        dia_title = Paragraph(f"<b>Fecha: {fecha.strftime('%d de %B de %Y')}</b>", subtitle_style)
        elements.append(dia_title)
        elements.append(Spacer(1, 0.1*inch))

        municipios = data_por_dia[fecha]

        # Tabla para este día - organizada por municipios
        table_data_dia = [[
            'Municipio',
            'Perros\nUrbano',
            'Perros\nRural',
            'Total\nPerros',
            'Gatos\nUrbano',
            'Gatos\nRural',
            'Total\nGatos',
            'Total\nUrbano',
            'Total\nRural',
            'TOTAL'
        ]]

        # Inicializar contadores para este día
        stats = {
            'perros_urbano': 0, 'perros_rural': 0,
            'gatos_urbano': 0, 'gatos_rural': 0
        }

        for municipio in sorted(municipios.keys()):
            mascotas_municipio = municipios[municipio]

            # Contadores para este municipio en este día
            stats_mun = {
                'perros_urbano': 0, 'perros_rural': 0,
                'gatos_urbano': 0, 'gatos_rural': 0
            }

            for mascota in mascotas_municipio:
                resp = mascota.responsable

                # Contabilizar para estadísticas
                zona = (resp.zona or '').lower().strip()
                es_urbano = zona == 'barrio'
                es_rural = zona in ['vereda', 'centro poblado']

                if mascota.tipo == 'perro':
                    if es_urbano:
                        stats_mun['perros_urbano'] += 1
                        stats['perros_urbano'] += 1
                    elif es_rural:
                        stats_mun['perros_rural'] += 1
                        stats['perros_rural'] += 1
                elif mascota.tipo == 'gato':
                    if es_urbano:
                        stats_mun['gatos_urbano'] += 1
                        stats['gatos_urbano'] += 1
                    elif es_rural:
                        stats_mun['gatos_rural'] += 1
                        stats['gatos_rural'] += 1

            # Agregar fila para este municipio
            total_perros_mun = stats_mun['perros_urbano'] + stats_mun['perros_rural']
            total_gatos_mun = stats_mun['gatos_urbano'] + stats_mun['gatos_rural']
            total_urbano_mun = stats_mun['perros_urbano'] + stats_mun['gatos_urbano']
            total_rural_mun = stats_mun['perros_rural'] + stats_mun['gatos_rural']
            total_mun = total_perros_mun + total_gatos_mun

            table_data_dia.append([
                municipio,
                str(stats_mun['perros_urbano']),
                str(stats_mun['perros_rural']),
                str(total_perros_mun),
                str(stats_mun['gatos_urbano']),
                str(stats_mun['gatos_rural']),
                str(total_gatos_mun),
                str(total_urbano_mun),
                str(total_rural_mun),
                str(total_mun)
            ])

        # Agregar subtotal del día
        total_perros = stats['perros_urbano'] + stats['perros_rural']
        total_gatos = stats['gatos_urbano'] + stats['gatos_rural']
        total_urbano = stats['perros_urbano'] + stats['gatos_urbano']
        total_rural = stats['perros_rural'] + stats['gatos_rural']
        total_general = total_perros + total_gatos

        table_data_dia.append([
            f'SUBTOTAL {fecha.strftime("%d/%m/%Y")}',
            str(stats['perros_urbano']),
            str(stats['perros_rural']),
            str(total_perros),
            str(stats['gatos_urbano']),
            str(stats['gatos_rural']),
            str(total_gatos),
            str(total_urbano),
            str(total_rural),
            str(total_general)
        ])

        # Crear tabla para este día
        table = Table(table_data_dia, colWidths=[1.5*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90e2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#90EE90')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.lightgrey])
        ]))

        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))

        # Guardar estadísticas del día
        estadisticas_por_dia[fecha] = stats

    # TOTALES GENERALES
    elements.append(PageBreak())
    elements.append(Paragraph("<b>TOTALES GENERALES</b>", title_style))
    elements.append(Spacer(1, 0.2*inch))

    totales = {
        'perros_urbano': 0, 'perros_rural': 0,
        'gatos_urbano': 0, 'gatos_rural': 0
    }

    for stats in estadisticas_por_dia.values():
        totales['perros_urbano'] += stats['perros_urbano']
        totales['perros_rural'] += stats['perros_rural']
        totales['gatos_urbano'] += stats['gatos_urbano']
        totales['gatos_rural'] += stats['gatos_rural']

    total_perros_final = totales['perros_urbano'] + totales['perros_rural']
    total_gatos_final = totales['gatos_urbano'] + totales['gatos_rural']
    total_urbano_final = totales['perros_urbano'] + totales['gatos_urbano']
    total_rural_final = totales['perros_rural'] + totales['gatos_rural']
    total_final = total_perros_final + total_gatos_final

    totales_table_data = [
        ['Perros Urbano', 'Perros Rural', 'Total Perros', 'Gatos Urbano', 'Gatos Rural', 'Total Gatos', 'Total Urbano', 'Total Rural', 'TOTAL'],
        [str(totales['perros_urbano']), str(totales['perros_rural']), str(total_perros_final),
         str(totales['gatos_urbano']), str(totales['gatos_rural']), str(total_gatos_final),
         str(total_urbano_final), str(total_rural_final), str(total_final)]
    ]

    totales_table = Table(totales_table_data, colWidths=[0.9*inch] * 9)
    totales_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ffd700')),
        ('GRID', (0, 0), (-1, -1), 2, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
    ]))

    elements.append(totales_table)

    # Construir PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_dia_por_municipio_{datetime.now().strftime("%Y%m%d")}.pdf"'
    response.write(pdf)
    return response


@login_required
def reporte_estadistico_rango_fechas_pdf(request):
    """
    Reporte 3: Estadístico por Rango de Fechas
    Muestra totales de perros/gatos urbano/rural por municipio en un rango de fechas
    """
    user = request.user
    if user.tipo_usuario != 'administrador':
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('login')

    # Obtener parámetros de fecha
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')

    # Parsear fechas
    try:
        if fecha_inicio_str:
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
        else:
            fecha_inicio = None

        if fecha_fin_str:
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
        else:
            fecha_fin = None
    except ValueError:
        messages.error(request, 'Formato de fecha inválido. Use AAAA-MM-DD')
        return redirect('dashboard_administrador')

    # Filtrar mascotas por rango de fechas (si se especifican)
    mascotas_query = Mascota.objects.select_related('responsable__planilla')

    if fecha_inicio and fecha_fin:
        # Si se especifican ambas fechas
        mascotas = mascotas_query.filter(
            creado__date__gte=fecha_inicio,
            creado__date__lte=fecha_fin
        )
    elif fecha_inicio:
        # Solo fecha de inicio
        mascotas = mascotas_query.filter(creado__date__gte=fecha_inicio)
        fecha_fin = date.today()
    elif fecha_fin:
        # Solo fecha fin
        mascotas = mascotas_query.filter(creado__date__lte=fecha_fin)
        # Obtener la fecha más antigua de los registros
        primera_mascota = mascotas_query.order_by('creado').first()
        fecha_inicio = primera_mascota.creado.date() if primera_mascota else date.today()
    else:
        # Sin filtro de fechas - TODOS los registros
        mascotas = mascotas_query.all()
        # Obtener rango completo
        primera_mascota = mascotas_query.order_by('creado').first()
        ultima_mascota = mascotas_query.order_by('-creado').first()
        fecha_inicio = primera_mascota.creado.date() if primera_mascota else date.today()
        fecha_fin = ultima_mascota.creado.date() if ultima_mascota else date.today()

    # Agrupar por municipio y calcular estadísticas
    stats_por_municipio = defaultdict(lambda: {
        'perros_urbano': 0, 'perros_rural': 0, 'perros_total': 0,
        'gatos_urbano': 0, 'gatos_rural': 0, 'gatos_total': 0,
        'total_urbano': 0, 'total_rural': 0, 'total': 0
    })

    for mascota in mascotas:
        municipio = mascota.responsable.planilla.municipio
        zona = (mascota.responsable.zona or '').lower().strip()
        tipo = mascota.tipo

        # Determinar si es urbano o rural (case-insensitive)
        # URBANO: solo barrio
        # RURAL: vereda y centro poblado
        es_urbano = zona == 'barrio'
        es_rural = zona in ['vereda', 'centro poblado']

        # Contadores
        if tipo == 'perro':
            stats_por_municipio[municipio]['perros_total'] += 1
            if es_urbano:
                stats_por_municipio[municipio]['perros_urbano'] += 1
            elif es_rural:
                stats_por_municipio[municipio]['perros_rural'] += 1
        else:  # gato
            stats_por_municipio[municipio]['gatos_total'] += 1
            if es_urbano:
                stats_por_municipio[municipio]['gatos_urbano'] += 1
            elif es_rural:
                stats_por_municipio[municipio]['gatos_rural'] += 1

        if es_urbano:
            stats_por_municipio[municipio]['total_urbano'] += 1
        elif es_rural:
            stats_por_municipio[municipio]['total_rural'] += 1

        stats_por_municipio[municipio]['total'] += 1

    # Crear PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), rightMargin=30, leftMargin=30,
                          topMargin=30, bottomMargin=18)
    elements = []

    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=20,
        alignment=1
    )

    # Título
    title = Paragraph(
        f"Reporte Estadístico de Vacunación<br/>"
        f"<font size=12>Período: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}</font>",
        title_style
    )
    elements.append(title)
    elements.append(Spacer(1, 0.3*inch))

    # Tabla de estadísticas
    table_data = [[
        'Municipio',
        'Perros\nUrbano',
        'Perros\nRural',
        'Total\nPerros',
        'Gatos\nUrbano',
        'Gatos\nRural',
        'Total\nGatos',
        'Total\nUrbano',
        'Total\nRural',
        'TOTAL'
    ]]

    # Totales generales
    totales = {
        'perros_urbano': 0, 'perros_rural': 0, 'perros_total': 0,
        'gatos_urbano': 0, 'gatos_rural': 0, 'gatos_total': 0,
        'total_urbano': 0, 'total_rural': 0, 'total': 0
    }

    # Agregar datos por municipio
    for municipio in sorted(stats_por_municipio.keys()):
        stats = stats_por_municipio[municipio]
        table_data.append([
            municipio,
            str(stats['perros_urbano']),
            str(stats['perros_rural']),
            str(stats['perros_total']),
            str(stats['gatos_urbano']),
            str(stats['gatos_rural']),
            str(stats['gatos_total']),
            str(stats['total_urbano']),
            str(stats['total_rural']),
            str(stats['total'])
        ])

        # Sumar a totales
        for key in totales:
            totales[key] += stats[key]

    # Agregar fila de totales
    table_data.append([
        'TOTALES',
        str(totales['perros_urbano']),
        str(totales['perros_rural']),
        str(totales['perros_total']),
        str(totales['gatos_urbano']),
        str(totales['gatos_rural']),
        str(totales['gatos_total']),
        str(totales['total_urbano']),
        str(totales['total_rural']),
        str(totales['total'])
    ])

    table = Table(table_data, colWidths=[1.5*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90e2')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ffd700')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.lightgrey])
    ]))

    elements.append(table)

    # Construir PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_estadistico_{fecha_inicio.strftime("%Y%m%d")}_{fecha_fin.strftime("%Y%m%d")}.pdf"'
    response.write(pdf)
    return response
