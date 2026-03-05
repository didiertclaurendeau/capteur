#!/bin/bash
# Script pour démarrer le serveur Flask

echo "Démarrage du serveur Flask..."
echo ""

# Vérifier si venv existe
if [ -d "venv" ]; then
    echo "Activation de l'environnement virtuel..."
    source venv/bin/activate
else
    echo "ATTENTION: Environnement virtuel non trouvé."
    echo "Utilisation de Python global."
    echo ""
fi

echo "Démarrage du serveur sur http://localhost:5000"
echo "Appuyez sur Ctrl+C pour arrêter le serveur"
echo ""
echo "Identifiants par défaut:"
echo "  Username: admin"
echo "  Password: admin123"
echo ""
echo "========================================"
echo ""

python3 app.py
