# backend/Dockerfile
FROM python:3-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Mettre à jour les paquets Debian avant d'installer quoi que ce soit
RUN apt-get update && \
    apt-get upgrade -y && \
    rm -rf /var/lib/apt/lists/*

# Installer vos dépendances Python (sans == dans requirements.txt si vous préférez)
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY app.py .

EXPOSE 5000
CMD ["python", "app.py"]
