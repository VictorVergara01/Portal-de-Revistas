# Usa una imagen base de Python
FROM python:3.11-slim-bullseye

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instala las dependencias del sistema necesarias para MySQL, Python y pkg-config
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    --no-install-recommends && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copia el archivo requirements.txt al contenedor
COPY requirements.txt /app/requirements.txt

# Actualiza pip y luego instala las dependencias de Python
RUN python -m pip install --upgrade pip && pip install --no-cache-dir -r /app/requirements.txt

# Copia todo el proyecto al contenedor
COPY . /app

# Recolecta archivos estáticos (sin detener el despliegue en caso de fallo)
RUN python manage.py collectstatic --noinput || echo "Static collection skipped"

# Expone el puerto por defecto que usará la aplicación
EXPOSE 8000

# Comando para iniciar la aplicación
CMD ["gunicorn", "gestor_revistas.wsgi:application", "--bind", "0.0.0.0:8000"]
