#!/bin/bash

# OCR Grec Mac v6.0 - Script d'installation optimisé pour macOS
# =============================================================

set -e  # Arrêter en cas d'erreur

echo "🚀 Installation OCR Grec Mac v6.0"
echo "=================================="

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérification du système
print_status "Vérification du système..."

if [[ "$OSTYPE" != "darwin"* ]]; then
    print_error "Ce script est conçu pour macOS uniquement."
    exit 1
fi

# Vérification de la version de macOS
MACOS_VERSION=$(sw_vers -productVersion)
print_status "macOS version: $MACOS_VERSION"

# Vérification de l'architecture
ARCH=$(uname -m)
print_status "Architecture: $ARCH"

if [[ "$ARCH" == "arm64" ]]; then
    print_success "Apple Silicon détecté - Optimisations activées"
    IS_APPLE_SILICON=true
else
    print_status "Intel Mac détecté"
    IS_APPLE_SILICON=false
fi

# Vérification de Homebrew
print_status "Vérification de Homebrew..."

if ! command -v brew &> /dev/null; then
    print_warning "Homebrew non installé. Installation en cours..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Ajouter Homebrew au PATH pour Apple Silicon
    if [[ "$IS_APPLE_SILICON" == true ]]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
else
    print_success "Homebrew déjà installé"
fi

# Mise à jour de Homebrew
print_status "Mise à jour de Homebrew..."
brew update

# Installation des dépendances système
print_status "Installation des dépendances système..."

# Tesseract OCR
print_status "Installation de Tesseract OCR..."
brew install tesseract
brew install tesseract-lang  # Langues supplémentaires

# Poppler pour le support PDF
print_status "Installation de Poppler..."
brew install poppler

# Python et pip
print_status "Vérification de Python..."
if ! command -v python3 &> /dev/null; then
    print_status "Installation de Python..."
    brew install python
fi

# Vérification de la version Python
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_success "Python version: $PYTHON_VERSION"

# Création de l'environnement virtuel
print_status "Création de l'environnement virtuel..."
if [ -d "venv" ]; then
    print_warning "Environnement virtuel existant détecté. Suppression..."
    rm -rf venv
fi

python3 -m venv venv
source venv/bin/activate

# Mise à jour de pip
print_status "Mise à jour de pip..."
pip install --upgrade pip

# Installation des dépendances Python
print_status "Installation des dépendances Python..."

# Installation des dépendances de base
pip install -r requirements_mac.txt

# Installation des dépendances spécifiques à l'architecture
if [[ "$IS_APPLE_SILICON" == true ]]; then
    print_status "Installation des optimisations Apple Silicon..."
    pip install pyobjc-framework-Cocoa pyobjc-framework-Quartz pyobjc-framework-AVFoundation
fi

# Vérification de Tesseract
print_status "Vérification de Tesseract..."
TESSERACT_VERSION=$(tesseract --version | head -n 1)
print_success "Tesseract: $TESSERACT_VERSION"

# Vérification des langues Tesseract
print_status "Vérification des langues Tesseract..."
LANGUAGES=$(tesseract --list-langs)
if echo "$LANGUAGES" | grep -q "grc"; then
    print_success "Grec ancien (grc) disponible"
else
    print_warning "Grec ancien non trouvé. Installation..."
    brew install tesseract-lang
fi

# Création des répertoires de l'application
print_status "Création des répertoires de l'application..."
mkdir -p ~/Library/Application\ Support/OCR\ Greek\ Mac
mkdir -p ~/Library/Caches/OCR\ Greek\ Mac
mkdir -p ~/Library/Logs/OCR\ Greek\ Mac

# Configuration des permissions
print_status "Configuration des permissions..."
chmod +x ocr_greek_mac.py

# Test de l'installation
print_status "Test de l'installation..."
python3 -c "
import sys
import tkinter as tk
from PIL import Image
import pytesseract
import cv2
import numpy as np

print('✅ Tkinter: OK')
print('✅ PIL/Pillow: OK')
print('✅ pytesseract: OK')
print('✅ OpenCV: OK')
print('✅ NumPy: OK')

# Test Tesseract
try:
    version = pytesseract.get_tesseract_version()
    print(f'✅ Tesseract version: {version}')
except Exception as e:
    print(f'❌ Erreur Tesseract: {e}')

# Test des langues
try:
    langs = pytesseract.get_languages()
    if 'grc' in langs:
        print('✅ Grec ancien disponible')
    else:
        print('⚠️  Grec ancien non disponible')
except Exception as e:
    print(f'❌ Erreur langues: {e}')

print('🎉 Tests terminés avec succès!')
"

# Création du script de lancement
print_status "Création du script de lancement..."
cat > launch_ocr_mac.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python3 ocr_greek_mac.py
EOF

chmod +x launch_ocr_mac.sh

# Création de l'alias dans le shell
print_status "Configuration de l'alias..."
SHELL_PROFILE=""
if [[ -f ~/.zshrc ]]; then
    SHELL_PROFILE=~/.zshrc
elif [[ -f ~/.bash_profile ]]; then
    SHELL_PROFILE=~/.bash_profile
elif [[ -f ~/.bashrc ]]; then
    SHELL_PROFILE=~/.bashrc
fi

if [[ -n "$SHELL_PROFILE" ]]; then
    # Vérifier si l'alias existe déjà
    if ! grep -q "alias ocr-greek" "$SHELL_PROFILE"; then
        echo "" >> "$SHELL_PROFILE"
        echo "# OCR Grec Mac v6.0" >> "$SHELL_PROFILE"
        echo "alias ocr-greek='cd $(pwd) && ./launch_ocr_mac.sh'" >> "$SHELL_PROFILE"
        print_success "Alias 'ocr-greek' ajouté à $SHELL_PROFILE"
    else
        print_warning "Alias 'ocr-greek' déjà présent dans $SHELL_PROFILE"
    fi
fi

# Création du fichier de configuration
print_status "Création du fichier de configuration..."
cat > config.json << EOF
{
    "version": "6.0",
    "platform": "macos",
    "architecture": "$ARCH",
    "apple_silicon": $IS_APPLE_SILICON,
    "installation_date": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "python_version": "$PYTHON_VERSION",
    "tesseract_version": "$(tesseract --version | head -n 1 | cut -d' ' -f2)",
    "paths": {
        "app_support": "$HOME/Library/Application Support/OCR Greek Mac",
        "cache": "$HOME/Library/Caches/OCR Greek Mac",
        "logs": "$HOME/Library/Logs/OCR Greek Mac"
    },
    "optimizations": {
        "use_metal": true,
        "optimize_memory": true,
        "gesture_support": true,
        "retina_display": true,
        "native_menus": true
    }
}
EOF

# Finalisation
print_success "Installation terminée avec succès!"
echo ""
echo "🎉 OCR Grec Mac v6.0 est maintenant installé!"
echo ""
echo "📋 Pour lancer l'application:"
echo "   • Double-cliquez sur 'launch_ocr_mac.sh'"
echo "   • Ou utilisez la commande: ocr-greek"
echo "   • Ou lancez: python3 ocr_greek_mac.py"
echo ""
echo "📁 Fichiers créés:"
echo "   • Application: ocr_greek_mac.py"
echo "   • Lanceur: launch_ocr_mac.sh"
echo "   • Configuration: config.json"
echo "   • Environnement virtuel: venv/"
echo ""
echo "🔧 Optimisations activées:"
echo "   • Support Retina Display"
echo "   • Optimisations Apple Silicon: $IS_APPLE_SILICON"
echo "   • Contrôles gestuels Mac"
echo "   • Interface native macOS"
echo ""
echo "📚 Documentation:"
echo "   • README_MAC.md"
echo "   • LEMMATIQUE_SEARCH_DOCUMENTATION.md"
echo ""
print_success "Installation terminée! 🚀" 