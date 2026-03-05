#!/usr/bin/env python3
"""
Script de test pour vérifier la configuration du serveur Capteur
"""

import sys
import os

def test_imports():
    """Teste que toutes les dépendances sont installées"""
    print("🔍 Test des imports...")
    try:
        import flask
        print("  ✓ Flask installé")
    except ImportError:
        print("  ✗ Flask manquant - pip install Flask")
        return False
    
    try:
        import flask_session
        print("  ✓ Flask-Session installé")
    except ImportError:
        print("  ✗ Flask-Session manquant - pip install Flask-Session")
        return False
    
    try:
        import redis
        print("  ✓ Redis client installé")
    except ImportError:
        print("  ✗ Redis client manquant - pip install redis")
        return False
    
    try:
        from PIL import Image
        print("  ✓ Pillow installé")
    except ImportError:
        print("  ✗ Pillow manquant - pip install Pillow")
        return False
    
    try:
        import gunicorn
        print("  ✓ Gunicorn installé")
    except ImportError:
        print("  ✗ Gunicorn manquant - pip install gunicorn")
        return False
    
    return True

def test_redis():
    """Teste la connexion Redis"""
    print("\n🔍 Test de la connexion Redis...")
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0, socket_connect_timeout=2)
        r.ping()
        print("  ✓ Redis est accessible et répond")
        
        # Test d'écriture/lecture
        r.set('test_key', 'test_value', ex=10)
        value = r.get('test_key')
        if value == b'test_value':
            print("  ✓ Écriture/lecture Redis fonctionne")
            r.delete('test_key')
            return True
        else:
            print("  ✗ Problème avec écriture/lecture Redis")
            return False
            
    except redis.ConnectionError:
        print("  ⚠ Redis n'est pas accessible (non critique en dev)")
        print("    L'application utilisera le filesystem pour les sessions")
        return None  # None = warning, pas d'erreur
    except Exception as e:
        print(f"  ✗ Erreur Redis: {e}")
        return False

def test_folders():
    """Vérifie que les dossiers nécessaires existent"""
    print("\n🔍 Test des dossiers...")
    folders = ['uploads', 'thumbnails', 'flask_session']
    all_exist = True
    
    for folder in folders:
        if os.path.exists(folder):
            print(f"  ✓ {folder}/ existe")
        else:
            print(f"  ⚠ {folder}/ n'existe pas - création...")
            try:
                os.makedirs(folder, exist_ok=True)
                print(f"    ✓ {folder}/ créé")
            except Exception as e:
                print(f"    ✗ Impossible de créer {folder}/: {e}")
                all_exist = False
    
    return all_exist

def test_flask_app():
    """Teste que l'application Flask peut être importée"""
    print("\n🔍 Test de l'application Flask...")
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import app
        print("  ✓ app.py peut être importé")
        
        # Vérifier la configuration
        if hasattr(app, 'app'):
            print(f"  ✓ Application Flask trouvée")
            print(f"    - Préfixe URL: {app.app.config.get('APPLICATION_ROOT', '/')}")
            print(f"    - Type de session: {app.app.config.get('SESSION_TYPE', 'non défini')}")
            return True
        else:
            print("  ✗ Variable 'app' non trouvée dans app.py")
            return False
            
    except Exception as e:
        print(f"  ✗ Erreur lors de l'import: {e}")
        return False

def test_secret_key():
    """Vérifie la clé secrète"""
    print("\n🔍 Test de la clé secrète...")
    
    secret_key = os.environ.get('SECRET_KEY')
    if secret_key:
        print(f"  ✓ SECRET_KEY définie dans l'environnement")
        if len(secret_key) >= 32:
            print("  ✓ SECRET_KEY a une longueur suffisante")
            return True
        else:
            print("  ⚠ SECRET_KEY est trop courte (min 32 caractères)")
            return None
    else:
        print("  ⚠ SECRET_KEY non définie dans l'environnement")
        print("    L'application utilisera la clé par défaut (NON RECOMMANDÉ EN PRODUCTION)")
        return None

def test_nginx_config():
    """Vérifie que le fichier de configuration Nginx existe"""
    print("\n🔍 Test du fichier de configuration Nginx...")
    if os.path.exists('nginx.conf'):
        print("  ✓ nginx.conf existe")
        return True
    else:
        print("  ⚠ nginx.conf non trouvé (optionnel)")
        return None

def main():
    print("=" * 60)
    print("Test de Configuration du Serveur Capteur")
    print("=" * 60)
    
    results = {
        'imports': test_imports(),
        'redis': test_redis(),
        'folders': test_folders(),
        'flask_app': test_flask_app(),
        'secret_key': test_secret_key(),
        'nginx_config': test_nginx_config()
    }
    
    print("\n" + "=" * 60)
    print("Résumé des tests")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v is True)
    warnings = sum(1 for v in results.values() if v is None)
    failed = sum(1 for v in results.values() if v is False)
    
    for name, result in results.items():
        status = "✓ PASS" if result is True else "⚠ WARN" if result is None else "✗ FAIL"
        print(f"{name:15} : {status}")
    
    print("=" * 60)
    print(f"Total: {passed} passés, {warnings} avertissements, {failed} échecs")
    
    if failed > 0:
        print("\n❌ Certains tests ont échoué. Veuillez corriger les erreurs.")
        return 1
    elif warnings > 0:
        print("\n⚠️  Quelques avertissements. L'application peut fonctionner mais vérifiez la configuration.")
        return 0
    else:
        print("\n✅ Tous les tests sont passés! Le serveur est prêt.")
        return 0

if __name__ == '__main__':
    sys.exit(main())
