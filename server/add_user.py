"""
Script pour ajouter un utilisateur au serveur Flask
"""
from werkzeug.security import generate_password_hash
import json
import os

def add_user():
    print("=" * 50)
    print("Ajout d'un utilisateur")
    print("=" * 50)
    
    username = input("Nom d'utilisateur: ").strip()
    if not username:
        print("Erreur: Le nom d'utilisateur ne peut pas être vide")
        return
    
    password = input("Mot de passe: ").strip()
    if not password:
        print("Erreur: Le mot de passe ne peut pas être vide")
        return
    
    # Charger les utilisateurs existants
    users_file = 'users.json'
    users = {}
    
    if os.path.exists(users_file):
        try:
            with open(users_file, 'r') as f:
                users = json.load(f)
        except:
            print("Erreur lors de la lecture du fichier users.json")
            return
    
    # Vérifier si l'utilisateur existe déjà
    if username in users:
        confirm = input(f"L'utilisateur '{username}' existe déjà. Remplacer? (o/n): ")
        if confirm.lower() != 'o':
            print("Opération annulée")
            return
    
    # Ajouter l'utilisateur
    users[username] = generate_password_hash(password)
    
    # Sauvegarder
    try:
        with open(users_file, 'w') as f:
            json.dump(users, f, indent=2)
        print(f"\n✅ Utilisateur '{username}' créé avec succès!")
    except Exception as e:
        print(f"\n❌ Erreur lors de la sauvegarde: {e}")

if __name__ == '__main__':
    add_user()
