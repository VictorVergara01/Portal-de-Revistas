from django import forms
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, reverse
from django.contrib import messages
from django.utils.html import format_html
from .models import Revista, Articulo
from .utils import cosechar_datos_directo


# Formulario personalizado para el modelo Revista
class RevistaCreateForm(forms.ModelForm):
    class Meta:
        model = Revista
        fields = ['base_url', 'metadata_prefix', 'official_url']  # Incluir official_url para poder editarlo al crear

    def save(self, commit=True):
        """
        Completa los metadatos automáticamente al guardar el formulario.
        """
        instance = super().save(commit=False)
        if not instance.name:
            instance.fetch_metadata()
        if commit:
            instance.save()
        return instance


@admin.register(Revista)
class RevistaAdmin(admin.ModelAdmin):
    list_display = ('acciones', 'cover_image_display', 'name', 'official_url', 'base_url', 'last_harvest_date', 'publisher', 'admin_email')
    search_fields = ('name', 'base_url', 'admin_email', 'official_url')
    list_filter = ('metadata_prefix', 'publisher',)

    def cover_image_display(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover;" />', obj.cover_image.url)
        return "No Image"
    cover_image_display.short_description = "Portada"

    def get_form(self, request, obj=None, **kwargs):
        """
        Usa el formulario personalizado solo al crear una revista (obj=None).
        """
        if obj is None:
            kwargs['form'] = RevistaCreateForm
        return super().get_form(request, obj, **kwargs)

    def get_urls(self):
        """
        Agrega las URLs personalizadas para acciones como cosechar y subir imágenes.
        """
        urls = super().get_urls()
        custom_urls = [
            path('cosechar/<int:pk>/', self.admin_site.admin_view(self.cosechar_revista), name='cosechar-revista'),
            path('<int:pk>/subir-imagen/', self.admin_site.admin_view(self.subir_imagen), name='subir-imagen-revista'),
        ]
        return custom_urls + urls

    def cosechar_revista(self, request, pk):
        """
        Cosecha artículos de una revista usando su base URL y prefijo de metadatos.
        """
        try:
            revista = Revista.objects.get(pk=pk)
            cosechar_datos_directo(revista.base_url, revista.metadata_prefix, revista)
            messages.success(request, f"Datos cosechados exitosamente desde la revista: {revista.name or revista.base_url}")
        except Exception as e:
            messages.error(request, f"Error al cosechar datos: {str(e)}")
        return redirect('admin:revistas_revista_changelist')

    def subir_imagen(self, request, pk):
        """
        Muestra un formulario para subir una imagen de portada para una revista.
        """
        revista = Revista.objects.get(pk=pk)
        if request.method == "POST":
            imagen = request.FILES.get('cover_image')
            if imagen:
                revista.cover_image = imagen
                revista.save()
                messages.success(request, "Imagen subida exitosamente.")
                return redirect('admin:revistas_revista_changelist')
            else:
                messages.error(request, "No se seleccionó ninguna imagen.")
        return redirect(f'{reverse("admin:revistas_revista_change", args=[pk])}')

    def acciones(self, obj):
        """
        Agrega botones de acción para cosechar y subir imágenes de revistas.
        """
        return format_html(
            '<a href="{}" class="button" style="margin-right: 10px;">Cosechar</a>'
            '<a href="{}" class="button">Editar</a>',
            reverse('admin:cosechar-revista', args=[obj.pk]),
            reverse('admin:subir-imagen-revista', args=[obj.pk]),
        )
    acciones.short_description = 'Acciones'


@admin.register(Articulo)
class ArticuloAdmin(admin.ModelAdmin):
    """
    Administración personalizada para la clase Articulo.
    """
    list_display = (
        'title', 
        'creator', 
        'language', 
        'date_published', 
        'identifier', 
        'publisher', 
        'subject_es',  
        'subject_en',  
        'resource_type', 
        'source', 
        'relation', 
        'rights'
    )
    search_fields = ('title', 'creator', 'subject_es', 'subject_en', 'identifier')
    list_filter = ('language', 'date_published', 'fuente')
    ordering = ('-date_published',)
