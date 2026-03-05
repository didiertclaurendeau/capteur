# Guide de Démarrage Rapide

## Installation de Go (requis pour compiler)

### Windows
1. Téléchargez Go depuis https://go.dev/dl/
2. Exécutez l'installeur (ex: `go1.22.0.windows-amd64.msi`)
3. Redémarrez votre terminal
4. Vérifiez l'installation: `go version`

### Mac
```bash
brew install go
```
Ou téléchargez depuis https://go.dev/dl/

### Linux
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install golang-go

# Fedora/RHEL
sudo dnf install golang
```

## Compilation

### Windows
```bash
cd c:\Users\didie\sandbox\capteur
go mod download
go build -o capteur.exe .
```

### Mac/Linux
```bash
cd ~/path/to/capteur
go mod download
go build -o capteur .
```

## Utilisation

### Démarrer une capture
```bash
# Windows
capteur.exe --text "Ma Session" --interval 5

# Mac/Linux
./capteur --text "Ma Session" --interval 5
```

### Arrêter la capture
Appuyez sur **Ctrl+C**

## Installation de FFmpeg (optionnel mais recommandé)

### Windows
1. Téléchargez FFmpeg: https://www.gyan.dev/ffmpeg/builds/
2. Extrayez le ZIP
3. Ajoutez le dossier `bin` au PATH système
4. Vérifiez: `ffmpeg -version`

### Mac
```bash
brew install ffmpeg
```

### Linux
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# Fedora/RHEL
sudo dnf install ffmpeg
```

## Test rapide

Une fois compilé et FFmpeg installé:
```bash
# Capture 5 images avec intervalle de 2 secondes
capteur --text "Test" --interval 2

# Attendez 10 secondes, puis appuyez sur Ctrl+C
# Les vidéos seront créées dans ./output/
```

## Dépannage

### "go: command not found"
Go n'est pas installé ou pas dans le PATH. Suivez les instructions d'installation ci-dessus.

### "ffmpeg: command not found"  
FFmpeg n'est pas installé. Les images seront capturées mais pas converties en vidéo automatiquement. Installez FFmpeg ou créez la vidéo manuellement.

### Compilation échouée sur Windows
Assurez-vous d'utiliser un terminal avec les permissions administrateur si nécessaire.

### Compilation échouée sur Mac
Sur Mac M1/M2, utilisez:
```bash
CGO_ENABLED=1 GOARCH=arm64 go build -o capteur .
```

## Prochaines étapes

- Consultez [README.md](README.md) pour la documentation complète
- Modifiez `main.go` pour personnaliser le comportement
- Utilisez `build.bat` (Windows) ou `build.sh` (Mac/Linux) pour compiler pour toutes les plateformes
