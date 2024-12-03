# gunicorn.conf.py

# Enlace al que se debe conectar el servidor (puede ser un socket o una dirección IP:puerto)
bind = "0.0.0.0:8000"  # Utiliza un socket UNIX para mayor rendimiento

# Número de procesos trabajadores
workers = 3

# Tiempo máximo de espera para una solicitud (en segundos)
timeout = 30

# Número máximo de solicitudes que un trabajador puede manejar antes de ser reiniciado
max_requests = 1000

# Clase de trabajador (sync, eventlet, gevent, etc.)
worker_class = 'gevent'

# Archivo de registro de acceso
accesslog = '/var/log/gunicorn/access.log'

# Archivo de registro de error
errorlog = '/var/log/gunicorn/error.log'

# Captura las señales SIGTERM y SIGINT para un cierre suave
capture_output = True

# Especifica el formato de los registros
loglevel = 'debug'  # Puedes cambiar a 'info', 'warning', 'error' o 'critical'

# Otras opciones (consulta la documentación para más detalles):
# keepalive = 2
# preload_app = True
# ...

