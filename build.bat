@echo off
REM Script de build pour Windows

echo Telechargement des dependances...
go mod download

echo.
echo Compilation pour Windows (64-bit)...
go build -ldflags="-s -w" -o capteur-windows-amd64.exe .

echo.
echo Compilation pour Mac Intel (64-bit)...
set GOOS=darwin
set GOARCH=amd64
go build -ldflags="-s -w" -o capteur-mac-amd64 .

echo.
echo Compilation pour Mac ARM (M1/M2)...
set GOOS=darwin
set GOARCH=arm64
go build -ldflags="-s -w" -o capteur-mac-arm64 .

echo.
echo Compilation pour Linux (64-bit)...
set GOOS=linux
set GOARCH=amd64
go build -ldflags="-s -w" -o capteur-linux-amd64 .

REM Reset environment variables
set GOOS=
set GOARCH=

echo.
echo Compilation terminee!
echo Executables crees:
echo   - capteur-windows-amd64.exe (Windows 64-bit)
echo   - capteur-mac-amd64 (Mac Intel)
echo   - capteur-mac-arm64 (Mac M1/M2)
echo   - capteur-linux-amd64 (Linux 64-bit)
