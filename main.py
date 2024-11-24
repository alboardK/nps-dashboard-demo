import streamlit as st
from data_loader import load_google_sheet_data, generate_test_data
from data_preprocessing import preprocess_data
from nps_overview import display_nps_overview
from nps_metrics import display_metrics_details
from nps_responses import display_responses_details
from config import DEFAULT_SETTINGS
import pandas as pd
from datetime import datetime
from auth import Authenticator

# Configuration globale
ENABLE_AUTH = True  # Mettre à True pour activer l'authentification

def display_config_tab(data_source):
    """Affiche l'onglet de configuration."""
    st.header("Configuration")
    
    if ENABLE_AUTH and st.session_state.get('user_role') != "admin":
        st.warning("Accès réservé aux administrateurs")
        return data_source
    
    col1, col2 = st.columns([3, 1])
    
    with col1:    
        st.subheader("Source des données")
        new_data_source = st.selectbox(
            "Source des données",
            ["Données réelles", "Données de test"],
            index=0 if data_source == "Données réelles" else 1
        )
    
    with col2:
        st.markdown("### ")  # Pour aligner avec le selectbox
        if st.button("🚪 Déconnexion", type="secondary"):
            st.session_state.authenticated = False
            st.rerun()
    
    # Informations sur l'utilisateur connecté
    st.markdown("---")
    st.markdown(f"**Utilisateur connecté :** {st.session_state.get('user', 'Non connecté')}")
    st.markdown(f"**Rôle :** {st.session_state.get('user_role', 'Non défini')}")
    
    return new_data_source

def preprocess_dataframe(df):
    """Prétraite le DataFrame pour assurer la cohérence des types de données."""
    if df.empty:
        return df
        
    # Conversion des dates
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
    
    # Création/vérification de la colonne Catégorie si elle n'existe pas
    if 'Recommandation' in df.columns and 'Catégorie' not in df.columns:
        df['Catégorie'] = df['Recommandation'].apply(lambda x: 
            'Promoteur' if x >= 9 else ('Passif' if x >= 7 else 'Détracteur'))
    
    # Conversion des colonnes numériques
    numeric_columns = [
        'Recommandation',
        'ProbabiliteReabo',
        'Satisfaction_Salle',
        'Satisfaction_Piscine',
        'Satisfaction_Coaching',
        'Satisfaction_DispoCours',
        'Satisfaction_DispoEquipements',
        'Satisfaction_Coachs',
        'Satisfaction_MNS',
        'Satisfaction_Accueil',
        'Satisfaction_Conseiller',
        'Satisfaction_Ambiance',
        'Satisfaction_Proprete',
        'Satisfaction_Vestiaires',
        'Satisfaction_Restauration',
        'Satisfaction_Festive',
        'Satisfaction_Masterclass'
    ]
    
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Nettoyage des colonnes textuelles
    text_columns = ['Nom', 'Prenom', 'Email', 'PourquoiNote', 'PourquoiReabo', 'Ameliorations', 'Catégorie']
    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).replace('nan', '').str.strip()
    
    return df

def configure_page():
    """Configure la page Streamlit."""
    st.set_page_config(
        page_title="NPS Dashboard - Annette K",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Application du thème sombre
    st.markdown("""
        <style>
            /* Base theme */
            .stApp {
                background-color: #1E1E1E;
                color: white;
            }
            
            /* Headers */
            h1, h2, h3, h4, h5, h6 {
                color: white !important;
            }
            
            /* Login form styling */
            .stButton button {
                width: 100%;
                background-color: #2D2D2D;
                border: 1px solid #444;
                color: white;
            }
            .stTextInput input {
                background-color: #2D2D2D;
                color: white;
                border: 1px solid #444;
            }
            .stTextInput input:focus {
                border-color: #666;
                box-shadow: 0 0 0 1px #666;
            }
            
            /* Widgets */
            .stSelectbox, .stMultiSelect {
                background-color: #2D2D2D;
            }
            
            /* Metrics containers */
            .metric-container div {
                background-color: #2D2D2D !important;
            }
            
            /* Remove padding */
            .block-container {
                padding-top: 2rem;
                padding-bottom: 0rem;
            }
            
            /* Custom scrollbar */
            ::-webkit-scrollbar {
                width: 10px;
                height: 10px;
            }
            
            ::-webkit-scrollbar-track {
                background: #1E1E1E;
            }
            
            ::-webkit-scrollbar-thumb {
                background: #888;
                border-radius: 5px;
            }
            
            ::-webkit-scrollbar-thumb:hover {
                background: #555;
            }
            
            /* Cacher le menu hamburger et le footer */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            .stDeployButton {display:none;}
            
            /* Login container */
            [data-testid="stForm"] {
                background-color: #2D2D2D;
                padding: 1rem;
                border-radius: 4px;
            }
        </style>
    """, unsafe_allow_html=True)

def load_data(use_test_data=True):
    """Charge et prétraite les données."""
    try:
        if use_test_data:
            df = generate_test_data()
        else:
            df = load_google_sheet_data()
        
        # Prétraitement des données
        df = preprocess_dataframe(df)
        return df
        
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {str(e)}")
        return pd.DataFrame()

def main():
    """Fonction principale de l'application."""
    configure_page()
    
    # Vérification de sécurité
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    # Gestion de l'authentification
    if ENABLE_AUTH:
        authenticator = Authenticator()
        if not authenticator.login():
            return
    else:
        # En mode développement, définir des valeurs par défaut
        if not st.session_state.authenticated:
            st.session_state.authenticated = True
            st.session_state.user = "dev@annettek.fr"
            st.session_state.user_role = "admin"
    
    # État initial de la source de données
    if 'data_source' not in st.session_state:
        st.session_state.data_source = "Données réelles"
    
    # Création des onglets
    tab1, tab2, tab3, tab4 = st.tabs([
        "Vue d'ensemble NPS",
        "Détails des métriques",
        "Détails des réponses",
        "Configuration"
    ])
    
    # Chargement des données
    df = load_data(use_test_data=(st.session_state.data_source == "Données de test"))
    
    if df.empty:
        st.warning("Aucune donnée n'est disponible.")
        return
    
    with tab1:
        display_nps_overview(df)
    
    with tab2:
        display_metrics_details(df)
    
    with tab3:
        display_responses_details(df)
    
    with tab4:
        new_data_source = display_config_tab(st.session_state.data_source)
        if new_data_source != st.session_state.data_source:
            st.session_state.data_source = new_data_source
            st.rerun()

if __name__ == "__main__":
    main()