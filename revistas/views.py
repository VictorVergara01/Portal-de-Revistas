from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from .models import Revista, Articulo
from .serializers import RevistaSerializer, ArticuloSerializer
from django.contrib import messages
from .forms import RevistaImageUploadForm
from rest_framework.generics import ListAPIView
from django.db.models import Min


class StatsView(APIView):
    """
    Devuelve estadísticas globales del portal: total de revistas, artículos y autores.
    """
    def get(self, request):
        total_revistas = Revista.objects.count()
        total_articulos = Articulo.objects.count()
        total_autores = Articulo.objects.values("creator").distinct().count()

        data = {
            "total_revistas": total_revistas,
            "total_articulos": total_articulos,
            "total_autores": total_autores,
        }
        return Response(data)

def instituciones_unicas(request):
    """
    Devuelve una lista de instituciones únicas (publishers) del portal.
    """
    instituciones = Revista.objects.values_list('publisher', flat=True).distinct()
    instituciones = list(filter(None, instituciones))  # Filtra valores nulos o vacíos
    return JsonResponse(instituciones, safe=False)


class AllArticlesView(ListAPIView):
    """
    Vista para listar todos los artículos, sin importar la fuente.
    """
    queryset = Articulo.objects.all()
    serializer_class = ArticuloSerializer


def subir_imagen_revista(request, pk):
    revista = get_object_or_404(Revista, pk=pk)
    
    if request.method == 'POST':
        form = RevistaImageUploadForm(request.POST, request.FILES, instance=revista)
        if form.is_valid():
            form.save()
            messages.success(request, "Imagen de portada subida exitosamente.")
            return redirect('detalle-revista', pk=pk)  # Redirige a la página de detalles de la revista
        else:
            messages.error(request, "Error al subir la imagen. Por favor, intenta nuevamente.")
    
    else:
        form = RevistaImageUploadForm(instance=revista)

    return render(request, 'revistas/subir_imagen.html', {'form': form, 'revista': revista})


class RevistaListView(generics.ListAPIView):
    """
    Vista para listar todas las revistas.
    """
    queryset = Revista.objects.all()
    serializer_class = RevistaSerializer


class RevistaDetailView(APIView):
    """
    Devuelve los detalles de una revista específica en formato JSON,
    incluyendo información adicional como el total de artículos, autores y año de inicio.
    """
    def get(self, request, pk):
        revista = get_object_or_404(Revista, pk=pk)

        # Obtener datos adicionales
        total_articles = Articulo.objects.filter(fuente=revista).count()
        total_authors = Articulo.objects.filter(fuente=revista).values("creator").distinct().count()
        start_year = Articulo.objects.filter(fuente=revista).aggregate(Min("date_published"))["date_published__min"]

        # Preparar los datos
        data = {
            "id": revista.id,
            "name": revista.name,
            "publisher": revista.publisher,
            "cover_image": revista.cover_image.url if revista.cover_image else None,
            "last_harvest_date": revista.last_harvest_date,
            "description": revista.description,
            "official_url": revista.official_url,
            "total_articles": total_articles,
            "total_authors": total_authors,
            "start_year": start_year.year if start_year else "Desconocido",
        }
        return JsonResponse(data)


class ArticuloListView(generics.ListAPIView):
    """
    Vista para listar artículos asociados a una revista específica.
    """
    serializer_class = ArticuloSerializer

    def get_queryset(self):
        fuente_id = self.kwargs.get('fuente_id')
        return Articulo.objects.filter(fuente_id=fuente_id)


class ArticulosPorRevistaView(APIView):
    """
    Vista para devolver los artículos asociados a una revista específica con un control adicional.
    """
    def get(self, request, fuente_id):
        revista = get_object_or_404(Revista, id=fuente_id)
        articulos = Articulo.objects.filter(fuente=revista)
        serializer = ArticuloSerializer(articulos, many=True)
        return Response(serializer.data)


class ArticuloDetailView(generics.RetrieveAPIView):
    """
    Vista para obtener los detalles de un artículo específico.
    """
    queryset = Articulo.objects.all()
    serializer_class = ArticuloSerializer
