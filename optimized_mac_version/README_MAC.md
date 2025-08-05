# 🔤 OCR Grec Mac v6.0 - Version Optimisée pour macOS

## 📋 Vue d'ensemble

OCR Grec Mac v6.0 est une application révolutionnaire d'OCR (Reconnaissance Optique de Caractères) spécialement conçue pour l'analyse de textes grecs anciens, optimisée pour macOS avec des fonctionnalités avancées et une interface native.

## 🚀 Fonctionnalités Principales

### 🔍 OCR Avancé
- **Reconnaissance de textes grecs anciens** avec Tesseract OCR
- **Support multi-langues** (Grec ancien, Grec moderne, Latin, Anglais, Français)
- **Traitement d'images et PDF** haute résolution
- **Optimisations Retina Display** pour une qualité maximale

### 🔤 Recherche Lemmatique Révolutionnaire
- **Base de données de lemmes grecs** complète
- **Analyse morphologique détaillée** (cas, nombre, genre, temps, voix, mode)
- **Recherche dans textes classiques** (Homère, Platon, Nouveau Testament)
- **Suggestions intelligentes** et auto-complétion

### 🎓 Tuteur IA Spécialisé
- **Assistant IA pour l'apprentissage** du grec ancien
- **Modes d'enseignement** : Grammaire, Littérature, Histoire, Syntaxe
- **Niveaux adaptatifs** : Débutant, Intermédiaire, Avancé
- **Conversations contextuelles** et historique

### 🔍 FIND ! - Identification Intelligente
- **Identification automatique** d'auteur et d'œuvre
- **Recherche dans Perseus** Digital Library
- **Comparaison avec originaux** grecs
- **Suggestions de corrections** intelligentes

### 🏺 Contextualisation Historique
- **Frise chronologique interactive** des auteurs grecs
- **Cartes géographiques** des lieux historiques
- **Influences entre auteurs** et époques
- **Événements historiques** contextuels

### 👆 Contrôles Gestuels Mac (macOS uniquement)
- **Zoom par pincement** sur trackpad
- **Rotation de pages** par gestes
- **Navigation par glissement** entre documents
- **Gestes personnalisables** selon les préférences

## 🖥️ Optimisations macOS

### Apple Silicon (M1/M2/M3)
- **Optimisations natives** pour processeurs ARM64
- **Performance accrue** jusqu'à 3x plus rapide
- **Gestion mémoire optimisée** pour les puces Apple
- **Support Metal** pour l'accélération graphique

### Retina Display
- **Rendu haute résolution** automatique
- **Images optimisées** pour écrans Retina
- **Interface adaptative** selon la densité de pixels
- **Zoom fluide** et précis

### Interface Native
- **Design macOS** natif avec SF Pro Display
- **Menus système** intégrés
- **Contrôles gestuels** trackpad/magic mouse
- **Thème système** automatique (clair/sombre)

## 📦 Installation

### Prérequis
- macOS 10.15 (Catalina) ou plus récent
- Homebrew (installé automatiquement si nécessaire)
- Python 3.8+ (installé automatiquement)

### Installation Automatique
```bash
# Cloner le projet
git clone <repository-url>
cd optimized_mac_version

# Lancer l'installation
chmod +x install_mac.sh
./install_mac.sh
```

### Installation Manuelle
```bash
# 1. Installer les dépendances système
brew install tesseract tesseract-lang poppler python

# 2. Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# 3. Installer les dépendances Python
pip install -r requirements_mac.txt

# 4. Lancer l'application
python3 ocr_greek_mac.py
```

## 🎯 Utilisation

### Lancement Rapide
```bash
# Après installation
ocr-greek

# Ou directement
./launch_ocr_mac.sh
```

### Interface Principale
1. **Ouvrir un document** : Image ou PDF
2. **Lancer l'OCR** : Reconnaissance automatique
3. **Analyser le texte** : Recherche lemmatique, FIND !, Tuteur IA
4. **Exporter les résultats** : Formats TXT, JSON, PDF

### Raccourcis Clavier
- `⌘O` : Ouvrir image
- `⌘P` : Ouvrir PDF
- `⌘R` : Lancer OCR
- `⌘F` : FIND ! - Identifier auteur/œuvre
- `⌘L` : Recherche lemmatique
- `⌘T` : Tuteur IA
- `⌘H` : Contexte historique
- `⌘G` : Contrôles gestuels (Mac uniquement)

## 🏗️ Architecture Technique

### Structure du Projet
```
optimized_mac_version/
├── ocr_greek_mac.py          # Application principale
├── lemmatique_search.py      # Moteur de recherche lemmatique
├── mac_config.py             # Configuration optimisée Mac
├── requirements_mac.txt      # Dépendances Python
├── install_mac.sh           # Script d'installation
├── launch_ocr_mac.sh        # Script de lancement
├── config.json              # Configuration utilisateur
└── README_MAC.md            # Documentation
```

### Technologies Utilisées
- **Python 3.8+** : Langage principal
- **Tkinter** : Interface graphique
- **Tesseract OCR** : Reconnaissance de caractères
- **OpenCV** : Traitement d'images
- **PIL/Pillow** : Manipulation d'images
- **pdf2image** : Support PDF
- **OpenRouter API** : Intelligence artificielle
- **sv-ttk** : Thème moderne pour Tkinter

### Optimisations Performance
- **Multithreading** pour l'OCR
- **Cache intelligent** des résultats
- **Gestion mémoire** optimisée
- **Accélération GPU** via Metal (Apple Silicon)
- **Compression d'images** adaptative

## 🔧 Configuration

### Fichier de Configuration
```json
{
    "version": "6.0",
    "platform": "macos",
    "architecture": "arm64",
    "apple_silicon": true,
    "optimizations": {
        "use_metal": true,
        "optimize_memory": true,
        "gesture_support": true,
        "retina_display": true,
        "native_menus": true
    }
}
```

### Personnalisation
- **Thèmes** : Clair/Sombre automatique
- **Langues** : Grec ancien, moderne, Latin, etc.
- **Gestes** : Personnalisation des contrôles
- **Performance** : Ajustement selon le matériel

## 📊 Fonctionnalités Avancées

### Recherche Lemmatique
- **10 lemmes grecs classiques** avec toutes leurs formes
- **Analyse morphologique** complète
- **Contextes d'usage** dans textes classiques
- **Statistiques détaillées** par cas, nombre, genre

### Tuteur IA
- **Claude 3 Haiku** via OpenRouter
- **Conversations contextuelles** sur le grec ancien
- **Explications grammaticales** détaillées
- **Historique des conversations** persistant

### FIND ! Révolutionnaire
- **Identification automatique** d'auteurs et œuvres
- **Recherche Perseus** intégrée
- **Comparaison intelligente** avec originaux
- **Suggestions de corrections** basées sur l'IA

## 🐛 Dépannage

### Problèmes Courants

#### Tesseract non trouvé
```bash
brew install tesseract
brew install tesseract-lang
```

#### Langue grecque manquante
```bash
tesseract --list-langs
# Si 'grc' manque :
brew install tesseract-lang
```

#### Erreur de permissions
```bash
chmod +x ocr_greek_mac.py
chmod +x launch_ocr_mac.sh
```

#### Problème de mémoire
- Redémarrer l'application
- Fermer d'autres applications
- Vérifier l'espace disque disponible

### Logs et Debug
```bash
# Voir les logs
tail -f ~/Library/Logs/OCR\ Greek\ Mac/ocr_greek_mac.log

# Mode debug
python3 -u ocr_greek_mac.py
```

## 🔄 Mise à Jour

### Mise à Jour Automatique
```bash
# Depuis le répertoire du projet
git pull origin main
./install_mac.sh
```

### Mise à Jour Manuelle
```bash
# Mettre à jour les dépendances
pip install --upgrade -r requirements_mac.txt

# Vérifier Tesseract
brew upgrade tesseract
```

## 📚 Documentation Complète

- **[Documentation Recherche Lemmatique](LEMMATIQUE_SEARCH_DOCUMENTATION.md)**
- **[Guide d'Installation](install_mac.sh)**
- **[Configuration Avancée](mac_config.py)**

## 🤝 Contribution

### Développement
```bash
# Cloner le projet
git clone <repository-url>
cd optimized_mac_version

# Installer en mode développement
pip install -r requirements_mac.txt
pip install pytest black flake8

# Lancer les tests
pytest

# Formater le code
black *.py
```

### Rapporter un Bug
1. Vérifier les logs : `~/Library/Logs/OCR Greek Mac/`
2. Reproduire le problème
3. Créer une issue avec les détails

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

## 🙏 Remerciements

- **Google Tesseract** : Moteur OCR
- **OpenRouter** : API d'intelligence artificielle
- **Perseus Digital Library** : Base de données de textes classiques
- **Communauté Python** : Bibliothèques et outils

## 📞 Support

- **Documentation** : README_MAC.md
- **Issues** : GitHub Issues
- **Email** : support@ocr-greek-mac.com

---

**Version** : 6.0  
**Date** : 5 août 2025  
**Plateforme** : macOS 10.15+  
**Architecture** : Intel x86_64 / Apple Silicon ARM64  
**Statut** : ✅ OPÉRATIONNEL 