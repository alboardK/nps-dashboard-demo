import gspread
import pandas as pd
import numpy as np
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import streamlit as st
from config import METRIC_STRUCTURE, SHEET_ID, SHEET_NAME
from data_preprocessing import preprocess_data

def get_all_metrics():
    """Récupère toutes les métriques depuis METRIC_STRUCTURE."""
    metrics = {}
    for category in METRIC_STRUCTURE.values():
        metrics.update(category['metrics'])
    return metrics

def load_google_sheet_data():
    """Charge les données depuis Google Sheets."""
    try:
        # Utilisation des secrets Streamlit pour les credentials en production
        if 'GOOGLE_APPLICATION_CREDENTIALS' in st.secrets:
            credentials_dict = st.secrets["GOOGLE_APPLICATION_CREDENTIALS"]
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets"]
            creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
        else:
            # En développement local, utilise le fichier JSON
            scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets"]
            creds = ServiceAccountCredentials.from_json_keyfile_name("src/nps-annette-k-d47ddcca9303.json", scope)

        client = gspread.authorize(creds)
        sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
        data = sheet.get_all_values()

        # Convertir en DataFrame
        df = pd.DataFrame(data[1:], columns=data[0])  # Première ligne comme noms de colonnes
        
        # Exclure la colonne Email si elle existe
        if 'Email' in df.columns:
            df = df.drop('Email', axis=1)

        # Appliquer le prétraitement
        df = preprocess_data(df)

        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {str(e)}")
        return pd.DataFrame()

def generate_test_data(n_months=12, responses_per_month=50):
    """Génère des données de test NPS synthétiques."""
    dates, scores, reabo_scores, names = ([] for _ in range(4))
    
    # Récupérer toutes les métriques
    all_metrics = {}
    for category in METRIC_STRUCTURE.values():
        all_metrics.update({k: [] for k in category['metrics'].keys()})
    
    start_date = datetime.now() - timedelta(days=n_months * 30)
    
    for _ in range(n_months * responses_per_month):
        date = start_date + timedelta(days=np.random.randint(0, n_months * 30))
        dates.append(date)
        
        score = np.random.choice(range(0, 11), p=[0.05]*6 + [0.1, 0.1, 0.15, 0.15, 0.2])
        scores.append(score)
        
        reabo_score = np.random.choice(range(0, 11), p=[0.05]*6 + [0.1, 0.1, 0.15, 0.15, 0.2])
        reabo_scores.append(reabo_score)

        # Remplissage des scores de satisfaction
        for metric in all_metrics.keys():
            all_metrics[metric].append(
                np.random.choice([np.nan, 1, 2, 3, 4, 5], p=[0.1, 0.1, 0.1, 0.2, 0.3, 0.2])
            )
        
        names.append(f"User_{_}")
    
    # Création du DataFrame
    df = pd.DataFrame({
        'Date': dates,
        'Recommandation': scores,
        'ProbabiliteReabo': reabo_scores,
        'Nom': names,
        **all_metrics
    })
    
    return df

if __name__ == "__main__":
    # Test des fonctions
    print("Test de génération de données :")
    df_test = generate_test_data(n_months=2, responses_per_month=10)
    print(df_test.head())
    
    print("\nTest de chargement des données réelles :")
    df_real = load_google_sheet_data()
    print(df_real.head() if not df_real.empty else "Pas de données réelles disponibles")