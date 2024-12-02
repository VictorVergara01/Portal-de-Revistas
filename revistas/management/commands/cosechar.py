from django.core.management.base import BaseCommand
from revistas.utils import cosechar_datos_directo

class Command(BaseCommand):
    help = "Cosecha datos desde un enlace OAI-PMH y guarda los registros en la base de datos."

    def add_arguments(self, parser):
        parser.add_argument(
            '--url',
            type=str,
            help='URL del servidor OAI-PMH',
            required=True
        )
        parser.add_argument(
            '--metadata_prefix',
            type=str,
            help='Prefijo de metadatos (por defecto: oai_dc)',
            default='oai_dc'
        )

    def handle(self, *args, **kwargs):
        url = kwargs['url']
        metadata_prefix = kwargs['metadata_prefix']

        self.stdout.write(f"Iniciando cosecha desde: {url} con prefijo: {metadata_prefix}")
        cosechar_datos_directo(url, metadata_prefix)
        self.stdout.write(self.style.SUCCESS("Cosecha completada."))
