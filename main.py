"""Application principale NPS Dashboard."""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from nps_overview import display_nps_overview, get_nps_category
from config import SATISFACTION_CRITERIA, METRIC_CATEGORIES, DEFAULT_SETTINGS

# Configuration de la page - DOIT ÊTRE EN PREMIER
st.set_page_config(
    page_title="NPS Dashboard - Annette K",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def generate_test_data(n_months=12, responses_per_month=50):
    """Génère des données de test avec des valeurs manquantes."""
    print("\nGénération des données de test:")
    
    dates = []
    scores = []
    satisfaction_scores = {k: [] for k in SATISFACTION_CRITERIA.keys()}
    names = []
    emails = []
    comments = []
    
    start_date = datetime.now() - timedelta(days=n_months*30)

    for i in range(n_months * responses_per_month):
        # Génération des données de base
        date = start_date + timedelta(days=np.random.randint(0, n_months*30))
        dates.append(date)
        
        score = np.random.choice(range(0, 11), 
                               p=[0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.1, 0.1, 0.15, 0.15, 0.2])
        scores.append(score)
        
        # Pour chaque critère, 15% de chance d'avoir une valeur manquante
        for criteria in SATISFACTION_CRITERIA.keys():
            if np.random.random() < 0.15:  # 15% de chances d'avoir un NaN
                satisfaction_scores[criteria].append(np.nan)
            else:
                satisfaction_scores[criteria].append(
                    np.random.choice(range(1, 6), p=[0.05, 0.1, 0.2, 0.3, 0.35])
                )
        
        # Données utilisateur
        first_name = np.random.choice(['Jean', 'Marie', 'Pierre', 'Sophie', 'Thomas', 'Julie'])
        last_name = np.random.choice(['Martin', 'Bernard', 'Dubois', 'Robert', 'Richard'])
        names.append(f"{last_name} {first_name}")
        emails.append(f"{first_name.lower()}.{last_name.lower()}@email.com")
        comments.append(np.random.choice(["Très satisfait", "Service correct", "À améliorer"]))
    
    # Création du DataFrame
    data = {
        'Horodateur': pd.to_datetime(dates),
        'Recommandation': scores,
        'Nom': names,
        'Email': emails,
        'Commentaire': comments,
        **satisfaction_scores
    }
    
    return pd.DataFrame(data)

def display_satisfaction_metrics(df):
    """Affiche les métriques de satisfaction en ignorant les valeurs manquantes."""
    st.header("Métriques de satisfaction")
    
    # Calculer les périodes
    current_month = df['Horodateur'].dt.strftime('%Y-%m').max()
    df_current = df[df['Horodateur'].dt.strftime('%Y-%m') == current_month]
    df_previous = df[df['Horodateur'].dt.strftime('%Y-%m') < current_month]
    
    for category, criteria_list in METRIC_CATEGORIES.items():
        st.subheader(category)
        cols = st.columns(len(criteria_list))
        
        for i, criteria in enumerate(criteria_list):
            # Calcul des moyennes en ignorant les NaN
            current_valid = df_current[criteria].dropna()
            previous_valid = df_previous[criteria].dropna()
            
            current_avg = current_valid.mean() if len(current_valid) > 0 else None
            previous_avg = previous_valid.mean() if len(previous_valid) > 0 else None
            
            # Calcul du nombre de réponses valides
            nb_responses = len(current_valid)
            
            with cols[i]:
                metric_container = st.container()
                
                if current_avg is not None:
                    delta = None
                    if previous_avg is not None:
                        delta = current_avg - previous_avg
                    
                    metric_container.metric(
                        label=f"{SATISFACTION_CRITERIA[criteria]} ({nb_responses} réponses)",
                        value=f"{current_avg:.1f}/5",
                        delta=f"{delta:.1f}" if delta is not None else None
                    )
                else:
                    metric_container.warning(f"Pas de données pour {SATISFACTION_CRITERIA[criteria]}")

def calculate_category_average(row, criteria_list):
    """
    Calcule la moyenne d'une catégorie en ignorant les valeurs manquantes.
    """
    values = [row[criteria] for criteria in criteria_list if pd.notna(row[criteria])]
    if values:
        return sum(values) / len(values)
    return None

def display_detailed_responses(df):
    """Affiche les réponses détaillées avec aperçu des informations clés."""
    st.header("Réponses détaillées")
    
    # Filtres de base
    col1, col2 = st.columns([2,1])
    with col1:
        search_term = st.text_input("Rechercher par nom")
    with col2:
        categories = st.multiselect(
            "Filtrer par type",
            ["Promoteur", "Neutre", "Détracteur"],
            default=["Promoteur", "Neutre", "Détracteur"]
        )
    
    df['Catégorie'] = df['Recommandation'].apply(get_nps_category)
    
    # Application des filtres
    mask = (
        df['Catégorie'].isin(categories) &
        (df['Nom'].str.contains(search_term, case=False) if search_term else True)
    )
    
    filtered_df = df[mask].sort_values('Horodateur', ascending=False)
    
    # Affichage des réponses détaillées
    for _, row in filtered_df.head(5).iterrows():
        # Création de l'aperçu avec les informations clés
        reabo_value = f"{int(row['Reabonnement'])}/10" if pd.notna(row.get('Reabonnement')) else "n/a"
        header = (
            f"{row['Nom']} - {row['Horodateur'].strftime('%d/%m/%Y')}\n"
            f"NPS: {int(row['Recommandation'])}/10 | Réabonnement: {reabo_value} | "
            f"Catégorie: {row['Catégorie']}"
        )
        
        with st.expander(header):
            # [Reste du code précédent pour l'affichage détaillé...]
            # Bloc 1 : Scores principaux
            st.markdown("### 🎯 Scores principaux")
            cols = st.columns(2)
            with cols[0]:
                score_color = "green" if row['Recommandation'] >= 9 else "orange" if row['Recommandation'] >= 7 else "red"
                st.markdown(f"**Recommandation :** ::{score_color}[{int(row['Recommandation'])}/10]")
            with cols[1]:
                if pd.notna(row.get('Reabonnement')):
                    reabo_color = "green" if row['Reabonnement'] >= 8 else "orange" if row['Reabonnement'] >= 6 else "red"
                    st.markdown(f"**Probabilité de réabonnement :** ::{reabo_color}[{int(row['Reabonnement'])}/10]")
                else:
                    st.markdown("**Probabilité de réabonnement :** *n/a*")
            
            # Bloc 2 : Commentaire
            if pd.notna(row['Commentaire']):
                st.markdown("### 💭 Commentaire")
                st.info(row['Commentaire'])
            
            # Bloc 3 : Notes détaillées par catégorie
            st.markdown("### 📈 Évaluation détaillée")
            
            for category, criteria_list in METRIC_CATEGORIES.items():
                category_avg = calculate_category_average(row, criteria_list)
                
                if category_avg is not None:
                    st.markdown(f"#### ▶ {category} (moyenne: {category_avg:.1f}/5)")
                else:
                    st.markdown(f"#### ▶ {category} (pas de données)")
                
                data = []
                for criteria in criteria_list:
                    if pd.notna(row[criteria]):
                        value = f"{row[criteria]}/5"
                        color = "green" if row[criteria] >= 4 else "orange" if row[criteria] >= 3 else "red"
                    else:
                        value = "n/a"
                        color = "grey"
                    
                    data.append({
                        "Critère": SATISFACTION_CRITERIA[criteria],
                        "Note": value,
                        "Couleur": color
                    })
                
                for item in data:
                    cols = st.columns([3, 1])
                    with cols[0]:
                        st.write(f"• {item['Critère']}")
                    with cols[1]:
                        if item['Note'] != "n/a":
                            st.markdown(f"::{item['Couleur']}[{item['Note']}]")
                        else:
                            st.markdown(f"*{item['Note']}*")
                
                st.markdown("---")

def main():
    """Fonction principale de l'application."""
    # Configuration sidebar
    with st.sidebar:
        st.markdown("""
            <style>
            [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
                width: 250px;
            }
            </style>
            """, unsafe_allow_html=True)
        st.title("⚙️ Configuration")
        theme = st.selectbox("Thème", ["Clair", "Sombre"], key="theme")
        seuil_representativite = st.number_input(
            "Seuil de représentativité",
            min_value=1,
            value=DEFAULT_SETTINGS['seuil_representativite']
        )
    
    # Génération des données de test
    df = generate_test_data()
    
    # Debug prints
    print("DataFrame généré:")
    print("Shape:", df.shape)
    print("Colonnes:", df.columns.tolist())
    print("Premières lignes:")
    print(df.head())
    
    # Interface principale
    tab1, tab2, tab3 = st.tabs([
        "📈 NPS Overview",
        "⭐ Satisfaction",
        "📝 Réponses détaillées"
    ])
    
    # Ajout de ces lignes pour passer les données aux tabs
    with tab1:
        display_nps_overview(df, seuil_representativite)
    with tab2:
        display_satisfaction_metrics(df)
    with tab3:
        display_detailed_responses(df)

if __name__ == "__main__":
    main()
