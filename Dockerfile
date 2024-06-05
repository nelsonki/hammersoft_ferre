# Define la imagen base utilizando la versión de Python que necesitas
FROM python:3.9

# Configura las variables de entorno utilizadas por el contenedor
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Instala las dependencias del proyecto Django
# Copia el archivo 'requirements.txt' y ejecuta pip install sobre él
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copia el proyecto Django en el directorio de trabajo del contenedor
COPY . /app/

# Abre el puerto por el cual el contenedor aceptará conexiones
EXPOSE 8000

# Ejecuta el servidor Gunicorn para el proyecto Django
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app.wsgi:application"]