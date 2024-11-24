import gspread
import pandas as pd
import numpy as np
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import streamlit as st
from config import METRIC_STRUCTURE
from data_preprocessing import preprocess_data

def get_google_credentials():
    """Récupère les credentials Google de manière sécurisée avec gestion des erreurs."""
    try:
        # Vérification de l'existence des secrets nécessaires
        if "GOOGLE_APPLICATION_CREDENTIALS" not in st.secrets:
            raise KeyError("Configuration Google non trouvée dans les secrets")
        
        credentials_dict = st.secrets.get("GOOGLE_APPLICATION_CREDENTIALS", {})
        required_keys = [
            "type", "project_id", "private_key_id", "private_key",
            "client_email", "client_id", "auth_uri", "token_uri"
        ]
        
        # Vérification des clés requises
        missing_keys = [key for key in required_keys if key not in credentials_dict]
        if missing_keys:
            raise KeyError(f"Clés manquantes dans la configuration Google: {', '.join(missing_keys)}")
            
        return credentials_dict
    except Exception as e:
        st.error(f"Erreur lors de la récupération des credentials: {str(e)}")
        return None

def load_google_sheet_data():
    """Charge les données depuis Google Sheets avec meilleure gestion des erreurs."""
    try:
        # Récupération des credentials
        credentials_dict = get_google_credentials()
        if not credentials_dict:
            return pd.DataFrame()
        
        # Récupération des configurations Google Sheets
        sheets_config = st.secrets.get("google_sheets", {})
        sheet_id = sheets_config.get("sheet_id")
        sheet_name = sheets_config.get("sheet_name")
        
        if not all([sheet_id, sheet_name]):
            raise KeyError("Configuration Google Sheets incomplète")
        
        # Configuration de l'authentification
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
        client = gspread.authorize(creds)
        
        # Accès et lecture du sheet
        sheet = client.open_by_key(sheet_id).worksheet(sheet_name)
        data = sheet.get_all_values()
        
        if not data:
            st.warning("Aucune donnée trouvée dans le Google Sheet")
            return pd.DataFrame()
            
        # Conversion en DataFrame
        df = pd.DataFrame(data[1:], columns=data[0])
        
        # Suppression de la colonne email pour la confidentialité
        if 'Email' in df.columns:
            df = df.drop('Email', axis=1)
            
        # Prétraitement des données
        df = preprocess_data(df)
        return df
        
    except gspread.exceptions.APIError as e:
        st.error(f"Erreur API Google Sheets: {str(e)}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {str(e)}")
        return pd.DataFrame()

def generate_test_data(n_months=12, responses_per_month=50):
    """Génère des données de test NPS synthétiques."""
    try:
        dates, scores, reabo_scores, names, categories = ([] for _ in range(5))
        
        # Récupération des métriques depuis la configuration
        all_metrics = {}
        for category in METRIC_STRUCTURE.values():
            all_metrics.update({k: [] for k in category['metrics'].keys()})
        
        start_date = datetime.now() - timedelta(days=n_months * 30)
        
        # Catégories possibles pour le NPS
        nps_categories = ['Détracteur', 'Passif', 'Promoteur']
        
        for i in range(n_months * responses_per_month):
            # Génération date
            dates.append(start_date + timedelta(days=np.random.randint(0, n_months * 30)))
            
            # Génération score NPS
            score = np.random.choice(range(0, 11), p=[0.05]*6 + [0.1, 0.1, 0.15, 0.15, 0.2])
            scores.append(score)
            
            # Détermination de la catégorie basée sur le score
            if score <= 6:
                category = 'Détracteur'
            elif score <= 8:
                category = 'Passif'
            else:
                category = 'Promoteur'
            categories.append(category)
            
            # Autres données
            reabo_scores.append(np.random.choice(range(0, 11), p=[0.05]*6 + [0.1, 0.1, 0.15, 0.15, 0.2]))
            
            for metric in all_metrics.keys():
                all_metrics[metric].append(
                    np.random.choice([np.nan, 1, 2, 3, 4, 5], p=[0.1, 0.1, 0.1, 0.2, 0.3, 0.2])
                )
            
            names.append(f"User_{i}")
        
        test_data = pd.DataFrame({
            'Date': dates,
            'Recommandation': scores,
            'Catégorie': categories,  # Ajout de la colonne Catégorie
            'ProbabiliteReabo': reabo_scores,
            'Nom': names,
            **all_metrics
        })
        
        return test_data
        
    except Exception as e:
        st.error(f"Erreur lors de la génération des données de test: {str(e)}")
        return pd.DataFrame()

if __name__ == "__main__":
    st.write("Test de génération de données :")
    df_test = generate_test_data(n_months=2, responses_per_month=10)
    if not df_test.empty:
        st.write(df_test.head())
    
    st.write("\nTest de chargement des données réelles :")
    df_real = load_google_sheet_data()
    if not df_real.empty:
        st.write(df_real.head())
    else:
        st.write("Pas de données réelles disponibles")