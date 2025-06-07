FROM python:3-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Dépendances système nécessaires à faiss + sentence-transformers
RUN apt-get update && \
    apt-get install -y build-essential libglib2.0-0 libsm6 libxrender1 libxext6 && \
    rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copier tous les fichiers nécessaires
COPY . .

# ⚠️ Exécuter l’indexation au build (FAISS index + pickle)
RUN python ingest_pdfs.py

EXPOSE 5000
CMD ["python", "app.py"]
