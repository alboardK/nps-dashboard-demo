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
def get_color_style(score, type="nps"):
    """Retourne le style CSS pour une note donnée."""
    if pd.isna(score):
        return "color: gray;"
        
    if type == "nps":
        if score >= 9:
            return "color: rgb(46, 204, 113);"  # Vert
        elif score >= 7:
            return "color: rgb(241, 196, 15);"  # Orange
        return "color: rgb(231, 76, 60);"  # Rouge
    else:  # notes sur 5
        if score >= 4:
            return "color: rgb(46, 204, 113);"
        elif score >= 3:
            return "color: rgb(241, 196, 15);"
        return "color: rgb(231, 76, 60);"
    
def generate_test_data(n_months=12, responses_per_month=50):
    """Génère des données de test avec des valeurs manquantes."""
    print("\nGénération des données de test:")
    
    dates = []
    scores = []
    reabo_scores = []  # Nouveau: scores de réabonnement
    satisfaction_scores = {k: [] for k in SATISFACTION_CRITERIA.keys()}
    names = []
    emails = []
    comments_nps = []  # Nouveau: commentaires NPS
    comments_reabo = []  # Nouveau: commentaires réabonnement
    
    start_date = datetime.now() - timedelta(days=n_months*30)

    for i in range(n_months * responses_per_month):
        # Génération des données de base
        date = start_date + timedelta(days=np.random.randint(0, n_months*30))
        dates.append(date)
        
        # Score NPS
        score = np.random.choice(range(0, 11), 
                               p=[0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.1, 0.1, 0.15, 0.15, 0.2])
        scores.append(score)
        
        # Commentaire NPS basé sur le score
        if score >= 9:
            comment_nps = np.random.choice([
                "Très satisfait des services, équipe au top",
                "Excellente salle, coachs professionnels",
                "Super ambiance et équipements de qualité",
                "Je recommande vivement, personnel attentif"
            ])
        elif score >= 7:
            comment_nps = np.random.choice([
                "Bonne salle dans l'ensemble",
                "Services corrects mais quelques points à améliorer",
                "Satisfait mais des ajustements seraient bienvenus",
                "Expérience positive avec quelques réserves"
            ])
        else:
            comment_nps = np.random.choice([
                "Vestiaires pas toujours propres",
                "Trop de monde aux heures de pointe",
                "Équipements à moderniser",
                "Personnel pas toujours disponible"
            ])
        comments_nps.append(comment_nps)
        
        # Score et commentaire de réabonnement
        reabo_score = np.random.choice(range(0, 11), 
                                     p=[0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.1, 0.1, 0.15, 0.15, 0.2])
        reabo_scores.append(reabo_score)
        
        if reabo_score >= 9:
            comment_reabo = np.random.choice([
                "Je compte rester fidèle",
                "Très satisfait, je continue l'aventure",
                "L'abonnement correspond parfaitement à mes besoins",
                "Je me sens bien dans cette salle"
            ])
        elif reabo_score >= 7:
            comment_reabo = np.random.choice([
                "Je verrai selon les évolutions",
                "En attente de voir les améliorations",
                "Je reste mais j'attends des changements",
                "Satisfait pour l'instant"
            ])
        else:
            comment_reabo = np.random.choice([
                "Je réfléchis à changer de salle",
                "Déménagement possible",
                "Je compare avec d'autres salles",
                "Pas sûr de continuer"
            ])
        comments_reabo.append(comment_reabo)
        
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
    
    # Création du DataFrame avec les nouveaux champs
    data = {
        'Horodateur': pd.to_datetime(dates),
        'Recommandation': scores,
        'Pourquoi cette note ?': comments_nps,
        'Reabonnement': reabo_scores,
        'Pourquoi cette réponse ?': comments_reabo,
        'Nom': names,
        'Email': emails,
        **satisfaction_scores
    }
    
    df = pd.DataFrame(data)
    
    # Debug prints
    print("\nDonnées générées:")
    print("Shape:", df.shape)
    print("Colonnes:", df.columns.tolist())
    print("Premières lignes:")
    print(df.head())
    
    return df

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
    """Affiche les réponses détaillées avec mise en page améliorée."""
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
    
    # Style CSS pour la mise en page
    st.markdown("""
        <style>
        .metric-box {
            background-color: rgba(0,0,0,0.05);
            border-radius: 5px;
            padding: 10px;
            margin: 5px 0;
        }
        .score-box {
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .comment-box {
            font-style: italic;
            font-size: 0.9em;
            margin-top: 5px;
        }
        .rating-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-top: 10px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Affichage des réponses
    for _, row in filtered_df.head(5).iterrows():
        nps_style = get_color_style(row['Recommandation'], "nps")
        reabo_style = get_color_style(row['Reabonnement'], "nps") if pd.notna(row.get('Reabonnement')) else "color: gray;"
        
        # En-tête de l'expander avec résumé
        header = f"""
            <div class="metric-box">
                <div style="font-weight: bold">{row['Nom']} - {row['Horodateur'].strftime('%d/%m/%Y')}</div>
                <div style="display: flex; justify-content: space-between; margin-top: 5px;">
                    <div>
                        <span style="{nps_style}">NPS: {int(row['Recommandation'])}/10</span>
                        <span style="margin-left: 10px; color: gray;">- {row['Catégorie']}</span>
                    </div>
                    <div style="{reabo_style}">
                        Réabo: {int(row['Reabonnement']) if pd.notna(row.get('Reabonnement')) else 'n/a'}/10
                    </div>
                </div>
            </div>
        """
        
        with st.expander(header, expanded=False):
            # Section Évaluation Globale
            st.markdown("### 🎯 Évaluation globale")
            cols = st.columns(2)
            
            # Colonne NPS
            with cols[0]:
                st.markdown(f"""
                    <div class="metric-box">
                        <div class="score-box">
                            Recommandation: <span style="{nps_style}">{int(row['Recommandation'])}/10</span>
                        </div>
                        <div class="comment-box">
                            {row['Pourquoi cette note ?']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            # Colonne Réabonnement
            with cols[1]:
                if pd.notna(row.get('Reabonnement')):
                    st.markdown(f"""
                        <div class="metric-box">
                            <div class="score-box">
                                Réabonnement: <span style="{reabo_style}">{int(row['Reabonnement'])}/10</span>
                            </div>
                            <div class="comment-box">
                                {row['Pourquoi cette réponse ?']}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                        <div class="metric-box">
                            <div class="score-box">
                                Réabonnement: <span style="color: gray;">n/a</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            
            # Section Notes Détaillées
            st.markdown("### 📈 Notes détaillées")
            
            # Affichage en grille des catégories
            cols = st.columns(2)
            categories_list = list(METRIC_CATEGORIES.items())
            
            for i, col in enumerate(cols):
                with col:
                    for j in range(i, len(categories_list), 2):
                        category, criteria_list = categories_list[j]
                        st.markdown(f"""
                            <div class="metric-box">
                                <div style="font-weight: bold; margin-bottom: 8px;">{category}</div>
                        """, unsafe_allow_html=True)
                        
                        for criteria in criteria_list:
                            value = row[criteria]
                            if pd.notna(value):
                                style = get_color_style(value, "satisfaction")
                                st.markdown(f"""
                                    <div style="display: flex; justify-content: space-between; margin: 2px 0;">
                                        <span>{SATISFACTION_CRITERIA[criteria]}</span>
                                        <span style="{style}">{value}/5</span>
                                    </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown(f"""
                                    <div style="display: flex; justify-content: space-between; margin: 2px 0;">
                                        <span>{SATISFACTION_CRITERIA[criteria]}</span>
                                        <span style="color: gray;">n/a</span>
                                    </div>
                                """, unsafe_allow_html=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)

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
