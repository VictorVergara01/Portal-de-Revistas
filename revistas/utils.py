import requests
import xml.etree.ElementTree as ET
from .models import Articulo, Revista
import unicodedata
from django.utils.timezone import now
from .models import Revista, Articulo


def transfer_publisher_to_revista():
    revistas = Revista.objects.all()

    for revista in revistas:
        # Obtener el primer artículo de la revista que tenga un publisher
        articulo = Articulo.objects.filter(fuente=revista).exclude(publisher__isnull=True).first()
        if articulo and articulo.publisher:
            # Actualizar el campo publisher en la revista
            revista.publisher = articulo.publisher
            revista.save()
            print(f"Actualizado publisher de la revista {revista.name} a {articulo.publisher}")


def limpiar_texto(texto, max_length=None):
    """
    Limpia caracteres especiales no válidos (como emojis) para evitar errores al guardar en MySQL.
    """
    if texto:
        texto_limpio = ''.join(c for c in texto if unicodedata.category(c) != 'Cs')  # Elimina caracteres no válidos
        if max_length and len(texto_limpio) > max_length:
            return texto_limpio[:max_length]
        return texto_limpio
    return "No disponible"


def generar_link_oficial(identifier, relation_elements):
    """
    Genera o valida un link oficial para el artículo.
    """
    # Prioriza los valores en relation_elements si existen
    if relation_elements:
        for rel in relation_elements:
            if "http" in rel.text:  # Asegura que el texto sea un enlace válido
                # Procesa el enlace para mantener el formato deseado
                if "/article/view/" in rel.text:
                    parts = rel.text.split("/article/view/")
                    if len(parts) > 1:
                        return f"{parts[0]}/article/view/{parts[1].split('/')[0]}"  # Elimina cualquier segmento adicional

    # Genera un enlace básico basado en el identifier si no hay relación disponible
    if identifier.startswith("oai:"):
        parts = identifier.split(":")
        if len(parts) > 2:
            return f"https://{parts[1]}/article/view/{parts[-1]}"

    return "Sin enlace oficial"

def cosechar_datos_directo(url, metadata_prefix, fuente):
    """
    Descarga y almacena todos los artículos desde un servidor OAI-PMH y actualiza el publisher de la revista.
    """
    print(f"Iniciando la cosecha desde: {url} con prefijo: {metadata_prefix}")
    base_url = f"{url}?verb=ListRecords"
    next_token = None

    while True:
        if next_token:
            request_url = f"{base_url}&resumptionToken={next_token}"
        else:
            request_url = f"{base_url}&metadataPrefix={metadata_prefix}"

        print(f"Realizando solicitud a: {request_url}")
        response = requests.get(request_url)

        if response.status_code != 200:
            raise Exception(f"Error al conectar con {url}. Código de estado: {response.status_code}")

        print(f"Respuesta XML recibida:\n{response.text[:500]}... [truncado]")

        try:
            registros, next_token = procesar_respuesta(response.text)
        except Exception as e:
            print(f"Error al procesar la respuesta: {e}")
            break

        print(f"Registros cosechados en este lote: {len(registros)}")

        for registro in registros:
            official_link = generar_link_oficial(registro['identifier'], registro.get('relation_elements', []))

            # Actualizar o crear el artículo
            articulo, created = Articulo.objects.update_or_create(
                identifier=registro['identifier'],
                defaults={
                    "title": limpiar_texto(registro['title'], max_length=500),
                    "creator": registro['creator'],
                    "subject_es": registro['subject_es'],
                    "subject_en": registro['subject_en'],
                    "description_es": registro['description_es'],
                    "description_en": registro['description_en'],
                    "publisher": registro['publisher'],
                    "date_published": registro['date_published'],
                    "resource_type": registro['resource_type'],
                    "format": registro['format'],
                    "source": registro['source'],
                    "language": registro['language'],
                    "relation": "; ".join([rel.text for rel in registro.get('relation_elements', []) if rel.text]),
                    "official_link": official_link,
                    "rights": registro['rights'],
                    "fuente": fuente,
                }
            )
            print(f"Artículo {'creado' if created else 'actualizado'}: {registro['title']}")

            # Si el artículo tiene un publisher y la revista no lo tiene, actualizar la revista
            if articulo.publisher and not fuente.publisher:
                fuente.publisher = articulo.publisher
                fuente.save()
                print(f"Publisher de la revista '{fuente.name}' actualizado a '{articulo.publisher}'.")

        if not next_token:
            print("No hay más registros para cosechar.")
            break

    fuente.last_harvest_date = now()
    fuente.save()

    print("Cosecha completada.")


def procesar_respuesta(xml_response):
    """
    Procesa la respuesta XML y devuelve los registros en un formato limpio.
    """
    registros = []
    namespaces = {
        "oai": "http://www.openarchives.org/OAI/2.0/",
        "dc": "http://purl.org/dc/elements/1.1/",
        "xml": "http://www.w3.org/XML/1998/namespace"
    }
    root = ET.fromstring(xml_response)

    for record in root.findall(".//oai:record", namespaces):
        identifier_element = record.find(".//oai:header/oai:identifier", namespaces)
        metadata = record.find(".//oai:metadata", namespaces)

        if identifier_element is None or metadata is None:
            print("Registro inválido encontrado. Saltando...")
            continue

        identifier = identifier_element.text

        title = metadata.find(".//dc:title[@xml:lang='es-ES']", namespaces)
        creator = metadata.find(".//dc:creator", namespaces)
        subject_es = metadata.find(".//dc:subject[@xml:lang='es-ES']", namespaces)
        subject_en = metadata.find(".//dc:subject[@xml:lang='en-US']", namespaces)
        description_es = metadata.find(".//dc:description[@xml:lang='es-ES']", namespaces)
        description_en = metadata.find(".//dc:description[@xml:lang='en-US']", namespaces)
        publisher = metadata.find(".//dc:publisher[@xml:lang='es-ES']", namespaces)
        date_published = metadata.find(".//dc:date", namespaces)
        resource_type = metadata.find(".//dc:type", namespaces)
        format_element = metadata.findall(".//dc:format", namespaces)
        source = metadata.findall(".//dc:source", namespaces)
        language = metadata.find(".//dc:language", namespaces)
        relation_elements = metadata.findall(".//dc:relation", namespaces)
        rights = metadata.find(".//dc:rights[@xml:lang='es-ES']", namespaces)

        registros.append({
            "identifier": identifier,
            "title": title.text if title is not None else "Sin título",
            "creator": creator.text if creator is not None else "Desconocido",
            "subject_es": subject_es.text if subject_es is not None else "Sin tema",
            "subject_en": subject_en.text if subject_en is not None else "No subject",
            "description_es": description_es.text if description_es is not None else "No disponible",
            "description_en": description_en.text if description_en is not None else "Not available",
            "publisher": publisher.text if publisher is not None else "No especificado",
            "date_published": date_published.text if date_published is not None else None,
            "resource_type": resource_type.text if resource_type is not None else "No especificado",
            "format": "; ".join([fmt.text for fmt in format_element if fmt.text]) or "Sin Formato",
            "source": "; ".join([src.text for src in source if src.text]) or "Sin Fuente",
            "language": language.text if language is not None else "Desconocido",
            "relation_elements": relation_elements,
            "rights": rights.text if rights is not None else "Sin derechos especificados",
        })

    next_token = root.find(".//oai:resumptionToken", namespaces)
    next_token = next_token.text if next_token is not None else None

    return registros, next_token
