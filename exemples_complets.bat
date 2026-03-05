@echo off
REM Script d'exemple pour demarrer la capture
REM Modifiez les parametres selon vos besoins

echo ========================================
echo Exemples d'utilisation de Capteur
echo ========================================
echo.

REM ========================================
REM MODE LOCAL (Sauvegarde + Video)
REM ========================================
echo MODE LOCAL (Sauvegarde + Video):
echo ----------------------------------------
echo.

echo Exemple 1: Capture basique toutes les 5 secondes
echo Commande: capteur.exe --text "Session 2024"
echo.

echo Exemple 2: Capture toutes les 10 secondes
echo Commande: capteur.exe --text "Test Demo" --interval 10
echo.

echo Exemple 3: Haute frequence avec video rapide
echo Commande: capteur.exe --text "Monitoring" --interval 2 --fps 15
echo.

echo Exemple 4: Configuration complete
echo Commande: capteur.exe --text "Projet XYZ" --interval 3 --fps 10 --fontsize 64 --output ./mes_videos
echo.

REM ========================================
REM MODE UPLOAD (Envoi vers serveur)
REM ========================================
echo.
echo MODE UPLOAD (Envoi vers serveur):
echo ----------------------------------------
echo.

echo Exemple 5: Upload vers serveur local avec ID
echo Commande: capteur.exe --text "Session 2024" --url http://localhost:5000/upload --id poste_bureau
echo.

echo Exemple 6: Upload vers serveur distant
echo Commande: capteur.exe --text "Monitoring" --url http://192.168.1.100:5000/upload --id poste_01 --interval 10
echo.

echo Exemple 7: Upload avec ID auto-genere
echo Commande: capteur.exe --text "Test" --url http://localhost:5000/upload
echo (L'ID sera genere automatiquement)
echo.

echo ========================================
echo Instructions :
echo ========================================
echo.
echo MODE LOCAL: 
echo   1. Compilez: go build -o capteur.exe
echo   2. Executez une commande mode local
echo   3. Ctrl+C pour arreter et creer la video
echo.
echo MODE UPLOAD:
echo   1. Demarrez le serveur: cd server ^&^& start_server.bat
echo   2. Compilez le client: go build -o capteur.exe
echo   3. Executez une commande mode upload
echo   4. Ouvrez http://localhost:5000
echo   5. Login: admin / admin123
echo   6. Ctrl+C pour arreter la capture
echo.

REM Decommentez pour lancer en mode local
REM capteur.exe --text "Ma Session" --interval 5

REM Decommentez pour lancer en mode upload
REM capteur.exe --text "Ma Session" --url http://localhost:5000/upload --id mon_pc

pause
