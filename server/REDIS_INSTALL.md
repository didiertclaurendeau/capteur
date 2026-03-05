# Installation de Redis

Redis est nécessaire pour partager les sessions entre plusieurs workers de l'application en production.

## Windows

### Option 1: Memurai (Recommandé pour Windows)

Memurai est un port Redis entièrement compatible pour Windows.

1. Téléchargez depuis: https://www.memurai.com/get-memurai
2. Installez l'exécutable
3. Démarrez le service Memurai

### Option 2: Redis via WSL2

```bash
# Dans WSL2 (Ubuntu)
sudo apt update
sudo apt install redis-server

# Démarrer Redis
sudo service redis-server start

# Vérifier
redis-cli ping
# Doit retourner: PONG

# Configurer pour démarrer automatiquement
sudo systemctl enable redis-server
```

### Option 3: Docker (Si Docker Desktop est installé)

```bash
# Démarrer un conteneur Redis
docker run -d -p 6379:6379 --name redis redis:alpine

# Vérifier
docker ps

# Se connecter
docker exec -it redis redis-cli ping
```

### Test de connexion

```bash
# Depuis PowerShell ou CMD
# Installer redis-cli pour Windows depuis: https://github.com/microsoftarchive/redis/releases

redis-cli ping
# Doit retourner: PONG
```

## Linux

### Ubuntu/Debian

```bash
sudo apt update
sudo apt install redis-server

# Démarrer
sudo systemctl start redis-server

# Activer au démarrage
sudo systemctl enable redis-server

# Vérifier
redis-cli ping
```

### CentOS/RHEL

```bash
sudo yum install redis

# Démarrer
sudo systemctl start redis

# Activer au démarrage
sudo systemctl enable redis

# Vérifier
redis-cli ping
```

### Fedora

```bash
sudo dnf install redis

# Démarrer
sudo systemctl start redis

# Activer au démarrage
sudo systemctl enable redis

# Vérifier
redis-cli ping
```

## macOS

### Avec Homebrew

```bash
brew install redis

# Démarrer
brew services start redis

# Vérifier
redis-cli ping
```

### Manuellement

```bash
# Télécharger et compiler
wget http://download.redis.io/redis-stable.tar.gz
tar xzf redis-stable.tar.gz
cd redis-stable
make

# Démarrer
src/redis-server
```

## Configuration

### Configuration de base (/etc/redis/redis.conf)

```conf
# Écouter seulement sur localhost (sécurité)
bind 127.0.0.1

# Port par défaut
port 6379

# Activer la persistance
save 900 1
save 300 10
save 60 10000

# Fichier de persistance
dir /var/lib/redis
dbfilename dump.rdb

# Logs
loglevel notice
logfile /var/log/redis/redis-server.log

# Limite mémoire (ajustez selon vos besoins)
maxmemory 256mb
maxmemory-policy allkeys-lru
```

### Redémarrer après modification

```bash
# Linux
sudo systemctl restart redis

# macOS
brew services restart redis
```

## Vérification

### Test de connexion Python

```python
import redis

# Se connecter
r = redis.Redis(host='localhost', port=6379, db=0)

# Test ping
print(r.ping())  # Doit afficher: True

# Écrire une clé
r.set('test', 'Hello Redis!')

# Lire une clé
print(r.get('test'))  # Doit afficher: b'Hello Redis!'

# Supprimer
r.delete('test')
```

### Test via redis-cli

```bash
# Se connecter
redis-cli

# Dans le CLI Redis:
127.0.0.1:6379> ping
PONG

127.0.0.1:6379> set test "Hello"
OK

127.0.0.1:6379> get test
"Hello"

127.0.0.1:6379> keys *
1) "test"

127.0.0.1:6379> del test
(integer) 1

127.0.0.1:6379> exit
```

## Surveillance

### Voir les statistiques

```bash
redis-cli INFO
```

### Surveiller les commandes en temps réel

```bash
redis-cli MONITOR
```

### Voir les clés de session de l'application

```bash
redis-cli KEYS "capteur:*"
```

## Dépannage

### Redis ne démarre pas

```bash
# Vérifier les logs
sudo tail -f /var/log/redis/redis-server.log

# Vérifier le processus
ps aux | grep redis

# Vérifier le port
sudo netstat -tulpn | grep 6379
```

### Connexion refusée

- Vérifiez que Redis est démarré
- Vérifiez le fichier de configuration (bind address)
- Vérifiez le pare-feu

### Fichier de configuration corrompu

```bash
# Sauvegarder l'ancien
sudo cp /etc/redis/redis.conf /etc/redis/redis.conf.bak

# Réinstaller Redis
sudo apt reinstall redis-server  # Ubuntu
```

## Désinstallation

### Linux

```bash
# Ubuntu/Debian
sudo systemctl stop redis-server
sudo apt remove --purge redis-server

# CentOS/RHEL
sudo systemctl stop redis
sudo yum remove redis
```

### macOS

```bash
brew services stop redis
brew uninstall redis
```

### Windows

- Désinstaller Memurai via le panneau de configuration
- Ou arrêter le conteneur Docker:
  ```bash
  docker stop redis
  docker rm redis
  ```

## Alternative sans Redis

Si vous ne pouvez pas installer Redis, l'application utilisera automatiquement le stockage filesystem pour les sessions. Cependant, cela ne fonctionne pas bien avec plusieurs workers.

Pour développement seulement:
```bash
# Ne pas installer Redis
# L'application se repliera sur Flask-Session avec filesystem

# Limitation: Un seul worker Gunicorn
gunicorn --workers 1 app:app
```

⚠️ **Note**: Le stockage filesystem des sessions **ne fonctionne pas** avec plusieurs workers. Vous devez utiliser Redis pour un déploiement multi-worker en production.
