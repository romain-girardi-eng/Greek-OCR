# Guide d'Installation - OCR Grec Ancien v4.0

## 📋 Prérequis

### Système d'exploitation
- **macOS** 10.14 ou plus récent
- **Windows** 10 ou plus récent
- **Linux** (Ubuntu 18.04+, Debian 10+, etc.)

### Python
- **Python 3.8** ou plus récent
- **pip** (gestionnaire de paquets Python)

## 🚀 Installation

### 1. Installation de Python

#### macOS
```bash
# Avec Homebrew (recommandé)
brew install python3

# Ou télécharger depuis python.org
# https://www.python.org/downloads/macos/
```

#### Windows
```bash
# Télécharger depuis python.org
# https://www.python.org/downloads/windows/
# Cocher "Add Python to PATH" lors de l'installation
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### 2. Installation de Tesseract OCR

#### macOS
```bash
# Avec Homebrew
brew install tesseract
brew install tesseract-lang  # Langues supplémentaires

# Vérification
tesseract --version
```

#### Windows
```bash
# Télécharger depuis GitHub
# https://github.com/UB-Mannheim/tesseract/wiki
# Installer et ajouter au PATH système
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt install tesseract-ocr
sudo apt install tesseract-ocr-grc  # Grec ancien
sudo apt install tesseract-ocr-ell  # Grec moderne
sudo apt install tesseract-ocr-lat  # Latin
```

### 3. Installation des dépendances Python

#### Création d'un environnement virtuel (recommandé)
```bash
# Créer un environnement virtuel
python3 -m venv ocr_env

# Activer l'environnement
# macOS/Linux:
source ocr_env/bin/activate
# Windows:
ocr_env\Scripts\activate
```

#### Installation des paquets
```bash
# Installation des dépendances principales
pip install pillow pytesseract python-dotenv

# Installation des dépendances optionnelles
pip install opencv-python numpy

# Installation du support PDF (optionnel)
pip install pdf2image

# Sur macOS, installer poppler pour pdf2image
brew install poppler

# Sur Linux
sudo apt install poppler-utils
```

### 4. Vérification de l'installation

```bash
# Tester Tesseract
python3 -c "import pytesseract; print(pytesseract.get_tesseract_version())"

# Tester les langues disponibles
tesseract --list-langs
```

## 🎯 Utilisation

### Lancement de l'application
```bash
python3 ocr_greek_app_v4_improved.py
```

### Fonctionnalités principales

#### 1. Ouverture de fichiers
- **Images** : PNG, JPG, JPEG, TIFF, BMP, GIF
- **PDF** : Support illimité avec aucune limite de pages

#### 2. Configuration OCR
- **Langues** : Grec ancien, moderne, latin, anglais, français, etc.
- **Modes** : Par défaut, mot unique, bloc, ligne, etc.
- **Traitement** : Amélioration automatique d'image

#### 3. Export
- **Formats** : JSON, TXT, CSV, HTML, Markdown
- **Métadonnées** : Timestamp, statistiques, configuration

#### 4. Support PDF illimité
- **Aucune limite** : PDFs de toute taille supportés
- **Détection automatique** : Nombre de pages détecté
- **Interruption** : Possibilité d'arrêter la conversion
- **Optimisation** : Gestion mémoire intelligente

## 🔧 Configuration avancée

### Variables d'environnement
Créer un fichier `.env` dans le répertoire de l'application :

```env
# Configuration Tesseract
TESSERACT_CMD=/usr/local/bin/tesseract

# Configuration de l'application
LOG_LEVEL=INFO
CACHE_SIZE=20
MAX_DPI=600
```

### Personnalisation des thèmes
Modifier les thèmes dans la classe `CFG.THEMES` :

```python
THEMES = {
    "light": {
        "bg": "#f0f0f0",
        "fg": "#2c2c2c",
        "accent": "#007acc",
        # ...
    },
    "dark": {
        "bg": "#2d2d30",
        "fg": "#ffffff",
        "accent": "#007acc",
        # ...
    }
}
```

## 🐛 Dépannage

### Problèmes courants

#### 1. Tesseract non trouvé
```bash
# Vérifier l'installation
which tesseract

# Ajouter au PATH si nécessaire
export PATH="/usr/local/bin:$PATH"
```

#### 2. Langues manquantes
```bash
# Lister les langues installées
tesseract --list-langs

# Installer les langues manquantes
# macOS:
brew install tesseract-lang

# Linux:
sudo apt install tesseract-ocr-grc tesseract-ocr-ell
```

#### 3. Erreurs OpenCV
```bash
# Réinstaller OpenCV
pip uninstall opencv-python
pip install opencv-python-headless
```

#### 4. Problèmes PDF
```bash
# Vérifier poppler
which pdftoppm

# Installer poppler si manquant
# macOS:
brew install poppler

# Linux:
sudo apt install poppler-utils
```

### Logs et débogage
L'application génère des logs dans `ocr_app_v4.log` :

```bash
# Suivre les logs en temps réel
tail -f ocr_app_v4.log

# Voir les erreurs
grep ERROR ocr_app_v4.log
```

## 📚 Ressources

### Documentation
- [Tesseract Documentation](https://tesseract-ocr.github.io/)
- [OpenCV Documentation](https://docs.opencv.org/)
- [PIL/Pillow Documentation](https://pillow.readthedocs.io/)

### Langues disponibles
- **grc** : Grec ancien
- **ell** : Grec moderne
- **lat** : Latin
- **eng** : Anglais
- **fra** : Français
- **deu** : Allemand
- **ita** : Italien

### Optimisation des performances

#### Pour les gros fichiers
```python
# Dans CFG, ajuster :
CACHE_SIZE = 10          # Réduire pour économiser la mémoire
PDF_BATCH = 20           # Réduire pour les PDF volumineux
MAX_DPI = 300            # Réduire pour accélérer le traitement
```

#### Pour la qualité maximale
```python
# Dans CFG, ajuster :
MAX_DPI = 600            # Augmenter pour plus de qualité
CACHE_SIZE = 30          # Augmenter pour plus de fluidité
```

## 🤝 Support

### Signaler un bug
1. Vérifier les logs dans `ocr_app_v4.log`
2. Noter la version de Python et Tesseract
3. Décrire les étapes pour reproduire le problème

### Améliorations
Les suggestions d'amélioration sont les bienvenues :
- Interface utilisateur
- Nouvelles fonctionnalités
- Optimisations de performance
- Support de nouvelles langues

## 📄 Licence

Ce projet est distribué sous licence MIT. Voir le fichier LICENSE pour plus de détails.

---

**Note** : Cette application est spécialement optimisée pour le grec ancien mais fonctionne également avec d'autres langues classiques et modernes. 