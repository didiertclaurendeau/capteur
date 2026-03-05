# Serveur Flask - Récepteur d'Images

Serveur web Flask pour recevoir et gérer les images envoyées par l'application de capture d'écran.

## Fonctionnalités

- ✅ **Réception d'images**: Endpoint pour recevoir les images via HTTP POST
- ✅ **Authentification**: Système de login/logout pour sécuriser l'accès
- ✅ **Miniatures automatiques**: Création de thumbnails à la réception
- ✅ **Rotation d'images**: Conserve les 3 dernières images par moniteur
- ✅ **Galerie web**: Interface moderne pour visualiser toutes les images
- ✅ **Vue détaillée**: Clic sur une image pour voir en grand avec zoom
- ✅ **Organisation par client**: Images groupées par Client ID
- ✅ **Support Nginx**: Fonctionne derrière un reverse proxy sur `/capture`
- ✅ **Sessions partagées**: Via Redis pour déploiement multi-worker
- ✅ **Health check**: Endpoint de santé pour monitoring

## Installation

### 1. Installer Python 3.8+

Assurez-vous d'avoir Python 3.8 ou supérieur installé.

### 2. Installer les dépendances

```bash
cd server
pip install -r requirements.txt
```

Ou avec un environnement virtuel (recommandé):

```bash
cd server

# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate

# Puis installer les dépendances
pip install -r requirements.txt
```

## Démarrage du serveur

### Mode développement

```bash
cd server
python app.py
```

Le serveur démarrera sur `http://0.0.0.0:5002`

### Mode production (avec Gunicorn)

```bash
cd server

# Linux/Mac
chmod +x start_gunicorn.sh
./start_gunicorn.sh

# Ou directement
gunicorn --workers 4 --bind 127.0.0.1:5002 app:app
```

### Déploiement derrière Nginx

# Développement (serveur local)
capteur.exe --text "Ma Session" --url http://localhost:5002/upload --id mon_client

# Production (derrière Nginx sur /capture)
capteur.exe --text "Ma Session" --url https://votre-domaine.com/capture/capture`, consultez le guide complet:

📖 **[Guide de déploiement complet](DEPLOYMENT.md)**

L'application est configurée pour fonctionner sur le préfixe `/capture` avec:
- Support multi-workers via Gunicorn
- Sessions partagées via Redis
- Health check sur `/capture/health`
- Configuration Nginx exemple fournie

Installation rapide Redis: [REDIS_INSTALL.md](REDIS_INSTALL.md)

## Connexion par défaut

- **Utilisateur**: `admin`
- **Mot de passe**: `admin123`

⚠️ **IMPORTANT**: Changez ces identifiants en production!

## Utilisation avec le client

### Mode local (sans serveur)
```bash
capteur.exe --text "Ma Session"
```
Les images sont sauvegardées localement et converties en vidéo.

### Mode upload (avec serveur)
```bash
capteur.exe --text "Ma Session" --url http://localhost:5000/upload --id mon_client
```
Les images sont envoyées au serveur en temps réel.

### Paramètres serveur

| Paramètre | Description |
|-----------|-------------|
| `--url` / `-u` | URL du serveur (ex: http://192.168.1.100:5000/upload) |
| `--id` / `-d` | ID du client (généré automatiquement si omis) |

## Configuration du serveur

### Changer le port

Dans [app.py](app.py), modifiez la dernière ligne:
```python
app.run(host='0.0.0.0', port=5000, debug=True)  # Changez 5000
```

### Modifier le nombre d'images conservées

Dans [app.py](app.py), ligne 17:
```python
MAX_IMAGES_PER_CLIENT = 3  # Changez cette valeur
```

### Changer la taille des miniatures

Dans [app.py](app.py), ligne 16:
```python
THUMBNAIL_SIZE = (200, 200)  # (largeur, hauteur)
```

### Ajouter des utilisateurs

Le fichier `users.json` est créé automatiquement. Pour ajouter un utilisateur:

```python
from werkzeug.security import generate_password_hash
import json

# Charger les utilisateurs existants
with open('users.json', 'r') as f:
    users = json.load(f)

# Ajouter un nouvel utilisateur
users['nouveau_user'] = generate_password_hash('mot_de_passe')

# Sauvegarder
with open('users.json', 'w') as f:
    json.dump(users, f)
```

Ou utilisez ce script Python:
```python
from werkzeug.security import generate_password_hash
import json

username = input("Nom d'utilisateur: ")
password = input("Mot de passe: ")

users = {}
try:
    with open('users.json', 'r') as f:
        users = json.load(f)
except:
    pass

users[username] = generate_password_hash(password)

with open('users.json', 'w') as f:
    json.dump(users, f)

print(f"Utilisateur '{username}' créé avec succès!")
```

## Structure des dossiers

```
server/
├── app.py                   # Application Flask principale
├── requirements.txt         # Dépendances Python
├── templates/              # Templates HTML
│   ├── base.html           # Template de base
│   ├── login.html          # Page de connexion
│   ├── gallery.html        # Galerie d'images
│   └── detail.html         # Détail d'une image
├── uploads/                # Images complètes (créé automatiquement)
├── thumbnails/             # Miniatures (créé automatiquement)
├── users.json              # Base de données utilisateurs (créé auto)
└── metadata.json           # Métadonnées des images (créé auto)
```

## API Endpoints

### POST /upload
Reçoit une image du client.

**Paramètres (multipart/form-data)**:
- `image`: Fichier image (PNG)
- `client_id`: ID du client
- `monitor_id`: ID du moniteur (0, 1, 2, etc.)

**Réponse**:
```json
{
  "status": "success",
  "filename": "client_0.png"
}
```

### GET /
Page de galerie (requiert authentification)

### GET /image/<filename>
Page de détail d'une image (requiert authentification)

### GET /thumbnail/<filename>
Retourne la miniature d'une image

### GET /fullimage/<filename>
Retourne l'image complète (requiert authentification)

## Accès distant

Pour accéder au serveur depuis d'autres machines du réseau:

1. Trouvez l'IP de votre machine:
   ```bash
   # Windows
   ipconfig
   
   # Mac/Linux
   ifconfig
   ```

2. Utilisez cette IP dans l'URL du client:
   ```bash
   capteur.exe --text "Test" --url http://192.168.1.XXX:5000/upload
   ```

3. Assurez-vous que le pare-feu autorise les connexions sur le port 5000.

## Sécurité

### Pour la production

1. **Changez la clé secrète** dans [app.py](app.py):
   ```python
   app.secret_key = 'votre_cle_secrete_aleatoire_tres_longue'
   ```

2. **Désactivez le mode debug**:
   ```python
   app.run(host='0.0.0.0', port=5000, debug=False)
   ```

3. **Utilisez HTTPS** avec un reverse proxy (nginx, Apache)

4. **Changez les identifiants par défaut**

5. **Limitez les tailles de fichiers** si nécessaire

## Dépannage

### Port déjà utilisé
Si le port 5000 est déjà utilisé, changez-le dans `app.py` ou arrêtez l'application qui l'utilise.

### Images ne s'affichent pas
Vérifiez que les dossiers `uploads/` et `thumbnails/` existent et ont les permissions d'écriture.

### Erreur d'import PIL
Installez Pillow:
```bash
pip install Pillow
```

### Connexion refusée depuis une autre machine
- Vérifiez que le serveur écoute sur `0.0.0.0` et non `127.0.0.1`
- Vérifiez votre pare-feu
- Assurez-vous d'utiliser la bonne adresse IP

## Développement

Pour contribuer ou modifier:

1. Activez le mode debug (déjà activé par défaut)
2. Les modifications aux templates sont rechargées automatiquement
3. Les modifications au code Python nécessitent un redémarrage

## Licence

MIT License - Libre d'utilisation et de modification
