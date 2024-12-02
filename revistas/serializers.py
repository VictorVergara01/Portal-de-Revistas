# serializers.py
from rest_framework import serializers
from .models import Revista, Articulo

class RevistaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Revista
        fields = '__all__'

class ArticuloSerializer(serializers.ModelSerializer):
    class Meta:
        model = Articulo
        fields = '__all__'
