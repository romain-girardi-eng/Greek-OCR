# 🧠 Fonctionnalité "Think !" - Analyse Sémantique

## 📋 Vue d'ensemble

La fonctionnalité **"Think !"** est un système d'analyse sémantique intelligent qui transforme le texte OCR brut en informations structurées et compréhensibles. Elle utilise l'intelligence artificielle pour analyser le contenu et extraire des insights profonds.

## 🎯 Fonctionnalités principales

### **1. Identification automatique des concepts**
- **Philosophie** : Concepts métaphysiques, éthiques, logiques
- **Théologie** : Concepts religieux, divins, spirituels
- **Histoire** : Événements, périodes, civilisations
- **Littérature** : Styles, genres, figures de style
- **Science** : Phénomènes naturels, lois, observations

### **2. Extraction des entités**
- **Personnes** : Noms de personnes, personnages historiques, auteurs
- **Lieux** : Villes, pays, régions, bâtiments importants
- **Dates** : Années, siècles, périodes historiques
- **Concepts** : Idées, notions philosophiques, doctrines
- **Références** : Citations, sources, œuvres mentionnées

### **3. Génération de résumés automatiques**
- Résumés détaillés en français
- Identification du sujet principal
- Extraction des idées clés
- Contexte historique ou philosophique
- Conclusions et enseignements

### **4. Détection des citations et références**
- **Citations directes** : Textes entre guillemets
- **Références indirectes** : Allusions à d'autres œuvres
- **Sources** : Mentions d'œuvres, livres, textes

## 🚀 Utilisation

### **Accès à la fonctionnalité**

#### **Via le menu**
```
OCR → 🧠 Think ! - Analyse Sémantique
```

#### **Via la barre d'outils**
```
Bouton "🧠 Think !" (mis en évidence)
```

#### **Raccourci clavier**
```
Cmd+T (macOS)
```

### **Prérequis**
1. **OCR effectué** : Avoir des résultats OCR à analyser
2. **Connexion internet** : Pour l'API OpenRouter
3. **Clé API** : Configuration de la clé OpenRouter

## 🔧 Architecture technique

### **Modules principaux**

#### **1. SemanticAnalyzer**
```python
class SemanticAnalyzer:
    """Analyseur sémantique intelligent"""
    
    def analyze_text(self, text: str, language: str) -> SemanticAnalysis:
        # Analyse complète du texte
```

#### **2. SemanticAnalysisUI**
```python
class SemanticAnalysisUI:
    """Interface utilisateur pour l'analyse sémantique"""
    
    def show_analysis_dialog(self, text: str, language: str):
        # Affichage du dialogue d'analyse
```

#### **3. Classes de données**
```python
@dataclass
class Entity:
    """Entité extraite du texte"""
    name: str
    type: str  # person, place, date, concept, reference
    confidence: float
    context: str

@dataclass
class Concept:
    """Concept identifié dans le texte"""
    name: str
    category: str  # philosophy, theology, history, literature, science
    description: str
    confidence: float

@dataclass
class Citation:
    """Citation ou référence identifiée"""
    text: str
    source: Optional[str]
    type: str  # direct, indirect, reference
    confidence: float
```

### **Flux de traitement**

```
Texte OCR → Extraction entités → Identification concepts → 
Détection citations → Génération résumé → Interface utilisateur
```

## 📊 Interface utilisateur

### **Onglets de résultats**

#### **1. 📝 Résumé**
- Résumé détaillé en français
- Analyse du contenu principal
- Contexte et enseignements

#### **2. 👥 Entités**
- Liste des entités extraites
- Type et confiance
- Contexte d'apparition

#### **3. 💡 Concepts**
- Concepts identifiés par catégorie
- Descriptions détaillées
- Concepts liés

#### **4. 📚 Citations**
- Citations et références
- Sources identifiées
- Types de citations

#### **5. 📊 Métadonnées**
- Informations techniques
- Statistiques d'analyse
- Données de performance

## 🎨 Exemples d'utilisation

### **Exemple 1 : Texte philosophique grec**
```
Texte OCR: "ὁ δὲ νοῦς θύραθεν ἐπεισιέναι φαίνεται..."

Résultats Think !:
- Concepts: νοῦς (philosophy), θύραθεν (philosophy)
- Entités: Aristote (person), Lycée (place)
- Citations: Référence à De Anima
- Résumé: Discussion sur l'intellect et sa relation avec l'âme...
```

### **Exemple 2 : Texte théologique**
```
Texte OCR: "ἐν ἀρχῇ ἦν ὁ λόγος..."

Résultats Think !:
- Concepts: λόγος (theology), ἀρχῇ (theology)
- Entités: Jean (person), Évangile (reference)
- Citations: Citation directe de l'Évangile de Jean
- Résumé: Prologue de l'Évangile de Jean, concept du Logos...
```

### **Exemple 3 : Texte historique**
```
Texte OCR: "Ἀλέξανδρος ὁ Μέγας..."

Résultats Think !:
- Concepts: conquête (history), empire (history)
- Entités: Alexandre le Grand (person), Macédoine (place)
- Dates: 4e siècle av. J.-C.
- Résumé: Récit des conquêtes d'Alexandre le Grand...
```

## ⚙️ Configuration

### **Clé API OpenRouter**
```python
# Dans config.py
AI_CONFIG = {
    "openrouter": {
        "api_key": "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"
    }
}
```

### **Modèle IA utilisé**
- **Modèle** : Claude 3 Haiku (Anthropic)
- **Température** : 0.3 (cohérence élevée)
- **Tokens max** : 1000 (réponses détaillées)

## 📈 Métriques de performance

### **Indicateurs de qualité**
- **Confiance globale** : Score de 0 à 1
- **Nombre d'entités** : Entités extraites
- **Nombre de concepts** : Concepts identifiés
- **Nombre de citations** : Références détectées

### **Optimisations**
- **Threading** : Analyse en arrière-plan
- **Cache** : Mise en cache des résultats
- **Validation** : Vérification des données
- **Gestion d'erreurs** : Récupération robuste

## 🔍 Cas d'usage avancés

### **1. Analyse comparative**
```python
# Comparer plusieurs textes
analysis1 = analyzer.analyze_text(text1, "grc")
analysis2 = analyzer.analyze_text(text2, "grc")

# Identifier les concepts communs
common_concepts = set(c1.name for c1 in analysis1.concepts) & set(c2.name for c2 in analysis2.concepts)
```

### **2. Recherche thématique**
```python
# Filtrer par catégorie
philosophy_concepts = [c for c in analysis.concepts if c.category == "philosophy"]
theology_concepts = [c for c in analysis.concepts if c.category == "theology"]
```

### **3. Analyse de confiance**
```python
# Filtrer par niveau de confiance
high_confidence_entities = [e for e in analysis.entities if e.confidence > 0.8]
```

## 🛠️ Développement

### **Ajout de nouvelles catégories**
```python
# Dans SemanticAnalyzer
self.concept_categories["nouvelle_categorie"] = ["mot1", "mot2", "mot3"]
```

### **Personnalisation des prompts**
```python
# Modification des prompts d'analyse
def _custom_prompt(self, text: str, language: str) -> str:
    return f"Prompt personnalisé pour {language}: {text}"
```

### **Intégration d'autres APIs**
```python
# Support d'autres modèles IA
def _call_custom_api(self, prompt: str) -> Any:
    # Implémentation personnalisée
    pass
```

## 🔮 Évolutions futures

### **1. Fonctionnalités avancées**
- **Analyse comparative** : Comparaison de plusieurs textes
- **Graphe de connaissances** : Visualisation des relations
- **Traduction automatique** : Traduction des concepts
- **Recherche sémantique** : Recherche par concept

### **2. Intégrations**
- **Bases de données** : Stockage des analyses
- **APIs externes** : Wikipédia, bases de données académiques
- **Export avancé** : JSON, XML, RDF
- **Collaboration** : Partage d'analyses

### **3. Intelligence artificielle**
- **Modèles locaux** : Analyse hors ligne
- **Apprentissage** : Amélioration continue
- **Personnalisation** : Adaptation au domaine
- **Multilingue** : Support de plus de langues

## 📝 Exemples de code

### **Utilisation basique**
```python
from semantic_analyzer import SemanticAnalyzer

# Créer l'analyseur
analyzer = SemanticAnalyzer(api_key="your_api_key")

# Analyser un texte
analysis = analyzer.analyze_text("Votre texte grec ici", "grc")

# Accéder aux résultats
print(f"Résumé: {analysis.summary}")
print(f"Entités: {len(analysis.entities)}")
print(f"Concepts: {len(analysis.concepts)}")
```

### **Interface utilisateur**
```python
from semantic_analyzer import SemanticAnalysisUI

# Créer l'interface
ui = SemanticAnalysisUI(parent_window, analyzer)

# Afficher l'analyse
ui.show_analysis_dialog("Votre texte", "grc")
```

### **Export des résultats**
```python
import json

# Exporter en JSON
def export_analysis(analysis: SemanticAnalysis, filename: str):
    data = {
        "summary": analysis.summary,
        "entities": [{"name": e.name, "type": e.type} for e in analysis.entities],
        "concepts": [{"name": c.name, "category": c.category} for c in analysis.concepts],
        "citations": [{"text": cit.text, "source": cit.source} for cit in analysis.citations],
        "metadata": analysis.metadata
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
```

---

## 🎯 Conclusion

La fonctionnalité **"Think !"** transforme l'OCR en véritable compréhension du contenu, offrant des insights profonds sur les textes grecs anciens et modernes. Elle combine l'intelligence artificielle avec une interface utilisateur intuitive pour créer une expérience d'analyse sémantique unique. 