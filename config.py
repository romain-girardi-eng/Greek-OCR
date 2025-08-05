"""
Configuration globale de l'application OCR Grec v5.0
==================================================
Configuration centralisée et optimisée pour la production.
"""

import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class TesseractConfig:
    """Configuration Tesseract optimisée"""
    default: str = "--oem 3 --psm 6"
    single_word: str = "--oem 3 --psm 8"
    sparse: str = "--oem 3 --psm 11"
    block: str = "--oem 3 --psm 3"
    line: str = "--oem 3 --psm 7"


@dataclass
class LanguageConfig:
    """Configuration des langues supportées"""
    code: str
    name: str
    description: str


@dataclass
class ThresholdConfig:
    """Seuils de confiance OCR"""
    reliable: int = 85
    uncertain: int = 70


@dataclass
class PDFConfig:
    """Configuration PDF optimisée"""
    cache_size: int = 50
    batch_size: int = 100
    max_dpi: int = 600
    default_dpi: int = 300
    max_image_size: int = 2048
    memory_limit_per_batch: int = 1024 * 1024 * 1024  # 1GB
    max_concurrent_threads: int = 4


@dataclass
class AIConfig:
    """Configuration IA centralisée"""
    openrouter_api_key: str = "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"
    openrouter_url: str = "https://openrouter.ai/api/v1/chat/completions"
    openrouter_model: str = "anthropic/claude-3-haiku"
    openrouter_max_tokens: int = 1000
    openrouter_temperature: float = 0.3
    openrouter_timeout: int = 30
    claude_url: str = "https://api.anthropic.com/v1/messages"
    claude_model: str = "claude-3-haiku-20240307"
    claude_max_tokens: int = 100
    claude_timeout: int = 10


@dataclass
class UIConfig:
    """Configuration interface utilisateur"""
    window_default_size: str = "1200x800"
    window_min_size: str = "600x500"
    window_title: str = "OCR Grec v5.0"
    fonts_title: tuple = ("Segoe UI", 16, "bold")
    fonts_subtitle: tuple = ("Segoe UI", 14, "bold")
    fonts_normal: tuple = ("Segoe UI", 10)
    fonts_small: tuple = ("Segoe UI", 9)


@dataclass
class ThemeConfig:
    """Configuration des thèmes"""
    light: Dict[str, str] = field(default_factory=lambda: {
        "bg": "#ffffff", "fg": "#1f1f1f", "button_bg": "#f3f2f1",
        "button_fg": "#1f1f1f", "entry_bg": "#ffffff", "entry_fg": "#1f1f1f",
        "highlight_bg": "#0078d4", "highlight_fg": "#ffffff", "menu_bg": "#ffffff",
        "menu_fg": "#1f1f1f", "text_bg": "#faf9f8", "text_fg": "#1f1f1f",
        "accent": "#0078d4", "success": "#107c10", "warning": "#ff8c00",
        "error": "#d13438", "border": "#e1dfdd", "hover": "#f3f2f1"
    })
    dark: Dict[str, str] = field(default_factory=lambda: {
        "bg": "#1a1a1a", "fg": "#e0e0e0", "button_bg": "#2d2d2d",
        "button_fg": "#e0e0e0", "entry_bg": "#2d2d2d", "entry_fg": "#e0e0e0",
        "highlight_bg": "#0078d4", "highlight_fg": "#ffffff", "menu_bg": "#1a1a1a",
        "menu_fg": "#e0e0e0", "text_bg": "#252525", "text_fg": "#e0e0e0",
        "accent": "#0078d4", "success": "#107c10", "warning": "#ff8c00",
        "error": "#d13438", "border": "#404040", "hover": "#3d3d3d"
    })


@dataclass
class MessageConfig:
    """Configuration des messages utilisateur"""
    errors: Dict[str, str] = field(default_factory=lambda: {
        "no_image": "Aucune image chargée",
        "no_ocr_results": "Aucun résultat OCR disponible",
        "processing": "Traitement en cours...",
        "api_error": "Erreur API: {error}",
        "file_error": "Erreur fichier: {error}",
        "ocr_error": "Erreur OCR: {error}"
    })
    info: Dict[str, str] = field(default_factory=lambda: {
        "ocr_complete": "OCR terminé avec succès",
        "corrections_applied": "{count} mots corrigés avec succès",
        "no_corrections": "Aucune correction appliquée",
        "no_doubtful_words": "Aucun mot douteux trouvé"
    })
    help: Dict[str, str] = field(default_factory=lambda: {
        "zoom": "Ctrl + Molette: Zoom\nMolette seule: Défilement\nTrackpad pinch: Zoom",
        "ocr_modes": "Sélectionnez le mode OCR selon votre document",
        "languages": "Choisissez la langue du texte à reconnaître"
    })


class Config:
    """Configuration globale de l'application v5.0"""
    
    # Instances des configurations
    tesseract = TesseractConfig()
    thresholds = ThresholdConfig()
    pdf = PDFConfig()
    ai = AIConfig()
    ui = UIConfig()
    themes = ThemeConfig()
    messages = MessageConfig()
    
    # Langues supportées
    LANGUAGES: Dict[str, LanguageConfig] = {
        "auto": LanguageConfig("grc+eng+fra", "Auto (Grec + Anglais + Français)", "Détection automatique"),
        "grec_ancien": LanguageConfig("grc", "Grec Ancien", "Langue grecque classique"),
        "grec_moderne": LanguageConfig("ell", "Grec Moderne", "Langue grecque moderne"),
        "anglais": LanguageConfig("eng", "Anglais", "Langue anglaise"),
        "francais": LanguageConfig("fra", "Français", "Langue française"),
        "latin": LanguageConfig("lat", "Latin", "Langue latine"),
        "allemand": LanguageConfig("deu", "Allemand", "Langue allemande"),
        "italien": LanguageConfig("ita", "Italien", "Langue italienne")
    }
    
    # Chemins par défaut
    DEFAULT_PATHS = {
        "cache_dir": Path.home() / ".ocr_cache",
        "logs_dir": Path.home() / ".ocr_logs",
        "temp_dir": Path.home() / ".ocr_temp",
        "config_file": Path.home() / ".ocr_config.json"
    }
    
    # Constantes de performance
    PERFORMANCE = {
        "max_image_size": 4096,
        "max_memory_usage": 2 * 1024 * 1024 * 1024,  # 2GB
        "thread_pool_size": 8,
        "cache_ttl": 3600,  # 1 heure
        "batch_timeout": 300  # 5 minutes
    }
    
    @classmethod
    def get_available_languages(cls) -> Dict[str, LanguageConfig]:
        """Retourne les langues réellement disponibles sur le système"""
        try:
            import pytesseract
            available_codes = pytesseract.get_languages()
            
            filtered_languages = {}
            for key, lang_config in cls.LANGUAGES.items():
                if key == "auto":
                    filtered_languages[key] = lang_config
                else:
                    if lang_config.code in available_codes:
                        filtered_languages[key] = lang_config
            
            return filtered_languages
        except Exception:
            return cls.LANGUAGES
    
    @classmethod
    def get_tesseract_config(cls, mode: str = "default") -> str:
        """Retourne la configuration Tesseract pour un mode donné"""
        config_map = {
            "default": cls.tesseract.default,
            "single_word": cls.tesseract.single_word,
            "sparse": cls.tesseract.sparse,
            "block": cls.tesseract.block,
            "line": cls.tesseract.line
        }
        return config_map.get(mode, cls.tesseract.default)
    
    @classmethod
    def get_theme_colors(cls, theme: str = "light") -> Dict[str, str]:
        """Retourne les couleurs d'un thème"""
        return cls.themes.light if theme == "light" else cls.themes.dark
    
    @classmethod
    def get_message(cls, category: str, key: str, **kwargs) -> str:
        """Retourne un message formaté"""
        messages = getattr(cls.messages, category, {})
        message = messages.get(key, "")
        return message.format(**kwargs) if kwargs else message
    
    # Configuration IA pour compatibilité avec les anciens fichiers
    AI_CONFIG = {
        "openrouter": {
            "api_key": "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",
            "url": "https://openrouter.ai/api/v1/chat/completions",
            "model": "anthropic/claude-3-haiku",
            "max_tokens": 1000,
            "temperature": 0.3,
            "timeout": 30
        },
        "claude": {
            "url": "https://api.anthropic.com/v1/messages",
            "model": "claude-3-haiku-20240307",
            "max_tokens": 100,
            "timeout": 10
        }
    }
    
    @classmethod
    def ensure_directories(cls) -> None:
        """Crée les répertoires nécessaires"""
        for path in cls.DEFAULT_PATHS.values():
            if isinstance(path, Path):
                path.mkdir(parents=True, exist_ok=True)
