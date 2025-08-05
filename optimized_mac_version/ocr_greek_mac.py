#!/usr/bin/env python3
"""
OCR GREC ANCIEN - VERSION MAC OPTIMISÉE
======================================
Version refactorisée, optimisée pour macOS avec toutes les fonctionnalités intégrées.
"""

import os
import sys
import json
import time
import gc
import logging
import threading
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import wraps
from collections import defaultdict

# Imports Tkinter
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

# Imports PIL
from PIL import Image, ImageTk

# Imports externes
import pytesseract
import cv2
import numpy as np
import requests
import sv_ttk
from dotenv import load_dotenv
import webbrowser
from datetime import datetime
import platform

# Support PDF conditionnel
try:
    from pdf2image import convert_from_path, pdfinfo_from_path
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    logging.warning("pdf2image non installé : support PDF désactivé.")

# Configuration logging optimisée pour Mac
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("ocr_greek_mac.log"), 
        logging.StreamHandler()
    ]
)

# Chargement variables environnement
load_dotenv()


@dataclass
class AppState:
    """État global de l'application optimisé"""
    current_page: int = 0
    is_processing: bool = False
    ai_processing: bool = False
    zoom_factor: float = 1.0
    current_theme: str = "light"
    current_images: List[Image.Image] = field(default_factory=list)
    ocr_results: List[Dict[str, Any]] = field(default_factory=list)
    pdf_cache: Dict[str, Any] = field(default_factory=dict)
    pdf_cache_order: List[str] = field(default_factory=list)
    current_file_path: str = ""
    current_task_id: str = ""
    identified_author: Optional[Dict[str, Any]] = None


class ValidationError(Exception):
    """Exception pour les erreurs de validation"""
    pass


class MacOptimizedConfig:
    """Configuration optimisée pour macOS"""
    
    # Configuration Tesseract optimisée
    TESSERACT_CONFIG = {
        "default": "--oem 3 --psm 6 -c tessedit_do_invert=0",
        "single_word": "--oem 3 --psm 8 -c tessedit_do_invert=0",
        "sparse": "--oem 3 --psm 11 -c tessedit_do_invert=0",
        "block": "--oem 3 --psm 3 -c tessedit_do_invert=0",
        "line": "--oem 3 --psm 7 -c tessedit_do_invert=0"
    }
    
    # Langues supportées
    LANGUAGES = {
        "auto": {"code": "grc+eng+fra", "name": "Auto (Grec + Anglais + Français)"},
        "grec_ancien": {"code": "grc", "name": "Grec Ancien"},
        "grec_moderne": {"code": "ell", "name": "Grec Moderne"},
        "anglais": {"code": "eng", "name": "Anglais"},
        "francais": {"code": "fra", "name": "Français"},
        "latin": {"code": "lat", "name": "Latin"}
    }
    
    # Configuration UI optimisée pour Mac
    UI_CONFIG = {
        "window_title": "OCR Grec Mac v6.0",
        "window_size": "1400x900",
        "min_size": "800x600",
        "mac_style": True
    }
    
    # Configuration IA
    AI_CONFIG = {
        "openrouter": {
            "api_key": "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",
            "url": "https://openrouter.ai/api/v1/chat/completions",
            "model": "anthropic/claude-3-haiku",
            "max_tokens": 1000,
            "temperature": 0.3,
            "timeout": 30
        }
    }
    
    # Messages
    MESSAGES = {
        "errors": {
            "no_image": "Aucune image chargée",
            "no_ocr_results": "Aucun résultat OCR disponible",
            "processing": "Traitement en cours...",
            "ocr_error": "Erreur OCR: {error}"
        },
        "info": {
            "ocr_complete": "OCR terminé avec succès",
            "image_loaded": "Image chargée: {filename}"
        }
    }
    
    # Optimisations Mac
    MAC_OPTIMIZATIONS = {
        "use_metal": True,
        "optimize_memory": True,
        "gesture_support": True,
        "retina_display": True,
        "native_menus": True
    }


class MacOptimizedUIManager:
    """Gestionnaire d'interface utilisateur optimisé pour Mac"""
    
    def __init__(self, app: 'MacOptimizedOCRApp') -> None:
        self.app = app
        self.setup_mac_theme()
        
    def setup_mac_theme(self) -> None:
        """Configure le thème Mac"""
        if platform.system() == "Darwin":
            # Utiliser le thème système Mac
            sv_ttk.set_theme("light")
            self.colors = {
                "bg": "#ffffff",
                "fg": "#000000",
                "button_bg": "#f0f0f0",
                "button_fg": "#000000",
                "text_bg": "#fafafa",
                "text_fg": "#000000",
                "accent": "#007aff",
                "success": "#34c759",
                "warning": "#ff9500",
                "error": "#ff3b30"
            }
        else:
            # Thème par défaut pour autres systèmes
            self.colors = {
                "bg": "#ffffff",
                "fg": "#1f1f1f",
                "button_bg": "#f3f2f1",
                "button_fg": "#1f1f1f",
                "text_bg": "#faf9f8",
                "text_fg": "#1f1f1f",
                "accent": "#0078d4",
                "success": "#107c10",
                "warning": "#ff8c00",
                "error": "#d13438"
            }
        
    def setup_window(self) -> None:
        """Configure la fenêtre principale optimisée pour Mac"""
        self.app.title(MacOptimizedConfig.UI_CONFIG["window_title"])
        self.app.geometry(MacOptimizedConfig.UI_CONFIG["window_size"])
        self.app.minsize(*map(int, MacOptimizedConfig.UI_CONFIG["min_size"].split('x')))
        self.app.configure(bg=self.colors["bg"])
        
        # Optimisations Mac
        if platform.system() == "Darwin":
            self._setup_mac_specifics()
    
    def _setup_mac_specifics(self) -> None:
        """Configuration spécifique à Mac"""
        # Centrage sur écran Retina
        self.app.update_idletasks()
        width = self.app.winfo_width()
        height = self.app.winfo_height()
        x = (self.app.winfo_screenwidth() // 2) - (width // 2)
        y = (self.app.winfo_screenheight() // 2) - (height // 2)
        self.app.geometry(f"{width}x{height}+{x}+{y}")
        
        # Support Retina Display
        if hasattr(self.app, 'tk.call'):
            self.app.tk.call('tk', 'scaling', 2.0)
    
    def create_menu(self) -> None:
        """Crée le menu principal optimisé pour Mac"""
        menubar = tk.Menu(self.app, bg=self.colors["bg"], fg=self.colors["fg"])
        self.app.config(menu=menubar)
        
        # Menu Fichier
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.colors["bg"], fg=self.colors["fg"])
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Ouvrir Image", command=self.app.open_image, accelerator="⌘O")
        file_menu.add_command(label="Ouvrir PDF", command=self.app.open_pdf, accelerator="⌘P")
        file_menu.add_separator()
        file_menu.add_command(label="Exporter", command=self.app.export_results, accelerator="⌘E")
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.app.quit, accelerator="⌘Q")
        
        # Menu OCR
        ocr_menu = tk.Menu(menubar, tearoff=0, bg=self.colors["bg"], fg=self.colors["fg"])
        menubar.add_cascade(label="OCR", menu=ocr_menu)
        ocr_menu.add_command(label="Lancer OCR", command=self.app.perform_ocr, accelerator="⌘R")
        
        # Menu FIND !
        find_menu = tk.Menu(menubar, tearoff=0, bg=self.colors["bg"], fg=self.colors["fg"])
        menubar.add_cascade(label="FIND !", menu=find_menu)
        find_menu.add_command(label="🔍 Identifier Auteur/Œuvre", command=self.app.perform_find, accelerator="⌘F")
        find_menu.add_command(label="📚 Rechercher dans Perseus", command=self.app.search_perseus)
        find_menu.add_command(label="🔗 Comparer avec Original", command=self.app.compare_with_original)
        find_menu.add_separator()
        find_menu.add_command(label="🔤 Recherche Lemmatique", command=self.app.open_lemmatique_search, accelerator="⌘L")
        find_menu.add_separator()
        find_menu.add_command(label="⚙️ Configuration FIND !", command=self.app.configure_find)
        
        # Menu Tuteur IA
        tutor_menu = tk.Menu(menubar, tearoff=0, bg=self.colors["bg"], fg=self.colors["fg"])
        menubar.add_cascade(label="🎓 Tuteur IA", menu=tutor_menu)
        tutor_menu.add_command(label="💬 Chat avec Tuteur", command=self.app.open_tutor_ia, accelerator="⌘T")
        tutor_menu.add_separator()
        tutor_menu.add_command(label="📝 Historique Conversations", command=self.app.show_conversation_history)
        
        # Menu Histoire
        history_menu = tk.Menu(menubar, tearoff=0, bg=self.colors["bg"], fg=self.colors["fg"])
        menubar.add_cascade(label="🏺 Histoire", menu=history_menu)
        history_menu.add_command(label="📅 Frise Chronologique", command=self.app.open_historical_context, accelerator="⌘H")
        history_menu.add_command(label="🗺️ Cartes Interactives", command=self.app.show_historical_maps)
        history_menu.add_command(label="🔗 Influences Auteurs", command=self.app.show_author_influences)
        history_menu.add_command(label="📚 Événements Historiques", command=self.app.show_historical_events)
        
        # Menu Contrôles Gestuels (Mac uniquement)
        if platform.system() == "Darwin":
            gesture_menu = tk.Menu(menubar, tearoff=0, bg=self.colors["bg"], fg=self.colors["fg"])
            menubar.add_cascade(label="👆 Gestes", menu=gesture_menu)
            gesture_menu.add_command(label="🔧 Configuration Gestes", command=self.app.open_gesture_controls, accelerator="⌘G")
            gesture_menu.add_command(label="📊 Historique Gestes", command=self.app.show_gesture_history)
            gesture_menu.add_command(label="⚙️ Gestes Personnalisés", command=self.app.configure_custom_gestures)
            gesture_menu.add_separator()
            gesture_menu.add_command(label="🔍 Zoom Pincement", command=lambda: self.app.set_gesture_setting("pinch_zoom", True))
            gesture_menu.add_command(label="🔄 Rotation Pages", command=lambda: self.app.set_gesture_setting("rotation_pages", True))
            gesture_menu.add_command(label="📱 Navigation Glissement", command=lambda: self.app.set_gesture_setting("swipe_navigation", True))
        
        # Menu Aide
        help_menu = tk.Menu(menubar, tearoff=0, bg=self.colors["bg"], fg=self.colors["fg"])
        menubar.add_cascade(label="Aide", menu=help_menu)
        help_menu.add_command(label="À propos", command=self.app.show_about)
    
    def create_toolbar(self) -> None:
        """Crée la barre d'outils optimisée pour Mac"""
        toolbar = tk.Frame(self.app, bg=self.colors["bg"], relief=tk.RAISED, bd=1)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # Boutons principaux
        tk.Button(toolbar, text="📁 Ouvrir", command=self.app.open_image,
                 bg=self.colors["button_bg"], fg=self.colors["button_fg"]).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="📄 PDF", command=self.app.open_pdf,
                 bg=self.colors["button_bg"], fg=self.colors["button_fg"]).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="🔍 OCR", command=self.app.perform_ocr,
                 bg=self.colors["button_bg"], fg=self.colors["button_fg"]).pack(side=tk.LEFT, padx=2)
        
        # Séparateur
        tk.Frame(toolbar, width=2, bg="#e1dfdd").pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        # Bouton FIND ! révolutionnaire
        find_button = tk.Button(toolbar, text="🔍 FIND !", command=self.app.perform_find,
                               bg=self.colors["accent"], fg="white", font=("SF Pro Display", 10, "bold"),
                               relief=tk.RAISED, bd=2)
        find_button.pack(side=tk.LEFT, padx=5)
        
        # Bouton Recherche Lemmatique
        lemmatique_button = tk.Button(toolbar, text="🔤 Lemmatique", command=self.app.open_lemmatique_search,
                                     bg="#9c27b0", fg="white", font=("SF Pro Display", 10, "bold"),
                                     relief=tk.RAISED, bd=2)
        lemmatique_button.pack(side=tk.LEFT, padx=5)
        
        # Bouton Tuteur IA
        tutor_button = tk.Button(toolbar, text="🎓 Tuteur IA", command=self.app.open_tutor_ia,
                                bg=self.colors["success"], fg="white", font=("SF Pro Display", 10, "bold"),
                                relief=tk.RAISED, bd=2)
        tutor_button.pack(side=tk.LEFT, padx=5)
        
        # Bouton Contexte Historique
        history_button = tk.Button(toolbar, text="🏺 Histoire", command=self.app.open_historical_context,
                                  bg=self.colors["warning"], fg="white", font=("SF Pro Display", 10, "bold"),
                                  relief=tk.RAISED, bd=2)
        history_button.pack(side=tk.LEFT, padx=5)
        
        # Bouton Contrôles Gestuels (Mac uniquement)
        if platform.system() == "Darwin":
            gesture_button = tk.Button(toolbar, text="👆 Gestes", command=self.app.open_gesture_controls,
                                     bg="#9c27b0", fg="white", font=("SF Pro Display", 10, "bold"),
                                     relief=tk.RAISED, bd=2)
            gesture_button.pack(side=tk.LEFT, padx=5)
        
        # Séparateur
        tk.Frame(toolbar, width=2, bg="#e1dfdd").pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        # Contrôles zoom
        tk.Button(toolbar, text="🔍+", command=self.app.zoom_in,
                 bg=self.colors["button_bg"], fg=self.colors["button_fg"]).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="🔍-", command=self.app.zoom_out,
                 bg=self.colors["button_bg"], fg=self.colors["button_fg"]).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="🔍⟲", command=self.app.zoom_reset,
                 bg=self.colors["button_bg"], fg=self.colors["button_fg"]).pack(side=tk.LEFT, padx=2)
    
    def create_main_panel(self) -> None:
        """Crée le panneau principal optimisé"""
        self.main_panel = tk.Frame(self.app, bg=self.colors["bg"])
        self.main_panel.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_status_bar(self) -> None:
        """Crée la barre de statut optimisée"""
        self.status_bar = tk.Label(self.app, text="Prêt", bd=1, relief=tk.SUNKEN, anchor=tk.W,
                                  bg=self.colors["text_bg"], fg=self.colors["text_fg"])
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)


class MacOptimizedFileManager:
    """Gestionnaire de fichiers optimisé pour Mac"""
    
    def __init__(self, app: 'MacOptimizedOCRApp') -> None:
        self.app = app
    
    def handle_file_open(self, filename: str) -> None:
        """Gère l'ouverture d'un fichier optimisé"""
        if not filename:
            return
            
        if self._is_image_file(filename):
            self._load_image_safe(filename)
        elif self._is_pdf_file(filename):
            self._load_pdf_safe(filename)
        else:
            messagebox.showerror("Erreur", f"Format de fichier non supporté: {filename}")
    
    def _is_image_file(self, filename: str) -> bool:
        """Vérifie si c'est un fichier image"""
        extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif']
        return any(filename.lower().endswith(ext) for ext in extensions)
    
    def _is_pdf_file(self, filename: str) -> bool:
        """Vérifie si c'est un fichier PDF"""
        return filename.lower().endswith('.pdf')
    
    def _load_image_safe(self, path: str) -> None:
        """Charge une image de manière sécurisée et optimisée"""
        try:
            with Image.open(path) as img:
                # Conversion en RGB si nécessaire
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Optimisation pour Mac (Retina Display)
                max_size = 4096 if platform.system() == "Darwin" else 2048
                if max(img.size) > max_size:
                    ratio = max_size / max(img.size)
                    new_size = tuple(int(dim * ratio) for dim in img.size)
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                self.app.state.current_images = [img]
                self.app.state.current_file_path = path
                self.app.state.current_page = 0
                self.app.display_current_image()
                self.app.set_status(MacOptimizedConfig.MESSAGES["info"]["image_loaded"].format(filename=Path(path).name))
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement de l'image: {e}")
    
    def _load_pdf_safe(self, path: str) -> None:
        """Charge un PDF de manière sécurisée et optimisée"""
        if not PDF_SUPPORT:
            messagebox.showerror("Erreur", "Support PDF non disponible")
            return
        
        try:
            self.app.set_status("Chargement PDF en cours...")
            
            # Conversion PDF optimisée
            dpi = 300 if platform.system() == "Darwin" else 200
            images = convert_from_path(path, dpi=dpi, fmt='RGB')
            
            # Optimisation des images pour Mac
            optimized_images = []
            max_size = 2048 if platform.system() == "Darwin" else 1024
            for img in images:
                if max(img.size) > max_size:
                    ratio = max_size / max(img.size)
                    new_size = tuple(int(dim * ratio) for dim in img.size)
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                optimized_images.append(img)
            
            self.app.state.current_images = optimized_images
            self.app.state.current_file_path = path
            self.app.state.current_page = 0
            self.app.display_current_image()
            self.app.set_status(f"PDF chargé: {len(optimized_images)} pages")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement PDF: {e}")


# Import des modules spécialisés
try:
    from lemmatique_search import LemmatiqueSearchEngine, LemmatiqueSearchUI
    LEMMATIQUE_AVAILABLE = True
except ImportError:
    LEMMATIQUE_AVAILABLE = False
    logging.warning("Module de recherche lemmatique non disponible")

# Import des autres modules (à créer dans les fichiers séparés)
try:
    from mac_modules.tutor_ia import MacOptimizedTutorIA
    from mac_modules.find_manager import MacOptimizedFindManager
    from mac_modules.historical_context import MacOptimizedHistoricalContext
    from mac_modules.gesture_controls import MacOptimizedGestureControls
    from mac_modules.ocr_manager import MacOptimizedOCRManager
    MODULES_AVAILABLE = True
except ImportError:
    MODULES_AVAILABLE = False
    logging.warning("Modules spécialisés non disponibles, utilisation des versions de base")


class MacOptimizedOCRApp(tk.Tk):
    """Application OCR optimisée pour Mac"""
    
    def __init__(self) -> None:
        super().__init__()
        
        # Initialisation de l'état
        self.state = AppState()
        
        # Initialisation des gestionnaires
        self.file_manager = MacOptimizedFileManager(self)
        self.ui_manager = MacOptimizedUIManager(self)
        
        # Initialisation des modules spécialisés
        self._initialize_modules()
        
        # Configuration de l'interface
        self.ui_manager.setup_window()
        self.ui_manager.create_menu()
        self.ui_manager.create_toolbar()
        self.ui_manager.create_main_panel()
        self.ui_manager.create_status_bar()
        
        # Configuration des événements
        self._setup_events()
        
        # Démarrage
        self._start_app()
    
    def _initialize_modules(self) -> None:
        """Initialise les modules spécialisés"""
        if MODULES_AVAILABLE:
            self.ocr_manager = MacOptimizedOCRManager(self)
            self.find_manager = MacOptimizedFindManager(self)
            self.tuteur_ia = MacOptimizedTutorIA(self)
            self.context_historique = MacOptimizedHistoricalContext(self)
            self.controles_gestuels = MacOptimizedGestureControls(self)
        else:
            # Versions de base si les modules ne sont pas disponibles
            self.ocr_manager = None
            self.find_manager = None
            self.tuteur_ia = None
            self.context_historique = None
            self.controles_gestuels = None
        
        # Initialisation du moteur de recherche lemmatique
        if LEMMATIQUE_AVAILABLE:
            try:
                self.lemmatique_engine = LemmatiqueSearchEngine()
                self.lemmatique_ui = LemmatiqueSearchUI(self, self.lemmatique_engine)
            except Exception as e:
                logging.error(f"Erreur initialisation lemmatique: {e}")
                self.lemmatique_engine = None
                self.lemmatique_ui = None
        else:
            self.lemmatique_engine = None
            self.lemmatique_ui = None
    
    def _setup_events(self) -> None:
        """Configure les événements de l'application"""
        # Raccourcis clavier optimisés pour Mac
        self.bind('<Command-o>', lambda e: self.open_image())
        self.bind('<Command-p>', lambda e: self.open_pdf())
        self.bind('<Command-r>', lambda e: self.perform_ocr())
        self.bind('<Command-f>', lambda e: self.perform_find())
        self.bind('<Command-l>', lambda e: self.open_lemmatique_search())
        self.bind('<Command-t>', lambda e: self.open_tutor_ia())
        self.bind('<Command-h>', lambda e: self.open_historical_context())
        if platform.system() == "Darwin":
            self.bind('<Command-g>', lambda e: self.open_gesture_controls())
        
        # Événements de fermeture
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _start_app(self) -> None:
        """Démarre l'application optimisée"""
        logging.info(f"OS: {sys.platform}")
        logging.info(f"Python: {sys.version}")
        logging.info(f"Tesseract: {pytesseract.get_tesseract_version()}")
        logging.info(f"PDF Support: {PDF_SUPPORT}")
        logging.info(f"Mac Optimizations: {MacOptimizedConfig.MAC_OPTIMIZATIONS}")
        
        self.set_status("Application prête - Optimisée pour Mac")
    
    def _on_closing(self) -> None:
        """Gère la fermeture de l'application"""
        self.quit()
    
    # Méthodes publiques pour l'interface
    def open_image(self) -> None:
        """Ouvre une image"""
        filename = filedialog.askopenfilename(
            title="Sélectionner une image",
            filetypes=[
                ("Images", "*.png *.jpg *.jpeg *.bmp *.tiff *.gif"),
                ("Tous les fichiers", "*.*")
            ]
        )
        self.file_manager.handle_file_open(filename)
    
    def open_pdf(self) -> None:
        """Ouvre un PDF"""
        if not PDF_SUPPORT:
            messagebox.showerror("Erreur", "Support PDF non disponible")
            return
        
        filename = filedialog.askopenfilename(
            title="Sélectionner un PDF",
            filetypes=[("PDF", "*.pdf"), ("Tous les fichiers", "*.*")]
        )
        self.file_manager.handle_file_open(filename)
    
    def perform_ocr(self) -> None:
        """Lance l'OCR"""
        if self.ocr_manager:
            self.ocr_manager.perform_ocr()
        else:
            messagebox.showwarning("Attention", "Module OCR non disponible")
    
    def perform_find(self) -> None:
        """Lance la fonction FIND !"""
        if self.find_manager:
            self.find_manager.perform_find()
        else:
            messagebox.showwarning("Attention", "Module FIND ! non disponible")
    
    def open_lemmatique_search(self) -> None:
        """Ouvre l'outil de recherche lemmatique"""
        if not self.lemmatique_ui:
            messagebox.showerror("Erreur", "Module de recherche lemmatique non disponible")
            return
        
        # Récupérer le texte OCR actuel
        ocr_text = ""
        if self.state.ocr_results:
            ocr_text = self.extract_text_from_ocr_results()
        
        # Ouvrir l'interface de recherche lemmatique
        self.lemmatique_ui.show_search_dialog(ocr_text)
        self.set_status("🔤 Recherche lemmatique ouverte")
    
    def open_tutor_ia(self) -> None:
        """Ouvre l'interface du tuteur IA"""
        if self.tuteur_ia:
            self.tuteur_ia.open_tutor_ia()
        else:
            messagebox.showwarning("Attention", "Module Tuteur IA non disponible")
    
    def open_historical_context(self) -> None:
        """Ouvre l'interface de contextualisation historique"""
        if self.context_historique:
            self.context_historique.open_historical_context()
        else:
            messagebox.showwarning("Attention", "Module Contexte Historique non disponible")
    
    def open_gesture_controls(self) -> None:
        """Ouvre l'interface de configuration des gestes"""
        if platform.system() != "Darwin":
            messagebox.showinfo("Contrôles Gestuels", "Les contrôles gestuels sont disponibles uniquement sur macOS.")
            return
        
        if self.controles_gestuels:
            self.controles_gestuels.open_gesture_controls()
        else:
            messagebox.showwarning("Attention", "Module Contrôles Gestuels non disponible")
    
    # Méthodes de configuration
    def set_gesture_setting(self, setting: str, enabled: bool) -> None:
        """Définit un paramètre de geste"""
        if self.controles_gestuels:
            self.controles_gestuels.set_gesture_setting(setting, enabled)
    
    # Méthodes d'affichage
    def display_current_image(self) -> None:
        """Affiche l'image courante"""
        if not self.state.current_images:
            return
        
        try:
            # Effacer le contenu précédent du panneau principal
            for widget in self.ui_manager.main_panel.winfo_children():
                widget.destroy()
            
            # Récupérer l'image courante
            current_image = self.state.current_images[self.state.current_page]
            
            # Créer un canvas pour l'affichage avec scrollbar
            canvas_frame = tk.Frame(self.ui_manager.main_panel, bg=self.ui_manager.colors["bg"])
            canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Canvas pour l'image
            canvas = tk.Canvas(canvas_frame, bg=self.ui_manager.colors["bg"], highlightthickness=0)
            
            # Scrollbars
            h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=canvas.xview)
            v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
            
            # Configuration du canvas
            canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
            
            # Redimensionner l'image selon le zoom
            img_width, img_height = current_image.size
            zoomed_width = int(img_width * self.state.zoom_factor)
            zoomed_height = int(img_height * self.state.zoom_factor)
            
            # Redimensionner l'image
            resized_image = current_image.resize((zoomed_width, zoomed_height), Image.Resampling.LANCZOS)
            
            # Convertir en PhotoImage
            photo = ImageTk.PhotoImage(resized_image)
            
            # Garder une référence pour éviter le garbage collection
            self.current_photo = photo
            
            # Ajouter l'image au canvas
            canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            canvas.configure(scrollregion=canvas.bbox("all"))
            
            # Pack des éléments
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
            
            # Informations sur l'image
            info_frame = tk.Frame(self.ui_manager.main_panel, bg=self.ui_manager.colors["text_bg"])
            info_frame.pack(fill=tk.X, padx=5, pady=2)
            
            # Nombre de pages pour les PDF
            if len(self.state.current_images) > 1:
                page_info = f"Page {self.state.current_page + 1} sur {len(self.state.current_images)}"
                
                # Contrôles de navigation
                nav_frame = tk.Frame(info_frame, bg=self.ui_manager.colors["text_bg"])
                nav_frame.pack(side=tk.RIGHT, padx=5)
                
                if self.state.current_page > 0:
                    prev_button = tk.Button(nav_frame, text="◀ Précédent", 
                                          command=self.previous_page,
                                          bg=self.ui_manager.colors["button_bg"],
                                          fg=self.ui_manager.colors["button_fg"])
                    prev_button.pack(side=tk.LEFT, padx=2)
                
                if self.state.current_page < len(self.state.current_images) - 1:
                    next_button = tk.Button(nav_frame, text="Suivant ▶", 
                                          command=self.next_page,
                                          bg=self.ui_manager.colors["button_bg"],
                                          fg=self.ui_manager.colors["button_fg"])
                    next_button.pack(side=tk.LEFT, padx=2)
                
                # Label d'information
                tk.Label(info_frame, text=page_info, 
                        bg=self.ui_manager.colors["text_bg"],
                        fg=self.ui_manager.colors["text_fg"]).pack(side=tk.LEFT, padx=5)
            
            # Informations sur l'image
            img_info = f"Taille: {img_width}x{img_height} | Zoom: {self.state.zoom_factor:.1f}x"
            tk.Label(info_frame, text=img_info, 
                    bg=self.ui_manager.colors["text_bg"],
                    fg=self.ui_manager.colors["text_fg"]).pack(side=tk.RIGHT, padx=5)
            
            # Mettre à jour le statut
            filename = Path(self.state.current_file_path).name
            self.set_status(f"Image affichée: {filename} - Page {self.state.current_page + 1}")
            
        except Exception as e:
            messagebox.showerror("Erreur d'affichage", f"Erreur lors de l'affichage de l'image: {e}")
            logging.error(f"Erreur display_current_image: {e}")
    
    def previous_page(self) -> None:
        """Page précédente"""
        if self.state.current_page > 0:
            self.state.current_page -= 1
            self.display_current_image()
    
    def next_page(self) -> None:
        """Page suivante"""
        if self.state.current_page < len(self.state.current_images) - 1:
            self.state.current_page += 1
            self.display_current_image()
    
    def set_status(self, text: str) -> None:
        """Met à jour la barre de statut"""
        if hasattr(self.ui_manager, 'status_bar'):
            self.ui_manager.status_bar.config(text=text)
    
    def extract_text_from_ocr_results(self) -> str:
        """Extrait le texte des résultats OCR"""
        if not self.state.ocr_results:
            return ""
        
        text_parts = []
        for result in self.state.ocr_results:
            if isinstance(result, dict) and 'text' in result:
                text_parts.append(result['text'])
        
        return " ".join(text_parts)
    
    # Méthodes de zoom
    def zoom_in(self) -> None:
        """Zoom avant"""
        if self.state.current_images:
            self.state.zoom_factor *= 1.2
            self.display_current_image()
    
    def zoom_out(self) -> None:
        """Zoom arrière"""
        if self.state.current_images:
            self.state.zoom_factor /= 1.2
            self.display_current_image()
    
    def zoom_reset(self) -> None:
        """Remet le zoom à zéro"""
        if self.state.current_images:
            self.state.zoom_factor = 1.0
            self.display_current_image()
    
    # Méthodes utilitaires
    def export_results(self) -> None:
        """Exporte les résultats"""
        if not self.state.ocr_results:
            messagebox.showwarning("Attention", "Aucun résultat à exporter")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Exporter les résultats",
            defaultextension=".txt",
            filetypes=[("Texte", "*.txt"), ("JSON", "*.json"), ("Tous les fichiers", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    if filename.endswith('.json'):
                        json.dump(self.state.ocr_results, f, ensure_ascii=False, indent=2)
                    else:
                        for result in self.state.ocr_results:
                            if isinstance(result, dict) and 'text' in result:
                                f.write(result['text'] + '\n')
                
                self.set_status(f"Résultats exportés vers {filename}")
                messagebox.showinfo("Succès", "Résultats exportés avec succès")
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'export: {e}")
    
    def show_about(self) -> None:
        """Affiche la boîte de dialogue À propos"""
        about_text = f"""OCR Grec Mac v6.0

Version optimisée pour macOS
Développé avec Python et Tkinter

Fonctionnalités:
• OCR de textes grecs anciens
• Recherche lemmatique avancée
• Tuteur IA spécialisé
• Contextualisation historique
• Contrôles gestuels Mac
• Support PDF complet

© 2025 - Version Mac Optimisée"""
        
        messagebox.showinfo("À propos", about_text)
    
    # Méthodes de placeholder pour les modules non disponibles
    def search_perseus(self) -> None:
        """Recherche dans Perseus"""
        messagebox.showinfo("Perseus", "Fonctionnalité Perseus non disponible dans cette version")
    
    def compare_with_original(self) -> None:
        """Compare avec l'original"""
        messagebox.showinfo("Comparaison", "Fonctionnalité de comparaison non disponible dans cette version")
    
    def configure_find(self) -> None:
        """Configure FIND !"""
        messagebox.showinfo("Configuration FIND !", "Configuration FIND ! non disponible dans cette version")
    
    def show_conversation_history(self) -> None:
        """Affiche l'historique des conversations"""
        messagebox.showinfo("Historique", "Historique des conversations non disponible dans cette version")
    
    def show_historical_maps(self) -> None:
        """Affiche les cartes historiques"""
        messagebox.showinfo("Cartes", "Cartes historiques non disponibles dans cette version")
    
    def show_author_influences(self) -> None:
        """Affiche les influences d'auteurs"""
        messagebox.showinfo("Influences", "Influences d'auteurs non disponibles dans cette version")
    
    def show_historical_events(self) -> None:
        """Affiche les événements historiques"""
        messagebox.showinfo("Événements", "Événements historiques non disponibles dans cette version")
    
    def show_gesture_history(self) -> None:
        """Affiche l'historique des gestes"""
        messagebox.showinfo("Historique Gestes", "Historique des gestes non disponible dans cette version")
    
    def configure_custom_gestures(self) -> None:
        """Configure les gestes personnalisés"""
        messagebox.showinfo("Gestes Personnalisés", "Configuration des gestes personnalisés non disponible dans cette version")


def main() -> None:
    """Fonction principale"""
    try:
        app = MacOptimizedOCRApp()
        app.mainloop()
    except Exception as e:
        logging.error(f"Erreur fatale: {e}")
        messagebox.showerror("Erreur Fatale", f"Erreur lors du démarrage de l'application:\n{e}")


if __name__ == "__main__":
    main() 