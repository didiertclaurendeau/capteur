# Guide de Déploiement - Serveur Capteur derrière Nginx

Ce guide explique comment déployer le serveur Capteur en production derrière Nginx avec support multi-workers et sessions partagées via Redis.

## Architecture

```
Internet → Nginx (Port 80/443)
              ↓
         /capture route
              ↓
    Gunicorn (4+ workers sur port 5002-5005)
              ↓
         Flask App
              ↓
         Redis (Sessions partagées)
```

## Prérequis

- **Serveur Linux** (Ubuntu 20.04+ ou similaire)
- **Python 3.8+**
- **Nginx**
- **Redis** (pour sessions partagées entre workers)
- **Accès sudo** pour l'installation

## Installation Complète

### 1. Préparer le serveur

```bash
# Mise à jour du système
sudo apt update && sudo apt upgrade -y

# Installer les dépendances système
sudo apt install -y python3 python3-venv python3-pip nginx redis-server git

# Vérifier que Redis fonctionne
sudo systemctl status redis
sudo systemctl enable redis
```

### 2. Installer l'application

```bash
# Créer un utilisateur dédié (recommandé)
sudo useradd -r -s /bin/bash -d /opt/capteur capteur

# Créer les dossiers
sudo mkdir -p /opt/capteur
sudo chown capteur:capteur /opt/capteur

# Se placer dans le dossier
cd /opt/capteur

# Cloner ou copier les fichiers du serveur
# git clone <votre-repo> .
# ou copier les fichiers manuellement

# Créer l'environnement virtuel Python
sudo -u capteur python3 -m venv venv

# Activer l'environnement virtuel
sudo -u capteur venv/bin/pip install --upgrade pip

# Installer les dépendances
sudo -u capteur venv/bin/pip install -r server/requirements.txt

# Créer les dossiers nécessaires
sudo -u capteur mkdir -p server/uploads
sudo -u capteur mkdir -p server/thumbnails
sudo -u capteur mkdir -p server/flask_session
sudo -u capteur mkdir -p /var/log/capteur

# Permissions
sudo chown -R capteur:capteur /opt/capteur
sudo chown -R capteur:capteur /var/log/capteur
```

### 3. Configurer les variables d'environnement

```bash
# Générer une clé secrète forte
python3 -c "import secrets; print(secrets.token_hex(32))"

# Créer un fichier d'environnement
sudo nano /opt/capteur/.env
```

Contenu du fichier `.env`:
```bash
SECRET_KEY=votre_cle_secrete_generee_ci_dessus
REDIS_HOST=localhost
REDIS_PORT=6379
FLASK_ENV=production
```

### 4. Configurer Nginx

```bash
# Copier la configuration Nginx
sudo cp server/nginx.conf /etc/nginx/sites-available/capteur

# Éditer la configuration
sudo nano /etc/nginx/sites-available/capteur
```

Modifiez les valeurs suivantes:
- `server_name` : Votre nom de domaine
- Chemins vers les fichiers statiques si nécessaire
- Nombre de workers dans `upstream`

```bash
# Activer le site
sudo ln -s /etc/nginx/sites-available/capteur /etc/nginx/sites-enabled/

# Tester la configuration
sudo nginx -t

# Recharger Nginx
sudo systemctl reload nginx
```

### 5. Configurer le service Systemd

```bash
# Copier le fichier de service
sudo cp server/capteur.service /etc/systemd/system/

# Éditer le service
sudo nano /etc/systemd/system/capteur.service
```

Modifiez:
- `User` et `Group` (ex: `capteur`)
- `WorkingDirectory` : `/opt/capteur/server`
- `Environment="PATH=..."` : `/opt/capteur/venv/bin`
- `ExecStart` : Chemin complet vers gunicorn
- `SECRET_KEY` : Votre clé secrète

Exemple de configuration:
```ini
[Service]
User=capteur
Group=capteur
WorkingDirectory=/opt/capteur/server
Environment="PATH=/opt/capteur/venv/bin"
Environment="SECRET_KEY=votre_cle_secrete"
ExecStart=/opt/capteur/venv/bin/gunicorn \
    --workers 4 \
    --bind 127.0.0.1:5002 \
    --timeout 300 \
    --access-logfile /var/log/capteur/access.log \
    --error-logfile /var/log/capteur/error.log \
    app:app
```

```bash
# Recharger systemd
sudo systemctl daemon-reload

# Activer le service au démarrage
sudo systemctl enable capteur

# Démarrer le service
sudo systemctl start capteur

# Vérifier le statut
sudo systemctl status capteur

# Voir les logs
sudo journalctl -u capteur -f
```

### 6. Configuration du pare-feu

```bash
# Autoriser HTTP et HTTPS
sudo ufw allow 'Nginx Full'

# Ou spécifiquement
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Activer le pare-feu
sudo ufw enable

# Vérifier le statut
sudo ufw status
```

### 7. Configurer SSL avec Let's Encrypt (Recommandé)

```bash
# Installer Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtenir un certificat SSL
sudo certbot --nginx -d votre-domaine.com

# Le certificat se renouvellera automatiquement
# Tester le renouvellement:
sudo certbot renew --dry-run
```

## Configuration du Client

Maintenant que le serveur est déployé sur `/capture`, mettez à jour l'URL du client:

```bash
# Avec HTTP
capteur.exe --text "Session" --url http://votre-domaine.com/capture/upload --id client_01

# Avec HTTPS (recommandé)
capteur.exe --text "Session" --url https://votre-domaine.com/capture/upload --id client_01
```

## Commandes de Gestion

### Gérer le service

```bash
# Démarrer
sudo systemctl start capteur

# Arrêter
sudo systemctl stop capteur

# Redémarrer
sudo systemctl restart capteur

# Recharger la configuration (sans interruption)
sudo systemctl reload capteur

# Voir les logs en temps réel
sudo journalctl -u capteur -f

# Voir les logs avec plus de contexte
sudo journalctl -u capteur -n 100

# Logs d'accès Gunicorn
sudo tail -f /var/log/capteur/access.log

# Logs d'erreur Gunicorn
sudo tail -f /var/log/capteur/error.log
```

### Gérer Nginx

```bash
# Tester la configuration
sudo nginx -t

# Recharger la configuration
sudo systemctl reload nginx

# Redémarrer
sudo systemctl restart nginx

# Voir les logs
sudo tail -f /var/log/nginx/capteur_access.log
sudo tail -f /var/log/nginx/capteur_error.log
```

### Gérer Redis

```bash
# Statut
sudo systemctl status redis

# Redémarrer
sudo systemctl restart redis

# Se connecter au CLI Redis
redis-cli

# Dans le CLI, voir les clés de session:
redis-cli KEYS "capteur:*"

# Voir toutes les clés
redis-cli KEYS "*"

# Vider toutes les sessions
redis-cli FLUSHDB
```

## Tests

### 1. Tester le health check

```bash
curl http://localhost/capture/health
```

Réponse attendue:
```json
{
  "status": "healthy",
  "checks": {
    "uploads_dir": true,
    "thumbnails_dir": true,
    "users_file": true,
    "redis": true
  }
}
```

### 2. Tester l'upload

```bash
# Créer une image de test
convert -size 100x100 xc:blue test.png

# Uploader
curl -X POST \
  -F "image=@test.png" \
  -F "client_id=test_client" \
  -F "monitor_id=0" \
  http://localhost/capture/upload
```

### 3. Tester l'interface web

Ouvrez un navigateur et accédez à:
- `http://votre-domaine.com/capture/`
- Login: `admin` / `admin123`

## Monitoring

### Configuration de base

```bash
# Installer htop pour surveiller les processus
sudo apt install htop

# Surveiller l'utilisation:
htop

# Surveiller Redis
redis-cli INFO
redis-cli MONITOR  # Voir les commandes en temps réel
```

### Logs centralisés (optionnel)

Pour des logs plus professionnels, configurez rsyslog ou utilisez:

```bash
# Installer lnav pour navigation des logs
sudo apt install lnav

# Voir tous les logs de l'application
lnav /var/log/capteur/*.log
```

## Sauvegarde

### Script de sauvegarde

```bash
#!/bin/bash
# /opt/capteur/backup.sh

BACKUP_DIR="/backups/capteur"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Sauvegarder les uploads
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz -C /opt/capteur/server uploads/

# Sauvegarder les utilisateurs
cp /opt/capteur/server/users.json $BACKUP_DIR/users_$DATE.json

# Sauvegarder les métadonnées
cp /opt/capteur/server/metadata.json $BACKUP_DIR/metadata_$DATE.json

# Garder seulement les 7 derniers jours
find $BACKUP_DIR -name "uploads_*.tar.gz" -mtime +7 -delete
find $BACKUP_DIR -name "users_*.json" -mtime +7 -delete
find $BACKUP_DIR -name "metadata_*.json" -mtime +7 -delete

echo "Sauvegarde terminée: $DATE"
```

```bash
# Rendre exécutable
chmod +x /opt/capteur/backup.sh

# Ajouter au crontab (tous les jours à 2h du matin)
sudo crontab -e
```

Ajoutez:
```
0 2 * * * /opt/capteur/backup.sh >> /var/log/capteur/backup.log 2>&1
```

## Dépannage

### Le service ne démarre pas

```bash
# Vérifier les logs
sudo journalctl -u capteur -n 50

# Vérifier les permissions
ls -la /opt/capteur/server/

# Tester manuellement
cd /opt/capteur/server
source ../venv/bin/activate
python app.py
```

### Erreurs de connexion Redis

```bash
# Vérifier que Redis fonctionne
sudo systemctl status redis

# Tester la connexion
redis-cli ping
# Doit retourner: PONG

# Redémarrer Redis
sudo systemctl restart redis
```

### Erreurs 502 Bad Gateway

```bash
# Vérifier que Gunicorn fonctionne
sudo systemctl status capteur

# Vérifier les logs Nginx
sudo tail -f /var/log/nginx/error.log

# Vérifier les workers
ps aux | grep gunicorn
```

### Sessions ne fonctionnent pas

```bash
# Vérifier la configuration des cookies
# Les cookies doivent être sur le bon domaine et path

# Vérifier Redis
redis-cli KEYS "capteur:*"

# Si vide, vérifier la configuration Flask-Session
```

### Performances lentes

```bash
# Augmenter le nombre de workers
# Éditer /etc/systemd/system/capteur.service
# Changer --workers 4 à --workers 8 (ou plus)

# Redémarrer
sudo systemctl daemon-reload
sudo systemctl restart capteur
```

## Optimisations pour Production

### 1. Compression Nginx

Ajoutez dans votre configuration Nginx:

```nginx
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
```

### 2. Cache des fichiers statiques

Les thumbnails sont déjà configurés avec cache dans `nginx.conf`.

### 3. Rate limiting

Protégez l'endpoint d'upload:

```nginx
limit_req_zone $binary_remote_addr zone=upload:10m rate=10r/m;

location /capture/upload {
    limit_req zone=upload burst=5;
    # ... reste de la config
}
```

### 4. Redis persistance

Éditez `/etc/redis/redis.conf`:

```
save 900 1
save 300 10
save 60 10000
```

Redémarrez Redis:
```bash
sudo systemctl restart redis
```

## Mise à jour de l'application

```bash
# Arrêter le service
sudo systemctl stop capteur

# Faire une sauvegarde
/opt/capteur/backup.sh

# Mettre à jour le code
cd /opt/capteur
git pull  # ou copier les nouveaux fichiers

# Mettre à jour les dépendances si nécessaire
sudo -u capteur venv/bin/pip install -r server/requirements.txt

# Redémarrer
sudo systemctl start capteur

# Vérifier
sudo systemctl status capteur
```

## Sécurité

### Checklist de sécurité

- [ ] Clé secrète forte et unique (SECRET_KEY)
- [ ] Utilisateur par défaut changé
- [ ] HTTPS activé (Let's Encrypt)
- [ ] Pare-feu configuré (UFW)
- [ ] Redis protégé (bind 127.0.0.1)
- [ ] Permissions fichiers correctes
- [ ] Logs rotatifs configurés
- [ ] Sauvegardes automatiques
- [ ] Rate limiting activé
- [ ] Fail2ban installé (optionnel)

### Fail2ban (optionnel)

```bash
sudo apt install fail2ban

# Créer un filtre pour Capteur
sudo nano /etc/fail2ban/filter.d/capteur.conf
```

Contenu:
```ini
[Definition]
failregex = ^.*"POST /capture/login.*" 401.*$
ignoreregex =
```

```bash
# Créer une jail
sudo nano /etc/fail2ban/jail.local
```

Contenu:
```ini
[capteur]
enabled = true
port = http,https
filter = capteur
logpath = /var/log/capteur/access.log
maxretry = 5
bantime = 3600
```

```bash
# Redémarrer Fail2ban
sudo systemctl restart fail2ban
```

## Support

Pour des questions ou des problèmes:
1. Vérifiez les logs
2. Consultez la documentation
3. Ouvrez une issue sur le dépôt GitHub
