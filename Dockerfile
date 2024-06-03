# Utiliser une image Python 3.10
FROM python:3.10-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le contenu actuel du répertoire dans le conteneur
COPY . /app

# Installer les paquets nécessaires spécifiés dans requirements.txt
RUN apt-get update && apt-get install -y build-essential \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get remove -y build-essential \
    && apt-get autoremove -y \
    && apt-get clean

# Rendre le port 5000 accessible à l'extérieur du conteneur
EXPOSE 5000

# Définir les variables d'environnement
ENV FLASK_APP=run.py
ENV FLASK_RUN_HOST=0.0.0.0

# Lancer l'application Flask
CMD ["flask", "run"]
