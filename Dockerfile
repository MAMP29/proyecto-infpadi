# Usa una imagen base de Python oficial, que es muy ligera.
FROM python:3.11-slim

WORKDIR /app

# Instala dependencias
COPY requirements-cpu.txt .
RUN pip install --no-cache-dir -r requirements-cpu.txt

# Copia el código
COPY ./modelo/ /app/backend/

# Expone puertos
EXPOSE 8000

# Este CMD es importante para que Docker Compose pueda desplegar el servicio
CMD ["python3", "backend/main.py", "--num-gpus", "2", "--force"]