# Utiliser une image de base officielle de Python
FROM python:3.12

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de l'application
COPY . /app

# Installer les dépendances
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Exposer le port de l'application
EXPOSE 8000

# Définir la commande par défaut
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]