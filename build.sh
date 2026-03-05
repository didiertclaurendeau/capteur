#!/bin/bash
# Script de build pour Mac/Linux

echo "Téléchargement des dépendances..."
go mod download

echo ""
echo "Compilation pour Windows (64-bit)..."
GOOS=windows GOARCH=amd64 go build -ldflags="-s -w" -o capteur-windows-amd64.exe .

echo ""
echo "Compilation pour Mac Intel (64-bit)..."
GOOS=darwin GOARCH=amd64 go build -ldflags="-s -w" -o capteur-mac-amd64 .

echo ""
echo "Compilation pour Mac ARM (M1/M2)..."
GOOS=darwin GOARCH=arm64 go build -ldflags="-s -w" -o capteur-mac-arm64 .

echo ""
echo "Compilation pour Linux (64-bit)..."
GOOS=linux GOARCH=amd64 go build -ldflags="-s -w" -o capteur-linux-amd64 .

echo ""
echo "Compilation terminée!"
echo "Exécutables créés:"
echo "  - capteur-windows-amd64.exe (Windows 64-bit)"
echo "  - capteur-mac-amd64 (Mac Intel)"
echo "  - capteur-mac-arm64 (Mac M1/M2)"
echo "  - capteur-linux-amd64 (Linux 64-bit)"

# Rendre les exécutables Mac/Linux exécutables
chmod +x capteur-mac-amd64 capteur-mac-arm64 capteur-linux-amd64
