#!/usr/bin/env python3
"""
Configuration optimisée pour macOS
"""

import platform
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class MacConfig:
    """Configuration spécifique à macOS"""
    
    # Détection du système
    is_macos: bool = platform.system() == "Darwin"
    is_retina: bool = False
    is_apple_silicon: bool = False
    
    # Optimisations Mac
    use_metal: bool = True
    optimize_memory: bool = True
    gesture_support: bool = True
    retina_display: bool = True
    native_menus: bool = True
    
    # Configuration Tesseract optimisée pour Mac
    tesseract_config = {
        "default": "--oem 3 --psm 6 -c tessedit_do_invert=0",
        "single_word": "--oem 3 --psm 8 -c tessedit_do_invert=0",
        "sparse": "--oem 3 --psm 11 -c tessedit_do_invert=0",
        "block": "--oem 3 --psm 3 -c tessedit_do_invert=0",
        "line": "--oem 3 --psm 7 -c tessedit_do_invert=0"
    }
    
    # Configuration UI Mac
    ui_config = {
        "window_title": "OCR Grec Mac v6.0",
        "window_size": "1400x900",
        "min_size": "800x600",
        "mac_style": True,
        "font_family": "SF Pro Display" if platform.system() == "Darwin" else "Segoe UI",
        "font_size": 12,
        "accent_color": "#007aff" if platform.system() == "Darwin" else "#0078d4"
    }
    
    # Configuration IA
    ai_config = {
        "openrouter": {
            "api_key": "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",
            "url": "https://openrouter.ai/api/v1/chat/completions",
            "model": "anthropic/claude-3-haiku",
            "max_tokens": 1000,
            "temperature": 0.3,
            "timeout": 30
        }
    }
    
    # Chemins Mac
    paths = {
        "home": Path.home(),
        "documents": Path.home() / "Documents",
        "desktop": Path.home() / "Desktop",
        "downloads": Path.home() / "Downloads",
        "app_support": Path.home() / "Library" / "Application Support" / "OCR Greek Mac",
        "cache": Path.home() / "Library" / "Caches" / "OCR Greek Mac",
        "logs": Path.home() / "Library" / "Logs" / "OCR Greek Mac"
    }
    
    def __post_init__(self):
        """Initialisation post-création"""
        if self.is_macos:
            self._detect_mac_features()
            self._create_directories()
    
    def _detect_mac_features(self):
        """Détecte les fonctionnalités Mac"""
        # Détection Retina Display
        try:
            import tkinter as tk
            root = tk.Tk()
            self.is_retina = root.tk.call('tk', 'scaling') > 1.0
            root.destroy()
        except:
            self.is_retina = False
        
        # Détection Apple Silicon
        try:
            import subprocess
            result = subprocess.run(['uname', '-m'], capture_output=True, text=True)
            self.is_apple_silicon = result.stdout.strip() == 'arm64'
        except:
            self.is_apple_silicon = False
    
    def _create_directories(self):
        """Crée les répertoires nécessaires"""
        for path in self.paths.values():
            if isinstance(path, Path):
                path.mkdir(parents=True, exist_ok=True)
    
    def get_optimized_dpi(self) -> int:
        """Retourne le DPI optimisé pour Mac"""
        if self.is_retina:
            return 300
        return 200
    
    def get_optimized_image_size(self) -> int:
        """Retourne la taille d'image optimisée"""
        if self.is_retina:
            return 4096
        return 2048
    
    def get_optimized_pdf_dpi(self) -> int:
        """Retourne le DPI PDF optimisé"""
        if self.is_retina:
            return 300
        return 200
    
    def get_optimized_pdf_size(self) -> int:
        """Retourne la taille PDF optimisée"""
        if self.is_retina:
            return 2048
        return 1024
    
    def get_colors(self) -> Dict[str, str]:
        """Retourne les couleurs optimisées pour Mac"""
        if self.is_macos:
            return {
                "bg": "#ffffff",
                "fg": "#000000",
                "button_bg": "#f0f0f0",
                "button_fg": "#000000",
                "text_bg": "#fafafa",
                "text_fg": "#000000",
                "accent": "#007aff",
                "success": "#34c759",
                "warning": "#ff9500",
                "error": "#ff3b30",
                "border": "#e5e5e7",
                "hover": "#f2f2f7"
            }
        else:
            return {
                "bg": "#ffffff",
                "fg": "#1f1f1f",
                "button_bg": "#f3f2f1",
                "button_fg": "#1f1f1f",
                "text_bg": "#faf9f8",
                "text_fg": "#1f1f1f",
                "accent": "#0078d4",
                "success": "#107c10",
                "warning": "#ff8c00",
                "error": "#d13438",
                "border": "#e1dfdd",
                "hover": "#f3f2f1"
            }
    
    def get_font_config(self) -> Dict[str, Any]:
        """Retourne la configuration de police optimisée"""
        if self.is_macos:
            return {
                "family": "SF Pro Display",
                "size": 12,
                "title_size": 16,
                "subtitle_size": 14,
                "small_size": 10
            }
        else:
            return {
                "family": "Segoe UI",
                "size": 10,
                "title_size": 14,
                "subtitle_size": 12,
                "small_size": 9
            }
    
    def get_gesture_config(self) -> Dict[str, Any]:
        """Retourne la configuration des gestes"""
        if not self.is_macos:
            return {}
        
        return {
            "pinch_zoom": True,
            "rotation_pages": True,
            "swipe_navigation": True,
            "custom_gestures": True,
            "sensitivity": 1.0,
            "smooth_scrolling": True
        }
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Retourne la configuration de performance"""
        return {
            "max_threads": 8 if self.is_apple_silicon else 4,
            "memory_limit": "2GB" if self.is_apple_silicon else "1GB",
            "cache_size": 100 if self.is_apple_silicon else 50,
            "batch_size": 10 if self.is_apple_silicon else 5,
            "use_metal": self.use_metal and self.is_macos,
            "optimize_memory": self.optimize_memory
        }


# Instance globale de configuration
mac_config = MacConfig() 