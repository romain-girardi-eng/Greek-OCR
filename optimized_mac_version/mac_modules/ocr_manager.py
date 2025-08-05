#!/usr/bin/env python3
"""
Module OCR optimisé pour macOS
"""

import os
import sys
import logging
import threading
import time
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass

import pytesseract
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

# Import de la configuration Mac
from mac_config import mac_config


@dataclass
class OCRResult:
    """Résultat d'une analyse OCR"""
    text: str
    confidence: float
    language: str
    processing_time: float
    image_path: str
    preprocessed: bool = False
    enhanced: bool = False


class MacOptimizedOCRManager:
    """Gestionnaire OCR optimisé pour macOS"""
    
    def __init__(self, app: 'MacOptimizedOCRApp') -> None:
        self.app = app
        self.is_processing = False
        self.current_task_id = None
        self.setup_tesseract()
    
    def setup_tesseract(self) -> None:
        """Configure Tesseract pour macOS"""
        try:
            # Vérifier que Tesseract est installé
            version = pytesseract.get_tesseract_version()
            logging.info(f"Tesseract version: {version}")
            
            # Configuration optimisée pour Mac
            if mac_config.is_apple_silicon:
                # Optimisations pour Apple Silicon
                os.environ['OMP_THREAD_LIMIT'] = '8'
                os.environ['OMP_NUM_THREADS'] = '8'
            else:
                # Optimisations pour Intel
                os.environ['OMP_THREAD_LIMIT'] = '4'
                os.environ['OMP_NUM_THREADS'] = '4'
            
            # Vérifier les langues disponibles
            languages = pytesseract.get_languages()
            logging.info(f"Langues disponibles: {languages}")
            
            # Vérifier que le grec ancien est disponible
            if 'grc' not in languages:
                logging.warning("Grec ancien (grc) non disponible dans Tesseract")
            
        except Exception as e:
            logging.error(f"Erreur configuration Tesseract: {e}")
            raise
    
    def perform_ocr(self) -> None:
        """Lance l'OCR sur l'image courante"""
        if not self.app.state.current_images:
            self.app.show_error("Aucune image chargée")
            return
        
        if self.is_processing:
            self.app.show_error("OCR déjà en cours")
            return
        
        # Lancer l'OCR dans un thread séparé
        self.is_processing = True
        self.current_task_id = f"ocr_{int(time.time())}"
        
        thread = threading.Thread(target=self._perform_ocr_thread, daemon=True)
        thread.start()
    
    def _perform_ocr_thread(self) -> None:
        """Thread d'exécution de l'OCR"""
        try:
            self.app.set_status("🔍 OCR en cours...")
            
            # Récupérer l'image courante
            current_image = self.app.state.current_images[self.app.state.current_page]
            
            # Préprocesser l'image
            preprocessed_image = self._preprocess_image(current_image)
            
            # Effectuer l'OCR
            results = self._extract_text(preprocessed_image)
            
            # Mettre à jour l'état de l'application
            self.app.state.ocr_results = results
            
            # Afficher les résultats
            self._display_ocr_results(results)
            
            self.app.set_status("✅ OCR terminé avec succès")
            
        except Exception as e:
            logging.error(f"Erreur OCR: {e}")
            self.app.show_error(f"Erreur lors de l'OCR: {e}")
        
        finally:
            self.is_processing = False
            self.current_task_id = None
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """Préprocesse l'image pour améliorer l'OCR"""
        try:
            # Convertir en RGB si nécessaire
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convertir en numpy array pour OpenCV
            img_array = np.array(image)
            
            # Conversion BGR pour OpenCV
            img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            # Amélioration du contraste
            lab = cv2.cvtColor(img_cv, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            cl = clahe.apply(l)
            enhanced = cv2.merge((cl,a,b))
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
            
            # Réduction du bruit
            denoised = cv2.fastNlMeansDenoisingColored(enhanced, None, 10, 10, 7, 21)
            
            # Amélioration de la netteté
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            sharpened = cv2.filter2D(denoised, -1, kernel)
            
            # Conversion retour en PIL
            enhanced_pil = Image.fromarray(cv2.cvtColor(sharpened, cv2.COLOR_BGR2RGB))
            
            return enhanced_pil
            
        except Exception as e:
            logging.warning(f"Erreur préprocessing: {e}, utilisation de l'image originale")
            return image
    
    def _extract_text(self, image: Image.Image) -> List[OCRResult]:
        """Extrait le texte de l'image avec différentes configurations"""
        results = []
        
        # Configurations OCR à tester
        configs = [
            {
                "name": "Grec ancien",
                "lang": "grc",
                "config": mac_config.tesseract_config["default"]
            },
            {
                "name": "Grec ancien + Anglais",
                "lang": "grc+eng",
                "config": mac_config.tesseract_config["default"]
            },
            {
                "name": "Grec ancien + Français",
                "lang": "grc+fra",
                "config": mac_config.tesseract_config["default"]
            },
            {
                "name": "Auto-détection",
                "lang": "grc+eng+fra",
                "config": mac_config.tesseract_config["default"]
            }
        ]
        
        for config in configs:
            try:
                start_time = time.time()
                
                # Extraction du texte
                text = pytesseract.image_to_string(
                    image,
                    lang=config["lang"],
                    config=config["config"]
                )
                
                # Calcul de la confiance
                data = pytesseract.image_to_data(
                    image,
                    lang=config["lang"],
                    config=config["config"],
                    output_type=pytesseract.Output.DICT
                )
                
                # Calculer la confiance moyenne
                confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                
                processing_time = time.time() - start_time
                
                # Créer le résultat
                result = OCRResult(
                    text=text.strip(),
                    confidence=avg_confidence,
                    language=config["lang"],
                    processing_time=processing_time,
                    image_path=self.app.state.current_file_path,
                    preprocessed=True,
                    enhanced=True
                )
                
                results.append(result)
                
                logging.info(f"OCR {config['name']}: {len(text)} caractères, confiance {avg_confidence:.1f}%")
                
            except Exception as e:
                logging.error(f"Erreur OCR {config['name']}: {e}")
                continue
        
        return results
    
    def _display_ocr_results(self, results: List[OCRResult]) -> None:
        """Affiche les résultats OCR dans l'interface"""
        if not results:
            self.app.show_error("Aucun résultat OCR obtenu")
            return
        
        # Créer une fenêtre de résultats
        self._create_results_window(results)
    
    def _create_results_window(self, results: List[OCRResult]) -> None:
        """Crée une fenêtre pour afficher les résultats OCR"""
        import tkinter as tk
        from tkinter import ttk, scrolledtext
        
        # Créer la fenêtre de résultats
        results_window = tk.Toplevel(self.app)
        results_window.title("🔍 Résultats OCR")
        results_window.geometry("1000x700")
        results_window.configure(bg=self.app.ui_manager.colors["bg"])
        
        # Titre
        title_label = tk.Label(results_window, 
                              text="🔍 Résultats de l'OCR", 
                              font=("SF Pro Display", 16, "bold"),
                              bg=self.app.ui_manager.colors["bg"],
                              fg=self.app.ui_manager.colors["accent"])
        title_label.pack(pady=10)
        
        # Notebook pour les différents résultats
        notebook = ttk.Notebook(results_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Créer un onglet pour chaque configuration
        for i, result in enumerate(results):
            # Frame pour l'onglet
            tab_frame = tk.Frame(notebook, bg=self.app.ui_manager.colors["bg"])
            notebook.add(tab_frame, text=f"{result.language} ({result.confidence:.1f}%)")
            
            # Informations sur le résultat
            info_frame = tk.Frame(tab_frame, bg=self.app.ui_manager.colors["text_bg"])
            info_frame.pack(fill=tk.X, padx=5, pady=5)
            
            info_text = f"Langue: {result.language} | Confiance: {result.confidence:.1f}% | Temps: {result.processing_time:.2f}s | Caractères: {len(result.text)}"
            tk.Label(info_frame, text=info_text,
                    bg=self.app.ui_manager.colors["text_bg"],
                    fg=self.app.ui_manager.colors["text_fg"]).pack(pady=5)
            
            # Zone de texte pour le résultat
            text_frame = tk.Frame(tab_frame, bg=self.app.ui_manager.colors["bg"])
            text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Scrollbar et zone de texte
            text_widget = scrolledtext.ScrolledText(
                text_frame,
                wrap=tk.WORD,
                font=("SF Pro Display", 12),
                bg=self.app.ui_manager.colors["text_bg"],
                fg=self.app.ui_manager.colors["text_fg"],
                insertbackground=self.app.ui_manager.colors["text_fg"]
            )
            text_widget.pack(fill=tk.BOTH, expand=True)
            
            # Insérer le texte
            text_widget.insert(tk.END, result.text)
            
            # Boutons d'action
            button_frame = tk.Frame(tab_frame, bg=self.app.ui_manager.colors["bg"])
            button_frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Bouton copier
            copy_button = tk.Button(button_frame, text="📋 Copier",
                                  command=lambda t=result.text: self._copy_to_clipboard(t),
                                  bg=self.app.ui_manager.colors["button_bg"],
                                  fg=self.app.ui_manager.colors["button_fg"])
            copy_button.pack(side=tk.LEFT, padx=5)
            
            # Bouton sauvegarder
            save_button = tk.Button(button_frame, text="💾 Sauvegarder",
                                  command=lambda r=result: self._save_result(r),
                                  bg=self.app.ui_manager.colors["button_bg"],
                                  fg=self.app.ui_manager.colors["button_fg"])
            save_button.pack(side=tk.LEFT, padx=5)
            
            # Bouton recherche lemmatique
            if result.text.strip():
                lemmatique_button = tk.Button(button_frame, text="🔤 Recherche Lemmatique",
                                            command=lambda t=result.text: self._open_lemmatique_search(t),
                                            bg=self.app.ui_manager.colors["accent"],
                                            fg="white")
                lemmatique_button.pack(side=tk.LEFT, padx=5)
        
        # Bouton fermer
        close_button = tk.Button(results_window, text="Fermer",
                               command=results_window.destroy,
                               bg=self.app.ui_manager.colors["button_bg"],
                               fg=self.app.ui_manager.colors["button_fg"])
        close_button.pack(pady=10)
    
    def _copy_to_clipboard(self, text: str) -> None:
        """Copie le texte dans le presse-papiers"""
        try:
            self.app.clipboard_clear()
            self.app.clipboard_append(text)
            self.app.set_status("📋 Texte copié dans le presse-papiers")
        except Exception as e:
            logging.error(f"Erreur copie presse-papiers: {e}")
    
    def _save_result(self, result: OCRResult) -> None:
        """Sauvegarde le résultat OCR"""
        try:
            from tkinter import filedialog
            
            filename = filedialog.asksaveasfilename(
                title="Sauvegarder le résultat OCR",
                defaultextension=".txt",
                filetypes=[("Texte", "*.txt"), ("Tous les fichiers", "*.*")]
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"Résultat OCR - {result.language}\n")
                    f.write(f"Confiance: {result.confidence:.1f}%\n")
                    f.write(f"Temps de traitement: {result.processing_time:.2f}s\n")
                    f.write(f"Image: {result.image_path}\n")
                    f.write("-" * 50 + "\n")
                    f.write(result.text)
                
                self.app.set_status(f"💾 Résultat sauvegardé: {filename}")
                
        except Exception as e:
            logging.error(f"Erreur sauvegarde: {e}")
            self.app.show_error(f"Erreur lors de la sauvegarde: {e}")
    
    def _open_lemmatique_search(self, text: str) -> None:
        """Ouvre la recherche lemmatique avec le texte OCR"""
        try:
            if hasattr(self.app, 'lemmatique_ui') and self.app.lemmatique_ui:
                self.app.lemmatique_ui.show_search_dialog(text)
                self.app.set_status("🔤 Recherche lemmatique ouverte")
            else:
                self.app.show_error("Module de recherche lemmatique non disponible")
        except Exception as e:
            logging.error(f"Erreur ouverture recherche lemmatique: {e}")
    
    def get_ocr_status(self) -> Dict[str, Any]:
        """Retourne le statut de l'OCR"""
        return {
            "is_processing": self.is_processing,
            "current_task_id": self.current_task_id,
            "tesseract_version": pytesseract.get_tesseract_version(),
            "available_languages": pytesseract.get_languages(),
            "mac_optimizations": {
                "apple_silicon": mac_config.is_apple_silicon,
                "retina_display": mac_config.is_retina,
                "thread_limit": os.environ.get('OMP_THREAD_LIMIT', '4')
            }
        } 