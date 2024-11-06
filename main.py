import streamlit as st
from data_loader import load_google_sheet_data, generate_test_data
from data_preprocessing import preprocess_data
from nps_overview import display_nps_overview
from nps_metrics import display_metrics_details
from nps_responses import display_responses_details
from config import DEFAULT_SETTINGS

# Configuration de la page
st.set_page_config(
    page_title="NPS Dashboard - Annette K",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"  # Changé de "expanded" à "collapsed"
)

def configure_sidebar():
    """Configure la barre latérale avec les options de configuration de l'application et applique le thème immédiatement."""
    with st.sidebar:
        st.title("⚙️ Configuration")
        data_source = st.selectbox("Source des données", ["Données réelles", "Données de test"], key="data_source")
        show_raw_data = st.checkbox("Afficher les données brutes")
        seuil_representativite = st.number_input(
            "Seuil de représentativité",
            min_value=1,
            value=DEFAULT_SETTINGS['seuil_representativite']
        )
        
        # Choix du thème avec application immédiate du CSS
        theme = st.radio("Choisir un thème", options=["Clair", "Sombre"], index=1)  # index=1 pour Sombre par défaut
        
        # Application des styles CSS globaux selon le thème
        if theme == "Sombre":
            st.markdown("""
                <style>
                    /* Styles globaux */
                    .stApp {
                        background-color: #1E1E1E;
                        color: white;
                    }
                    
                    /* En-têtes */
                    .css-10trblm {
                        color: white;
                    }
                    
                    /* Conteneurs */
                    .css-1r6slb0, .css-12oz5g7 {
                        background-color: #2D2D2D;
                        color: white;
                    }
                    
                    /* Graphiques */
                    .js-plotly-plot .plotly {
                        background-color: #2D2D2D !important;
                    }
                    
                    /* Tableaux */
                    .dataframe {
                        background-color: #2D2D2D;
                        color: white;
                    }
                    
                    /* Widgets */
                    .stSelectbox, .stNumberInput {
                        background-color: #2D2D2D;
                        color: white;
                    }
                    
                    /* Onglets */
                    .stTabs [data-baseweb="tab-list"] {
                        background-color: #2D2D2D;
                    }
                    
                    .stTabs [data-baseweb="tab"] {
                        color: white;
                    }
                    
                    /* Cartes et conteneurs */
                    .nps-container {
                        background-color: #2D2D2D !important;
                    }
                </style>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <style>
                    /* Styles globaux */
                    .stApp {
                        background-color: #FFFFFF;
                        color: black;
                    }
                    
                    /* En-têtes */
                    .css-10trblm {
                        color: black;
                    }
                    
                    /* Conteneurs */
                    .css-1r6slb0, .css-12oz5g7 {
                        background-color: #F0F2F6;
                    }
                    
                    /* Graphiques */
                    .js-plotly-plot .plotly {
                        background-color: #FFFFFF !important;
                    }
                    
                    /* Tableaux */
                    .dataframe {
                        background-color: #FFFFFF;
                        color: black;
                    }
                    
                    /* Widgets */
                    .stSelectbox, .stNumberInput {
                        background-color: #FFFFFF;
                    }
                    
                    /* Onglets */
                    .stTabs [data-baseweb="tab-list"] {
                        background-color: #F0F2F6;
                    }
                    
                    .stTabs [data-baseweb="tab"] {
                        color: black;
                    }
                    
                    /* Cartes et conteneurs */
                    .nps-container {
                        background-color: #F0F2F6 !important;
                    }
                </style>
            """, unsafe_allow_html=True)
        
    return data_source, show_raw_data, seuil_representativite

def main():
    """Fonction principale de l'application."""
    data_source, show_raw_data, seuil_representativite = configure_sidebar()
    
    # Charger les données en fonction de la source sélectionnée
    if data_source == "Données réelles":
        df = load_google_sheet_data()
    else:
        df = generate_test_data()

    # Appliquer le prétraitement des données
    df = preprocess_data(df)

    # Afficher les données brutes dans la barre latérale si l'option est activée
    if show_raw_data:
        st.sidebar.subheader("Données brutes")
        st.sidebar.dataframe(df)

    # Créer les onglets
    tabs = st.tabs(["Vue d'ensemble NPS", "Détails des métriques", "Détails des réponses"])

    with tabs[0]:
        display_nps_overview(df, seuil_representativite)

    with tabs[1]:
        display_metrics_details(df)

    with tabs[2]:
        display_responses_details(df)

if __name__ == "__main__":
    main()
