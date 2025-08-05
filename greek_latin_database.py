# Base de données exhaustive des auteurs et œuvres gréco-latines
# Sources: Perseus Digital Library, TLG, PHI, et autres corpus académiques

GRECO_LATIN_DATABASE = {
    # ===== AUTEURS GRECS ANTIQUES =====
    
    # Époque archaïque (VIIIe-VIe siècle av. J.-C.)
    "Homère": {
        "période": "VIIIe siècle av. J.-C.",
        "œuvres": [
            "Iliade", "Odyssée", "Hymnes homériques", "Batrachomyomachie", 
            "Margites", "Épigones", "Chants cypriens", "Petite Iliade"
        ],
        "search_terms": ["μῆνιν", "ἄνδρα", "πολύτροπον", "Ἀχιλλεύς", "Ὀδυσσεύς", "Ἀγαμέμνων"]
    },
    
    "Hésiode": {
        "période": "VIIIe siècle av. J.-C.",
        "œuvres": [
            "Théogonie", "Les Travaux et les Jours", "Le Bouclier d'Héraclès",
            "Catalogue des femmes", "Préceptes de Chiron", "Mélampodie"
        ],
        "search_terms": ["θεογονία", "Ἔρις", "Πανδώρα", "Ἀφροδίτη", "Μοῖραι"]
    },
    
    "Sappho": {
        "période": "VIIe siècle av. J.-C.",
        "œuvres": [
            "Poèmes lyriques", "Hymne à Aphrodite", "Ode à Anactoria",
            "Épithalames", "Fragments"
        ],
        "search_terms": ["Ἀφροδίτα", "Ἀνακτορία", "Ἄδωνις", "λεύκοι", "μέλισσα"]
    },
    
    "Alcée": {
        "période": "VIIe siècle av. J.-C.",
        "œuvres": [
            "Odes politiques", "Chants de guerre", "Hymnes", "Chansons d'amour",
            "Fragments"
        ],
        "search_terms": ["ναῦς", "πόλεμος", "ἀνέμων", "οἶνος", "ἐλευθερία"]
    },
    
    "Archiloque": {
        "période": "VIIe siècle av. J.-C.",
        "œuvres": [
            "Épodes", "Élégies", "Iambes", "Hymnes", "Fragments"
        ],
        "search_terms": ["ἰάμβος", "ἐλεγεία", "παραίνεσις", "γνώμη"]
    },
    
    "Tyrtée": {
        "période": "VIIe siècle av. J.-C.",
        "œuvres": [
            "Élégies martiales", "Eunomie", "Constitution", "Fragments"
        ],
        "search_terms": ["ἀρετή", "πόλεμος", "Σπάρτη", "εὐνομία"]
    },
    
    "Solon": {
        "période": "VIIe-VIe siècle av. J.-C.",
        "œuvres": [
            "Élégies", "Iambes", "Tétramètres trochaïques", "Constitution",
            "Fragments politiques"
        ],
        "search_terms": ["δικαιοσύνη", "εὐνομία", "Ἀθήναι", "σεῖσάχθεια"]
    },
    
    "Théognis": {
        "période": "VIe siècle av. J.-C.",
        "œuvres": [
            "Élégies", "Maximes", "Poèmes politiques", "Fragments"
        ],
        "search_terms": ["ἀρετή", "κακία", "γνώμη", "παραίνεσις"]
    },
    
    "Pindare": {
        "période": "VIe-Ve siècle av. J.-C.",
        "œuvres": [
            "Odes pythiques", "Odes olympiques", "Odes néméennes", "Odes isthmiques",
            "Hymnes", "Péans", "Dithyrambes", "Épinicies", "Fragments"
        ],
        "search_terms": ["νίκη", "ἀρετή", "θεοί", "ἀθλητής", "χάρις"]
    },
    
    "Bacchylide": {
        "période": "VIe-Ve siècle av. J.-C.",
        "œuvres": [
            "Odes", "Dithyrambes", "Épinicies", "Hymnes", "Fragments"
        ],
        "search_terms": ["νίκη", "θεοί", "χάρις", "ἀρετή"]
    },
    
    # Époque classique (Ve-IVe siècle av. J.-C.)
    "Eschyle": {
        "période": "Ve siècle av. J.-C.",
        "œuvres": [
            "Les Perses", "Les Sept contre Thèbes", "Les Suppliantes", 
            "L'Orestie (Agamemnon, Les Choéphores, Les Euménides)",
            "Prométhée enchaîné", "Prométhée délivré", "Prométhée porteur de feu"
        ],
        "search_terms": ["δράμα", "τραγῳδία", "μοῖρα", "δίκη", "ἄτη"]
    },
    
    "Sophocle": {
        "période": "Ve siècle av. J.-C.",
        "œuvres": [
            "Antigone", "Œdipe roi", "Œdipe à Colone", "Électre", "Ajax",
            "Les Trachiniennes", "Philoctète", "Œdipe à Colone"
        ],
        "search_terms": ["τύχη", "ἀνάγκη", "δίκη", "θεοί", "μοῖρα"]
    },
    
    "Euripide": {
        "période": "Ve siècle av. J.-C.",
        "œuvres": [
            "Médée", "Hippolyte", "Les Bacchantes", "Iphigénie en Aulide",
            "Iphigénie en Tauride", "Hélène", "Andromaque", "Hécube",
            "Les Troyennes", "Électre", "Oreste", "Ion", "Alceste"
        ],
        "search_terms": ["πάθος", "ἔρως", "μανία", "θεοί", "τύχη"]
    },
    
    "Aristophane": {
        "période": "Ve-IVe siècle av. J.-C.",
        "œuvres": [
            "Les Nuées", "Les Guêpes", "Les Oiseaux", "Lysistrata",
            "Les Grenouilles", "L'Assemblée des femmes", "Les Cavaliers",
            "La Paix", "Les Acharniens", "Ploutos"
        ],
        "search_terms": ["κωμῳδία", "σάτυρος", "παραβάλλω", "γέλως"]
    },
    
    "Hérodote": {
        "période": "Ve siècle av. J.-C.",
        "œuvres": [
            "Histoires", "Enquête", "Logoi", "Fragments"
        ],
        "search_terms": ["ἱστορία", "λόγος", "θαῦμα", "νόμος", "θεοί"]
    },
    
    "Thucydide": {
        "période": "Ve siècle av. J.-C.",
        "œuvres": [
            "Histoire de la guerre du Péloponnèse", "Discours", "Fragments"
        ],
        "search_terms": ["πόλεμος", "λόγος", "ἀλήθεια", "δύναμις", "στρατηγός"]
    },
    
    "Xénophon": {
        "période": "Ve-IVe siècle av. J.-C.",
        "œuvres": [
            "Anabase", "Cyropédie", "Mémorables", "Économique",
            "Helléniques", "Agesilas", "Hiéron", "Constitution des Lacédémoniens"
        ],
        "search_terms": ["στρατηγός", "ἀρετή", "παιδεία", "οἰκονομία"]
    },
    
    "Platon": {
        "période": "Ve-IVe siècle av. J.-C.",
        "œuvres": [
            "La République", "Le Banquet", "Phèdre", "Apologie de Socrate",
            "Criton", "Phédon", "Timée", "Lois", "Théétète", "Parménide",
            "Sophiste", "Politique", "Philèbe", "Lysis", "Charmide",
            "Lachès", "Protagoras", "Gorgias", "Ménon", "Euthydème"
        ],
        "search_terms": ["ἰδέα", "ψυχή", "ἀρετή", "σοφία", "φιλοσοφία"]
    },
    
    "Aristote": {
        "période": "IVe siècle av. J.-C.",
        "œuvres": [
            "Éthique à Nicomaque", "Politique", "Poétique", "Métaphysique",
            "Organon", "Physique", "De l'âme", "Rhétorique", "Éthique à Eudème",
            "Grande Morale", "Constitution d'Athènes"
        ],
        "search_terms": ["ἀρετή", "εὐδαιμονία", "λόγος", "οὐσία", "ἐνέργεια"]
    },
    
    "Isocrate": {
        "période": "Ve-IVe siècle av. J.-C.",
        "œuvres": [
            "Panégyrique", "Philippe", "Aréopagitique", "Sur la paix",
            "Contre les sophistes", "Éloge d'Hélène", "Busiris"
        ],
        "search_terms": ["λόγος", "παιδεία", "φιλοσοφία", "πολιτική"]
    },
    
    "Démosthène": {
        "période": "IVe siècle av. J.-C.",
        "œuvres": [
            "Philippiques", "Olynthiennes", "Sur la couronne", "Contre Midias",
            "Contre Androtion", "Contre Timocrate", "Discours politiques"
        ],
        "search_terms": ["δημοκρατία", "ἐλευθερία", "πατρίς", "ἀρετή"]
    },
    
    "Eschine": {
        "période": "IVe siècle av. J.-C.",
        "œuvres": [
            "Contre Timarque", "Sur l'ambassade", "Contre Ctésiphon"
        ],
        "search_terms": ["δημοκρατία", "νόμος", "ἀρετή", "πατρίς"]
    },
    
    # Époque hellénistique (IIIe-Ier siècle av. J.-C.)
    "Théocrite": {
        "période": "IIIe siècle av. J.-C.",
        "œuvres": [
            "Idylles", "Bucoliques", "Épigrammes", "Hymnes", "Fragments"
        ],
        "search_terms": ["βουκολικός", "ποιμήν", "ἄγρος", "ἔρως"]
    },
    
    "Callimaque": {
        "période": "IIIe siècle av. J.-C.",
        "œuvres": [
            "Hymnes", "Épigrammes", "Aitia", "Hécale", "Iambes"
        ],
        "search_terms": ["ποίησις", "ἐπύλλιον", "ἐλεγεία", "γραμματική"]
    },
    
    "Apollonios de Rhodes": {
        "période": "IIIe siècle av. J.-C.",
        "œuvres": [
            "Argonautiques", "Fondations", "Épigrammes", "Fragments"
        ],
        "search_terms": ["Ἀργώ", "Ἰάσων", "Μήδεια", "θαῦμα"]
    },
    
    "Polybe": {
        "période": "IIe siècle av. J.-C.",
        "œuvres": [
            "Histoires", "Fragments", "Discours"
        ],
        "search_terms": ["ἱστορία", "πολιτική", "στρατηγία", "αἰτία"]
    },
    
    "Posidonios": {
        "période": "IIe-Ier siècle av. J.-C.",
        "œuvres": [
            "Sur l'océan", "Météorologiques", "Éthique", "Fragments"
        ],
        "search_terms": ["φύσις", "κόσμος", "ψυχή", "θεοί"]
    },
    
    # Époque romaine (Ier siècle av. J.-C. - Ve siècle ap. J.-C.)
    "Plutarque": {
        "période": "Ier-IIe siècle ap. J.-C.",
        "œuvres": [
            "Vies parallèles", "Œuvres morales", "Vies des hommes illustres",
            "Moralia", "Vie d'Alexandre", "Vie de César"
        ],
        "search_terms": ["βίος", "ἀρετή", "παράδειγμα", "φιλοσοφία"]
    },
    
    "Lucien": {
        "période": "IIe siècle ap. J.-C.",
        "œuvres": [
            "Dialogues des morts", "Histoires vraies", "L'Âne d'or",
            "Dialogues des dieux", "Dialogues marins", "Satires"
        ],
        "search_terms": ["διαλογή", "σάτυρος", "γέλως", "φιλοσοφία"]
    },
    
    "Épictète": {
        "période": "Ier-IIe siècle ap. J.-C.",
        "œuvres": [
            "Manuel", "Entretiens", "Fragments"
        ],
        "search_terms": ["ἀρετή", "προαίρεσις", "φύσις", "λόγος"]
    },
    
    "Marc Aurèle": {
        "période": "IIe siècle ap. J.-C.",
        "œuvres": [
            "Pensées pour moi-même", "Correspondance", "Fragments"
        ],
        "search_terms": ["λογισμός", "φύσις", "ἀρετή", "θεοί"]
    },
    
    "Plotin": {
        "période": "IIIe siècle ap. J.-C.",
        "œuvres": [
            "Ennéades", "Traités", "Fragments"
        ],
        "search_terms": ["ἕν", "νοῦς", "ψυχή", "οὐσία"]
    },
    
    "Porphyre": {
        "période": "IIIe siècle ap. J.-C.",
        "œuvres": [
            "Vie de Plotin", "Isagoge", "Contre les chrétiens", "Fragments"
        ],
        "search_terms": ["φιλοσοφία", "λόγος", "θεοί", "ψυχή"]
    },
    
    "Jamblique": {
        "période": "IVe siècle ap. J.-C.",
        "œuvres": [
            "Vie de Pythagore", "Protreptique", "Théologie", "Fragments"
        ],
        "search_terms": ["θεοί", "ψυχή", "μαθηματικά", "θεουργία"]
    },
    
    "Proclus": {
        "période": "Ve siècle ap. J.-C.",
        "œuvres": [
            "Éléments de théologie", "Commentaires", "Hymnes", "Fragments"
        ],
        "search_terms": ["θεοί", "νοῦς", "ψυχή", "ἕν"]
    },
    
    # ===== AUTEURS LATINS =====
    
    # République (IIIe-Ier siècle av. J.-C.)
    "Ennius": {
        "période": "IIIe-IIe siècle av. J.-C.",
        "œuvres": [
            "Annales", "Tragédies", "Comédies", "Satires", "Fragments"
        ],
        "search_terms": ["Roma", "virtus", "fides", "pietas"]
    },
    
    "Plautus": {
        "période": "IIIe-IIe siècle av. J.-C.",
        "œuvres": [
            "Amphitryon", "Aulularia", "Captivi", "Casina", "Cistellaria",
            "Curculio", "Epidicus", "Menaechmi", "Mercator", "Miles gloriosus"
        ],
        "search_terms": ["comedia", "servus", "senex", "adulescens"]
    },
    
    "Térence": {
        "période": "IIe siècle av. J.-C.",
        "œuvres": [
            "Andria", "Hecyra", "Heautontimorumenos", "Eunuchus",
            "Phormio", "Adelphoe"
        ],
        "search_terms": ["comedia", "humanitas", "urbanitas"]
    },
    
    "Lucrèce": {
        "période": "Ier siècle av. J.-C.",
        "œuvres": [
            "De rerum natura", "Fragments"
        ],
        "search_terms": ["natura", "atomus", "voluptas", "religio"]
    },
    
    "Catulle": {
        "période": "Ier siècle av. J.-C.",
        "œuvres": [
            "Carmina", "Poèmes", "Épigrammes", "Fragments"
        ],
        "search_terms": ["Lesbia", "amor", "odi", "amo", "poeta"]
    },
    
    "Cicéron": {
        "période": "Ier siècle av. J.-C.",
        "œuvres": [
            "De oratore", "De republica", "De legibus", "De officiis",
            "De finibus", "Tusculanes", "De natura deorum", "Catilinaires",
            "Philippiques", "Pro Milone", "Pro Archia", "Lettres"
        ],
        "search_terms": ["oratio", "eloquentia", "virtus", "res publica"]
    },
    
    "César": {
        "période": "Ier siècle av. J.-C.",
        "œuvres": [
            "Commentaires sur la guerre des Gaules", "Guerre civile",
            "Guerre d'Alexandrie", "Guerre d'Afrique", "Guerre d'Espagne"
        ],
        "search_terms": ["bellum", "exercitus", "victoria", "virtus"]
    },
    
    "Salluste": {
        "période": "Ier siècle av. J.-C.",
        "œuvres": [
            "Conjuration de Catilina", "Guerre de Jugurtha", "Histoires"
        ],
        "search_terms": ["virtus", "ambitio", "avaritia", "res publica"]
    },
    
    "Virgile": {
        "période": "Ier siècle av. J.-C.",
        "œuvres": [
            "Énéide", "Géorgiques", "Bucoliques", "Appendix Vergiliana"
        ],
        "search_terms": ["Aeneas", "Roma", "fatum", "pietas", "virtus"]
    },
    
    "Horace": {
        "période": "Ier siècle av. J.-C.",
        "œuvres": [
            "Odes", "Épîtres", "Satires", "Art poétique", "Chant séculaire"
        ],
        "search_terms": ["carpe diem", "aurea mediocritas", "beatus ille"]
    },
    
    "Ovide": {
        "période": "Ier siècle av. J.-C.",
        "œuvres": [
            "Métamorphoses", "Amours", "Art d'aimer", "Remèdes à l'amour",
            "Héroïdes", "Fastes", "Tristes", "Pontiques"
        ],
        "search_terms": ["amor", "mutatio", "fatum", "poeta"]
    },
    
    "Tite-Live": {
        "période": "Ier siècle av. J.-C.",
        "œuvres": [
            "Histoire romaine", "Ab Urbe condita", "Fragments"
        ],
        "search_terms": ["Roma", "virtus", "libertas", "res publica"]
    },
    
    # Empire (Ier-Ve siècle ap. J.-C.)
    "Sénèque": {
        "période": "Ier siècle ap. J.-C.",
        "œuvres": [
            "Lettres à Lucilius", "De la colère", "De la clémence",
            "De la vie heureuse", "De la brièveté de la vie", "Tragédies"
        ],
        "search_terms": ["virtus", "sapientia", "fortuna", "mors"]
    },
    
    "Lucain": {
        "période": "Ier siècle ap. J.-C.",
        "œuvres": [
            "Pharsale", "Fragments", "Épigrammes"
        ],
        "search_terms": ["bellum civile", "fatum", "libertas", "virtus"]
    },
    
    "Perse": {
        "période": "Ier siècle ap. J.-C.",
        "œuvres": [
            "Satires", "Fragments"
        ],
        "search_terms": ["satira", "virtus", "vita", "mores"]
    },
    
    "Juvénal": {
        "période": "Ier-IIe siècle ap. J.-C.",
        "œuvres": [
            "Satires", "Fragments"
        ],
        "search_terms": ["satira", "virtus", "vita", "mores", "Roma"]
    },
    
    "Tacite": {
        "période": "Ier-IIe siècle ap. J.-C.",
        "œuvres": [
            "Annales", "Histoires", "Agricola", "Germanie", "Dialogue des orateurs"
        ],
        "search_terms": ["libertas", "virtus", "res publica", "tyrannus"]
    },
    
    "Pline l'Ancien": {
        "période": "Ier siècle ap. J.-C.",
        "œuvres": [
            "Histoire naturelle", "Fragments"
        ],
        "search_terms": ["natura", "scientia", "mirabilia", "historia"]
    },
    
    "Pline le Jeune": {
        "période": "Ier-IIe siècle ap. J.-C.",
        "œuvres": [
            "Lettres", "Panégyrique de Trajan", "Fragments"
        ],
        "search_terms": ["epistula", "eloquentia", "virtus", "amicitia"]
    },
    
    "Suétone": {
        "période": "Ier-IIe siècle ap. J.-C.",
        "œuvres": [
            "Vies des douze Césars", "De viris illustribus", "Fragments"
        ],
        "search_terms": ["vita", "mores", "virtus", "vitia"]
    },
    
    "Apulée": {
        "période": "IIe siècle ap. J.-C.",
        "œuvres": [
            "L'Âne d'or", "Apologie", "Florides", "De deo Socratis"
        ],
        "search_terms": ["fabulae", "mirabilia", "philosophia", "religio"]
    },
    
    "Ammien Marcellin": {
        "période": "IVe siècle ap. J.-C.",
        "œuvres": [
            "Histoires", "Res gestae", "Fragments"
        ],
        "search_terms": ["historia", "bellum", "virtus", "fortuna"]
    },
    
    "Claudien": {
        "période": "IVe-Ve siècle ap. J.-C.",
        "œuvres": [
            "Poèmes", "Épigrammes", "Panégyriques", "Fragments"
        ],
        "search_terms": ["panegyricus", "virtus", "victoria", "imperator"]
    },
    
    "Boèce": {
        "période": "Ve-VIe siècle ap. J.-C.",
        "œuvres": [
            "Consolation de la philosophie", "Traités", "Fragments"
        ],
        "search_terms": ["philosophia", "fortuna", "virtus", "sapientia"]
    },
    
    # ===== AUTEURS CHRÉTIENS =====
    
    "Clément d'Alexandrie": {
        "période": "IIe-IIIe siècle ap. J.-C.",
        "œuvres": [
            "Protreptique", "Pédagogue", "Stromates", "Fragments"
        ],
        "search_terms": ["λόγος", "παιδεία", "φιλοσοφία", "θεός"]
    },
    
    "Origène": {
        "période": "IIe-IIIe siècle ap. J.-C.",
        "œuvres": [
            "Contre Celse", "Commentaires", "Homélies", "Fragments"
        ],
        "search_terms": ["λόγος", "θεός", "ψυχή", "ἀλήθεια"]
    },
    
    "Eusèbe de Césarée": {
        "période": "IIIe-IVe siècle ap. J.-C.",
        "œuvres": [
            "Histoire ecclésiastique", "Préparation évangélique", "Fragments"
        ],
        "search_terms": ["ἐκκλησία", "θεός", "λόγος", "ἱστορία"]
    },
    
    "Basile de Césarée": {
        "période": "IVe siècle ap. J.-C.",
        "œuvres": [
            "Hexaéméron", "Homélies", "Lettres", "Règles monastiques"
        ],
        "search_terms": ["θεός", "κτίσις", "μοναχός", "ἀρετή"]
    },
    
    "Grégoire de Nazianze": {
        "période": "IVe siècle ap. J.-C.",
        "œuvres": [
            "Discours théologiques", "Poèmes", "Lettres", "Fragments"
        ],
        "search_terms": ["θεός", "λόγος", "τριάς", "ἀρετή"]
    },
    
    "Grégoire de Nysse": {
        "période": "IVe siècle ap. J.-C.",
        "œuvres": [
            "Vie de Moïse", "Homélies", "Traités", "Fragments"
        ],
        "search_terms": ["θεός", "ψυχή", "ἀρετή", "μοναχός"]
    },
    
    "Jean Chrysostome": {
        "période": "IVe-Ve siècle ap. J.-C.",
        "œuvres": [
            "Homélies", "Commentaires", "Lettres", "Fragments"
        ],
        "search_terms": ["λόγος", "ἐκκλησία", "ἀρετή", "θεός"]
    },
    
    "Augustin": {
        "période": "IVe-Ve siècle ap. J.-C.",
        "œuvres": [
            "Confessions", "Cité de Dieu", "De la Trinité", "Lettres",
            "Sermons", "Commentaires"
        ],
        "search_terms": ["Deus", "gratia", "peccatum", "caritas", "fides"]
    },
    
    "Jérôme": {
        "période": "IVe-Ve siècle ap. J.-C.",
        "œuvres": [
            "Vulgate", "Lettres", "Commentaires", "Vie des saints"
        ],
        "search_terms": ["scriptura", "monachus", "virginitas", "doctrina"]
    }
}

# Fonction pour obtenir tous les auteurs
def get_all_authors():
    """Retourne la liste de tous les auteurs"""
    return list(GRECO_LATIN_DATABASE.keys())

# Fonction pour obtenir toutes les œuvres d'un auteur
def get_works_by_author(author_name):
    """Retourne toutes les œuvres d'un auteur donné"""
    if author_name in GRECO_LATIN_DATABASE:
        return GRECO_LATIN_DATABASE[author_name]["œuvres"]
    return []

# Fonction pour rechercher des auteurs par terme
def search_authors(search_term):
    """Recherche des auteurs contenant le terme de recherche"""
    results = []
    search_term_lower = search_term.lower()
    
    for author_name, author_info in GRECO_LATIN_DATABASE.items():
        if (search_term_lower in author_name.lower() or
            search_term_lower in author_info["période"].lower() or
            any(search_term_lower in work.lower() for work in author_info["œuvres"])):
            results.append(author_name)
    
    return results

# Fonction pour obtenir les informations complètes d'un auteur
def get_author_info(author_name):
    """Retourne les informations complètes d'un auteur"""
    return GRECO_LATIN_DATABASE.get(author_name, {}) 