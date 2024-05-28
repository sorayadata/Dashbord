# Utiliser une image Python officielle comme base
FROM python:3.11.2-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier d'abord le fichier requirements.txt dans le répertoire de travail
COPY requirements.txt .

# Installer les dépendances Python
RUN --mount=type=cache,target=/root/.cache \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        zlib1g-dev libjpeg-dev libpng-dev && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y --auto-remove zlib1g-dev libjpeg-dev libpng-dev

# Copier le reste des fichiers de l'application dans le répertoire de travail
COPY . .

# Spécifier la commande par défaut pour exécuter l'application
CMD ["streamlit", "run", "dashbo.py"]


