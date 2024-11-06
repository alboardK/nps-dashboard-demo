# data_preprocessing.py

import pandas as pd

# Renommer les colonnes en utilisant des mots-clés flexibles
def rename_columns_flexibly(df):
    rename_mapping = {
        "Horodateur": "Date",
        "Adresse e-mail": "Email",
        "Recommandation": "Recommandation",
        "Pourquoi cette note": "PourquoiNote",
        "probabilité que vous soyez toujours abonné": "ProbabiliteReabo",
        "Pourquoi cette réponse": "PourquoiReabo",
        "salle de sport": "Satisfaction_Salle",
        "piscine": "Satisfaction_Piscine",
        "coaching en groupe": "Satisfaction_Coaching",
        "disponibilité des cours": "Satisfaction_DispoCours",
        "disponibilité des équipements": "Satisfaction_DispoEquipements",
        "coachs": "Satisfaction_Coachs",
        "maitres nageurs": "Satisfaction_MNS",
        "personnel d'accueil": "Satisfaction_Accueil",
        "conseiller sports": "Satisfaction_Conseiller",
        "ambiance générale": "Satisfaction_Ambiance",
        "propreté générale": "Satisfaction_Proprete",
        "vestiaires": "Satisfaction_Vestiaires",
        "offre de restauration": "Satisfaction_Restauration",
        "offre festive": "Satisfaction_Festive",
        "masterclass / evenements sportifs": "Satisfaction_Masterclass",
        "Quelles améliorations proposeriez": "Ameliorations",
        "Votre Nom": "Nom",
        "Votre prénom": "Prenom",
        "Score": "Score",
        "MOTS CLES": "MotsCles"
    }

    new_column_names = {}
    for col in df.columns:
        for keyword, new_name in rename_mapping.items():
            if keyword.lower() in col.lower():
                new_column_names[col] = new_name
                break

    df = df.rename(columns=new_column_names)
    return df

# Correction d'anomalies dans les colonnes
def correct_anomalies(df):
    if "Satisfaction_DispoCours" in df.columns:
        df['Satisfaction_DispoCours'] = df['Satisfaction_DispoCours'].replace(0, pd.NA)
    return df

# Fonction pour catégoriser les scores NPS
def get_nps_category(score):
    try:
        score = float(score)
        if score >= 8:
            return "Promoter"
        elif score >= 6:
            return "Passive"
        else:
            return "Detractor"
    except ValueError:
        return "Unknown"

# Fonction de prétraitement des données
def preprocess_data(df):
    # Renommer les colonnes
    df = rename_columns_flexibly(df)
    
    # Correction des anomalies
    df = correct_anomalies(df)
    
    # Conversion de la colonne 'Date' en format datetime avec le bon format
    # Remplace "jour/mois/année" par le format correct si nécessaire
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
    
    # Conversion stricte de 'Recommandation' en float, en remplaçant les erreurs par NaN
    df['Recommandation'] = pd.to_numeric(df['Recommandation'], errors='coerce')

    # Ajout : conversion des colonnes de satisfaction en numérique
    satisfaction_columns = [col for col in df.columns if 'Satisfaction_' in col]
    for col in satisfaction_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Suppression des lignes avec des NaN dans 'Recommandation' après conversion
    df = df.dropna(subset=['Recommandation'])

    # Catégoriser les scores NPS et ajouter une colonne 'Catégorie'
    df['Catégorie'] = df['Recommandation'].apply(get_nps_category)
    
    # Vérifications de test
    print("Colonnes après renommage :", df.columns.tolist())
    print("Types des colonnes :", df.dtypes)
    print("Aperçu des premières lignes :", df.head())
    
    return df