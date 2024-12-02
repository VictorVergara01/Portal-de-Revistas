from django import forms
from .models import Revista

class RevistaImageUploadForm(forms.ModelForm):
    class Meta:
        model = Revista
        fields = ['cover_image']  # Solo el campo de la imagen
