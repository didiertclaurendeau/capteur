@echo off
REM Script pour démarrer le serveur Flask

echo Demarrage du serveur Flask...
echo.

REM Vérifier si venv existe
if exist venv\ (
    echo Activation de l'environnement virtuel...
    call venv\Scripts\activate
) else (
    echo ATTENTION: Environnement virtuel non trouve.
    echo Utilisation de Python global.
    echo.
)

echo Demarrage du serveur sur http://localhost:5000
echo Appuyez sur Ctrl+C pour arreter le serveur
echo.
echo Identifiants par defaut:
echo   Username: admin
echo   Password: admin123
echo.
echo ========================================
echo.

python app.py

pause
