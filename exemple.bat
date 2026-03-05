@echo off
REM Script d'exemple pour demarrer la capture
REM Modifiez les parametres selon vos besoins

echo ========================================
echo Exemple d'utilisation de Capteur
echo ========================================
echo.

REM Exemple 1: Utilisation basique
echo Exemple 1: Capture toutes les 5 secondes avec texte "Session 2024"
echo Commande: capteur.exe --text "Session 2024"
echo.

REM Exemple 2: Avec intervalle personnalise
echo Exemple 2: Capture toutes les 10 secondes
echo Commande: capteur.exe --text "Test Demo" --interval 10
echo.

REM Exemple 3: Haute frequence avec vidéo rapide
echo Exemple 3: Capture toutes les 2 secondes, video a 15 FPS
echo Commande: capteur.exe --text "Monitoring" --interval 2 --fps 15
echo.

REM Exemple 4: Configuration complete
echo Exemple 4: Configuration complete personnalisee
echo Commande: capteur.exe --text "Projet XYZ" --interval 3 --fps 10 --fontsize 64 --output ./mes_videos
echo.

echo ========================================
echo Pour executer l'application :
echo ========================================
echo 1. Assurez-vous que capteur.exe est compile
echo 2. Copiez une des commandes ci-dessus
echo 3. Appuyez sur Ctrl+C pour arreter
echo.

REM Decommentez la ligne ci-dessous pour lancer avec des parametres par defaut
REM capteur.exe --text "Ma Session" --interval 5 --fps 5

pause
