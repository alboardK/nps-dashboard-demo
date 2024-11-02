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
    """Génère des données de test."""
    print("\nGénération des données de test:")
    print(f"Paramètres: {n_months} mois, {responses_per_month} réponses par mois")
    
    dates = []
    scores = []
    satisfaction_scores = {k: [] for k in SATISFACTION_CRITERIA.keys()}
    names = []
    emails = []
    comments = []
    
    start_date = datetime.now() - timedelta(days=n_months*30)
    print("Date de début:", start_date)

    for i in range(n_months * responses_per_month):
        # Génération des données
        date = start_date + timedelta(days=np.random.randint(0, n_months*30))
        dates.append(date)
        
        score = np.random.choice(range(0, 11), 
                               p=[0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.1, 0.1, 0.15, 0.15, 0.2])
        scores.append(score)
        
        for criteria in SATISFACTION_CRITERIA.keys():
            satisfaction_scores[criteria].append(
                np.random.choice(range(1, 6), p=[0.05, 0.1, 0.2, 0.3, 0.35])
            )
        
        # Noms et emails
        first_name = np.random.choice(['Jean', 'Marie', 'Pierre', 'Sophie', 'Thomas', 'Julie'])
        last_name = np.random.choice(['Martin', 'Bernard', 'Dubois', 'Robert', 'Richard'])
        names.append(f"{last_name} {first_name}")
        emails.append(f"{first_name.lower()}.{last_name.lower()}@email.com")
        
        # Commentaires
        comment_types = {
            'Promoteur': ["Très satisfait", "Super ambiance", "Excellent rapport qualité/prix"],
            'Neutre': ["Service correct", "Quelques améliorations possibles", "Dans la moyenne"],
            'Détracteur': ["Vestiaires sales", "Trop de monde", "Équipements à moderniser"]
        }
        category = get_nps_category(score)
        comments.append(np.random.choice(comment_types[category]))
    
    # Création du DataFrame
    data = {
        'Horodateur': pd.to_datetime(dates),  # Conversion explicite en datetime
        'Recommandation': scores,
        'Nom': names,
        'Email': emails,
        'Commentaire': comments,
        **satisfaction_scores
    }
    
    df = pd.DataFrame(data)
    print("Shape of DataFrame:", df.shape)  # Debug pour vérifier que le DataFrame est créé
    print("Columns:", df.columns)  # Debug pour vérifier les colonnes
    print("Horodateur dtype:", df['Horodateur'].dtype)  # Debug pour vérifier le type de la colonne
    
    # Avant de retourner le DataFrame
    df = pd.DataFrame(data)
    print("\nDonnées générées:")
    print("Shape:", df.shape)
    print("Colonnes:", df.columns.tolist())
    print("Premières lignes:")
    print(df.head())
    
    return df

def display_satisfaction_metrics(df):
    """Affiche les métriques de satisfaction."""
    st.header("Métriques de satisfaction")
    
    current_month = df['Horodateur'].dt.strftime('%Y-%m').max()
    df_current = df[df['Horodateur'].dt.strftime('%Y-%m') == current_month]
    df_previous = df[df['Horodateur'].dt.strftime('%Y-%m') < current_month]
    
    for category, criteria_list in METRIC_CATEGORIES.items():
        st.subheader(category)
        cols = st.columns(len(criteria_list))
        
        for i, criteria in enumerate(criteria_list):
            current_avg = df_current[criteria].mean()
            previous_avg = df_previous[criteria].mean()
            
            cols[i].metric(
                SATISFACTION_CRITERIA[criteria],
                f"{current_avg:.1f}/5",
                f"{(current_avg - previous_avg):.1f}"
            )

def display_detailed_responses(df):
    """Affiche les réponses détaillées."""
    st.header("Réponses détaillées")
    
    # Structure des données
    col1, col2, col3 = st.columns([2,1,1])
    with col1:
        search_term = st.text_input("Rechercher par nom")
    with col2:
        categories = st.multiselect(
            "Filtrer par type",
            ["Promoteur", "Neutre", "Détracteur"],
            default=["Promoteur", "Neutre", "Détracteur"]
        )
    with col3:
        show_fields = st.multiselect(
            "Champs à afficher",
            list(SATISFACTION_CRITERIA.values()),
            default=[]
        )
    
    df['Catégorie'] = df['Recommandation'].apply(get_nps_category)
    
    mask = (
        df['Catégorie'].isin(categories) &
        (df['Nom'].str.contains(search_term, case=False) if search_term else True)
    )
    
    filtered_df = df[mask].sort_values('Horodateur', ascending=False)
    
    for _, row in filtered_df.head(5).iterrows():
        with st.expander(f"{row['Nom']} - {row['Horodateur'].strftime('%d/%m/%Y')} - Note: {row['Recommandation']}/10"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Email:** {row['Email']}")
                st.write(f"**Catégorie:** {row['Catégorie']}")
                if row['Commentaire']:
                    st.write(f"**Commentaire:** {row['Commentaire']}")
            
            with col2:
                if show_fields:
                    st.write("**Notes détaillées:**")
                    for field in show_fields:
                        key = [k for k, v in SATISFACTION_CRITERIA.items() if v == field][0]
                        if key in row:
                            st.write(f"{field}: {row[key]}/5")

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
