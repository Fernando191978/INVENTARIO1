#IMAGEN MADRE
FROM python:3.11-slim

# CONFIGURACION PARA PODER VER LOS LOGS EN TIEMPO REAL
ENV PYTHONUNBUFFERED=1

# Instalar todas las dependencias necesarias para WeasyPrint
# Instalar dependencias del sistema para WeasyPrint
RUN apt-get update && apt-get install -y \
    build-essential \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    libglib-2.0-0 \
    libgobject-2.0-0 \
    gobject-introspection \
    libgirepository1.0-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY ./requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]