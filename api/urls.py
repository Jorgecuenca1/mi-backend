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
    
    # Vistas de planillas y responsables
    path('responsables/seleccionar/', views.elegir_planilla, name='elegir_planilla'),
    path('planillas/<int:planilla_id>/responsable/nuevo/',
     crear_responsable_con_mascotas,
     name='crear_responsable')
]