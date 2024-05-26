# Spécifier l'image de base
FROM python:3.11-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le fichier requirements.txt dans le répertoire de travail
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste des fichiers de l'application dans le répertoire de travail
COPY . .

# Spécifier la commande par défaut pour exécuter l'application
CMD ["streamlit", "run", "dashboard.py"]


