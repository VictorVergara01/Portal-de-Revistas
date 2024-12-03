# Usa una imagen base de Python
FROM python:3.11-slim-bullseye

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instala las dependencias del sistema necesarias para MySQL y Python
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    && apt-get clean

# Copia los archivos necesarios al contenedor
COPY requirements.txt requirements.txt

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el proyecto al contenedor
COPY . .

# Recolecta archivos estáticos
RUN python manage.py collectstatic --noinput

# Expone el puerto por defecto que usará la aplicación
EXPOSE 8000

# Comando para iniciar la aplicación
CMD ["gunicorn", "gestor_revistas.wsgi:application", "--bind", "0.0.0.0:8000"]
