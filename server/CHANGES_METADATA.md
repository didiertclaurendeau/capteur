# Corrections des métadonnées et de la galerie

## Problèmes corrigés

### 1. Duplications dans metadata.json ✅
**Problème:** Le fichier metadata.json contenait des entrées en double pour chaque moniteur. Par exemple, pour 3 moniteurs, on avait 3 entrées dupliquées par moniteur au lieu d'une seule par moniteur.

**Solution:** Modifié la fonction `save_metadata()` pour:
- Vérifier si une entrée avec le même `filename` existe déjà
- Mettre à jour le `timestamp` de l'entrée existante au lieu d'ajouter une nouvelle
- Garder seulement une entrée par fichier image

**Avant:**
```python
metadata[key].append({
    'filename': filename,
    'timestamp': datetime.now().isoformat(),
    ...
})
```

**Après:**
```python
# Chercher si une entrée avec le même filename existe déjà
existing_index = None
for i, entry in enumerate(metadata[key]):
    if entry['filename'] == filename:
        existing_index = i
        break

# Mettre à jour l'entrée existante ou ajouter une nouvelle
if existing_index is not None:
    metadata[key][existing_index] = new_entry
else:
    metadata[key].append(new_entry)
```

### 2. Organisation des fichiers ✅
**Problème:** Le fichier metadata.json était stocké à la racine du serveur.

**Solution:** 
- Créé un dossier `server/data/` pour les données
- Déplacé metadata.json vers `server/data/metadata.json`
- Ajouté `DATA_FOLDER = 'data'` dans la configuration

### 3. Galerie responsive ✅
**Problème:** La galerie n'affichait pas assez de colonnes sur les écrans larges.

**Solution:** Amélioré le CSS avec des breakpoints responsive explicites:
- Mobile (< 576px): 1 colonne
- Tablette (≥ 576px): 2 colonnes
- Desktop (≥ 992px): 3 colonnes
- Large (≥ 1400px): 4 colonnes

## Résultat attendu

Après ces modifications, le fichier `server/data/metadata.json` devrait ressembler à:

```json
{
  "424242_0": [
    {
      "filename": "424242_0.png",
      "timestamp": "2026-03-05T19:42:14.997727",
      "client_id": "424242",
      "monitor_id": "0"
    }
  ],
  "424242_1": [
    {
      "filename": "424242_1.png",
      "timestamp": "2026-03-05T19:42:14.777910",
      "client_id": "424242",
      "monitor_id": "1"
    }
  ],
  "424242_2": [
    {
      "filename": "424242_2.png",
      "timestamp": "2026-03-05T19:42:14.875200",
      "client_id": "424242",
      "monitor_id": "2"
    }
  ]
}
```

**Note:** Une seule entrée par moniteur, avec le timestamp mis à jour à chaque nouvel upload.

## Migration

Si vous avez un ancien fichier metadata.json:

```bash
cd server
mkdir -p data
# Option 1: Supprimer l'ancien (recommandé)
rm metadata.json

# Option 2: Le garder comme backup
mv metadata.json data/metadata_backup.json
```

Le nouveau fichier sera créé automatiquement au prochain upload.

## Test

Pour vérifier que tout fonctionne:

1. Démarrer le serveur
2. Envoyer des captures avec le client Go:
   ```bash
   capteur.exe --text "Test" --url http://localhost:5002/upload --id 424242 --interval 5
   ```
3. Vérifier `server/data/metadata.json` - il devrait y avoir une seule entrée par moniteur
4. Recharger la page de la galerie - les vignettes devraient s'afficher en colonnes multiples

## Fichiers modifiés

- `server/app.py`: Fonction save_metadata() et chemins vers metadata.json
- `server/templates/gallery.html`: CSS responsive pour la grille d'images
