# Capteur - Application de Capture d'Écran Multi-Moniteurs

Application portable pour capturer des screenshots à intervalles réguliers et créer des vidéos compressées avec overlay de texte. Supporte plusieurs moniteurs simultanément.

>[!IMPORTANT] Cette application fut construite avec l'aide de l'IA pour démontrer les capacités de génération de code et de documentation. Bien que fonctionnelle, elle peut nécessiter des ajustements pour des cas d'utilisation spécifiques.

## Fonctionnalités

- ✅ **Multi-plateforme**: Windows, Mac, Linux
- ✅ **Multi-moniteurs**: Crée un fichier vidéo séparé par moniteur
- ✅ **Overlay de texte**: Affiche un texte personnalisé au centre de chaque image
- ✅ **Compression vidéo**: Utilise H.264 pour des fichiers de taille optimale
- ✅ **Portable**: Un seul exécutable, aucune installation nécessaire
- ✅ **Configurable**: Intervalle, FPS, texte, taille de police via ligne de commande

## Prérequis

### Pour utiliser l'application
- **FFmpeg** (optionnel mais recommandé pour la création automatique de vidéos)
  - Windows: Téléchargez depuis https://www.gyan.dev/ffmpeg/builds/ et ajoutez au PATH
  - Mac: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg` (Ubuntu/Debian) ou `sudo yum install ffmpeg` (CentOS/RHEL)

### Pour compiler l'application
- **Go 1.21+**: Téléchargez depuis https://go.dev/dl/

## Installation Rapide

### Option 1: Télécharger l'exécutable précompilé
1. Téléchargez l'exécutable pour votre plateforme dans la section Releases
2. Placez-le dans un dossier de votre choix
3. C'est tout! L'application est prête à utiliser

### Option 2: Compiler depuis le source

#### Windows
```bash
# Télécharger les dépendances
go mod download

# Compiler pour Windows
go build -ldflags="-s -w" -o capteur.exe .
```

#### Mac
```bash
# Télécharger les dépendances
go mod download

# Compiler pour Mac
go build -ldflags="-s -w" -o capteur .
```

#### Linux
```bash
# Télécharger les dépendances
go mod download

# Compiler pour Linux
go build -ldflags="-s -w" -o capteur .
```

## Utilisation

### Syntaxe de base
```bash
capteur --text "Votre texte ici" [options]
```

### Paramètres

| Paramètre | Court | Description | Défaut | Requis |
|-----------|-------|-------------|--------|--------|
| `--text` | `-t` | Texte à afficher au centre de l'image | - | ✅ Oui |
| `--interval` | `-i` | Intervalle entre captures (secondes) | 5 | Non |
| `--fps` | `-f` | Frame rate de la vidéo de sortie | 5 | Non |
| `--output` | `-o` | Répertoire de sortie | ./output | Non |
| `--fontsize` | `-s` | Taille de la police du texte | 48.0 | Non |

### Exemples

#### Capture toutes les 10 secondes avec texte "Session 2024"
```bash
capteur --text "Session 2024" --interval 10
```

#### Capture toutes les 5 secondes, vidéo à 10 FPS
```bash
capteur --text "Test" --interval 5 --fps 10
```

#### Capture avec texte plus grand et dossier de sortie personnalisé
```bash
capteur --text "Projet XYZ" --fontsize 72 --output ./mes_captures
```

#### Version courte (avec alias)
```bash
capteur -t "Demo" -i 3 -f 15 -o ./demo
```

### Arrêter la capture
Appuyez sur **Ctrl+C** pour arrêter la capture. L'application créera automatiquement les vidéos à partir des images capturées.

## Structure de sortie

```
output/
├── monitor_0/
│   ├── frame_00000.png
│   ├── frame_00001.png
│   └── ...
├── monitor_1/
│   ├── frame_00000.png
│   └── ...
├── monitor_0.mp4
└── monitor_1.mp4
```

- Un dossier `monitor_X` par moniteur contenant les captures PNG
- Un fichier `monitor_X.mp4` par moniteur avec la vidéo compressée

## Compression et qualité

L'application utilise le codec H.264 avec les paramètres suivants:
- **CRF 23**: Qualité standard (0=meilleure qualité, 51=pire qualité)
- **Preset medium**: Compromis entre vitesse d'encodage et compression
- **Format yuv420p**: Compatible avec la plupart des lecteurs vidéo

Pour modifier la compression, éditez les paramètres dans la fonction `createVideo()` du fichier `main.go`:
- CRF plus bas (ex: 18) = meilleure qualité, fichiers plus gros
- CRF plus haut (ex: 28) = qualité réduite, fichiers plus petits

## Compilation cross-plateforme

### Depuis Windows pour toutes les plateformes
```bash
# Pour Windows 64-bit
set GOOS=windows
set GOARCH=amd64
go build -ldflags="-s -w" -o capteur-windows-amd64.exe .

# Pour Mac 64-bit (Intel)
set GOOS=darwin
set GOARCH=amd64
go build -ldflags="-s -w" -o capteur-mac-amd64 .

# Pour Mac ARM (M1/M2)
set GOOS=darwin
set GOARCH=arm64
go build -ldflags="-s -w" -o capteur-mac-arm64 .

# Pour Linux 64-bit
set GOOS=linux
set GOARCH=amd64
go build -ldflags="-s -w" -o capteur-linux-amd64 .
```

### Depuis Mac/Linux pour toutes les plateformes
```bash
# Pour Windows 64-bit
GOOS=windows GOARCH=amd64 go build -ldflags="-s -w" -o capteur-windows-amd64.exe .

# Pour Mac 64-bit (Intel)
GOOS=darwin GOARCH=amd64 go build -ldflags="-s -w" -o capteur-mac-amd64 .

# Pour Mac ARM (M1/M2)
GOOS=darwin GOARCH=arm64 go build -ldflags="-s -w" -o capteur-mac-arm64 .

# Pour Linux 64-bit
GOOS=linux GOARCH=amd64 go build -ldflags="-s -w" -o capteur-linux-amd64 .
```

## Dépannage

### FFmpeg non trouvé
Si FFmpeg n'est pas installé, l'application capturera les images mais ne créera pas la vidéo automatiquement. Vous verrez un message avec la commande à exécuter manuellement pour créer la vidéo.

### Erreur "Aucun moniteur détecté"
Vérifiez que votre système a au moins un moniteur actif et que l'application a les permissions nécessaires.

### Police de caractères non trouvée
L'application tente de charger une police système standard. Si aucune n'est trouvée, le texte ne sera pas ajouté aux images. Vous pouvez modifier les chemins des polices dans la fonction `addTextOverlay()` du fichier `main.go`.

### Taille de fichier importante
Si les vidéos sont trop volumineuses:
1. Augmentez le paramètre CRF (ex: 28 au lieu de 23)
2. Réduisez le FPS de sortie (ex: 2 au lieu de 5)
3. Augmentez l'intervalle entre captures (ex: 10s au lieu de 5s)

## Désinstallation

Pour supprimer l'application, effacez simplement:
1. L'exécutable (`capteur.exe` ou `capteur`)
2. Le dossier de sortie (par défaut `./output`)

Aucune trace n'est laissée dans le système.

## Architecture technique

- **Langage**: Go 1.21+
- **Capture d'écran**: `github.com/kbinani/screenshot` (cross-plateforme)
- **Overlay graphique**: `github.com/fogleman/gg` (basé sur Cairo)
- **Encodage vidéo**: FFmpeg avec H.264
- **CLI**: `github.com/spf13/pflag`

## Licence

MIT License - Libre d'utilisation et de modification

## Contribution

Les contributions sont les bienvenues! N'hésitez pas à ouvrir une issue ou une pull request.
