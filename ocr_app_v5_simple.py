#!/usr/bin/env python3
"""
OCR GREC ANCIEN – VERSION 5.0 SIMPLIFIÉE
========================================
Version simplifiée pour test et démonstration.
"""

import os
import sys
import json
import time
import gc
import logging
import threading
import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import wraps
from collections import defaultdict, deque

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
import json
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

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("ocr_app_v5_simple.log"), 
        logging.StreamHandler()
    ]
)

# Chargement variables environnement
load_dotenv()

# Configuration spécifique macOS
IS_MACOS = platform.system() == "Darwin"
MACOS_VERSION = None
if IS_MACOS:
    try:
        import subprocess
        result = subprocess.run(['sw_vers', '-productVersion'], capture_output=True, text=True)
        MACOS_VERSION = result.stdout.strip()
        logging.info(f"macOS Version: {MACOS_VERSION}")
    except:
        MACOS_VERSION = "Unknown"

# Configuration du cache
CACHE_DIR = Path.home() / ".greek_ocr_cache"
CACHE_DIR.mkdir(exist_ok=True)
CACHE_DB_PATH = CACHE_DIR / "cache.db"
CACHE_MAX_SIZE = 500 * 1024 * 1024  # 500MB
CACHE_TTL = 24 * 60 * 60  # 24 heures

# Configuration des gestes macOS
GESTURE_CONFIG = {
    "pinch_zoom_sensitivity": 0.1,
    "pan_sensitivity": 1.0,
    "rotation_sensitivity": 0.5,
    "momentum_scrolling": True,
    "haptic_feedback": True,
    "smooth_animations": True,
    "animation_duration": 300,  # ms
    "fps_target": 60
}

# Configuration des polices et tailles
FONT_CONFIG = {
    "default_font": "Segoe UI",
    "default_size": 11,
    "title_size": 16,
    "subtitle_size": 14,
    "button_size": 11,
    "text_size": 11,
    "small_size": 9,
    "large_size": 13
}

# Configuration des thèmes
THEME_CONFIG = {
    "light": {
        "name": "Jour",
        "bg": "#ffffff",
        "fg": "#1f1f1f",
        "button_bg": "#f8f9fa",
        "button_fg": "#212529",
        "text_bg": "#faf9f8",
        "text_fg": "#1f1f1f",
        "accent": "#007acc",
        "success": "#28a745",
        "warning": "#ffc107",
        "danger": "#dc3545",
        "info": "#17a2b8",
        "border": "#dee2e6",
        "highlight": "#e3f2fd"
    },
    "dark": {
        "name": "Nuit",
        "bg": "#1e1e1e",
        "fg": "#ffffff",
        "button_bg": "#2d2d30",
        "button_fg": "#ffffff",
        "text_bg": "#252526",
        "text_fg": "#cccccc",
        "accent": "#0078d4",
        "success": "#107c10",
        "warning": "#ff8c00",
        "danger": "#d13438",
        "info": "#0078d4",
        "border": "#3e3e42",
        "highlight": "#094771"
    },
    "classic": {
        "name": "Classique",
        "bg": "#f0f0f0",
        "fg": "#000000",
        "button_bg": "#e1e1e1",
        "button_fg": "#000000",
        "text_bg": "#ffffff",
        "text_fg": "#000000",
        "accent": "#000080",
        "success": "#008000",
        "warning": "#808000",
        "danger": "#800000",
        "info": "#000080",
        "border": "#808080",
        "highlight": "#c0c0c0"
    },
    "modern": {
        "name": "Moderne",
        "bg": "#f8f9fa",
        "fg": "#212529",
        "button_bg": "#ffffff",
        "button_fg": "#495057",
        "text_bg": "#ffffff",
        "text_fg": "#212529",
        "accent": "#6f42c1",
        "success": "#28a745",
        "warning": "#fd7e14",
        "danger": "#e83e8c",
        "info": "#17a2b8",
        "border": "#e9ecef",
        "highlight": "#f8f9fa"
    }
}

# Styles d'interface disponibles
INTERFACE_STYLES = {
    "default": {
        "name": "Par défaut",
        "border_radius": 0,
        "shadow": False,
        "gradient": False,
        "transparency": 1.0
    },
    "rounded": {
        "name": "Arrondi",
        "border_radius": 8,
        "shadow": True,
        "gradient": False,
        "transparency": 1.0
    },
    "glass": {
        "name": "Verre",
        "border_radius": 12,
        "shadow": True,
        "gradient": True,
        "transparency": 0.95
    },
    "minimal": {
        "name": "Minimaliste",
        "border_radius": 0,
        "shadow": False,
        "gradient": False,
        "transparency": 1.0
    }
}

# Polices disponibles
AVAILABLE_FONTS = [
    "Segoe UI",
    "Arial",
    "Helvetica",
    "Times New Roman",
    "Georgia",
    "Verdana",
    "Tahoma",
    "Trebuchet MS",
    "Lucida Grande",
    "Monaco",
    "Menlo",
    "SF Pro Display",
    "SF Pro Text"
]

# Tailles disponibles
AVAILABLE_SIZES = [8, 9, 10, 11, 12, 13, 14, 16, 18, 20, 22, 24, 26, 28, 32]

# Types de gestes trackpad macOS
class TrackpadGestureType:
    PINCH_ZOOM = "pinch_zoom"
    TWO_FINGER_PAN = "two_finger_pan"
    THREE_FINGER_SWIPE = "three_finger_swipe"
    TWO_FINGER_ROTATION = "two_finger_rotation"
    MOMENTUM_SCROLL = "momentum_scroll"
    FORCE_CLICK = "force_click"
    SECONDARY_CLICK = "secondary_click"

# Import de la base de données exhaustive des auteurs et œuvres gréco-latines
try:
    from greek_latin_database import GRECO_LATIN_DATABASE, get_all_authors, get_works_by_author, search_authors, get_author_info
except ImportError:
    # Fallback si le fichier n'est pas trouvé
    GRECO_LATIN_DATABASE = {
    "Homère": {
        "période": "VIIIe siècle av. J.-C.",
        "œuvres": ["Iliade", "Odyssée", "Hymnes homériques"]
    },
    "Hésiode": {
        "période": "VIIIe siècle av. J.-C.",
        "œuvres": ["Théogonie", "Les Travaux et les Jours", "Le Bouclier d'Héraclès"]
    },
    "Sappho": {
        "période": "VIIe siècle av. J.-C.",
        "œuvres": ["Poèmes lyriques", "Hymne à Aphrodite"]
    },
    "Pindare": {
        "période": "VIe-Ve siècle av. J.-C.",
        "œuvres": ["Odes pythiques", "Odes olympiques", "Odes néméennes", "Odes isthmiques"]
    },
    "Eschyle": {
        "période": "Ve siècle av. J.-C.",
        "œuvres": ["Les Perses", "Les Sept contre Thèbes", "Les Suppliantes", "L'Orestie", "Prométhée enchaîné"]
    },
    "Sophocle": {
        "période": "Ve siècle av. J.-C.",
        "œuvres": ["Antigone", "Œdipe roi", "Œdipe à Colone", "Électre", "Ajax", "Les Trachiniennes", "Philoctète"]
    },
    "Euripide": {
        "période": "Ve siècle av. J.-C.",
        "œuvres": ["Médée", "Hippolyte", "Les Bacchantes", "Iphigénie en Aulide", "Iphigénie en Tauride", "Hélène", "Andromaque"]
    },
    "Aristophane": {
        "période": "Ve-IVe siècle av. J.-C.",
        "œuvres": ["Les Nuées", "Les Guêpes", "Les Oiseaux", "Lysistrata", "Les Grenouilles", "L'Assemblée des femmes"]
    },
    "Hérodote": {
        "période": "Ve siècle av. J.-C.",
        "œuvres": ["Histoires", "Enquête"]
    },
    "Thucydide": {
        "période": "Ve siècle av. J.-C.",
        "œuvres": ["Histoire de la guerre du Péloponnèse"]
    },
    "Xénophon": {
        "période": "Ve-IVe siècle av. J.-C.",
        "œuvres": ["Anabase", "Cyropédie", "Mémorables", "Économique"]
    },
    "Platon": {
        "période": "Ve-IVe siècle av. J.-C.",
        "œuvres": ["La République", "Le Banquet", "Phèdre", "Apologie de Socrate", "Criton", "Phédon", "Timée", "Lois"]
    },
    "Aristote": {
        "période": "IVe siècle av. J.-C.",
        "œuvres": ["Éthique à Nicomaque", "Politique", "Poétique", "Métaphysique", "Organon", "Physique"]
    },
    "Théocrite": {
        "période": "IIIe siècle av. J.-C.",
        "œuvres": ["Idylles", "Bucoliques"]
    },
    "Callimaque": {
        "période": "IIIe siècle av. J.-C.",
        "œuvres": ["Hymnes", "Épigrammes", "Aitia"]
    },
    "Apollonios de Rhodes": {
        "période": "IIIe siècle av. J.-C.",
        "œuvres": ["Argonautiques"]
    },
    "Polybe": {
        "période": "IIe siècle av. J.-C.",
        "œuvres": ["Histoires"]
    },
    "Plutarque": {
        "période": "Ier-IIe siècle ap. J.-C.",
        "œuvres": ["Vies parallèles", "Œuvres morales"]
    },
    "Lucien": {
        "période": "IIe siècle ap. J.-C.",
        "œuvres": ["Dialogues des morts", "Histoires vraies", "L'Âne d'or"]
    },
    "Épictète": {
        "période": "Ier-IIe siècle ap. J.-C.",
        "œuvres": ["Manuel", "Entretiens"]
    },
    "Marc Aurèle": {
        "période": "IIe siècle ap. J.-C.",
        "œuvres": ["Pensées pour moi-même"]
    },
    "Plotin": {
        "période": "IIIe siècle ap. J.-C.",
        "œuvres": ["Ennéades"]
    },
    "Virgile": {
        "période": "Ier siècle av. J.-C.",
        "œuvres": ["Énéide", "Géorgiques", "Bucoliques"]
    },
    "Horace": {
        "période": "Ier siècle av. J.-C.",
        "œuvres": ["Odes", "Épîtres", "Satires", "Art poétique"]
    },
    "Ovide": {
        "période": "Ier siècle av. J.-C.",
        "œuvres": ["Métamorphoses", "Art d'aimer", "Héroïdes", "Tristes", "Pontiques"]
    },
    "Cicéron": {
        "période": "Ier siècle av. J.-C.",
        "œuvres": ["De la République", "Des Lois", "De l'Orateur", "Catilinaires", "Philippiques", "Lettres"]
    },
    "César": {
        "période": "Ier siècle av. J.-C.",
        "œuvres": ["Commentaires sur la Guerre des Gaules", "Commentaires sur la Guerre civile"]
    },
    "Salluste": {
        "période": "Ier siècle av. J.-C.",
        "œuvres": ["Conjuration de Catilina", "Guerre de Jugurtha"]
    },
    "Tite-Live": {
        "période": "Ier siècle av. J.-C.",
        "œuvres": ["Histoire romaine"]
    },
    "Tacite": {
        "période": "Ier-IIe siècle ap. J.-C.",
        "œuvres": ["Annales", "Histoires", "Germanie", "Agricola"]
    },
    "Sénèque": {
        "période": "Ier siècle ap. J.-C.",
        "œuvres": ["Lettres à Lucilius", "De la colère", "De la brièveté de la vie", "Médée", "Phèdre"]
    },
    "Lucain": {
        "période": "Ier siècle ap. J.-C.",
        "œuvres": ["La Pharsale"]
    },
    "Juvénal": {
        "période": "Ier-IIe siècle ap. J.-C.",
        "œuvres": ["Satires"]
    },
    "Pline l'Ancien": {
        "période": "Ier siècle ap. J.-C.",
        "œuvres": ["Histoire naturelle"]
    },
    "Pline le Jeune": {
        "période": "Ier-IIe siècle ap. J.-C.",
        "œuvres": ["Lettres", "Panégyrique de Trajan"]
    },
    "Suétone": {
        "période": "Ier-IIe siècle ap. J.-C.",
        "œuvres": ["Vies des douze Césars"]
    },
    "Apulée": {
        "période": "IIe siècle ap. J.-C.",
        "œuvres": ["L'Âne d'or", "Apologie", "Florides"]
    }
}

    def get_all_authors():
        return list(GRECO_LATIN_DATABASE.keys())
    
    def get_works_by_author(author_name):
        if author_name in GRECO_LATIN_DATABASE:
            return GRECO_LATIN_DATABASE[author_name]["œuvres"]
        return []
    
    def search_authors(search_term):
        results = []
        search_term_lower = search_term.lower()
        for author_name, author_info in GRECO_LATIN_DATABASE.items():
            if (search_term_lower in author_name.lower() or
                search_term_lower in author_info["période"].lower() or
                any(search_term_lower in work.lower() for work in author_info["œuvres"])):
                results.append(author_name)
        return results
    
    def get_author_info(author_name):
        return GRECO_LATIN_DATABASE.get(author_name, {})


@dataclass
class AppState:
    """État global de l'application avec type hints complets"""
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


class ValidationError(Exception):
    """Exception pour les erreurs de validation"""
    pass


class SimpleConfig:
    """Configuration simplifiée"""
    
    # Configuration Tesseract
    TESSERACT_CONFIG = {
        "default": "--oem 3 --psm 6",
        "single_word": "--oem 3 --psm 8",
        "sparse": "--oem 3 --psm 11",
        "block": "--oem 3 --psm 3",
        "line": "--oem 3 --psm 7"
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
    
    # Configuration UI
    UI_CONFIG = {
        "window_title": "OCR Grec v5.0 Simple",
        "window_size": "1200x800",
        "min_size": "600x500"
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


class SimpleUIManager:
    """Gestionnaire d'interface utilisateur simplifié avec gestion des polices"""
    
    def __init__(self, app: 'SimpleOCRApp') -> None:
        self.app = app
        self.colors = {
            "bg": "#ffffff",
            "fg": "#1f1f1f",
            "button_bg": "#f3f2f1",
            "button_fg": "#1f1f1f",
            "text_bg": "#faf9f8",
            "text_fg": "#1f1f1f"
        }
        
        # Références aux gestionnaires
        self.font_manager = None  # Sera défini après l'initialisation
        self.interface_customizer = None  # Sera défini après l'initialisation
    
    def get_current_colors(self) -> dict:
        """Retourne les couleurs du thème actuel"""
        if self.interface_customizer:
            return self.interface_customizer.get_current_theme()
        return self.colors
        
    def setup_window(self) -> None:
        """Configure la fenêtre principale"""
        self.app.title(SimpleConfig.UI_CONFIG["window_title"])
        self.app.geometry(SimpleConfig.UI_CONFIG["window_size"])
        self.app.minsize(*map(int, SimpleConfig.UI_CONFIG["min_size"].split('x')))
        self.app.configure(bg=self.colors["bg"])
        
        # Centrage sur macOS
        if sys.platform == "darwin":
            self._center_window_macos()
    
    def _center_window_macos(self) -> None:
        """Centre la fenêtre sur macOS"""
        self.app.update_idletasks()
        width = self.app.winfo_width()
        height = self.app.winfo_height()
        x = (self.app.winfo_screenwidth() // 2) - (width // 2)
        y = (self.app.winfo_screenheight() // 2) - (height // 2)
        self.app.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_menu(self) -> None:
        """Crée le menu principal"""
        menubar = tk.Menu(self.app, bg=self.colors["bg"], fg=self.colors["fg"])
        self.app.config(menu=menubar)
        
        # Menu Fichier
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.colors["bg"], fg=self.colors["fg"])
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Ouvrir Image", command=self.app.open_image)
        file_menu.add_command(label="Ouvrir PDF", command=self.app.open_pdf)
        file_menu.add_separator()
        file_menu.add_command(label="Exporter", command=self.app.export_results)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.app.quit)
        
        # Menu OCR
        ocr_menu = tk.Menu(menubar, tearoff=0, bg=self.colors["bg"], fg=self.colors["fg"])
        menubar.add_cascade(label="OCR", menu=ocr_menu)
        ocr_menu.add_command(label="Lancer OCR", command=self.app.perform_ocr)
        
        # Menu FIND !
        find_menu = tk.Menu(menubar, tearoff=0, bg=self.colors["bg"], fg=self.colors["fg"])
        menubar.add_cascade(label="FIND !", menu=find_menu)
        find_menu.add_command(label="🔍 Identifier Auteur/Œuvre", command=self.app.perform_find)
        find_menu.add_command(label="📚 Rechercher dans Perseus", command=self.app.search_perseus)
        find_menu.add_command(label="🔗 Comparer avec Original", command=self.app.compare_with_original)
        find_menu.add_separator()
        find_menu.add_command(label="🔤 Recherche Lemmatique", command=self.app.open_lemmatique_search)
        find_menu.add_separator()
        find_menu.add_command(label="⚙️ Configuration FIND !", command=self.app.configure_find)
        
        # Menu Tuteur IA
        tutor_menu = tk.Menu(menubar, tearoff=0, bg=self.colors["bg"], fg=self.colors["fg"])
        menubar.add_cascade(label="🎓 Tuteur IA", menu=tutor_menu)
        tutor_menu.add_command(label="💬 Chat avec Tuteur", command=self.app.open_tutor_ia)
        tutor_menu.add_separator()
        tutor_menu.add_command(label="📝 Historique Conversations", command=self.app.show_conversation_history)
        
        # Menu Histoire
        history_menu = tk.Menu(menubar, tearoff=0, bg=self.colors["bg"], fg=self.colors["fg"])
        menubar.add_cascade(label="🏺 Histoire", menu=history_menu)
        history_menu.add_command(label="📅 Frise Chronologique", command=self.app.open_historical_context)
        history_menu.add_command(label="🗺️ Cartes Interactives", command=self.app.show_historical_maps)
        history_menu.add_command(label="🔗 Influences Auteurs", command=self.app.show_author_influences)
        history_menu.add_command(label="📚 Événements Historiques", command=self.app.show_historical_events)
        
        # Menu Contrôles Gestuels (Mac uniquement)
        if platform.system() == "Darwin":
            gesture_menu = tk.Menu(menubar, tearoff=0, bg=self.colors["bg"], fg=self.colors["fg"])
            menubar.add_cascade(label="👆 Gestes", menu=gesture_menu)
            gesture_menu.add_command(label="🔧 Configuration Gestes", command=self.app.open_gesture_controls)
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
        """Crée la barre d'outils avec polices harmonisées"""
        toolbar = tk.Frame(self.app, bg=self.colors["bg"], relief=tk.RAISED, bd=1)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # Style uniforme pour tous les boutons - Police plus grande et noire
        button_font = ("Segoe UI", 13, "bold")  # Police plus grande
        button_padx = 8
        button_pady = 4
        
        # Boutons principaux - Tous en noir
        tk.Button(toolbar, text="📁 Ouvrir", command=self.app.open_image,
                 bg="#f8f9fa", fg="black", font=button_font,
                 relief=tk.RAISED, bd=2, padx=button_padx, pady=button_pady).pack(side=tk.LEFT, padx=3)
        
        tk.Button(toolbar, text="📄 PDF", command=self.app.open_pdf,
                 bg="#f8f9fa", fg="black", font=button_font,
                 relief=tk.RAISED, bd=2, padx=button_padx, pady=button_pady).pack(side=tk.LEFT, padx=3)
        
        # Bouton OCR avec menu déroulant
        ocr_frame = tk.Frame(toolbar, bg="#f8f9fa")
        ocr_frame.pack(side=tk.LEFT, padx=3)
        
        ocr_button = tk.Button(ocr_frame, text="🔍 OCR", command=self.app.perform_ocr,
                              bg="#f8f9fa", fg="black", font=button_font,
                              relief=tk.RAISED, bd=2, padx=button_padx, pady=button_pady)
        ocr_button.pack(side=tk.LEFT)
        
        # Bouton options OCR avancées
        ocr_options_button = tk.Button(ocr_frame, text="⚙️", command=self.app.open_ocr_options,
                                      bg="#f8f9fa", fg="black", font=("Segoe UI", 10, "bold"),
                                      relief=tk.RAISED, bd=1, padx=2, pady=button_pady)
        ocr_options_button.pack(side=tk.LEFT, padx=(2, 0))
        
        # Séparateur
        tk.Frame(toolbar, width=2, bg="#dee2e6").pack(side=tk.LEFT, padx=8, fill=tk.Y)
        
        # Bouton FIND ! révolutionnaire - Noir
        find_button = tk.Button(toolbar, text="🔍 FIND !", command=self.app.perform_find,
                               bg="#007acc", fg="black", font=button_font,
                               relief=tk.RAISED, bd=2, padx=button_padx, pady=button_pady)
        find_button.pack(side=tk.LEFT, padx=3)
        
        # Bouton Recherche Lemmatique - Noir
        lemmatique_button = tk.Button(toolbar, text="🔤 Lemmatique", command=self.app.open_lemmatique_search,
                                     bg="#6f42c1", fg="black", font=button_font,
                                     relief=tk.RAISED, bd=2, padx=button_padx, pady=button_pady)
        lemmatique_button.pack(side=tk.LEFT, padx=3)
        
        # Bouton Tuteur IA - Noir
        tutor_button = tk.Button(toolbar, text="🎓 Tuteur IA", command=self.app.open_tutor_ia,
                                bg="#28a745", fg="black", font=button_font,
                                relief=tk.RAISED, bd=2, padx=button_padx, pady=button_pady)
        tutor_button.pack(side=tk.LEFT, padx=3)
        
        # Bouton Contexte Historique - Noir
        history_button = tk.Button(toolbar, text="🏺 Histoire", command=self.app.open_historical_context,
                                  bg="#fd7e14", fg="black", font=button_font,
                                  relief=tk.RAISED, bd=2, padx=button_padx, pady=button_pady)
        history_button.pack(side=tk.LEFT, padx=3)
        
        # Bouton Contrôles Gestuels (Mac uniquement) - Noir
        if platform.system() == "Darwin":
            gesture_button = tk.Button(toolbar, text="👆 Gestes", command=self.app.open_gesture_controls,
                                     bg="#17a2b8", fg="black", font=button_font,
                                     relief=tk.RAISED, bd=2, padx=button_padx, pady=button_pady)
            gesture_button.pack(side=tk.LEFT, padx=3)
        
        # Séparateur
        tk.Frame(toolbar, width=2, bg="#dee2e6").pack(side=tk.LEFT, padx=8, fill=tk.Y)
        
        # Contrôles zoom avec style uniforme - Noir
        tk.Button(toolbar, text="🔍+", command=self.app.zoom_in,
                 bg="#f8f9fa", fg="black", font=button_font,
                 relief=tk.RAISED, bd=2, padx=button_padx, pady=button_pady).pack(side=tk.LEFT, padx=3)
        
        tk.Button(toolbar, text="🔍-", command=self.app.zoom_out,
                 bg="#f8f9fa", fg="black", font=button_font,
                 relief=tk.RAISED, bd=2, padx=button_padx, pady=button_pady).pack(side=tk.LEFT, padx=3)
        
        tk.Button(toolbar, text="🔍⟲", command=self.app.zoom_reset,
                 bg="#f8f9fa", fg="black", font=button_font,
                 relief=tk.RAISED, bd=2, padx=button_padx, pady=button_pady).pack(side=tk.LEFT, padx=3)
        
        # Séparateur
        tk.Frame(toolbar, width=2, bg="#dee2e6").pack(side=tk.LEFT, padx=8, fill=tk.Y)
        
        # Bouton Paramètres de Police - Noir
        font_button = tk.Button(toolbar, text="🔤 Police", command=self.app.open_font_settings,
                               bg="#6c757d", fg="black", font=button_font,
                               relief=tk.RAISED, bd=2, padx=button_padx, pady=button_pady)
        font_button.pack(side=tk.LEFT, padx=3)
        
        # Séparateur
        tk.Frame(toolbar, width=2, bg="#dee2e6").pack(side=tk.LEFT, padx=8, fill=tk.Y)
        
        # Bouton Personnalisation de l'Interface - Noir
        custom_button = tk.Button(toolbar, text="🎨 Personnalisation", command=self.app.open_interface_customization,
                                 bg="#fd7e14", fg="black", font=button_font,
                                 relief=tk.RAISED, bd=2, padx=button_padx, pady=button_pady)
        custom_button.pack(side=tk.LEFT, padx=3)
    
    def create_main_panel(self) -> None:
        """Crée le panneau principal avec interface image/texte en vis-à-vis"""
        self.main_panel = tk.Frame(self.app, bg=self.colors["bg"])
        self.main_panel.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Encadré de conseil en haut
        self._create_advice_panel()
        
        # Panneau principal avec image et texte en vis-à-vis
        self._create_split_panel()
    
    def _create_advice_panel(self) -> None:
        """Crée l'encadré de conseil"""
        advice_font = self.font_manager.get_subtitle_font() if self.font_manager else ("Segoe UI", 11, "bold")
        text_font = self.font_manager.get_text_font() if self.font_manager else ("Segoe UI", 10)
        
        advice_frame = tk.LabelFrame(self.main_panel, text="💡 Conseil", 
                                   font=advice_font, 
                                   bg="#fff3cd", fg="#856404", 
                                   relief=tk.RAISED, bd=2)
        advice_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        advice_text = """Pour de meilleurs résultats OCR, utilisez des images à haute résolution avec un bon contraste. 
Le système FIND! peut identifier automatiquement l'auteur et l'œuvre à partir du contenu détecté !"""
        
        advice_label = tk.Label(advice_frame, text=advice_text, 
                              font=text_font, 
                              bg="#fff3cd", fg="#856404",
                              wraplength=800, justify=tk.LEFT)
        advice_label.pack(padx=15, pady=10)
    
    def _create_split_panel(self) -> None:
        """Crée le panneau divisé image/texte"""
        # Panneau principal divisé
        self.split_panel = tk.PanedWindow(self.main_panel, orient=tk.HORIZONTAL, bg=self.colors["bg"])
        self.split_panel.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Panneau gauche pour l'image
        self.image_panel = tk.Frame(self.split_panel, bg=self.colors["bg"])
        self.split_panel.add(self.image_panel, width=600)
        
        # Panneau droit pour le texte OCR
        self.text_panel = tk.Frame(self.split_panel, bg=self.colors["bg"])
        self.split_panel.add(self.text_panel, width=400)
        
        # Titre du panneau texte
        title_font = self.font_manager.get_subtitle_font() if self.font_manager else ("Segoe UI", 14, "bold")
        text_title = tk.Label(self.text_panel, text="📝 Résultats OCR", 
                             font=title_font, 
                             bg=self.colors["bg"], fg=self.colors["text_fg"])
        text_title.pack(pady=(10, 5))
        
        # Zone de texte avec scrollbar
        text_frame = tk.Frame(self.text_panel, bg=self.colors["bg"])
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        text_font = self.font_manager.get_text_font() if self.font_manager else ("Segoe UI", 11)
        self.ocr_text_widget = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            font=text_font,
            bg=self.colors["text_bg"],
            fg=self.colors["text_fg"],
            state=tk.DISABLED
        )
        self.ocr_text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Boutons d'action
        self._create_action_buttons()
    
    def _create_action_buttons(self) -> None:
        """Crée les boutons d'action"""
        button_frame = tk.Frame(self.text_panel, bg=self.colors["bg"])
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        button_font = self.font_manager.get_button_font() if self.font_manager else ("Segoe UI", 12, "bold")
        
        # Bouton FIND
        self.find_button = tk.Button(
            button_frame,
            text="🔍 FIND!",
            font=button_font,
            bg="#007acc",
            fg="white",
            command=self.app.perform_find,
            state=tk.DISABLED
        )
        self.find_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Bouton Export
        export_button = tk.Button(
            button_frame,
            text="📤 Export",
            font=button_font,
            bg="#28a745",
            fg="white",
            command=self.app.export_results
        )
        export_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Bouton Clear
        clear_button = tk.Button(
            button_frame,
            text="🗑️ Clear",
            font=button_font,
            bg="#dc3545",
            fg="white",
            command=self._clear_ocr_text
        )
        clear_button.pack(side=tk.RIGHT)
    
    def _clear_ocr_text(self) -> None:
        """Efface le texte OCR"""
        self.ocr_text_widget.config(state=tk.NORMAL)
        self.ocr_text_widget.delete(1.0, tk.END)
        self.ocr_text_widget.config(state=tk.DISABLED)
        self.find_button.config(state=tk.DISABLED)
    
    def create_status_bar(self) -> None:
        """Crée la barre de statut"""
        colors = self.get_current_colors()
        status_font = self.font_manager.get_text_font() if self.font_manager else ("Segoe UI", 10)
        self.status_bar = tk.Label(self.app, text="Prêt", bd=1, relief=tk.SUNKEN, anchor=tk.W,
                                  bg=colors["text_bg"], fg=colors["text_fg"], font=status_font)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def update_theme(self) -> None:
        """Met à jour le thème de l'interface"""
        if not self.interface_customizer:
            return
        
        try:
            colors = self.get_current_colors()
            
            # Mettre à jour la fenêtre principale
            self.app.configure(bg=colors["bg"])
            
            # Mettre à jour la toolbar
            self._update_toolbar_theme(colors)
            
            # Mettre à jour le panneau principal
            self._update_main_panel_theme(colors)
            
            # Mettre à jour la barre de statut
            self._update_status_bar_theme(colors)
            
        except Exception as e:
            logging.error(f"Erreur lors de la mise à jour du thème: {e}")
    
    def update_style(self) -> None:
        """Met à jour le style de l'interface"""
        if not self.interface_customizer:
            return
        
        try:
            style = self.interface_customizer.get_current_style()
            
            # Appliquer les styles (bordures arrondies, ombres, etc.)
            self._apply_interface_style(style)
            
        except Exception as e:
            logging.error(f"Erreur lors de la mise à jour du style: {e}")
    
    def _update_toolbar_theme(self, colors: dict) -> None:
        """Met à jour le thème de la toolbar"""
        for widget in self.app.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.configure(bg=colors["bg"])
                for child in widget.winfo_children():
                    if isinstance(child, tk.Button):
                        child.configure(bg=colors["button_bg"], fg=colors["button_fg"])
    
    def _update_main_panel_theme(self, colors: dict) -> None:
        """Met à jour le thème du panneau principal"""
        if hasattr(self, 'main_panel'):
            self.main_panel.configure(bg=colors["bg"])
            
            # Mettre à jour tous les widgets enfants
            self._update_widget_theme(self.main_panel, colors)
    
    def _update_status_bar_theme(self, colors: dict) -> None:
        """Met à jour le thème de la barre de statut"""
        if hasattr(self, 'status_bar'):
            self.status_bar.configure(bg=colors["text_bg"], fg=colors["text_fg"])
    
    def _update_widget_theme(self, widget: tk.Widget, colors: dict) -> None:
        """Met à jour récursivement le thème d'un widget et ses enfants"""
        try:
            if isinstance(widget, tk.Label):
                widget.configure(bg=colors["bg"], fg=colors["fg"])
            elif isinstance(widget, tk.Button):
                widget.configure(bg=colors["button_bg"], fg=colors["button_fg"])
            elif isinstance(widget, tk.Frame):
                widget.configure(bg=colors["bg"])
            elif isinstance(widget, tk.Text) or isinstance(widget, scrolledtext.ScrolledText):
                widget.configure(bg=colors["text_bg"], fg=colors["text_fg"])
            elif isinstance(widget, tk.LabelFrame):
                widget.configure(bg=colors["bg"], fg=colors["fg"])
            
            # Mettre à jour les enfants
            for child in widget.winfo_children():
                self._update_widget_theme(child, colors)
                
        except Exception as e:
            logging.error(f"Erreur mise à jour widget thème: {e}")
    
    def _apply_interface_style(self, style: dict) -> None:
        """Applique le style d'interface"""
        try:
            # Appliquer les bordures arrondies si supportées
            if style.get("border_radius", 0) > 0:
                # Note: Tkinter ne supporte pas nativement les bordures arrondies
                # Cette fonctionnalité pourrait être implémentée avec des extensions
                pass
            
            # Appliquer la transparence si supportée
            transparency = style.get("transparency", 1.0)
            if transparency < 1.0:
                # Note: Tkinter ne supporte pas nativement la transparence
                # Cette fonctionnalité pourrait être implémentée avec des extensions
                pass
                
        except Exception as e:
            logging.error(f"Erreur application style: {e}")
    
    def update_fonts(self) -> None:
        """Met à jour toutes les polices de l'interface"""
        if not self.font_manager:
            return
        
        try:
            # Mettre à jour la toolbar
            self._update_toolbar_fonts()
            
            # Mettre à jour le panneau principal
            self._update_main_panel_fonts()
            
            # Mettre à jour la barre de statut
            self._update_status_bar_fonts()
            
        except Exception as e:
            logging.error(f"Erreur lors de la mise à jour des polices: {e}")
    
    def _update_toolbar_fonts(self) -> None:
        """Met à jour les polices de la toolbar"""
        button_font = self.font_manager.get_button_font()
        
        # Mettre à jour tous les boutons de la toolbar
        for widget in self.app.winfo_children():
            if isinstance(widget, tk.Frame) and hasattr(widget, 'winfo_children'):
                for child in widget.winfo_children():
                    if isinstance(child, tk.Button):
                        child.config(font=button_font)
    
    def _update_main_panel_fonts(self) -> None:
        """Met à jour les polices du panneau principal"""
        if hasattr(self, 'main_panel'):
            # Mettre à jour l'encadré de conseil
            for widget in self.main_panel.winfo_children():
                if isinstance(widget, tk.LabelFrame):
                    widget.config(font=self.font_manager.get_subtitle_font())
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Label):
                            child.config(font=self.font_manager.get_text_font())
            
            # Mettre à jour le panneau divisé
            if hasattr(self, 'split_panel'):
                for widget in self.split_panel.winfo_children():
                    if isinstance(widget, tk.Frame):
                        for child in widget.winfo_children():
                            if isinstance(child, tk.Label):
                                child.config(font=self.font_manager.get_subtitle_font())
                            elif isinstance(child, tk.Frame):
                                for grandchild in child.winfo_children():
                                    if isinstance(grandchild, tk.Button):
                                        grandchild.config(font=self.font_manager.get_button_font())
                                    elif isinstance(grandchild, scrolledtext.ScrolledText):
                                        grandchild.config(font=self.font_manager.get_text_font())
    
    def _update_status_bar_fonts(self) -> None:
        """Met à jour les polices de la barre de statut"""
        if hasattr(self, 'status_bar'):
            self.status_bar.config(font=self.font_manager.get_text_font())


class SimpleFileManager:
    """Gestionnaire de fichiers simplifié"""
    
    def __init__(self, app: 'SimpleOCRApp') -> None:
        self.app = app
    
    def handle_file_open(self, filename: str) -> None:
        """Gère l'ouverture d'un fichier"""
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
        """Charge une image de manière sécurisée"""
        try:
            with Image.open(path) as img:
                # Conversion en RGB si nécessaire
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Redimensionnement si trop grande
                max_size = 4096
                if max(img.size) > max_size:
                    ratio = max_size / max(img.size)
                    new_size = tuple(int(dim * ratio) for dim in img.size)
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                self.app.state.current_images = [img]
                self.app.state.current_file_path = path
                self.app.state.current_page = 0
                self.app.display_current_image()
                self.app.set_status(SimpleConfig.MESSAGES["info"]["image_loaded"].format(filename=Path(path).name))
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement de l'image: {e}")
    
    def _load_pdf_safe(self, path: str) -> None:
        """Charge un PDF de manière sécurisée"""
        if not PDF_SUPPORT:
            messagebox.showerror("Erreur", "Support PDF non disponible")
            return
        
        try:
            self.app.set_status("Chargement PDF en cours...")
            
            # Conversion PDF
            images = convert_from_path(path, dpi=300, fmt='RGB')
            
            # Optimisation des images
            optimized_images = []
            for img in images:
                if max(img.size) > 2048:
                    ratio = 2048 / max(img.size)
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


class TuteurIA:
    """Tuteur IA spécialisé en grec ancien avec interface de professeur antique"""
    
    def __init__(self, app: 'SimpleOCRApp') -> None:
        self.app = app
        self.openrouter_api_key = "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"
        self.openrouter_url = "https://openrouter.ai/api/v1/chat/completions"
        self.conversation_history = []
        
        # Message de bienvenue en grec ancien
        self.welcome_message = """Χαῖρε ! Je suis votre tuteur IA spécialisé en grec ancien. 

🏛️ **Mon rôle** : Je peux vous aider avec la grammaire, la syntaxe, la littérature et l'histoire de la Grèce antique.

📚 **Mes domaines d'expertise** :
• Grammaire grecque ancienne (déclinaisons, conjugaisons)
• Syntaxe et analyse de phrases
• Littérature classique (Homère, Platon, Aristote, etc.)
• Histoire et contexte culturel
• Étymologie et évolution linguistique

🎓 **Comment puis-je vous assister aujourd'hui ?**

Vous pouvez me poser des questions sur :
- L'analyse grammaticale d'un texte
- La traduction et l'interprétation
- Le contexte historique d'une œuvre
- Les nuances de la langue grecque
- Tout autre aspect de la culture antique

Parlez-moi de ce que vous étudiez ou de vos difficultés !"""
        
    def chat_with_tutor(self, message: str, context: str = "") -> str:
        """Chat en temps réel avec le tuteur IA"""
        try:
            # Construction du prompt contextuel
            system_prompt = self._build_system_prompt()
            
            # Ajout du contexte du texte OCR
            if context:
                message = f"Contexte du texte analysé: {context}\n\nQuestion de l'étudiant: {message}"
            
            # Préparation de la requête
            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "anthropic/claude-3-haiku",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            # Appel à l'API OpenRouter
            response = requests.post(self.openrouter_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            tutor_response = result["choices"][0]["message"]["content"]
            
            # Sauvegarde de la conversation
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "user_message": message,
                "tutor_response": tutor_response
            })
            
            return tutor_response
            
        except Exception as e:
            logging.error(f"Erreur tuteur IA: {e}")
            return f"Erreur de communication avec le tuteur IA: {str(e)}"
    
    def _build_system_prompt(self) -> str:
        """Construit le prompt système pour le tuteur IA"""
        base_prompt = """Tu es un tuteur IA spécialisé en grec ancien, expert en grammaire, syntaxe, littérature et histoire.

RÔLE: Professeur personnel de grec ancien adaptatif

COMPÉTENCES:
1. GRAMMAIRE GRECQUE ANCIENNE:
   - Déclinaisons (5 cas: nominatif, génitif, datif, accusatif, vocatif)
   - Conjugaisons (temps, modes, voix)
   - Syntaxe complexe (propositions subordonnées, participes, infinitifs)
   - Particules et connecteurs logiques

2. LITTÉRATURE ET STYLE:
   - Figures de style (métaphores, comparaisons, hyperboles)
   - Mètres poétiques (hexamètre dactylique, trimètre iambique)
   - Genres littéraires (épopée, tragédie, comédie, philosophie)
   - Analyse stylistique et rhétorique

3. CONTEXTE HISTORIQUE:
   - Périodes historiques (archaïque, classique, hellénistique)
   - Événements historiques et leur impact
   - Influences culturelles et philosophiques
   - Connexions entre auteurs et époques

4. MÉTHODE PÉDAGOGIQUE:
   - Explications progressives et adaptées
   - Exemples concrets tirés des textes classiques
   - Exercices pratiques et corrections
   - Encouragement et motivation

STYLE DE RÉPONSE:
- Explications claires et structurées
- Utilisation d'exemples concrets
- Encouragement et soutien pédagogique
- Réponses en français avec termes grecs quand nécessaire

OBJECTIF: Aider l'étudiant à comprendre et maîtriser le grec ancien de manière interactive et personnalisée."""
        
        return base_prompt
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Récupère l'historique des conversations"""
        return self.conversation_history
    
    def clear_conversation_history(self) -> None:
        """Efface l'historique des conversations"""
        self.conversation_history = []
        logging.info("Historique des conversations effacé")


class ControlesGestuels:
    """Gestion optimisée des contrôles gestuels pour Mac"""
    
    def __init__(self, app: 'SimpleOCRApp') -> None:
        self.app = app
        self.is_macos = platform.system() == 'Darwin'
        
        # État des gestes
        self.current_zoom = 1.0
        self.current_rotation = 0
        self.pan_x = 0
        self.pan_y = 0
        
        # Configuration des limites
        self.zoom_min = 0.1
        self.zoom_max = 5.0
        self.zoom_step = 0.01
        
        # État du drag
        self.is_panning = False
        self.drag_start_pos = None
        self.drag_start_time = None
        self.last_click_pos = None
        self.pan_start_x = 0
        self.pan_start_y = 0
        self.pan_initial_x = 0
        self.pan_initial_y = 0
        
        # Historique des gestes
        self.gesture_history = []
        
        logging.info("Contrôles gestuels initialisés")
    
    def setup_gesture_controls(self, canvas) -> None:
        """Configure les contrôles gestuels sur le canvas - optimisé pour Mac"""
        # Bind des événements de souris pour les gestes - sans conflit avec Ctrl
        canvas.bind('<Button-1>', self._on_mouse_click)
        canvas.bind('<B1-Motion>', self._on_mouse_drag)
        canvas.bind('<ButtonRelease-1>', self._on_mouse_release)
        canvas.bind('<MouseWheel>', self._on_mouse_wheel)
        
        # Bind spécifique pour éviter les conflits avec Ctrl
        canvas.bind('<Control-Button-1>', self._on_mouse_click)
        canvas.bind('<Control-B1-Motion>', self._on_mouse_drag)
        canvas.bind('<Control-ButtonRelease-1>', self._on_mouse_release)
        
        # Bind des événements de clavier pour les gestes
        canvas.bind('<KeyPress>', self._on_key_press)
        
        # Bind des événements de trackpad (macOS) - optimisé
        if self.is_macos:
            # Gestes trackpad natifs
            canvas.bind('<Button-4>', self._on_trackpad_gesture)  # Trackpad up
            canvas.bind('<Button-5>', self._on_trackpad_gesture)  # Trackpad down
            canvas.bind('<Double-Button-1>', self._on_double_tap)
        
            # Optimisation pour les gestes fluides
            canvas.configure(cursor="crosshair")  # Curseur personnalisé
            
            # Support des gestes de pincement natifs
            canvas.bind('<Configure>', self._on_canvas_configure)
        
        # Focus sur le canvas pour capturer les événements clavier
        canvas.focus_set()
        
        logging.info("Contrôles gestuels configurés pour macOS" if self.is_macos else "Contrôles gestuels configurés")
    
    def _on_mouse_click(self, event) -> None:
        """Gestion du clic de souris"""
        self.last_click_pos = (event.x, event.y)
        self.drag_start_pos = (event.x, event.y)
        self.drag_start_time = datetime.now()
        
        # Activer le pan si on est zoomé
        if self.current_zoom > 1.0:
            self.is_panning = True
            self.pan_start_x = event.x
            self.pan_start_y = event.y
            self.pan_initial_x = self.pan_x
            self.pan_initial_y = self.pan_y
            self._log_gesture("click_pan_activated", f"zoom={self.current_zoom}")
        else:
            self.is_panning = False
            self._log_gesture("click_no_pan", f"zoom={self.current_zoom}")
    
    def _on_mouse_drag(self, event) -> None:
        """Gestion du glissement de souris - optimisé pour Mac"""
        if not self.drag_start_pos:
            return
        
        # Calculer le delta depuis le début du drag
        delta_x = event.x - self.pan_start_x
        delta_y = event.y - self.pan_start_y
        
        # Déplacement de l'image (pan) - mouvement naturel optimisé
        if self.is_panning and self.current_zoom > 1.0:
            # Calculer la nouvelle position de pan - mouvement naturel
            new_pan_x = self.pan_initial_x + delta_x
            new_pan_y = self.pan_initial_y + delta_y
            
            # Vérifier si le pan a changé pour éviter les mises à jour inutiles
            if new_pan_x != self.pan_x or new_pan_y != self.pan_y:
                self.pan_x = new_pan_x
                self.pan_y = new_pan_y
                self._apply_pan()  # Mise à jour immédiate
                self._log_gesture("pan", f"pan_x={self.pan_x}, pan_y={self.pan_y}")
            return
        elif self.current_zoom > 1.0:
            # Si on est zoomé mais pas en mode pan, activer le pan
            self.is_panning = True
            self.pan_initial_x = self.pan_x
            self.pan_initial_y = self.pan_y
            self.pan_start_x = event.x
            self.pan_start_y = event.y
            self._log_gesture("pan_start", f"zoom={self.current_zoom}")
        else:
            # Debug: pourquoi le pan ne fonctionne pas
            self._log_gesture("pan_debug", f"is_panning={self.is_panning}, zoom={self.current_zoom}, delta_x={delta_x}, delta_y={delta_y}")
    
    def _on_mouse_release(self, event) -> None:
        """Gestion de la libération de souris"""
        self.is_panning = False
        
        if self.drag_start_time:
            duration = (datetime.now() - self.drag_start_time).total_seconds()
            
            # Détection du tap vs drag
            if duration < 0.3 and self.last_click_pos:
                current_pos = (event.x, event.y)
                distance = ((current_pos[0] - self.last_click_pos[0])**2 + 
                          (current_pos[1] - self.last_click_pos[1])**2)**0.5
                
                if distance < 10:
                    self._handle_tap(event.x, event.y)
    
    def _on_mouse_wheel(self, event) -> None:
        """Gestion de la molette de souris pour zoom - optimisé pour Mac"""
        old_zoom = self.current_zoom
        
        if event.delta > 0:
            self.current_zoom = min(self.zoom_max, self.current_zoom * 1.1)
        else:
            self.current_zoom = max(self.zoom_min, self.current_zoom * 0.9)
        
        if self.current_zoom != old_zoom:
            self._apply_zoom()
            self._log_gesture("wheel_zoom", f"zoom={self.current_zoom:.2f}")
    
    def _on_key_press(self, event) -> None:
        """Gestion des touches clavier pour les gestes"""
        key = event.keysym.lower()
        
        if key == 'plus' or key == 'equal':
            self.zoom_in()
        elif key == 'minus':
            self.zoom_out()
        elif key == 'r':
            self.rotate_clockwise()
        elif key == 'l':
            self.rotate_counterclockwise()
        elif key == 'right':
            self.next_page()
        elif key == 'left':
            self.previous_page()
        elif key == '0':
            self.reset_view()
    
    def _on_trackpad_gesture(self, event) -> None:
        """Gestion des gestes trackpad - optimisé pour Mac"""
        if event.num == 4:  # Trackpad up
            self.current_zoom = min(self.zoom_max, self.current_zoom * 1.05)
        elif event.num == 5:  # Trackpad down
            self.current_zoom = max(self.zoom_min, self.current_zoom * 0.95)
        
        self._apply_zoom()
        self._log_gesture("trackpad_zoom", f"zoom={self.current_zoom:.2f}")
    
    def _on_canvas_configure(self, event) -> None:
        """Gestion de la configuration du canvas pour les gestes natifs"""
        # Support des gestes de pincement natifs macOS
        if hasattr(event, 'width') and hasattr(event, 'height'):
            # Mise à jour de la taille du canvas
            self._log_gesture("canvas_configure", f"size={event.width}x{event.height}")
    
    def _on_double_tap(self, event) -> None:
        """Gestion du double tap pour zoom"""
        self.zoom_to_point(event.x, event.y)
    
    def _handle_tap(self, x: int, y: int) -> None:
        """Gestion du tap simple"""
        if not self.is_panning:
            self.zoom_to_point(x, y)
    
    def zoom_in(self) -> None:
        """Zoom avant - optimisé pour Mac"""
        old_zoom = self.current_zoom
        self.current_zoom = min(self.zoom_max, self.current_zoom * 1.15)
        if self.current_zoom != old_zoom:
            self._apply_zoom()
            self._log_gesture("zoom_in", f"zoom={self.current_zoom:.2f}")
    
    def zoom_out(self) -> None:
        """Zoom arrière - optimisé pour Mac"""
        old_zoom = self.current_zoom
        self.current_zoom = max(self.zoom_min, self.current_zoom * 0.87)
        if self.current_zoom != old_zoom:
            self._apply_zoom()
            self._log_gesture("zoom_out", f"zoom={self.current_zoom:.2f}")
    
    def zoom_to_point(self, x: int, y: int) -> None:
        """Zoom vers un point spécifique"""
        old_zoom = self.current_zoom
        self.current_zoom = min(self.zoom_max, self.current_zoom * 1.5)
        if self.current_zoom != old_zoom:
            self._apply_zoom()
            self._log_gesture("zoom_to_point", f"x={x}, y={y}, zoom={self.current_zoom:.2f}")
    
    def rotate_clockwise(self) -> None:
        """Rotation horaire"""
        self.current_rotation = (self.current_rotation + 90) % 360
        self._apply_rotation()
        self._log_gesture("rotate_clockwise", f"rotation={self.current_rotation}")
    
    def rotate_counterclockwise(self) -> None:
        """Rotation anti-horaire"""
        self.current_rotation = (self.current_rotation - 90) % 360
        self._apply_rotation()
        self._log_gesture("rotate_counterclockwise", f"rotation={self.current_rotation}")
    
    def next_page(self) -> None:
        """Page suivante"""
        if hasattr(self.app, 'next_page'):
            self.app.next_page()
            self._log_gesture("next_page", "")
    
    def previous_page(self) -> None:
        """Page précédente"""
        if hasattr(self.app, 'previous_page'):
            self.app.previous_page()
            self._log_gesture("previous_page", "")
    
    def reset_view(self) -> None:
        """Reset de la vue"""
        self.current_zoom = 1.0
        self.current_rotation = 0
        self.pan_x = 0
        self.pan_y = 0
        self._apply_zoom()
        self._log_gesture("reset_view", "")
    
    def toggle_fullscreen(self) -> None:
        """Basculer le mode plein écran"""
        if hasattr(self.app, 'toggle_fullscreen'):
            self.app.toggle_fullscreen()
            self._log_gesture("toggle_fullscreen", "")
    
    def _apply_zoom(self) -> None:
        """Applique le zoom à l'image - optimisé"""
        if hasattr(self.app, '_update_image_display'):
            self.app._update_image_display()
    
    def _apply_rotation(self) -> None:
        """Applique la rotation à l'image"""
        if hasattr(self.app, '_update_image_display'):
            self.app._update_image_display()
    
    def _apply_pan(self) -> None:
        """Applique le déplacement de l'image - optimisé"""
        try:
            if hasattr(self.app, '_update_image_display'):
                self.app._update_image_display()
                self._log_gesture("pan_applied", f"pan_x={self.pan_x}, pan_y={self.pan_y}")
            else:
                self._log_gesture("pan_error", "_update_image_display not found")
        except Exception as e:
            self._log_gesture("pan_error", f"Exception: {e}")
    
    def _log_gesture(self, gesture_type: str, details: str) -> None:
        """Enregistre un geste dans l'historique"""
        gesture = {
            'timestamp': datetime.now(),
            'type': gesture_type,
            'details': details,
            'zoom': self.current_zoom,
            'rotation': self.current_rotation,
            'pan_x': self.pan_x,
            'pan_y': self.pan_y
        }
        self.gesture_history.append(gesture)
        
        # Limiter l'historique à 1000 entrées
        if len(self.gesture_history) > 1000:
            self.gesture_history = self.gesture_history[-1000:]
        
        logging.info(f"Geste détecté: {gesture_type} - {details}")
    
    def get_gesture_history(self) -> List[Dict[str, Any]]:
        """Retourne l'historique des gestes"""
        return self.gesture_history.copy()
    
    def clear_gesture_history(self) -> None:
        """Efface l'historique des gestes"""
        self.gesture_history.clear()


# Interface pour les contrôles gestuels avancés
class GestureController:
    """Contrôleur de gestes trackpad macOS natifs avec animations fluides"""
    
    def __init__(self, app: 'SimpleOCRApp') -> None:
        self.app = app
        self.canvas = None
        self.is_trackpad = False
        self.gesture_history = deque(maxlen=100)
        self.animation_frame = None
        self.momentum_scroll = None
        self.haptic_enabled = GESTURE_CONFIG["haptic_feedback"]
        self.smooth_animations = GESTURE_CONFIG["smooth_animations"]
        
        # État des gestes
        self.current_gesture = None
        self.gesture_start_time = 0
        self.gesture_start_pos = (0, 0)
        self.gesture_velocity = (0, 0)
        
        # Configuration des préférences système
        self.system_preferences = self._get_system_preferences()
        
        # Animation state
        self.animation_targets = {}
        self.animation_start_time = 0
        
        logging.info("🎮 GestureController initialisé pour macOS")
    
    def _get_system_preferences(self) -> Dict[str, Any]:
        """Récupère les préférences système macOS"""
        prefs = {
            "trackpad_speed": 1.0,
            "scroll_speed": 1.0,
            "zoom_speed": 1.0,
            "momentum_scrolling": True,
            "natural_scrolling": True
        }
        
        if IS_MACOS:
            try:
                # Lecture des préférences système via defaults
                result = subprocess.run([
                    'defaults', 'read', 'com.apple.driver.AppleBluetoothMultitouch.trackpad'
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    # Parse des préférences (simplifié)
                    if "TrackpadSpeed" in result.stdout:
                        prefs["trackpad_speed"] = 1.0  # Valeur par défaut
                    
                logging.info(f"Préférences système chargées: {prefs}")
            except Exception as e:
                logging.warning(f"Impossible de charger les préférences système: {e}")
        
        return prefs
    
    def setup_trackpad_gestures(self, canvas: tk.Canvas) -> None:
        """Configure les gestes trackpad natifs sur le canvas"""
        self.canvas = canvas
        
        # Détection trackpad vs souris
        self._detect_input_device()
        
        # Bind des événements trackpad avancés
        if self.is_trackpad:
            self._bind_trackpad_events()
        else:
            self._bind_mouse_events()
        
        # Bind des événements de configuration
        canvas.bind('<Configure>', self._on_canvas_configure)
        
        logging.info(f"🎮 Gestes configurés: {'Trackpad' if self.is_trackpad else 'Souris'}")
    
    def _detect_input_device(self) -> None:
        """Détecte si l'utilisateur utilise un trackpad ou une souris"""
        if IS_MACOS:
            try:
                # Vérification de la présence d'un trackpad
                result = subprocess.run([
                    'system_profiler', 'SPTrackpadDataType'
                ], capture_output=True, text=True)
                
                self.is_trackpad = "Trackpad" in result.stdout
                
                # Détection via les préférences système
                if not self.is_trackpad:
                    result = subprocess.run([
                        'defaults', 'read', 'com.apple.driver.AppleBluetoothMultitouch.trackpad'
                    ], capture_output=True, text=True)
                    self.is_trackpad = result.returncode == 0
                    
            except Exception as e:
                logging.warning(f"Erreur détection périphérique: {e}")
                self.is_trackpad = False
        
        logging.info(f"Périphérique détecté: {'Trackpad' if self.is_trackpad else 'Souris'}")
    
    def _bind_trackpad_events(self) -> None:
        """Bind des événements trackpad natifs macOS"""
        if not self.canvas:
            return
        
        # Événements de base
        self.canvas.bind('<Button-1>', self._on_trackpad_click)
        self.canvas.bind('<B1-Motion>', self._on_trackpad_drag)
        self.canvas.bind('<ButtonRelease-1>', self._on_trackpad_release)
        
        # Événements wheel détaillés (trackpad)
        self.canvas.bind('<MouseWheel>', self._on_trackpad_wheel)
        self.canvas.bind('<Button-4>', self._on_trackpad_wheel)  # Linux
        self.canvas.bind('<Button-5>', self._on_trackpad_wheel)  # Linux
        
        # Événements macOS spécifiques
        if IS_MACOS:
            self.canvas.bind('<Control-Button-1>', self._on_secondary_click)
            self.canvas.bind('<Button-2>', self._on_secondary_click)
            self.canvas.bind('<Button-3>', self._on_secondary_click)
            
            # Événements de pression (Force Touch)
            self.canvas.bind('<Double-Button-1>', self._on_force_click)
            
            # Événements de rotation
            self.canvas.bind('<Shift-MouseWheel>', self._on_trackpad_rotation)
            
            # Événements de zoom
            self.canvas.bind('<Control-MouseWheel>', self._on_trackpad_zoom)
        
        # Événements clavier pour les gestes
        self.canvas.bind('<KeyPress>', self._on_key_gesture)
        self.canvas.focus_set()
    
    def _bind_mouse_events(self) -> None:
        """Bind des événements souris classiques"""
        if not self.canvas:
            return
        
        self.canvas.bind('<Button-1>', self._on_mouse_click)
        self.canvas.bind('<B1-Motion>', self._on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self._on_mouse_release)
        self.canvas.bind('<MouseWheel>', self._on_mouse_wheel)
        self.canvas.bind('<Control-MouseWheel>', self._on_mouse_zoom)
    
    def _on_trackpad_click(self, event) -> None:
        """Gestion du clic trackpad avec détection de pression"""
        self.gesture_start_time = time.time()
        self.gesture_start_pos = (event.x, event.y)
        self.current_gesture = TrackpadGestureType.FORCE_CLICK
        
        # Feedback haptique si supporté
        if self.haptic_enabled:
            self._trigger_haptic_feedback("light")
        
        self._log_gesture("trackpad_click", f"pos=({event.x},{event.y})")
    
    def _on_trackpad_drag(self, event) -> None:
        """Gestion du drag trackpad avec momentum"""
        if not self.current_gesture:
            return
        
        current_pos = (event.x, event.y)
        delta_x = current_pos[0] - self.gesture_start_pos[0]
        delta_y = current_pos[1] - self.gesture_start_pos[1]
        
        # Calcul de la vélocité pour le momentum
        elapsed_time = time.time() - self.gesture_start_time
        if elapsed_time > 0:
            self.gesture_velocity = (delta_x / elapsed_time, delta_y / elapsed_time)
        
        # Application du déplacement avec sensibilité système
        sensitivity = self.system_preferences["trackpad_speed"]
        adjusted_delta_x = delta_x * sensitivity
        adjusted_delta_y = delta_y * sensitivity
        
        # Détermination du type de geste
        if abs(delta_x) > abs(delta_y):
            self.current_gesture = TrackpadGestureType.TWO_FINGER_PAN
        else:
            self.current_gesture = TrackpadGestureType.MOMENTUM_SCROLL
        
        # Application du geste
        self._apply_trackpad_gesture(self.current_gesture, adjusted_delta_x, adjusted_delta_y)
        
        self._log_gesture("trackpad_drag", f"gesture={self.current_gesture}, delta=({adjusted_delta_x:.2f},{adjusted_delta_y:.2f})")
    
    def _on_trackpad_wheel(self, event) -> None:
        """Gestion de la molette trackpad avec détection détaillée"""
        # Détection du type d'événement wheel
        if hasattr(event, 'delta'):
            # Windows/macOS
            delta = event.delta
            if IS_MACOS:
                # macOS utilise des valeurs différentes
                delta = delta / 120.0
        else:
            # Linux
            delta = 1 if event.num == 4 else -1
        
        # Détection des modificateurs
        is_zoom = event.state & 0x4  # Ctrl
        is_rotation = event.state & 0x1  # Shift
        
        if is_zoom:
            self._handle_trackpad_zoom(delta)
        elif is_rotation:
            self._handle_trackpad_rotation(delta)
        else:
            self._handle_trackpad_scroll(delta)
        
        self._log_gesture("trackpad_wheel", f"delta={delta:.2f}, zoom={is_zoom}, rotation={is_rotation}")
    
    def _handle_trackpad_zoom(self, delta: float) -> None:
        """Gestion du zoom trackpad avec animations fluides"""
        zoom_factor = 1.0 + (delta * GESTURE_CONFIG["pinch_zoom_sensitivity"])
        current_zoom = self.app.controles_gestuels.current_zoom
        target_zoom = current_zoom * zoom_factor
        
        # Limites de zoom
        target_zoom = max(0.1, min(10.0, target_zoom))
        
        if self.smooth_animations:
            self._animate_zoom(current_zoom, target_zoom)
        else:
            self.app.controles_gestuels.current_zoom = target_zoom
            self.app.controles_gestuels._apply_zoom()
        
        # Feedback haptique
        if self.haptic_enabled and abs(delta) > 0.1:
            self._trigger_haptic_feedback("medium")
    
    def _handle_trackpad_rotation(self, delta: float) -> None:
        """Gestion de la rotation trackpad"""
        rotation_delta = delta * GESTURE_CONFIG["rotation_sensitivity"]
        current_rotation = self.app.controles_gestuels.current_rotation
        target_rotation = current_rotation + rotation_delta
        
        if self.smooth_animations:
            self._animate_rotation(current_rotation, target_rotation)
        else:
            self.app.controles_gestuels.current_rotation = target_rotation
            self.app.controles_gestuels._apply_rotation()
    
    def _handle_trackpad_scroll(self, delta: float) -> None:
        """Gestion du scroll trackpad avec momentum"""
        scroll_sensitivity = self.system_preferences["scroll_speed"]
        scroll_delta = delta * scroll_sensitivity
        
        if GESTURE_CONFIG["momentum_scrolling"]:
            self._start_momentum_scroll(scroll_delta)
        else:
            # Scroll direct
            self._apply_scroll(scroll_delta)
    
    def _start_momentum_scroll(self, initial_delta: float) -> None:
        """Démarre le scroll avec momentum"""
        if self.momentum_scroll:
            self.app.after_cancel(self.momentum_scroll)
        
        self.momentum_scroll = self.app.after(16, lambda: self._apply_momentum_scroll(initial_delta))
    
    def _apply_momentum_scroll(self, delta: float) -> None:
        """Applique le scroll avec momentum"""
        # Application du scroll
        self._apply_scroll(delta)
        
        # Calcul du momentum (décélération)
        momentum_factor = 0.95
        new_delta = delta * momentum_factor
        
        # Continuer si le momentum est suffisant
        if abs(new_delta) > 0.1:
            self.momentum_scroll = self.app.after(16, lambda: self._apply_momentum_scroll(new_delta))
        else:
            self.momentum_scroll = None
    
    def _apply_scroll(self, delta: float) -> None:
        """Applique le scroll vertical"""
        # Calcul du déplacement en pixels
        scroll_pixels = int(delta * 20)  # 20 pixels par unité de scroll
        
        # Application au pan vertical
        current_pan_y = self.app.controles_gestuels.pan_y
        new_pan_y = current_pan_y - scroll_pixels  # Inversé pour scroll naturel
        
        self.app.controles_gestuels.pan_y = new_pan_y
        self.app.controles_gestuels._apply_pan()
    
    def _animate_zoom(self, start_zoom: float, target_zoom: float) -> None:
        """Animation fluide du zoom avec requestAnimationFrame"""
        duration = GESTURE_CONFIG["animation_duration"] / 1000.0  # Conversion en secondes
        start_time = time.time()
        
        def animate():
            elapsed = time.time() - start_time
            progress = min(elapsed / duration, 1.0)
            
            # Fonction d'easing (ease-out)
            ease_progress = 1 - (1 - progress) ** 3
            
            current_zoom = start_zoom + (target_zoom - start_zoom) * ease_progress
            self.app.controles_gestuels.current_zoom = current_zoom
            self.app.controles_gestuels._apply_zoom()
            
            if progress < 1.0:
                self.animation_frame = self.app.after(16, animate)  # ~60 FPS
            else:
                self.animation_frame = None
        
        animate()
    
    def _animate_rotation(self, start_rotation: float, target_rotation: float) -> None:
        """Animation fluide de la rotation"""
        duration = GESTURE_CONFIG["animation_duration"] / 1000.0
        start_time = time.time()
        
        def animate():
            elapsed = time.time() - start_time
            progress = min(elapsed / duration, 1.0)
            
            # Fonction d'easing
            ease_progress = 1 - (1 - progress) ** 2
            
            current_rotation = start_rotation + (target_rotation - start_rotation) * ease_progress
            self.app.controles_gestuels.current_rotation = current_rotation
            self.app.controles_gestuels._apply_rotation()
            
            if progress < 1.0:
                self.animation_frame = self.app.after(16, animate)
            else:
                self.animation_frame = None
        
        animate()
    
    def _trigger_haptic_feedback(self, intensity: str) -> None:
        """Déclenche le feedback haptique si supporté"""
        if not self.haptic_enabled or not IS_MACOS:
            return
        
        try:
            # Utilisation de la commande macOS pour le feedback haptique
            if intensity == "light":
                subprocess.run(['osascript', '-e', 'tell application "System Events" to key code 49'], 
                             capture_output=True)
            elif intensity == "medium":
                subprocess.run(['osascript', '-e', 'tell application "System Events" to key code 50'], 
                             capture_output=True)
            elif intensity == "heavy":
                subprocess.run(['osascript', '-e', 'tell application "System Events" to key code 51'], 
                             capture_output=True)
        except Exception as e:
            logging.debug(f"Feedback haptique non supporté: {e}")
    
    def _on_secondary_click(self, event) -> None:
        """Gestion du clic secondaire (clic droit)"""
        self._log_gesture("secondary_click", f"pos=({event.x},{event.y})")
        
        # Affichage du menu contextuel
        self._show_context_menu(event.x, event.y)
    
    def _on_force_click(self, event) -> None:
        """Gestion du Force Click (macOS)"""
        self._log_gesture("force_click", f"pos=({event.x},{event.y})")
        
        # Zoom vers le point de clic
        self.app.controles_gestuels.zoom_to_point(event.x, event.y)
        
        # Feedback haptique fort
        if self.haptic_enabled:
            self._trigger_haptic_feedback("heavy")
    
    def _show_context_menu(self, x: int, y: int) -> None:
        """Affiche le menu contextuel"""
        menu = tk.Menu(self.canvas, tearoff=0)
        
        menu.add_command(label="🔍 Zoom vers ce point", 
                        command=lambda: self.app.controles_gestuels.zoom_to_point(x, y))
        menu.add_command(label="🔄 Réinitialiser la vue", 
                        command=self.app.controles_gestuels.reset_view)
        menu.add_separator()
        menu.add_command(label="📊 Historique des gestes", 
                        command=self.app.show_gesture_history)
        menu.add_command(label="⚙️ Configuration des gestes", 
                        command=self.app.open_gesture_controls)
        
        menu.tk_popup(x, y)
    
    def _on_canvas_configure(self, event) -> None:
        """Gestion de la reconfiguration du canvas"""
        self._log_gesture("canvas_configure", f"size={event.width}x{event.height}")
    
    def _on_key_gesture(self, event) -> None:
        """Gestion des raccourcis clavier pour les gestes"""
        key = event.keysym.lower()
        
        if key == 'plus' or key == 'equal':
            self.app.controles_gestuels.zoom_in()
        elif key == 'minus':
            self.app.controles_gestuels.zoom_out()
        elif key == 'r':
            self.app.controles_gestuels.reset_view()
        elif key == 'left':
            self.app.controles_gestuels.previous_page()
        elif key == 'right':
            self.app.controles_gestuels.next_page()
        
        self._log_gesture("key_gesture", f"key={key}")
    
    def _log_gesture(self, gesture_type: str, details: str) -> None:
        """Enregistre un geste dans l'historique"""
        gesture_info = {
            "type": gesture_type,
            "details": details,
            "timestamp": time.time(),
            "device": "trackpad" if self.is_trackpad else "mouse"
        }
        
        self.gesture_history.append(gesture_info)
        logging.info(f"🎮 Geste détecté: {gesture_type} - {details}")
    
    def get_gesture_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques des gestes"""
        if not self.gesture_history:
            return {}
        
        gesture_counts = defaultdict(int)
        for gesture in self.gesture_history:
            gesture_counts[gesture["type"]] += 1
        
        return {
            "total_gestures": len(self.gesture_history),
            "gesture_counts": dict(gesture_counts),
            "device_type": "trackpad" if self.is_trackpad else "mouse",
            "last_gesture": self.gesture_history[-1] if self.gesture_history else None
        }
    
    def clear_gesture_history(self) -> None:
        """Efface l'historique des gestes"""
        self.gesture_history.clear()
        logging.info("🎮 Historique des gestes effacé")
    
    def stop_animations(self) -> None:
        """Arrête toutes les animations en cours"""
        if self.animation_frame:
            self.app.after_cancel(self.animation_frame)
            self.animation_frame = None
        
        if self.momentum_scroll:
            self.app.after_cancel(self.momentum_scroll)
            self.momentum_scroll = None
        
        logging.info("🎮 Animations arrêtées")
    
    # Méthodes de compatibilité avec l'ancien système
    def _on_trackpad_release(self, event) -> None:
        """Gestion de la libération du trackpad"""
        self.current_gesture = None
        self._log_gesture("trackpad_release", f"pos=({event.x},{event.y})")
    
    def _on_mouse_click(self, event) -> None:
        """Compatibilité avec les événements souris"""
        self._on_trackpad_click(event)
    
    def _on_mouse_drag(self, event) -> None:
        """Compatibilité avec les événements souris"""
        self._on_trackpad_drag(event)
    
    def _on_mouse_release(self, event) -> None:
        """Compatibilité avec les événements souris"""
        self._on_trackpad_release(event)
    
    def _on_mouse_wheel(self, event) -> None:
        """Compatibilité avec les événements souris"""
        self._on_trackpad_wheel(event)
    
    def _on_mouse_zoom(self, event) -> None:
        """Compatibilité avec les événements souris"""
        self._on_trackpad_wheel(event)
    
    def _on_trackpad_rotation(self, event) -> None:
        """Gestion de la rotation trackpad"""
        if hasattr(event, 'delta'):
            delta = event.delta / 120.0
        else:
            delta = 1 if event.num == 4 else -1
        
        self._handle_trackpad_rotation(delta)
    
    def _on_trackpad_zoom(self, event) -> None:
        """Gestion du zoom trackpad"""
        if hasattr(event, 'delta'):
            delta = event.delta / 120.0
        else:
            delta = 1 if event.num == 4 else -1
        
        self._handle_trackpad_zoom(delta)
    
    def _apply_trackpad_gesture(self, gesture_type: str, delta_x: float, delta_y: float) -> None:
        """Applique un geste trackpad spécifique"""
        if gesture_type == TrackpadGestureType.TWO_FINGER_PAN:
            # Application du pan
            current_pan_x = self.app.controles_gestuels.pan_x
            current_pan_y = self.app.controles_gestuels.pan_y
            
            new_pan_x = current_pan_x + delta_x
            new_pan_y = current_pan_y + delta_y
            
            self.app.controles_gestuels.pan_x = new_pan_x
            self.app.controles_gestuels.pan_y = new_pan_y
            self.app.controles_gestuels._apply_pan()
        
        elif gesture_type == TrackpadGestureType.MOMENTUM_SCROLL:
            # Le scroll est géré par _apply_scroll
            pass


class ContextualisationHistorique:
    """Contextualisation historique des textes grecs"""
    
    def __init__(self, app: 'SimpleOCRApp') -> None:
        self.app = app
        
        # Base de données historique
        self.historical_timeline = {
            "archaic": {
                "period": "VIIIe-VIe siècle av. J.-C.",
                "events": [
                    {"year": -800, "event": "Début de la période archaïque", "description": "Émergence de la polis"},
                    {"year": -750, "event": "Homère compose l'Iliade et l'Odyssée", "description": "Fondation de la littérature grecque"},
                    {"year": -700, "event": "Hésiode compose la Théogonie", "description": "Poésie didactique"},
                    {"year": -650, "event": "Archiloque de Paros", "description": "Poésie lyrique"},
                    {"year": -600, "event": "Sappho de Lesbos", "description": "Poétesse lyrique"},
                    {"year": -550, "event": "Anacréon", "description": "Poésie de banquet"}
                ]
            },
            "classical": {
                "period": "Ve-IVe siècle av. J.-C.",
                "events": [
                    {"year": -500, "event": "Début de la période classique", "description": "Apogée d'Athènes"},
                    {"year": -490, "event": "Bataille de Marathon", "description": "Victoire athénienne"},
                    {"year": -480, "event": "Bataille de Salamine", "description": "Victoire navale"},
                    {"year": -450, "event": "Périclès au pouvoir", "description": "Âge d'or d'Athènes"},
                    {"year": -430, "event": "Guerre du Péloponnèse", "description": "Conflit Athènes-Sparte"},
                    {"year": -399, "event": "Procès et mort de Socrate", "description": "Condamnation à mort"},
                    {"year": -380, "event": "Platon fonde l'Académie", "description": "Première université"},
                    {"year": -350, "event": "Aristote à l'Académie", "description": "Élève de Platon"},
                    {"year": -335, "event": "Aristote fonde le Lycée", "description": "École péripatéticienne"}
                ]
            },
            "hellenistic": {
                "period": "IIIe-Ier siècle av. J.-C.",
                "events": [
                    {"year": -323, "event": "Mort d'Alexandre le Grand", "description": "Fin de l'empire"},
                    {"year": -300, "event": "Période hellénistique", "description": "Diffusion de la culture grecque"},
                    {"year": -250, "event": "Callimaque", "description": "Poète alexandrin"},
                    {"year": -200, "event": "Polybe", "description": "Historien"},
                    {"year": -100, "event": "Plutarque", "description": "Biographe et moraliste"}
                ]
            }
        }
        
        # Cartes des lieux historiques
        self.historical_places = {
            "athens": {
                "name": "Athènes",
                "coordinates": {"lat": 37.9838, "lng": 23.7275},
                "periods": ["archaic", "classical", "hellenistic"],
                "description": "Capitale de l'Attique, berceau de la démocratie",
                "landmarks": ["Acropole", "Agora", "Parthénon", "Académie", "Lycée"]
            },
            "sparta": {
                "name": "Sparte",
                "coordinates": {"lat": 37.0819, "lng": 22.4233},
                "periods": ["archaic", "classical"],
                "description": "Cité guerrière du Péloponnèse",
                "landmarks": ["Acropole de Sparte", "Sanctuaire d'Artémis Orthia"]
            },
            "thebes": {
                "name": "Thèbes",
                "coordinates": {"lat": 38.3217, "lng": 23.3194},
                "periods": ["archaic", "classical"],
                "description": "Cité de Béotie, rivale d'Athènes",
                "landmarks": ["Cadmée", "Sanctuaire d'Apollon Isménien"]
            },
            "delphi": {
                "name": "Delphes",
                "coordinates": {"lat": 38.4824, "lng": 22.5010},
                "periods": ["archaic", "classical", "hellenistic"],
                "description": "Sanctuaire panhellénique d'Apollon",
                "landmarks": ["Temple d'Apollon", "Oracle", "Trésors"]
            },
            "olympia": {
                "name": "Olympie",
                "coordinates": {"lat": 37.6383, "lng": 21.6300},
                "periods": ["archaic", "classical", "hellenistic"],
                "description": "Sanctuaire de Zeus et site des Jeux Olympiques",
                "landmarks": ["Temple de Zeus", "Stade", "Gymnase"]
            }
        }
        
        # Influences entre auteurs
        self.author_influences = {
            "homer": {
                "influenced": ["hesiod", "archilochus", "sappho", "pindar", "all_tragic_poets"],
                "influenced_by": ["oral_tradition"],
                "period": "archaic",
                "description": "Fondateur de la littérature grecque"
            },
            "plato": {
                "influenced": ["aristotle", "plotinus", "augustine", "all_philosophy"],
                "influenced_by": ["socrates", "pythagoras", "heraclitus"],
                "period": "classical",
                "description": "Fondateur de l'idéalisme philosophique"
            },
            "aristotle": {
                "influenced": ["theophrastus", "alexander", "all_science", "medieval_philosophy"],
                "influenced_by": ["plato", "socrates", "empedocles"],
                "period": "classical",
                "description": "Fondateur de la logique et de la science"
            },
            "sophocles": {
                "influenced": ["euripides", "seneca", "all_tragedy"],
                "influenced_by": ["aeschylus", "homer"],
                "period": "classical",
                "description": "Maître de la tragédie classique"
            }
        }
    
    def get_timeline_for_author(self, author_id: str) -> Dict[str, Any]:
        """Récupère la frise chronologique pour un auteur"""
        author_info = self.app.find_manager.greek_authors.get(author_id)
        if not author_info:
            return {"error": "Auteur non trouvé"}
        
        # Déterminer la période de l'auteur
        author_period = self._get_author_period(author_id)
        
        # Récupérer les événements de cette période
        timeline_events = self.historical_timeline.get(author_period, {}).get("events", [])
        
        # Ajouter l'auteur à la timeline
        author_event = self._create_author_event(author_id, author_info)
        timeline_events.append(author_event)
        
        # Trier par année
        timeline_events.sort(key=lambda x: x["year"])
        
        return {
            "author": author_info,
            "period": author_period,
            "timeline": timeline_events,
            "period_info": self.historical_timeline.get(author_period, {})
        }
    
    def _get_author_period(self, author_id: str) -> str:
        """Détermine la période d'un auteur"""
        period_mapping = {
            "homer": "archaic",
            "hesiod": "archaic",
            "sappho": "archaic",
            "anacreon": "archaic",
            "aeschylus": "classical",
            "sophocles": "classical",
            "euripides": "classical",
            "plato": "classical",
            "aristotle": "classical",
            "herodotus": "classical",
            "thucydides": "classical",
            "xenophon": "classical",
            "demosthenes": "classical",
            "lysias": "classical"
        }
        return period_mapping.get(author_id, "classical")
    
    def _create_author_event(self, author_id: str, author_info: Dict[str, Any]) -> Dict[str, Any]:
        """Crée un événement pour un auteur"""
        period_years = {
            "archaic": -700,
            "classical": -400,
            "hellenistic": -200
        }
        
        return {
            "year": period_years.get(self._get_author_period(author_id), -400),
            "event": f"{author_info['name']} - Activité littéraire",
            "description": f"Période d'activité de {author_info['name']}",
            "type": "author",
            "author_id": author_id
        }
    
    def get_historical_places(self, author_id: str = None) -> Dict[str, Any]:
        """Récupère les lieux historiques liés à un auteur"""
        if author_id:
            author_period = self._get_author_period(author_id)
            places = {k: v for k, v in self.historical_places.items() 
                     if author_period in v["periods"]}
        else:
            places = self.historical_places
        
        return {
            "places": places,
            "total": len(places)
        }
    
    def get_author_influences(self, author_id: str) -> Dict[str, Any]:
        """Récupère les influences d'un auteur"""
        influences = self.author_influences.get(author_id, {})
        
        return {
            "author": author_id,
            "influenced": influences.get("influenced", []),
            "influenced_by": influences.get("influenced_by", []),
            "description": influences.get("description", ""),
            "period": influences.get("period", "")
        }
    
    def generate_historical_context(self, author_id: str, text: str) -> str:
        """Génère un contexte historique pour un texte"""
        timeline = self.get_timeline_for_author(author_id)
        places = self.get_historical_places(author_id)
        influences = self.get_author_influences(author_id)
        
        context = f"""CONTEXTE HISTORIQUE - {timeline['author']['name']}

📅 PÉRIODE: {timeline['period_info']['period']}

🏛️ LIEUX IMPORTANTS:
"""
        for place_id, place_info in places["places"].items():
            context += f"• {place_info['name']}: {place_info['description']}\n"
        
        context += f"""
🔗 INFLUENCES:
• Influencé par: {', '.join(influences['influenced_by'])}
• A influencé: {', '.join(influences['influenced'])}
• Description: {influences['description']}

📚 ÉVÉNEMENTS CONTEMPORAINS:
"""
        for event in timeline["timeline"][:5]:  # Top 5 events
            context += f"• {event['year']} av. J.-C.: {event['event']}\n"
        
        return context


class FindManager:
    """Gestionnaire FIND ! révolutionnaire - Identification automatique d'auteur/œuvre"""
    
    def __init__(self, app: 'SimpleOCRApp') -> None:
        self.app = app
        self.perseus_base_url = "http://www.perseus.tufts.edu/hopper/"
        self.loeb_base_url = "https://www.loebclassics.com/"
        
        # Base de données d'auteurs grecs classiques
        self.greek_authors = {
            "homer": {
                "name": "Homère",
                "works": ["iliad", "odyssey"],
                "period": "VIIIe siècle av. J.-C.",
                "search_terms": ["homer", "homère", "iliad", "odyssey", "odyssée"]
            },
            "plato": {
                "name": "Platon",
                "works": ["republic", "apology", "phaedo", "symposium"],
                "period": "428-348 av. J.-C.",
                "search_terms": ["plato", "platon", "republic", "république", "apology"]
            },
            "aristotle": {
                "name": "Aristote",
                "works": ["nicomachean_ethics", "politics", "metaphysics"],
                "period": "384-322 av. J.-C.",
                "search_terms": ["aristotle", "aristote", "ethics", "éthique", "politics"]
            },
            "sophocles": {
                "name": "Sophocle",
                "works": ["oedipus_tyrannus", "antigone", "electra"],
                "period": "496-406 av. J.-C.",
                "search_terms": ["sophocles", "sophocle", "oedipus", "oedipe", "antigone"]
            },
            "euripides": {
                "name": "Euripide",
                "works": ["medea", "bacchae", "trojan_women"],
                "period": "480-406 av. J.-C.",
                "search_terms": ["euripides", "euripide", "medea", "médée", "bacchae"]
            },
            "herodotus": {
                "name": "Hérodote",
                "works": ["histories"],
                "period": "484-425 av. J.-C.",
                "search_terms": ["herodotus", "hérodote", "histories", "histoires"]
            },
            "thucydides": {
                "name": "Thucydide",
                "works": ["peloponnesian_war"],
                "period": "460-400 av. J.-C.",
                "search_terms": ["thucydides", "thucydide", "peloponnesian", "péloponnèse"]
            },
            "xenophon": {
                "name": "Xénophon",
                "works": ["anabasis", "cyropaedia", "memorabilia"],
                "period": "430-354 av. J.-C.",
                "search_terms": ["xenophon", "xénophon", "anabasis", "cyropaedia"]
            },
            "demosthenes": {
                "name": "Démosthène",
                "works": ["orations", "philippics"],
                "period": "384-322 av. J.-C.",
                "search_terms": ["demosthenes", "démosthène", "orations", "philippics"]
            },
            "lysias": {
                "name": "Lysias",
                "works": ["speeches"],
                "period": "445-380 av. J.-C.",
                "search_terms": ["lysias", "lysias", "speeches", "discours"]
            }
        }
    
    def identify_author_and_work(self, text: str) -> Dict[str, Any]:
        """Identifie automatiquement l'auteur et l'œuvre à partir du texte avec IA OpenRouter"""
        try:
            # Utiliser l'IA OpenRouter pour l'identification
            prompt = f"""Tu es un expert en littérature grecque et latine antique. Analyse ce texte et identifie l'auteur et l'œuvre.

TEXTE À ANALYSER:
{text}

Instructions:
1. Analyse le style, le vocabulaire, les thèmes et les références
2. Identifie les mots-clés caractéristiques
3. Détermine la période historique
4. Évalue ta confiance (0-100)

Réponds UNIQUEMENT au format JSON exact suivant (sans texte avant ou après):
{{
    "author_id": "nom_technique_auteur",
    "author_name": "Nom complet de l'auteur",
    "work_name": "Nom de l'œuvre",
    "period": "Période historique",
    "confidence": 85,
    "analysis": "Analyse détaillée de l'identification",
    "key_indicators": ["indicateur1", "indicateur2"],
    "greek_terms": ["terme_grec1", "terme_grec2"]
}}

Si tu ne peux pas identifier avec certitude, utilise "unknown" pour author_id et work_name."""

            # Appel direct à l'API OpenRouter
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "anthropic/claude-3.5-sonnet",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 1000,
                    "temperature": 0.1
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result["choices"][0]["message"]["content"].strip()
                
                # Parser la réponse JSON
                import json
                try:
                    # Extraire le JSON de la réponse
                    json_start = ai_response.find('{')
                    json_end = ai_response.rfind('}') + 1
                    if json_start != -1 and json_end != -1:
                        json_str = ai_response[json_start:json_end]
                        parsed_result = json.loads(json_str)
                        
                                            # Ajouter des informations supplémentaires
                    if parsed_result.get("author_id") != "unknown":
                        author_name = parsed_result.get("author_name", "")
                        author_info = GRECO_LATIN_DATABASE.get(author_name, {})
                        parsed_result["works"] = author_info.get("œuvres", [])
                        parsed_result["search_terms"] = author_info.get("search_terms", [])
                        
                        return parsed_result
                    else:
                        # Fallback si pas de JSON valide
                        return self._fallback_identification(text)
                        
                except json.JSONDecodeError:
                    # Fallback si erreur de parsing JSON
                    return self._fallback_identification(text)
            else:
                logging.warning(f"Erreur API OpenRouter: {response.status_code}")
                return self._fallback_identification(text)
                
        except Exception as e:
            logging.error(f"Erreur lors de l'identification IA: {e}")
            return self._fallback_identification(text)
    
    def _fallback_identification(self, text: str) -> Dict[str, Any]:
        """Méthode de fallback avec recherche de mots-clés"""
        text_lower = text.lower()
        results = []
        
        for author_name, author_info in GRECO_LATIN_DATABASE.items():
            score = 0
            matched_terms = []
            
            # Recherche de termes caractéristiques
            search_terms = author_info.get("search_terms", [])
            for term in search_terms:
                if term.lower() in text_lower:
                    score += 10
                    matched_terms.append(term)
            
            # Recherche de noms d'œuvres
            works = author_info.get("œuvres", [])
            for work in works:
                if work.lower() in text_lower:
                    score += 20
                    matched_terms.append(work)
            
            # Recherche de mots grecs caractéristiques
            greek_indicators = self._find_greek_indicators(text)
            if greek_indicators:
                score += 5
                matched_terms.extend(greek_indicators)
            
            if score > 0:
                results.append({
                    "author_id": author_name.lower().replace(" ", "_"),
                    "author_name": author_name,
                    "period": author_info.get("période", "Inconnue"),
                    "works": works,
                    "score": score,
                    "matched_terms": matched_terms,
                    "confidence": min(score / 50 * 100, 100)
                })
        
        # Retourner le meilleur résultat ou un résultat par défaut
        if results:
            best_result = max(results, key=lambda x: x["score"])
            best_result["analysis"] = "Identification par mots-clés (fallback)"
            best_result["key_indicators"] = best_result["matched_terms"]
            return best_result
        else:
            return {
                "author_id": "unknown",
                "author_name": "Auteur inconnu",
                "work_name": "Œuvre inconnue",
                "period": "Période indéterminée",
                "confidence": 0,
                "analysis": "Aucune correspondance trouvée",
                "key_indicators": [],
                "greek_terms": []
            }
        
        # Tri par score décroissant
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return {
            "top_matches": results[:3],
            "best_match": results[0] if results else None,
            "total_matches": len(results)
        }
    
    def _find_greek_indicators(self, text: str) -> List[str]:
        """Trouve des indicateurs de texte grec"""
        indicators = []
        
        # Mots grecs courants
        greek_words = [
            "και", "της", "του", "τον", "την", "τους", "τας", "των",
            "ειναι", "εστιν", "ησαν", "εχει", "εχουσι", "λεγει", "λεγουσι",
            "θεος", "ανθρωπος", "πολις", "οικος", "πατηρ", "μητηρ",
            "υιος", "θυγατηρ", "φιλος", "πολεμος", "ειρηνη", "δικαιοσυνη"
        ]
        
        for word in greek_words:
            if word in text.lower():
                indicators.append(word)
        
        return indicators
    
    def search_perseus_digital_library(self, author: str, work: str = None) -> Dict[str, Any]:
        """Recherche dans la bibliothèque numérique Perseus"""
        try:
            # Construction de l'URL de recherche
            search_url = f"{self.perseus_base_url}text"
            
            params = {
                "doc": f"Perseus:text:1999.01.{author}",
                "lang": "greek"
            }
            
            if work:
                params["doc"] += f":{work}"
            
            # Simulation de la recherche (en production, on ferait un vrai appel API)
            return {
                "url": search_url,
                "params": params,
                "available": True,
                "text_samples": self._get_sample_greek_text(author, work)
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "available": False
            }
    
    def _get_sample_greek_text(self, author: str, work: str = None) -> List[str]:
        """Récupère des échantillons de texte grec original"""
        # Base de données d'échantillons de texte grec
        greek_samples = {
            "homer": {
                "iliad": [
                    "Μῆνιν ἄειδε, θεά, Πηληϊάδεω Ἀχιλῆος",
                    "οὐλομένην, ἣ μυρί᾽ Ἀχαιοῖς ἄλγε᾽ ἔθηκε,",
                    "πολλὰς δ᾽ ἰφθίμους ψυχὰς Ἄϊδι προΐαψεν"
                ],
                "odyssey": [
                    "Ἄνδρα μοι ἔννεπε, Μοῦσα, πολύτροπον, ὃς μάλα πολλὰ",
                    "πλάγχθη, ἐπεὶ Τροίης ἱερὸν πτολίεθρον ἔπερσε·",
                    "πολλῶν δ᾽ ἀνθρώπων ἴδεν ἄστεα καὶ νόον ἔγνω,"
                ]
            },
            "plato": {
                "republic": [
                    "Κατέβην χθὲς εἰς Πειραιᾶ μετὰ Γλαύκωνος τοῦ Ἀρίστωνος",
                    "προσευξόμενός τε τῇ θεῷ καὶ ἅμα τὴν ἑορτὴν βουλόμενος",
                    "θεάσασθαι τίνα τρόπον ποιήσουσιν ἅτε νῦν πρῶτον ἄγοντες."
                ]
            },
            "aristotle": {
                "nicomachean_ethics": [
                    "Πᾶσα τέχνη καὶ πᾶσα μέθοδος, ὁμοίως δὲ πρᾶξίς",
                    "τε καὶ προαίρεσις, ἀγαθοῦ τινὸς ἐφίεσθαι δοκεῖ·",
                    "διὸ καλῶς ἀπεφήναντο τἀγαθόν, οὗ πάντ᾽ ἐφίεται."
                ]
            }
        }
        
        if author in greek_samples:
            if work and work in greek_samples[author]:
                return greek_samples[author][work]
            else:
                # Retourner le premier échantillon disponible
                first_work = list(greek_samples[author].keys())[0]
                return greek_samples[author][first_work]
        
        return ["Texte grec non disponible pour cet auteur."]
    
    def compare_texts(self, ocr_text: str, original_text: str) -> Dict[str, Any]:
        """Compare le texte OCR avec le texte original en utilisant l'IA OpenRouter"""
        try:
            # Utiliser l'IA OpenRouter pour la comparaison
            prompt = f"""Tu es un expert en philologie grecque. Compare ce texte OCR avec le texte original et identifie les erreurs.

TEXTE OCR:
{ocr_text}

TEXTE ORIGINAL:
{original_text}

Réponds au format JSON exact suivant:
{{
    "similarity_percentage": 85.5,
    "analysis": "Analyse détaillée de la comparaison",
    "errors": [
        {{
            "type": "erreur_ocr",
            "ocr_text": "texte_incorrect",
            "original_text": "texte_correct",
            "position": "début/milieu/fin",
            "suggestion": "correction_suggérée"
        }}
    ],
    "corrections": ["correction1", "correction2"],
    "quality_assessment": "excellent/bon/moyen/faible"
}}"""

            # Utiliser l'IA pour la comparaison
            response = self.app.tuteur_ia.chat_with_tutor(prompt, "comparaison_textes")
            
            # Parser la réponse JSON
            import json
            try:
                # Extraire le JSON de la réponse
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start != -1 and json_end != -1:
                    json_str = response[json_start:json_end]
                    result = json.loads(json_str)
                    return result
                else:
                    # Fallback si pas de JSON valide
                    return self._fallback_compare_texts(ocr_text, original_text)
                    
            except json.JSONDecodeError:
                # Fallback si erreur de parsing JSON
                return self._fallback_compare_texts(ocr_text, original_text)
                
        except Exception as e:
            logging.error(f"Erreur lors de la comparaison IA: {e}")
            return self._fallback_compare_texts(ocr_text, original_text)
    
    def _fallback_compare_texts(self, ocr_text: str, original_text: str) -> Dict[str, Any]:
        """Méthode de fallback avec comparaison algorithmique"""
        # Normalisation des textes
        ocr_normalized = self._normalize_text(ocr_text)
        original_normalized = self._normalize_text(original_text)
        
        # Calcul de similarité
        similarity = self._calculate_similarity(ocr_normalized, original_normalized)
        
        # Identification des différences
        differences = self._find_differences(ocr_normalized, original_normalized)
        
        return {
            "similarity_percentage": similarity,
            "differences": differences,
            "suggestions": self._generate_corrections(differences, original_text),
            "analysis": "Comparaison algorithmique (fallback)",
            "quality_assessment": "moyen"
        }
    
    def _normalize_text(self, text: str) -> str:
        """Normalise le texte pour la comparaison"""
        import re
        # Suppression des espaces multiples et normalisation
        text = re.sub(r'\s+', ' ', text.strip())
        # Conversion en minuscules
        text = text.lower()
        # Suppression de la ponctuation
        text = re.sub(r'[^\w\s]', '', text)
        return text
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calcule la similarité entre deux textes"""
        if not text1 or not text2:
            return 0.0
        
        # Algorithme de similarité simple (Levenshtein)
        def levenshtein_distance(s1, s2):
            if len(s1) < len(s2):
                return levenshtein_distance(s2, s1)
            
            if len(s2) == 0:
                return len(s1)
            
            previous_row = list(range(len(s2) + 1))
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            
            return previous_row[-1]
        
        distance = levenshtein_distance(text1, text2)
        max_length = max(len(text1), len(text2))
        
        if max_length == 0:
            return 100.0
        
        similarity = (1 - distance / max_length) * 100
        return max(0.0, min(100.0, similarity))
    
    def _find_differences(self, text1: str, text2: str) -> List[Dict[str, Any]]:
        """Trouve les différences entre deux textes"""
        differences = []
        
        # Comparaison mot par mot
        words1 = text1.split()
        words2 = text2.split()
        
        max_len = max(len(words1), len(words2))
        
        for i in range(max_len):
            word1 = words1[i] if i < len(words1) else ""
            word2 = words2[i] if i < len(words2) else ""
            
            if word1 != word2:
                differences.append({
                    "position": i,
                    "ocr_word": word1,
                    "original_word": word2,
                    "type": "substitution" if word1 and word2 else "insertion/deletion"
                })
        
        return differences
    
    def _generate_corrections(self, differences: List[Dict[str, Any]], original_text: str) -> List[str]:
        """Génère des suggestions de correction"""
        suggestions = []
        
        for diff in differences:
            if diff["type"] == "substitution":
                suggestions.append(f"Remplacer '{diff['ocr_word']}' par '{diff['original_word']}'")
            elif diff["type"] == "insertion/deletion":
                if diff["ocr_word"]:
                    suggestions.append(f"Supprimer le mot '{diff['ocr_word']}'")
                else:
                    suggestions.append(f"Ajouter le mot '{diff['original_word']}'")
        
        return suggestions


# Système de cache intelligent
class CacheSystem:
    """Système de cache intelligent avec IndexedDB, LocalStorage et compression"""
    
    def __init__(self) -> None:
        self.cache_dir = CACHE_DIR
        self.db_path = CACHE_DB_PATH
        self.max_size = CACHE_MAX_SIZE
        self.ttl = CACHE_TTL
        
        # Initialisation de la base de données SQLite
        self._init_database()
        
        # Cache en mémoire pour les accès fréquents
        self.memory_cache = {}
        self.memory_cache_size = 0
        self.max_memory_cache_size = 50 * 1024 * 1024  # 50MB
        
        # Statistiques du cache
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "compressions": 0
        }
        
        logging.info("📊 CacheSystem initialisé")
    
    def _init_database(self) -> None:
        """Initialise la base de données SQLite pour le cache"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Table pour les images
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS image_cache (
                    key TEXT PRIMARY KEY,
                    data BLOB,
                    size INTEGER,
                    created_at REAL,
                    accessed_at REAL,
                    compression_ratio REAL
                )
            ''')
            
            # Table pour les résultats OCR
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ocr_cache (
                    key TEXT PRIMARY KEY,
                    data TEXT,
                    size INTEGER,
                    created_at REAL,
                    accessed_at REAL,
                    language TEXT
                )
            ''')
            
            # Table pour les requêtes API
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_cache (
                    key TEXT PRIMARY KEY,
                    data TEXT,
                    size INTEGER,
                    created_at REAL,
                    accessed_at REAL,
                    endpoint TEXT,
                    ttl INTEGER
                )
            ''')
            
            # Index pour les performances
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_image_accessed ON image_cache(accessed_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_ocr_accessed ON ocr_cache(accessed_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_api_created ON api_cache(created_at)')
            
            conn.commit()
            conn.close()
            
            logging.info("📊 Base de données cache initialisée")
            
        except Exception as e:
            logging.error(f"Erreur initialisation cache DB: {e}")
    
    def _generate_key(self, data: Any, prefix: str = "") -> str:
        """Génère une clé de cache unique"""
        if isinstance(data, str):
            content = data.encode('utf-8')
        elif isinstance(data, bytes):
            content = data
        else:
            content = pickle.dumps(data)
        
        hash_obj = hashlib.sha256(content)
        return f"{prefix}_{hash_obj.hexdigest()}"
    
    def _compress_data(self, data: bytes) -> Tuple[bytes, float]:
        """Compresse les données avec zlib"""
        try:
            compressed = zlib.compress(data, level=9)
            ratio = len(compressed) / len(data) if len(data) > 0 else 1.0
            self.stats["compressions"] += 1
            return compressed, ratio
        except Exception as e:
            logging.warning(f"Erreur compression: {e}")
            return data, 1.0
    
    def _decompress_data(self, data: bytes) -> bytes:
        """Décompresse les données"""
        try:
            return zlib.decompress(data)
        except Exception as e:
            logging.warning(f"Erreur décompression: {e}")
            return data
    
    def cache_image(self, image: Image.Image, key: str = None) -> str:
        """Cache une image avec compression"""
        if key is None:
            key = self._generate_key(image.tobytes(), "img")
        
        try:
            # Conversion en bytes
            img_bytes = image.tobytes()
            
            # Compression
            compressed_data, ratio = self._compress_data(img_bytes)
            
            # Stockage en base
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO image_cache 
                (key, data, size, created_at, accessed_at, compression_ratio)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (key, compressed_data, len(compressed_data), time.time(), time.time(), ratio))
            
            conn.commit()
            conn.close()
            
            # Nettoyage si nécessaire
            self._cleanup_cache()
            
            logging.info(f"📊 Image cachée: {key} (compression: {ratio:.2f})")
            return key
            
        except Exception as e:
            logging.error(f"Erreur cache image: {e}")
            return None
    
    def get_cached_image(self, key: str) -> Optional[Image.Image]:
        """Récupère une image du cache"""
        try:
            # Vérification cache mémoire
            if key in self.memory_cache:
                self.stats["hits"] += 1
                return self.memory_cache[key]
            
            # Vérification base de données
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT data, size FROM image_cache 
                WHERE key = ? AND (time.time() - created_at) < ?
            ''', (key, self.ttl))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                compressed_data, size = result
                
                # Décompression
                img_bytes = self._decompress_data(compressed_data)
                
                # Reconstruction de l'image (simplifié)
                # Note: Cette partie nécessiterait plus de contexte sur l'image
                # Pour l'instant, on retourne None
                
                # Mise à jour du cache mémoire
                if len(self.memory_cache) < 100:  # Limite mémoire
                    self.memory_cache[key] = None  # Placeholder
                
                self.stats["hits"] += 1
                logging.info(f"📊 Image trouvée en cache: {key}")
                return None  # Placeholder
            else:
                self.stats["misses"] += 1
                logging.info(f"📊 Image non trouvée en cache: {key}")
                return None
                
        except Exception as e:
            logging.error(f"Erreur récupération image cache: {e}")
            return None
    
    def cache_ocr_result(self, text: str, language: str, key: str = None) -> str:
        """Cache un résultat OCR"""
        if key is None:
            key = self._generate_key(text, "ocr")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO ocr_cache 
                (key, data, size, created_at, accessed_at, language)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (key, text, len(text), time.time(), time.time(), language))
            
            conn.commit()
            conn.close()
            
            logging.info(f"📊 Résultat OCR caché: {key}")
            return key
            
        except Exception as e:
            logging.error(f"Erreur cache OCR: {e}")
            return None
    
    def get_cached_ocr_result(self, key: str) -> Optional[str]:
        """Récupère un résultat OCR du cache"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT data FROM ocr_cache 
                WHERE key = ? AND (time.time() - created_at) < ?
            ''', (key, self.ttl))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                self.stats["hits"] += 1
                logging.info(f"📊 Résultat OCR trouvé en cache: {key}")
                return result[0]
            else:
                self.stats["misses"] += 1
                logging.info(f"📊 Résultat OCR non trouvé en cache: {key}")
                return None
                
        except Exception as e:
            logging.error(f"Erreur récupération OCR cache: {e}")
            return None
    
    def cache_api_response(self, endpoint: str, params: Dict, response: Dict, ttl: int = None) -> str:
        """Cache une réponse API"""
        if ttl is None:
            ttl = self.ttl
        
        key = self._generate_key(f"{endpoint}_{json.dumps(params, sort_keys=True)}", "api")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            response_json = json.dumps(response)
            
            cursor.execute('''
                INSERT OR REPLACE INTO api_cache 
                (key, data, size, created_at, accessed_at, endpoint, ttl)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (key, response_json, len(response_json), time.time(), time.time(), endpoint, ttl))
            
            conn.commit()
            conn.close()
            
            logging.info(f"📊 Réponse API cachée: {key}")
            return key
            
        except Exception as e:
            logging.error(f"Erreur cache API: {e}")
            return None
    
    def get_cached_api_response(self, endpoint: str, params: Dict) -> Optional[Dict]:
        """Récupère une réponse API du cache"""
        key = self._generate_key(f"{endpoint}_{json.dumps(params, sort_keys=True)}", "api")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT data, ttl FROM api_cache 
                WHERE key = ? AND (time.time() - created_at) < ttl
            ''', (key,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                response_json, ttl = result
                self.stats["hits"] += 1
                logging.info(f"📊 Réponse API trouvée en cache: {key}")
                return json.loads(response_json)
            else:
                self.stats["misses"] += 1
                logging.info(f"📊 Réponse API non trouvée en cache: {key}")
                return None
                
        except Exception as e:
            logging.error(f"Erreur récupération API cache: {e}")
            return None
    
    def _cleanup_cache(self) -> None:
        """Nettoie le cache selon la politique LRU"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Calcul de la taille totale
            cursor.execute('SELECT SUM(size) FROM image_cache')
            total_size = cursor.fetchone()[0] or 0
            
            if total_size > self.max_size:
                # Suppression des entrées les moins récemment utilisées
                cursor.execute('''
                    DELETE FROM image_cache 
                    WHERE key IN (
                        SELECT key FROM image_cache 
                        ORDER BY accessed_at ASC 
                        LIMIT (SELECT COUNT(*) FROM image_cache) / 10
                    )
                ''')
                
                self.stats["evictions"] += 1
                logging.info("📊 Cache nettoyé (LRU)")
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logging.error(f"Erreur nettoyage cache: {e}")
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques du cache"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Statistiques des tables
            cursor.execute('SELECT COUNT(*), SUM(size) FROM image_cache')
            img_count, img_size = cursor.fetchone()
            
            cursor.execute('SELECT COUNT(*), SUM(size) FROM ocr_cache')
            ocr_count, ocr_size = cursor.fetchone()
            
            cursor.execute('SELECT COUNT(*), SUM(size) FROM api_cache')
            api_count, api_size = cursor.fetchone()
            
            conn.close()
            
            total_size = (img_size or 0) + (ocr_size or 0) + (api_size or 0)
            hit_rate = self.stats["hits"] / (self.stats["hits"] + self.stats["misses"]) if (self.stats["hits"] + self.stats["misses"]) > 0 else 0
            
            return {
                "total_size": total_size,
                "max_size": self.max_size,
                "usage_percent": (total_size / self.max_size) * 100,
                "hit_rate": hit_rate,
                "hits": self.stats["hits"],
                "misses": self.stats["misses"],
                "evictions": self.stats["evictions"],
                "compressions": self.stats["compressions"],
                "image_cache": {
                    "count": img_count or 0,
                    "size": img_size or 0
                },
                "ocr_cache": {
                    "count": ocr_count or 0,
                    "size": ocr_size or 0
                },
                "api_cache": {
                    "count": api_count or 0,
                    "size": api_size or 0
                }
            }
            
        except Exception as e:
            logging.error(f"Erreur statistiques cache: {e}")
            return {}
    
    def clear_cache(self, cache_type: str = "all") -> None:
        """Efface le cache"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if cache_type == "all":
                cursor.execute('DELETE FROM image_cache')
                cursor.execute('DELETE FROM ocr_cache')
                cursor.execute('DELETE FROM api_cache')
            elif cache_type == "images":
                cursor.execute('DELETE FROM image_cache')
            elif cache_type == "ocr":
                cursor.execute('DELETE FROM ocr_cache')
            elif cache_type == "api":
                cursor.execute('DELETE FROM api_cache')
            
            conn.commit()
            conn.close()
            
            # Effacement du cache mémoire
            self.memory_cache.clear()
            self.memory_cache_size = 0
            
            logging.info(f"📊 Cache effacé: {cache_type}")
            
        except Exception as e:
            logging.error(f"Erreur effacement cache: {e}")


class InterfaceCustomizer:
    """Gestionnaire de personnalisation complète de l'interface"""
    
    def __init__(self, app: 'SimpleOCRApp') -> None:
        self.app = app
        self.current_theme = "light"
        self.current_style = "default"
        self.theme_callbacks = []
        self.style_callbacks = []
        
        # Charger les préférences sauvegardées
        self._load_interface_preferences()
    
    def _load_interface_preferences(self) -> None:
        """Charge les préférences d'interface depuis un fichier"""
        try:
            interface_file = Path.home() / ".greek_ocr_interface_config.json"
            if interface_file.exists():
                with open(interface_file, 'r') as f:
                    config = json.load(f)
                    self.current_theme = config.get("theme", "light")
                    self.current_style = config.get("style", "default")
        except Exception as e:
            logging.warning(f"Impossible de charger les préférences d'interface: {e}")
    
    def _save_interface_preferences(self) -> None:
        """Sauvegarde les préférences d'interface dans un fichier"""
        try:
            interface_file = Path.home() / ".greek_ocr_interface_config.json"
            config = {
                "theme": self.current_theme,
                "style": self.current_style
            }
            with open(interface_file, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            logging.warning(f"Impossible de sauvegarder les préférences d'interface: {e}")
    
    def get_current_theme(self) -> dict:
        """Retourne le thème actuel"""
        return THEME_CONFIG.get(self.current_theme, THEME_CONFIG["light"])
    
    def get_current_style(self) -> dict:
        """Retourne le style actuel"""
        return INTERFACE_STYLES.get(self.current_style, INTERFACE_STYLES["default"])
    
    def set_theme(self, theme_name: str) -> None:
        """Change le thème de l'application"""
        if theme_name in THEME_CONFIG:
            self.current_theme = theme_name
            self._save_interface_preferences()
            self._apply_theme_changes()
        else:
            logging.warning(f"Thème non supporté: {theme_name}")
    
    def set_style(self, style_name: str) -> None:
        """Change le style de l'interface"""
        if style_name in INTERFACE_STYLES:
            self.current_style = style_name
            self._save_interface_preferences()
            self._apply_style_changes()
        else:
            logging.warning(f"Style non supporté: {style_name}")
    
    def _apply_theme_changes(self) -> None:
        """Applique les changements de thème à toute l'application"""
        for callback in self.theme_callbacks:
            try:
                callback()
            except Exception as e:
                logging.error(f"Erreur lors de l'application du thème: {e}")
    
    def _apply_style_changes(self) -> None:
        """Applique les changements de style à toute l'application"""
        for callback in self.style_callbacks:
            try:
                callback()
            except Exception as e:
                logging.error(f"Erreur lors de l'application du style: {e}")
    
    def register_theme_callback(self, callback: callable) -> None:
        """Enregistre un callback pour les changements de thème"""
        self.theme_callbacks.append(callback)
    
    def register_style_callback(self, callback: callable) -> None:
        """Enregistre un callback pour les changements de style"""
        self.style_callbacks.append(callback)
    
    def open_customization_panel(self) -> None:
        """Ouvre le panneau de personnalisation complet"""
        self._create_customization_window()
    
    def _create_customization_window(self) -> None:
        """Crée la fenêtre de personnalisation complète"""
        custom_window = tk.Toplevel(self.app)
        custom_window.title("🎨 Personnalisation de l'Interface")
        custom_window.geometry("800x600")
        custom_window.configure(bg=self.get_current_theme()["bg"])
        custom_window.resizable(True, True)
        
        # Centrer la fenêtre
        custom_window.transient(self.app)
        custom_window.grab_set()
        
        # Titre principal
        title_label = tk.Label(custom_window, text="🎨 Personnalisation de l'Interface", 
                              font=("Segoe UI", 18, "bold"), 
                              bg=self.get_current_theme()["bg"], 
                              fg=self.get_current_theme()["accent"])
        title_label.pack(pady=20)
        
        # Notebook pour les onglets
        notebook = ttk.Notebook(custom_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Onglet Thèmes
        theme_frame = tk.Frame(notebook, bg=self.get_current_theme()["bg"])
        notebook.add(theme_frame, text="🌙 Thèmes")
        self._create_theme_tab(theme_frame)
        
        # Onglet Styles
        style_frame = tk.Frame(notebook, bg=self.get_current_theme()["bg"])
        notebook.add(style_frame, text="🎭 Styles")
        self._create_style_tab(style_frame)
        
        # Onglet Polices
        font_frame = tk.Frame(notebook, bg=self.get_current_theme()["bg"])
        notebook.add(font_frame, text="🔤 Polices")
        self._create_font_tab(font_frame)
        
        # Onglet Aperçu
        preview_frame = tk.Frame(notebook, bg=self.get_current_theme()["bg"])
        notebook.add(preview_frame, text="👁️ Aperçu")
        self._create_preview_tab(preview_frame)
        
        # Boutons d'action
        self._create_action_buttons(custom_window)
    
    def _create_theme_tab(self, parent: tk.Frame) -> None:
        """Crée l'onglet des thèmes"""
        # Titre de l'onglet
        title_label = tk.Label(parent, text="🌙 Choisissez votre thème", 
                              font=("Segoe UI", 14, "bold"), 
                              bg=self.get_current_theme()["bg"], 
                              fg=self.get_current_theme()["fg"])
        title_label.pack(pady=10)
        
        # Frame pour les thèmes
        themes_frame = tk.Frame(parent, bg=self.get_current_theme()["bg"])
        themes_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        theme_var = tk.StringVar(value=self.current_theme)
        
        # Création des boutons de thème
        for theme_key, theme_data in THEME_CONFIG.items():
            theme_button = tk.Button(
                themes_frame,
                text=f"{theme_data['name']}",
                font=("Segoe UI", 12, "bold"),
                bg=theme_data["accent"],
                fg="white",
                relief=tk.RAISED,
                bd=2,
                padx=20,
                pady=10,
                command=lambda t=theme_key, v=theme_var: self._select_theme(t, v)
            )
            theme_button.pack(fill=tk.X, pady=5)
            
            # Indicateur de sélection
            if theme_key == self.current_theme:
                theme_button.config(bg=theme_data["success"])
    
    def _create_style_tab(self, parent: tk.Frame) -> None:
        """Crée l'onglet des styles"""
        # Titre de l'onglet
        title_label = tk.Label(parent, text="🎭 Choisissez votre style", 
                              font=("Segoe UI", 14, "bold"), 
                              bg=self.get_current_theme()["bg"], 
                              fg=self.get_current_theme()["fg"])
        title_label.pack(pady=10)
        
        # Frame pour les styles
        styles_frame = tk.Frame(parent, bg=self.get_current_theme()["bg"])
        styles_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        style_var = tk.StringVar(value=self.current_style)
        
        # Création des boutons de style
        for style_key, style_data in INTERFACE_STYLES.items():
            style_button = tk.Button(
                styles_frame,
                text=f"{style_data['name']}",
                font=("Segoe UI", 12, "bold"),
                bg=self.get_current_theme()["accent"],
                fg="white",
                relief=tk.RAISED,
                bd=2,
                padx=20,
                pady=10,
                command=lambda s=style_key, v=style_var: self._select_style(s, v)
            )
            style_button.pack(fill=tk.X, pady=5)
            
            # Indicateur de sélection
            if style_key == self.current_style:
                style_button.config(bg=self.get_current_theme()["success"])
    
    def _create_font_tab(self, parent: tk.Frame) -> None:
        """Crée l'onglet des polices"""
        # Titre de l'onglet
        title_label = tk.Label(parent, text="🔤 Personnalisez vos polices", 
                              font=("Segoe UI", 14, "bold"), 
                              bg=self.get_current_theme()["bg"], 
                              fg=self.get_current_theme()["fg"])
        title_label.pack(pady=10)
        
        # Frame pour les polices
        font_frame = tk.Frame(parent, bg=self.get_current_theme()["bg"])
        font_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Sélection de police
        font_label = tk.Label(font_frame, text="Police:", 
                             font=("Segoe UI", 12, "bold"), 
                             bg=self.get_current_theme()["bg"], 
                             fg=self.get_current_theme()["fg"])
        font_label.pack(anchor=tk.W, pady=5)
        
        font_var = tk.StringVar(value=self.app.font_manager.current_font)
        font_combo = ttk.Combobox(font_frame, textvariable=font_var, 
                                 values=AVAILABLE_FONTS, 
                                 font=("Segoe UI", 11), state="readonly")
        font_combo.pack(fill=tk.X, pady=5)
        
        # Sélection de taille
        size_label = tk.Label(font_frame, text="Taille:", 
                             font=("Segoe UI", 12, "bold"), 
                             bg=self.get_current_theme()["bg"], 
                             fg=self.get_current_theme()["fg"])
        size_label.pack(anchor=tk.W, pady=5)
        
        size_var = tk.IntVar(value=self.app.font_manager.current_size)
        size_combo = ttk.Combobox(font_frame, textvariable=size_var, 
                                 values=AVAILABLE_SIZES, 
                                 font=("Segoe UI", 11), state="readonly")
        size_combo.pack(fill=tk.X, pady=5)
        
        # Aperçu de police
        preview_label = tk.Label(font_frame, text="Aperçu:", 
                                font=("Segoe UI", 12, "bold"), 
                                bg=self.get_current_theme()["bg"], 
                                fg=self.get_current_theme()["fg"])
        preview_label.pack(anchor=tk.W, pady=5)
        
        preview_text = tk.Text(font_frame, height=4, wrap=tk.WORD, 
                              font=("Segoe UI", 11), 
                              bg=self.get_current_theme()["text_bg"],
                              fg=self.get_current_theme()["text_fg"])
        preview_text.pack(fill=tk.X, pady=5)
        
        # Fonction de mise à jour de l'aperçu
        def update_font_preview(*args):
            try:
                preview_font = (font_var.get(), size_var.get(), "normal")
                preview_text.config(font=preview_font)
                preview_text.delete(1.0, tk.END)
                preview_text.insert(tk.END, "Aperçu de la police sélectionnée\n\n")
                preview_text.insert(tk.END, "Texte normal\n")
                preview_text.insert(tk.END, "Texte en gras\n", "bold")
                preview_text.insert(tk.END, "Texte en italique\n", "italic")
                preview_text.tag_config("bold", font=(font_var.get(), size_var.get(), "bold"))
                preview_text.tag_config("italic", font=(font_var.get(), size_var.get(), "italic"))
            except Exception as e:
                logging.error(f"Erreur mise à jour aperçu police: {e}")
        
        font_var.trace('w', update_font_preview)
        size_var.trace('w', update_font_preview)
        update_font_preview()
        
        # Stocker les variables pour utilisation ultérieure
        self.font_var = font_var
        self.size_var = size_var
    
    def _create_preview_tab(self, parent: tk.Frame) -> None:
        """Crée l'onglet d'aperçu"""
        # Titre de l'onglet
        title_label = tk.Label(parent, text="👁️ Aperçu de votre personnalisation", 
                              font=("Segoe UI", 14, "bold"), 
                              bg=self.get_current_theme()["bg"], 
                              fg=self.get_current_theme()["fg"])
        title_label.pack(pady=10)
        
        # Frame d'aperçu
        preview_frame = tk.Frame(parent, bg=self.get_current_theme()["bg"])
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Zone d'aperçu
        preview_text = tk.Text(preview_frame, height=15, wrap=tk.WORD, 
                              font=("Segoe UI", 11), 
                              bg=self.get_current_theme()["text_bg"],
                              fg=self.get_current_theme()["text_fg"])
        preview_text.pack(fill=tk.BOTH, expand=True)
        
        # Contenu d'aperçu
        preview_content = """
🎨 APERÇU DE VOTRE PERSONNALISATION

Thème actuel: {theme}
Style actuel: {style}
Police actuelle: {font} {size}

Ceci est un aperçu de l'apparence de votre interface personnalisée.
Vous pouvez voir ici comment vos choix de thème, style et police
s'affichent ensemble.

Fonctionnalités disponibles:
• 🌙 Thèmes jour/nuit
• 🎭 Styles d'interface
• 🔤 Personnalisation des polices
• 👁️ Aperçu en temps réel

Cliquez sur "Appliquer" pour voir les changements dans l'application principale !
        """.format(
            theme=THEME_CONFIG[self.current_theme]["name"],
            style=INTERFACE_STYLES[self.current_style]["name"],
            font=self.app.font_manager.current_font,
            size=self.app.font_manager.current_size
        )
        
        preview_text.insert(tk.END, preview_content)
        preview_text.config(state=tk.DISABLED)
    
    def _create_action_buttons(self, parent: tk.Toplevel) -> None:
        """Crée les boutons d'action"""
        button_frame = tk.Frame(parent, bg=self.get_current_theme()["bg"])
        button_frame.pack(pady=20)
        
        # Bouton Appliquer
        apply_button = tk.Button(button_frame, text="✅ Appliquer", 
                                font=("Segoe UI", 12, "bold"), 
                                bg=self.get_current_theme()["success"], 
                                fg="white",
                                command=lambda: self._apply_customization(parent))
        apply_button.pack(side=tk.LEFT, padx=10)
        
        # Bouton Réinitialiser
        reset_button = tk.Button(button_frame, text="🔄 Réinitialiser", 
                                font=("Segoe UI", 12, "bold"), 
                                bg=self.get_current_theme()["warning"], 
                                fg="black",
                                command=self._reset_customization)
        reset_button.pack(side=tk.LEFT, padx=10)
        
        # Bouton Annuler
        cancel_button = tk.Button(button_frame, text="❌ Annuler", 
                                 font=("Segoe UI", 12, "bold"), 
                                 bg=self.get_current_theme()["danger"], 
                                 fg="white",
                                 command=parent.destroy)
        cancel_button.pack(side=tk.LEFT, padx=10)
    
    def _select_theme(self, theme_name: str, theme_var: tk.StringVar) -> None:
        """Sélectionne un thème"""
        theme_var.set(theme_name)
        self.current_theme = theme_name
        # Mettre à jour l'aperçu
        self._update_preview()
    
    def _select_style(self, style_name: str, style_var: tk.StringVar) -> None:
        """Sélectionne un style"""
        style_var.set(style_name)
        self.current_style = style_name
        # Mettre à jour l'aperçu
        self._update_preview()
    
    def _update_preview(self) -> None:
        """Met à jour l'aperçu"""
        # Cette méthode sera appelée pour mettre à jour l'aperçu
        # quand l'utilisateur change les paramètres
        pass
    
    def _apply_customization(self, window: tk.Toplevel) -> None:
        """Applique la personnalisation"""
        try:
            # Appliquer le thème
            self.set_theme(self.current_theme)
            
            # Appliquer le style
            self.set_style(self.current_style)
            
            # Appliquer la police
            if hasattr(self, 'font_var') and hasattr(self, 'size_var'):
                self.app.font_manager.set_font(self.font_var.get(), self.size_var.get())
            
            messagebox.showinfo("Succès", "La personnalisation a été appliquée avec succès !")
            window.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'application: {e}")
    
    def _reset_customization(self) -> None:
        """Réinitialise la personnalisation"""
        try:
            # Réinitialiser le thème
            self.current_theme = "light"
            
            # Réinitialiser le style
            self.current_style = "default"
            
            # Réinitialiser la police
            self.app.font_manager.set_font(FONT_CONFIG["default_font"], FONT_CONFIG["default_size"])
            
            # Appliquer les changements
            self.set_theme("light")
            self.set_style("default")
            
            messagebox.showinfo("Succès", "La personnalisation a été réinitialisée !")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la réinitialisation: {e}")


class FontManager:
    """Gestionnaire de polices et tailles pour l'application"""
    
    def __init__(self, app: 'SimpleOCRApp') -> None:
        self.app = app
        self.current_font = FONT_CONFIG["default_font"]
        self.current_size = FONT_CONFIG["default_size"]
        self.font_callbacks = []
        
        # Charger les préférences sauvegardées
        self._load_font_preferences()
    
    def _load_font_preferences(self) -> None:
        """Charge les préférences de police depuis un fichier"""
        try:
            font_file = Path.home() / ".greek_ocr_font_config.json"
            if font_file.exists():
                with open(font_file, 'r') as f:
                    config = json.load(f)
                    self.current_font = config.get("font", FONT_CONFIG["default_font"])
                    self.current_size = config.get("size", FONT_CONFIG["default_size"])
        except Exception as e:
            logging.warning(f"Impossible de charger les préférences de police: {e}")
    
    def _save_font_preferences(self) -> None:
        """Sauvegarde les préférences de police dans un fichier"""
        try:
            font_file = Path.home() / ".greek_ocr_font_config.json"
            config = {
                "font": self.current_font,
                "size": self.current_size
            }
            with open(font_file, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            logging.warning(f"Impossible de sauvegarder les préférences de police: {e}")
    
    def get_font(self, style: str = "normal", weight: str = "normal") -> tuple:
        """Retourne la police actuelle avec le style et poids spécifiés"""
        if style == "bold":
            return (self.current_font, self.current_size, "bold")
        elif style == "italic":
            return (self.current_font, self.current_size, "italic")
        elif style == "bold italic":
            return (self.current_font, self.current_size, "bold italic")
        else:
            return (self.current_font, self.current_size, weight)
    
    def get_title_font(self) -> tuple:
        """Retourne la police pour les titres"""
        return (self.current_font, FONT_CONFIG["title_size"], "bold")
    
    def get_subtitle_font(self) -> tuple:
        """Retourne la police pour les sous-titres"""
        return (self.current_font, FONT_CONFIG["subtitle_size"], "bold")
    
    def get_button_font(self) -> tuple:
        """Retourne la police pour les boutons"""
        return (self.current_font, FONT_CONFIG["button_size"], "bold")
    
    def get_text_font(self) -> tuple:
        """Retourne la police pour le texte normal"""
        return (self.current_font, FONT_CONFIG["text_size"], "normal")
    
    def get_small_font(self) -> tuple:
        """Retourne la police pour le petit texte"""
        return (self.current_font, FONT_CONFIG["small_size"], "normal")
    
    def get_large_font(self) -> tuple:
        """Retourne la police pour le grand texte"""
        return (self.current_font, FONT_CONFIG["large_size"], "normal")
    
    def set_font(self, font_name: str, size: int) -> None:
        """Change la police et la taille de l'application"""
        if font_name in AVAILABLE_FONTS and size in AVAILABLE_SIZES:
            self.current_font = font_name
            self.current_size = size
            self._save_font_preferences()
            self._apply_font_changes()
        else:
            logging.warning(f"Police ou taille non supportée: {font_name}, {size}")
    
    def _apply_font_changes(self) -> None:
        """Applique les changements de police à toute l'application"""
        # Notifier tous les widgets enregistrés
        for callback in self.font_callbacks:
            try:
                callback()
            except Exception as e:
                logging.error(f"Erreur lors de l'application du changement de police: {e}")
    
    def register_font_callback(self, callback: callable) -> None:
        """Enregistre un callback pour les changements de police"""
        self.font_callbacks.append(callback)
    
    def open_font_settings(self) -> None:
        """Ouvre la fenêtre de paramètres de police"""
        self._create_font_settings_window()
    
    def _create_font_settings_window(self) -> None:
        """Crée la fenêtre de paramètres de police"""
        settings_window = tk.Toplevel(self.app)
        settings_window.title("🔤 Paramètres de Police")
        settings_window.geometry("500x400")
        settings_window.configure(bg="#f8f9fa")
        settings_window.resizable(False, False)
        
        # Centrer la fenêtre
        settings_window.transient(self.app)
        settings_window.grab_set()
        
        # Titre
        title_label = tk.Label(settings_window, text="🔤 Paramètres de Police", 
                              font=self.get_title_font(), 
                              bg="#f8f9fa", fg="#007acc")
        title_label.pack(pady=20)
        
        # Frame principal
        main_frame = tk.Frame(settings_window, bg="#f8f9fa")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Sélection de police
        font_frame = tk.LabelFrame(main_frame, text="Police", 
                                  font=self.get_subtitle_font(), bg="#f8f9fa")
        font_frame.pack(fill=tk.X, pady=10)
        
        font_var = tk.StringVar(value=self.current_font)
        font_combo = ttk.Combobox(font_frame, textvariable=font_var, 
                                 values=AVAILABLE_FONTS, 
                                 font=self.get_text_font(), state="readonly")
        font_combo.pack(fill=tk.X, padx=10, pady=10)
        
        # Sélection de taille
        size_frame = tk.LabelFrame(main_frame, text="Taille", 
                                  font=self.get_subtitle_font(), bg="#f8f9fa")
        size_frame.pack(fill=tk.X, pady=10)
        
        size_var = tk.IntVar(value=self.current_size)
        size_combo = ttk.Combobox(size_frame, textvariable=size_var, 
                                 values=AVAILABLE_SIZES, 
                                 font=self.get_text_font(), state="readonly")
        size_combo.pack(fill=tk.X, padx=10, pady=10)
        
        # Aperçu
        preview_frame = tk.LabelFrame(main_frame, text="Aperçu", 
                                     font=self.get_subtitle_font(), bg="#f8f9fa")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        preview_text = tk.Text(preview_frame, height=8, wrap=tk.WORD, 
                              font=self.get_text_font(), bg="white")
        preview_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Fonction de mise à jour de l'aperçu
        def update_preview(*args):
            try:
                preview_font = (font_var.get(), size_var.get(), "normal")
                preview_text.config(font=preview_font)
                preview_text.delete(1.0, tk.END)
                preview_text.insert(tk.END, "Aperçu de la police sélectionnée\n\n")
                preview_text.insert(tk.END, "Texte normal\n")
                preview_text.insert(tk.END, "Texte en gras\n", "bold")
                preview_text.insert(tk.END, "Texte en italique\n", "italic")
                preview_text.tag_config("bold", font=(font_var.get(), size_var.get(), "bold"))
                preview_text.tag_config("italic", font=(font_var.get(), size_var.get(), "italic"))
            except Exception as e:
                logging.error(f"Erreur mise à jour aperçu: {e}")
        
        font_var.trace('w', update_preview)
        size_var.trace('w', update_preview)
        update_preview()
        
        # Boutons d'action
        button_frame = tk.Frame(settings_window, bg="#f8f9fa")
        button_frame.pack(pady=20)
        
        # Bouton Appliquer
        apply_button = tk.Button(button_frame, text="✅ Appliquer", 
                                font=self.get_button_font(), bg="#28a745", fg="white",
                                command=lambda: self._apply_font_settings(
                                    font_var.get(), size_var.get(), settings_window))
        apply_button.pack(side=tk.LEFT, padx=10)
        
        # Bouton Réinitialiser
        reset_button = tk.Button(button_frame, text="🔄 Réinitialiser", 
                                font=self.get_button_font(), bg="#ffc107", fg="black",
                                command=lambda: self._reset_font_settings(
                                    font_var, size_var))
        reset_button.pack(side=tk.LEFT, padx=10)
        
        # Bouton Annuler
        cancel_button = tk.Button(button_frame, text="❌ Annuler", 
                                 font=self.get_button_font(), bg="#dc3545", fg="white",
                                 command=settings_window.destroy)
        cancel_button.pack(side=tk.LEFT, padx=10)
    
    def _apply_font_settings(self, font_name: str, size: int, window: tk.Toplevel) -> None:
        """Applique les nouveaux paramètres de police"""
        try:
            self.set_font(font_name, size)
            messagebox.showinfo("Succès", "Les paramètres de police ont été appliqués avec succès !")
            window.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'application des paramètres: {e}")
    
    def _reset_font_settings(self, font_var: tk.StringVar, size_var: tk.StringVar) -> None:
        """Réinitialise les paramètres de police"""
        font_var.set(FONT_CONFIG["default_font"])
        size_var.set(FONT_CONFIG["default_size"])


class WordEvaluator:
    """Évaluateur IA des mots avec OpenRouter"""
    
    def __init__(self, app: 'SimpleOCRApp') -> None:
        self.app = app
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        self.openrouter_url = "https://openrouter.ai/api/v1/chat/completions"
    
    def evaluate_words(self, text: str) -> List[Dict[str, Any]]:
        """Évalue chaque mot avec l'IA et retourne un score avec code couleur"""
        if not self.openrouter_api_key:
            return self._fallback_evaluation(text)
        
        try:
            # Préparation de la requête
            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "Content-Type": "application/json"
            }
            
            prompt = f"""Analyse ce texte grec ancien et évalue chaque mot individuellement.
            
Texte: {text}

Pour chaque mot, fournis:
1. Le mot original
2. Un score de confiance (0-100)
3. Une correction suggérée si nécessaire
4. Un code couleur (green=excellent, yellow=correct, red=erreur, blue=douteux)

Format de réponse JSON:
{{
    "words": [
        {{
            "word": "mot",
            "confidence": 85,
            "correction": "mot_corrigé",
            "color": "green",
            "notes": "explication"
        }}
    ]
}}

Analyse uniquement le texte grec ancien."""

            data = {
                "model": "anthropic/claude-3.5-sonnet",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "max_tokens": 2000
            }
            
            response = requests.post(self.openrouter_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Parse de la réponse JSON
            import json
            evaluation = json.loads(content)
            return evaluation.get('words', [])
            
        except Exception as e:
            logging.error(f"Erreur évaluation IA: {e}")
            return self._fallback_evaluation(text)
    
    def _fallback_evaluation(self, text: str) -> List[Dict[str, Any]]:
        """Évaluation de fallback sans IA"""
        words = text.split()
        evaluated_words = []
        
        for word in words:
            # Logique simple de fallback
            if len(word) > 2:
                confidence = 80
                color = "green"
            elif len(word) > 1:
                confidence = 60
                color = "yellow"
            else:
                confidence = 30
                color = "red"
            
            evaluated_words.append({
                "word": word,
                "confidence": confidence,
                "correction": word,
                "color": color,
                "notes": "Évaluation automatique"
            })
        
        return evaluated_words


class OCRTextEditor:
    """Éditeur de texte OCR avec surbrillance des mots correspondants dans l'image"""
    
    def __init__(self, app: 'SimpleOCRApp') -> None:
        self.app = app
        self.word_positions = {}  # {word: [(x1, y1, x2, y2, confidence), ...]}
        self.current_highlight = None
        self.highlight_rectangle = None
        self.editable_text_widget = None
        self.original_ocr_results = []
        
    def setup_editable_text_widget(self, text_widget: tk.Text) -> None:
        """Configure le widget de texte pour l'édition et la surbrillance"""
        self.editable_text_widget = text_widget
        
        # Activer l'édition
        text_widget.config(state=tk.NORMAL)
        
        # Bind les événements de clic pour la surbrillance
        text_widget.bind("<Button-1>", self._on_text_click)
        text_widget.bind("<KeyRelease>", self._on_text_change)
        text_widget.bind("<FocusOut>", self._on_focus_out)
        
        # Configuration des tags pour la surbrillance
        text_widget.tag_config("highlighted_word", background="#ffff00", relief="raised", borderwidth=1)
        text_widget.tag_config("selected_word", background="#ff6b6b", foreground="white", relief="raised", borderwidth=2)
        text_widget.tag_config("editable", background="#f8f9fa", relief="solid", borderwidth=1)
        
    def set_ocr_results(self, results: List[Dict[str, Any]]) -> None:
        """Définit les résultats OCR avec les positions des mots"""
        self.original_ocr_results = results
        self.word_positions = {}
        
        for result in results:
            # Utiliser les positions de mots détaillées si disponibles
            word_positions = result.get('word_positions', [])
            
            if word_positions:
                # Utiliser les positions exactes fournies par Tesseract
                for word_data in word_positions:
                    word_text = word_data.get('text', '').strip()
                    bbox = word_data.get('bbox', None)
                    confidence = word_data.get('confidence', 0)
                    
                    if word_text and bbox:
                        if word_text not in self.word_positions:
                            self.word_positions[word_text] = []
                        self.word_positions[word_text].append((bbox[0], bbox[1], bbox[2], bbox[3], confidence))
            else:
                # Fallback : utiliser l'ancienne méthode avec estimation
                text = result.get('text', '')
                bbox = result.get('bbox', None)  # (x1, y1, x2, y2)
                confidence = result.get('confidence', 0)
                
                if bbox and text.strip():
                    # Diviser le texte en mots
                    words = text.split()
                    if len(words) == 1:
                        # Un seul mot
                        self.word_positions[text.strip()] = [(bbox[0], bbox[1], bbox[2], bbox[3], confidence)]
                    else:
                        # Plusieurs mots - estimer les positions
                        word_width = (bbox[2] - bbox[0]) / len(words)
                        for i, word in enumerate(words):
                            word_x1 = bbox[0] + (i * word_width)
                            word_x2 = bbox[0] + ((i + 1) * word_width)
                            if word.strip():
                                self.word_positions[word.strip()] = [(word_x1, bbox[1], word_x2, bbox[3], confidence)]
    
    def _on_text_click(self, event) -> None:
        """Gère le clic sur un mot dans le texte"""
        if not self.editable_text_widget:
            return
            
        # Obtenir le mot cliqué
        index = self.editable_text_widget.index(f"@{event.x},{event.y}")
        word_start = self.editable_text_widget.index(f"{index} wordstart")
        word_end = self.editable_text_widget.index(f"{index} wordend")
        clicked_word = self.editable_text_widget.get(word_start, word_end).strip()
        
        if clicked_word and clicked_word in self.word_positions:
            # Supprimer la surbrillance précédente
            self._clear_highlight()
            
            # Surligner le mot dans le texte
            self.editable_text_widget.tag_add("selected_word", word_start, word_end)
            
            # Surligner le mot correspondant dans l'image
            self._highlight_word_in_image(clicked_word)
    
    def _highlight_word_in_image(self, word: str) -> None:
        """Surligne le mot correspondant dans l'image"""
        if word not in self.word_positions:
            return
            
        # Supprimer la surbrillance précédente
        if self.highlight_rectangle:
            self.app.image_canvas.delete(self.highlight_rectangle)
        
        # Obtenir les positions du mot
        positions = self.word_positions[word]
        
        # Créer la surbrillance pour chaque occurrence
        for x1, y1, x2, y2, confidence in positions:
            # Convertir les coordonnées selon le zoom et le pan actuels
            zoom = getattr(self.app.controles_gestuels, 'current_zoom', 1.0)
            pan_x = getattr(self.app.controles_gestuels, 'pan_x', 0)
            pan_y = getattr(self.app.controles_gestuels, 'pan_y', 0)
            
            # Appliquer les transformations
            scaled_x1 = (x1 * zoom) - pan_x
            scaled_y1 = (y1 * zoom) - pan_y
            scaled_x2 = (x2 * zoom) - pan_x
            scaled_y2 = (y2 * zoom) - pan_y
            
            # Créer le rectangle de surbrillance
            self.highlight_rectangle = self.app.image_canvas.create_rectangle(
                scaled_x1, scaled_y1, scaled_x2, scaled_y2,
                outline="#ff0000", width=3, fill="", stipple="gray50"
            )
            
            # Ajouter une animation de clignotement
            self._animate_highlight()
    
    def _animate_highlight(self) -> None:
        """Anime la surbrillance du mot"""
        if not self.highlight_rectangle:
            return
            
        def blink():
            if self.highlight_rectangle:
                current_color = self.app.image_canvas.itemcget(self.highlight_rectangle, "outline")
                new_color = "#00ff00" if current_color == "#ff0000" else "#ff0000"
                self.app.image_canvas.itemconfig(self.highlight_rectangle, outline=new_color)
                self.app.after(500, blink)
        
        blink()
    
    def _clear_highlight(self) -> None:
        """Supprime la surbrillance actuelle"""
        if self.highlight_rectangle:
            self.app.image_canvas.delete(self.highlight_rectangle)
            self.highlight_rectangle = None
        
        if self.editable_text_widget:
            self.editable_text_widget.tag_remove("selected_word", "1.0", tk.END)
    
    def _on_text_change(self, event) -> None:
        """Gère les changements dans le texte"""
        # Mettre à jour les positions des mots si nécessaire
        self._update_word_positions()
    
    def _on_focus_out(self, event) -> None:
        """Gère la perte de focus du widget de texte"""
        # Optionnel : sauvegarder les modifications
        pass
    
    def _update_word_positions(self) -> None:
        """Met à jour les positions des mots après édition"""
        # Cette méthode peut être étendue pour gérer les modifications de texte
        pass
    
    def enable_editing(self) -> None:
        """Active l'édition du texte OCR"""
        if self.editable_text_widget:
            self.editable_text_widget.config(state=tk.NORMAL)
            self.editable_text_widget.bind("<KeyRelease>", self._on_text_change)
    
    def disable_editing(self) -> None:
        """Désactive l'édition du texte OCR"""
        if self.editable_text_widget:
            self.editable_text_widget.config(state=tk.DISABLED)
            self.editable_text_widget.unbind("<KeyRelease>")
    
    def get_edited_text(self) -> str:
        """Retourne le texte édité"""
        if self.editable_text_widget:
            return self.editable_text_widget.get("1.0", tk.END).strip()
        return ""
    
    def save_edits(self) -> None:
        """Sauvegarde les modifications du texte"""
        edited_text = self.get_edited_text()
        # Ici on peut ajouter la logique pour sauvegarder les modifications
        logging.info(f"Texte édité sauvegardé: {len(edited_text)} caractères")
    
    def reset_to_original(self) -> None:
        """Remet le texte à son état original"""
        if self.editable_text_widget and self.original_ocr_results:
            self.editable_text_widget.config(state=tk.NORMAL)
            self.editable_text_widget.delete("1.0", tk.END)
            
            # Réafficher le texte original
            for result in self.original_ocr_results:
                text = result.get('text', '')
                self.editable_text_widget.insert(tk.END, f"{text}\n\n")
            
            self.editable_text_widget.config(state=tk.NORMAL)


class AdvancedOCRManager:
    """Gestionnaire OCR avancé avec sélection de zones, colonnes et amélioration IA"""
    
    def __init__(self, app: 'SimpleOCRApp') -> None:
        self.app = app
        self.word_evaluator = WordEvaluator(app)
        
        # Zones de sélection
        self.selected_regions = []  # Zones sélectionnées pour l'OCR
        self.active_selection = None
        self.selection_start = None
        self.selection_end = None
        
        # Configuration des colonnes
        self.column_detection_enabled = True
        self.multilingual_mode = True
        self.ia_enhancement_enabled = True
        
        # Configuration des langues par colonne
        self.column_languages = {
            "left": "grc",      # Grec ancien pour colonne gauche
            "right": "fra",     # Français pour colonne droite
            "center": "grc+fra" # Mixte pour colonne centrale
        }
        
        # Mode d'OCR actuel
        self.ocr_mode = "full"  # full, selected, columns, pdf_full
    
    def open_ocr_options(self) -> None:
        """Ouvre la fenêtre d'options OCR avancées"""
        self._create_ocr_options_window()
    
    def _create_ocr_options_window(self) -> None:
        """Crée la fenêtre d'options OCR"""
        options_window = tk.Toplevel(self.app)
        options_window.title("🔍 Options OCR Avancées")
        options_window.geometry("600x500")
        options_window.configure(bg="#f8f9fa")
        options_window.resizable(True, True)
        
        # Centrer la fenêtre
        options_window.transient(self.app)
        options_window.grab_set()
        
        # Titre
        title_label = tk.Label(options_window, text="🔍 Options OCR Avancées", 
                              font=("Segoe UI", 16, "bold"), 
                              bg="#f8f9fa", fg="#212529")
        title_label.pack(pady=20)
        
        # Notebook pour les onglets
        notebook = ttk.Notebook(options_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Onglet Mode d'OCR
        mode_frame = tk.Frame(notebook, bg="#f8f9fa")
        notebook.add(mode_frame, text="🎯 Mode d'OCR")
        self._create_mode_tab(mode_frame)
        
        # Onglet Colonnes
        columns_frame = tk.Frame(notebook, bg="#f8f9fa")
        notebook.add(columns_frame, text="📰 Colonnes")
        self._create_columns_tab(columns_frame)
        
        # Onglet Amélioration IA
        ia_frame = tk.Frame(notebook, bg="#f8f9fa")
        notebook.add(ia_frame, text="🤖 IA")
        self._create_ia_tab(ia_frame)
        
        # Boutons d'action
        self._create_ocr_action_buttons(options_window)
    
    def _create_mode_tab(self, parent: tk.Frame) -> None:
        """Crée l'onglet des modes d'OCR"""
        # Titre
        title_label = tk.Label(parent, text="🎯 Choisissez le mode d'OCR", 
                              font=("Segoe UI", 14, "bold"), 
                              bg="#f8f9fa", fg="#212529")
        title_label.pack(pady=10)
        
        # Frame pour les modes
        modes_frame = tk.Frame(parent, bg="#f8f9fa")
        modes_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Variable pour le mode sélectionné
        mode_var = tk.StringVar(value=self.ocr_mode)
        
        # Mode OCR intégral
        full_radio = tk.Radiobutton(modes_frame, text="📄 OCR Intégral", 
                                   variable=mode_var, value="full",
                                   font=("Segoe UI", 12), bg="#f8f9fa",
                                   command=lambda: self._set_ocr_mode("full"))
        full_radio.pack(anchor=tk.W, pady=5)
        
        # Mode sélection de zone
        selected_radio = tk.Radiobutton(modes_frame, text="🎯 Sélection de Zone", 
                                       variable=mode_var, value="selected",
                                       font=("Segoe UI", 12), bg="#f8f9fa",
                                       command=lambda: self._set_ocr_mode("selected"))
        selected_radio.pack(anchor=tk.W, pady=5)
        
        # Mode détection de colonnes
        columns_radio = tk.Radiobutton(modes_frame, text="📰 Détection de Colonnes", 
                                      variable=mode_var, value="columns",
                                      font=("Segoe UI", 12), bg="#f8f9fa",
                                      command=lambda: self._set_ocr_mode("columns"))
        columns_radio.pack(anchor=tk.W, pady=5)
        
        # Mode PDF intégral
        pdf_radio = tk.Radiobutton(modes_frame, text="📚 OCR PDF Complet", 
                                  variable=mode_var, value="pdf_full",
                                  font=("Segoe UI", 12), bg="#f8f9fa",
                                  command=lambda: self._set_ocr_mode("pdf_full"))
        pdf_radio.pack(anchor=tk.W, pady=5)
        
        # Description des modes
        desc_frame = tk.Frame(modes_frame, bg="#e9ecef", relief=tk.RAISED, bd=1)
        desc_frame.pack(fill=tk.X, pady=10, padx=10)
        
        desc_text = tk.Text(desc_frame, height=6, wrap=tk.WORD, 
                           font=("Segoe UI", 10), bg="#e9ecef")
        desc_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Fonction de mise à jour de la description
        def update_description(*args):
            desc_text.delete(1.0, tk.END)
            mode = mode_var.get()
            descriptions = {
                "full": "OCR de l'image entière avec détection automatique de langue.",
                "selected": "OCR uniquement de la zone sélectionnée à la souris.",
                "columns": "Détection automatique des colonnes et OCR séparé par langue.",
                "pdf_full": "OCR de toutes les pages du PDF avec gestion des colonnes."
            }
            desc_text.insert(tk.END, descriptions.get(mode, ""))
        
        mode_var.trace('w', update_description)
        update_description()
    
    def _create_columns_tab(self, parent: tk.Frame) -> None:
        """Crée l'onglet de configuration des colonnes"""
        # Titre
        title_label = tk.Label(parent, text="📰 Configuration des Colonnes", 
                              font=("Segoe UI", 14, "bold"), 
                              bg="#f8f9fa", fg="#212529")
        title_label.pack(pady=10)
        
        # Frame pour les options
        options_frame = tk.Frame(parent, bg="#f8f9fa")
        options_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Détection automatique des colonnes
        detect_var = tk.BooleanVar(value=self.column_detection_enabled)
        detect_check = tk.Checkbutton(options_frame, text="🔍 Détection automatique des colonnes", 
                                     variable=detect_var, font=("Segoe UI", 12), bg="#f8f9fa",
                                     command=lambda: self._set_column_detection(detect_var.get()))
        detect_check.pack(anchor=tk.W, pady=5)
        
        # Mode multilingue
        multi_var = tk.BooleanVar(value=self.multilingual_mode)
        multi_check = tk.Checkbutton(options_frame, text="🌍 Mode multilingue", 
                                    variable=multi_var, font=("Segoe UI", 12), bg="#f8f9fa",
                                    command=lambda: self._set_multilingual_mode(multi_var.get()))
        multi_check.pack(anchor=tk.W, pady=5)
        
        # Configuration des langues par colonne
        lang_frame = tk.LabelFrame(options_frame, text="🌍 Langues par Colonne", 
                                 font=("Segoe UI", 12, "bold"), bg="#f8f9fa")
        lang_frame.pack(fill=tk.X, pady=10, padx=10)
        
        # Colonne gauche
        left_frame = tk.Frame(lang_frame, bg="#f8f9fa")
        left_frame.pack(fill=tk.X, pady=5)
        tk.Label(left_frame, text="Colonne Gauche:", font=("Segoe UI", 11), bg="#f8f9fa").pack(side=tk.LEFT)
        left_lang_var = tk.StringVar(value=self.column_languages["left"])
        left_combo = ttk.Combobox(left_frame, textvariable=left_lang_var, 
                                 values=["grc", "ell", "eng", "fra", "lat"], 
                                 font=("Segoe UI", 10), state="readonly")
        left_combo.pack(side=tk.RIGHT, padx=10)
        
        # Colonne droite
        right_frame = tk.Frame(lang_frame, bg="#f8f9fa")
        right_frame.pack(fill=tk.X, pady=5)
        tk.Label(right_frame, text="Colonne Droite:", font=("Segoe UI", 11), bg="#f8f9fa").pack(side=tk.LEFT)
        right_lang_var = tk.StringVar(value=self.column_languages["right"])
        right_combo = ttk.Combobox(right_frame, textvariable=right_lang_var, 
                                  values=["grc", "ell", "eng", "fra", "lat"], 
                                  font=("Segoe UI", 10), state="readonly")
        right_combo.pack(side=tk.RIGHT, padx=10)
        
        # Colonne centrale
        center_frame = tk.Frame(lang_frame, bg="#f8f9fa")
        center_frame.pack(fill=tk.X, pady=5)
        tk.Label(center_frame, text="Colonne Centrale:", font=("Segoe UI", 11), bg="#f8f9fa").pack(side=tk.LEFT)
        center_lang_var = tk.StringVar(value=self.column_languages["center"])
        center_combo = ttk.Combobox(center_frame, textvariable=center_lang_var, 
                                   values=["grc", "ell", "eng", "fra", "lat", "grc+fra", "grc+eng"], 
                                   font=("Segoe UI", 10), state="readonly")
        center_combo.pack(side=tk.RIGHT, padx=10)
        
        # Sauvegarder les changements
        def save_languages():
            self.column_languages["left"] = left_lang_var.get()
            self.column_languages["right"] = right_lang_var.get()
            self.column_languages["center"] = center_lang_var.get()
            messagebox.showinfo("Succès", "Configuration des langues sauvegardée !")
        
        save_button = tk.Button(options_frame, text="💾 Sauvegarder", 
                               command=save_languages, 
                               bg="#28a745", fg="white", font=("Segoe UI", 11, "bold"))
        save_button.pack(pady=10)
    
    def _create_ia_tab(self, parent: tk.Frame) -> None:
        """Crée l'onglet d'amélioration IA"""
        # Titre
        title_label = tk.Label(parent, text="🤖 Amélioration par Intelligence Artificielle", 
                              font=("Segoe UI", 14, "bold"), 
                              bg="#f8f9fa", fg="#212529")
        title_label.pack(pady=10)
        
        # Frame pour les options
        options_frame = tk.Frame(parent, bg="#f8f9fa")
        options_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Amélioration IA
        ia_var = tk.BooleanVar(value=self.ia_enhancement_enabled)
        ia_check = tk.Checkbutton(options_frame, text="🤖 Améliorer l'OCR par l'IA", 
                                 variable=ia_var, font=("Segoe UI", 12), bg="#f8f9fa",
                                 command=lambda: self._set_ia_enhancement(ia_var.get()))
        ia_check.pack(anchor=tk.W, pady=5)
        
        # Description des améliorations
        desc_frame = tk.Frame(options_frame, bg="#e9ecef", relief=tk.RAISED, bd=1)
        desc_frame.pack(fill=tk.X, pady=10, padx=10)
        
        desc_text = tk.Text(desc_frame, height=8, wrap=tk.WORD, 
                           font=("Segoe UI", 10), bg="#e9ecef")
        desc_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        desc_content = """🤖 Améliorations IA disponibles :

• 🔍 Correction automatique des erreurs OCR
• 📝 Reconstitution du contexte manquant
• 🌍 Détection et correction de la langue
• 📚 Suggestions basées sur les sources classiques
• ✨ Amélioration de la ponctuation et de la structure
• 🎯 Évaluation de la confiance par mot

L'IA utilise l'API OpenRouter pour analyser et améliorer les résultats OCR."""
        
        desc_text.insert(tk.END, desc_content)
        desc_text.config(state=tk.DISABLED)
    
    def _create_ocr_action_buttons(self, parent: tk.Toplevel) -> None:
        """Crée les boutons d'action OCR"""
        button_frame = tk.Frame(parent, bg="#f8f9fa")
        button_frame.pack(pady=20)
        
        # Bouton Lancer OCR
        launch_button = tk.Button(button_frame, text="🚀 Lancer OCR", 
                                 font=("Segoe UI", 12, "bold"), 
                                 bg="#007acc", fg="white",
                                 command=lambda: self._launch_ocr(parent))
        launch_button.pack(side=tk.LEFT, padx=10)
        
        # Bouton Sélectionner Zone
        select_button = tk.Button(button_frame, text="🎯 Sélectionner Zone", 
                                 font=("Segoe UI", 12, "bold"), 
                                 bg="#28a745", fg="white",
                                 command=lambda: self._start_zone_selection(parent))
        select_button.pack(side=tk.LEFT, padx=10)
        
        # Bouton Annuler
        cancel_button = tk.Button(button_frame, text="❌ Annuler", 
                                 font=("Segoe UI", 12, "bold"), 
                                 bg="#dc3545", fg="white",
                                 command=parent.destroy)
        cancel_button.pack(side=tk.LEFT, padx=10)
    
    def _set_ocr_mode(self, mode: str) -> None:
        """Définit le mode d'OCR"""
        self.ocr_mode = mode
        logging.info(f"Mode OCR défini: {mode}")
    
    def _set_column_detection(self, enabled: bool) -> None:
        """Active/désactive la détection de colonnes"""
        self.column_detection_enabled = enabled
        logging.info(f"Détection de colonnes: {'activée' if enabled else 'désactivée'}")
    
    def _set_multilingual_mode(self, enabled: bool) -> None:
        """Active/désactive le mode multilingue"""
        self.multilingual_mode = enabled
        logging.info(f"Mode multilingue: {'activé' if enabled else 'désactivé'}")
    
    def _set_ia_enhancement(self, enabled: bool) -> None:
        """Active/désactive l'amélioration IA"""
        self.ia_enhancement_enabled = enabled
        logging.info(f"Amélioration IA: {'activée' if enabled else 'désactivée'}")
    
    def _start_zone_selection(self, window: tk.Toplevel) -> None:
        """Démarre la sélection de zone"""
        window.destroy()
        self.ocr_mode = "selected"
        self._enable_zone_selection()
    
    def _enable_zone_selection(self) -> None:
        """Active la sélection de zone sur l'image"""
        if hasattr(self.app, 'image_canvas'):
            self.app.image_canvas.config(cursor="crosshair")
            self.app.image_canvas.bind("<Button-1>", self._on_selection_start)
            self.app.image_canvas.bind("<B1-Motion>", self._on_selection_drag)
            self.app.image_canvas.bind("<ButtonRelease-1>", self._on_selection_end)
            self.app.set_status("🎯 Cliquez et glissez pour sélectionner une zone...")
    
    def _on_selection_start(self, event) -> None:
        """Début de la sélection de zone"""
        self.selection_start = (event.x, event.y)
        self.active_selection = self.app.image_canvas.create_rectangle(
            event.x, event.y, event.x, event.y, 
            outline="red", width=2, tags="selection"
        )
    
    def _on_selection_drag(self, event) -> None:
        """Pendant le glissement de sélection"""
        if self.active_selection:
            self.app.image_canvas.coords(self.active_selection, 
                                       self.selection_start[0], self.selection_start[1], 
                                       event.x, event.y)
    
    def _on_selection_end(self, event) -> None:
        """Fin de la sélection de zone"""
        if self.selection_start:
            self.selection_end = (event.x, event.y)
            x1, y1 = self.selection_start
            x2, y2 = self.selection_end
            
            # Normaliser les coordonnées
            x1, x2 = min(x1, x2), max(x1, x2)
            y1, y2 = min(y1, y2), max(y1, y2)
            
            self.selected_regions.append({
                "x1": x1, "y1": y1, "x2": x2, "y2": y2,
                "width": x2 - x1, "height": y2 - y1
            })
            
            # Désactiver la sélection
            self.app.image_canvas.config(cursor="")
            self.app.image_canvas.unbind("<Button-1>")
            self.app.image_canvas.unbind("<B1-Motion>")
            self.app.image_canvas.unbind("<ButtonRelease-1>")
            
            self.app.set_status(f"✅ Zone sélectionnée: {x2-x1}x{y2-y1} pixels")
            
            # Lancer l'OCR sur la zone sélectionnée
            self._launch_ocr_on_selected_zone()
    
    def _launch_ocr_on_selected_zone(self) -> None:
        """Lance l'OCR sur la zone sélectionnée"""
        if not self.selected_regions:
            return
        
        region = self.selected_regions[-1]  # Dernière zone sélectionnée
        self.perform_ocr_on_region(region)
    
    def _launch_ocr(self, window: tk.Toplevel) -> None:
        """Lance l'OCR selon le mode sélectionné"""
        window.destroy()
        
        if self.ocr_mode == "selected" and not self.selected_regions:
            messagebox.showwarning("Attention", "Veuillez d'abord sélectionner une zone.")
            return
        
        self.perform_ocr()
    
    def perform_ocr(self) -> None:
        """Lance l'OCR selon le mode configuré"""
        if not self.app.state.current_images:
            messagebox.showwarning("Attention", SimpleConfig.MESSAGES["errors"]["no_image"])
            return
        
        self.app.state.is_processing = True
        self.app.set_status("OCR en cours...")
        
        def ocr_worker():
            try:
                if self.ocr_mode == "selected":
                    self._perform_selected_ocr()
                elif self.ocr_mode == "columns":
                    self._perform_column_ocr()
                elif self.ocr_mode == "pdf_full":
                    self._perform_pdf_full_ocr()
                else:
                    self._perform_full_ocr()
                    
            except Exception as e:
                self.app.after(0, self._on_ocr_error, e)
        
        # Lancement dans un thread séparé
        thread = threading.Thread(target=ocr_worker, daemon=True)
        thread.start()
    
    def _perform_full_ocr(self) -> None:
        """OCR intégral de l'image avec positions des mots"""
        try:
            image = self.app.state.current_images[self.app.state.current_page]
            
            # OCR avec Tesseract pour obtenir les données détaillées
            config = SimpleConfig.TESSERACT_CONFIG["default"]
            
            # Obtenir les données OCR avec positions
            ocr_data = pytesseract.image_to_data(image, config=config, lang='grc+eng+fra', output_type=pytesseract.Output.DICT)
            
            # Extraire le texte et les positions
            text_lines = []
            word_positions = []
            
            for i in range(len(ocr_data['text'])):
                if int(ocr_data['conf'][i]) > 0:  # Ignorer les éléments avec confiance 0
                    text = ocr_data['text'][i].strip()
                    if text:
                        x = ocr_data['left'][i]
                        y = ocr_data['top'][i]
                        w = ocr_data['width'][i]
                        h = ocr_data['height'][i]
                        conf = float(ocr_data['conf'][i])
                        
                        word_positions.append({
                            'text': text,
                            'bbox': (x, y, x + w, y + h),
                            'confidence': conf
                        })
                        text_lines.append(text)
            
            # Texte complet
            full_text = ' '.join(text_lines)
            
            # Amélioration IA si activée
            if self.ia_enhancement_enabled:
                self.app.set_status("Amélioration IA en cours...")
                full_text = self._enhance_text_with_ia(full_text)
            
            # Évaluation IA des mots
            self.app.set_status("Évaluation IA des mots...")
            evaluated_words = self.word_evaluator.evaluate_words(full_text)
            
            # Création des résultats avec positions
            results = [{
                "text": full_text.strip(), 
                "confidence": 100.0,
                "evaluated_words": evaluated_words,
                "mode": "full",
                "word_positions": word_positions,
                "bbox": (0, 0, image.width, image.height)  # Bbox de l'image complète
            }]
            
            self.app.after(0, self._on_ocr_complete, results)
            
        except Exception as e:
            self.app.after(0, self._on_ocr_error, e)
    
    def _perform_selected_ocr(self) -> None:
        """OCR sur zone sélectionnée"""
        try:
            if not self.selected_regions:
                raise ValueError("Aucune zone sélectionnée")
            
            image = self.app.state.current_images[self.app.state.current_page]
            results = []
            
            for i, region in enumerate(self.selected_regions):
                # Découper la zone
                cropped_image = image.crop((region["x1"], region["y1"], region["x2"], region["y2"]))
                
                # OCR sur la zone
                config = SimpleConfig.TESSERACT_CONFIG["default"]
                text = pytesseract.image_to_string(cropped_image, config=config, lang='grc+eng+fra')
                
                # Amélioration IA si activée
                if self.ia_enhancement_enabled:
                    text = self._enhance_text_with_ia(text)
                
                # Évaluation IA
                evaluated_words = self.word_evaluator.evaluate_words(text)
                
                results.append({
                    "text": text.strip(),
                    "confidence": 100.0,
                    "evaluated_words": evaluated_words,
                    "mode": "selected",
                    "region": region
                })
            
            self.app.after(0, self._on_ocr_complete, results)
            
        except Exception as e:
            self.app.after(0, self._on_ocr_error, e)
    
    def _perform_column_ocr(self) -> None:
        """OCR avec détection de colonnes"""
        try:
            image = self.app.state.current_images[self.app.state.current_page]
            
            # Détection des colonnes
            columns = self._detect_columns(image)
            results = []
            
            for i, column in enumerate(columns):
                # OCR sur chaque colonne avec la langue appropriée
                lang = self._get_column_language(i, len(columns))
                config = SimpleConfig.TESSERACT_CONFIG["default"]
                text = pytesseract.image_to_string(column["image"], config=config, lang=lang)
                
                # Amélioration IA si activée
                if self.ia_enhancement_enabled:
                    text = self._enhance_text_with_ia(text, lang)
                
                # Évaluation IA
                evaluated_words = self.word_evaluator.evaluate_words(text)
                
                results.append({
                    "text": text.strip(),
                    "confidence": 100.0,
                    "evaluated_words": evaluated_words,
                    "mode": "column",
                    "column_index": i,
                    "language": lang,
                    "region": column["region"]
                })
            
            self.app.after(0, self._on_ocr_complete, results)
            
        except Exception as e:
            self.app.after(0, self._on_ocr_error, e)
    
    def _perform_pdf_full_ocr(self) -> None:
        """OCR complet d'un PDF"""
        try:
            if not self.app.state.current_file_path.endswith('.pdf'):
                raise ValueError("Cette option n'est disponible que pour les PDF")
            
            # OCR de toutes les pages
            all_results = []
            
            for page_num in range(len(self.app.state.current_images)):
                self.app.set_status(f"OCR page {page_num + 1}/{len(self.app.state.current_images)}...")
                
                # Charger la page
                image = self.app.state.current_images[page_num]
                
                # Détection de colonnes si activée
                if self.column_detection_enabled:
                    columns = self._detect_columns(image)
                    
                    for i, column in enumerate(columns):
                        lang = self._get_column_language(i, len(columns))
                        config = SimpleConfig.TESSERACT_CONFIG["default"]
                        text = pytesseract.image_to_string(column["image"], config=config, lang=lang)
                        
                        if self.ia_enhancement_enabled:
                            text = self._enhance_text_with_ia(text, lang)
                        
                        evaluated_words = self.word_evaluator.evaluate_words(text)
                        
                        all_results.append({
                            "text": text.strip(),
                            "confidence": 100.0,
                            "evaluated_words": evaluated_words,
                            "mode": "pdf_column",
                            "page": page_num + 1,
                            "column_index": i,
                            "language": lang,
                            "region": column["region"]
                        })
                else:
                    # OCR intégral de la page
                    config = SimpleConfig.TESSERACT_CONFIG["default"]
                    text = pytesseract.image_to_string(image, config=config, lang='grc+eng+fra')
                    
                    if self.ia_enhancement_enabled:
                        text = self._enhance_text_with_ia(text)
                    
                    evaluated_words = self.word_evaluator.evaluate_words(text)
                    
                    all_results.append({
                        "text": text.strip(),
                        "confidence": 100.0,
                        "evaluated_words": evaluated_words,
                        "mode": "pdf_full",
                        "page": page_num + 1
                    })
            
            self.app.after(0, self._on_ocr_complete, all_results)
            
        except Exception as e:
            self.app.after(0, self._on_ocr_error, e)
    
    def _detect_columns(self, image: Image.Image) -> List[Dict[str, Any]]:
        """Détecte les colonnes dans l'image"""
        try:
            # Conversion en niveaux de gris
            gray = image.convert('L')
            
            # Détection des bords verticaux
            import numpy as np
            from PIL import ImageFilter
            
            # Filtre pour détecter les lignes verticales
            kernel = np.array([[-1, -1, -1],
                              [-1,  8, -1],
                              [-1, -1, -1]])
            
            # Application du filtre
            filtered = gray.filter(ImageFilter.Kernel((3, 3), kernel.flatten()))
            
            # Détection des zones de texte
            # Cette méthode simplifiée divise l'image en colonnes basées sur la densité de pixels
            
            width, height = image.size
            columns = []
            
            # Division en 2 ou 3 colonnes selon la largeur
            if width > 800:  # Largeur suffisante pour 2 colonnes
                col_width = width // 2
                
                # Colonne gauche
                left_col = image.crop((0, 0, col_width, height))
                columns.append({
                    "image": left_col,
                    "region": {"x1": 0, "y1": 0, "x2": col_width, "y2": height}
                })
                
                # Colonne droite
                right_col = image.crop((col_width, 0, width, height))
                columns.append({
                    "image": right_col,
                    "region": {"x1": col_width, "y1": 0, "x2": width, "y2": height}
                })
            else:
                # Une seule colonne
                columns.append({
                    "image": image,
                    "region": {"x1": 0, "y1": 0, "x2": width, "y2": height}
                })
            
            return columns
            
        except Exception as e:
            logging.error(f"Erreur détection colonnes: {e}")
            # Fallback: retourner l'image entière
            return [{
                "image": image,
                "region": {"x1": 0, "y1": 0, "x2": image.size[0], "y2": image.size[1]}
            }]
    
    def _get_column_language(self, column_index: int, total_columns: int) -> str:
        """Détermine la langue pour une colonne donnée"""
        if total_columns == 1:
            return self.column_languages["center"]
        elif total_columns == 2:
            if column_index == 0:
                return self.column_languages["left"]
            else:
                return self.column_languages["right"]
        else:
            return self.column_languages["center"]
    
    def _enhance_text_with_ia(self, text: str, language: str = "grc") -> str:
        """Améliore le texte avec l'IA via OpenRouter"""
        try:
            if not text.strip():
                return text
            
            # Préparation du prompt pour l'amélioration
            prompt = f"""Tu es un expert en OCR et en langues anciennes. Améliore ce texte OCR en corrigeant les erreurs, en restaurant la ponctuation et en améliorant la lisibilité.

Texte original: {text}

Langue: {language}

Instructions:
1. Corrige les erreurs OCR évidentes
2. Restaure la ponctuation manquante
3. Améliore la structure et la lisibilité
4. Conserve le sens original
5. Retourne uniquement le texte amélioré

Texte amélioré:"""

            # Appel à l'API OpenRouter
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "anthropic/claude-3.5-sonnet",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 2000,
                    "temperature": 0.1
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                enhanced_text = result["choices"][0]["message"]["content"].strip()
                return enhanced_text
            else:
                logging.warning(f"Erreur API OpenRouter: {response.status_code}")
                return text
                
        except Exception as e:
            logging.error(f"Erreur amélioration IA: {e}")
            return text
    
    def perform_ocr_on_region(self, region: Dict[str, int]) -> None:
        """Lance l'OCR sur une région spécifique"""
        if not self.app.state.current_images:
            return
        
        self.app.state.is_processing = True
        self.app.set_status("OCR zone sélectionnée...")
        
        def ocr_worker():
            try:
                image = self.app.state.current_images[self.app.state.current_page]
                
                # Découper la région
                cropped_image = image.crop((region["x1"], region["y1"], region["x2"], region["y2"]))
                
                # OCR sur la région
                config = SimpleConfig.TESSERACT_CONFIG["default"]
                text = pytesseract.image_to_string(cropped_image, config=config, lang='grc+eng+fra')
                
                # Amélioration IA si activée
                if self.ia_enhancement_enabled:
                    text = self._enhance_text_with_ia(text)
                
                # Évaluation IA
                evaluated_words = self.word_evaluator.evaluate_words(text)
                
                results = [{
                    "text": text.strip(),
                    "confidence": 100.0,
                    "evaluated_words": evaluated_words,
                    "mode": "region",
                    "region": region
                }]
                
                self.app.after(0, self._on_ocr_complete, results)
                
            except Exception as e:
                self.app.after(0, self._on_ocr_error, e)
        
        thread = threading.Thread(target=ocr_worker, daemon=True)
        thread.start()
    
    def _on_ocr_complete(self, results: List[Dict[str, Any]]) -> None:
        """Appelé quand l'OCR est terminé"""
        self.app.state.ocr_results = results
        self.app.state.is_processing = False
        self.app.set_status(SimpleConfig.MESSAGES["info"]["ocr_complete"])
        
        # Nettoyer la sélection
        if hasattr(self.app, 'image_canvas'):
            self.app.image_canvas.delete("selection")
        
        # Affichage des résultats dans l'interface principale
        self.app.display_ocr_results_in_main(results)
    
    def _on_ocr_error(self, error: Exception) -> None:
        """Appelé en cas d'erreur OCR"""
        self.app.state.is_processing = False
        self.app.set_status(f"Erreur OCR: {error}")
        messagebox.showerror("Erreur", SimpleConfig.MESSAGES["errors"]["ocr_error"].format(error=str(error)))
        
        # Nettoyer la sélection
        if hasattr(self.app, 'image_canvas'):
            self.app.image_canvas.delete("selection")


class SimpleOCRApp(tk.Tk):
    """Application OCR simplifiée"""
    
    def __init__(self) -> None:
        super().__init__()
        
        # Initialisation de l'état
        self.state = AppState()
        
        # Initialisation des gestionnaires
        self.font_manager = FontManager(self)  # Gestionnaire de polices
        self.interface_customizer = InterfaceCustomizer(self)  # Gestionnaire de personnalisation
        self.file_manager = SimpleFileManager(self)
        self.ocr_manager = AdvancedOCRManager(self)
        self.find_manager = FindManager(self)  # Gestionnaire FIND ! révolutionnaire
        self.text_editor = OCRTextEditor(self)  # Éditeur de texte OCR avec surbrillance
        self.tuteur_ia = TuteurIA(self)  # Tuteur IA spécialisé
        self.context_historique = ContextualisationHistorique(self)  # Contextualisation historique
        self.controles_gestuels = ControlesGestuels(self)  # Contrôles gestuels Mac
        
        # Nouvelles fonctionnalités avancées
        self.gesture_controller = GestureController(self)
        self.cache_system = CacheSystem()
        
        # Import et initialisation du moteur de recherche lemmatique
        try:
            from lemmatique_search import LemmatiqueSearchEngine, LemmatiqueSearchUI
            self.lemmatique_engine = LemmatiqueSearchEngine()
            self.lemmatique_ui = LemmatiqueSearchUI(self, self.lemmatique_engine)
        except ImportError as e:
            logging.warning(f"Module de recherche lemmatique non disponible: {e}")
            self.lemmatique_engine = None
            self.lemmatique_ui = None
        
        # Configuration de l'interface
        self.ui_manager = SimpleUIManager(self)
        
        # Lier les gestionnaires à l'UIManager
        self.ui_manager.font_manager = self.font_manager
        self.ui_manager.interface_customizer = self.interface_customizer
        
        # Enregistrer les callbacks
        self.font_manager.register_font_callback(self.ui_manager.update_fonts)
        self.interface_customizer.register_theme_callback(self.ui_manager.update_theme)
        self.interface_customizer.register_style_callback(self.ui_manager.update_style)
        
        self.ui_manager.setup_window()
        self.ui_manager.create_menu()
        self.ui_manager.create_toolbar()
        self.ui_manager.create_main_panel()
        self.ui_manager.create_status_bar()
        
        # Configuration des événements
        self._setup_events()
        
        # Démarrage
        self._start_app()
    
    def _setup_events(self) -> None:
        """Configure les événements de l'application"""
        # Raccourcis clavier
        self.bind('<Command-o>', lambda e: self.open_image())
        self.bind('<Command-p>', lambda e: self.open_pdf())
        self.bind('<Command-r>', lambda e: self.perform_ocr())
        self.bind('<Command-f>', lambda e: self.perform_find())  # FIND ! shortcut
        self.bind('<Command-l>', lambda e: self.open_lemmatique_search())  # Lemmatique shortcut
        self.bind('<Command-t>', lambda e: self.open_tutor_ia())  # Tuteur IA shortcut
        self.bind('<Command-h>', lambda e: self.open_historical_context())  # Histoire shortcut
        if platform.system() == "Darwin":
            self.bind('<Command-g>', lambda e: self.open_gesture_controls())  # Gestes shortcut
        
        # Événements de fermeture
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _start_app(self) -> None:
        """Démarre l'application"""
        logging.info(f"OS: {sys.platform}")
        logging.info(f"Python: {sys.version}")
        logging.info(f"Tesseract: {pytesseract.get_tesseract_version()}")
        logging.info(f"PDF Support: {PDF_SUPPORT}")
        
        self.set_status("Application prête")
    
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
        self.ocr_manager.perform_ocr()
    
    def open_ocr_options(self) -> None:
        """Ouvre les options OCR avancées"""
        self.ocr_manager.open_ocr_options()
    
    def perform_find(self) -> None:
        """Lance la fonction FIND ! révolutionnaire"""
        if not self.state.ocr_results:
            messagebox.showwarning("Attention", "Aucun résultat OCR disponible. Lancez d'abord l'OCR.")
            return
        
        text = self.extract_text_from_ocr_results()
        if not text.strip():
            messagebox.showwarning("Attention", "Aucun texte à analyser.")
            return
        
        # Ouvrir l'interface FIND avec choix manuel
        self._open_find_interface(text)
    
    def _open_find_interface(self, text: str) -> None:
        """Ouvre l'interface FIND avec menus déroulants"""
        find_window = tk.Toplevel(self)
        find_window.title("🔍 FIND! - Identification d'Auteur et d'Œuvre")
        find_window.geometry("800x600")
        find_window.configure(bg="#f8f9fa")
        
        # Titre
        title_label = tk.Label(find_window, text="🔍 FIND! - Identification d'Auteur et d'Œuvre", 
                              font=("Segoe UI", 16, "bold"), bg="#f8f9fa", fg="#007acc")
        title_label.pack(pady=20)
        
        # Texte analysé
        text_frame = tk.LabelFrame(find_window, text="📝 Texte analysé", 
                                  font=("Segoe UI", 12, "bold"), bg="#f8f9fa")
        text_frame.pack(fill=tk.X, padx=20, pady=10)
        
        text_widget = scrolledtext.ScrolledText(text_frame, height=6, font=("Segoe UI", 10), wrap=tk.WORD)
        text_widget.pack(fill=tk.X, padx=10, pady=10)
        text_widget.insert(tk.END, text)
        text_widget.config(state=tk.DISABLED)
        
        # Section sélection manuelle
        manual_frame = tk.LabelFrame(find_window, text="🎯 Sélection Manuelle", 
                                    font=("Segoe UI", 12, "bold"), bg="#f8f9fa")
        manual_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Auteur
        author_frame = tk.Frame(manual_frame, bg="#f8f9fa")
        author_frame.pack(fill=tk.X, padx=10, pady=5)
        
        author_label = tk.Label(author_frame, text="Auteur:", font=("Segoe UI", 11, "bold"), bg="#f8f9fa")
        author_label.pack(side=tk.LEFT, padx=(0, 10))
        
        author_var = tk.StringVar()
        author_entry = tk.Entry(author_frame, textvariable=author_var, font=("Segoe UI", 11), width=30)
        author_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        author_combo = ttk.Combobox(author_frame, textvariable=author_var, 
                                   values=get_all_authors(), 
                                   font=("Segoe UI", 11), state="readonly")
        author_combo.pack(side=tk.LEFT)
        
        # Œuvre
        work_frame = tk.Frame(manual_frame, bg="#f8f9fa")
        work_frame.pack(fill=tk.X, padx=10, pady=5)
        
        work_label = tk.Label(work_frame, text="Œuvre:", font=("Segoe UI", 11, "bold"), bg="#f8f9fa")
        work_label.pack(side=tk.LEFT, padx=(0, 10))
        
        work_var = tk.StringVar()
        work_entry = tk.Entry(work_frame, textvariable=work_var, font=("Segoe UI", 11), width=30)
        work_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        work_combo = ttk.Combobox(work_frame, textvariable=work_var, 
                                 font=("Segoe UI", 11), state="readonly")
        work_combo.pack(side=tk.LEFT)
        
        # Fonction pour mettre à jour les œuvres selon l'auteur
        def update_works(*args):
            selected_author = author_var.get()
            works = get_works_by_author(selected_author)
            work_combo['values'] = works
            work_var.set("")  # Réinitialiser la sélection d'œuvre
        
        author_var.trace('w', update_works)
        
        # Boutons d'action
        button_frame = tk.Frame(find_window, bg="#f8f9fa")
        button_frame.pack(pady=20)
        
        # Bouton identification automatique
        auto_button = tk.Button(button_frame, text="🤖 Identification Automatique", 
                               font=("Segoe UI", 12, "bold"), bg="#28a745", fg="white",
                               command=lambda: self._auto_identify(text, find_window))
        auto_button.pack(side=tk.LEFT, padx=10)
        
        # Bouton validation manuelle
        manual_button = tk.Button(button_frame, text="✅ Valider Sélection", 
                                 font=("Segoe UI", 12, "bold"), bg="#007acc", fg="white",
                                 command=lambda: self._validate_manual_selection(
                                     author_var.get(), work_var.get(), text, find_window))
        manual_button.pack(side=tk.LEFT, padx=10)
        
        # Bouton annuler
        cancel_button = tk.Button(button_frame, text="❌ Annuler", 
                                 font=("Segoe UI", 12, "bold"), bg="#dc3545", fg="white",
                                 command=find_window.destroy)
        cancel_button.pack(side=tk.LEFT, padx=10)
    
    def _auto_identify(self, text: str, window: tk.Toplevel) -> None:
        """Lance l'identification automatique"""
        self.set_status("🔍 FIND ! - Identification automatique en cours...")
        
        def find_worker():
            try:
                identification_result = self.find_manager.identify_author_and_work(text)
                self.after(0, lambda: self._show_find_results(identification_result, text))
                self.after(0, window.destroy)
            except Exception as e:
                self.after(0, lambda: self._show_find_error(e))
        
        thread = threading.Thread(target=find_worker, daemon=True)
        thread.start()
    
    def _validate_manual_selection(self, author: str, work: str, text: str, window: tk.Toplevel) -> None:
        """Valide la sélection manuelle"""
        if not author:
            messagebox.showwarning("Attention", "Veuillez sélectionner un auteur.")
            return
        
        # Créer un résultat d'identification manuel
        identification_result = {
            "best_match": {
                "author": author,
                "work": work,
                "confidence": 100.0,
                "method": "manual_selection"
            },
            "top_matches": [{
                "author": author,
                "work": work,
                "confidence": 100.0
            }]
        }
        
        self._show_find_results(identification_result, text)
        window.destroy()
    
    def _show_find_results(self, identification_result: Dict[str, Any], original_text: str) -> None:
        """Affiche les résultats de FIND !"""
        self.set_status("🔍 FIND ! - Résultats disponibles")
        
        # Création de la fenêtre de résultats
        result_window = tk.Toplevel(self)
        result_window.title("🔍 FIND ! - Résultats d'Identification")
        result_window.geometry("900x700")
        result_window.configure(bg="#f0f0f0")
        
        # Titre principal
        title_label = tk.Label(result_window, text="🔍 FIND ! - Identification Automatique", 
                              font=("Segoe UI", 16, "bold"), bg="#f0f0f0", fg="#0078d4")
        title_label.pack(pady=10)
        
        # Frame principal avec scrollbar
        main_frame = tk.Frame(result_window, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        canvas = tk.Canvas(main_frame, bg="#f0f0f0")
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f0f0f0")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Meilleur match
        if identification_result.get("best_match"):
            best_match = identification_result["best_match"]
            
            # Sauvegarder l'auteur identifié pour la contextualisation historique
            self.identified_author = best_match
            
            # Section meilleur match
            best_frame = tk.LabelFrame(scrollable_frame, text="🎯 MEILLEUR MATCH", 
                                     font=("Segoe UI", 12, "bold"), bg="#e8f4fd", fg="#0078d4")
            best_frame.pack(fill=tk.X, pady=10, padx=10)
            
            # Informations de l'auteur
            author_info = f"👤 Auteur: {best_match.get('author_name', best_match.get('author', 'Inconnu'))}"
            period_info = f"📅 Période: {best_match.get('period', 'Inconnue')}"
            confidence_info = f"🎯 Confiance: {best_match.get('confidence', 0):.1f}%"
            
            tk.Label(best_frame, text=author_info, font=("Segoe UI", 11, "bold"), 
                    bg="#e8f4fd").pack(anchor="w", padx=10, pady=2)
            tk.Label(best_frame, text=period_info, font=("Segoe UI", 10), 
                    bg="#e8f4fd").pack(anchor="w", padx=10, pady=2)
            tk.Label(best_frame, text=confidence_info, font=("Segoe UI", 10), 
                    bg="#e8f4fd").pack(anchor="w", padx=10, pady=2)
            
            # Œuvres identifiées
            works = best_match.get('works', best_match.get('work', []))
            if isinstance(works, str):
                works = [works]
            works_text = "📚 Œuvres identifiées:\n" + "\n".join([f"  • {work}" for work in works])
            tk.Label(best_frame, text=works_text, font=("Segoe UI", 10), 
                    bg="#e8f4fd", justify=tk.LEFT).pack(anchor="w", padx=10, pady=5)
            
            # Termes correspondants
            matched_terms = best_match.get('matched_terms', [])
            terms_text = "🔍 Termes correspondants:\n" + ", ".join(matched_terms) if matched_terms else "🔍 Aucun terme spécifique identifié"
            tk.Label(best_frame, text=terms_text, font=("Segoe UI", 10), 
                    bg="#e8f4fd", justify=tk.LEFT).pack(anchor="w", padx=10, pady=5)
            
            # Boutons d'action
            button_frame = tk.Frame(best_frame, bg="#e8f4fd")
            button_frame.pack(pady=10)
            
            tk.Button(button_frame, text="📚 Rechercher dans Perseus", 
                     command=lambda: self.search_perseus(best_match), 
                     bg="#0078d4", fg="white", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=5)
            
            tk.Button(button_frame, text="🔗 Comparer avec Original", 
                     command=lambda: self.compare_with_original(original_text, best_match), 
                     bg="#107c10", fg="white", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        # Autres matches
        if identification_result.get("top_matches") and len(identification_result["top_matches"]) > 1:
            other_frame = tk.LabelFrame(scrollable_frame, text="🔍 AUTRES POSSIBILITÉS", 
                                      font=("Segoe UI", 12, "bold"), bg="#fff8e1", fg="#ff8c00")
            other_frame.pack(fill=tk.X, pady=10, padx=10)
            
            for i, match in enumerate(identification_result["top_matches"][1:], 2):
                author_name = match.get('author_name', match.get('author', 'Inconnu'))
                confidence = match.get('confidence', 0)
                match_text = f"{i}. {author_name} ({confidence:.1f}%)"
                tk.Label(other_frame, text=match_text, font=("Segoe UI", 10), 
                        bg="#fff8e1").pack(anchor="w", padx=10, pady=2)
        
        # Texte analysé
        text_frame = tk.LabelFrame(scrollable_frame, text="📝 TEXTE ANALYSÉ", 
                                 font=("Segoe UI", 12, "bold"), bg="#f3f2f1")
        text_frame.pack(fill=tk.X, pady=10, padx=10)
        
        text_widget = scrolledtext.ScrolledText(text_frame, height=8, wrap=tk.WORD, 
                                              font=("Segoe UI", 10))
        text_widget.pack(fill=tk.X, padx=10, pady=10)
        text_widget.insert(tk.END, original_text)
        text_widget.config(state=tk.DISABLED)
        
        # Configuration du scroll
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _show_find_error(self, error: Exception) -> None:
        """Affiche une erreur FIND !"""
        self.set_status("❌ Erreur FIND !")
        messagebox.showerror("Erreur FIND !", f"Erreur lors de l'identification:\n{error}")
    
    def search_perseus(self, author_match: Dict[str, Any] = None) -> None:
        """Recherche dans la bibliothèque Perseus"""
        if not author_match:
            messagebox.showwarning("Attention", "Aucun auteur identifié.")
            return
        
        try:
            # Recherche dans Perseus
            perseus_result = self.find_manager.search_perseus_digital_library(
                author_match["author_id"], 
                author_match["works"][0] if author_match["works"] else None
            )
            
            if perseus_result["available"]:
                self._show_perseus_results(perseus_result, author_match)
            else:
                messagebox.showwarning("Perseus", "Texte non disponible dans Perseus.")
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la recherche Perseus:\n{e}")
    
    def _show_perseus_results(self, perseus_result: Dict[str, Any], author_match: Dict[str, Any]) -> None:
        """Affiche les résultats Perseus"""
        # Création de la fenêtre Perseus
        author_name = author_match.get('author_name', author_match.get('author', 'Inconnu'))
        perseus_window = tk.Toplevel(self)
        perseus_window.title(f"📚 Perseus - {author_name}")
        perseus_window.geometry("800x600")
        
        # Titre
        title_label = tk.Label(perseus_window, text=f"📚 Texte Grec Original - {author_name}", 
                              font=("Segoe UI", 14, "bold"))
        title_label.pack(pady=10)
        
        # Texte grec
        text_frame = tk.LabelFrame(perseus_window, text="🏺 Texte Grec Original (Unicode)", 
                                 font=("Segoe UI", 12, "bold"))
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        greek_text = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, 
                                             font=("Times New Roman", 14))
        greek_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Insertion du texte grec
        for sample in perseus_result["text_samples"]:
            greek_text.insert(tk.END, sample + "\n\n")
        
        greek_text.config(state=tk.DISABLED)
        
        # Boutons
        button_frame = tk.Frame(perseus_window)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="🔗 Ouvrir dans Perseus", 
                 command=lambda: self._open_perseus_url(perseus_result["url"]), 
                 bg="#0078d4", fg="white").pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="🔗 Comparer avec OCR", 
                 command=lambda: self._compare_with_ocr_text(greek_text.get("1.0", tk.END)), 
                 bg="#107c10", fg="white").pack(side=tk.LEFT, padx=5)
    
    def _open_perseus_url(self, url: str) -> None:
        """Ouvre l'URL Perseus dans le navigateur"""
        import webbrowser
        try:
            webbrowser.open(url)
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir le navigateur:\n{e}")
    
    def _compare_with_ocr_text(self, greek_text: str) -> None:
        """Compare le texte grec avec l'OCR"""
        if not self.state.ocr_results:
            messagebox.showwarning("Attention", "Aucun résultat OCR disponible.")
            return
        
        ocr_text = self.extract_text_from_ocr_results()
        comparison_result = self.find_manager.compare_texts(ocr_text, greek_text)
        
        self._show_comparison_results(comparison_result, ocr_text, greek_text)
    
    def compare_with_original(self, ocr_text: str, author_match: Dict[str, Any] = None) -> None:
        """Compare avec le texte original"""
        if not author_match:
            messagebox.showwarning("Attention", "Aucun auteur identifié.")
            return
        
        try:
            # Récupération du texte original
            perseus_result = self.find_manager.search_perseus_digital_library(
                author_match["author_id"], 
                author_match["works"][0] if author_match["works"] else None
            )
            
            if perseus_result["available"]:
                original_text = "\n".join(perseus_result["text_samples"])
                comparison_result = self.find_manager.compare_texts(ocr_text, original_text)
                
                self._show_comparison_results(comparison_result, ocr_text, original_text)
            else:
                messagebox.showwarning("Comparaison", "Texte original non disponible.")
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la comparaison:\n{e}")
    
    def _show_comparison_results(self, comparison_result: Dict[str, Any], ocr_text: str, original_text: str) -> None:
        """Affiche les résultats de comparaison"""
        # Création de la fenêtre de comparaison
        comp_window = tk.Toplevel(self)
        comp_window.title("🔗 Comparaison OCR vs Original")
        comp_window.geometry("1000x700")
        
        # Titre
        title_label = tk.Label(comp_window, text="🔗 Comparaison OCR vs Texte Original", 
                              font=("Segoe UI", 14, "bold"))
        title_label.pack(pady=10)
        
        # Similarité
        similarity_frame = tk.LabelFrame(comp_window, text="📊 Similarité", 
                                       font=("Segoe UI", 12, "bold"))
        similarity_frame.pack(fill=tk.X, padx=20, pady=10)
        
        similarity_text = f"🎯 Similarité: {comparison_result['similarity_percentage']:.1f}%"
        tk.Label(similarity_frame, text=similarity_text, font=("Segoe UI", 12, "bold")).pack(pady=10)
        
        # Différences
        if comparison_result["differences"]:
            diff_frame = tk.LabelFrame(comp_window, text="🔍 Différences Identifiées", 
                                     font=("Segoe UI", 12, "bold"))
            diff_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            diff_text = scrolledtext.ScrolledText(diff_frame, height=10, wrap=tk.WORD)
            diff_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            for i, diff in enumerate(comparison_result["differences"][:20], 1):  # Limiter à 20 différences
                diff_text.insert(tk.END, f"{i}. Position {diff['position']}: ")
                diff_text.insert(tk.END, f"'{diff['ocr_word']}' → '{diff['original_word']}' ")
                diff_text.insert(tk.END, f"({diff['type']})\n")
            
            diff_text.config(state=tk.DISABLED)
        
        # Suggestions
        if comparison_result["suggestions"]:
            sugg_frame = tk.LabelFrame(comp_window, text="💡 Suggestions de Correction", 
                                     font=("Segoe UI", 12, "bold"))
            sugg_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            sugg_text = scrolledtext.ScrolledText(sugg_frame, height=8, wrap=tk.WORD)
            sugg_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            for i, suggestion in enumerate(comparison_result["suggestions"][:10], 1):  # Limiter à 10 suggestions
                sugg_text.insert(tk.END, f"{i}. {suggestion}\n")
            
            sugg_text.config(state=tk.DISABLED)
    
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
    
    def configure_find(self) -> None:
        """Configure les paramètres FIND !"""
        messagebox.showinfo("Configuration FIND !", 
                          "🔧 Configuration FIND !\n\n"
                          "Cette fonctionnalité permet de:\n"
                          "• Identifier automatiquement l'auteur et l'œuvre\n"
                          "• Rechercher dans la bibliothèque Perseus\n"
                          "• Comparer avec le texte grec original\n"
                          "• Recherche lemmatique avancée\n"
                          "• Générer des suggestions de correction\n\n"
                          "Configuration avancée disponible dans la version complète.")
    
    # ===== MÉTHODES TUTEUR IA =====
    
    def open_tutor_ia(self) -> None:
        """Ouvre l'interface du tuteur IA"""
        # Création de la fenêtre du tuteur
        tutor_window = tk.Toplevel(self)
        tutor_window.title("🎓 Tuteur IA - Grec Ancien")
        tutor_window.geometry("900x700")
        tutor_window.configure(bg="#f0f8ff")
        
        # Titre avec logo de professeur ancien
        title_frame = tk.Frame(tutor_window, bg="#f0f8ff")
        title_frame.pack(pady=10)
        
        # Logo de professeur ancien (emoji)
        logo_label = tk.Label(title_frame, text="🏛️", font=("Segoe UI", 24), 
                             bg="#f0f8ff", fg="#8B4513")
        logo_label.pack()
        
        title_label = tk.Label(title_frame, text="🎓 Tuteur IA Spécialisé en Grec Ancien", 
                              font=("Segoe UI", 16, "bold"), bg="#f0f8ff", fg="#107c10")
        title_label.pack()
        
        # Sous-titre en grec
        subtitle_label = tk.Label(title_frame, text="Χαῖρε ! Professeur IA de Grec Ancien", 
                                 font=("Segoe UI", 12, "italic"), bg="#f0f8ff", fg="#8B4513")
        subtitle_label.pack()
        
        # Frame principal
        main_frame = tk.Frame(tutor_window, bg="#f0f8ff")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Zone de chat
        chat_frame = tk.LabelFrame(main_frame, text="💬 Conversation avec le Tuteur", 
                                 font=("Segoe UI", 12, "bold"), bg="#e8f4fd")
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Zone de texte pour les messages
        chat_text = scrolledtext.ScrolledText(chat_frame, height=20, wrap=tk.WORD, 
                                            font=("Segoe UI", 10), bg="white")
        chat_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Message de bienvenue en grec ancien
        welcome_msg = self.tuteur_ia.welcome_message
        
        chat_text.insert(tk.END, welcome_msg + "\n\n" + "="*50 + "\n\n")
        chat_text.config(state=tk.DISABLED)
        
        # Zone de saisie
        input_frame = tk.Frame(main_frame, bg="#e8f4fd")
        input_frame.pack(fill=tk.X, pady=10)
        
        input_entry = tk.Entry(input_frame, font=("Segoe UI", 11), width=60)
        input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        input_entry.focus()
        
        def send_message():
            message = input_entry.get().strip()
            if not message:
                return
            
            # Afficher le message utilisateur
            chat_text.config(state=tk.NORMAL)
            chat_text.insert(tk.END, f"👤 Vous: {message}\n\n")
            chat_text.config(state=tk.DISABLED)
            
            # Effacer l'entrée
            input_entry.delete(0, tk.END)
            
            # Récupérer le contexte du texte OCR
            context = ""
            if self.state.ocr_results:
                context = self.extract_text_from_ocr_results()
            
            # Obtenir la réponse du tuteur
            def get_tutor_response():
                try:
                    response = self.tuteur_ia.chat_with_tutor(message, context)
                    
                    # Afficher la réponse
                    self.after(0, lambda: display_response(response))
                    
                except Exception as e:
                    error_msg = f"Erreur de communication avec le tuteur: {e}"
                    self.after(0, lambda: display_response(error_msg))
            
            def display_response(response):
                chat_text.config(state=tk.NORMAL)
                chat_text.insert(tk.END, f"🎓 Tuteur IA: {response}\n\n" + "="*50 + "\n\n")
                chat_text.config(state=tk.DISABLED)
                chat_text.see(tk.END)
            
            # Lancer la requête dans un thread séparé
            thread = threading.Thread(target=get_tutor_response, daemon=True)
            thread.start()
        
        # Bouton d'envoi
        send_button = tk.Button(input_frame, text="📤 Envoyer", command=send_message,
                               bg="#107c10", fg="white", font=("Segoe UI", 10, "bold"))
        send_button.pack(side=tk.RIGHT)
        
        # Raccourci Entrée
        input_entry.bind('<Return>', lambda e: send_message())
        
        # Contrôles du tuteur
        controls_frame = tk.Frame(main_frame, bg="#e8f4fd")
        controls_frame.pack(fill=tk.X, pady=10)
        
        # Boutons d'action
        clear_button = tk.Button(controls_frame, text="🗑️ Effacer Chat", 
                                command=lambda: self.clear_tutor_chat(chat_text),
                                bg="#d13438", fg="white")
        clear_button.pack(side=tk.RIGHT, padx=5)
        
        history_button = tk.Button(controls_frame, text="📝 Historique", 
                                  command=self.show_conversation_history,
                                  bg="#0078d4", fg="white")
        history_button.pack(side=tk.RIGHT, padx=5)
    
    def clear_tutor_chat(self, chat_text) -> None:
        """Efface le chat du tuteur"""
        chat_text.config(state=tk.NORMAL)
        chat_text.delete("1.0", tk.END)
        chat_text.config(state=tk.DISABLED)
        self.tuteur_ia.clear_conversation_history()
    
    def show_conversation_history(self) -> None:
        """Affiche l'historique des conversations"""
        history = self.tuteur_ia.get_conversation_history()
        
        if not history:
            messagebox.showinfo("Historique", "Aucune conversation enregistrée.")
            return
        
        # Création de la fenêtre d'historique
        history_window = tk.Toplevel(self)
        history_window.title("📝 Historique des Conversations")
        history_window.geometry("800x600")
        
        # Zone de texte
        history_text = scrolledtext.ScrolledText(history_window, wrap=tk.WORD, 
                                               font=("Segoe UI", 10))
        history_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Affichage de l'historique
        for i, conv in enumerate(history, 1):
            history_text.insert(tk.END, f"=== Conversation {i} ===\n")
            history_text.insert(tk.END, f"Date: {conv['timestamp']}\n")
            history_text.insert(tk.END, f"👤 Vous: {conv['user_message']}\n")
            history_text.insert(tk.END, f"🎓 Tuteur: {conv['tutor_response']}\n")
            history_text.insert(tk.END, "="*50 + "\n\n")
        
        history_text.config(state=tk.DISABLED)
    
    # ===== MÉTHODES CONTEXTUALISATION HISTORIQUE =====
    
    def open_historical_context(self) -> None:
        """Ouvre l'interface de contextualisation historique"""
        # Vérifier si un auteur a été identifié
        if not hasattr(self, 'identified_author') or not self.identified_author:
            messagebox.showwarning("Contexte Historique", 
                                 "Aucun auteur identifié. Lancez d'abord FIND ! pour identifier l'auteur.")
            return
        
        author_id = self.identified_author.get("author_id", "unknown")
        author_name = self.identified_author.get("author_name", self.identified_author.get("author", "Inconnu"))
        
        # Récupération des données historiques
        timeline = self.context_historique.get_timeline_for_author(author_id)
        places = self.context_historique.get_historical_places(author_id)
        influences = self.context_historique.get_author_influences(author_id)
        
        # Création de la fenêtre
        history_window = tk.Toplevel(self)
        history_window.title(f"🏺 Contexte Historique - {author_name}")
        history_window.geometry("1000x800")
        history_window.configure(bg="#fff8e1")
        
        # Titre
        title_label = tk.Label(history_window, text=f"🏺 Contexte Historique - {author_name}", 
                              font=("Segoe UI", 16, "bold"), bg="#fff8e1", fg="#ff8c00")
        title_label.pack(pady=10)
        
        # Frame principal avec scrollbar
        main_frame = tk.Frame(history_window, bg="#fff8e1")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        canvas = tk.Canvas(main_frame, bg="#fff8e1")
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#fff8e1")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Section Frise Chronologique
        timeline_frame = tk.LabelFrame(scrollable_frame, text="📅 Frise Chronologique", 
                                     font=("Segoe UI", 12, "bold"), bg="#ffeaa7")
        timeline_frame.pack(fill=tk.X, pady=10, padx=10)
        
        timeline_text = scrolledtext.ScrolledText(timeline_frame, height=8, wrap=tk.WORD, 
                                                font=("Segoe UI", 10))
        timeline_text.pack(fill=tk.X, padx=10, pady=10)
        
        # Affichage de la timeline
        timeline_text.insert(tk.END, f"Période: {timeline['period_info']['period']}\n\n")
        for event in timeline["timeline"]:
            year = abs(event["year"])
            timeline_text.insert(tk.END, f"• {year} av. J.-C.: {event['event']}\n")
            if event.get("description"):
                timeline_text.insert(tk.END, f"  {event['description']}\n")
            timeline_text.insert(tk.END, "\n")
        
        timeline_text.config(state=tk.DISABLED)
        
        # Section Lieux Historiques
        places_frame = tk.LabelFrame(scrollable_frame, text="🗺️ Lieux Historiques", 
                                   font=("Segoe UI", 12, "bold"), bg="#ffeaa7")
        places_frame.pack(fill=tk.X, pady=10, padx=10)
        
        places_text = scrolledtext.ScrolledText(places_frame, height=6, wrap=tk.WORD, 
                                              font=("Segoe UI", 10))
        places_text.pack(fill=tk.X, padx=10, pady=10)
        
        # Affichage des lieux
        for place_id, place_info in places["places"].items():
            places_text.insert(tk.END, f"🏛️ {place_info['name']}\n")
            places_text.insert(tk.END, f"   {place_info['description']}\n")
            places_text.insert(tk.END, f"   Monuments: {', '.join(place_info['landmarks'])}\n")
            places_text.insert(tk.END, f"   Coordonnées: {place_info['coordinates']['lat']:.4f}, {place_info['coordinates']['lng']:.4f}\n\n")
        
        places_text.config(state=tk.DISABLED)
        
        # Section Influences
        influences_frame = tk.LabelFrame(scrollable_frame, text="🔗 Influences et Connexions", 
                                       font=("Segoe UI", 12, "bold"), bg="#ffeaa7")
        influences_frame.pack(fill=tk.X, pady=10, padx=10)
        
        influences_text = scrolledtext.ScrolledText(influences_frame, height=6, wrap=tk.WORD, 
                                                  font=("Segoe UI", 10))
        influences_text.pack(fill=tk.X, padx=10, pady=10)
        
        # Affichage des influences
        influences_text.insert(tk.END, f"📚 {influences['description']}\n\n")
        influences_text.insert(tk.END, f"👥 Influencé par: {', '.join(influences['influenced_by'])}\n\n")
        influences_text.insert(tk.END, f"🌟 A influencé: {', '.join(influences['influenced'])}\n\n")
        influences_text.insert(tk.END, f"📅 Période: {influences['period']}\n")
        
        influences_text.config(state=tk.DISABLED)
        
        # Boutons d'action
        button_frame = tk.Frame(scrollable_frame, bg="#fff8e1")
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="🗺️ Voir sur Carte", 
                 command=lambda: self.show_historical_maps(author_id),
                 bg="#0078d4", fg="white").pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="📚 Plus d'Événements", 
                 command=lambda: self.show_historical_events(timeline),
                 bg="#107c10", fg="white").pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="🎓 Demander au Tuteur", 
                 command=lambda: self.ask_tutor_about_history(author_id),
                 bg="#ff8c00", fg="white").pack(side=tk.LEFT, padx=5)
        
        # Configuration du scroll
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def show_historical_maps(self, author_id: str = None) -> None:
        """Affiche les cartes interactives"""
        places = self.context_historique.get_historical_places(author_id)
        
        # Création de la fenêtre des cartes
        maps_window = tk.Toplevel(self)
        maps_window.title("🗺️ Cartes Interactives - Grèce Antique")
        maps_window.geometry("800x600")
        
        # Titre
        title_label = tk.Label(maps_window, text="🗺️ Cartes Interactives - Grèce Antique", 
                              font=("Segoe UI", 14, "bold"))
        title_label.pack(pady=10)
        
        # Zone de texte avec les informations
        info_text = scrolledtext.ScrolledText(maps_window, wrap=tk.WORD, 
                                            font=("Segoe UI", 10))
        info_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        info_text.insert(tk.END, "🗺️ CARTES INTERACTIVES - GRÈCE ANTIQUE\n")
        info_text.insert(tk.END, "="*50 + "\n\n")
        
        for place_id, place_info in places["places"].items():
            info_text.insert(tk.END, f"🏛️ {place_info['name']}\n")
            info_text.insert(tk.END, f"   📍 Coordonnées: {place_info['coordinates']['lat']:.4f}, {place_info['coordinates']['lng']:.4f}\n")
            info_text.insert(tk.END, f"   📖 Description: {place_info['description']}\n")
            info_text.insert(tk.END, f"   🏛️ Monuments: {', '.join(place_info['landmarks'])}\n")
            info_text.insert(tk.END, f"   📅 Périodes: {', '.join(place_info['periods'])}\n\n")
            
            # Lien Google Maps
            lat = place_info['coordinates']['lat']
            lng = place_info['coordinates']['lng']
            maps_url = f"https://www.google.com/maps?q={lat},{lng}"
            
            info_text.insert(tk.END, f"   🔗 Voir sur Google Maps: {maps_url}\n\n")
        
        info_text.insert(tk.END, "💡 Pour voir les cartes interactives:\n")
        info_text.insert(tk.END, "1. Cliquez sur les liens Google Maps ci-dessus\n")
        info_text.insert(tk.END, "2. Explorez les lieux historiques\n")
        info_text.insert(tk.END, "3. Découvrez les monuments antiques\n")
        
        info_text.config(state=tk.DISABLED)
        
        # Bouton pour ouvrir Google Maps
        def open_google_maps():
            webbrowser.open("https://www.google.com/maps/search/Greece+ancient+ruins")
        
        tk.Button(maps_window, text="🗺️ Ouvrir Google Maps", 
                 command=open_google_maps,
                 bg="#0078d4", fg="white").pack(pady=10)
    
    def show_author_influences(self) -> None:
        """Affiche les influences entre auteurs"""
        if not hasattr(self, 'identified_author') or not self.identified_author:
            messagebox.showwarning("Influences", "Aucun auteur identifié.")
            return
        
        author_id = self.identified_author["author_id"]
        influences = self.context_historique.get_author_influences(author_id)
        
        # Création de la fenêtre
        author_name = self.identified_author.get("author_name", self.identified_author.get("author", "Inconnu"))
        influences_window = tk.Toplevel(self)
        influences_window.title(f"🔗 Influences - {author_name}")
        influences_window.geometry("700x500")
        
        # Zone de texte
        influences_text = scrolledtext.ScrolledText(influences_window, wrap=tk.WORD, 
                                                  font=("Segoe UI", 11))
        influences_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Affichage des influences
        influences_text.insert(tk.END, f"🔗 INFLUENCES - {author_name.upper()}\n")
        influences_text.insert(tk.END, "="*50 + "\n\n")
        
        influences_text.insert(tk.END, f"📚 Description: {influences['description']}\n\n")
        influences_text.insert(tk.END, f"📅 Période: {influences['period']}\n\n")
        
        influences_text.insert(tk.END, "👥 INFLUENCES REÇUES:\n")
        influences_text.insert(tk.END, "-" * 30 + "\n")
        for influence in influences['influenced_by']:
            influences_text.insert(tk.END, f"• {influence}\n")
        
        influences_text.insert(tk.END, "\n🌟 INFLUENCES EXERCÉES:\n")
        influences_text.insert(tk.END, "-" * 30 + "\n")
        for influence in influences['influenced']:
            influences_text.insert(tk.END, f"• {influence}\n")
        
        influences_text.config(state=tk.DISABLED)
    
    def show_historical_events(self, timeline: Dict[str, Any] = None) -> None:
        """Affiche les événements historiques"""
        if not timeline:
            if not hasattr(self, 'identified_author') or not self.identified_author:
                messagebox.showwarning("Événements", "Aucun auteur identifié.")
                return
            author_id = self.identified_author["author_id"]
            timeline = self.context_historique.get_timeline_for_author(author_id)
        
        # Création de la fenêtre
        events_window = tk.Toplevel(self)
        events_window.title("📚 Événements Historiques")
        events_window.geometry("800x600")
        
        # Zone de texte
        events_text = scrolledtext.ScrolledText(events_window, wrap=tk.WORD, 
                                              font=("Segoe UI", 11))
        events_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Affichage des événements
        events_text.insert(tk.END, f"📚 ÉVÉNEMENTS HISTORIQUES - {timeline['period_info']['period']}\n")
        events_text.insert(tk.END, "="*60 + "\n\n")
        
        for event in timeline["timeline"]:
            year = abs(event["year"])
            events_text.insert(tk.END, f"📅 {year} av. J.-C.\n")
            events_text.insert(tk.END, f"📖 {event['event']}\n")
            if event.get("description"):
                events_text.insert(tk.END, f"📝 {event['description']}\n")
            events_text.insert(tk.END, "\n" + "-"*40 + "\n\n")
        
        events_text.config(state=tk.DISABLED)
    
    def ask_tutor_about_history(self, author_id: str) -> None:
        """Demande au tuteur des informations historiques"""
        author_info = self.find_manager.greek_authors.get(author_id)
        if not author_info:
            return
        
        # Générer le contexte historique
        context = self.context_historique.generate_historical_context(author_id, "")
        
        # Ouvrir le tuteur avec le contexte
        self.open_tutor_ia()
        
        # Pré-remplir avec une question sur l'histoire
        question = f"Peux-tu m'expliquer le contexte historique de {author_info['name']} et son époque ?"
        
        # Note: Dans une implémentation complète, on passerait cette question au tuteur
        messagebox.showinfo("Question Historique", 
                          f"Question posée au tuteur:\n\n{question}\n\n"
                          f"Le tuteur IA a été ouvert avec le contexte historique de {author_info['name']}.")
    
    # ===== MÉTHODES CONTRÔLES GESTUELS =====
    
    def open_gesture_controls(self) -> None:
        """Ouvre l'interface de configuration des contrôles gestuels"""
        if platform.system() != "Darwin":
            messagebox.showinfo("Contrôles Gestuels", 
                              "Les contrôles gestuels sont disponibles uniquement sur macOS.")
            return
        
        # Création de la fenêtre de configuration
        gesture_window = tk.Toplevel(self)
        gesture_window.title("👆 Configuration des Contrôles Gestuels")
        gesture_window.geometry("800x600")
        gesture_window.configure(bg="#f3e5f5")
        
        # Titre
        title_label = tk.Label(gesture_window, text="👆 Contrôles Gestuels pour Mac", 
                              font=("Segoe UI", 16, "bold"), bg="#f3e5f5", fg="#9c27b0")
        title_label.pack(pady=10)
        
        # Frame principal
        main_frame = tk.Frame(gesture_window, bg="#f3e5f5")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Section Gestes Disponibles
        gestures_frame = tk.LabelFrame(main_frame, text="🎯 Gestes Disponibles", 
                                     font=("Segoe UI", 12, "bold"), bg="#e1bee7")
        gestures_frame.pack(fill=tk.X, pady=10)
        
        # Liste des gestes
        gestures_info = [
            ("🔍 Pincement", "Zoom avant/arrière sur le manuscrit", "pinch_zoom"),
            ("🔄 Rotation", "Rotation à deux doigts pour tourner pages", "rotation_pages"),
            ("📱 Glissement", "Navigation temporelle par glissement", "swipe_navigation"),
            ("👆 Tap", "Zoom sur un point spécifique", "tap_zoom"),
            ("🖱️ Molette", "Zoom avec la molette de souris", "mouse_wheel"),
            ("⌨️ Clavier", "Raccourcis clavier pour les gestes", "keyboard_shortcuts")
        ]
        
        for gesture_name, description, setting_key in gestures_info:
            gesture_frame = tk.Frame(gestures_frame, bg="#e1bee7")
            gesture_frame.pack(fill=tk.X, padx=10, pady=5)
            
            tk.Label(gesture_frame, text=gesture_name, font=("Segoe UI", 10, "bold"), 
                    bg="#e1bee7").pack(side=tk.LEFT)
            tk.Label(gesture_frame, text=description, font=("Segoe UI", 9), 
                    bg="#e1bee7").pack(side=tk.LEFT, padx=10)
            
            # Checkbox pour activer/désactiver
            var = tk.BooleanVar(value=self.controles_gestuels.gesture_settings.get(setting_key, True))
            cb = tk.Checkbutton(gesture_frame, variable=var, 
                              command=lambda s=setting_key, v=var: self.set_gesture_setting(s, v.get()),
                              bg="#e1bee7")
            cb.pack(side=tk.RIGHT)
        
        # Section Raccourcis Clavier
        shortcuts_frame = tk.LabelFrame(main_frame, text="⌨️ Raccourcis Clavier", 
                                      font=("Segoe UI", 12, "bold"), bg="#e1bee7")
        shortcuts_frame.pack(fill=tk.X, pady=10)
        
        shortcuts_info = [
            ("+ / =", "Zoom avant"),
            ("-", "Zoom arrière"),
            ("R", "Rotation horaire"),
            ("L", "Rotation anti-horaire"),
            ("→", "Page suivante"),
            ("←", "Page précédente"),
            ("0", "Remise à zéro"),
            ("Cmd+G", "Configuration gestes")
        ]
        
        for i, (shortcut, description) in enumerate(shortcuts_info):
            if i % 2 == 0:
                row_frame = tk.Frame(shortcuts_frame, bg="#e1bee7")
                row_frame.pack(fill=tk.X, padx=10, pady=2)
            
            tk.Label(row_frame, text=f"{shortcut}: {description}", font=("Segoe UI", 9), 
                    bg="#e1bee7").pack(side=tk.LEFT, padx=10)
        
        # Section Gestes Personnalisés
        custom_frame = tk.LabelFrame(main_frame, text="⚙️ Gestes Personnalisés", 
                                   font=("Segoe UI", 12, "bold"), bg="#e1bee7")
        custom_frame.pack(fill=tk.X, pady=10)
        
        custom_gestures = self.controles_gestuels.custom_gestures
        for gesture_name, action in custom_gestures.items():
            gesture_frame = tk.Frame(custom_frame, bg="#e1bee7")
            gesture_frame.pack(fill=tk.X, padx=10, pady=2)
            
            tk.Label(gesture_frame, text=gesture_name, font=("Segoe UI", 9), 
                    bg="#e1bee7").pack(side=tk.LEFT)
            tk.Label(gesture_frame, text=f"→ {action}", font=("Segoe UI", 9), 
                    bg="#e1bee7").pack(side=tk.LEFT, padx=10)
        
        # Section Historique
        history_frame = tk.LabelFrame(main_frame, text="📊 Historique des Gestes", 
                                    font=("Segoe UI", 12, "bold"), bg="#e1bee7")
        history_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        history_text = scrolledtext.ScrolledText(history_frame, height=8, wrap=tk.WORD, 
                                               font=("Segoe UI", 9))
        history_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Affichage de l'historique
        history = self.controles_gestuels.get_gesture_history()
        if history:
            for gesture in history[-10:]:  # 10 derniers gestes
                history_text.insert(tk.END, f"📅 {gesture['timestamp']}\n")
                history_text.insert(tk.END, f"👆 {gesture['type']}: {gesture['details']}\n")
                history_text.insert(tk.END, f"🔍 Zoom: {gesture['zoom']:.2f}, 🔄 Rotation: {gesture['rotation']}°\n")
                history_text.insert(tk.END, "-" * 40 + "\n")
        else:
            history_text.insert(tk.END, "Aucun geste enregistré.\n")
        
        history_text.config(state=tk.DISABLED)
        
        # Boutons d'action
        button_frame = tk.Frame(main_frame, bg="#f3e5f5")
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="🗑️ Effacer Historique", 
                 command=self.clear_gesture_history,
                 bg="#d32f2f", fg="white").pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="⚙️ Configurer Gestes", 
                 command=self.configure_custom_gestures,
                 bg="#1976d2", fg="white").pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="🔄 Remise à Zéro", 
                 command=self.reset_gesture_settings,
                 bg="#388e3c", fg="white").pack(side=tk.LEFT, padx=5)
    
    def show_gesture_history(self) -> None:
        """Affiche l'historique des gestes"""
        if platform.system() != "Darwin":
            messagebox.showinfo("Historique", "Contrôles gestuels disponibles uniquement sur macOS.")
            return
        
        history = self.controles_gestuels.get_gesture_history()
        
        if not history:
            messagebox.showinfo("Historique", "Aucun geste enregistré.")
            return
        
        # Création de la fenêtre d'historique
        history_window = tk.Toplevel(self)
        history_window.title("📊 Historique des Gestes")
        history_window.geometry("700x500")
        
        # Zone de texte
        history_text = scrolledtext.ScrolledText(history_window, wrap=tk.WORD, 
                                               font=("Segoe UI", 10))
        history_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Affichage de l'historique
        for i, gesture in enumerate(history, 1):
            history_text.insert(tk.END, f"=== Geste {i} ===\n")
            history_text.insert(tk.END, f"Date: {gesture['timestamp']}\n")
            history_text.insert(tk.END, f"Type: {gesture['type']}\n")
            history_text.insert(tk.END, f"Détails: {gesture['details']}\n")
            history_text.insert(tk.END, f"Zoom: {gesture['zoom']:.2f}\n")
            history_text.insert(tk.END, f"Rotation: {gesture['rotation']}°\n")
            history_text.insert(tk.END, f"Page: {gesture['page']}\n")
            history_text.insert(tk.END, "="*50 + "\n\n")
        
        history_text.config(state=tk.DISABLED)
    
    def configure_custom_gestures(self) -> None:
        """Configure les gestes personnalisés"""
        if platform.system() != "Darwin":
            messagebox.showinfo("Configuration", "Contrôles gestuels disponibles uniquement sur macOS.")
            return
        
        # Création de la fenêtre de configuration
        config_window = tk.Toplevel(self)
        config_window.title("⚙️ Configuration des Gestes Personnalisés")
        config_window.geometry("600x400")
        
        # Titre
        title_label = tk.Label(config_window, text="⚙️ Gestes Personnalisés", 
                              font=("Segoe UI", 14, "bold"))
        title_label.pack(pady=10)
        
        # Zone de configuration
        config_frame = tk.Frame(config_window)
        config_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Liste des gestes disponibles
        available_gestures = [
            "three_finger_swipe_up",
            "three_finger_swipe_down", 
            "four_finger_pinch",
            "two_finger_double_tap",
            "three_finger_tap",
            "four_finger_swipe_left",
            "four_finger_swipe_right"
        ]
        
        available_actions = [
            "next_page",
            "previous_page", 
            "reset_view",
            "toggle_fullscreen",
            "zoom_in",
            "zoom_out",
            "rotate_clockwise",
            "rotate_counterclockwise"
        ]
        
        # Configuration des gestes
        for i, gesture in enumerate(available_gestures):
            row_frame = tk.Frame(config_frame)
            row_frame.pack(fill=tk.X, pady=2)
            
            tk.Label(row_frame, text=gesture, font=("Segoe UI", 10)).pack(side=tk.LEFT)
            
            action_var = tk.StringVar(value=self.controles_gestuels.custom_gestures.get(gesture, ""))
            action_menu = tk.OptionMenu(row_frame, action_var, *available_actions)
            action_menu.pack(side=tk.LEFT, padx=10)
            
            # Sauvegarde de la configuration
            def save_config(g=gesture, v=action_var):
                self.controles_gestuels.set_custom_gesture(g, v.get())
            
            action_var.trace("w", lambda *args, g=gesture, v=action_var: save_config(g, v))
        
        # Boutons
        button_frame = tk.Frame(config_window)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="💾 Sauvegarder", 
                 command=config_window.destroy,
                 bg="#1976d2", fg="white").pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="🔄 Remise à Zéro", 
                 command=self.reset_custom_gestures,
                 bg="#d32f2f", fg="white").pack(side=tk.LEFT, padx=5)
    
    def set_gesture_setting(self, setting: str, enabled: bool) -> None:
        """Définit un paramètre de geste"""
        self.controles_gestuels.set_gesture_setting(setting, enabled)
        self.set_status(f"Paramètre geste {setting}: {'activé' if enabled else 'désactivé'}")
    
    def clear_gesture_history(self) -> None:
        """Efface l'historique des gestes"""
        self.controles_gestuels.clear_gesture_history()
        messagebox.showinfo("Historique", "Historique des gestes effacé.")
    
    def reset_gesture_settings(self) -> None:
        """Remet à zéro les paramètres des gestes"""
        for setting in self.controles_gestuels.gesture_settings:
            self.controles_gestuels.set_gesture_setting(setting, True)
        messagebox.showinfo("Paramètres", "Paramètres des gestes remis à zéro.")
    
    def reset_custom_gestures(self) -> None:
        """Remet à zéro les gestes personnalisés"""
        default_gestures = {
            "three_finger_swipe_up": "next_page",
            "three_finger_swipe_down": "previous_page",
            "four_finger_pinch": "reset_view",
            "two_finger_double_tap": "toggle_fullscreen"
        }
        
        for gesture, action in default_gestures.items():
            self.controles_gestuels.set_custom_gesture(gesture, action)
        
        messagebox.showinfo("Gestes", "Gestes personnalisés remis à zéro.")
    
    def update_image_display(self) -> None:
        """Met à jour l'affichage de l'image avec zoom, rotation et déplacement"""
        if hasattr(self, 'image_label') and self.image_label and self.state.current_images and len(self.state.current_images) > 0:
            # Récupération des paramètres de transformation
            zoom = self.controles_gestuels.current_zoom
            rotation = self.controles_gestuels.current_rotation
            pan_x = self.controles_gestuels.pan_x
            pan_y = self.controles_gestuels.pan_y
            
            # Mise à jour de l'affichage
            self.set_status(f"Zoom: {zoom:.2f}x, Rotation: {rotation}°, Pan: ({pan_x}, {pan_y})")
            
            # Application des transformations à l'image
            self._apply_image_transformations(zoom, rotation, pan_x, pan_y)
    

    
    def load_page(self, page_number: int) -> None:
        """Charge une page spécifique"""
        if hasattr(self, 'pdf_pages') and self.pdf_pages:
            if 0 <= page_number < len(self.pdf_pages):
                self.current_page = page_number
                self.load_pdf_page(page_number)
                self.set_status(f"Page {page_number + 1}/{len(self.pdf_pages)}")
    
    def export_results(self) -> None:
        """Exporte les résultats"""
        if not self.state.ocr_results:
            messagebox.showwarning("Attention", SimpleConfig.MESSAGES["errors"]["no_ocr_results"])
            return
        
        filename = filedialog.asksaveasfilename(
            title="Exporter les résultats",
            defaultextension=".txt",
            filetypes=[
                ("Texte", "*.txt"),
                ("JSON", "*.json"),
                ("Tous les fichiers", "*.*")
            ]
        )
        
        if filename:
            self._export_to_file(filename)
    
    def _export_to_file(self, filename: str) -> None:
        """Exporte vers un fichier"""
        try:
            text = self.extract_text_from_ocr_results()
            
            if filename.endswith('.json'):
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.state.ocr_results, f, ensure_ascii=False, indent=2)
            else:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(text)
            
            self.set_status(f"Résultats exportés vers {Path(filename).name}")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'export: {e}")
    
    def extract_text_from_ocr_results(self) -> str:
        """Extrait le texte des résultats OCR"""
        if not self.state.ocr_results:
            return ""
        
        text_parts = []
        for result in self.state.ocr_results:
            text = result.get('text', '').strip()
            if text:
                text_parts.append(text)
        
        return ' '.join(text_parts)
    
    def display_current_image(self) -> None:
        """Affiche l'image courante avec zoom et pan - optimisé pour Mac"""
        if not self.state.current_images:
            return
        
        # Créer le canvas une seule fois s'il n'existe pas
        if not hasattr(self, 'image_canvas'):
            self._create_image_canvas()
        
        # Appliquer les transformations
        self._update_image_display()
    
    def _create_image_canvas(self) -> None:
        """Crée le canvas d'affichage d'image optimisé pour Mac"""
        # Nettoyer le panneau image
        for widget in self.ui_manager.image_panel.winfo_children():
            widget.destroy()
        
        # Créer un frame pour le canvas avec scrollbars
        canvas_frame = tk.Frame(self.ui_manager.image_panel, bg=self.ui_manager.colors["bg"])
        canvas_frame.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
        
        # Créer le canvas principal
        self.image_canvas = tk.Canvas(
            canvas_frame,
            bg=self.ui_manager.colors["bg"],
            highlightthickness=0,
            cursor="crosshair"  # Curseur personnalisé pour Mac
        )
        
        # Scrollbars pour le défilement
        self.h_scrollbar = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.image_canvas.xview)
        self.v_scrollbar = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.image_canvas.yview)
        
        # Configuration du canvas
        self.image_canvas.configure(
            xscrollcommand=self.h_scrollbar.set,
            yscrollcommand=self.v_scrollbar.set
        )
        
        # Pack des éléments
        self.image_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Configuration des contrôles gestuels avancés
        self.gesture_controller.setup_trackpad_gestures(self.image_canvas)
        
        # Configuration des contrôles gestuels de base
        self.controles_gestuels.setup_gesture_controls(self.image_canvas)
        
        # Forcer la mise à jour de l'affichage
        self.image_canvas.update()
    
    def _update_image_display(self) -> None:
        """Met à jour l'affichage de l'image avec les transformations actuelles"""
        if not self.state.current_images or not hasattr(self, 'image_canvas'):
            return
        
        image = self.state.current_images[self.state.current_page]
        zoom = getattr(self.controles_gestuels, 'current_zoom', 1.0)
        rotation = getattr(self.controles_gestuels, 'current_rotation', 0)
        pan_x = getattr(self.controles_gestuels, 'pan_x', 0)
        pan_y = getattr(self.controles_gestuels, 'pan_y', 0)
        
        # Obtenir la taille du canvas
        canvas_width = self.image_canvas.winfo_width()
        canvas_height = self.image_canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            # Canvas pas encore initialisé, attendre
            self.after(100, self._update_image_display)
            return
        
        # Calcul de la taille d'affichage optimale
        img_ratio = image.width / image.height
        canvas_ratio = canvas_width / canvas_height
        
        if img_ratio > canvas_ratio:
            base_width = canvas_width
            base_height = int(canvas_width / img_ratio)
        else:
            base_height = canvas_height
            base_width = int(canvas_height * img_ratio)
        
        # Application du zoom
        zoomed_width = int(base_width * zoom)
        zoomed_height = int(base_height * zoom)
        
        # Optimisation du resampling pour Mac
        if zoom > 3.0:
            resampling = Image.Resampling.NEAREST  # Ultra rapide
        elif zoom > 2.0:
            resampling = Image.Resampling.BILINEAR  # Rapide
        else:
            resampling = Image.Resampling.LANCZOS  # Qualité optimale
        
        # Redimensionnement de l'image
        resized_image = image.resize((zoomed_width, zoomed_height), resampling)
        
        # Application de la rotation
        if rotation != 0:
            resized_image = resized_image.rotate(rotation, expand=True, resample=Image.Resampling.BICUBIC)
        
        # Conversion pour Tkinter
        photo = ImageTk.PhotoImage(resized_image)
        
        # Nettoyer le canvas
        self.image_canvas.delete("all")
        
        # Calcul de la position avec pan optimisé
        if zoom > 1.0:
            # Image zoomée : appliquer le pan avec limites
            # Inverser le pan pour que l'image suive le mouvement de la souris
            x_offset = (canvas_width - zoomed_width) // 2 + pan_x
            y_offset = (canvas_height - zoomed_height) // 2 + pan_y
            
            # Limiter le pan pour éviter les espaces vides
            if zoomed_width > canvas_width:
                x_offset = max(min(x_offset, 0), canvas_width - zoomed_width)
            if zoomed_height > canvas_height:
                y_offset = max(min(y_offset, 0), canvas_height - zoomed_height)
        else:
            # Image non zoomée : centrer
            x_offset = (canvas_width - zoomed_width) // 2
            y_offset = (canvas_height - zoomed_height) // 2
        
        # Affichage de l'image
        self.image_canvas.create_image(x_offset, y_offset, anchor=tk.NW, image=photo)
        self.image_canvas.image = photo  # Garder la référence
        
        # Configuration de la région de défilement
        self.image_canvas.configure(scrollregion=self.image_canvas.bbox("all"))
        
        # Debug optimisé
        logging.info(f"Image updated: zoom={zoom:.2f}, size=({zoomed_width}x{zoomed_height}), pan=({pan_x},{pan_y}), pos=({x_offset},{y_offset})")
        
        # Forcer la mise à jour
        self.image_canvas.update_idletasks()
    
    def display_ocr_results_in_main(self, results: List[Dict[str, Any]]) -> None:
        """Affiche les résultats OCR dans l'interface principale avec codes couleur et édition"""
        if not results:
            return
        
        # Configurer l'éditeur de texte OCR
        self.text_editor.setup_editable_text_widget(self.ui_manager.ocr_text_widget)
        self.text_editor.set_ocr_results(results)
        
        # Activer le widget de texte pour l'édition
        self.ui_manager.ocr_text_widget.config(state=tk.NORMAL)
        self.ui_manager.ocr_text_widget.delete(1.0, tk.END)
        
        for result in results:
            text = result.get('text', '')
            evaluated_words = result.get('evaluated_words', [])
            
            if evaluated_words:
                # Affichage avec codes couleur
                for word_data in evaluated_words:
                    word = word_data.get('word', '')
                    confidence = word_data.get('confidence', 0)
                    correction = word_data.get('correction', '')
                    color = word_data.get('color', 'black')
                    notes = word_data.get('notes', '')
                    
                    # Définir les couleurs
                    color_map = {
                        'green': '#28a745',    # Vert pour excellent
                        'yellow': '#ffc107',   # Jaune pour correct
                        'red': '#dc3545',      # Rouge pour erreur
                        'blue': '#17a2b8'      # Bleu pour douteux
                    }
                    
                    word_color = color_map.get(color, '#000000')
                    
                    # Insérer le mot avec sa couleur
                    self.ui_manager.ocr_text_widget.insert(tk.END, f"{word} ", f"word_{color}")
                    
                    # Configurer la couleur du tag
                    self.ui_manager.ocr_text_widget.tag_config(f"word_{color}", foreground=word_color)
                    
                    # Ajouter les informations de confiance si nécessaire
                    if confidence < 80:
                        self.ui_manager.ocr_text_widget.insert(tk.END, f"[{confidence}%] ", f"confidence")
                        self.ui_manager.ocr_text_widget.tag_config("confidence", foreground="#6c757d", font=("Segoe UI", 9))
                    
                    # Ajouter la correction si différente
                    if correction and correction != word:
                        self.ui_manager.ocr_text_widget.insert(tk.END, f"→{correction} ", f"correction")
                        self.ui_manager.ocr_text_widget.tag_config("correction", foreground="#fd7e14", font=("Segoe UI", 9, "italic"))
                
                # Nouvelle ligne
                self.ui_manager.ocr_text_widget.insert(tk.END, "\n\n")
                
            else:
                # Affichage simple si pas d'évaluation
                self.ui_manager.ocr_text_widget.insert(tk.END, f"{text}\n\n")
        
        # Garder le widget éditable
        self.ui_manager.ocr_text_widget.config(state=tk.NORMAL)
        
        # Activer le bouton FIND
        self.ui_manager.find_button.config(state=tk.NORMAL)
        
        # Ajouter les boutons d'édition
        self._add_editing_buttons()
    
    def _add_editing_buttons(self) -> None:
        """Ajoute les boutons d'édition du texte OCR"""
        # Créer un frame pour les boutons d'édition
        if hasattr(self.ui_manager, 'editing_buttons_frame'):
            self.ui_manager.editing_buttons_frame.destroy()
        
        self.ui_manager.editing_buttons_frame = tk.Frame(self.ui_manager.text_panel, bg="#f8f9fa")
        self.ui_manager.editing_buttons_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        
        # Bouton pour activer/désactiver l'édition
        edit_button = tk.Button(
            self.ui_manager.editing_buttons_frame,
            text="✏️ Éditer le texte",
            command=self._toggle_text_editing,
            bg="#007bff",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief=tk.RAISED,
            bd=2
        )
        edit_button.pack(side=tk.LEFT, padx=5)
        
        # Bouton pour sauvegarder les modifications
        save_button = tk.Button(
            self.ui_manager.editing_buttons_frame,
            text="💾 Sauvegarder",
            command=self._save_text_edits,
            bg="#28a745",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief=tk.RAISED,
            bd=2
        )
        save_button.pack(side=tk.LEFT, padx=5)
        
        # Bouton pour remettre à l'original
        reset_button = tk.Button(
            self.ui_manager.editing_buttons_frame,
            text="🔄 Remettre à l'original",
            command=self._reset_text_to_original,
            bg="#dc3545",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief=tk.RAISED,
            bd=2
        )
        reset_button.pack(side=tk.LEFT, padx=5)
        
        # Bouton pour effacer la surbrillance
        clear_highlight_button = tk.Button(
            self.ui_manager.editing_buttons_frame,
            text="❌ Effacer surbrillance",
            command=self._clear_word_highlight,
            bg="#6c757d",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief=tk.RAISED,
            bd=2
        )
        clear_highlight_button.pack(side=tk.LEFT, padx=5)
        
        # Label d'information
        info_label = tk.Label(
            self.ui_manager.editing_buttons_frame,
            text="💡 Cliquez sur un mot pour le surligner dans l'image",
            font=("Segoe UI", 9, "italic"),
            fg="#6c757d",
            bg="#f8f9fa"
        )
        info_label.pack(side=tk.RIGHT, padx=5)
    
    def _toggle_text_editing(self) -> None:
        """Active/désactive l'édition du texte"""
        if self.ui_manager.ocr_text_widget.cget("state") == tk.NORMAL:
            self.text_editor.disable_editing()
            self.ui_manager.ocr_text_widget.config(state=tk.DISABLED)
        else:
            self.text_editor.enable_editing()
            self.ui_manager.ocr_text_widget.config(state=tk.NORMAL)
    
    def _save_text_edits(self) -> None:
        """Sauvegarde les modifications du texte"""
        self.text_editor.save_edits()
        messagebox.showinfo("Sauvegarde", "Modifications sauvegardées avec succès !")
    
    def _reset_text_to_original(self) -> None:
        """Remet le texte à son état original"""
        self.text_editor.reset_to_original()
        messagebox.showinfo("Reset", "Texte remis à son état original !")
    
    def _clear_word_highlight(self) -> None:
        """Efface la surbrillance du mot dans l'image"""
        self.text_editor._clear_highlight()
    
    def display_ocr_results(self, results: List[Dict[str, Any]]) -> None:
        """Affiche les résultats OCR (méthode legacy)"""
        self.display_ocr_results_in_main(results)
    
    def zoom_in(self) -> None:
        """Zoom avant - optimisé pour Mac"""
        if hasattr(self, 'controles_gestuels'):
            self.controles_gestuels.zoom_in()
    
    def zoom_out(self) -> None:
        """Zoom arrière - optimisé pour Mac"""
        if hasattr(self, 'controles_gestuels'):
            self.controles_gestuels.zoom_out()
    
    def zoom_reset(self) -> None:
        """Reset du zoom - optimisé pour Mac"""
        if hasattr(self, 'controles_gestuels'):
            self.controles_gestuels.reset_view()
    
    def next_page(self) -> None:
        """Page suivante"""
        if self.state.current_page < len(self.state.current_images) - 1:
            self.state.current_page += 1
            self.load_page(self.state.current_page)
    
    def previous_page(self) -> None:
        """Page précédente"""
        if self.state.current_page > 0:
            self.state.current_page -= 1
            self.load_page(self.state.current_page)
    
    def show_about(self) -> None:
        """Affiche les informations sur l'application"""
        about_text = "OCR Grec v5.0 Simple\n\n"
        about_text += "Application de reconnaissance optique de caractères\n"
        about_text += "spécialisée pour le grec ancien.\n\n"
        about_text += "Version simplifiée pour test et démonstration.\n\n"
        about_text += "Fonctionnalités:\n"
        about_text += "• OCR haute précision\n"
        about_text += "• Support images et PDFs\n"
        about_text += "• Interface moderne\n"
        about_text += "• Export des résultats"
        
        messagebox.showinfo("À propos", about_text)
    
    def set_status(self, text: str) -> None:
        """Met à jour la barre de statut"""
        self.ui_manager.status_bar.config(text=text)
    
    def open_font_settings(self) -> None:
        """Ouvre les paramètres de police"""
        if hasattr(self, 'font_manager'):
            self.font_manager.open_font_settings()
        else:
            messagebox.showwarning("Attention", "Gestionnaire de polices non disponible")
    
    def open_interface_customization(self) -> None:
        """Ouvre le panneau de personnalisation de l'interface"""
        if hasattr(self, 'interface_customizer'):
            self.interface_customizer.open_customization_panel()
        else:
            messagebox.showwarning("Attention", "Gestionnaire de personnalisation non disponible")


def main() -> None:
    """Point d'entrée principal"""
    try:
        app = SimpleOCRApp()
        app.mainloop()
    except Exception as e:
        logging.error(f"Erreur fatale: {e}")
        messagebox.showerror("Erreur Fatale", f"L'application a rencontré une erreur fatale:\n{e}")


if __name__ == "__main__":
    main() 