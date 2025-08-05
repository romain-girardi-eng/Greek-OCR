# 🔧 Dépannage - Support PDF

## Problème : Impossible de sélectionner les PDF

### ✅ Solutions rapides

#### 1. Vérifier l'installation de pdf2image
```bash
# Test rapide
python3 -c "import pdf2image; print('pdf2image OK')"
```

Si vous obtenez une erreur :
```bash
pip install pdf2image
```

#### 2. Vérifier l'installation de Poppler
```bash
# Test sur macOS/Linux
pdftoppm -h
```

Si la commande n'existe pas :

**macOS :**
```bash
brew install poppler
```

**Linux (Ubuntu/Debian) :**
```bash
sudo apt update
sudo apt install poppler-utils
```

**Windows :**
- Téléchargez depuis : https://poppler.freedesktop.org/
- Ajoutez le dossier bin au PATH système

#### 3. Test complet
```bash
python3 test_pdf_support.py
```

## 🚨 Problèmes courants

### Erreur : "pdf2image non installé"
**Solution :**
```bash
pip install pdf2image
```

### Erreur : "Poppler not found"
**Solution :**
- Installez Poppler (voir ci-dessus)
- Redémarrez l'application

### Erreur : "Permission denied"
**Solution :**
```bash
# Sur Linux/macOS
chmod +x /usr/local/bin/pdftoppm
```

### Erreur : "DLL not found" (Windows)
**Solution :**
- Installez Visual C++ Redistributable
- Vérifiez que Poppler est dans le PATH

## 🔍 Diagnostic avancé

### Test manuel de pdf2image
```python
from pdf2image import convert_from_path
# Test avec un petit PDF
images = convert_from_path('test.pdf', first_page=1, last_page=1)
print(f"Conversion réussie : {len(images)} page(s)")
```

### Vérification du PATH
```bash
# macOS/Linux
echo $PATH | grep poppler

# Windows
echo %PATH% | findstr poppler
```

### Test de Tesseract
```bash
tesseract --version
tesseract --list-langs
```

## 📋 Checklist de résolution

- [ ] pdf2image installé : `pip install pdf2image`
- [ ] Poppler installé et dans le PATH
- [ ] Tesseract installé et fonctionnel
- [ ] Redémarrage de l'application après installation
- [ ] Test avec le script `test_pdf_support.py`

## 🆘 Si rien ne fonctionne

### Option 1 : Installation complète
```bash
# Désinstaller et réinstaller
pip uninstall pdf2image
pip install pdf2image

# Sur macOS
brew uninstall poppler
brew install poppler

# Sur Linux
sudo apt remove poppler-utils
sudo apt install poppler-utils
```

### Option 2 : Environnement virtuel
```bash
# Créer un nouvel environnement
python3 -m venv ocr_env
source ocr_env/bin/activate  # macOS/Linux
# ou
ocr_env\Scripts\activate     # Windows

# Installer tout
pip install -r requirements.txt
```

### Option 3 : Utiliser uniquement les images
Si le support PDF pose problème, l'application fonctionne parfaitement avec :
- Images PNG, JPG, JPEG, TIFF, BMP, GIF
- Export des résultats en plusieurs formats
- Toutes les fonctionnalités OCR

## 📞 Support

Si le problème persiste :
1. Exécutez `python3 test_pdf_support.py`
2. Copiez la sortie complète
3. Vérifiez votre système d'exploitation et version Python
4. Consultez les logs dans `ocr_app_v4.log`

---

**Note :** L'application fonctionne parfaitement sans support PDF pour les images. Le support PDF est une fonctionnalité bonus qui nécessite des dépendances supplémentaires. 