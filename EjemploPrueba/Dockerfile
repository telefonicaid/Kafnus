FROM python:3.9-slim

WORKDIR /app

# Instala dependencias de sistema necesarias para compilar paquetes
RUN apt-get update && apt-get install -y gcc build-essential

# Copia requerimientos y código
COPY requirements.txt .
COPY stream_processor.py .

# Instala dependencias
RUN pip install --upgrade pip && pip install -r requirements.txt

# Comando que se ejecutará cuando arranque el contenedor
CMD ["faust", "-A", "stream_processor", "worker", "-l", "info"]
