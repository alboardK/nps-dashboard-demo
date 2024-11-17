import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from config import METRIC_STRUCTURE, SCORE_COLORS

def get_service_name(col):
    """Obtient le nom du service à partir de la colonne en utilisant METRIC_STRUCTURE."""
    for category in METRIC_STRUCTURE.values():
        if col in category['metrics']:
            return category['metrics'][col]
    return col.replace('Satisfaction_', '')

def get_metric_category(metric_name):
    """Récupère la catégorie d'une métrique."""
    for category, details in METRIC_STRUCTURE.items():
        if metric_name in details['metrics']:
            return category
    return None

def calculate_category_scores(df, period='all'):
    """Calcule les scores moyens par catégorie pour une période donnée."""
    print("DEBUG - Début calculate_category_scores")
    print(f"DEBUG - Colonnes disponibles: {df.columns.tolist()}")
    category_scores = {}
    
    # Filtrer les données selon la période si nécessaire
    if period != 'all':
        current_date = df['Date'].max()
        if period == 'last_month':
            df = df[df['Date'] >= (current_date - timedelta(days=30))]
        elif period == 'last_quarter':
            df = df[df['Date'] >= (current_date - timedelta(days=90))]
        elif period == 'last_year':
            df = df[df['Date'] >= (current_date - timedelta(days=365))]

    # Calculer les scores pour chaque catégorie
    for category, details in METRIC_STRUCTURE.items():
        print(f"DEBUG - Traitement de la catégorie: {category}")
        metrics = details['metrics'].keys()
        print(f"DEBUG - Métriques recherchées: {list(metrics)}")
        scores = []
        for metric in metrics:
            if metric in df.columns:
                avg_score = df[metric].mean()
                if not pd.isna(avg_score):
                    scores.append(avg_score)
                print(f"DEBUG - Métrique {metric}: score moyen = {avg_score}")
            else:
                print(f"DEBUG - Métrique {metric} non trouvée dans les colonnes")
        
        if scores:
            category_scores[category] = {
                'mean': sum(scores) / len(scores),
                'metrics': {metric: df[metric].mean() for metric in metrics if metric in df.columns},
                'count': len(df),
                'color': details['color']
            }
            print(f"DEBUG - Score final pour {category}: {category_scores[category]['mean']}")
    
    print("DEBUG - Scores par catégorie:", category_scores)
    return category_scores

def get_score_color(score):
    """Détermine la couleur en fonction du score."""
    if pd.isna(score):
        return SCORE_COLORS['average']
    elif score >= 4.5:
        return SCORE_COLORS['excellent']
    elif score >= 4.0:
        return SCORE_COLORS['good']
    elif score >= 3.0:
        return SCORE_COLORS['average']
    elif score >= 2.0:
        return SCORE_COLORS['poor']
    else:
        return SCORE_COLORS['bad']

def calculate_satisfaction_stats(df, column):
    """Calcule les statistiques de satisfaction pour une colonne donnée."""
    stats = {}
    
    try:
        numeric_data = df[column]
        
        # Moyenne
        stats['moyenne'] = numeric_data.mean()
        
        # Tendance (m-1)
        current_month = df['Date'].max().replace(day=1)
        last_month = current_month - timedelta(days=1)
        current_mean = df[df['Date'] >= current_month][column].mean()
        previous_mean = df[(df['Date'] >= last_month) & 
                         (df['Date'] < current_month)][column].mean()
        stats['tendance'] = current_mean - previous_mean if not pd.isna(previous_mean) else 0
        
        # Distribution par catégorie
        stats['satisfaits'] = (numeric_data >= 4).sum() / numeric_data.count() * 100
        stats['neutres'] = (numeric_data == 3).sum() / numeric_data.count() * 100
        stats['insatisfaits'] = (numeric_data <= 2).sum() / numeric_data.count() * 100
        
        # Nombre de réponses
        stats['nb_reponses'] = numeric_data.notna().sum()
        
    except Exception as e:
        print(f"DEBUG - Erreur dans calculate_satisfaction_stats pour {column}:", str(e))
        stats = {
            'moyenne': 0,
            'tendance': 0,
            'satisfaits': 0,
            'neutres': 0,
            'insatisfaits': 0,
            'nb_reponses': 0
        }
    
    return stats

def get_top_flop_services(df):
    """Calcule les services avec leur performance."""
    resultats = []
    
    try:
        for col in df.columns:
            if 'Satisfaction_' in col:
                stats = calculate_satisfaction_stats(df, col)
                
                if stats['nb_reponses'] > 0:
                    service_name = get_service_name(col)
                    resultats.append({
                        'service': service_name,
                        'moyenne': stats['moyenne'],
                        'tendance': stats['tendance'],
                        'nb_reponses': stats['nb_reponses']
                    })
        
        # Tri par moyenne
        resultats.sort(key=lambda x: x['moyenne'], reverse=True)
        
        # Séparer top 3 et flop 3
        top_3 = resultats[:3] if len(resultats) >= 3 else resultats
        flop_3 = resultats[-3:] if len(resultats) >= 3 else resultats[::-1]
        
        return top_3, flop_3
        
    except Exception as e:
        print(f"DEBUG - Erreur dans get_top_flop_services:", str(e))
        return [], []

def get_cell_color(score, max_score, scores):
    """
    Détermine la couleur de la cellule en fonction du score.
    Ne colore que les meilleurs et moins bons scores.
    """
    if pd.isna(score):
        return "rgb(52, 73, 94)"  # Couleur neutre pour les valeurs manquantes
    
    # Trier tous les scores pour déterminer les seuils
    valid_scores = [s for s in scores if not pd.isna(s)]
    if not valid_scores:
        return "rgb(52, 73, 94)"
    
    # Définir les seuils pour les meilleurs (top 15%) et moins bons scores (bottom 15%)
    threshold_top = sorted(valid_scores, reverse=True)[int(len(valid_scores) * 0.15)]
    threshold_bottom = sorted(valid_scores)[int(len(valid_scores) * 0.15)]
    
    if score >= threshold_top:
        # Vert plus sombre pour les meilleurs scores
        return "rgb(36, 161, 88)"  # Vert assombri de 8%
    elif score <= threshold_bottom:
        # Rouge plus sombre pour les moins bons scores
        return "rgb(176, 52, 40)"  # Rouge assombri de 8%
    else:
        # Gris neutre pour les scores intermédiaires
        return "rgb(52, 73, 94)"

def calculate_global_nps(df):
    """Calcule le NPS global et le nombre de réponses."""
    total_reponses = df['Recommandation'].notna().sum()
    if total_reponses == 0:
        return 0, 0, 0, 0
        
    promoteurs = (df['Recommandation'] >= 9).sum()
    detracteurs = (df['Recommandation'] <= 6).sum()
    
    # Calcul du score de réabonnement moyen
    reabo_score = pd.to_numeric(df['ProbabiliteReabo'], errors='coerce').mean()
    reabo_reponses = pd.to_numeric(df['ProbabiliteReabo'], errors='coerce').notna().sum()
    
    nps = ((promoteurs - detracteurs) / total_reponses) * 100
    return round(nps), total_reponses, round(reabo_score, 1), reabo_reponses

def get_nps_color(score):
    """Détermine la couleur en fonction du score."""
    if score >= 50:
        return SCORE_COLORS['excellent']
    elif score >= 0:
        return SCORE_COLORS['average']
    else:
        return SCORE_COLORS['bad']

def get_nps_label(score):
    """Retourne le label approprié pour le score."""
    if score >= 50:
        return "Excellent"
    elif score >= 0:
        return "Moyen"
    else:
        return "À améliorer"

def display_metrics_details(df):
    """Affiche les détails des métriques de satisfaction."""
    # Modifier cette partie au début de display_metrics_details
    st.header("Détails des métriques de satisfaction")
        
    st.markdown("<br>", unsafe_allow_html=True)  # Ajouter un peu d'espace
    container = st.container()
    with container:
        col1, col2, col3 = st.columns([6, 1, 6])  # Meilleur ratio pour l'alignement
        with col1:
            periode = st.selectbox(
                "",
                ["Dernier mois", "Dernier trimestre", "Dernière année", "Tout"],
                label_visibility="collapsed"
            )
        with col3:
            view_mode = st.radio(
                "",
                ["Vue classique", "Vue par catégorie"],
                horizontal=True,
                key="view_mode",
                label_visibility="collapsed"
            )
    st.markdown("<br>", unsafe_allow_html=True)  # Ajouter un peu d'espace
        
    # Filtrage des données
    filtered_df = df.copy()
    if periode != "Tout":
        current_date = df['Date'].max()
        if periode == "Dernier mois":
            start_date = current_date - timedelta(days=30)
        elif periode == "Dernier trimestre":
            start_date = current_date - timedelta(days=90)
        else:
            start_date = current_date - timedelta(days=365)
        filtered_df = df[df['Date'] >= start_date]

    # Calcul et affichage des métriques globales
    nps_score, total_reponses, reabo_score, reabo_reponses = calculate_global_nps(filtered_df)
    nps_color = get_nps_color(nps_score)
    nps_label = get_nps_label(nps_score)
    reabo_color = get_nps_color(reabo_score * 10)  # Conversion sur 100 pour utiliser la même échelle
    reabo_label = get_nps_label(reabo_score * 10)
    
    # Affichage du résumé en trois colonnes
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""
            <div style='padding: 20px; border-radius: 10px; background-color: {nps_color}15;'>
                <h3 style='margin: 0; text-align: center; color: {nps_color};'>Score NPS</h3>
                <h2 style='margin: 10px 0; text-align: center;'>{nps_score}%</h2>
                <p style='margin: 0; text-align: center; color: {nps_color};'>{nps_label}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f"""
            <div style='padding: 20px; border-radius: 10px; background-color: {reabo_color}15;'>
                <h3 style='margin: 0; text-align: center; color: {reabo_color};'>Probabilité de réabonnement</h3>
                <h2 style='margin: 10px 0; text-align: center;'>{reabo_score}/10</h2>
                <p style='margin: 0; text-align: center; color: {reabo_color};'>
                    {reabo_reponses} réponses
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <div style='padding: 20px; border-radius: 10px; background-color: {SCORE_COLORS['average']}15;'>
                <h3 style='margin: 0; text-align: center; color: {SCORE_COLORS['average']};'>Réponses totales</h3>
                <h2 style='margin: 10px 0; text-align: center;'>{total_reponses}</h2>
                <p style='margin: 0; text-align: center; color: {SCORE_COLORS['average']};'>
                    {periode}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    try:
        if view_mode == "Vue classique":
            # Récupération des top/flop services
            top_3, flop_3 = get_top_flop_services(filtered_df)
            
            # Affichage Top/Flop en colonnes avec centrage
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                    <div style='text-align: center;'>
                        <h5>Points forts</h5>
                    </div>
                """, unsafe_allow_html=True)
                for service in top_3:
                    tendance = service['tendance']
                    tendance_icon = "↑" if tendance > 0 else "↓" if tendance < 0 else "−"
                    tendance_color = "green" if tendance > 0 else "red" if tendance < 0 else "gray"
                    st.markdown(f"""
                        <div style='font-family: monospace; margin: 5px 0; text-align: center;'>
                            <strong>{service['moyenne']:.1f}</strong> - {service['service']}
                            <span style='color: {tendance_color}'>
                                {tendance_icon} {abs(tendance):.1f}
                            </span>
                        </div>
                    """, unsafe_allow_html=True)

            with col2:
                st.markdown("""
                    <div style='text-align: center;'>
                        <h5>Points d'amélioration</h5>
                    </div>
                """, unsafe_allow_html=True)
                for service in flop_3:
                    tendance = service['tendance']
                    tendance_icon = "↑" if tendance > 0 else "↓" if tendance < 0 else "−"
                    tendance_color = "green" if tendance > 0 else "red" if tendance < 0 else "gray"
                    st.markdown(f"""
                        <div style='font-family: monospace; margin: 5px 0; text-align: center;'>
                            <strong>{service['moyenne']:.1f}</strong> - {service['service']}
                            <span style='color: {tendance_color}'>
                                {tendance_icon} {abs(tendance):.1f}
                            </span>
                        </div>
                    """, unsafe_allow_html=True)

            # Déplacer la légende des tendances après les points forts/faibles
            st.markdown("""
                <div style='font-size: 0.8em; color: gray; margin: 10px 0; text-align: center;'>
                    la différence avec le mois précédent
                    (↑ amélioration, ↓ baisse)
                </div>
            """, unsafe_allow_html=True)

            st.markdown("---")

            # Collecte des statistiques pour tous les services
            all_services_stats = []
            for col in filtered_df.columns:
                if 'Satisfaction_' in col:
                    stats = calculate_satisfaction_stats(filtered_df, col)
                    if stats['nb_reponses'] > 0:
                        service_name = get_service_name(col)
                        all_services_stats.append({
                            'service': service_name,
                            'moyenne': stats['moyenne'],
                            'satisfaits': stats['satisfaits'],
                            'neutres': stats['neutres'],
                            'insatisfaits': stats['insatisfaits'],
                            'nb_reponses': stats['nb_reponses']
                        })

            # Tri par moyenne décroissante
            all_services_stats.sort(key=lambda x: x['moyenne'], reverse=True)

            # Grille des scores
            st.subheader("Vue d'ensemble des services")
            
            # Création d'une grille 3x5
            grid_scores = [""] * 15
            all_scores = [s['moyenne'] for s in all_services_stats]
            
            for idx, service in enumerate(all_services_stats):
                if idx < 15:
                    score = service['moyenne']
                    grid_scores[idx] = {
                        'name': service['service'],
                        'score': score,
                        'color': get_cell_color(score, max(all_scores), all_scores),
                        'nb_reponses': service['nb_reponses']
                    }

            # Affichage de la grille
            for row in range(3):
                cols = st.columns(5)
                for col in range(5):
                    idx = row * 5 + col
                    if idx < len(grid_scores) and grid_scores[idx]:
                        with cols[col]:
                            st.markdown(f"""
                                <div style='padding: 10px; border-radius: 5px; margin: 5px; 
                                    text-align: center; height: 90px; background-color: {grid_scores[idx]['color']}; 
                                    color: white; display: flex; flex-direction: column; justify-content: space-between;'>
                                    <div style='font-size: 0.8em; margin-bottom: 5px;'>{grid_scores[idx]['name']}</div>
                                    <div style='font-size: 1.2em; font-weight: bold;'>{grid_scores[idx]['score']:.1f}</div>
                                    <div style='font-size: 0.7em; opacity: 0.8;'>{grid_scores[idx]['nb_reponses']} réponses</div>
                                </div>
                            """, unsafe_allow_html=True)

            st.markdown("---")

            # Graphique empilé des pourcentages avec scores moyens
            st.subheader("Détail des notes par service")
            
            fig_stack = go.Figure()

            # Tri des services par score pour le graphique
            all_services_stats.sort(key=lambda x: x['moyenne'])
            y_services = [s['service'] for s in all_services_stats]

            # Ajout des trois catégories
            fig_stack.add_trace(go.Bar(
                name='Satisfaits (4-5)',
                y=y_services,
                x=[s['satisfaits'] for s in all_services_stats],
                orientation='h',
                marker_color='rgb(46, 204, 113)',
                text=[f"{x:.0f}%" for x in [s['satisfaits'] for s in all_services_stats]],
                textposition='inside'
            ))

            fig_stack.add_trace(go.Bar(
                name='Neutres (3)',
                y=y_services,
                x=[s['neutres'] for s in all_services_stats],
                orientation='h',
                marker_color='rgb(241, 196, 15)',
                text=[f"{x:.0f}%" for x in [s['neutres'] for s in all_services_stats]],
                textposition='inside'
            ))

            fig_stack.add_trace(go.Bar(
                name='Insatisfaits (1-2)',
                y=y_services,
                x=[s['insatisfaits'] for s in all_services_stats],
                orientation='h',
                marker_color='rgb(231, 76, 60)',
                text=[f"{x:.0f}%" for x in [s['insatisfaits'] for s in all_services_stats]],
                textposition='inside'
            ))

            # Ajout des scores moyens à droite
            for idx, service in enumerate(all_services_stats):
                fig_stack.add_annotation(
                    x=100,
                    y=service['service'],
                    text=f"{service['moyenne']:.1f}",
                    showarrow=False,
                    xanchor='left',
                    xshift=10,
                    font=dict(size=12)
                )

            fig_stack.update_layout(
                barmode='stack',
                height=400,
                margin=dict(l=20, r=50, t=30, b=20),
                xaxis_title="Pourcentage",
                xaxis_range=[0, 100],
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )

            st.plotly_chart(fig_stack, use_container_width=True)

        else:  # Vue par catégorie
            # Calcul des scores par catégorie
            current_scores = calculate_category_scores(filtered_df)
            
            # Affichage des catégories
            st.markdown("### Vue par catégories")
            
            # Création d'une grille de catégories
            cols = st.columns(len(METRIC_STRUCTURE))
            
            for idx, (category, details) in enumerate(METRIC_STRUCTURE.items()):
                if category in current_scores:
                    score_info = current_scores[category]
                    with cols[idx]:
                        st.markdown(f"""
                            <div style='padding: 15px; border-radius: 5px; 
                                background-color: {details["color"]}15;'>
                                <h4 style='color: {details["color"]};'>{details['label']}</h4>
                                <h2 style='text-align: center;'>{score_info['mean']:.1f}/5</h2>
                                <p style='text-align: center; font-size: 0.8em;'>
                                    {score_info['count']} réponses
                                </p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Affichage des métriques détaillées de la catégorie
                        for metric, score in score_info['metrics'].items():
                            if not pd.isna(score):
                                metric_name = METRIC_STRUCTURE[category]['metrics'][metric]
                                st.markdown(f"""
                                    <div style='padding: 8px; margin: 5px 0; 
                                        background-color: {get_score_color(score)}15;
                                        border-radius: 3px;'>
                                        <div style='font-size: 0.9em;'>{metric_name}</div>
                                        <div style='font-size: 1.1em; font-weight: bold;'>
                                            {score:.1f}
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)

    except Exception as e:
        print(f"DEBUG - Erreur dans display_metrics_details:", str(e))
        st.error("Une erreur est survenue lors de l'affichage des métriques")