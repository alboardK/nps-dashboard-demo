"""Configuration de l'application."""

# config.py

# Critères de satisfaction
SATISFACTION_CRITERIA = {
    'Satisfaction_Salle': 'Expérience salle de sport',
    'Satisfaction_Piscine': 'Expérience piscine',
    'Satisfaction_Coaching': 'Qualité coaching en groupe',
    'Satisfaction_DispoCours': 'Disponibilité des cours',
    'Satisfaction_DispoEquipements': 'Disponibilité équipements',
    'Satisfaction_Coachs': 'Les coachs',
    'Satisfaction_MNS': 'Les maîtres nageurs',
    'Satisfaction_Accueil': "Personnel d'accueil",
    'Satisfaction_Conseiller': 'Conseiller sports',
    'Satisfaction_Ambiance': 'Ambiance générale',
    'Satisfaction_Proprete': 'Propreté générale',
    'Satisfaction_Vestiaires': 'Vestiaires',
    'Satisfaction_Restauration': 'Offre restauration',
    'Satisfaction_Festive': 'Offre festive'
}

METRIC_CATEGORIES = {
    "Expérience": ['Satisfaction_Salle', 'Satisfaction_Piscine'],
    "Personnel": ['Satisfaction_Coachs', 'Satisfaction_MNS', 'Satisfaction_Accueil', 'Satisfaction_Conseiller'],
    "Services": ['Satisfaction_Coaching', 'Satisfaction_DispoCours', 'Satisfaction_DispoEquipements', 'Satisfaction_Restauration'],
    "Infrastructure": ['Satisfaction_Ambiance', 'Satisfaction_Proprete', 'Satisfaction_Vestiaires', 'Satisfaction_Festive']
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
    'theme': 'Clair'  # Définir le thème par défaut
}