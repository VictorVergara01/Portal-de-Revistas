# Usa una imagen base de Python
FROM python:3.11-slim-bullseye

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instala las dependencias del sistema necesarias para Python, MySQL, y Nginx
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    nginx \
    --no-install-recommends && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copia el archivo requirements.txt al contenedor
COPY requirements.txt /app/requirements.txt

# Actualiza pip e instala las dependencias de Python
RUN python -m pip install --upgrade pip && pip install --no-cache-dir -r /app/requirements.txt

# Copia el código fuente al contenedor
COPY . /app

# Ejecuta collectstatic para recolectar los archivos estáticos
RUN python manage.py collectstatic --noinput

RUN chmod -R 755 /app/static

# Copia la configuración de Nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Expone los puertos necesarios
EXPOSE 80

# Comando para iniciar Nginx y Gunicorn
# Copia el script para crear el superusuario
COPY create_superuser.py /app/create_superuser.py

# Comando para iniciar el servidor y crear el superusuario
CMD ["sh", "-c", "python manage.py migrate && python manage.py shell < create_superuser.py && nginx && gunicorn -c gunicorn.conf.py gestor_revistas.wsgi:application"]