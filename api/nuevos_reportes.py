# Nuevos reportes PDF para VetControl
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
    from . import pdf_utils

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

    # Procesar cada municipio
    for municipio in sorted(data_por_municipio.keys()):
        # Subtítulo del municipio
        municipio_title = Paragraph(f"<b>Municipio: {municipio}</b>", subtitle_style)
        elements.append(municipio_title)
        elements.append(Spacer(1, 0.1*inch))

        dias = data_por_municipio[municipio]
        total_municipio = 0

        for fecha in sorted(dias.keys()):
            mascotas_dia = dias[fecha]
            total_municipio += len(mascotas_dia)

            # Encabezado de día
            dia_texto = Paragraph(f"<i>Fecha: {fecha.strftime('%d/%m/%Y')}</i>", styles['Normal'])
            elements.append(dia_texto)
            elements.append(Spacer(1, 0.05*inch))

            # Tabla de mascotas
            table_data = [['#', 'Responsable', 'Mascota', 'Tipo', 'Raza', 'Color', 'Zona', 'Vacunador']]

            for idx, mascota in enumerate(mascotas_dia, 1):
                resp = mascota.responsable
                zona_text = resp.zona or 'N/A'
                table_data.append([
                    str(idx),
                    resp.nombre[:20],
                    mascota.nombre[:15],
                    'P' if mascota.tipo == 'perro' else 'G',
                    mascota.raza[:15] if mascota.raza else 'N/A',
                    mascota.color[:10] if mascota.color else 'N/A',
                    zona_text[:15],
                    mascota.created_by.username[:12] if mascota.created_by else 'N/A'
                ])

            table = Table(table_data, colWidths=[0.4*inch, 1.2*inch, 1*inch, 0.5*inch, 1*inch, 0.8*inch, 1*inch, 0.8*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90e2')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))

            elements.append(table)
            elements.append(Spacer(1, 0.15*inch))

        # Total del municipio
        total_text = Paragraph(f"<b>Total {municipio}: {total_municipio} mascotas</b>", subtitle_style)
        elements.append(total_text)
        elements.append(Spacer(1, 0.2*inch))
        elements.append(PageBreak())

    # Total general
    total_general = sum(len(dias_data) for municipio_data in data_por_municipio.values()
                       for dias_data in municipio_data.values())
    total_final = Paragraph(f"<b>TOTAL GENERAL: {total_general} mascotas vacunadas</b>", title_style)
    elements.append(total_final)

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
    from . import pdf_utils

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

    # Procesar cada día
    for fecha in sorted(data_por_dia.keys()):
        # Subtítulo del día
        dia_title = Paragraph(f"<b>Fecha: {fecha.strftime('%d de %B de %Y')}</b>", subtitle_style)
        elements.append(dia_title)
        elements.append(Spacer(1, 0.1*inch))

        municipios = data_por_dia[fecha]
        total_dia = 0

        for municipio in sorted(municipios.keys()):
            mascotas_municipio = municipios[municipio]
            total_dia += len(mascotas_municipio)

            # Encabezado de municipio
            municipio_texto = Paragraph(f"<i>Municipio: {municipio}</i>", styles['Normal'])
            elements.append(municipio_texto)
            elements.append(Spacer(1, 0.05*inch))

            # Tabla de mascotas
            table_data = [['#', 'Responsable', 'Mascota', 'Tipo', 'Raza', 'Color', 'Zona', 'Vacunador']]

            for idx, mascota in enumerate(mascotas_municipio, 1):
                resp = mascota.responsable
                zona_text = resp.zona or 'N/A'
                table_data.append([
                    str(idx),
                    resp.nombre[:20],
                    mascota.nombre[:15],
                    'P' if mascota.tipo == 'perro' else 'G',
                    mascota.raza[:15] if mascota.raza else 'N/A',
                    mascota.color[:10] if mascota.color else 'N/A',
                    zona_text[:15],
                    mascota.created_by.username[:12] if mascota.created_by else 'N/A'
                ])

            table = Table(table_data, colWidths=[0.4*inch, 1.2*inch, 1*inch, 0.5*inch, 1*inch, 0.8*inch, 1*inch, 0.8*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90e2')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))

            elements.append(table)
            elements.append(Spacer(1, 0.15*inch))

        # Total del día
        total_text = Paragraph(f"<b>Total {fecha.strftime('%d/%m/%Y')}: {total_dia} mascotas</b>", subtitle_style)
        elements.append(total_text)
        elements.append(Spacer(1, 0.2*inch))
        elements.append(PageBreak())

    # Total general
    total_general = sum(len(municipios_data) for dia_data in data_por_dia.values()
                       for municipios_data in dia_data.values())
    total_final = Paragraph(f"<b>TOTAL GENERAL: {total_general} mascotas vacunadas</b>", title_style)
    elements.append(total_final)

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
    from . import pdf_utils

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
            fecha_inicio = date(2000, 1, 1)

        if fecha_fin_str:
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
        else:
            fecha_fin = date.today()
    except ValueError:
        messages.error(request, 'Formato de fecha inválido. Use AAAA-MM-DD')
        return redirect('dashboard_administrador')

    # Filtrar mascotas por rango de fechas
    mascotas = Mascota.objects.select_related(
        'responsable__planilla'
    ).filter(
        creado__date__gte=fecha_inicio,
        creado__date__lte=fecha_fin
    )

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
