# Implementación del Cosechador de Revistas Científicas

Este proyecto implementa un cosechador de revistas científicas utilizando el protocolo OAI-PMH, basado en Django. Sigue las instrucciones a continuación para instalar, configurar y ejecutar el proyecto en un entorno Linux.

---

## Requisitos previos

Antes de comenzar, asegúrate de tener instalado lo siguiente:

- **Ubuntu o una distribución Linux compatible**
- **Acceso root o permisos sudo**
- **Git**
- **MySQL Server**

---

## Instalación y configuración

### 1. Actualizar el sistema
```bash
sudo apt update && sudo apt upgrade
```

### 2. Instalar herramientas esenciales
```bash
sudo apt install git
sudo apt install net-tools
sudo apt install ufw
sudo apt install pkg-config
sudo apt install build-essential default-libmysqlclient-dev
```

### 3. Clonar el repositorio
```bash
git clone https://github.com/VictorVergara01/Portal-de-Revistas.git
cd Portal-de-Revistas
```

### 4. Instalar Python 3.12
```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.12
python3.12 --version  # Verificar la instalación
```

### 5. Configurar el entorno virtual
```bash
sudo apt install python3.12-venv
python3.12 -m venv env
source env/bin/activate
```

### 6. Instalar dependencias del proyecto
```bash
pip install -r requirements.txt
```

### 7. Instalar MySQL Server
```bash
sudo apt install mysql-server
sudo mysql_secure_installation
```

### 8. Configurar la base de datos
Accede a MySQL:
```bash
sudo mysql -u root -p
```

Ejecuta los siguientes comandos para crear la base de datos y el usuario:
```sql
CREATE DATABASE revistas_db;
CREATE USER 'revista'@'localhost' IDENTIFIED BY '123qweASD';
GRANT ALL PRIVILEGES ON revistas_db.* TO 'revista'@'localhost';
FLUSH PRIVILEGES;
exit
```

### 9. Realizar las migraciones de la base de datos
```bash
python manage.py makemigrations
python manage.py migrate
```

### 10. Crear un usuario administrador
```bash
python manage.py createsuperuser
```

### 11. Recopilar archivos estáticos
```bash
python manage.py collectstatic
```

### 12. Ejecutar el servidor de desarrollo
```bash
python manage.py runserver
```

---

## Configuración para producción

### 1. Instalar Gunicorn
Gunicorn es un servidor WSGI para aplicaciones Python, ideal para entornos de producción:
```bash
pip install gunicorn
```

### 2. Ejecutar Gunicorn
```bash
gunicorn gestor_revistas.wsgi:application
```

O usando un archivo de configuración:
```bash
gunicorn -c gunicorn.conf.py gestor_revistas.wsgi:application
```

---

## Notas adicionales

- Asegúrate de configurar el firewall (UFW) para permitir el tráfico necesario:
  ```bash
  sudo ufw allow 8000  # Puerto por defecto para Django
  sudo ufw allow 80    # Puerto HTTP
  sudo ufw enable
  ```

- Configura un servidor web como **Nginx** para servir la aplicación en producción.

---

## Contribuir

Si deseas contribuir a este proyecto, realiza un fork del repositorio y crea un pull request con tus cambios.

---

## Licencia

Este proyecto está licenciado bajo la [Licencia MIT](LICENSE).
