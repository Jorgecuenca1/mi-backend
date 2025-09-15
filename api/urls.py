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
]