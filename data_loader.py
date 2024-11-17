# Notre but ici : fournir des données.
# les données peuvent etre de nature réelles ou inventée voilà pourquoi il y a deux fonctions : 
# l'une a pour but de récuperer les données réelles et l'autre a pour but d'inventer des données.
# les données réelles devront etre transformées avant d'etre utilisées. 
# Une fonction preprocess existe dans le code pour ça.

import gspread
import pandas as pd
import numpy as np
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
from config import METRIC_STRUCTURE
from data_preprocessing import preprocess_data  # Importe le prétraitement

# Paramètres de la feuille Google Sheets
SHEET_ID = "1i8TU3c72YH-5sfAKcxmeuthgSeHcW3-ycg7cwzOtkrE"
SHEET_NAME = "Réponses"
JSON_CREDENTIALS_PATH = "src/nps-annette-k-d47ddcca9303.json"

def get_all_metrics():
    """Récupère toutes les métriques depuis METRIC_STRUCTURE."""
    metrics = {}
    for category in METRIC_STRUCTURE.values():
        metrics.update(category['metrics'])
    return metrics

def load_google_sheet_data():
    # Authentification et chargement des données depuis Google Sheets
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_CREDENTIALS_PATH, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
    data = sheet.get_all_values()

    # Convertir en DataFrame
    df = pd.DataFrame(data[1:], columns=data[0])  # Première ligne comme noms de colonnes

    # Appliquer le prétraitement
    df = preprocess_data(df)

    return df

def generate_test_data(n_months=12, responses_per_month=50):
    """
    Génère des données de test NPS synthétiques.
    """
    dates, scores, reabo_scores, names, emails, comments_nps, comments_reabo = ([] for _ in range(7))
    
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
        comments_nps.append(np.random.choice(["Très bien", "Satisfaisant", "Peut mieux faire", "À améliorer"]))
        
        reabo_score = np.random.choice(range(0, 11), p=[0.05]*6 + [0.1, 0.1, 0.15, 0.15, 0.2])
        reabo_scores.append(reabo_score)
        comments_reabo.append(np.random.choice(["Je compte rester", "Peut-être", "Je vais changer"]))

        # Remplissage des scores de satisfaction avec probabilités ajustées
        for metric in all_metrics.keys():
            all_metrics[metric].append(
                np.random.choice([np.nan, 1, 2, 3, 4, 5], p=[0.1, 0.1, 0.1, 0.2, 0.3, 0.2])
            )
        
        first_name, last_name = np.random.choice(['Jean', 'Marie']), np.random.choice(['Martin', 'Dubois'])
        names.append(f"{last_name} {first_name}")
        emails.append(f"{first_name.lower()}.{last_name.lower()}@email.com")
    
    # Création du DataFrame
    df = pd.DataFrame({
        'Date': dates,
        'Recommandation': scores,
        'Pourquoi cette note ?': comments_nps,
        'Reabonnement': reabo_scores,
        'Pourquoi cette réponse ?': comments_reabo,
        'Nom': names,
        'Email': emails,
        **all_metrics
    })
    
    print("Aperçu des données de test :")
    print(df.head())
    
    return df

# Test pour vérifier l'importation des données
if __name__ == "__main__":
    # Charger les données depuis Google Sheets sans passer de paramètres
    df_google = load_google_sheet_data()
    print("\nDonnées importées depuis Google Sheets :")
    print(df_google.head())
    
    # Générer des données de test
    df_test = generate_test_data()
    print("\nDonnées de test générées :")
    print(df_test.head())