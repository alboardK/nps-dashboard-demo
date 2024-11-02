"""Composant pour l'affichage de la vue d'ensemble NPS."""
import streamlit as st
import plotly.graph_objects as go
from config import COLORS

def get_nps_category(score):
    """Détermine la catégorie NPS en fonction du score."""
    if score >= 8:
        return "Promoteur"
    elif score <= 6:
        return "Détracteur"
    return "Neutre"

def calculate_nps(scores):
    """Calcule le score NPS."""
    if len(scores) == 0:
        return 0
    promoters = sum(score >= 8 for score in scores)
    detractors = sum(score <= 6 for score in scores)
    total = len(scores)
    return round((promoters/total - detractors/total) * 100)

def display_nps_overview(df, seuil):
    """Affiche la vue d'ensemble NPS."""
    st.header("Vue d'ensemble NPS")
    
    # Vérification des données
    if df is None or df.empty:
        st.error("Aucune donnée disponible")
        return
        
    if 'Horodateur' not in df.columns:
        st.error("La colonne 'Horodateur' est manquante")
        return
    
    # Préparation des données mensuelles
    df['Mois'] = df['Horodateur'].dt.strftime('%Y-%m')
    df['Mois_Nom'] = df['Horodateur'].dt.strftime('%B %Y')
    df['Catégorie'] = df['Recommandation'].apply(get_nps_category)
    
    # NPS actuel
    current_month = df['Mois'].max()
    current_month_name = df[df['Mois'] == current_month]['Mois_Nom'].iloc[0]
    previous_month = df[df['Mois'] < current_month]['Mois'].max()
    previous_month_name = df[df['Mois'] == previous_month]['Mois_Nom'].iloc[0]
    
    current_data = df[df['Mois'] == current_month]
    current_nps = calculate_nps(current_data['Recommandation'])
    
    previous_data = df[df['Mois'] == previous_month]
    previous_nps = calculate_nps(previous_data['Recommandation'])
    
    # Affichage du NPS principal dans un cadre stylisé
    st.markdown("""
        <style>
        .nps-box {
            background-color: #1E1E1E;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .nps-title {
            color: #FFFFFF;
            font-size: 1.2em;
            margin-bottom: 10px;
        }
        .nps-value {
            color: #FFFFFF;
            font-size: 3em;
            font-weight: bold;
            margin: 10px 0;
        }
        .nps-change {
            font-size: 1.1em;
            margin-top: 10px;
        }
        </style>
        """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        delta = current_nps - previous_nps
        delta_color = "green" if delta >= 0 else "red"
        delta_symbol = "↑" if delta >= 0 else "↓"
        
        st.markdown(f"""
            <div class="nps-box">
                <div class="nps-title">NPS ce mois-ci</div>
                <div class="nps-value">{int(current_nps)}%</div>
                <div class="nps-change" style="color: {delta_color}">
                    {delta_symbol} {abs(int(delta))}% par rapport à {previous_month_name}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Graphique avec tooltips et NPS par barre
    monthly_distribution = df.groupby(['Mois', 'Mois_Nom', 'Catégorie']).size().unstack(fill_value=0)
    monthly_nps = df.groupby('Mois').apply(lambda x: calculate_nps(x['Recommandation'])).reset_index()
    monthly_nps.columns = ['Mois', 'NPS']
    
    fig = go.Figure()
    
    for category in ['Détracteur', 'Neutre', 'Promoteur']:
        fig.add_trace(go.Bar(
            name=category,
            x=monthly_distribution.index.get_level_values('Mois'),
            y=monthly_distribution[category],
            marker_color=COLORS[category],
            hovertemplate="Mois: %{x}<br>" +
                         f"{category}s: %{{y}}<br>" +
                         "<extra></extra>"
        ))
    
    # Ajout de la ligne NPS
    fig.add_trace(go.Scatter(
        x=monthly_nps['Mois'],
        y=monthly_nps['NPS'],
        mode='lines+text',
        name='NPS',
        line=dict(color='white', width=2),
        text=monthly_nps['NPS'].apply(lambda x: f"{int(x)}%"),
        textposition='top center',
        textfont=dict(size=14, color='white'),
        hovertemplate="NPS: %{text}<br><extra></extra>"
    ))
    
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

    # Affichage des données mensuelles avec seuil de représentativité
    monthly_counts = df.groupby('Mois').size()
    st.markdown("### Détail mensuel")
    
    for month in monthly_distribution.index.get_level_values('Mois'):
        count = monthly_counts[month]
        if count < seuil:
            st.warning(f"{month}: {count} réponses (sous le seuil de représentativité)")
        else:
            st.success(f"{month}: {count} réponses")