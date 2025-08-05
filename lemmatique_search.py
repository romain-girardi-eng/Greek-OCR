#!/usr/bin/env python3
"""
OUTIL DE RECHERCHE LEMMATIQUE RÉVOLUTIONNAIRE - GREC ANCIEN
==========================================================
Recherche toutes les formes d'un lemme grec dans le texte OCR et base de données classiques.
"""

import re
import json
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
import requests
from collections import defaultdict

# Imports Tkinter
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class LemmaForm:
    """Forme d'un lemme grec"""
    form: str
    lemma: str
    pos: str  # Part of speech
    case: Optional[str] = None
    number: Optional[str] = None
    gender: Optional[str] = None
    person: Optional[str] = None
    tense: Optional[str] = None
    voice: Optional[str] = None
    mood: Optional[str] = None
    frequency: int = 1


@dataclass
class LemmaSearchResult:
    """Résultat de recherche lemmatique"""
    lemma: str
    forms_found: List[LemmaForm]
    total_occurrences: int
    contexts: List[str]
    authors: List[str]
    works: List[str]
    periods: List[str]
    semantic_domains: List[str]


class LemmatiqueSearchEngine:
    """Moteur de recherche lemmatique pour grec ancien"""
    
    def __init__(self):
        self.lemma_database = self._load_lemma_database()
        self.classical_texts = self._load_classical_texts()
        self.search_cache = {}
        
    def _load_lemma_database(self) -> Dict[str, List[LemmaForm]]:
        """Charge la base de données de lemmes grecs"""
        # Base de données de lemmes grecs classiques
        lemma_data = {
            "λόγος": [
                LemmaForm("λόγος", "λόγος", "noun", "nominative", "singular", "masculine"),
                LemmaForm("λόγου", "λόγος", "noun", "genitive", "singular", "masculine"),
                LemmaForm("λόγῳ", "λόγος", "noun", "dative", "singular", "masculine"),
                LemmaForm("λόγον", "λόγος", "noun", "accusative", "singular", "masculine"),
                LemmaForm("λόγε", "λόγος", "noun", "vocative", "singular", "masculine"),
                LemmaForm("λόγοι", "λόγος", "noun", "nominative", "plural", "masculine"),
                LemmaForm("λόγων", "λόγος", "noun", "genitive", "plural", "masculine"),
                LemmaForm("λόγοις", "λόγος", "noun", "dative", "plural", "masculine"),
                LemmaForm("λόγους", "λόγος", "noun", "accusative", "plural", "masculine"),
            ],
            "θεός": [
                LemmaForm("θεός", "θεός", "noun", "nominative", "singular", "masculine"),
                LemmaForm("θεοῦ", "θεός", "noun", "genitive", "singular", "masculine"),
                LemmaForm("θεῷ", "θεός", "noun", "dative", "singular", "masculine"),
                LemmaForm("θεόν", "θεός", "noun", "accusative", "singular", "masculine"),
                LemmaForm("θεέ", "θεός", "noun", "vocative", "singular", "masculine"),
                LemmaForm("θεοί", "θεός", "noun", "nominative", "plural", "masculine"),
                LemmaForm("θεῶν", "θεός", "noun", "genitive", "plural", "masculine"),
                LemmaForm("θεοῖς", "θεός", "noun", "dative", "plural", "masculine"),
                LemmaForm("θεούς", "θεός", "noun", "accusative", "plural", "masculine"),
            ],
            "εἰμί": [
                LemmaForm("εἰμί", "εἰμί", "verb", person="1st", number="singular", tense="present", voice="active", mood="indicative"),
                LemmaForm("εἶ", "εἰμί", "verb", person="2nd", number="singular", tense="present", voice="active", mood="indicative"),
                LemmaForm("ἐστί", "εἰμί", "verb", person="3rd", number="singular", tense="present", voice="active", mood="indicative"),
                LemmaForm("ἐσμέν", "εἰμί", "verb", person="1st", number="plural", tense="present", voice="active", mood="indicative"),
                LemmaForm("ἐστέ", "εἰμί", "verb", person="2nd", number="plural", tense="present", voice="active", mood="indicative"),
                LemmaForm("εἰσί", "εἰμί", "verb", person="3rd", number="plural", tense="present", voice="active", mood="indicative"),
                LemmaForm("ἦν", "εἰμί", "verb", person="3rd", number="singular", tense="imperfect", voice="active", mood="indicative"),
                LemmaForm("ἦσαν", "εἰμί", "verb", person="3rd", number="plural", tense="imperfect", voice="active", mood="indicative"),
            ],
            "γίγνομαι": [
                LemmaForm("γίγνομαι", "γίγνομαι", "verb", person="1st", number="singular", tense="present", voice="middle", mood="indicative"),
                LemmaForm("γίγνῃ", "γίγνομαι", "verb", person="2nd", number="singular", tense="present", voice="middle", mood="indicative"),
                LemmaForm("γίγνεται", "γίγνομαι", "verb", person="3rd", number="singular", tense="present", voice="middle", mood="indicative"),
                LemmaForm("γίγνεσθαι", "γίγνομαι", "verb", tense="present", voice="middle", mood="infinitive"),
                LemmaForm("ἐγένετο", "γίγνομαι", "verb", person="3rd", number="singular", tense="aorist", voice="middle", mood="indicative"),
            ],
            "ἀρχή": [
                LemmaForm("ἀρχή", "ἀρχή", "noun", "nominative", "singular", "feminine"),
                LemmaForm("ἀρχῆς", "ἀρχή", "noun", "genitive", "singular", "feminine"),
                LemmaForm("ἀρχῇ", "ἀρχή", "noun", "dative", "singular", "feminine"),
                LemmaForm("ἀρχήν", "ἀρχή", "noun", "accusative", "singular", "feminine"),
                LemmaForm("ἀρχαί", "ἀρχή", "noun", "nominative", "plural", "feminine"),
                LemmaForm("ἀρχῶν", "ἀρχή", "noun", "genitive", "plural", "feminine"),
                LemmaForm("ἀρχαῖς", "ἀρχή", "noun", "dative", "plural", "feminine"),
                LemmaForm("ἀρχάς", "ἀρχή", "noun", "accusative", "plural", "feminine"),
            ],
            "ζωή": [
                LemmaForm("ζωή", "ζωή", "noun", "nominative", "singular", "feminine"),
                LemmaForm("ζωῆς", "ζωή", "noun", "genitive", "singular", "feminine"),
                LemmaForm("ζωῇ", "ζωή", "noun", "dative", "singular", "feminine"),
                LemmaForm("ζωήν", "ζωή", "noun", "accusative", "singular", "feminine"),
                LemmaForm("ζωαί", "ζωή", "noun", "nominative", "plural", "feminine"),
                LemmaForm("ζωῶν", "ζωή", "noun", "genitive", "plural", "feminine"),
                LemmaForm("ζωαῖς", "ζωή", "noun", "dative", "plural", "feminine"),
                LemmaForm("ζωάς", "ζωή", "noun", "accusative", "plural", "feminine"),
            ],
            "φῶς": [
                LemmaForm("φῶς", "φῶς", "noun", "nominative", "singular", "neuter"),
                LemmaForm("φωτός", "φῶς", "noun", "genitive", "singular", "neuter"),
                LemmaForm("φωτί", "φῶς", "noun", "dative", "singular", "neuter"),
                LemmaForm("φῶς", "φῶς", "noun", "accusative", "singular", "neuter"),
                LemmaForm("φῶτα", "φῶς", "noun", "nominative", "plural", "neuter"),
                LemmaForm("φώτων", "φῶς", "noun", "genitive", "plural", "neuter"),
                LemmaForm("φωσί", "φῶς", "noun", "dative", "plural", "neuter"),
                LemmaForm("φῶτα", "φῶς", "noun", "accusative", "plural", "neuter"),
            ],
            "κόσμος": [
                LemmaForm("κόσμος", "κόσμος", "noun", "nominative", "singular", "masculine"),
                LemmaForm("κόσμου", "κόσμος", "noun", "genitive", "singular", "masculine"),
                LemmaForm("κόσμῳ", "κόσμος", "noun", "dative", "singular", "masculine"),
                LemmaForm("κόσμον", "κόσμος", "noun", "accusative", "singular", "masculine"),
                LemmaForm("κόσμε", "κόσμος", "noun", "vocative", "singular", "masculine"),
                LemmaForm("κόσμοι", "κόσμος", "noun", "nominative", "plural", "masculine"),
                LemmaForm("κόσμων", "κόσμος", "noun", "genitive", "plural", "masculine"),
                LemmaForm("κόσμοις", "κόσμος", "noun", "dative", "plural", "masculine"),
                LemmaForm("κόσμους", "κόσμος", "noun", "accusative", "plural", "masculine"),
            ],
            "ἀλήθεια": [
                LemmaForm("ἀλήθεια", "ἀλήθεια", "noun", "nominative", "singular", "feminine"),
                LemmaForm("ἀληθείας", "ἀλήθεια", "noun", "genitive", "singular", "feminine"),
                LemmaForm("ἀληθείᾳ", "ἀλήθεια", "noun", "dative", "singular", "feminine"),
                LemmaForm("ἀλήθειαν", "ἀλήθεια", "noun", "accusative", "singular", "feminine"),
                LemmaForm("ἀλήθειαι", "ἀλήθεια", "noun", "nominative", "plural", "feminine"),
                LemmaForm("ἀληθειῶν", "ἀλήθεια", "noun", "genitive", "plural", "feminine"),
                LemmaForm("ἀληθείαις", "ἀλήθεια", "noun", "dative", "plural", "feminine"),
                LemmaForm("ἀληθείας", "ἀλήθεια", "noun", "accusative", "plural", "feminine"),
            ],
            "χάρις": [
                LemmaForm("χάρις", "χάρις", "noun", "nominative", "singular", "feminine"),
                LemmaForm("χάριτος", "χάρις", "noun", "genitive", "singular", "feminine"),
                LemmaForm("χάριτι", "χάρις", "noun", "dative", "singular", "feminine"),
                LemmaForm("χάριν", "χάρις", "noun", "accusative", "singular", "feminine"),
                LemmaForm("χάριτες", "χάρις", "noun", "nominative", "plural", "feminine"),
                LemmaForm("χαρίτων", "χάρις", "noun", "genitive", "plural", "feminine"),
                LemmaForm("χάρισιν", "χάρις", "noun", "dative", "plural", "feminine"),
                LemmaForm("χάριτας", "χάρις", "noun", "accusative", "plural", "feminine"),
            ]
        }
        
        # Créer un index inversé pour la recherche rapide
        lemma_index = defaultdict(list)
        for lemma, forms in lemma_data.items():
            for form in forms:
                lemma_index[form.form.lower()].append(form)
                lemma_index[lemma].append(form)  # Ajouter aussi le lemme lui-même
        
        return dict(lemma_index)
    
    def _load_classical_texts(self) -> Dict[str, Dict[str, Any]]:
        """Charge la base de données de textes classiques"""
        return {
            "homer_iliad": {
                "author": "Homère",
                "work": "Iliade",
                "period": "VIIIe siècle av. J.-C.",
                "text": "Μῆνιν ἄειδε, θεά, Πηληϊάδεω Ἀχιλῆος οὐλομένην, ἣ μυρί᾽ Ἀχαιοῖς ἄλγε᾽ ἔθηκε, πολλὰς δ᾽ ἰφθίμους ψυχὰς Ἄϊδι προΐαψεν ἡρώων, αὐτοὺς δὲ ἑλώρια τεῦχε κύνεσσιν οἰωνοῖσί τε πᾶσι· Διὸς δ᾽ ἐτελείετο βουλή· ἐξ οὗ δὴ τὰ πρῶτα διαστήτην ἐρίσαντε Ἀτρεΐδης τε ἄναξ ἀνδρῶν καὶ δῖος Ἀχιλλεύς.",
                "lemmata": ["μῆνις", "θεός", "Ἀχιλλεύς", "Ἀχαιοί", "Ἄϊδης", "ἥρως", "Διός", "Ἀτρεΐδης"]
            },
            "homer_odyssey": {
                "author": "Homère",
                "work": "Odyssée",
                "period": "VIIIe siècle av. J.-C.",
                "text": "Ἄνδρα μοι ἔννεπε, Μοῦσα, πολύτροπον, ὃς μάλα πολλὰ πλάγχθη, ἐπεὶ Τροίης ἱερὸν πτολίεθρον ἔπερσε· πολλῶν δ᾽ ἀνθρώπων ἴδεν ἄστεα καὶ νόον ἔγνω, πολλὰ δ᾽ ὅ γ᾽ ἐν πόντῳ πάθεν ἄλγεα ὃν κατὰ θυμόν, ἀρνύμενος ἥν τε ψυχὴν καὶ νόστον ἑταίρων.",
                "lemmata": ["ἀνήρ", "Μοῦσα", "πολύτροπος", "Τροία", "ἄνθρωπος", "πόλις", "νόος", "πόντος", "ψυχή"]
            },
            "plato_republic": {
                "author": "Platon",
                "work": "République",
                "period": "Ve siècle av. J.-C.",
                "text": "Κατέβην χθὲς εἰς Πειραιᾶ μετὰ Γλαύκωνος τοῦ Ἀρίστωνος προσευξόμενός τε τῇ θεῷ καὶ ἅμα τὴν ἑορτὴν βουλόμενος θεάσασθαι τίνα τρόπον ποιήσουσιν ἅτε νῦν πρῶτον ἄγοντες.",
                "lemmata": ["καταβαίνω", "θεός", "ἑορτή", "θεάομαι", "τρόπος", "ἄγω"]
            },
            "john_gospel": {
                "author": "Jean",
                "work": "Évangile selon Jean",
                "period": "Ier siècle ap. J.-C.",
                "text": "Ἐν ἀρχῇ ἦν ὁ λόγος, καὶ ὁ λόγος ἦν πρὸς τὸν θεόν, καὶ θεὸς ἦν ὁ λόγος. Οὗτος ἦν ἐν ἀρχῇ πρὸς τὸν θεόν. Πάντα δι᾽ αὐτοῦ ἐγένετο, καὶ χωρὶς αὐτοῦ ἐγένετο οὐδὲ ἓν ὃ γέγονεν.",
                "lemmata": ["ἀρχή", "εἰμί", "λόγος", "θεός", "γίγνομαι"]
            }
        }
    
    def search_lemma(self, lemma: str, ocr_text: str = "", include_classical: bool = True) -> LemmaSearchResult:
        """
        Recherche toutes les formes d'un lemme
        
        Args:
            lemma: Lemme à rechercher
            ocr_text: Texte OCR à analyser
            include_classical: Inclure la recherche dans les textes classiques
            
        Returns:
            LemmaSearchResult: Résultat de la recherche
        """
        lemma = lemma.lower().strip()
        
        # Vérifier le cache
        cache_key = f"{lemma}_{hash(ocr_text)}_{include_classical}"
        if cache_key in self.search_cache:
            return self.search_cache[cache_key]
        
        # Récupérer toutes les formes du lemme
        all_forms = self.lemma_database.get(lemma, [])
        
        # Rechercher dans le texte OCR
        ocr_occurrences = []
        ocr_contexts = []
        
        if ocr_text:
            ocr_occurrences, ocr_contexts = self._search_in_text(ocr_text, all_forms)
        
        # Rechercher dans les textes classiques
        classical_occurrences = []
        classical_contexts = []
        authors = []
        works = []
        periods = []
        
        if include_classical:
            classical_occurrences, classical_contexts, authors, works, periods = self._search_in_classical_texts(all_forms)
        
        # Combiner les résultats
        all_occurrences = ocr_occurrences + classical_occurrences
        all_contexts = ocr_contexts + classical_contexts
        
        # Analyser les domaines sémantiques
        semantic_domains = self._analyze_semantic_domains(lemma, all_occurrences)
        
        # Créer le résultat
        result = LemmaSearchResult(
            lemma=lemma,
            forms_found=all_occurrences,
            total_occurrences=len(all_occurrences),
            contexts=all_contexts,
            authors=list(set(authors)),
            works=list(set(works)),
            periods=list(set(periods)),
            semantic_domains=semantic_domains
        )
        
        # Mettre en cache
        self.search_cache[cache_key] = result
        
        return result
    
    def _search_in_text(self, text: str, forms: List[LemmaForm]) -> Tuple[List[LemmaForm], List[str]]:
        """Recherche les formes dans un texte"""
        occurrences = []
        contexts = []
        
        text_lower = text.lower()
        
        for form in forms:
            # Recherche simple
            if form.form in text_lower:
                occurrences.append(form)
                
                # Extraire le contexte
                start = text_lower.find(form.form)
                if start != -1:
                    context_start = max(0, start - 50)
                    context_end = min(len(text), start + len(form.form) + 50)
                    context = text[context_start:context_end]
                    contexts.append(f"...{context}...")
        
        return occurrences, contexts
    
    def _search_in_classical_texts(self, forms: List[LemmaForm]) -> Tuple[List[LemmaForm], List[str], List[str], List[str], List[str]]:
        """Recherche dans les textes classiques"""
        occurrences = []
        contexts = []
        authors = []
        works = []
        periods = []
        
        for text_id, text_data in self.classical_texts.items():
            text_lower = text_data["text"].lower()
            
            for form in forms:
                if form.form in text_lower:
                    # Créer une copie avec le contexte
                    form_with_context = LemmaForm(
                        form=form.form,
                        lemma=form.lemma,
                        pos=form.pos,
                        case=form.case,
                        number=form.number,
                        gender=form.gender,
                        person=form.person,
                        tense=form.tense,
                        voice=form.voice,
                        mood=form.mood,
                        frequency=form.frequency
                    )
                    occurrences.append(form_with_context)
                    
                    # Extraire le contexte
                    start = text_lower.find(form.form)
                    if start != -1:
                        context_start = max(0, start - 50)
                        context_end = min(len(text_data["text"]), start + len(form.form) + 50)
                        context = text_data["text"][context_start:context_end]
                        contexts.append(f"[{text_data['author']} - {text_data['work']}] ...{context}...")
                        
                        authors.append(text_data["author"])
                        works.append(text_data["work"])
                        periods.append(text_data["period"])
        
        return occurrences, contexts, authors, works, periods
    
    def _analyze_semantic_domains(self, lemma: str, occurrences: List[LemmaForm]) -> List[str]:
        """Analyse les domaines sémantiques d'un lemme"""
        domains = []
        
        # Analyse basée sur le lemme et les occurrences
        if lemma in ["θεός", "θεός"]:
            domains.extend(["religion", "theology", "divine"])
        elif lemma in ["λόγος"]:
            domains.extend(["philosophy", "speech", "reason", "word"])
        elif lemma in ["εἰμί", "γίγνομαι"]:
            domains.extend(["existence", "being", "ontology"])
        elif lemma in ["ἀρχή"]:
            domains.extend(["beginning", "principle", "authority", "rule"])
        elif lemma in ["ζωή"]:
            domains.extend(["life", "existence", "vitality"])
        elif lemma in ["φῶς"]:
            domains.extend(["light", "illumination", "knowledge"])
        elif lemma in ["κόσμος"]:
            domains.extend(["world", "universe", "order", "beauty"])
        elif lemma in ["ἀλήθεια"]:
            domains.extend(["truth", "reality", "veracity"])
        elif lemma in ["χάρις"]:
            domains.extend(["grace", "favor", "beauty", "gratitude"])
        
        return list(set(domains))
    
    def get_lemma_statistics(self, lemma: str) -> Dict[str, Any]:
        """Obtient les statistiques d'un lemme"""
        forms = self.lemma_database.get(lemma, [])
        
        stats = {
            "lemma": lemma,
            "total_forms": len(forms),
            "by_case": defaultdict(int),
            "by_number": defaultdict(int),
            "by_gender": defaultdict(int),
            "by_person": defaultdict(int),
            "by_tense": defaultdict(int),
            "by_voice": defaultdict(int),
            "by_mood": defaultdict(int),
            "forms_list": [form.form for form in forms]
        }
        
        for form in forms:
            if form.case:
                stats["by_case"][form.case] += 1
            if form.number:
                stats["by_number"][form.number] += 1
            if form.gender:
                stats["by_gender"][form.gender] += 1
            if form.person:
                stats["by_person"][form.person] += 1
            if form.tense:
                stats["by_tense"][form.tense] += 1
            if form.voice:
                stats["by_voice"][form.voice] += 1
            if form.mood:
                stats["by_mood"][form.mood] += 1
        
        return stats
    
    def suggest_lemmata(self, word: str) -> List[str]:
        """Suggère des lemmes basés sur un mot"""
        suggestions = []
        word_lower = word.lower()
        
        # Recherche exacte
        if word_lower in self.lemma_database:
            suggestions.append(word_lower)
        
        # Recherche par similarité
        for lemma in self.lemma_database.keys():
            if lemma.startswith(word_lower) or word_lower.startswith(lemma):
                if lemma not in suggestions:
                    suggestions.append(lemma)
        
        # Recherche par formes
        for form, forms_list in self.lemma_database.items():
            for form_obj in forms_list:
                if form_obj.form.startswith(word_lower) or word_lower.startswith(form_obj.form):
                    if form_obj.lemma not in suggestions:
                        suggestions.append(form_obj.lemma)
        
        return suggestions[:10]  # Limiter à 10 suggestions


class LemmatiqueSearchUI:
    """Interface utilisateur pour la recherche lemmatique"""
    
    def __init__(self, parent, search_engine: LemmatiqueSearchEngine):
        self.parent = parent
        self.search_engine = search_engine
        
    def show_search_dialog(self, ocr_text: str = ""):
        """Affiche la fenêtre de recherche lemmatique"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("🔍 Recherche Lemmatique - Grec Ancien")
        dialog.geometry("1000x700")
        dialog.configure(bg="#f0f8ff")
        
        # Titre
        title_label = tk.Label(dialog, text="🔍 Recherche Lemmatique Révolutionnaire", 
                              font=("Segoe UI", 16, "bold"), bg="#f0f8ff", fg="#0078d4")
        title_label.pack(pady=10)
        
        # Frame de recherche
        search_frame = tk.Frame(dialog, bg="#f0f8ff")
        search_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Zone de saisie
        tk.Label(search_frame, text="Lemme à rechercher:", font=("Segoe UI", 12, "bold"), 
                bg="#f0f8ff").pack(anchor="w")
        
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var, font=("Segoe UI", 14), width=40)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        search_entry.focus()
        
        # Bouton de recherche
        search_button = tk.Button(search_frame, text="🔍 Rechercher", 
                                 command=lambda: self._perform_search(dialog, search_var.get(), ocr_text),
                                 bg="#0078d4", fg="white", font=("Segoe UI", 12, "bold"))
        search_button.pack(side=tk.RIGHT)
        
        # Raccourci Entrée
        search_entry.bind('<Return>', lambda e: self._perform_search(dialog, search_var.get(), ocr_text))
        
        # Zone de résultats
        self.results_frame = tk.Frame(dialog, bg="#f0f8ff")
        self.results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Message initial
        initial_label = tk.Label(self.results_frame, 
                               text="Entrez un lemme grec pour commencer la recherche...\n\nExemples: λόγος, θεός, εἰμί, ἀρχή",
                               font=("Segoe UI", 12), bg="#f0f8ff", fg="#666666")
        initial_label.pack(expand=True)
    
    def _perform_search(self, dialog, lemma: str, ocr_text: str):
        """Effectue la recherche"""
        if not lemma.strip():
            return
        
        # Effacer les résultats précédents
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        # Afficher un indicateur de chargement
        loading_label = tk.Label(self.results_frame, text="🔍 Recherche en cours...", 
                               font=("Segoe UI", 12), bg="#f0f8ff")
        loading_label.pack(expand=True)
        dialog.update()
        
        try:
            # Effectuer la recherche
            result = self.search_engine.search_lemma(lemma, ocr_text, include_classical=True)
            
            # Afficher les résultats
            self._display_results(dialog, result)
            
        except Exception as e:
            error_label = tk.Label(self.results_frame, text=f"❌ Erreur: {e}", 
                                 font=("Segoe UI", 12), bg="#f0f8ff", fg="#d13438")
            error_label.pack(expand=True)
    
    def _display_results(self, dialog, result: LemmaSearchResult):
        """Affiche les résultats de recherche"""
        # Effacer le contenu précédent
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        # Créer un canvas avec scrollbar
        canvas = tk.Canvas(self.results_frame, bg="#f0f8ff")
        scrollbar = ttk.Scrollbar(self.results_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f0f8ff")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Titre des résultats
        title_label = tk.Label(scrollable_frame, 
                             text=f"🔍 Résultats pour le lemme: {result.lemma}", 
                             font=("Segoe UI", 14, "bold"), bg="#f0f8ff", fg="#0078d4")
        title_label.pack(pady=10)
        
        # Statistiques
        stats_frame = tk.LabelFrame(scrollable_frame, text="📊 Statistiques", 
                                  font=("Segoe UI", 12, "bold"), bg="#e8f4fd")
        stats_frame.pack(fill=tk.X, pady=10, padx=10)
        
        stats_text = f"📈 Total d'occurrences: {result.total_occurrences}\n"
        stats_text += f"📝 Formes trouvées: {len(result.forms_found)}\n"
        stats_text += f"📚 Auteurs: {', '.join(result.authors) if result.authors else 'Aucun'}\n"
        stats_text += f"📖 Œuvres: {', '.join(result.works) if result.works else 'Aucune'}\n"
        stats_text += f"📅 Périodes: {', '.join(result.periods) if result.periods else 'Aucune'}\n"
        stats_text += f"🎯 Domaines sémantiques: {', '.join(result.semantic_domains) if result.semantic_domains else 'Aucun'}"
        
        tk.Label(stats_frame, text=stats_text, font=("Segoe UI", 10), 
                bg="#e8f4fd", justify=tk.LEFT).pack(padx=10, pady=10)
        
        # Formes trouvées
        if result.forms_found:
            forms_frame = tk.LabelFrame(scrollable_frame, text="📝 Formes Trouvées", 
                                      font=("Segoe UI", 12, "bold"), bg="#fff8e1")
            forms_frame.pack(fill=tk.X, pady=10, padx=10)
            
            forms_text = scrolledtext.ScrolledText(forms_frame, height=6, wrap=tk.WORD, 
                                                 font=("Segoe UI", 10))
            forms_text.pack(fill=tk.X, padx=10, pady=10)
            
            for form in result.forms_found:
                form_info = f"• {form.form} ({form.pos}"
                if form.case:
                    form_info += f", {form.case}"
                if form.number:
                    form_info += f", {form.number}"
                if form.gender:
                    form_info += f", {form.gender}"
                if form.person:
                    form_info += f", {form.person}"
                if form.tense:
                    form_info += f", {form.tense}"
                form_info += ")\n"
                forms_text.insert(tk.END, form_info)
            
            forms_text.config(state=tk.DISABLED)
        
        # Contextes
        if result.contexts:
            contexts_frame = tk.LabelFrame(scrollable_frame, text="📖 Contextes", 
                                         font=("Segoe UI", 12, "bold"), bg="#f3f2f1")
            contexts_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)
            
            contexts_text = scrolledtext.ScrolledText(contexts_frame, height=8, wrap=tk.WORD, 
                                                    font=("Segoe UI", 10))
            contexts_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            for i, context in enumerate(result.contexts, 1):
                contexts_text.insert(tk.END, f"{i}. {context}\n\n")
            
            contexts_text.config(state=tk.DISABLED)
        
        # Configuration du scroll
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


# Test de l'outil
if __name__ == "__main__":
    import tkinter as tk
    from tkinter import ttk, scrolledtext
    
    # Créer l'application de test
    root = tk.Tk()
    root.title("Test Recherche Lemmatique")
    root.geometry("800x600")
    
    # Créer le moteur de recherche
    search_engine = LemmatiqueSearchEngine()
    
    # Créer l'interface
    ui = LemmatiqueSearchUI(root, search_engine)
    
    # Afficher la fenêtre de recherche
    ui.show_search_dialog("Ἐν ἀρχῇ ἦν ὁ λόγος, καὶ ὁ λόγος ἦν πρὸς τὸν θεόν, καὶ θεὸς ἦν ὁ λόγος.")
    
    root.mainloop() 