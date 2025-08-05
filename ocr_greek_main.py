#!/usr/bin/env python3
"""
OCR GREC ANCIEN - POINT D'ENTRÉE PRINCIPAL
==========================================
Lance la version optimisée pour Mac ou la version de base selon la plateforme.
"""

import sys
import os
import platform
from pathlib import Path

def main():
    """Fonction principale qui détermine quelle version lancer"""
    
    print("🔤 OCR Grec Ancien - Lancement...")
    print("=" * 50)
    
    # Détection de la plateforme
    is_macos = platform.system() == "Darwin"
    
    if is_macos:
        print("🍎 macOS détecté - Lancement de la version optimisée...")
        
        # Vérifier si la version optimisée existe
        optimized_path = Path("optimized_mac_version/ocr_greek_mac.py")
        
        if optimized_path.exists():
            print("✅ Version optimisée trouvée")
            
            # Importer et lancer la version optimisée
            try:
                sys.path.insert(0, "optimized_mac_version")
                from ocr_greek_mac import main as mac_main
                mac_main()
            except ImportError as e:
                print(f"❌ Erreur d'import: {e}")
                print("🔄 Lancement de la version de base...")
                launch_base_version()
        else:
            print("⚠️ Version optimisée non trouvée")
            print("🔄 Lancement de la version de base...")
            launch_base_version()
    else:
        print("🖥️ Autre plateforme détectée - Lancement de la version de base...")
        launch_base_version()

def launch_base_version():
    """Lance la version de base"""
    print("📚 Lancement de la version de base...")
    
    # Vérifier si les modules de base existent
    if Path("lemmatique_search.py").exists():
        print("✅ Module de recherche lemmatique trouvé")
        
        try:
            # Import et lancement de base
            import tkinter as tk
            from tkinter import ttk, scrolledtext
            from lemmatique_search import LemmatiqueSearchEngine, LemmatiqueSearchUI
            
            # Créer une application de base
            root = tk.Tk()
            root.title("OCR Grec - Version de Base")
            root.geometry("800x600")
            
            # Créer le moteur de recherche
            search_engine = LemmatiqueSearchEngine()
            ui = LemmatiqueSearchUI(root, search_engine)
            
            # Afficher l'interface
            ui.show_search_dialog()
            
            print("🎉 Application lancée avec succès!")
            root.mainloop()
            
        except Exception as e:
            print(f"❌ Erreur lors du lancement: {e}")
            print("💡 Vérifiez que toutes les dépendances sont installées")
    else:
        print("❌ Modules de base non trouvés")
        print("💡 Veuillez installer les dépendances ou utiliser la version optimisée")

if __name__ == "__main__":
    main() 