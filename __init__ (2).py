"""
Prediction Page - Advanced Engagement Prediction Interface

This page provides comprehensive prediction capabilities using the Markov engagement model,
including single predictions, Monte Carlo simulations, scenario comparisons, and sensitivity analysis.

Author: ITESM
Date: 2025-11-18
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, List, Optional, Any
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.models.markov_model import MarkovEngagementPredictor
from src.models.predictor import (
    predict_employee_engagement,
    compare_scenarios,
    analyze_feature_impact,
    calculate_confidence_intervals
)
from src.data.loader import DataLoader

# Import shared components
sys.path.insert(0, str(Path(__file__).parent.parent))
from components.header import render_header, render_sidebar_logos, get_global_css

# Page configuration
st.set_page_config(page_title="Prediction", page_icon="public/img/tec.png", layout="wide")

# Render sidebar with logos
with st.sidebar:
    render_sidebar_logos()

# Color scheme for engagement states
STATE_COLORS = {
    'Bajo': '#D62828',
    'Medio': '#F77F00',
    'Alto': '#06A77D',
    'Muy Alto': '#2E86AB'
}

STATES = ['Bajo', 'Medio', 'Alto', 'Muy Alto']


# ==================== UTILITY FUNCTIONS ====================

def convert_time_to_steps(value: int, unit: str) -> int:
    """Convert time value to number of steps."""
    conversions = {
        'Días': 1,
        'Semanas': 7,
        'Meses': 30,
        'Trimestres': 90
    }
    return value * conversions[unit]


def format_time_equivalence(value: int, unit: str) -> str:
    """Format time equivalence string."""
    days = convert_time_to_steps(value, unit)
    weeks = days / 7
    months = days / 30

    parts = [f"{days} días"]
    if weeks >= 1:
        parts.append(f"~{weeks:.1f} semanas")
    if months >= 1:
        parts.append(f"~{months:.1f} meses")

    return " = ".join(parts)


def create_gauge_chart(probability: float, state: str) -> go.Figure:
    """Create a gauge chart for confidence level."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=probability * 100,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Probabilidad de la Predicción", 'font': {'size': 20}},
        number={'suffix': "%", 'font': {'size': 40}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': STATE_COLORS.get(state, '#2E86AB')},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 25], 'color': '#FFE5E5'},
                {'range': [25, 50], 'color': '#FFF4E5'},
                {'range': [50, 75], 'color': '#E5F7F0'},
                {'range': [75, 100], 'color': '#E5F2FF'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))

    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig


def create_probability_bars(prediction: Dict[str, float]) -> go.Figure:
    """Create horizontal bar chart for probability distribution."""
    states_sorted = sorted(prediction.items(), key=lambda x: x[1], reverse=True)
    states = [s[0] for s in states_sorted]
    probs = [s[1] * 100 for s in states_sorted]
    colors = [STATE_COLORS[s] for s in states]

    fig = go.Figure(go.Bar(
        x=probs,
        y=states,
        orientation='h',
        marker=dict(color=colors),
        text=[f'{p:.1f}%' for p in probs],
        textposition='auto',
        textfont=dict(size=14, color='white', family='Arial Black')
    ))

    fig.update_layout(
        title="Distribución de Probabilidades",
        xaxis_title="Probabilidad (%)",
        yaxis_title="Estado de Engagement",
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=False
    )

    return fig


def create_trajectory_chart(current_state: str, n_steps: int, predictor: MarkovEngagementPredictor, features: Optional[Dict] = None) -> go.Figure:
    """Create line chart showing probability evolution over time."""
    states = ['Bajo', 'Medio', 'Alto', 'Muy Alto']
    colors = {'Bajo': '#D62828', 'Medio': '#F77F00', 'Alto': '#06A77D', 'Muy Alto': '#2E86AB'}

    # Calculate probabilities at each step
    steps_to_show = min(n_steps, 20)  # Limit for readability
    step_range = list(range(0, n_steps + 1, max(1, n_steps // steps_to_show)))
    if step_range[-1] != n_steps:
        step_range.append(n_steps)

    prob_evolution = {state: [] for state in states}

    for step in step_range:
        if step == 0:
            # Initial state - 100% in current state
            for state in states:
                prob_evolution[state].append(100.0 if state == current_state else 0.0)
        else:
            pred = predictor.predict_next_state(current_state, features, step)
            for state in states:
                prob_evolution[state].append(pred.get(state, 0) * 100)

    fig = go.Figure()

    # Add line for each state
    for state in states:
        fig.add_trace(go.Scatter(
            x=step_range,
            y=prob_evolution[state],
            mode='lines+markers',
            name=state,
            line=dict(color=colors[state], width=2),
            marker=dict(size=6),
            hovertemplate=f'{state}: %{{y:.1f}}%<extra></extra>'
        ))

    fig.update_layout(
        title="Evolución de Probabilidades",
        xaxis_title="Tiempo (steps)",
        yaxis_title="Probabilidad (%)",
        yaxis=dict(range=[0, 100]),
        height=350,
        margin=dict(l=20, r=20, t=40, b=20),
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5)
    )

    return fig


def create_monte_carlo_chart(mc_results: Dict[str, Any]) -> go.Figure:
    """Create chart showing Monte Carlo simulation trajectories."""
    engagement_map = {'Bajo': 1, 'Medio': 2, 'Alto': 3, 'Muy Alto': 4}

    # Sample trajectories (max 50 for performance)
    n_sample = min(50, len(mc_results['trajectories']))
    sample_indices = np.random.choice(len(mc_results['trajectories']), n_sample, replace=False)

    fig = go.Figure()

    # Plot sample trajectories
    for idx in sample_indices:
        trajectory = mc_results['trajectories'][idx]
        values = [engagement_map[s] for s in trajectory]
        steps = list(range(len(values)))

        fig.add_trace(go.Scatter(
            x=steps,
            y=values,
            mode='lines',
            line=dict(color='lightblue', width=1),
            opacity=0.3,
            showlegend=False,
            hoverinfo='skip'
        ))

    # Plot mean trajectory
    expected_values = mc_results['expected_values']
    steps = list(range(len(expected_values)))

    fig.add_trace(go.Scatter(
        x=steps,
        y=expected_values,
        mode='lines+markers',
        name='Media',
        line=dict(color='#2E86AB', width=4),
        marker=dict(size=8, color='#2E86AB')
    ))

    # Confidence intervals
    ci_lower = [ci[0] for ci in mc_results['confidence_intervals']]
    ci_upper = [ci[1] for ci in mc_results['confidence_intervals']]

    fig.add_trace(go.Scatter(
        x=steps + steps[::-1],
        y=ci_upper + ci_lower[::-1],
        fill='toself',
        fillcolor='rgba(46, 134, 171, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name='IC 95%',
        showlegend=True
    ))

    fig.update_layout(
        title="Trayectorias Simuladas (Monte Carlo)",
        xaxis_title="Tiempo (steps)",
        yaxis_title="Nivel de Engagement",
        yaxis=dict(
            tickmode='array',
            tickvals=[1, 2, 3, 4],
            ticktext=['Bajo', 'Medio', 'Alto', 'Muy Alto']
        ),
        height=450,
        margin=dict(l=20, r=20, t=40, b=20),
        hovermode='x unified'
    )

    return fig


def create_final_state_distribution(mc_results: Dict[str, Any]) -> go.Figure:
    """Create histogram of final states from Monte Carlo simulation."""
    final_states = [trajectory[-1] for trajectory in mc_results['trajectories']]

    counts = pd.Series(final_states).value_counts()
    states = [s for s in STATES if s in counts.index]
    values = [counts[s] for s in states]
    colors = [STATE_COLORS[s] for s in states]

    fig = go.Figure(go.Bar(
        x=states,
        y=values,
        marker=dict(color=colors),
        text=[f'{v/sum(values)*100:.1f}%' for v in values],
        textposition='auto',
        textfont=dict(size=14, color='white', family='Arial Black')
    ))

    fig.update_layout(
        title="Distribución de Estados Finales",
        xaxis_title="Estado",
        yaxis_title="Frecuencia",
        height=350,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=False
    )

    return fig


# ==================== MAIN PAGE ====================

# Render professional header
render_header(
    title="Predicción de Engagement",
    subtitle="Markov Prediction Engine",
    description="Genera predicciones de estados de engagement usando modelos de Cadenas de Markov."
)

# Initialize session state
if 'prediction_history' not in st.session_state:
    st.session_state.prediction_history = []

if 'comparison_scenarios' not in st.session_state:
    st.session_state.comparison_scenarios = []

# Check if model is available
if 'predictor' not in st.session_state or st.session_state.predictor is None:
    st.error("No hay un modelo entrenado disponible. Por favor, ve a la página de Variable Selection, selecciona las variables y haz clic en 'Guardar y Entrenar Modelo'.")
    st.stop()

predictor = st.session_state.predictor

# ==================== SIDEBAR CONFIGURATION ====================

with st.sidebar:
    st.header("Configuración de Predicción")

    # 1. Current Engagement State
    st.subheader("Estado Actual")
    current_state = st.radio(
        "Selecciona el estado actual de engagement:",
        STATES,
        index=1,
        help="Estado de engagement del empleado en el momento actual"
    )

    # Color-coded state indicator
    state_color = STATE_COLORS[current_state]
    st.markdown(
        f"<div style='background-color: {state_color}; padding: 10px; border-radius: 5px; text-align: center; color: white; font-weight: bold;'>"
        f"Estado: {current_state}"
        f"</div>",
        unsafe_allow_html=True
    )

    st.markdown("---")

    # 2. Context Variables
    st.subheader("Variables de Contexto")

    use_all_data = st.checkbox("Usar todos los datos (sin filtro)", value=True)

    features_dict = None
    if not use_all_data:
        if hasattr(predictor, 'conditional_matrices') and predictor.conditional_matrices:
            st.info("Selecciona valores para las variables contextuales:")
            features_dict = {}

            for feature, matrices in predictor.conditional_matrices.items():
                values = list(matrices.keys())
                selected = st.selectbox(
                    f"{feature}:",
                    ['<Todos>'] + values,
                    help=f"Selecciona un valor específico para {feature}"
                )
                if selected != '<Todos>':
                    features_dict[feature] = selected

            if not features_dict:
                features_dict = None
        else:
            st.warning("No hay variables contextuales disponibles en el modelo.")

    st.markdown("---")

    # 3. Time Horizon
    st.subheader("Horizonte Temporal")

    time_unit = st.radio(
        "Unidad de tiempo:",
        ['Días', 'Semanas', 'Meses', 'Trimestres'],
        index=1,
        horizontal=True
    )

    # Dynamic range based on unit
    ranges = {
        'Días': (1, 365),
        'Semanas': (1, 52),
        'Meses': (1, 12),
        'Trimestres': (1, 4)
    }

    time_value = st.slider(
        f"Cantidad de {time_unit.lower()}:",
        min_value=ranges[time_unit][0],
        max_value=ranges[time_unit][1],
        value=min(4, ranges[time_unit][1]),
        step=1
    )

    # Presets
    st.caption("Presets rápidos:")
    cols = st.columns(4)

    presets = {
        '1 sem': (1, 'Semanas'),
        '1 mes': (1, 'Meses'),
        '3 meses': (3, 'Meses'),
        '1 año': (12, 'Meses')
    }

    for col, (label, (val, unit)) in zip(cols, presets.items()):
        if col.button(label, use_container_width=True):
            time_value = val
            time_unit = unit
            st.rerun()

    # Calculate steps
    n_steps = convert_time_to_steps(time_value, time_unit)

    st.info(f"**Equivalencia:** {format_time_equivalence(time_value, time_unit)}")
    st.caption(f"**Steps del modelo:** {n_steps}")

    st.markdown("---")

    # 4. Predict Button
    predict_button = st.button(
        "PREDECIR",
        type="primary",
        use_container_width=True,
        help="Generar predicción con la configuración actual"
    )

# ==================== MAIN CONTENT ====================

if predict_button:
    with st.spinner("Generando predicción..."):
        try:
            # Make prediction
            result = predict_employee_engagement(
                predictor,
                current_state,
                features_dict,
                n_steps=n_steps,
                n_simulations=1000,
                include_monte_carlo=True
            )

            # Store in session state
            st.session_state.last_prediction = result
            st.session_state.prediction_config = {
                'current_state': current_state,
                'features': features_dict,
                'n_steps': n_steps,
                'time_value': time_value,
                'time_unit': time_unit
            }

            st.success("Predicción completada exitosamente!")

        except Exception as e:
            st.error(f"Error al generar predicción: {str(e)}")
            st.stop()

# Display prediction results
if 'last_prediction' in st.session_state:
    result = st.session_state.last_prediction
    config = st.session_state.prediction_config

    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Predicción Principal",
        "Simulación Monte Carlo",
        "Análisis Comparativo",
        "Sensibilidad"
    ])

    # ==================== TAB 1: MAIN PREDICTION ====================

    with tab1:
        st.header("Predicción Principal")

        # Row 1: Main prediction
        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader("Estado Predicho")
            most_likely = result['most_likely_state']
            confidence = result['most_likely_probability']

            st.markdown(
                f"<div style='background-color: {STATE_COLORS[most_likely]}; padding: 30px; border-radius: 10px; text-align: center; color: white;'>"
                f"<h1 style='margin: 0; font-size: 48px;'>{most_likely}</h1>"
                f"<p style='margin: 10px 0 0 0; font-size: 18px;'>Confianza: {confidence*100:.1f}%</p>"
                f"</div>",
                unsafe_allow_html=True
            )

            st.markdown("")

            # Gauge chart
            st.plotly_chart(
                create_gauge_chart(confidence, most_likely),
                use_container_width=True
            )
            st.caption("Probabilidad del estado predicho. >70% alta certeza, 50-70% moderada, <50% resultado incierto.")

        with col2:
            # Probability distribution
            st.plotly_chart(
                create_probability_bars(result['analytical_prediction']),
                use_container_width=True
            )
            st.caption("Probabilidad de cada estado. La barra más larga es el estado predicho.")

            # Trajectory
            st.plotly_chart(
                create_trajectory_chart(config['current_state'], config['n_steps'], predictor, config['features']),
                use_container_width=True
            )
            st.caption("Cómo evolucionan las probabilidades en el tiempo. El cruce de líneas indica cambio de estado más probable.")

        st.markdown("---")

        # Row 2: Scenarios
        st.subheader("Escenarios Posibles")

        col1, col2, col3 = st.columns(3)

        # Calculate scenarios from MC results
        if 'monte_carlo' in result:
            final_states = [t[-1] for t in result['monte_carlo']['trajectories']]
            final_counts = pd.Series(final_states).value_counts()

            # Best case (90th percentile)
            best_states = sorted(final_counts.items(), key=lambda x: predictor.engagement_map[x[0]], reverse=True)
            best_case = best_states[0][0] if best_states else most_likely
            best_prob = final_counts[best_case] / len(final_states)

            # Expected (mode)
            expected_case = most_likely
            expected_prob = confidence

            # Worst case (10th percentile)
            worst_states = sorted(final_counts.items(), key=lambda x: predictor.engagement_map[x[0]])
            worst_case = worst_states[0][0] if worst_states else most_likely
            worst_prob = final_counts[worst_case] / len(final_states)

        else:
            best_case = expected_case = worst_case = most_likely
            best_prob = expected_prob = worst_prob = confidence

        with col1:
            st.markdown("##### Mejor Caso")
            st.metric(
                "Estado",
                best_case,
                help="Escenario optimista basado en percentil 90"
            )
            st.progress(best_prob)
            st.caption(f"Probabilidad: {best_prob*100:.1f}%")

        with col2:
            st.markdown("##### Caso Esperado")
            st.metric(
                "Estado",
                expected_case,
                help="Escenario más probable"
            )
            st.progress(expected_prob)
            st.caption(f"Probabilidad: {expected_prob*100:.1f}%")

        with col3:
            st.markdown("##### Peor Caso")
            st.metric(
                "Estado",
                worst_case,
                help="Escenario pesimista basado en percentil 10"
            )
            st.progress(worst_prob)
            st.caption(f"Probabilidad: {worst_prob*100:.1f}%")

        st.markdown("---")

        # Row 3: Movement probabilities
        st.subheader("Probabilidades de Movimiento")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Mejora",
                f"{result['improvement_probability']*100:.1f}%",
                help="Probabilidad de pasar a un estado superior"
            )

        with col2:
            st.metric(
                "Estabilidad",
                f"{result['stability_probability']*100:.1f}%",
                help="Probabilidad de permanecer en el mismo estado"
            )

        with col3:
            st.metric(
                "Deterioro",
                f"{result['deterioration_probability']*100:.1f}%",
                help="Probabilidad de pasar a un estado inferior"
            )

    # ==================== TAB 2: MONTE CARLO ====================

    with tab2:
        st.header("Simulación Monte Carlo")

        if 'monte_carlo' in result:
            mc_results = result['monte_carlo']

            # Configuration
            with st.expander("Configuración de Simulación", expanded=False):
                col1, col2 = st.columns(2)

                with col1:
                    n_sims = st.slider(
                        "Número de simulaciones:",
                        min_value=100,
                        max_value=5000,
                        value=1000,
                        step=100,
                        help="Mayor número = resultados más precisos pero más lento"
                    )

                with col2:
                    if st.button("Re-ejecutar Simulación", type="secondary"):
                        with st.spinner(f"Ejecutando {n_sims} simulaciones..."):
                            new_result = predict_employee_engagement(
                                predictor,
                                config['current_state'],
                                config['features'],
                                n_steps=config['n_steps'],
                                n_simulations=n_sims,
                                include_monte_carlo=True
                            )
                            st.session_state.last_prediction = new_result
                            st.rerun()

            # Results
            col1, col2 = st.columns([2, 1])

            with col1:
                # Trajectories chart
                st.plotly_chart(
                    create_monte_carlo_chart(mc_results),
                    use_container_width=True
                )
                st.caption("Líneas claras=trayectorias individuales, línea azul=promedio, banda=intervalo de confianza 95%.")

            with col2:
                # Final state distribution
                st.plotly_chart(
                    create_final_state_distribution(mc_results),
                    use_container_width=True
                )
                st.caption("Frecuencia de estados finales en las simulaciones. Muestra la variabilidad de resultados posibles.")

            st.markdown("---")

            # Statistics
            st.subheader("Estadísticas de Simulación")

            final_states = [t[-1] for t in mc_results['trajectories']]
            final_values = [predictor.engagement_map[s] for s in final_states]

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Media", f"{np.mean(final_values):.2f}")

            with col2:
                st.metric("Mediana", f"{np.median(final_values):.2f}")

            with col3:
                st.metric("Desv. Estándar", f"{np.std(final_values):.2f}")

            with col4:
                st.metric("Moda", pd.Series(final_states).mode()[0])

            st.markdown("---")

            # Probability over time
            st.subheader("Evolución de Probabilidades")

            state_probs = mc_results['state_probabilities']

            fig = go.Figure()

            for state in STATES:
                if state in state_probs.columns:
                    fig.add_trace(go.Scatter(
                        x=list(range(len(state_probs))),
                        y=state_probs[state],
                        mode='lines+markers',
                        name=state,
                        line=dict(color=STATE_COLORS[state], width=2),
                        marker=dict(size=6)
                    ))

            fig.update_layout(
                title="Probabilidad de cada Estado vs. Tiempo",
                xaxis_title="Tiempo (steps)",
                yaxis_title="Probabilidad",
                height=400,
                hovermode='x unified'
            )

            st.plotly_chart(fig, use_container_width=True)
            st.caption("Proporción de simulaciones en cada estado por paso. Convergencia indica estabilización del sistema.")

        else:
            st.warning("Simulación Monte Carlo no disponible. Ejecuta una predicción primero.")

    # ==================== TAB 3: COMPARATIVE ANALYSIS ====================

    with tab3:
        st.header("Análisis Comparativo")

        st.subheader("Agregar Escenarios para Comparar")

        col1, col2 = st.columns([3, 1])

        with col1:
            st.info("Agrega hasta 5 escenarios diferentes para comparar sus predicciones.")

        with col2:
            if st.button("Agregar Escenario Actual", disabled=len(st.session_state.comparison_scenarios) >= 5):
                scenario = {
                    'name': f"Escenario {len(st.session_state.comparison_scenarios) + 1}",
                    'current_state': config['current_state'],
                    'features': config['features'],
                    'prediction': result['most_likely_state'],
                    'confidence': result['most_likely_probability']
                }
                st.session_state.comparison_scenarios.append(scenario)
                st.rerun()

        # Display scenarios
        if st.session_state.comparison_scenarios:
            st.markdown("---")
            st.subheader("Escenarios Guardados")

            # Table
            scenario_data = []
            for i, sc in enumerate(st.session_state.comparison_scenarios):
                scenario_data.append({
                    'Nombre': sc['name'],
                    'Estado Actual': sc['current_state'],
                    'Variables': str(sc['features']) if sc['features'] else 'Todas',
                    'Predicción': sc['prediction'],
                    'Confianza': f"{sc['confidence']*100:.1f}%"
                })

            df_scenarios = pd.DataFrame(scenario_data)
            st.dataframe(df_scenarios, use_container_width=True)
            st.caption("Resumen de escenarios guardados. Compara diferentes configuraciones lado a lado.")

            # Actions
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("Limpiar Todo"):
                    st.session_state.comparison_scenarios = []
                    st.rerun()

            st.markdown("---")

            # Comparison visualizations
            st.subheader("Visualización Comparativa")

            # Bar chart comparison
            states_list = [sc['prediction'] for sc in st.session_state.comparison_scenarios]
            confidences = [sc['confidence'] for sc in st.session_state.comparison_scenarios]
            names = [sc['name'] for sc in st.session_state.comparison_scenarios]

            fig = go.Figure()

            for i, (name, state, conf) in enumerate(zip(names, states_list, confidences)):
                fig.add_trace(go.Bar(
                    name=name,
                    x=[name],
                    y=[conf * 100],
                    marker_color=STATE_COLORS[state],
                    text=f"{state}<br>{conf*100:.1f}%",
                    textposition='auto'
                ))

            fig.update_layout(
                title="Comparación de Confianza por Escenario",
                yaxis_title="Confianza (%)",
                height=400,
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True)
            st.caption("Comparación visual de escenarios. El color indica el estado predicho, la altura la confianza.")

        else:
            st.info("No hay escenarios guardados. Agrega el escenario actual para comenzar la comparación.")

    # ==================== TAB 4: SENSITIVITY ====================

    with tab4:
        st.header("Análisis de Sensibilidad")

        if hasattr(predictor, 'conditional_matrices') and predictor.conditional_matrices:
            st.subheader("Impacto de Variables Contextuales")

            selected_feature = st.selectbox(
                "Selecciona una variable para analizar:",
                list(predictor.conditional_matrices.keys())
            )

            if selected_feature:
                with st.spinner(f"Analizando impacto de {selected_feature}..."):
                    impact_df = analyze_feature_impact(
                        predictor,
                        config['current_state'],
                        selected_feature,
                        n_steps=config['n_steps'],
                        metric='improvement_probability'
                    )

                    st.dataframe(
                        impact_df.style.background_gradient(
                            subset=['improvement_probability'],
                            cmap='RdYlGn'
                        ),
                        use_container_width=True
                    )
                    st.caption("Probabilidad de mejora para cada valor de la variable. Verde=mayor probabilidad de mejora.")

                    # Tornado chart
                    fig = go.Figure(go.Bar(
                        x=impact_df['improvement_probability'],
                        y=impact_df['feature_value'],
                        orientation='h',
                        marker=dict(
                            color=impact_df['improvement_probability'],
                            colorscale='RdYlGn',
                            showscale=True
                        )
                    ))

                    fig.update_layout(
                        title=f"Impacto de {selected_feature} en Probabilidad de Mejora",
                        xaxis_title="Probabilidad de Mejora",
                        yaxis_title=selected_feature,
                        height=400
                    )

                    st.plotly_chart(fig, use_container_width=True)
                    st.caption("Barras más largas = mayor impacto positivo. Identifica los valores que maximizan la probabilidad de mejora.")

            st.markdown("---")

            # Recommendations
            st.subheader("Recomendaciones")

            st.success("""
            **Basado en el análisis:**

            1. Las variables con mayor impacto en las predicciones son aquellas que muestran mayor variación en las probabilidades.
            2. Valores específicos que maximizan la probabilidad de mejora deben ser considerados en planes de acción.
            3. Variables con bajo impacto pueden simplificarse en análisis futuros.
            """)

        else:
            st.warning("No hay variables contextuales disponibles en el modelo para análisis de sensibilidad.")

    # ==================== EXPORT RESULTS ====================

    st.markdown("---")
    st.subheader("Exportar Resultados")

    col1, col2, col3 = st.columns(3)

    with col1:
        # Export as JSON
        import json
        export_data = {
            'configuracion': config,
            'prediccion': {
                'estado_predicho': result['most_likely_state'],
                'confianza': result['most_likely_probability'],
                'probabilidades': result['analytical_prediction'],
                'mejora_prob': result['improvement_probability'],
                'deterioro_prob': result['deterioration_probability']
            }
        }

        st.download_button(
            "Descargar JSON",
            data=json.dumps(export_data, indent=2),
            file_name=f"prediccion_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

    with col2:
        # Export as CSV
        csv_data = pd.DataFrame([{
            'Estado Actual': config['current_state'],
            'Estado Predicho': result['most_likely_state'],
            'Confianza': result['most_likely_probability'],
            'P(Mejora)': result['improvement_probability'],
            'P(Deterioro)': result['deterioration_probability'],
            'Horizonte': f"{config['time_value']} {config['time_unit']}"
        }])

        st.download_button(
            "Descargar CSV",
            data=csv_data.to_csv(index=False),
            file_name=f"prediccion_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

else:
    # No prediction yet
    st.info("Configura los parámetros en el panel izquierdo y presiona **PREDECIR** para comenzar.")

    st.markdown("""
    ### Cómo usar esta página

    1. **Estado Actual**: Selecciona el nivel de engagement actual del empleado
    2. **Variables de Contexto**: Filtra por características específicas o usa todos los datos
    3. **Horizonte Temporal**: Define qué tan lejos en el futuro quieres predecir
    4. **Presiona PREDECIR**: Genera la predicción con análisis completo

    ### Qué incluye la predicción

    - **Predicción Principal**: Estado más probable con nivel de confianza
    - **Simulación Monte Carlo**: 1000+ simulaciones para estimar distribuciones
    - **Análisis Comparativo**: Compara múltiples escenarios lado a lado
    - **Análisis de Sensibilidad**: Identifica qué variables tienen mayor impacto
    """)
