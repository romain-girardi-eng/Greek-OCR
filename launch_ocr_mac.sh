#!/bin/bash

# Script de lancement rapide pour OCR Grec Mac v6.0
# ================================================

echo "🔤 Lancement OCR Grec Mac v6.0..."
echo "=================================="

# Vérifier si on est dans le bon répertoire
if [ ! -f "ocr_greek_main.py" ]; then
    echo "❌ Erreur: Ce script doit être exécuté depuis le répertoire racine du projet"
    exit 1
fi

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Erreur: Python 3 n'est pas installé"
    exit 1
fi

# Vérifier si l'environnement virtuel existe
if [ -d ".venv" ]; then
    echo "✅ Environnement virtuel trouvé, activation..."
    source .venv/bin/activate
else
    echo "⚠️ Aucun environnement virtuel trouvé, utilisation de Python système"
fi

# Vérifier les dépendances
echo "🔍 Vérification des dépendances..."

python3 -c "
import sys
import tkinter as tk
from PIL import Image
import pytesseract

print('✅ Tkinter: OK')
print('✅ PIL/Pillow: OK')

try:
    version = pytesseract.get_tesseract_version()
    print(f'✅ Tesseract: {version}')
except Exception as e:
    print(f'❌ Tesseract: {e}')

try:
    from pdf2image import convert_from_path
    print('✅ PDF Support: OK')
except ImportError:
    print('⚠️ PDF Support: pdf2image non installé')

print('🎉 Vérification terminée!')
"

# Lancer l'application
echo ""
echo "🚀 Lancement de l'application..."
echo "💡 Utilisez ⌘P pour ouvrir un PDF et tester l'affichage"
echo ""

python3 ocr_greek_main.py 