from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

from .views import crear_responsable_con_mascotas

urlpatterns = [
    # APIs REST
    path('planillas/', views.mis_planillas),
    path('planillas/<int:pk>/mascotas/', views.mascotas_planilla),
    
    # Nuevas APIs para Responsables y Mascotas
    path('responsables/', views.ResponsableViewSet.as_view()),
    path('planillas/<int:planilla_id>/responsables/', views.ResponsableViewSet.as_view()),
    path('responsables/<int:responsable_id>/mascotas/', views.MascotaViewSet.as_view()),
    
    # Vistas de autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboards por tipo de usuario
    path('dashboard/', views.dashboard_principal, name='dashboard_principal'),
    path('dashboard/administrador/', views.dashboard_administrador, name='dashboard_administrador'),
    path('dashboard/vacunador/', views.dashboard_vacunador, name='dashboard_vacunador'),
    path('dashboard/tecnico/', views.dashboard_tecnico, name='dashboard_tecnico'),
    
    # Vistas de planillas y responsables
    path('responsables/seleccionar/', views.elegir_planilla, name='elegir_planilla'),
    path('planillas/<int:planilla_id>/responsable/nuevo/',
     crear_responsable_con_mascotas,
     name='crear_responsable'),
    
    # URLs para registro de pérdidas
    path('perdidas/', views.registro_perdidas_list, name='registro_perdidas_list'),
    path('perdidas/estadisticas/', views.estadisticas_perdidas, name='estadisticas_perdidas'),

    # URL para reporte PDF de vacunadores
    path('reporte/vacunador/pdf/', views.reporte_vacunador_pdf, name='reporte_vacunador_pdf'),

    # URL para imprimir planilla por municipio (técnicos y vacunadores)
    path('planilla/imprimir/', views.imprimir_planilla_municipio_pdf, name='imprimir_planilla_municipio'),

    # URL para reporte estadístico de vacunación (técnicos y vacunadores)
    path('reporte/estadistico/', views.reporte_estadistico_vacunacion_pdf, name='reporte_estadistico_vacunacion'),

    # URLs para el árbol de reportes (solo administradores)
    path('reportes/arbol/', views.arbol_reportes, name='arbol_reportes'),
    path('reportes/estadisticas/', views.estadisticas_generales, name='estadisticas_generales'),
    path('reportes/filtros/', views.opciones_filtros_reportes, name='opciones_filtros_reportes'),
    path('reportes/arbol-web/', views.arbol_reportes_view, name='arbol_reportes_view'),

    # URLs para edición de responsables y mascotas
    path('responsables/<int:responsable_id>/', views.update_responsable, name='update_responsable'),
    path('mascotas/<int:mascota_id>/', views.update_mascota, name='update_mascota'),

    # URLs para eliminación de responsables y mascotas
    path('responsables/<int:responsable_id>/delete/', views.delete_responsable, name='delete_responsable'),
    path('mascotas/<int:mascota_id>/delete/', views.delete_mascota, name='delete_mascota'),

    # URLs para edición de fechas de creación
    path('responsables/<int:responsable_id>/fecha/', views.update_fecha_creacion_responsable, name='update_fecha_creacion_responsable'),
    path('mascotas/<int:mascota_id>/fecha/', views.update_fecha_creacion_mascota, name='update_fecha_creacion_mascota'),

    # URL para importación masiva de responsables y mascotas
    path('importar/responsables-mascotas/', views.importar_responsables_mascotas, name='importar_responsables_mascotas'),
]