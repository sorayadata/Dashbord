# Utiliser une image Python officielle comme base
FROM python:3.11-slim

# Installer les dépendances de Pillow
RUN apt-get update && \
    apt-get install -y zlib1g-dev libjpeg-dev libpng-dev && \
    rm -rf /var/lib/apt/lists/*

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le fichier requirements.txt dans le répertoire de travail
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste des fichiers de l'application dans le répertoire de travail
COPY . .

# Spécifier la commande par défaut pour exécuter l'application
CMD ["streamlit", "run", "dashbo.py"]


