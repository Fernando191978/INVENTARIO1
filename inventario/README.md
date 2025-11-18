# Sistema de Gestión de Inventario

Este proyecto es un **sistema de gestión de inventario** desarrollado en **Django 5.2.7**, que permite gestionar productos, clientes y ventas, con autenticación de usuarios y funcionalidades avanzadas como generación de PDFs y gráficos de ventas.  

---

## Aplicaciones (Apps)

### 1. **Clientes**
- Gestión completa de clientes.
- Funcionalidades:
  - Crear clientes.
  - Editar clientes.
  - Eliminar clientes.
  - Listar clientes.  

### 2. **Productos**
- Administración de inventario y stock.
- Funcionalidades:
  - Crear productos con código SKU y fotos.
  - Editar productos.
  - Eliminar productos.
  - Agregar o restar stock según necesidad.
  - Listar productos.  

### 3. **Ventas**
- Gestión de ventas y facturación.
- Funcionalidades:
  - Crear ventas.
  - Editar ventas.
  - Eliminar ventas.
  - Listar ventas.
  - **Detalle de venta en PDF**.
  - **Gráfico de ventas diarias** en la lista de ventas.  

### 4. **Accounts**
- Manejo de autenticación y usuarios.
- Funcionalidades:
  - Registro y login de usuarios.
  - Gestión de permisos y roles.  

---

## Requisitos (requirements.txt)

```txt
asgiref==3.10.0
beautifulsoup4==4.14.2
brotli==1.2.0
cffi==2.0.0
crispy-bootstrap4==2025.6
cssselect2==0.8.0
Django==5.2.7
django-allauth==65.13.0
django-bootstrap4==25.2
django-crispy-forms==2.4
django-ranged-response==0.2.0
fonttools==4.60.1
pillow==12.0.0
pycparser==2.23
pydyf==0.11.0
pyphen==0.17.2
soupsieve==2.8
sqlparse==0.5.3
tinycss2==1.4.0
tinyhtml5==2.0.0
typing_extensions==4.15.0
weasyprint==66.0
webencodings==0.5.1
django-filter==23.2

##Instalación local
##Clonar el repositorio:

#bash
#Copiar código
git clone https://github.com/Fernando191978/INVENTARIO1.git
cd INVENTARIO
Crear y activar entorno virtual:

#bash
#Copiar código
python -m venv env
source env/bin/activate   # Linux / Mac
env\Scripts\activate      # Windows
Instalar dependencias:

#bash
#Copiar código
pip install -r requirements.txt
Aplicar migraciones:

#bash
#Copiar código
python manage.py migrate
Crear superusuario:

#bash
#Copiar código
python manage.py createsuperuser
Ejecutar servidor:

#bash
#Copiar código
python manage.py runserver
Dockerización

##Este proyecto incluye Docker para levantar la aplicación y la base de datos fácilmente.

Dockerfile
dockerfile
#Copiar código
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
docker-compose.yml
yaml
Copiar código
version: "3.9"

services:
  web:
    build: .
    container_name: inventario_web
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      - DEBUG=1

  db:
    image: postgres:15
    container_name: inventario_db
    environment:
      POSTGRES_USER: inventario
      POSTGRES_PASSWORD: 1234
      POSTGRES_DB: inventario_db
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
##Configuración de base de datos en Django
#python
#Copiar código

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'inventario_db',
        'USER': 'inventario',
        'PASSWORD': 'inventario123',
        'HOST': 'db',
        'PORT': 5432,
    }
}
Levantar el proyecto con Docker
bash
Copiar código
docker-compose up --build
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
Acceder a la app en: http://localhost:8000/

##Estructura de carpetas
#bash
#Copiar código

INVENTARIO/
│
├── clientes/           # App Clientes
├── productos/          # App Productos
├── ventas/             # App Ventas
├── accounts/           # App de autenticación
├── static/             # Archivos estáticos
│   └── logo.png        # Logo del proyecto
├── templates/          # Plantillas HTML
├── env/                # Entorno virtual (no subir a git)
├── manage.py
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
##imagenes de git

##Tecnologías

Python 3.12+

Django 5.2.7

Bootstrap 5

WeasyPrint (para PDFs)

Chart.js (para gráficos de ventas)

PostgreSQL

Docker y Docker Compose

##Autor
Fernando Andrés Pintos