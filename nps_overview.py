import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

# Couleurs pour les catégories de NPS
COLORS = {
    "Promoteur": "rgb(46, 204, 113)",
    "Passif": "rgb(241, 196, 15)",
    "Détracteur": "rgb(231, 76, 60)"
}

def debug_dataframe(df, location):
    """Fonction de débogage pour afficher les informations importantes du DataFrame."""
    st.sidebar.markdown(f"### Debug info - {location}")
    if 'Catégorie' in df.columns:
        st.sidebar.write("Catégories uniques:", df['Catégorie'].unique())
    if 'Recommandation' in df.columns:
        st.sidebar.write("Plage de recommandations:", df['Recommandation'].min(), "à", df['Recommandation'].max())

def standardize_categories(df):
    """Standardise les catégories dans le DataFrame."""
    if 'Recommandation' not in df.columns:
        return df
        
    category_mapping = {
        'Promoter': 'Promoteur',
        'Passive': 'Passif',
        'Detractor': 'Détracteur',
        'Promoteurs': 'Promoteur',
        'Passifs': 'Passif',
        'Détracteurs': 'Détracteur'
    }
    
    # Si la colonne Catégorie n'existe pas, la créer
    if 'Catégorie' not in df.columns:
        df['Catégorie'] = df['Recommandation'].apply(get_nps_category)
    
    # Standardiser les catégories existantes
    df['Catégorie'] = df['Catégorie'].replace(category_mapping)
    
    return df

def get_nps_category(score):
    """Détermine la catégorie NPS basée sur le score."""
    try:
        score = float(score)
        if score >= 9:
            return "Promoteur"
        elif score >= 7:
            return "Passif"
        else:
            return "Détracteur"
    except (ValueError, TypeError):
        return "Inconnu"

def calculate_nps(data, target_month):
    """Calcule le NPS pour un mois spécifique."""
    # Convertir target_month en Period s'il ne l'est pas déjà
    if not isinstance(target_month, pd.Period):
        target_month = pd.Period(target_month, freq='M')
    
    # Filtre les données pour le mois ciblé
    month_data = data[data['Date'].dt.to_period('M') == target_month]
    
    if month_data.empty:
        return None

    promoteurs = month_data[month_data['Recommandation'] >= 9]
    detracteurs = month_data[month_data['Recommandation'] <= 6]
    
    if len(month_data) == 0:
        return None
        
    nps_score = ((len(promoteurs) - len(detracteurs)) / len(month_data)) * 100
    return nps_score

def display_nps_overview(df, seuil=35):
    """Affiche la vue d'ensemble du NPS."""
    st.header("Vue d'ensemble NPS")
    
    if df.empty:
        st.error("Aucune donnée disponible")
        return

    # Standardisation des catégories
    df = standardize_categories(df)
    
    # Debug info
    debug_dataframe(df, "After standardization")

    # Calculs des périodes
    valid_months = df.dropna(subset=['Recommandation']).groupby(df['Date'].dt.to_period("M")).size().index
    current_month = valid_months.max()  # Déjà un Period
    previous_month = current_month - 1  # Period arithmetic

    # Calculs NPS
    current_nps = calculate_nps(df, current_month)
    previous_nps = calculate_nps(df, previous_month)
    
    delta = current_nps - previous_nps if all(x is not None for x in [current_nps, previous_nps]) else None
    delta_symbol = "↑" if delta and delta > 0 else "↓"
    delta_color = "#2ecc71" if delta and delta > 0 else "#e74c3c"

    # Affichage NPS
    st.markdown(f"""
        <style>
            .nps-container {{
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 20px;
                border-radius: 10px;
                background-color: #333;
                color: white;
                margin-bottom: 20px;
                text-align: center;
            }}
            .nps-title {{ font-size: 1.5em; font-weight: bold; color: #ecf0f1; }}
            .nps-value {{ font-size: 3em; font-weight: bold; color: #2ecc71; margin: 10px 0; }}
            .nps-change {{ font-size: 1.2em; color: {delta_color}; }}
            .nps-subtitle {{ font-size: 1em; color: #bdc3c7; }}
        </style>

        <div class="nps-container">
            <div class="nps-title">NPS ce mois-ci</div>
            <div class="nps-value">{f"{int(current_nps)}%" if current_nps is not None else "Non disponible"}</div>
            <div class="nps-change">{f"{delta_symbol} {abs(int(delta))}%" if delta is not None else "Pas de données précédentes"}</div>
        </div>
    """, unsafe_allow_html=True)

    # Préparation des données pour le graphique
    monthly_distribution = df[df['Date'].dt.to_period("M").isin(valid_months)].groupby(
        [df['Date'].dt.to_period("M"), 'Catégorie']
    ).size().unstack(fill_value=0)
    
    # Debug info
    st.sidebar.write("Colonnes dans monthly_distribution:", monthly_distribution.columns.tolist())

    # Création du graphique
    fig = go.Figure()

    # Ajout des barres pour chaque catégorie
    for category in ['Détracteur', 'Passif', 'Promoteur']:
        if category in monthly_distribution.columns:
            fig.add_trace(go.Bar(
                name=category,
                x=monthly_distribution.index.astype(str),  # Conversion en string pour l'affichage
                y=monthly_distribution[category],
                marker_color=COLORS[category],
                hovertemplate=f"Mois: %{{x}}<br>{category}s: %{{y}}<br><extra></extra>"
            ))

    # Calcul et ajout de la ligne NPS
    monthly_nps = pd.DataFrame({
        'Mois': valid_months,
        'NPS': [calculate_nps(df, month) for month in valid_months]
    })

    fig.add_trace(go.Scatter(
        x=monthly_nps['Mois'].astype(str),  # Conversion en string pour l'affichage
        y=monthly_nps['NPS'],
        mode='lines+text',
        name='NPS',
        line=dict(color='white', width=2),
        text=[f"{int(x)}%" if pd.notna(x) else "N/A" for x in monthly_nps['NPS']],
        textposition='top center',
        textfont=dict(size=14, color='white'),
        hovertemplate="NPS: %{text}<br><extra></extra>"
    ))

    # Mise à jour du layout
    fig.update_layout(
        barmode='stack',
        title="Évolution mensuelle des réponses",
        showlegend=True,
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
    )

    st.plotly_chart(fig, use_container_width=True)

    # Affichage des détails mensuels
    st.markdown("### Détail mensuel")
    monthly_counts = df.groupby(df['Date'].dt.to_period("M")).size()
    
    for month in monthly_distribution.index:
        count = monthly_counts[month]
        if count < seuil:
            st.warning(f"{month}: {count} réponses (sous le seuil de représentativité)")
        else:
            st.success(f"{month}: {count} réponses")



if __name__ == "__main__":
    # Code de test
    import numpy as np
    
    dates = pd.date_range(start='2023-01-01', end='2024-02-29', freq='D')
    test_df = pd.DataFrame({
        'Date': dates,
        'Recommandation': np.random.choice(range(0, 11), size=len(dates))
    })
    display_nps_overview(test_df)