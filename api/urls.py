from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    # APIs REST
    path('planillas/', views.mis_planillas),
    path('planillas/<int:pk>/mascotas/', views.mascotas_planilla),
    
    # Nuevas APIs para Responsables y Mascotas
    path('responsables/', views.ResponsableViewSet.as_view()),
    path('planillas/<int:planilla_id>/responsables/', views.ResponsableViewSet.as_view()),
    path('responsables/<int:responsable_id>/mascotas/', views.MascotaViewSet.as_view()),
]