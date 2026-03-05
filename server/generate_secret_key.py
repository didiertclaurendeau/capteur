#!/usr/bin/env python3
"""
Script pour générer une clé secrète forte pour Flask
"""

import secrets

def generate_secret_key(length=32):
    """Génère une clé secrète cryptographiquement sûre"""
    return secrets.token_hex(length)

if __name__ == '__main__':
    print("=" * 60)
    print("Générateur de clé secrète Flask")
    print("=" * 60)
    print()
    
    key = generate_secret_key()
    
    print("Votre nouvelle clé secrète:")
    print()
    print(f"  {key}")
    print()
    print("Ajoutez-la dans votre fichier .env:")
    print()
    print(f"  SECRET_KEY={key}")
    print()
    print("Ou définissez-la comme variable d'environnement:")
    print()
    print("  # Linux/Mac:")
    print(f"  export SECRET_KEY='{key}'")
    print()
    print("  # Windows PowerShell:")
    print(f"  $env:SECRET_KEY='{key}'")
    print()
    print("  # Windows CMD:")
    print(f"  set SECRET_KEY={key}")
    print()
    print("=" * 60)
