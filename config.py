"""Configuration de l'application."""

# Critères de satisfaction
SATISFACTION_CRITERIA = {
    'experience_salle': 'Expérience salle de sport',
    'experience_piscine': 'Expérience piscine',
    'coaching_groupe': 'Qualité coaching en groupe',
    'disponibilite_cours': 'Disponibilité des cours',
    'disponibilite_equipements': 'Disponibilité équipements',
    'coachs': 'Les coachs',
    'maitres_nageurs': 'Les maîtres nageurs',
    'accueil': 'Personnel d\'accueil',
    'commercial': 'Conseiller sports',
    'ambiance': 'Ambiance générale',
    'proprete': 'Propreté générale',
    'vestiaires': 'Vestiaires',
    'restauration': 'Offre restauration',
    'evenements': 'Offre festive'
}

# Catégories de métriques
METRIC_CATEGORIES = {
    "Expérience": ['experience_salle', 'experience_piscine'],
    "Personnel": ['coachs', 'maitres_nageurs', 'accueil', 'commercial'],
    "Services": ['coaching_groupe', 'disponibilite_cours', 'disponibilite_equipements', 'restauration'],
    "Infrastructure": ['ambiance', 'proprete', 'vestiaires', 'evenements']
}

# Couleurs pour les graphiques
COLORS = {
    'Promoteur': '#2ECC71',
    'Neutre': '#F1C40F',
    'Détracteur': '#E74C3C'
}

# Configuration par défaut
DEFAULT_SETTINGS = {
    'seuil_representativite': 35,
    'theme': 'Clair'
}