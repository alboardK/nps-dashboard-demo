"""Configuration de l'application."""

# config.py

# Configuration par défaut
DEFAULT_SETTINGS = {
    'seuil_representativite': 35,
}

# Configuration des catégories et métriques
METRIC_STRUCTURE = {
    'personnel': {
        'label': 'Personnel',
        'color': '#4CAF50',
        'metrics': {
            'Satisfaction_Coachs': 'Coachs',
            'Satisfaction_MNS': 'Maîtres nageurs',
            'Satisfaction_Accueil': 'Personnel d\'accueil',
            'Satisfaction_Conseiller': 'Conseillers sports'
        }
    },
    'infrastructure': {
        'label': 'Infrastructure',
        'color': '#2196F3',
        'metrics': {
            'Satisfaction_Proprete': 'Propreté générale',
            'Satisfaction_Vestiaires': 'Vestiaires',
            'Satisfaction_DispoEquipements': 'Équipements sportifs'
        }
    },
    'services': {
        'label': 'Services',
        'color': '#FF9800',
        'metrics': {
            'Satisfaction_Coaching': 'Cours collectifs',
            'Satisfaction_Piscine': 'Expérience piscine',
            'Satisfaction_Restauration': 'Restauration',
            'Satisfaction_DispoCours': 'Disponibilité des cours'
        }
    },
    'experience': {
        'label': 'Expérience',
        'color': '#9C27B0',
        'metrics': {
            'Satisfaction_Ambiance': 'Ambiance générale',
            'Satisfaction_Festive': 'Offre festive',
            'Satisfaction_Masterclass': 'Masterclass/événements'
        }
    }
}

# Mapping des colonnes du fichier source vers les noms standardisés
COLUMN_MAPPING = {
    "Notez de 1 à 5 avec 1 pour \"pas du tout satisfait\" et 5 pour \"Parfaitement satisfait\" votre satisfaction sur les services suivants : [les coachs]": "Satisfaction_coachs",
    "Notez de 1 à 5 avec 1 pour \"pas du tout satisfait\" et 5 pour \"Parfaitement satisfait\" votre satisfaction sur les services suivants : [les maitres nageurs]": "Satisfaction_maitres_nageurs",
    "Notez de 1 à 5 avec 1 pour \"pas du tout satisfait\" et 5 pour \"Parfaitement satisfait\" votre satisfaction sur les services suivants : [le personnel d'accueil]": "Satisfaction_accueil",
    "Notez de 1 à 5 avec 1 pour \"pas du tout satisfait\" et 5 pour \"Parfaitement satisfait\" votre satisfaction sur les services suivants : [le conseiller sports (commercial)]": "Satisfaction_conseiller",
    "Notez de 1 à 5 avec 1 pour \"pas du tout satisfait\" et 5 pour \"Parfaitement satisfait\" votre satisfaction sur les services suivants : [la propreté générale]": "Satisfaction_proprete",
    "Notez de 1 à 5 avec 1 pour \"pas du tout satisfait\" et 5 pour \"Parfaitement satisfait\" votre satisfaction sur les services suivants : [les vestiaires (douches / sauna/ serviettes..)]": "Satisfaction_vestiaires",
    "Notez de 1 à 5 avec 1 pour \"pas du tout satisfait\" et 5 pour \"Parfaitement satisfait\" votre satisfaction sur les services suivants : [la disponibilité des équipements sportifs]": "Satisfaction_equipements",
    "Notez de 1 à 5 avec 1 pour \"pas du tout satisfait\" et 5 pour \"Parfaitement satisfait\" votre satisfaction sur les services suivants : [La qualité des coaching en groupe]": "Satisfaction_cours",
    "Notez de 1 à 5 avec 1 pour \"pas du tout satisfait\" et 5 pour \"Parfaitement satisfait\" votre satisfaction sur les services suivants : [l'expérience piscine]": "Satisfaction_piscine",
    "Notez de 1 à 5 avec 1 pour \"pas du tout satisfait\" et 5 pour \"Parfaitement satisfait\" votre satisfaction sur les services suivants : [l'offre de restauration]": "Satisfaction_restauration",
    "Notez de 1 à 5 avec 1 pour \"pas du tout satisfait\" et 5 pour \"Parfaitement satisfait\" votre satisfaction sur les services suivants : [la disponibilité des cours sur le planning]": "Satisfaction_disponibilite_cours",
    "Notez de 1 à 5 avec 1 pour \"pas du tout satisfait\" et 5 pour \"Parfaitement satisfait\" votre satisfaction sur les services suivants : [l'ambiance générale]": "Satisfaction_ambiance",
    "Notez de 1 à 5 avec 1 pour \"pas du tout satisfait\" et 5 pour \"Parfaitement satisfait\" votre satisfaction sur les services suivants : [L'offre festive ]": "Satisfaction_offre_festive",
    "Notez de 1 à 5 avec 1 pour \"pas du tout satisfait\" et 5 pour \"Parfaitement satisfait\" votre satisfaction sur les services suivants : [les masterclass / evenements sportifs]": "Satisfaction_masterclass"
}

# Couleurs pour les scores
SCORE_COLORS = {
    'excellent': 'rgb(36, 161, 88)',   # Vert foncé
    'good': 'rgb(134, 188, 37)',       # Vert clair
    'average': 'rgb(241, 196, 15)',    # Jaune
    'poor': 'rgb(230, 126, 34)',       # Orange
    'bad': 'rgb(176, 52, 40)'          # Rouge foncé
}