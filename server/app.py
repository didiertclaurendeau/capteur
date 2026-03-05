from flask import Flask, request, render_template, redirect, url_for, session, flash, send_file
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
from PIL import Image
import os
import json
from datetime import datetime, timedelta
from functools import wraps
import redis

app = Flask(__name__)

# Configuration pour fonctionner derrière Nginx sur /capture
# Note: Nginx strip le préfixe /capture avant de passer à Flask
# donc APPLICATION_ROOT reste à la racine
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'votre_cle_secrete_a_changer')  # IMPORTANT: Changez cette clé en production!

# Configuration des sessions pour Redis (sessions partagées entre workers)
# Si Redis n'est pas disponible, utilise le filesystem comme fallback
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, socket_connect_timeout=1)
    redis_client.ping()
    app.config['SESSION_TYPE'] = 'redis'
    app.config['SESSION_REDIS'] = redis_client
    print("✓ Redis connecté - Sessions partagées activées")
except (redis.ConnectionError, redis.TimeoutError):
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = './flask_session'
    os.makedirs('./flask_session', exist_ok=True)
    print("⚠ Redis non disponible - Utilisation du filesystem pour les sessions")

app.config['SESSION_PERMANENT'] = True
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'capteur:'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
app.config['SESSION_COOKIE_NAME'] = 'capteur_session'
app.config['SESSION_COOKIE_PATH'] = '/capture'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialiser Flask-Session
Session(app)

# Ajouter ProxyFix pour gérer les en-têtes de Nginx
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Configuration
UPLOAD_FOLDER = 'uploads'
THUMBNAILS_FOLDER = 'thumbnails'
DATA_FOLDER = 'data'
THUMBNAIL_SIZE = (200, 200)
MAX_IMAGES_PER_CLIENT = 3  # Nombre d'images à conserver par moniteur

# Créer les dossiers nécessaires
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(THUMBNAILS_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)

# Base de données simple (en production, utilisez une vraie base de données)
USERS_FILE = 'users.json'

def init_users():
    """Initialise le fichier utilisateurs s'il n'existe pas"""
    if not os.path.exists(USERS_FILE):
        # Créer un utilisateur par défaut: admin / admin123
        users = {
            'admin': generate_password_hash('admin123')
        }
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f)

def get_users():
    """Récupère les utilisateurs"""
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    """Sauvegarde les utilisateurs"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

# Health check endpoint pour Nginx/monitoring
@app.route('/health')
def health():
    """Endpoint de santé pour vérifier que l'application fonctionne"""
    try:
        # Vérifier que les dossiers essentiels existent
        checks = {
            'uploads_dir': os.path.exists(UPLOAD_FOLDER),
            'thumbnails_dir': os.path.exists(THUMBNAILS_FOLDER),
            'users_file': os.path.exists(USERS_FILE)
        }
        
        # Vérifier Redis si configuré
        if app.config['SESSION_TYPE'] == 'redis':
            try:
                app.config['SESSION_REDIS'].ping()
                checks['redis'] = True
            except:
                checks['redis'] = False
        
        # Si tous les checks sont OK, retourner 200
        if all(checks.values()):
            return {'status': 'healthy', 'checks': checks}, 200
        else:
            return {'status': 'degraded', 'checks': checks}, 503
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}, 503

# Décorateur pour les routes protégées
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Veuillez vous connecter pour accéder à cette page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        users = get_users()
        
        if username in users and check_password_hash(users[username], password):
            session['username'] = username
            flash('Connexion réussie!', 'success')
            return redirect(url_for('gallery'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Déconnexion réussie.', 'info')
    return redirect(url_for('login'))

@app.route('/upload', methods=['POST'])
def upload():
    """Endpoint pour recevoir les images des clients"""
    if 'image' not in request.files:
        return {'error': 'Aucun fichier image'}, 400
    
    file = request.files['image']
    client_id = request.form.get('client_id', 'unknown')
    monitor_id = request.form.get('monitor_id', '0')
    
    if file.filename == '':
        return {'error': 'Nom de fichier vide'}, 400
    
    # Sauvegarder l'image
    filename = secure_filename(f"{client_id}_{monitor_id}.png")
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    # Créer la miniature
    create_thumbnail(filepath, filename)
    
    # Gérer la rotation des images (garder les N dernières)
    manage_image_rotation(client_id, monitor_id)
    
    # Enregistrer les métadonnées
    save_metadata(client_id, monitor_id, filename)
    
    return {'status': 'success', 'filename': filename}, 200

def create_thumbnail(image_path, filename):
    """Crée une miniature de l'image"""
    try:
        with Image.open(image_path) as img:
            img.thumbnail(THUMBNAIL_SIZE)
            thumb_path = os.path.join(THUMBNAILS_FOLDER, filename)
            img.save(thumb_path, 'PNG')
    except Exception as e:
        print(f"Erreur lors de la création de la miniature: {e}")

def manage_image_rotation(client_id, monitor_id):
    """Gère la rotation des images pour ne garder que les N dernières"""
    pattern = f"{client_id}_{monitor_id}"
    
    # Récupérer toutes les images correspondantes
    images = []
    for filename in os.listdir(UPLOAD_FOLDER):
        if filename.startswith(pattern) and filename.endswith('.png'):
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            images.append({
                'filename': filename,
                'path': filepath,
                'mtime': os.path.getmtime(filepath)
            })
    
    # Trier par date de modification (plus récent en premier)
    images.sort(key=lambda x: x['mtime'], reverse=True)
    
    # Garder seulement les N plus récentes
    if len(images) > MAX_IMAGES_PER_CLIENT:
        for img in images[MAX_IMAGES_PER_CLIENT:]:
            # Supprimer l'image et sa miniature
            try:
                os.remove(img['path'])
                thumb_path = os.path.join(THUMBNAILS_FOLDER, img['filename'])
                if os.path.exists(thumb_path):
                    os.remove(thumb_path)
            except Exception as e:
                print(f"Erreur lors de la suppression de {img['filename']}: {e}")

def save_metadata(client_id, monitor_id, filename):
    """Sauvegarde les métadonnées de l'image"""
    metadata_file = os.path.join(DATA_FOLDER, 'metadata.json')
    
    # Charger les métadonnées existantes
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
    else:
        metadata = {}
    
    # Ajouter/mettre à jour les métadonnées
    key = f"{client_id}_{monitor_id}"
    if key not in metadata:
        metadata[key] = []
    
    # Créer la nouvelle entrée
    new_entry = {
        'filename': filename,
        'timestamp': datetime.now().isoformat(),
        'client_id': client_id,
        'monitor_id': monitor_id
    }
    
    # Chercher si une entrée avec le même filename existe déjà
    existing_index = None
    for i, entry in enumerate(metadata[key]):
        if entry['filename'] == filename:
            existing_index = i
            break
    
    # Mettre à jour l'entrée existante ou ajouter une nouvelle
    if existing_index is not None:
        # Mettre à jour la timestamp de l'entrée existante
        metadata[key][existing_index] = new_entry
    else:
        # Ajouter une nouvelle entrée
        metadata[key].append(new_entry)
    
    # Garder seulement les N dernières entrées
    metadata[key] = metadata[key][-MAX_IMAGES_PER_CLIENT:]
    
    # Sauvegarder
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)

@app.route('/')
@login_required
def gallery():
    """Page principale affichant toutes les miniatures"""
    metadata_file = os.path.join(DATA_FOLDER, 'metadata.json')
    
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
    else:
        metadata = {}
    
    # Organiser les images par client
    images_by_client = {}
    for key, entries in metadata.items():
        client_id = entries[0]['client_id'] if entries else 'unknown'
        if client_id not in images_by_client:
            images_by_client[client_id] = []
        
        for entry in entries:
            filename = entry['filename']
            if os.path.exists(os.path.join(UPLOAD_FOLDER, filename)):
                images_by_client[client_id].append({
                    'filename': filename,
                    'monitor_id': entry['monitor_id'],
                    'timestamp': entry['timestamp']
                })
    
    return render_template('gallery.html', images_by_client=images_by_client)

@app.route('/image/<filename>')
@login_required
def view_image(filename):
    """Page pour voir une image en détail"""
    filename = secure_filename(filename)
    image_path = os.path.join(UPLOAD_FOLDER, filename)
    
    if not os.path.exists(image_path):
        flash('Image non trouvée.', 'danger')
        return redirect(url_for('gallery'))
    
    # Récupérer les métadonnées
    metadata_file = os.path.join(DATA_FOLDER, 'metadata.json')
    image_info = None
    
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
            
        for key, entries in metadata.items():
            for entry in entries:
                if entry['filename'] == filename:
                    image_info = entry
                    break
    
    return render_template('detail.html', filename=filename, image_info=image_info)

@app.route('/thumbnail/<filename>')
def get_thumbnail(filename):
    """Sert la miniature d'une image"""
    filename = secure_filename(filename)
    thumb_path = os.path.join(THUMBNAILS_FOLDER, filename)
    
    if os.path.exists(thumb_path):
        response = send_file(thumb_path, mimetype='image/png')
        # Empêcher la mise en cache agressive pour voir les mises à jour rapidement
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    else:
        return '', 404

@app.route('/fullimage/<filename>')
@login_required
def get_fullimage(filename):
    """Sert l'image complète"""
    filename = secure_filename(filename)
    image_path = os.path.join(UPLOAD_FOLDER, filename)
    
    if os.path.exists(image_path):
        return send_file(image_path, mimetype='image/png')
    else:
        return '', 404

if __name__ == '__main__':
    init_users()
    print("=" * 50)
    print("Serveur de réception d'images")
    print("=" * 50)
    print("Configuration:")
    print(f"  Type de session: {app.config['SESSION_TYPE']}")
    print(f"  Cookie path: {app.config.get('SESSION_COOKIE_PATH', '/')}")
    print("")
    print("Utilisateur par défaut:")
    print("  Username: admin")
    print("  Password: admin123")
    print("")
    print("IMPORTANT: Changez le mot de passe en production!")
    print("")
    print("Pour déploiement avec Nginx:")
    print("  - Configurez le reverse proxy sur /capture")
    print("  - Installez et démarrez Redis pour sessions partagées")
    print("  - Définissez SECRET_KEY dans les variables d'environnement")
    print("  - Utilisez gunicorn avec plusieurs workers")
    print("=" * 50)
    
    # En développement, utiliser le serveur Flask
    # En production, utiliser gunicorn
    app.run(host='0.0.0.0', port=5002, debug=True)
