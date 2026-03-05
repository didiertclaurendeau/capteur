#!/bin/bash
# Script pour démarrer le serveur avec Gunicorn en production
# Pour utilisation derrière Nginx

# Configuration
WORKERS=4  # Nombre de workers (généralement 2-4 x nombre de CPU cores)
BIND_ADDRESS="127.0.0.1:5002"  # Adresse d'écoute
TIMEOUT=300  # Timeout en secondes
APP_MODULE="app:app"  # Module Flask

# Ou utiliser un socket Unix pour de meilleures performances
# BIND_ADDRESS="unix:/tmp/capteur.sock"

echo "Démarrage du serveur Capteur avec Gunicorn"
echo "Workers: $WORKERS"
echo "Bind: $BIND_ADDRESS"
echo ""

# Activer l'environnement virtuel si nécessaire
if [ -d "venv" ]; then
    echo "Activation de l'environnement virtuel..."
    source venv/bin/activate
fi

# Définir la clé secrète depuis l'environnement (IMPORTANT!)
if [ -z "$SECRET_KEY" ]; then
    echo "⚠️  ATTENTION: SECRET_KEY non définie!"
    echo "Définissez-la avec: export SECRET_KEY='votre_cle_tres_secrete'"
    echo "Utilisation de la clé par défaut (NON RECOMMANDÉ EN PRODUCTION)"
fi

# Démarrer Gunicorn
gunicorn \
    --workers $WORKERS \
    --bind $BIND_ADDRESS \
    --timeout $TIMEOUT \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --capture-output \
    --enable-stdio-inheritance \
    $APP_MODULE

# Options supplémentaires utiles:
# --daemon                    # Exécuter en arrière-plan
# --pid /tmp/capteur.pid      # Fichier PID
# --access-logfile /var/log/capteur/access.log
# --error-logfile /var/log/capteur/error.log
# --worker-class gevent       # Utiliser gevent pour async (nécessite: pip install gevent)
# --worker-connections 1000   # Avec gevent
