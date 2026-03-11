"""
Variable Selection Page - Sistema de Predicción de Engagement

Esta es la página MÁS COMPLEJA del sistema. Permite:
- Exploración individual de variables con análisis estadístico
- Selección múltiple de variables con preview
- Análisis de combinaciones e interacciones
- Sugerencias automáticas basadas en importancia
- Matrices de transición condicionales
- Tests estadísticos (Chi-squared, ANOVA, Cramér's V)

Author: ITESM
Date: 2025-11-18
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
from scipy.stats import chi2_contingency, f_oneway
import warnings
warnings.filterwarnings('ignore')

# Add src to path
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from data import DataLoader, EngagementPreprocessor
from models import MarkovEngagementPredictor
from visualization import create_interactive_heatmap, apply_plotly_theme

# Import shared components
sys.path.insert(0, str(Path(__file__).parent.parent))
from components.header import render_header, render_sidebar_logos, get_global_css

# Page configuration
st.set_page_config(
    page_title="Variable Selection - Engagement Prediction",
    page_icon="public/img/tec.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Render sidebar with logos
with st.sidebar:
    render_sidebar_logos()

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'df' not in st.session_state:
    st.session_state.df = None
if 'selected_variables' not in st.session_state:
    st.session_state.selected_variables = {}
if 'variable_values' not in st.session_state:
    st.session_state.variable_values = {}


def load_default_dataset():
    """Load default dataset"""
    try:
        default_path = Path(__file__).parent.parent.parent / "data" / "raw" / "data_globant_cleaned.csv"
        loader = DataLoader()
        df = loader.load_from_csv(default_path)
        return df, None
    except Exception as e:
        return None, str(e)


def calculate_cramers_v(x, y):
    """Calculate Cramér's V statistic for categorical association"""
    confusion_matrix = pd.crosstab(x, y)
    chi2 = chi2_contingency(confusion_matrix)[0]
    n = confusion_matrix.sum().sum()
    min_dim = min(confusion_matrix.shape) - 1
    return np.sqrt(chi2 / (n * min_dim))


def chi_squared_test(var1, var2):
    """Perform Chi-squared test of independence"""
    contingency_table = pd.crosstab(var1, var2)
    chi2, p_value, dof, expected = chi2_contingency(contingency_table)
    return {
        'chi2': chi2,
        'p_value': p_value,
        'dof': dof,
        'cramers_v': calculate_cramers_v(var1, var2)
    }


def anova_test(groups, values):
    """Perform one-way ANOVA test"""
    group_data = [values[groups == group].dropna() for group in groups.unique()]
    # Filter out empty groups
    group_data = [g for g in group_data if len(g) > 0]
    if len(group_data) < 2:
        return None
    f_stat, p_value = f_oneway(*group_data)
    return {
        'f_statistic': f_stat,
        'p_value': p_value
    }


def calculate_transition_matrix(df, condition_col=None, condition_val=None):
    """Calculate transition matrix for engagement categories"""
    df_work = df.copy()

    # Apply condition if specified
    if condition_col and condition_val:
        df_work = df_work[df_work[condition_col] == condition_val]

    # Create transitions
    preprocessor = EngagementPreprocessor(verbose=False)
    transitions = preprocessor.create_transitions(df_work, min_transitions=1)

    if len(transitions) == 0:
        return None

    # Calculate transition matrix (values between 0-1, heatmap formats as %)
    transition_matrix = pd.crosstab(
        transitions['current_category'],
        transitions['next_category'],
        normalize='index'
    )

    # Ensure all categories are present
    categories = ['Bajo', 'Medio', 'Alto', 'Muy Alto']
    for cat in categories:
        if cat not in transition_matrix.index:
            transition_matrix.loc[cat] = 0
        if cat not in transition_matrix.columns:
            transition_matrix[cat] = 0

    transition_matrix = transition_matrix.reindex(index=categories, columns=categories, fill_value=0)

    return transition_matrix


def create_correlation_heatmap(df, variables):
    """Create correlation heatmap for selected variables"""
    # Encode categorical variables
    df_encoded = df.copy()
    for var in variables:
        if df_encoded[var].dtype == 'object':
            df_encoded[var] = pd.Categorical(df_encoded[var]).codes

    # Add engagement if not present
    if 'Engagement' not in variables:
        variables_with_eng = variables + ['Engagement']
    else:
        variables_with_eng = variables

    # Calculate correlation matrix
    corr_matrix = df_encoded[variables_with_eng].corr()

    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix.values.round(2),
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(title="Correlación")
    ))

    fig.update_layout(
        title="Matriz de Correlación de Variables",
        xaxis_title="Variable",
        yaxis_title="Variable",
        height=500
    )

    fig = apply_plotly_theme(fig)

    return fig


def calculate_feature_importance(df):
    """Calculate feature importance based on statistical tests"""
    categorical_vars = ['Position', 'Seniority', 'Location', 'Studio', 'Client', 'Project', 'Team Name']
    importance_scores = {}

    for var in categorical_vars:
        if var in df.columns:
            try:
                # Chi-squared test with Engagement Category
                if 'Engagement Category' in df.columns:
                    result = chi_squared_test(df[var].dropna(), df['Engagement Category'].dropna())
                    # Use Cramér's V as importance score
                    importance_scores[var] = result['cramers_v']
                else:
                    importance_scores[var] = 0
            except:
                importance_scores[var] = 0

    # Sort by importance
    importance_df = pd.DataFrame([
        {'Variable': k, 'Importance (Cramér\'s V)': v}
        for k, v in importance_scores.items()
    ]).sort_values('Importance (Cramér\'s V)', ascending=False)

    return importance_df


def analyze_interaction(df, var1, var2, val1, val2):
    """Analyze interaction between two variable values"""
    # Filter data
    df_comb = df[(df[var1] == val1) & (df[var2] == val2)]
    df_var1_only = df[(df[var1] == val1) & (df[var2] != val2)]
    df_var2_only = df[(df[var1] != val1) & (df[var2] == val2)]
    df_neither = df[(df[var1] != val1) & (df[var2] != val2)]

    results = {
        'combination': {
            'count': len(df_comb),
            'mean_engagement': df_comb['Engagement'].mean() if len(df_comb) > 0 else 0,
            'category_dist': df_comb['Engagement Category'].value_counts().to_dict() if len(df_comb) > 0 else {}
        },
        f'{var1}_only': {
            'count': len(df_var1_only),
            'mean_engagement': df_var1_only['Engagement'].mean() if len(df_var1_only) > 0 else 0,
        },
        f'{var2}_only': {
            'count': len(df_var2_only),
            'mean_engagement': df_var2_only['Engagement'].mean() if len(df_var2_only) > 0 else 0,
        },
        'neither': {
            'count': len(df_neither),
            'mean_engagement': df_neither['Engagement'].mean() if len(df_neither) > 0 else 0,
        }
    }

    return results


# ============================================================================
# MAIN APP
# ============================================================================

# Render professional header
render_header(
    title="Selección de Variables",
    subtitle="Variable Selection",
    description="Selecciona y analiza las variables más relevantes para el modelo de predicción de engagement."
)

# Additional CSS for this page
st.markdown("""
<style>
    .warning-box {
        background-color: #FFF4E5;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #F77F00;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #E8F8F5;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #06A77D;
        margin: 1rem 0;
    }
    .stat-significant {
        color: #06A77D;
        font-weight: bold;
    }
    .stat-not-significant {
        color: #D62828;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Load data
if not st.session_state.data_loaded:
    with st.spinner("Cargando dataset..."):
        df, error = load_default_dataset()
        if error:
            st.error(f"Error al cargar datos: {error}")
            st.stop()
        else:
            st.session_state.df = df
            st.session_state.data_loaded = True
            st.success(f"Dataset cargado: {len(df):,} registros")

df = st.session_state.df

# ============================================================================
# SIDEBAR - RESUMEN Y AYUDA
# ============================================================================

st.sidebar.markdown("### Resumen de Selección")

if st.session_state.selected_variables:
    st.sidebar.success(f"{len(st.session_state.selected_variables)} variable(s) seleccionada(s)")
    for var, values in st.session_state.selected_variables.items():
        if values:
            st.sidebar.info(f"**{var}:** {len(values)} valor(es)")
else:
    st.sidebar.info("No hay variables seleccionadas")

if st.sidebar.button("Limpiar Selección", use_container_width=True):
    st.session_state.selected_variables = {}
    st.session_state.variable_values = {}
    st.rerun()

st.sidebar.markdown("---")

with st.sidebar.expander("Ayuda"):
    st.markdown("""
    **Cómo usar esta página:**

    1. **Exploración Individual:** Analiza una variable a la vez
    2. **Selección Múltiple:** Combina variables para predicción
    3. **Análisis de Interacciones:** Ve cómo se combinan
    4. **Sugerencias Automáticas:** Top variables por importancia

    **Métricas estadísticas:**
    - **p-value < 0.05:** Significativo
    - **Cramér's V:** Fuerza de asociación (0-1)
    - **Chi-squared:** Test de independencia
    - **ANOVA:** Diferencias entre grupos
    """)

# ============================================================================
# TABS PRINCIPALES
# ============================================================================

tab1, tab2, tab3 = st.tabs([
    "Exploración Individual",
    "Selección Múltiple",
    "Análisis de Combinaciones"
])

# ============================================================================
# TAB 1: EXPLORACIÓN INDIVIDUAL
# ============================================================================

with tab1:
    st.markdown('<div class="sub-header">Exploración de Variables Individual</div>', unsafe_allow_html=True)

    # Variable selector
    categorical_vars = ['Position', 'Seniority', 'Location', 'Studio', 'Client', 'Project', 'Team Name']
    available_vars = [var for var in categorical_vars if var in df.columns]

    selected_var = st.selectbox(
        "Selecciona una variable para analizar:",
        options=available_vars,
        index=0 if available_vars else None
    )

    if selected_var:

        st.markdown(f'<div class="section-header">Análisis de: {selected_var}</div>', unsafe_allow_html=True)

        # 1. VALORES ÚNICOS CON FRECUENCIAS
        st.markdown("**Valores Únicos y Frecuencias**")

        value_counts = df[selected_var].value_counts()
        value_df = pd.DataFrame({
            'Valor': value_counts.index,
            'Count': value_counts.values,
            'Porcentaje': (value_counts.values / len(df) * 100).round(2)
        })

        # Show table
        st.dataframe(
            value_df.style.background_gradient(subset=['Count'], cmap='Blues'),
            use_container_width=True,
            height=300
        )
        st.caption("Frecuencia de cada valor. Valores con pocos registros pueden dar predicciones menos confiables.")

        # 2. GRÁFICO DE DISTRIBUCIÓN
        st.markdown("**Distribución Visual**")

        col1, col2 = st.columns(2)

        with col1:
            # Bar chart
            fig_bar = go.Figure(data=[
                go.Bar(
                    x=value_counts.index,
                    y=value_counts.values,
                    marker_color='#2E86AB',
                    text=value_counts.values,
                    textposition='auto'
                )
            ])
            fig_bar.update_layout(
                title=f"Distribución de {selected_var}",
                xaxis_title=selected_var,
                yaxis_title="Frecuencia",
                height=400
            )
            fig_bar = apply_plotly_theme(fig_bar)
            st.plotly_chart(fig_bar, use_container_width=True)
            st.caption("Cantidad de registros por valor. Barras altas indican valores más representados.")

        with col2:
            # Pie chart
            fig_pie = go.Figure(data=[go.Pie(
                labels=value_counts.index[:10],  # Top 10
                values=value_counts.values[:10],
                hole=0.3
            )])
            fig_pie.update_layout(
                title=f"Proporción de {selected_var} (Top 10)",
                height=400
            )
            fig_pie = apply_plotly_theme(fig_pie)
            st.plotly_chart(fig_pie, use_container_width=True)
            st.caption("Proporción relativa de los 10 valores más frecuentes.")

        # 3. CORRELACIÓN CON ENGAGEMENT
        st.markdown("**Correlación con Engagement**")

        col1, col2 = st.columns(2)

        with col1:
            # Boxplot by category
            fig_box = go.Figure()

            for val in value_counts.index[:10]:  # Top 10 values
                val_data = df[df[selected_var] == val]['Engagement']
                fig_box.add_trace(go.Box(
                    y=val_data,
                    name=str(val),
                    boxmean='sd'
                ))

            fig_box.update_layout(
                title=f"Engagement por {selected_var}",
                yaxis_title="Engagement Score",
                xaxis_title=selected_var,
                height=400,
                showlegend=False
            )
            fig_box = apply_plotly_theme(fig_box)
            st.plotly_chart(fig_box, use_container_width=True)
            st.caption("Compara engagement entre valores. Cajas más altas = mayor engagement promedio.")

        with col2:
            # Statistical summary
            eng_by_var = df.groupby(selected_var)['Engagement'].agg(['mean', 'std', 'count']).round(2)
            eng_by_var = eng_by_var.sort_values('mean', ascending=False).head(10)

            st.markdown("**Top 10 por Engagement Medio:**")
            st.dataframe(
                eng_by_var.style.background_gradient(subset=['mean'], cmap='RdYlGn'),
                use_container_width=True
            )
            st.caption("Valores ordenados por engagement. std=variabilidad, count=registros disponibles.")

        # 4. MATRIZ DE TRANSICIÓN ESPECÍFICA
        st.markdown("**Matrices de Transición Condicionales**")

        st.info("Compara cómo cambia la matriz de transición para valores específicos de la variable")

        # Select a value to analyze
        selected_value = st.selectbox(
            f"Selecciona un valor de {selected_var}:",
            options=value_counts.index[:20],  # Top 20
            key=f"trans_value_{selected_var}"
        )

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**Matriz Global (todos los datos)**")
            global_matrix = calculate_transition_matrix(df)
            if global_matrix is not None:
                fig_global = create_interactive_heatmap(
                    global_matrix.values,
                    global_matrix.index.tolist(),
                    title="Matriz de Transición Global"
                )
                st.plotly_chart(fig_global, use_container_width=True)
                st.caption("Probabilidades de transición usando todos los datos. Filas suman 100%.")
            else:
                st.warning("No hay suficientes transiciones para calcular la matriz")

        with col2:
            st.markdown(f"**Matriz Condicional: {selected_var} = {selected_value}**")
            conditional_matrix = calculate_transition_matrix(df, selected_var, selected_value)
            if conditional_matrix is not None:
                fig_cond = create_interactive_heatmap(
                    conditional_matrix.values,
                    conditional_matrix.index.tolist(),
                    title=f"Matriz: {selected_var}={selected_value}"
                )
                st.plotly_chart(fig_cond, use_container_width=True)
                st.caption("Probabilidades solo para este valor. Compara con la global para ver diferencias.")

                # Show differences
                if global_matrix is not None:
                    diff_matrix = (conditional_matrix - global_matrix) * 100  # Convert to percentage points
                    st.markdown("**Diferencias (% puntos):**")
                    st.dataframe(
                        diff_matrix.style.format("{:.1f}").background_gradient(cmap='RdYlGn', vmin=-20, vmax=20),
                        use_container_width=True
                    )
                    st.caption("Verde=mayor probabilidad que global, Rojo=menor. Valores significativos sugieren variable relevante.")
            else:
                st.warning("No hay suficientes transiciones para esta condición")

        # 5. TEST ESTADÍSTICO
        st.markdown("**Test Estadístico de Significancia**")

        # Chi-squared test with Engagement Category
        if 'Engagement Category' in df.columns:
            test_result = chi_squared_test(
                df[selected_var].dropna(),
                df['Engagement Category'].dropna()
            )

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Chi-squared", f"{test_result['chi2']:.2f}")

            with col2:
                st.metric("p-value", f"{test_result['p_value']:.4f}")

            with col3:
                st.metric("Cramér's V", f"{test_result['cramers_v']:.3f}")

            with col4:
                if test_result['p_value'] < 0.05:
                    st.markdown('<div class="stat-significant">Significativo</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="stat-not-significant">No Significativo</div>', unsafe_allow_html=True)

            # Interpretation
            if test_result['p_value'] < 0.05:
                st.success(f"""
                **Interpretación:** Existe una relación estadísticamente significativa entre {selected_var}
                y Engagement Category (p < 0.05). La fuerza de la asociación es
                {'fuerte' if test_result['cramers_v'] > 0.3 else 'moderada' if test_result['cramers_v'] > 0.1 else 'débil'}
                (V = {test_result['cramers_v']:.3f}).
                """)
            else:
                st.warning(f"""
                **Interpretación:** No se encontró una relación estadísticamente significativa entre {selected_var}
                y Engagement Category (p ≥ 0.05).
                """)

        # ANOVA test
        anova_result = anova_test(df[selected_var], df['Engagement'])
        if anova_result:
            st.markdown("**ANOVA Test (Engagement numérico):**")
            col1, col2 = st.columns(2)

            with col1:
                st.metric("F-statistic", f"{anova_result['f_statistic']:.2f}")

            with col2:
                st.metric("p-value", f"{anova_result['p_value']:.4f}")

            if anova_result['p_value'] < 0.05:
                st.success("""
                Las medias de engagement difieren significativamente entre grupos (p < 0.05)
                """)

# ============================================================================
# TAB 2: SELECCIÓN MÚLTIPLE
# ============================================================================

with tab2:
    st.markdown('<div class="sub-header">Selección de Variables para el Modelo</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
    <b>Selecciona las variables</b> que el modelo usará para crear matrices de transición condicionales.<br>
    Los <b>valores específicos son opcionales</b>: si no seleccionas ninguno, se usarán todos los valores de esa variable.
    </div>
    """, unsafe_allow_html=True)

    # Organize variables by category
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Variables de Empleado**")

        emp_vars = ['Position', 'Seniority', 'Location']
        for var in emp_vars:
            if var in df.columns:
                if st.checkbox(f"{var}", key=f"select_{var}"):
                    # Variable is selected - store it (with or without specific values)
                    values = sorted(df[var].dropna().unique())

                    # Optional: filter by specific values
                    with st.expander(f"Filtrar por valores específicos (opcional)", expanded=False):
                        selected_vals = st.multiselect(
                            f"Valores de {var}:",
                            options=values,
                            default=None,
                            key=f"values_{var}",
                            help="Dejar vacío para usar TODOS los valores"
                        )

                    # Store variable (empty list means all values)
                    st.session_state.selected_variables[var] = selected_vals if selected_vals else []

                    if selected_vals:
                        st.caption(f"{len(selected_vals)} valor(es) específico(s)")
                    else:
                        st.caption("Usando todos los valores")
                else:
                    # Remove if unchecked
                    if var in st.session_state.selected_variables:
                        del st.session_state.selected_variables[var]

    with col2:
        st.markdown("**Variables de Organización**")

        org_vars = ['Studio', 'Client', 'Project', 'Team Name']
        for var in org_vars:
            if var in df.columns:
                if st.checkbox(f"{var}", key=f"select_{var}"):
                    values = sorted(df[var].dropna().unique())

                    # Limit display for variables with many values
                    display_values = values
                    if len(values) > 50:
                        value_counts = df[var].value_counts()
                        display_values = value_counts.index[:50].tolist()

                    with st.expander(f"Filtrar por valores específicos (opcional)", expanded=False):
                        if len(values) > 50:
                            st.caption(f"{var} tiene {len(values)} valores. Mostrando top 50.")
                        selected_vals = st.multiselect(
                            f"Valores de {var}:",
                            options=display_values,
                            default=None,
                            key=f"values_{var}",
                            help="Dejar vacío para usar TODOS los valores"
                        )

                    st.session_state.selected_variables[var] = selected_vals if selected_vals else []

                    if selected_vals:
                        st.caption(f"{len(selected_vals)} valor(es) específico(s)")
                    else:
                        st.caption("Usando todos los valores")
                else:
                    if var in st.session_state.selected_variables:
                        del st.session_state.selected_variables[var]

    # Temporal variables (if available)
    st.markdown("**Variables Temporales**")
    col1, col2, col3 = st.columns(3)

    temporal_vars = ['Year', 'Month']
    for i, var in enumerate(temporal_vars):
        if var in df.columns:
            with [col1, col2, col3][i]:
                if st.checkbox(f"{var}", key=f"select_{var}"):
                    values = sorted(df[var].dropna().unique())

                    with st.expander(f"Filtrar valores (opcional)", expanded=False):
                        selected_vals = st.multiselect(
                            f"Valores de {var}:",
                            options=values,
                            default=None,
                            key=f"values_{var}",
                            help="Dejar vacío para usar TODOS los valores"
                        )

                    st.session_state.selected_variables[var] = selected_vals if selected_vals else []

                    if selected_vals:
                        st.caption(f"{len(selected_vals)} valor(es)")
                    else:
                        st.caption("Todos los valores")
                else:
                    if var in st.session_state.selected_variables:
                        del st.session_state.selected_variables[var]

    # PANEL DE PREVIEW
    st.markdown("---")
    st.markdown('<div class="section-header">Preview de Selección</div>', unsafe_allow_html=True)

    # Get selected variable names (regardless of specific values)
    selected_var_names = list(st.session_state.selected_variables.keys())

    if selected_var_names:
        # Filter data based on selection (only if specific values are selected)
        df_filtered = df.copy()
        has_specific_filters = False

        for var, values in st.session_state.selected_variables.items():
            if values:  # Only filter if specific values were selected
                df_filtered = df_filtered[df_filtered[var].isin(values)]
                has_specific_filters = True

        num_records = len(df_filtered)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Registros para entrenar", f"{num_records:,}")

        with col2:
            percentage = (num_records / len(df)) * 100
            st.metric("Porcentaje del dataset", f"{percentage:.2f}%")

        with col3:
            if 'Engagement' in df_filtered.columns:
                st.metric("Engagement Medio", f"{df_filtered['Engagement'].mean():.2f}")

        # Warning if too few records
        if num_records < 50:
            st.markdown("""
            <div class="warning-box">
            <b>Advertencia:</b> Pocos registros para entrenar ({} registros).
            Considera usar menos filtros específicos para tener más datos.
            </div>
            """.format(num_records), unsafe_allow_html=True)

        # Show selection summary
        st.markdown("**Resumen de Selección:**")
        summary_data = []
        for var, vals in st.session_state.selected_variables.items():
            if vals:
                vals_str = ', '.join(map(str, vals[:3])) + ('...' if len(vals) > 3 else '')
                summary_data.append({'Variable': var, 'Filtro': vals_str, 'Tipo': 'Valores específicos'})
            else:
                unique_count = df[var].nunique()
                summary_data.append({'Variable': var, 'Filtro': f'Todos ({unique_count} valores)', 'Tipo': 'General'})

        combo_df = pd.DataFrame(summary_data)
        st.dataframe(combo_df, use_container_width=True, hide_index=True)
        st.caption("Variables seleccionadas para el modelo. 'General' usa todos los valores, 'Específicos' filtra datos.")

        # Engagement distribution for selection
        if 'Engagement Category' in df_filtered.columns:
            st.markdown("**Distribución de Engagement en la selección:**")

            cat_dist = df_filtered['Engagement Category'].value_counts()
            colors_map = {'Bajo': '#D62828', 'Medio': '#F77F00', 'Alto': '#06A77D', 'Muy Alto': '#2E86AB'}
            colors = [colors_map.get(cat, '#2E86AB') for cat in cat_dist.index]

            fig = go.Figure(data=[
                go.Bar(x=cat_dist.index, y=cat_dist.values, marker_color=colors)
            ])
            fig.update_layout(
                xaxis_title="Categoría",
                yaxis_title="Count",
                height=300
            )
            fig = apply_plotly_theme(fig)
            st.plotly_chart(fig, use_container_width=True)
            st.caption("Distribución de engagement con los filtros aplicados. Verifica que haya datos en todas las categorías.")

        # SAVE BUTTON AND TRAIN MODEL
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("Guardar y Entrenar Modelo", type="primary", use_container_width=True):
                st.session_state.variable_values = st.session_state.selected_variables.copy()

                # Train the model with selected variables
                with st.spinner("Entrenando modelo Markov..."):
                    try:
                        # Get the dataframe
                        if 'df' in st.session_state and st.session_state.df is not None:
                            df_train = st.session_state.df.copy()
                        else:
                            df_train = df.copy()

                        # Apply specific value filters if any
                        filters_applied = []
                        for var, values in st.session_state.selected_variables.items():
                            if values:  # If specific values were selected, filter the data
                                df_train = df_train[df_train[var].isin(values)]
                                filters_applied.append(f"{var}: {', '.join(map(str, values[:3]))}")

                        # Get list of variable names for conditional matrices
                        selected_features = list(st.session_state.selected_variables.keys())

                        # Create preprocessor and transitions
                        preprocessor = EngagementPreprocessor()

                        # Create transitions with selected features
                        transitions_df = preprocessor.create_transitions(
                            df_train,
                            min_transitions=2,
                            include_features=selected_features if selected_features else None
                        )

                        # Rename columns for the model
                        transitions_df = transitions_df.rename(columns={
                            'current_category': 'current_state',
                            'next_category': 'next_state'
                        })

                        # Create and train the predictor
                        predictor = MarkovEngagementPredictor()
                        predictor.fit(transitions_df, features=selected_features if selected_features else None)

                        # Save to session state
                        st.session_state.predictor = predictor
                        st.session_state.model_trained = True
                        st.session_state.transitions_df = transitions_df
                        st.session_state.selected_features = selected_features

                        st.success(f"Modelo entrenado exitosamente con {len(transitions_df):,} transiciones!")
                        if selected_features:
                            st.info(f"Variables para matrices condicionales: {', '.join(selected_features)}")
                        if filters_applied:
                            st.info(f"Filtros aplicados: {'; '.join(filters_applied)}")
                        elif selected_features:
                            st.info("Usando todos los valores de cada variable (sin filtros)")
                    except Exception as e:
                        st.error(f"Error al entrenar el modelo: {str(e)}")
                        st.session_state.model_trained = False

        with col2:
            if st.button("Limpiar Todo", use_container_width=True):
                st.session_state.selected_variables = {}
                st.session_state.variable_values = {}
                st.rerun()

    else:
        st.info("Selecciona variables arriba para ver el preview")

# ============================================================================
# TAB 3: ANÁLISIS DE COMBINACIONES
# ============================================================================

with tab3:
    st.markdown('<div class="sub-header">Análisis de Combinaciones e Interacciones</div>', unsafe_allow_html=True)

    # Sugerencias automáticas
    st.markdown("**Sugerencias Automáticas**")

    with st.spinner("Calculando importancia de variables..."):
        importance_df = calculate_feature_importance(df)

    st.markdown("**Top Variables por Importancia Estadística:**")

    # Show top 5
    top_vars = importance_df.head(5)

    col1, col2 = st.columns([2, 1])

    with col1:
        fig_importance = go.Figure(data=[
            go.Bar(
                y=top_vars['Variable'],
                x=top_vars['Importance (Cramér\'s V)'],
                orientation='h',
                marker_color='#2E86AB',
                text=top_vars['Importance (Cramér\'s V)'].round(3),
                textposition='auto'
            )
        ])
        fig_importance.update_layout(
            title="Top 5 Variables Más Relevantes",
            xaxis_title="Cramér's V (fuerza de asociación)",
            yaxis_title="Variable",
            height=300
        )
        fig_importance = apply_plotly_theme(fig_importance)
        st.plotly_chart(fig_importance, use_container_width=True)
        st.caption("Cramér's V mide asociación con engagement. Mayor valor = variable más influyente.")

    with col2:
        st.dataframe(
            importance_df.style.background_gradient(subset=['Importance (Cramér\'s V)'], cmap='Greens'),
            use_container_width=True,
            height=300
        )
        st.caption("Ranking completo. Valores >0.1 indican asociación moderada, >0.3 fuerte.")

    # Correlación entre variables seleccionadas
    if st.session_state.selected_variables and len(st.session_state.selected_variables) >= 2:
        st.markdown("---")
        st.markdown("**Heatmap de Correlaciones Cruzadas**")

        selected_vars_list = list(st.session_state.selected_variables.keys())
        fig_corr = create_correlation_heatmap(df, selected_vars_list)
        st.plotly_chart(fig_corr, use_container_width=True)
        st.caption("Correlación entre variables seleccionadas. Evita variables muy correlacionadas (>0.7) para reducir redundancia.")

    # Análisis de interacciones
    st.markdown("---")
    st.markdown("**Análisis de Interacciones**")

    st.info("Analiza cómo la combinación de dos variables afecta el engagement")

    col1, col2 = st.columns(2)

    with col1:
        var1 = st.selectbox(
            "Primera Variable:",
            options=available_vars,
            key="interaction_var1"
        )

    with col2:
        var2 = st.selectbox(
            "Segunda Variable:",
            options=[v for v in available_vars if v != var1],
            key="interaction_var2"
        )

    if var1 and var2:
        col1, col2 = st.columns(2)

        with col1:
            values1 = df[var1].value_counts().index[:10]
            val1 = st.selectbox(f"Valor de {var1}:", options=values1)

        with col2:
            values2 = df[var2].value_counts().index[:10]
            val2 = st.selectbox(f"Valor de {var2}:", options=values2)

        if st.button("Analizar Interacción", type="primary"):
            with st.spinner("Analizando interacción..."):
                interaction_results = analyze_interaction(df, var1, var2, val1, val2)

                st.markdown("**Resultados del Análisis:**")

                # Create comparison table
                comparison_df = pd.DataFrame([
                    {
                        'Condición': f'{var1}={val1} + {var2}={val2}',
                        'Registros': interaction_results['combination']['count'],
                        'Engagement Medio': f"{interaction_results['combination']['mean_engagement']:.2f}"
                    },
                    {
                        'Condición': f'Solo {var1}={val1}',
                        'Registros': interaction_results[f'{var1}_only']['count'],
                        'Engagement Medio': f"{interaction_results[f'{var1}_only']['mean_engagement']:.2f}"
                    },
                    {
                        'Condición': f'Solo {var2}={val2}',
                        'Registros': interaction_results[f'{var2}_only']['count'],
                        'Engagement Medio': f"{interaction_results[f'{var2}_only']['mean_engagement']:.2f}"
                    },
                    {
                        'Condición': 'Ninguno',
                        'Registros': interaction_results['neither']['count'],
                        'Engagement Medio': f"{interaction_results['neither']['mean_engagement']:.2f}"
                    }
                ])

                st.dataframe(comparison_df, use_container_width=True, hide_index=True)
                st.caption("Compara engagement medio entre combinaciones. Diferencias grandes sugieren efecto de interacción.")

                # Visualize
                fig_interaction = go.Figure(data=[
                    go.Bar(
                        x=comparison_df['Condición'],
                        y=comparison_df['Registros'],
                        name='Registros',
                        marker_color='#2E86AB'
                    )
                ])

                fig_interaction.update_layout(
                    title="Comparación de Interacciones",
                    xaxis_title="Condición",
                    yaxis_title="Número de Registros",
                    height=400
                )
                fig_interaction = apply_plotly_theme(fig_interaction)
                st.plotly_chart(fig_interaction, use_container_width=True)
                st.caption("Cantidad de registros por condición. Pocas observaciones = menor confiabilidad estadística.")

                # Show category distribution for combination
                if interaction_results['combination']['category_dist']:
                    st.markdown(f"**Distribución de Categorías para {var1}={val1} + {var2}={val2}:**")

                    cat_dist = interaction_results['combination']['category_dist']
                    colors_map = {'Bajo': '#D62828', 'Medio': '#F77F00', 'Alto': '#06A77D', 'Muy Alto': '#2E86AB'}

                    fig_cat = go.Figure(data=[go.Pie(
                        labels=list(cat_dist.keys()),
                        values=list(cat_dist.values()),
                        marker=dict(colors=[colors_map.get(k, '#2E86AB') for k in cat_dist.keys()])
                    )])

                    fig_cat.update_layout(height=300)
                    fig_cat = apply_plotly_theme(fig_cat)
                    st.plotly_chart(fig_cat, use_container_width=True)
                    st.caption("Distribución de engagement para esta combinación específica de valores.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
    Variable Selection | Engagement Prediction System | ITESM
</div>
""", unsafe_allow_html=True)
