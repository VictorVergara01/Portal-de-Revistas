from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import subir_imagen_revista, instituciones_unicas
from .views import (
    RevistaListView,
    RevistaDetailView,  
    ArticuloListView,
    ArticuloDetailView,
    AllArticlesView,
    StatsView
)

urlpatterns = [
    path('revistas/', RevistaListView.as_view(), name='lista-revistas'),
    path('revistas/<int:pk>/', RevistaDetailView.as_view(), name='detalle-revista'),  # Ruta para detalles de revista
    path('revistas/<int:fuente_id>/articulos/', ArticuloListView.as_view(), name='lista-articulos'),
    path('articulos/<int:pk>/', ArticuloDetailView.as_view(), name='detalle-articulo'),
    path('revistas/<int:pk>/subir-imagen/', subir_imagen_revista, name='subir-imagen'),
    path('articulos/', AllArticlesView.as_view(), name='lista-todos-articulos'),
    path('instituciones/', instituciones_unicas, name='instituciones-unicas'),
    path('stats/', StatsView.as_view(), name='stats')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
