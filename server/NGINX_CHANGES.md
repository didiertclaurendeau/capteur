# Configuration Nginx - Résumé des Modifications

Ce document résume les modifications apportées pour permettre au serveur Flask de fonctionner correctement derrière Nginx sur la route `/capture` avec sessions partagées entre workers.

## Modifications du Code

### 1. Configuration Flask pour Nginx (`server/app.py`)

#### Préfixe d'URL
```python
app.config['APPLICATION_ROOT'] = '/capture'
```
Toutes les routes de l'application sont maintenant préfixées par `/capture`.

#### ProxyFix
```python
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
```
Gère correctement les en-têtes HTTP de Nginx (X-Forwarded-*).

#### Configuration des Sessions
```python
# Sessions via Redis (partagées entre workers)
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis_client
app.config['SESSION_COOKIE_PATH'] = '/capture'
```

#### Health Check
Nouveau endpoint: `/capture/health`
```python
@app.route('/health')
def health():
    # Vérifie l'état de l'application
    return {'status': 'healthy', 'checks': {...}}, 200
```

### 2. Nouvelles Dépendances (`server/requirements.txt`)

```
Flask-Session==0.6.0   # Pour sessions partagées
redis==5.0.1           # Client Redis
gunicorn==21.2.0       # Serveur WSGI pour production
```

## Nouveaux Fichiers

### Configuration et Documentation

1. **`server/nginx.conf`**
   - Configuration Nginx complète
   - Upstream avec plusieurs workers
   - En-têtes proxy configurés
   - Support HTTP/HTTPS
   - Rate limiting
   - Cache des fichiers statiques

2. **`server/DEPLOYMENT.md`**
   - Guide complet de déploiement
   - Installation pas à pas
   - Configuration systemd
   - Sécurité et optimisations
   - Dépannage

3. **`server/REDIS_INSTALL.md`**
   - Installation Redis sur Windows/Linux/macOS
   - Configuration de base
   - Tests de connexion
   - Surveillance

### Scripts de Démarrage

4. **`server/start_gunicorn.sh`**
   - Démarre l'application avec Gunicorn
   - Multiple workers
   - Logging configuré

5. **`server/capteur.service`**
   - Service systemd pour Linux
   - Démarrage automatique
   - Redémarrage en cas d'échec

### Utilitaires

6. **`server/test_config.py`**
   - Teste la configuration complète
   - Vérifie les dépendances
   - Teste Redis
   - Vérifie les dossiers

7. **`server/generate_secret_key.py`**
   - Génère une clé secrète forte
   - Pour SECRET_KEY

8. **`server/.env.example`**
   - Template de variables d'environnement
   - SECRET_KEY, Redis, etc.

## Architecture de Déploiement

```
┌─────────────┐
│   Client    │ (capteur.exe)
└──────┬──────┘
       │ HTTPS
       ▼
┌─────────────────────┐
│   Nginx (Port 80)   │
│   Route: /capture   │
└──────────┬──────────┘
           │ Proxy Pass
           ▼
┌────────────────────────────┐
│ Gunicorn (4 workers)       │
│ Ports: 5002-5005           │
└──────────┬─────────────────┘
           │
    ┌──────┴──────┐
    ▼             ▼
┌────────┐   ┌──────────┐
│ Flask  │   │  Redis   │
│  App   │──▶│ Sessions │
└────────┘   └──────────┘
```

## URLs Mises à Jour

### Avant (Développement)
```
http://localhost:5002/
http://localhost:5002/login
http://localhost:5002/upload
http://localhost:5002/thumbnail/<file>
```

### Après (Production avec Nginx)
```
https://domaine.com/capture/
https://domaine.com/capture/login
https://domaine.com/capture/upload
https://domaine.com/capture/thumbnail/<file>
```

## Configuration Client

### Avant
```bash
capteur.exe --text "Session" --url http://localhost:5002/upload
```

### Après (avec Nginx)
```bash
capteur.exe --text "Session" --url https://domaine.com/capture/upload
```

## Sessions Partagées

### Problème Résolu
Sans Redis, avec plusieurs workers Gunicorn, chaque worker a sa propre session en mémoire.
Un utilisateur authentifié sur le worker #1 ne sera pas reconnu par le worker #2.

### Solution
Redis centralise toutes les sessions. Tous les workers partagent le même store Redis.

```python
# Configuration automatique avec fallback
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    redis_client.ping()
    app.config['SESSION_TYPE'] = 'redis'  # ✓ Sessions partagées
except:
    app.config['SESSION_TYPE'] = 'filesystem'  # ⚠ Fallback (1 worker only)
```

## Sécurité

### Améliorations
- ✅ Clé secrète via variable d'environnement
- ✅ Cookies sécurisés avec path `/capture`
- ✅ HTTPS recommandé (Let's Encrypt)
- ✅ Rate limiting dans Nginx
- ✅ Fail2ban (optionnel)

### Checklist de Production
- [ ] SECRET_KEY unique et forte (64+ caractères)
- [ ] Mot de passe admin changé
- [ ] Redis protégé (bind 127.0.0.1)
- [ ] HTTPS activé avec certificat valide
- [ ] Pare-feu configuré (UFW)
- [ ] Logs rotatifs configurés
- [ ] Monitoring actif (health check)

## Tests

### Test de Configuration
```bash
cd server
python test_config.py
```

### Test de Health Check
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

### Test d'Upload
```bash
curl -X POST \
  -F "image=@test.png" \
  -F "client_id=test" \
  -F "monitor_id=0" \
  http://localhost/capture/upload
```

## Monitoring

### Logs à Surveiller

1. **Nginx**
   - `/var/log/nginx/capteur_access.log`
   - `/var/log/nginx/capteur_error.log`

2. **Gunicorn**
   - `/var/log/capteur/access.log`
   - `/var/log/capteur/error.log`

3. **Systemd**
   - `journalctl -u capteur -f`

4. **Redis**
   - `redis-cli INFO`
   - `redis-cli MONITOR`

### Commandes Utiles

```bash
# Statut du service
sudo systemctl status capteur

# Logs en temps réel
sudo tail -f /var/log/capteur/access.log

# Sessions Redis actives
redis-cli KEYS "capteur:*"

# Nombre de workers actifs
ps aux | grep gunicorn | wc -l

# Test de charge
ab -n 1000 -c 10 http://localhost/capture/health
```

## Rollback

Pour revenir à la configuration simple (développement):

```bash
# Arrêter les services
sudo systemctl stop capteur
sudo systemctl stop nginx

# Démarrer en mode dev
cd server
source venv/bin/activate
python app.py
```

L'application fonctionnera sur `http://localhost:5002` sans préfixe `/capture`.

## Support

- **Documentation complète**: [server/DEPLOYMENT.md](server/DEPLOYMENT.md)
- **Installation Redis**: [server/REDIS_INSTALL.md](server/REDIS_INSTALL.md)
- **Configuration Nginx**: [server/nginx.conf](server/nginx.conf)
- **Tests**: `python server/test_config.py`

## Prochaines Étapes

1. Installer Redis: voir [REDIS_INSTALL.md](server/REDIS_INSTALL.md)
2. Configurer Nginx: copier [nginx.conf](server/nginx.conf)
3. Déployer avec systemd: voir [DEPLOYMENT.md](server/DEPLOYMENT.md)
4. Tester: `python server/test_config.py`
5. Monitorer: `sudo journalctl -u capteur -f`
