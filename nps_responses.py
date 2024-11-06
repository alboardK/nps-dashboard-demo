import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go

def get_nps_category(score):
    """Détermine la catégorie NPS basée sur le score."""
    try:
        score = float(score)
        if score >= 9:
            return "Promoteur", "rgb(36, 161, 88)"  # Vert foncé
        elif score >= 7:
            return "Neutre", "rgb(241, 196, 15)"    # Jaune
        else:
            return "Détracteur", "rgb(176, 52, 40)"  # Rouge foncé
    except:
        return "Non défini", "rgb(128, 128, 128)"  # Gris par défaut

def calculate_nps(df):
    """Calcule le score NPS pour un ensemble de réponses."""
    if df.empty:
        return 0
    
    promoteurs = (df['Recommandation'] >= 9).sum()
    detracteurs = (df['Recommandation'] <= 6).sum()
    total = len(df)
    
    if total == 0:
        return 0
        
    return round(((promoteurs - detracteurs) / total) * 100)

def calculate_service_means(df):
    """Calcule les moyennes des services."""
    service_cols = [col for col in df.columns if "Notez de 1 à 5" in str(col)]
    means = {}
    for col in service_cols:
        service_name = col.replace("Notez de 1 à 5 avec 1 pour \"pas du tout satisfait\" et 5 pour \"Parfaitement satisfait\" votre satisfaction sur les services suivants : [", "").replace("]", "")
        means[service_name] = round(df[col].mean(), 1)
    return means

def display_search_results(filtered_df):
    """Affiche les résultats de la recherche de manière simple et cohérente avec le thème sombre."""
    nps_score = calculate_nps(filtered_df)
    service_means = calculate_service_means(filtered_df)
    
    # Calcul des distributions
    total = len(filtered_df)
    promoteurs = len(filtered_df[filtered_df['Recommandation'] >= 9])
    neutres = len(filtered_df[(filtered_df['Recommandation'] >= 7) & (filtered_df['Recommandation'] <= 8)])
    detracteurs = len(filtered_df[filtered_df['Recommandation'] <= 6])
    
    # Mise en page simplifiée en deux colonnes
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Métriques clés")
        st.markdown(f"""
            • **Réponses trouvées :** {total}  
            • **Score NPS :** {nps_score}%
        """)
    
    with col2:
        st.markdown("#### 📈 Distribution")
        st.markdown(f"""
            <span style='color: rgb(36, 161, 88)'>▉</span> Promoteurs : {promoteurs} ({int(promoteurs/total*100 if total else 0)}%)  
            <span style='color: rgb(241, 196, 15)'>▉</span> Neutres : {neutres} ({int(neutres/total*100 if total else 0)}%)  
            <span style='color: rgb(176, 52, 40)'>▉</span> Détracteurs : {detracteurs} ({int(detracteurs/total*100 if total else 0)}%)
        """, unsafe_allow_html=True)
    
    # Affichage simplifié des moyennes des services
    st.markdown("#### ⭐ Moyennes des services")
    service_cols = st.columns(5)  # 5 colonnes pour les services
    
    for idx, (service, score) in enumerate(service_means.items()):
        if not pd.isna(score):
            with service_cols[idx % 5]:
                st.markdown(f"""
                    <div style='background-color: rgb(45, 45, 45); padding: 8px; 
                         border-radius: 5px; text-align: center; margin: 2px;'>
                        <div style='font-size: 0.8em;'>{service}</div>
                        <div style='font-size: 1.2em; font-weight: bold;'>{score}/5</div>
                    </div>
                """, unsafe_allow_html=True)

def display_responses_details(df):
    """Affiche les détails des réponses avec filtres et expansion."""
    # Modification du style du titre pour le thème sombre
    st.markdown("""
        <style>
            h1, h2, h3, h4, h5, h6 {
                color: white !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.header("Recherche des réponses")
    
    # Section Filtres
    col1, col2, col3 = st.columns(3)
    
    with col1:
        date_range = st.date_input(
            "Période",
            value=(
                df['Date'].min().date(),
                df['Date'].max().date()
            ),
            max_value=datetime.now().date()
        )
    
    with col2:
        category_filter = st.selectbox(
            "Type de score",
            ["Tous", "Promoteurs", "Neutres", "Détracteurs"]
        )
    
    with col3:
        name_search = st.text_input("Rechercher un nom/prénom")

    # Application des filtres
    filtered_df = df.copy()
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[
            (filtered_df['Date'].dt.date >= start_date) &
            (filtered_df['Date'].dt.date <= end_date)
        ]
    
    if category_filter != "Tous":
        if category_filter == "Promoteurs":
            filtered_df = filtered_df[filtered_df['Recommandation'] >= 9]
        elif category_filter == "Neutres":
            filtered_df = filtered_df[
                (filtered_df['Recommandation'] >= 7) &
                (filtered_df['Recommandation'] <= 8)
            ]
        else:  # Détracteurs
            filtered_df = filtered_df[filtered_df['Recommandation'] <= 6]
    
    if name_search:
        name_search = name_search.lower()
        name_mask = (
            filtered_df['Nom'].str.lower().fillna('').str.contains(name_search) |
            filtered_df['prénom'].str.lower().fillna('').str.contains(name_search)
        )
        filtered_df = filtered_df[name_mask]

    # Affichage des résultats simplifiés
    display_search_results(filtered_df)
    st.markdown("---")  # Séparateur

    # Listing des réponses
    st.markdown("### Réponses")
    
    if filtered_df.empty:
        st.info("Aucune réponse ne correspond aux critères de recherche.")
        return

    # Tri par date décroissante
    filtered_df = filtered_df.sort_values('Date', ascending=False)

    for _, row in filtered_df.iterrows():
        category, color = get_nps_category(row.get('Recommandation', 0))
        
        # Construction du nom avec gestion des valeurs manquantes
        prenom = row.get('prénom', '')
        nom = row.get('Nom', '')
        date_str = row['Date'].strftime('%d/%m/%Y') if pd.notna(row.get('Date')) else ''
        
        # Création de la carte de réponse expandable
        with st.expander(f"{date_str} - {prenom} {nom} - {category}"):
            st.markdown(f"""
                <div style='background-color: {color}15; padding: 10px; border-radius: 5px;'>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                proba_reinscription = row.get('Sur une échelle de 1 à 10, \nQuelle est la probabilité que vous soyez toujours abonné chez Annette K. dans 6 mois ?', 'Non renseigné')
                st.markdown(f"""
                    **Score NPS:** {row.get('Recommandation', 'Non renseigné')}/10  
                    **Catégorie:** {category}  
                    **Probabilité de réinscription:** {proba_reinscription}/10
                """)
            
            with col2:
                commentaire = row.get('Pourquoi cette note ? ', '')
                if pd.notna(commentaire) and commentaire != '':
                    st.markdown("**Commentaire NPS:**")
                    st.write(commentaire)
            
            # Notes des services
            st.markdown("**Notes des services:**")
            service_cols = [col for col in df.columns if "Notez de 1 à 5" in str(col)]
            
            # Affichage en grille des notes de services
            cols = st.columns(3)
            for idx, service_col in enumerate(service_cols):
                with cols[idx % 3]:
                    service_name = service_col.replace("Notez de 1 à 5 avec 1 pour \"pas du tout satisfait\" et 5 pour \"Parfaitement satisfait\" votre satisfaction sur les services suivants : [", "").replace("]", "")
                    service_note = row.get(service_col, None)
                    if pd.notna(service_note):
                        st.markdown(f"""
                            <div style='background-color: rgb(45, 45, 45); padding: 8px; 
                                 border-radius: 5px; margin: 2px;'>
                                <div style='font-size: 0.8em;'>{service_name}</div>
                                <div style='font-size: 1.2em; font-weight: bold;'>{service_note}/5</div>
                            </div>
                        """, unsafe_allow_html=True)
            
            # Commentaires additionnels
            ameliorations = row.get('Si vous étiez manager chez Annette K, Quelles améliorations proposeriez vous ?', '')
            if pd.notna(ameliorations) and ameliorations != '':
                st.markdown("**Suggestions d'amélioration:**")
                st.write(ameliorations)
            
            st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    st.set_page_config(page_title="Test Responses", layout="wide")
    df = pd.DataFrame()  # À remplacer par vos données
    display_responses_details(df)