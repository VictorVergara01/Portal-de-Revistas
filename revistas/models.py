from django.db import models
import requests
import xml.etree.ElementTree as ET
from django.utils.timezone import now

import requests
from django.db import models
from xml.etree import ElementTree as ET


class Revista(models.Model):
    base_url = models.URLField(unique=True)  # Base URL para el OAI-PMH
    metadata_prefix = models.CharField(max_length=50, default='oai_dc')  # Prefijo de metadatos utilizado en OAI-PMH
    name = models.CharField(max_length=255, blank=True, null=True)  # Nombre del repositorio/revista
    protocol_version = models.CharField(max_length=10, blank=True, null=True)  # Versión del protocolo
    description = models.TextField(null=True, blank=True)
    official_url = models.URLField(max_length=255, blank=True, null=True)  # URL oficial formateada
    publisher = models.CharField(max_length=255, blank=True, null=True)
    earliest_datestamp = models.CharField(max_length=50, blank=True, null=True)  # Fecha más antigua
    deleted_record_policy = models.CharField(max_length=50, blank=True, null=True)  # Política de eliminación
    granularity = models.CharField(max_length=50, blank=True, null=True)  # Granularidad de fechas
    admin_email = models.EmailField(blank=True, null=True)  # Email del administrador
    last_harvest_date = models.DateTimeField(blank=True, null=True)  # Fecha de la última cosecha
    cover_image = models.ImageField(upload_to='revistas/covers/', null=True, blank=True)

    def fetch_metadata(self):
        """
        Extrae metadatos de la URL OAI-PMH y asigna los campos relevantes.
        """
        try:
            response = requests.get(f"{self.base_url}?verb=Identify")
            response.raise_for_status()

            namespaces = {"oai": "http://www.openarchives.org/OAI/2.0/"}
            root = ET.fromstring(response.text)

            # Extraer metadatos y asignarlos a los campos del modelo
            self.name = root.find(".//oai:repositoryName", namespaces).text
            self.protocol_version = root.find(".//oai:protocolVersion", namespaces).text
            self.earliest_datestamp = root.find(".//oai:earliestDatestamp", namespaces).text
            self.deleted_record_policy = root.find(".//oai:deletedRecord", namespaces).text
            self.granularity = root.find(".//oai:granularity", namespaces).text
            self.admin_email = root.find(".//oai:adminEmail", namespaces).text

            # Formatear official_url
            self.format_official_url()

        except Exception as e:
            raise ValueError(f"Error al extraer los datos de {self.base_url}: {e}")

    def format_official_url(self):
        """
        Formatea la base_url para obtener la official_url eliminando el sufijo '/oai'.
        """
        if self.base_url.endswith('/oai'):
            self.official_url = self.base_url[:-4]  # Eliminar '/oai'
        else:
            self.official_url = self.base_url

    def save(self, *args, **kwargs):
        """
        Sobrescribe el método save para extraer automáticamente los metadatos
        si la revista no tiene nombre y formatear la URL oficial.
        """
        if not self.official_url:
            self.format_official_url()
        if not self.name:
            self.fetch_metadata()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name or self.base_url



class Articulo(models.Model):
    """
    Modelo para representar un artículo científico cosechado.
    """
    title = models.CharField(max_length=500, default="Sin título")  # Limitamos a 500 caracteres
    creator = models.TextField(blank=True, null=True, default="Desconocido")
    subject_es = models.TextField(blank=True, null=True, default="Sin tema")
    subject_en = models.TextField(blank=True, null=True, default="No subject")
    description_es = models.TextField(blank=True, null=True, default="No disponible")
    description_en = models.TextField(blank=True, null=True, default="Not available")
    publisher = models.TextField(blank=True, null=True, default="No especificado")
    date_published = models.DateField(blank=True, null=True)
    identifier = models.CharField(max_length=255, unique=True)  # Identificador único
    language = models.CharField(max_length=10, blank=True, null=True, default="Desconocido")
    source = models.TextField(blank=True, null=True, default="Sin Fuente")
    resource_type = models.TextField(blank=True, null=True, default="No especificado")
    format = models.TextField(blank=True, null=True, default="Sin Formato")
    relation = models.TextField(blank=True, null=True, default="Sin Relación")
    official_link = models.URLField(blank=True, null=True, default="Sin enlace oficial")  # Enlace oficial
    rights = models.TextField(blank=True, null=True, default="Sin derechos especificados")
    fuente = models.ForeignKey(Revista, on_delete=models.CASCADE)
    def __str__(self):
        return self.title
