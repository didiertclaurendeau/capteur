# ✨ Nouvelles Fonctionnalités - Mode Upload avec Serveur Flask

Ce document décrit les nouvelles fonctionnalités ajoutées à l'application Capteur.

## 🎯 Vue d'ensemble

L'application possède maintenant **deux modes de fonctionnement** :

### Mode 1 : Local (Original)
Capture les images localement et crée une vidéo compressée à la fin.

### Mode 2 : Upload (Nouveau)
Envoie les images en temps réel vers un serveur Flask qui les stocke et permet de les visualiser via une interface web.

---

## 📋 Modifications du Client Go

### Nouveaux paramètres CLI

| Paramètre | Alias | Description |
|-----------|-------|-------------|
| `--url` | `-u` | URL du serveur pour l'upload (ex: http://localhost:5000/upload) |
| `--id` | `-d` | ID du client (généré automatiquement si non spécifié) |

### Nouvelles fonctionnalités

1. **Upload HTTP** : Envoi des images via multipart/form-data
2. **ID aléatoire** : Génération automatique si non spécifié
3. **Mode hybride** : Sélection automatique entre local et upload selon les paramètres
4. **Pas de vidéo** : En mode upload, pas de conversion vidéo (images envoyées en direct)

### Exemple d'utilisation

```bash
# Mode local (comportement original)
capteur.exe --text "Session" --interval 5

# Mode upload vers serveur local
capteur.exe --text "Session" --url http://localhost:5000/upload --id mon_pc

# Mode upload avec ID auto-généré
capteur.exe --text "Session" --url http://server.local:5000/upload
```

---

## 🌐 Nouveau Serveur Flask

### Architecture

```
server/
├── app.py                    # Application Flask principale
├── requirements.txt          # Dépendances Python
├── add_user.py              # Script pour ajouter des utilisateurs
├── start_server.bat         # Démarrage Windows
├── start_server.sh          # Démarrage Mac/Linux
├── README.md                # Documentation du serveur
└── templates/               # Interface web
    ├── base.html            # Template de base
    ├── login.html           # Page de connexion
    ├── gallery.html         # Galerie d'images
    └── detail.html          # Détail d'une image
```

### Fonctionnalités principales

#### 🔐 Authentification
- Système de login/logout sécurisé
- Mots de passe hashés (bcrypt)
- Sessions utilisateurs
- Utilisateur par défaut : `admin` / `admin123`

#### 📸 Réception d'images
- Endpoint POST `/upload`
- Accepte multipart/form-data
- Validation des fichiers
- Métadonnées stockées en JSON

#### 🖼️ Gestion des images
- **Rotation automatique** : Conserve les 3 dernières images par moniteur
- **Miniatures** : Génération automatique (200x200px)
- **Organisation** : Par client ID et moniteur ID
- **Nommage** : Format `{client_id}_{monitor_id}.png`

#### 🎨 Interface Web

##### Page de connexion (`/login`)
- Design moderne et épuré
- Informations d'identification par défaut affichées
- Messages d'erreur clairs

##### Galerie (`/`)
- Vue en grille avec miniatures
- Organisation par client
- Statistiques (nombre de clients, nombre d'images)
- Horodatage de chaque image
- Badge pour identifier le moniteur
- Responsive design

##### Page de détail (`/image/<filename>`)
- Image en taille réelle
- Zoom au clic
- Métadonnées complètes
- Bouton de téléchargement
- Retour à la galerie

### Endpoints API

| Méthode | Route | Description | Auth |
|---------|-------|-------------|------|
| GET | `/` | Galerie d'images | ✅ |
| GET | `/login` | Page de connexion | ❌ |
| POST | `/login` | Authentification | ❌ |
| GET | `/logout` | Déconnexion | ❌ |
| POST | `/upload` | Upload d'image | ❌ |
| GET | `/image/<filename>` | Détail image | ✅ |
| GET | `/thumbnail/<filename>` | Miniature | ❌ |
| GET | `/fullimage/<filename>` | Image complète | ✅ |

### Configuration

#### Paramètres modifiables dans `app.py`

```python
# Port du serveur
app.run(host='0.0.0.0', port=5000, debug=True)

# Nombre d'images conservées par moniteur
MAX_IMAGES_PER_CLIENT = 3

# Taille des miniatures
THUMBNAIL_SIZE = (200, 200)

# Clé secrète (IMPORTANT: à changer en production!)
app.secret_key = 'votre_cle_secrete_a_changer'
```

---

## 🚀 Installation et Démarrage

### Client Go

```bash
# Télécharger les dépendances
go mod download

# Compiler
go build -o capteur.exe .

# Utiliser en mode local
capteur.exe --text "Ma Session"

# Utiliser en mode upload
capteur.exe --text "Ma Session" --url http://localhost:5000/upload
```

### Serveur Flask

```bash
cd server

# Créer un environnement virtuel (recommandé)
python -m venv venv
venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # Mac/Linux

# Installer les dépendances
pip install -r requirements.txt

# Démarrer le serveur
python app.py
# ou
start_server.bat  # Windows
./start_server.sh  # Mac/Linux
```

---

## 📊 Flux de données

### Mode Local
```
Client → Capture → Sauvegarde locale → Vidéo MP4
```

### Mode Upload
```
Client → Capture → Upload HTTP → Serveur Flask
                                      ↓
                                  Sauvegarde
                                      ↓
                                  Miniature
                                      ↓
                                  Rotation
                                      ↓
                              Interface Web
```

---

## 🔒 Sécurité

### Implémenté
- ✅ Authentification par session
- ✅ Mots de passe hashés
- ✅ Validation des noms de fichiers (secure_filename)
- ✅ Protection CSRF basique

### Recommandations pour la production
- 🔸 Changer la clé secrète
- 🔸 Utiliser HTTPS
- 🔸 Ajouter rate limiting
- 🔸 Utiliser une vraie base de données
- 🔸 Désactiver le mode debug
- 🔸 Ajouter des logs détaillés
- 🔸 Limiter la taille des uploads

---

## 🎨 Technologies utilisées

### Client
- **Go 1.21+**
- **github.com/kbinani/screenshot** - Capture d'écran
- **github.com/fogleman/gg** - Overlay de texte
- **github.com/spf13/pflag** - Parsing CLI
- **net/http** - Client HTTP

### Serveur
- **Flask 3.0** - Framework web
- **Pillow 10.2** - Traitement d'images
- **Werkzeug 3.0** - Utilitaires (hash, sécurité)
- **HTML/CSS** - Interface utilisateur

---

## 📝 Exemples d'utilisation

### Scénario 1 : Monitoring local
```bash
capteur.exe --text "Poste 1" --interval 10 --fps 5
```
→ Crée une vidéo locale

### Scénario 2 : Surveillance réseau
```bash
# Sur le serveur
cd server && python app.py

# Sur chaque client
capteur.exe --text "Bureau Est" --url http://192.168.1.100:5000/upload --id bureau_est
capteur.exe --text "Bureau Ouest" --url http://192.168.1.100:5000/upload --id bureau_ouest
```
→ Toutes les images arrivent sur le serveur

### Scénario 3 : Tests rapides
```bash
# Serveur local
cd server && start_server.bat

# Client avec ID auto
capteur.exe --text "Test" --url http://localhost:5000/upload --interval 2

# Voir dans le navigateur
# http://localhost:5000
```

---

## 🐛 Dépannage

### Le serveur ne démarre pas
- Vérifiez que Python 3.8+ est installé
- Installez les dépendances : `pip install -r requirements.txt`
- Vérifiez que le port 5000 est disponible

### Les images n'arrivent pas
- Vérifiez que le serveur est démarré
- Vérifiez l'URL (doit finir par `/upload`)
- Vérifiez le pare-feu
- Testez avec curl :
  ```bash
  curl -X POST http://localhost:5000/upload
  ```

### Les miniatures ne s'affichent pas
- Vérifiez que Pillow est installé
- Vérifiez les permissions du dossier `thumbnails/`
- Regardez les logs du serveur

---

## 📈 Évolutions futures possibles

- [ ] Support de l'authentification par token/API key
- [ ] Compression des images avant envoi
- [ ] Streaming vidéo en temps réel
- [ ] Notifications push
- [ ] Tableau de bord avec statistiques
- [ ] Export des images en batch
- [ ] Support de multiples utilisateurs avec permissions
- [ ] Base de données PostgreSQL/MySQL
- [ ] Docker containerization
- [ ] API REST complète

---

## 📄 Licence

MIT License - Libre d'utilisation et de modification

---

## 👥 Contribution

Les contributions sont bienvenues ! Pour ajouter des fonctionnalités :

1. Fork le projet
2. Créez une branche (`git checkout -b feature/AmazingFeature`)
3. Commit (`git commit -m 'Add AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request
