import streamlit as st
import pandas as pd
from datetime import datetime
import html

# Constants avec couleurs mises à jour
NPS_CATEGORIES = {
    "Promoteur": {"range": (9, 10), "color": "#24A158", "bg_color": "rgba(36, 161, 88, 0.1)"},
    "Neutre": {"range": (7, 8), "color": "#F1C40F", "bg_color": "rgba(241, 196, 15, 0.1)"},
    "Détracteur": {"range": (0, 6), "color": "#B03428", "bg_color": "rgba(176, 52, 40, 0.1)"}
}

def get_nps_category(score):
    """Détermine la catégorie NPS et retourne les informations associées."""
    try:
        score = float(score)
        for category, info in NPS_CATEGORIES.items():
            if info["range"][0] <= score <= info["range"][1]:
                return category, info["color"], info["bg_color"]
        return "Inconnu", "#95A5A6", "rgba(149, 165, 166, 0.1)"
    except (ValueError, TypeError):
        return "Inconnu", "#95A5A6", "rgba(149, 165, 166, 0.1)"

def format_satisfaction_metrics(row):
    """Formate les métriques de satisfaction."""
    metrics = []
    for col in row.index:
        if col.startswith('Satisfaction_') and pd.notna(row[col]):
            name = col.replace('Satisfaction_', '').replace('_', ' ').title()
            score = float(row[col])
            color = "#24A158" if score == 5 else "#FFFFFF" if score == 4 else "#B03428"
            metrics.append((name, score, color))
    return sorted(metrics, key=lambda x: x[0])

def calculate_stats(df):
    """Calcule les statistiques pour les données filtrées."""
    if df.empty:
        return 0, 0, 0
    
    total = len(df)
    promoters = (df['Recommandation'] >= 9).sum()
    detractors = (df['Recommandation'] <= 6).sum()
    nps_score = (promoters - detractors) / total * 100
    
    reabo_mean = pd.to_numeric(df['ProbabiliteReabo'], errors='coerce').mean()
    
    return round(nps_score), round(reabo_mean, 1) if pd.notna(reabo_mean) else 0, total

def apply_filters(df, periode, search, types_avis):
    """Applique les filtres aux données."""
    try:
        filtered_df = df.copy()
        
        # Filtre période
        now = pd.Timestamp.now()
        if periode == "10 derniers avis":
            filtered_df = filtered_df.sort_values('Date', ascending=False).head(10)
        else:
            date_filters = {
                "30 derniers jours": now - pd.Timedelta(days=30),
                "3 derniers mois": now - pd.Timedelta(days=90),
                "Cette année": pd.Timestamp(year=now.year, month=1, day=1),
                "Tout": filtered_df['Date'].min()
            }
            if periode in date_filters:
                filtered_df = filtered_df[filtered_df['Date'] >= date_filters[periode]]
        
        # Filtre recherche
        if search:
            search = search.lower()
            name_mask = (
                filtered_df['Nom'].str.lower().fillna('').str.contains(search, na=False) |
                filtered_df['Prenom'].str.lower().fillna('').str.contains(search, na=False)
            )
            filtered_df = filtered_df[name_mask]
        
        # Filtre types d'avis
        if types_avis:
            mask = pd.Series(False, index=filtered_df.index)
            for type_avis in types_avis:
                category_info = NPS_CATEGORIES[type_avis.replace("s", "")]
                min_score, max_score = category_info["range"]
                mask |= filtered_df['Recommandation'].between(min_score, max_score)
            filtered_df = filtered_df[mask]
        
        return filtered_df
    
    except Exception as e:
        st.error(f"Erreur lors du filtrage: {str(e)}")
        return pd.DataFrame()

def display_response_card(row, is_new):
    """Affiche une carte de réponse formatée."""
    try:
        score = float(row['Recommandation'])
        category, color, bg_color = get_nps_category(score)
        
        # Nettoyage et formatage sécurisé du nom
        prenom = str(row.get('Prenom', '')).strip()
        nom = str(row.get('Nom', '')).strip()
        full_name = f"{prenom} {nom}".strip()
        
        # Formatage de la date
        date_str = pd.to_datetime(row['Date']).strftime('%d/%m/%Y')
        new_badge = '⭐ ' if is_new else ''
        
        # Construction du composant avec Streamlit natif plutôt que HTML pur
        st.markdown(
            f'<div class="response-card" '
            f'style="background-color: {bg_color}; '
            f'border-left: 4px solid {color}; '
            f'padding: 12px; '
            f'border-radius: 4px; '
            f'margin-bottom: 8px;">'
            f'<div style="display: flex; justify-content: space-between; align-items: center;">'
            f'<div>'
            f'<span style="color: #888;">{date_str}</span>'
            f'{new_badge}'
            f'<span style="margin-left: 10px;">{html.escape(full_name)}</span>'
            f'</div>'
            f'<div>'
            f'<span style="color: {color};">{category}</span>'
            f'<span style="margin-left: 10px; font-weight: bold; color: {color};">{int(score)}/10</span>'
            f'</div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    except Exception as e:
        st.error(f"Erreur d'affichage de la carte: {str(e)}")

def display_response_details(row, color):
    """Affiche les détails d'une réponse."""
    with st.expander("Voir détails"):
        cols = st.columns([1, 1])
        
        # NPS Score
        with cols[0]:
            st.markdown(f"""
                <div class="metric-card">
                    <div style="color: #888;">Score NPS</div>
                    <div style="font-size: 1.2em; color: {color};">{int(row['Recommandation'])}/10</div>
                    <div style="font-style: italic; font-size: 0.9em; margin-top: 5px;">
                        {f'"{row["PourquoiNote"]}"' if pd.notna(row.get('PourquoiNote')) else 'Pas de commentaire'}
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        # Réabonnement
        with cols[1]:
            reabo_score = row.get('ProbabiliteReabo', 'N/A')
            if pd.notna(reabo_score):
                reabo_score = int(float(reabo_score))
            st.markdown(f"""
                <div class="metric-card">
                    <div style="color: #888;">Réabonnement</div>
                    <div style="font-size: 1.2em;">{reabo_score}/10</div>
                    <div style="font-style: italic; font-size: 0.9em; margin-top: 5px;">
                        {f'"{row["PourquoiReabo"]}"' if pd.notna(row.get('PourquoiReabo')) else 'Pas de commentaire'}
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        # Métriques de satisfaction
        if metrics := format_satisfaction_metrics(row):
            st.markdown("### Notes détaillées")
            metric_cols = st.columns(4)
            for i, (name, score, color) in enumerate(metrics):
                with metric_cols[i % 4]:
                    st.markdown(f"""
                        <div style="text-align: center;">
                            <div style="color: #888;">{name}</div>
                            <div style="font-size: 1.2em; color: {color};">{int(score)}/5</div>
                        </div>
                    """, unsafe_allow_html=True)
        
        # Améliorations suggérées
        if pd.notna(row.get('Ameliorations')):
            st.markdown("""
                <div class="metric-card">
                    <div style="color: #888;">Suggestions d'amélioration</div>
                    <div style="font-style: italic; color: white;">"{}"</div>
                </div>
            """.format(row['Ameliorations']), unsafe_allow_html=True)

def display_responses_details(df):
    """Fonction principale d'affichage des réponses."""
    st.header("Détails des réponses")
    
    # Configuration du style
    st.markdown("""
        <style>
        .metric-card {
            background-color: rgba(255,255,255,0.05);
            padding: 12px;
            border-radius: 4px;
            margin-bottom: 10px;
        }
        .response-card {
            margin-bottom: 8px;
            border-radius: 4px;
            overflow: hidden;
        }
        .name-display {
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 200px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Filtres
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        periode = st.selectbox(
            "Période",
            ["10 derniers avis", "30 derniers jours", "3 derniers mois", "Cette année", "Tout"],
            index=0
        )
    with col2:
        search = st.text_input("Rechercher par nom ou prénom").strip()
    with col3:
        types_avis = st.multiselect(
            "Types d'avis",
            ["Promoteurs", "Neutres", "Détracteurs"],
            default=["Promoteurs", "Neutres", "Détracteurs"]
        )
    
    try:
        # Application des filtres
        filtered_df = apply_filters(df, periode, search, types_avis)
        
        if filtered_df.empty:
            st.info("Aucune réponse ne correspond aux critères de recherche")
            return
        
        # Affichage des statistiques
        nps_score, reabo_mean, total = calculate_stats(filtered_df)
        cols = st.columns(3)
        cols[0].metric("Score NPS", f"{nps_score}%")
        cols[1].metric("Prob. réabonnement", f"{reabo_mean}")
        cols[2].metric("Nombre de réponses", total)
        
        st.markdown("---")
        
        # Affichage des réponses
        now = pd.Timestamp.now()
        for _, row in filtered_df.sort_values('Date', ascending=False).iterrows():
            is_new = (now - pd.to_datetime(row['Date'])).days < 4
            display_response_card(row, is_new)
            category, color, _ = get_nps_category(row['Recommandation'])
            display_response_details(row, color)
            
    except Exception as e:
        st.error(f"Une erreur s'est produite: {str(e)}")