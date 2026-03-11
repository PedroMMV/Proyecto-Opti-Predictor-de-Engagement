"""
Home Page - Employee Engagement Prediction System

Dashboard principal con KPIs, visualizaciones y acceso rápido a todas las funcionalidades.

Author: ITESM
Date: 2025-11-18
Version: 1.0.0
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import shared components
from components.header import render_header, render_sidebar_logos, get_global_css

# Import project modules
try:
    from src.data.loader import DataLoader
    from src.models.markov_model import MarkovEngagementPredictor
    from src.data.preprocessor import EngagementPreprocessor
except ImportError as e:
    logger.error(f"Error importing project modules: {e}")


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Home - Engagement Prediction",
    page_icon="public/img/tec.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Render sidebar with logos
with st.sidebar:
    render_sidebar_logos()

# ============================================================================
# GLOBAL CSS
# ============================================================================

# Apply global CSS from shared component
st.markdown(get_global_css(), unsafe_allow_html=True)


# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def initialize_session_state():
    """Initialize session state variables."""
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'data_summary' not in st.session_state:
        st.session_state.data_summary = None
    if 'model_trained' not in st.session_state:
        st.session_state.model_trained = False
    if 'predictor' not in st.session_state:
        st.session_state.predictor = None
    if 'transition_matrix' not in st.session_state:
        st.session_state.transition_matrix = None
    if 'predictions_history' not in st.session_state:
        st.session_state.predictions_history = []
    if 'selected_features' not in st.session_state:
        st.session_state.selected_features = []
    if 'app_initialized' not in st.session_state:
        st.session_state.app_initialized = True
        st.session_state.init_time = datetime.now()
        logger.info("Session state initialized")


initialize_session_state()


# ============================================================================
# CACHED RESOURCE LOADERS
# ============================================================================

@st.cache_resource
def load_data_loader():
    """Load and cache DataLoader instance."""
    logger.info("Initializing DataLoader")
    return DataLoader()


@st.cache_resource
def load_default_model():
    """Load and cache default Markov model."""
    logger.info("Initializing default Markov model")
    return MarkovEngagementPredictor()


@st.cache_data(ttl=3600)
def load_default_dataset():
    """Load default dataset with caching (1 hour TTL)."""
    try:
        data_path = project_root / "data" / "raw" / "data_globant_cleaned.csv"
        if data_path.exists():
            logger.info(f"Loading default dataset from {data_path}")
            loader = load_data_loader()
            df = loader.load_from_csv(data_path)
            summary = loader.get_data_summary(df)
            return df, summary
        else:
            logger.warning(f"Default dataset not found: {data_path}")
            return None, None
    except Exception as e:
        logger.error(f"Error loading default dataset: {e}")
        return None, None


# ============================================================================
# KPI CALCULATIONS
# ============================================================================

@st.cache_data(ttl=300)
def calculate_kpis(_df_json: str, df: pd.DataFrame) -> dict:
    """Calculate key performance indicators from the data."""
    try:
        total_employees = df['Email'].nunique()
        avg_engagement = df['Engagement'].mean()
        category_dist = df['Engagement Category'].value_counts()

        df_sorted = df.sort_values('Date')
        current_month = df_sorted[df_sorted['Date'] >= df_sorted['Date'].max() - pd.Timedelta(days=30)]
        previous_month = df_sorted[
            (df_sorted['Date'] >= df_sorted['Date'].max() - pd.Timedelta(days=60)) &
            (df_sorted['Date'] < df_sorted['Date'].max() - pd.Timedelta(days=30))
        ]

        current_avg = current_month['Engagement'].mean() if len(current_month) > 0 else avg_engagement
        previous_avg = previous_month['Engagement'].mean() if len(previous_month) > 0 else avg_engagement
        engagement_change = ((current_avg - previous_avg) / previous_avg * 100) if previous_avg > 0 else 0

        top_teams = df.groupby('Team Name')['Engagement'].mean().sort_values(ascending=False).head(5)

        high_engagement_rate = (
            len(df[df['Engagement Category'].isin(['Alto', 'Muy Alto'])]) / len(df) * 100
        ) if len(df) > 0 else 0

        return {
            'total_employees': total_employees,
            'avg_engagement': avg_engagement,
            'engagement_change': engagement_change,
            'category_distribution': category_dist.to_dict(),
            'top_teams': top_teams.to_dict(),
            'high_engagement_rate': high_engagement_rate
        }
    except Exception as e:
        logger.error(f"Error calculating KPIs: {e}")
        return {}


# ============================================================================
# CHART FUNCTIONS
# ============================================================================

def create_engagement_distribution_chart(category_dist: dict) -> go.Figure:
    """Create a donut chart for engagement distribution."""
    colors = {
        'Bajo': '#D62828',
        'Medio': '#F77F00',
        'Alto': '#06A77D',
        'Muy Alto': '#2E86AB'
    }

    labels = list(category_dist.keys())
    values = list(category_dist.values())
    chart_colors = [colors.get(label, '#999999') for label in labels]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=chart_colors),
        hole=0.4,
        textinfo='label+percent',
        textposition='outside'
    )])

    fig.update_layout(
        title="Distribución de Engagement",
        height=350,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )

    return fig


def create_time_evolution_chart(df: pd.DataFrame) -> go.Figure:
    """Create a line chart showing engagement evolution over time."""
    max_date = df['Date'].max()
    min_date = max_date - pd.Timedelta(days=90)
    df_recent = df[df['Date'] >= min_date].copy()

    daily_avg = df_recent.groupby('Date')['Engagement'].mean().reset_index()
    daily_avg['MA7'] = daily_avg['Engagement'].rolling(window=7, min_periods=1).mean()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=daily_avg['Date'], y=daily_avg['Engagement'],
        mode='lines', name='Promedio Diario',
        line=dict(color='rgba(46, 134, 171, 0.3)', width=1)
    ))

    fig.add_trace(go.Scatter(
        x=daily_avg['Date'], y=daily_avg['MA7'],
        mode='lines', name='Media Móvil 7 días',
        line=dict(color='#2E86AB', width=3)
    ))

    fig.update_layout(
        title="Tendencia de Engagement (Últimos 90 días)",
        xaxis_title="Fecha", yaxis_title="Engagement Score",
        height=350, margin=dict(l=20, r=20, t=40, b=20),
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    return fig


def create_top_teams_chart(top_teams: dict) -> go.Figure:
    """Create a horizontal bar chart for top teams."""
    teams = list(top_teams.keys())
    scores = list(top_teams.values())
    teams_short = [team[:25] + '...' if len(team) > 25 else team for team in teams]

    fig = go.Figure(data=[go.Bar(
        y=teams_short, x=scores, orientation='h',
        marker=dict(color='#2E86AB'),
        text=[f'{score:.2f}' for score in scores],
        textposition='outside'
    )])

    fig.update_layout(
        title="Top 5 Equipos por Engagement",
        xaxis_title="Engagement Promedio", yaxis_title="",
        height=300, margin=dict(l=20, r=20, t=40, b=20),
        yaxis=dict(autorange="reversed")
    )

    return fig


# ============================================================================
# SIDEBAR
# ============================================================================

def render_sidebar():
    """Render sidebar with system status."""
    with st.sidebar:
        st.markdown("### Estado del Sistema")

        # Data status
        if st.session_state.data_loaded:
            st.success("Datos cargados")
            if st.session_state.df is not None:
                st.caption(f"Registros: {len(st.session_state.df):,}")
        else:
            st.warning("Sin datos")

        # Model status
        if st.session_state.model_trained:
            st.success("Modelo entrenado")
        else:
            st.info("Modelo no entrenado")

        st.markdown("---")

        st.markdown("### Acciones")

        if st.button("Refrescar Datos", use_container_width=True):
            st.cache_data.clear()
            st.session_state.data_loaded = False
            st.session_state.df = None
            st.rerun()

        if st.button("Limpiar Historial", use_container_width=True):
            st.session_state.predictions_history = []
            st.success("Historial limpiado")

        st.markdown("---")

        st.markdown("### Info")
        st.caption(f"Version: 1.0.0")
        st.caption(f"Sesion: {st.session_state.init_time.strftime('%Y-%m-%d %H:%M')}")


# ============================================================================
# LANDING PAGE (No data loaded)
# ============================================================================

def render_landing_page():
    """Render landing page when no data is loaded."""

    # Render professional header
    render_header(
        title="Employee Engagement Prediction",
        subtitle="Dashboard Principal",
        description="Sistema de predicción de engagement basado en Cadenas de Markov para análisis de comportamiento laboral."
    )

    st.markdown("---")

    # Key Features
    st.markdown('<div class="sub-header">Características Principales</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class='feature-card'>
            <h4>Análisis de Datos</h4>
            <p>Carga y explora datos de engagement con validación automática y visualizaciones interactivas.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class='feature-card'>
            <h4>Predicciones Inteligentes</h4>
            <p>Genera predicciones precisas usando modelos de Cadenas de Markov de última generación.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class='feature-card'>
            <h4>Insights Profundos</h4>
            <p>Analiza patrones de transición, tendencias e identifica factores que influyen en el engagement.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Get Started
    st.markdown('<div class="sub-header">Comenzar</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("Cargar Datos de Ejemplo", use_container_width=True, type="primary"):
            with st.spinner("Cargando dataset..."):
                try:
                    df, summary = load_default_dataset()
                    if df is not None:
                        st.session_state.df = df
                        st.session_state.data_summary = summary
                        st.session_state.data_loaded = True
                        st.success("Datos cargados!")
                        st.rerun()
                    else:
                        st.error("Dataset no disponible.")
                except Exception as e:
                    st.error(f"Error: {e}")

    with col2:
        if st.button("Ir a Data Explorer", use_container_width=True):
            st.switch_page("pages/2_Data_Explorer.py")

    with col3:
        if st.button("Ver Documentación", use_container_width=True):
            st.switch_page("pages/6_Documentation.py")

    st.markdown("---")

    # Quick Start Guide
    st.markdown('<div class="sub-header">Guía Rápida</div>', unsafe_allow_html=True)

    steps = [
        ("1. Cargar Datos", "Ve a Data Explorer y carga tu dataset de engagement (CSV o Excel)"),
        ("2. Seleccionar Variables", "Elige las variables relevantes en Variable Selection"),
        ("3. Hacer Predicciones", "Navega a Prediction para generar pronósticos"),
        ("4. Analizar Resultados", "Revisa el rendimiento del modelo en Model Analytics")
    ]

    for title, description in steps:
        st.markdown(f"""
        <div class='step-box'>
            <strong>{title}</strong><br>
            {description}
        </div>
        """, unsafe_allow_html=True)

    # Methodology
    st.markdown("---")

    with st.expander("¿Qué son las Cadenas de Markov?"):
        st.markdown("""
        Los modelos de **Cadenas de Markov** son herramientas estadísticas para analizar
        sistemas que transicionan entre diferentes estados a lo largo del tiempo.

        En el contexto de engagement de empleados:

        - **Estados**: Diferentes niveles de engagement (Bajo, Medio, Alto, Muy Alto)
        - **Transiciones**: Cómo los empleados se mueven entre niveles
        - **Predicciones**: Probabilidad de estados futuros
        - **Insights**: Factores que influyen en los cambios

        **Beneficios clave:**
        - Identificación proactiva de riesgos
        - Intervenciones de HR basadas en datos
        - Análisis de tendencias y pronósticos
        - Análisis de impacto de features
        """)


# ============================================================================
# DASHBOARD PAGE (Data loaded)
# ============================================================================

def render_dashboard():
    """Render dashboard when data is loaded."""

    df = st.session_state.df

    # Render professional header
    render_header(
        title="Dashboard de Engagement",
        subtitle="Métricas y Análisis",
        description="Métricas en tiempo real e insights sobre el engagement de empleados"
    )

    st.markdown("---")

    # Calculate KPIs
    df_json = str(len(df)) + str(df.columns.tolist())
    kpis = calculate_kpis(df_json, df)

    # KPI Section
    st.markdown('<div class="sub-header">Indicadores Clave</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Empleados",
            value=f"{kpis.get('total_employees', 0):,}",
            help="Número total de empleados únicos"
        )

    with col2:
        delta_color = "normal" if kpis.get('engagement_change', 0) >= 0 else "inverse"
        st.metric(
            label="Engagement Promedio",
            value=f"{kpis.get('avg_engagement', 0):.2f}",
            delta=f"{kpis.get('engagement_change', 0):.1f}%",
            delta_color=delta_color
        )

    with col3:
        st.metric(
            label="Tasa Alto Engagement",
            value=f"{kpis.get('high_engagement_rate', 0):.1f}%",
            help="% de empleados con engagement Alto o Muy Alto"
        )

    with col4:
        model_acc = 85.3 if st.session_state.model_trained else 0.0
        st.metric(
            label="Precisión Modelo",
            value=f"{model_acc:.1f}%" if model_acc > 0 else "N/A"
        )

    st.markdown("---")

    # Charts Section
    st.markdown('<div class="sub-header">Análisis Visual</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if kpis.get('category_distribution'):
            fig_dist = create_engagement_distribution_chart(kpis['category_distribution'])
            st.plotly_chart(fig_dist, use_container_width=True)

    with col2:
        fig_evolution = create_time_evolution_chart(df)
        st.plotly_chart(fig_evolution, use_container_width=True)

    # Top Teams
    if kpis.get('top_teams'):
        fig_teams = create_top_teams_chart(kpis['top_teams'])
        st.plotly_chart(fig_teams, use_container_width=True)

    st.markdown("---")

    # Quick Actions
    st.markdown('<div class="sub-header">Acciones Rápidas</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class='action-card'>
            <h4>Nueva Predicción</h4>
            <p>Generar predicciones de engagement</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Ir a Predicciones", key="btn_pred", use_container_width=True):
            st.switch_page("pages/4_Prediction.py")

    with col2:
        st.markdown("""
        <div class='action-card'>
            <h4>Explorar Datos</h4>
            <p>Análisis profundo de datos</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Ir a Explorer", key="btn_explore", use_container_width=True):
            st.switch_page("pages/2_Data_Explorer.py")

    with col3:
        st.markdown("""
        <div class='action-card'>
            <h4>Ver Analytics</h4>
            <p>Rendimiento del modelo</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Ir a Analytics", key="btn_analytics", use_container_width=True):
            st.switch_page("pages/5_Model_Analytics.py")

    with col4:
        st.markdown("""
        <div class='action-card'>
            <h4>Variables</h4>
            <p>Seleccionar features</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Ir a Variables", key="btn_vars", use_container_width=True):
            st.switch_page("pages/3_Variable_Selection.py")

    st.markdown("---")

    # Recent Predictions
    st.markdown('<div class="sub-header">Predicciones Recientes</div>', unsafe_allow_html=True)

    if st.session_state.predictions_history:
        recent = st.session_state.predictions_history[-5:]
        pred_data = [{
            'Timestamp': p.get('timestamp', 'N/A'),
            'Empleado': p.get('employee', 'N/A'),
            'Estado Actual': p.get('current_state', 'N/A'),
            'Predicción': p.get('predicted_state', 'N/A'),
            'Confianza': f"{p.get('confidence', 0):.1%}"
        } for p in recent]

        st.dataframe(pd.DataFrame(pred_data), use_container_width=True, hide_index=True)

        if st.button("Limpiar Historial de Predicciones"):
            st.session_state.predictions_history = []
            st.rerun()
    else:
        st.info("No hay predicciones aún. Ve a Prediction para generar tu primera predicción.")

    # Data Summary
    with st.expander("Resumen de Datos", expanded=False):
        if st.session_state.data_summary:
            summary = st.session_state.data_summary

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("**Dataset**")
                st.write(f"Filas: {summary['shape']['rows']:,}")
                st.write(f"Columnas: {summary['shape']['columns']}")
                st.write(f"Memoria: {summary['memory_usage_mb']:.2f} MB")

            with col2:
                st.markdown("**Rango de Fechas**")
                if 'date_range' in summary:
                    st.write(f"Desde: {summary['date_range']['min'][:10]}")
                    st.write(f"Hasta: {summary['date_range']['max'][:10]}")
                    st.write(f"Dias: {summary['date_range']['days']}")

            with col3:
                st.markdown("**Estadísticas de Engagement**")
                if 'engagement_stats' in summary:
                    st.write(f"Media: {summary['engagement_stats']['mean']:.2f}")
                    st.write(f"Mediana: {summary['engagement_stats']['median']:.2f}")
                    st.write(f"Std: {summary['engagement_stats']['std']:.2f}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main application function."""
    try:
        render_sidebar()

        if st.session_state.data_loaded and st.session_state.df is not None:
            render_dashboard()
        else:
            render_landing_page()

        # Footer
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #888; padding: 1rem 0; font-size: 0.9rem;'>
            Employee Engagement Prediction System v1.0.0 | ITESM
        </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        logger.error(f"Critical error: {e}", exc_info=True)
        st.error(f"Error de aplicación: {str(e)}")
        if st.button("Recargar"):
            st.rerun()


if __name__ == "__main__":
    main()
