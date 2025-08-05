"""
Module d'analyse OCR pour OCR Grec v4.0
======================================
Ce module gère l'analyse et le traitement des résultats OCR.
"""

import logging
from typing import Dict, List, Optional, Tuple
import pytesseract
from PIL import Image
from config import Config

class OCRAnalyzer:
    """Classe pour l'analyse avancée des résultats OCR"""
    
    @staticmethod
    def analyze_ocr(ocr_data: dict) -> dict:
        """
        Analyse avancée des données OCR
        
        Args:
            ocr_data: Données brutes de Tesseract
            
        Returns:
            Dictionnaire avec les résultats analysés
        """
        try:
            words, confs, text = [], [], []
            
            # Vérification des clés attendues
            required_keys = ['text', 'conf', 'left', 'top', 'width', 'height']
            if not all(key in ocr_data for key in required_keys):
                logging.error("Données OCR incomplètes")
                return dict(text="", words=[], avg=0, stats={})
            
            # Traitement des mots
            for i, w in enumerate(ocr_data["text"]):
                if not w or not w.strip():
                    continue
                    
                try:
                    c = int(float(ocr_data["conf"][i]))
                except (ValueError, IndexError, TypeError):
                    continue
                    
                if c < 0:
                    continue
                
                # Catégorisation améliorée
                if c >= Config.THRESHOLDS["reliable"]:
                    cat = "reliable"
                elif c >= Config.THRESHOLDS["uncertain"]:
                    cat = "uncertain"
                else:
                    cat = "unreliable"
                
                # Informations de position
                bbox = (
                    ocr_data["left"][i],
                    ocr_data["top"][i],
                    ocr_data["width"][i],
                    ocr_data["height"][i]
                )
                
                words.append(dict(
                    text=w, conf=c, cat=cat, bbox=bbox,
                    length=len(w), has_greek=any(ord(c) > 127 for c in w)
                ))
                confs.append(c)
                text.append(w)
            
            # Calculs statistiques
            avg = sum(confs) / len(confs) if confs else 0
            
            # Statistiques détaillées
            stats = OCRAnalyzer._calculate_stats(words, confs)
            
            return dict(
                text=" ".join(text), 
                words=words, 
                avg=avg,
                stats=stats
            )
            
        except Exception as e:
            logging.error(f"Erreur analyze_ocr: {e}")
            return dict(text="", words=[], avg=0, stats={})
    
    @staticmethod
    def _calculate_stats(words: List[dict], confs: List[int]) -> dict:
        """
        Calcule des statistiques détaillées
        
        Args:
            words: Liste des mots analysés
            confs: Liste des confiances
            
        Returns:
            Dictionnaire avec les statistiques
        """
        if not words:
            return {}
        
        # Statistiques par catégorie
        cats = {}
        for w in words:
            cat = w["cat"]
            if cat not in cats:
                cats[cat] = {"count": 0, "avg_conf": 0, "words": []}
            cats[cat]["count"] += 1
            cats[cat]["avg_conf"] += w["conf"]
            cats[cat]["words"].append(w["text"])
        
        # Moyennes par catégorie
        for cat in cats:
            cats[cat]["avg_conf"] /= cats[cat]["count"]
        
        # Statistiques générales
        greek_words = sum(1 for w in words if w["has_greek"])
        long_words = sum(1 for w in words if w["length"] > 8)
        
        return {
            "total_words": len(words),
            "categories": cats,
            "greek_words": greek_words,
            "long_words": long_words,
            "avg_confidence": sum(confs) / len(confs) if confs else 0,
            "min_confidence": min(confs) if confs else 0,
            "max_confidence": max(confs) if confs else 0
        }
    
    @staticmethod
    def get_doubtful_words(ocr_results: List[dict]) -> List[dict]:
        """
        Récupère les mots douteux des résultats OCR
        
        Args:
            ocr_results: Liste des résultats OCR
            
        Returns:
            Liste des mots douteux
        """
        doubtful_words = []
        
        for result in ocr_results:
            if isinstance(result, dict) and 'words' in result:
                for word in result['words']:
                    if word['cat'] in ['uncertain', 'unreliable']:
                        doubtful_words.append(word)
        
        return doubtful_words
    
    @staticmethod
    def get_word_context(ocr_results: List[dict], word_info: dict) -> str:
        """
        Obtient le contexte autour d'un mot
        
        Args:
            ocr_results: Résultats OCR
            word_info: Informations du mot
            
        Returns:
            Contexte autour du mot
        """
        try:
            # Chercher le mot dans le texte OCR
            for result in ocr_results:
                if isinstance(result, dict) and 'text' in result:
                    text = result['text']
                    word = word_info['text']
                    
                    # Trouver la position du mot
                    pos = text.find(word)
                    if pos != -1:
                        # Extraire le contexte (50 caractères avant et après)
                        start = max(0, pos - 50)
                        end = min(len(text), pos + len(word) + 50)
                        context = text[start:end]
                        return context
            
            return word_info['text']  # Fallback
        except Exception as e:
            logging.error(f"Erreur contexte: {e}")
            return word_info['text']
    
    @staticmethod
    def apply_corrections(ocr_results: List[dict], corrected_words: List[dict]) -> None:
        """
        Applique les corrections aux résultats OCR
        
        Args:
            ocr_results: Résultats OCR à modifier
            corrected_words: Liste des corrections à appliquer
        """
        try:
            # Mettre à jour les résultats OCR
            for result in ocr_results:
                if isinstance(result, dict) and 'words' in result:
                    for word in result['words']:
                        for correction in corrected_words:
                            if (word['text'] == correction['original']['text'] and 
                                word['conf'] == correction['original']['conf']):
                                word['text'] = correction['correction']
                                word['conf'] = 100  # Marquer comme corrigé
                                break
        except Exception as e:
            logging.error(f"Erreur application corrections: {e}")
    
    @staticmethod
    def validate_ocr_data(ocr_data: dict) -> bool:
        """
        Valide les données OCR
        
        Args:
            ocr_data: Données OCR à valider
            
        Returns:
            True si les données sont valides
        """
        try:
            required_keys = ['text', 'conf', 'left', 'top', 'width', 'height']
            
            # Vérifier la présence des clés
            if not all(key in ocr_data for key in required_keys):
                return False
            
            # Vérifier que toutes les listes ont la même longueur
            lengths = [len(ocr_data[key]) for key in required_keys]
            if len(set(lengths)) != 1:
                return False
            
            # Vérifier qu'il y a au moins un élément
            if lengths[0] == 0:
                return False
            
            return True
            
        except Exception as e:
            logging.error(f"Erreur validation OCR: {e}")
            return False 