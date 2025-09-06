from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static
from api.views import landing_page, reportes_view, login_view, logout_view, dashboard_principal, mapa_mascotas, api_mascotas_georef

urlpatterns = [
    # Landing page en la raíz
    path('', landing_page, name='landing'),
    path('reportes/', reportes_view, name='reportes'),
    
    # Mapa de mascotas
    path('mapa/', mapa_mascotas, name='mapa_mascotas'),
    path('api/mascotas-georef/', api_mascotas_georef, name='api_mascotas_georef'),
    
    # Autenticación y Dashboard
    path('dashboard/', dashboard_principal, name='dashboard_principal'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    
    # Admin y APIs
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include('api.urls')),

    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
