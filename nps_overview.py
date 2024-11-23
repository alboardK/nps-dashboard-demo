import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

# Couleurs pour les catégories de NPS
COLORS = {
    "Promoter": "rgb(46, 204, 113)",
    "Passive": "rgb(241, 196, 15)",
    "Detractor": "rgb(231, 76, 60)"
}

# Fonction pour catégoriser les scores NPS
def get_nps_category(score):
    try:
        score = float(score)
        if score >= 8:
            return "Promoter"
        elif score >= 6:
            return "Passive"
        else:
            return "Detractor"
    except ValueError:
        return "Unknown"

# Fonction pour calculer le NPS pour un mois spécifique
def calculate_nps(data, target_month):
    # Filtrer les données pour le mois ciblé et exclure les NaN
    month_data = data[(data['Date'].dt.to_period('M') == target_month.to_period('M')) & (data['Recommandation'].notna())]
    
    if month_data.empty:
        return None  # Pas de données pour ce mois

    # Catégorisation en fonction des scores NPS
    promoters = month_data[month_data['Recommandation'] >= 8]
    detractors = month_data[month_data['Recommandation'] <= 5]
    
    # Calcul du score NPS
    nps_score = ((len(promoters) - len(detractors)) / len(month_data)) * 100
    return nps_score

# Fonction pour trouver le dernier mois avec des données
def find_last_month_with_data(data, current_month):
    # Utiliser `Timestamp` pour assurer la compatibilité avec `DateOffset`
    last_month = current_month - pd.DateOffset(months=1)
    while last_month >= data['Date'].min():
        # Vérifier les données pour `last_month` en utilisant `.to_period('M')` pour correspondre à `calculate_nps`
        if not data[data['Date'].dt.to_period('M') == last_month.to_period('M')].empty:
            return last_month
        last_month -= pd.DateOffset(months=1)
    return None

# Fonction pour afficher l'aperçu du NPS
def display_nps_overview(df, seuil=35):
    st.header("Vue d'ensemble NPS")
    
    if df.empty:
        st.error("Aucune donnée disponible")
        return

    # Calcul des mois actuels et précédents
    valid_months = df.dropna(subset=['Recommandation']).groupby(df['Date'].dt.to_period("M")).size().index
    current_month = valid_months.max().to_timestamp()
    previous_month = find_last_month_with_data(df, current_month)

    # Calcul des NPS actuels et précédents
    current_nps = calculate_nps(df, current_month)
    previous_nps = calculate_nps(df, previous_month) if previous_month is not None else None
    delta = current_nps - previous_nps if previous_nps is not None else None
    delta_symbol = "↑" if delta and delta >= 0 else "↓"
    delta_color = "#2ecc71" if delta and delta >= 0 else "#e74c3c"  # Vert pour augmentation, rouge pour diminution
    previous_month_name = previous_month.strftime("%B %Y") if previous_month else "Pas de données antérieures"

    # Injection de CSS et affichage de la boîte de NPS
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
            .nps-title {{
                font-size: 1.5em;
                font-weight: bold;
                color: #ecf0f1;
            }}
            .nps-value {{
                font-size: 3em;
                font-weight: bold;
                color: #2ecc71;
                margin: 10px 0;
            }}
            .nps-change {{
                font-size: 1.2em;
                color: {delta_color};
            }}
            .nps-subtitle {{
                font-size: 1em;
                color: #bdc3c7;
            }}
        </style>

        <div class="nps-container">
            <div class="nps-title">NPS ce mois-ci</div>
            <div class="nps-value">{f"{int(current_nps)}%" if current_nps is not None else "Non disponible"}</div>
            <div class="nps-change">{delta_symbol} {abs(int(delta))}% par rapport à {previous_month_name}</div>
        </div>
    """, unsafe_allow_html=True)

    # Graphique d'évolution du NPS
    fig = go.Figure()

    monthly_distribution = df[df['Date'].dt.to_period("M").isin(valid_months)].groupby([df['Date'].dt.to_period("M"), 'Catégorie']).size().unstack(fill_value=0)
    monthly_nps = df[df['Date'].dt.to_period("M").isin(valid_months)].groupby(df['Date'].dt.to_period("M")).apply(lambda x: calculate_nps(x, x['Date'].iloc[0])).reset_index()
    monthly_nps.columns = ['Mois', 'NPS']

    for category in ['Detractor', 'Passive', 'Promoter']:
        fig.add_trace(go.Bar(
            name=category,
            x=monthly_distribution.index.to_timestamp(),
            y=monthly_distribution[category],
            marker_color=COLORS[category],
            hovertemplate="Mois: %{x}<br>" +
                         f"{category}s: %{{y}}<br>" +
                         "<extra></extra>"
        ))

    fig.add_trace(go.Scatter(
        x=monthly_nps['Mois'].dt.to_timestamp(),
        y=monthly_nps['NPS'],
        mode='lines+text',
        name='NPS',
        line=dict(color='white', width=2),
        text=monthly_nps['NPS'].apply(lambda x: f"{int(x)}%" if pd.notna(x) else "N/A"),
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

    # Détail mensuel
    st.markdown("### Détail mensuel")
    monthly_counts = df.groupby(df['Date'].dt.to_period("M")).size()
    for month in monthly_distribution.index:
        count = monthly_counts[month]
        if count < seuil:
            st.warning(f"{month}: {count} réponses (sous le seuil de représentativité)")
        else:
            st.success(f"{month}: {count} réponses")