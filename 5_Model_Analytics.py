"""
Data Explorer Page - Sistema de Predicción de Engagement

Esta página permite explorar y analizar el dataset de engagement con funcionalidad completa:
- Upload de datos con validación
- Estadísticas descriptivas
- Filtros dinámicos
- Visualización de distribuciones
- Análisis de calidad de datos
- Exportación de datos filtrados

Author: ITESM
Date: 2025-11-18
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io

# Add src to path
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from data import DataLoader, EngagementPreprocessor
from visualization import (
    plot_engagement_distribution,
    plot_temporal_evolution,
    create_interactive_heatmap,
    create_engagement_evolution_plot,
    create_interactive_violin_plot,
    apply_plotly_theme
)

# Import shared components
sys.path.insert(0, str(Path(__file__).parent.parent))
from components.header import render_header, render_sidebar_logos, get_global_css

# Page configuration
st.set_page_config(
    page_title="Data Explorer - Engagement Prediction",
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
if 'df_filtered' not in st.session_state:
    st.session_state.df_filtered = None
if 'filters_applied' not in st.session_state:
    st.session_state.filters_applied = {}


def load_default_dataset():
    """Load default dataset"""
    try:
        default_path = Path(__file__).parent.parent.parent / "data" / "raw" / "data_globant_cleaned.csv"
        loader = DataLoader()
        df = loader.load_from_csv(default_path)
        return df, None
    except Exception as e:
        return None, str(e)


def load_uploaded_file(uploaded_file):
    """Load uploaded file"""
    try:
        loader = DataLoader()
        df = loader.load_from_upload(uploaded_file)
        return df, None
    except Exception as e:
        return None, str(e)


def get_data_summary(df):
    """Generate comprehensive data summary"""
    loader = DataLoader()
    return loader.get_data_summary(df)


def get_quality_report(df):
    """Generate data quality report"""
    loader = DataLoader()
    return loader.detect_data_quality_issues(df)


def apply_filters(df, filters):
    """Apply filters to dataframe"""
    df_filtered = df.copy()

    # Date filter
    if 'date_range' in filters and filters['date_range']:
        start_date, end_date = filters['date_range']
        df_filtered = df_filtered[
            (df_filtered['Date'] >= pd.Timestamp(start_date)) &
            (df_filtered['Date'] <= pd.Timestamp(end_date))
        ]

    # Categorical filters
    for col in ['Position', 'Seniority', 'Studio', 'Location', 'Engagement Category']:
        if col in filters and filters[col]:
            df_filtered = df_filtered[df_filtered[col].isin(filters[col])]

    return df_filtered


def create_distribution_plots(df):
    """Create distribution visualizations"""

    # Engagement distribution
    fig_eng = go.Figure()

    fig_eng.add_trace(go.Histogram(
        x=df['Engagement'],
        nbinsx=30,
        name='Engagement',
        marker_color='#2E86AB',
        opacity=0.7
    ))

    fig_eng.update_layout(
        title="Distribución de Engagement",
        xaxis_title="Engagement Score",
        yaxis_title="Frecuencia",
        showlegend=False,
        height=400
    )
    fig_eng = apply_plotly_theme(fig_eng)

    # Boxplot
    fig_box = go.Figure()

    fig_box.add_trace(go.Box(
        y=df['Engagement'],
        name='Engagement',
        marker_color='#A23B72',
        boxmean='sd'
    ))

    fig_box.update_layout(
        title="Boxplot de Engagement",
        yaxis_title="Engagement Score",
        showlegend=False,
        height=400
    )
    fig_box = apply_plotly_theme(fig_box)

    return fig_eng, fig_box


def create_category_distributions(df):
    """Create category distribution plots"""

    # Position distribution
    pos_counts = df['Position'].value_counts()
    fig_pos = go.Figure(data=[
        go.Bar(x=pos_counts.index, y=pos_counts.values, marker_color='#06A77D')
    ])
    fig_pos.update_layout(
        title="Distribución por Posición",
        xaxis_title="Posición",
        yaxis_title="Count",
        height=400
    )
    fig_pos = apply_plotly_theme(fig_pos)

    # Seniority distribution
    sen_counts = df['Seniority'].value_counts()
    fig_sen = go.Figure(data=[
        go.Bar(x=sen_counts.index, y=sen_counts.values, marker_color='#F77F00')
    ])
    fig_sen.update_layout(
        title="Distribución por Seniority",
        xaxis_title="Seniority",
        yaxis_title="Count",
        height=400
    )
    fig_sen = apply_plotly_theme(fig_sen)

    # Studio distribution
    studio_counts = df['Studio'].value_counts().head(10)
    fig_studio = go.Figure(data=[
        go.Bar(x=studio_counts.values, y=studio_counts.index,
               orientation='h', marker_color='#2E86AB')
    ])
    fig_studio.update_layout(
        title="Top 10 Studios",
        xaxis_title="Count",
        yaxis_title="Studio",
        height=400
    )
    fig_studio = apply_plotly_theme(fig_studio)

    # Engagement Category distribution
    cat_counts = df['Engagement Category'].value_counts()
    colors_map = {'Bajo': '#D62828', 'Medio': '#F77F00', 'Alto': '#06A77D', 'Muy Alto': '#2E86AB'}
    colors = [colors_map.get(cat, '#2E86AB') for cat in cat_counts.index]

    fig_cat = go.Figure(data=[
        go.Bar(x=cat_counts.index, y=cat_counts.values, marker_color=colors)
    ])
    fig_cat.update_layout(
        title="Distribución por Categoría de Engagement",
        xaxis_title="Categoría",
        yaxis_title="Count",
        height=400
    )
    fig_cat = apply_plotly_theme(fig_cat)

    return fig_pos, fig_sen, fig_studio, fig_cat


def create_temporal_plot(df):
    """Create temporal evolution plot"""

    # Group by date and calculate mean engagement
    df_temporal = df.groupby('Date')['Engagement'].agg(['mean', 'std', 'count']).reset_index()

    fig = go.Figure()

    # Add mean line
    fig.add_trace(go.Scatter(
        x=df_temporal['Date'],
        y=df_temporal['mean'],
        mode='lines',
        name='Mean Engagement',
        line=dict(color='#2E86AB', width=2)
    ))

    # Add confidence interval
    fig.add_trace(go.Scatter(
        x=df_temporal['Date'].tolist() + df_temporal['Date'].tolist()[::-1],
        y=(df_temporal['mean'] + df_temporal['std']).tolist() +
          (df_temporal['mean'] - df_temporal['std']).tolist()[::-1],
        fill='toself',
        fillcolor='rgba(46, 134, 171, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name='±1 Std Dev',
        showlegend=True
    ))

    fig.update_layout(
        title="Evolución Temporal del Engagement",
        xaxis_title="Fecha",
        yaxis_title="Engagement Score",
        height=500,
        hovermode='x unified'
    )
    fig = apply_plotly_theme(fig)

    return fig


def create_quality_visualizations(quality_report):
    """Create quality visualization plots"""

    # Missing values chart
    missing = quality_report.get('missing_values', {})
    if missing:
        df_missing = pd.DataFrame([
            {'Column': col, 'Count': info['count'], 'Percentage': info['percentage']}
            for col, info in missing.items()
        ]).sort_values('Percentage', ascending=True)

        fig_missing = go.Figure(data=[
            go.Bar(
                x=df_missing['Percentage'],
                y=df_missing['Column'],
                orientation='h',
                marker_color='#F77F00',
                text=df_missing['Percentage'].apply(lambda x: f"{x:.1f}%"),
                textposition='auto'
            )
        ])

        fig_missing.update_layout(
            title="Valores Faltantes por Columna",
            xaxis_title="Porcentaje (%)",
            yaxis_title="Columna",
            height=400
        )
        fig_missing = apply_plotly_theme(fig_missing)

        return fig_missing

    return None


def export_data(df, format='csv'):
    """Export dataframe to downloadable file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if format == 'csv':
        output = io.BytesIO()
        df.to_csv(output, index=False, encoding='utf-8-sig')
        output.seek(0)
        filename = f"engagement_data_{timestamp}.csv"
        mime = 'text/csv'
    else:  # excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Data')
        output.seek(0)
        filename = f"engagement_data_{timestamp}.xlsx"
        mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    return output, filename, mime


# ============================================================================
# MAIN APP
# ============================================================================

# Render professional header
render_header(
    title="Explorador de Datos",
    subtitle="Data Explorer",
    description="Analiza y explora el dataset de engagement con filtros dinámicos y visualizaciones interactivas."
)

# ============================================================================
# A) UPLOAD DE DATOS
# ============================================================================

st.markdown('<div class="sub-header">Carga de Datos</div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    uploaded_file = st.file_uploader(
        "Arrastra y suelta tu archivo CSV o Excel aquí",
        type=['csv', 'xlsx', 'xls'],
        help="Formatos soportados: CSV, Excel (.xlsx, .xls)"
    )

with col2:
    use_default = st.checkbox("Usar dataset por defecto", value=True)

    if st.button("Cargar/Procesar Datos", type="primary"):
        with st.spinner("Cargando datos..."):
            if use_default or uploaded_file is None:
                df, error = load_default_dataset()
            else:
                df, error = load_uploaded_file(uploaded_file)

            if error:
                st.error(f"Error al cargar datos: {error}")
            else:
                st.session_state.df = df
                st.session_state.df_filtered = df.copy()
                st.session_state.data_loaded = True
                st.session_state.filters_applied = {}
                st.success(f"Datos cargados exitosamente: {len(df):,} registros")

# Preview of loaded data
if st.session_state.data_loaded:
    with st.expander("Preview de los datos (primeras 10 filas)", expanded=False):
        st.dataframe(
            st.session_state.df.head(10),
            use_container_width=True,
            height=300
        )

# ============================================================================
# SIDEBAR - FILTROS DINÁMICOS
# ============================================================================

if st.session_state.data_loaded:
    st.sidebar.markdown("### Filtros Dinámicos")

    df = st.session_state.df

    # Date range filter
    st.sidebar.markdown("#### Rango de Fechas")
    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()

    date_range = st.sidebar.date_input(
        "Seleccionar rango",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key="date_filter"
    )

    # Position filter
    st.sidebar.markdown("#### Position")
    positions = sorted(df['Position'].dropna().unique())
    selected_positions = st.sidebar.multiselect(
        "Seleccionar positions",
        options=positions,
        default=None,
        key="position_filter"
    )

    # Seniority filter
    st.sidebar.markdown("#### Seniority")
    seniorities = sorted(df['Seniority'].dropna().unique())
    selected_seniorities = st.sidebar.multiselect(
        "Seleccionar seniorities",
        options=seniorities,
        default=None,
        key="seniority_filter"
    )

    # Studio filter
    st.sidebar.markdown("#### Studio")
    studios = sorted(df['Studio'].dropna().unique())
    selected_studios = st.sidebar.multiselect(
        "Seleccionar studios",
        options=studios,
        default=None,
        key="studio_filter"
    )

    # Location filter
    st.sidebar.markdown("#### Location")
    locations = sorted(df['Location'].dropna().unique())
    selected_locations = st.sidebar.multiselect(
        "Seleccionar locations",
        options=locations,
        default=None,
        key="location_filter"
    )

    # Engagement Category filter
    st.sidebar.markdown("#### Engagement Category")
    categories = ['Bajo', 'Medio', 'Alto', 'Muy Alto']
    selected_categories = st.sidebar.multiselect(
        "Seleccionar categorías",
        options=categories,
        default=None,
        key="category_filter"
    )

    # Apply filters button
    st.sidebar.markdown("---")
    col_btn1, col_btn2 = st.sidebar.columns(2)

    with col_btn1:
        if st.button("Aplicar Filtros", type="primary", use_container_width=True):
            filters = {
                'date_range': date_range if len(date_range) == 2 else None,
                'Position': selected_positions,
                'Seniority': selected_seniorities,
                'Studio': selected_studios,
                'Location': selected_locations,
                'Engagement Category': selected_categories
            }
            st.session_state.df_filtered = apply_filters(df, filters)
            st.session_state.filters_applied = filters
            st.rerun()

    with col_btn2:
        if st.button("Limpiar", use_container_width=True):
            st.session_state.df_filtered = df.copy()
            st.session_state.filters_applied = {}
            st.rerun()

    # Show filter status
    if st.session_state.filters_applied:
        active_filters = sum(1 for v in st.session_state.filters_applied.values() if v)
        st.sidebar.success(f"{active_filters} filtro(s) activo(s)")
        filtered_count = len(st.session_state.df_filtered) if st.session_state.df_filtered is not None else len(df)
        st.sidebar.info(f"{filtered_count:,} de {len(df):,} registros")
    else:
        st.sidebar.info(f"{len(df):,} registros totales")

# ============================================================================
# MAIN CONTENT (only if data is loaded)
# ============================================================================

if st.session_state.data_loaded:

    df_display = st.session_state.df_filtered if st.session_state.df_filtered is not None else st.session_state.df

    # ============================================================================
    # B) ESTADÍSTICAS DESCRIPTIVAS
    # ============================================================================

    st.markdown('<div class="sub-header">Estadísticas Descriptivas</div>', unsafe_allow_html=True)

    # Tabs for organization
    tab1, tab2, tab3 = st.tabs(["Resumen General", "Estadísticas por Columna", "Valores Únicos"])

    with tab1:
        # General summary
        summary = get_data_summary(df_display)

        # Metrics in columns
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric("Registros", f"{summary['shape']['rows']:,}")

        with col2:
            st.metric("Columnas", f"{summary['shape']['columns']}")

        with col3:
            st.metric("Memoria (MB)", f"{summary['memory_usage_mb']:.2f}")

        with col4:
            if 'engagement_stats' in summary:
                st.metric("Engagement Medio", f"{summary['engagement_stats']['mean']:.2f}")

        with col5:
            if 'date_range' in summary:
                st.metric("Días de datos", f"{summary['date_range']['days']:,}")

        # Date range
        if 'date_range' in summary:
            st.markdown("**Rango de Fechas:**")
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**Inicio:** {summary['date_range']['min']}")
            with col2:
                st.info(f"**Fin:** {summary['date_range']['max']}")

        # Unique counts
        if 'unique_counts' in summary:
            st.markdown("**Valores Únicos:**")
            unique_df = pd.DataFrame([
                {'Columna': k, 'Valores Únicos': v}
                for k, v in summary['unique_counts'].items()
            ])
            st.dataframe(unique_df, use_container_width=True, hide_index=True)
            st.caption("Cardinalidad de cada columna. Valores muy altos pueden indicar campos de texto libre.")

        # Category distribution
        if 'category_distribution' in summary:
            st.markdown("**Distribución de Engagement Categories:**")
            cat_df = pd.DataFrame([
                {'Categoría': k, 'Count': v, 'Porcentaje': f"{v/summary['shape']['rows']*100:.1f}%"}
                for k, v in summary['category_distribution'].items()
            ])
            st.dataframe(cat_df, use_container_width=True, hide_index=True)
            st.caption("Distribución actual de engagement. Un desbalance extremo puede sesgar las predicciones.")

    with tab2:
        # Descriptive statistics
        st.markdown("**Estadísticas para Columnas Numéricas:**")

        numeric_cols = df_display.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            desc_stats = df_display[numeric_cols].describe().T
            desc_stats = desc_stats.round(2)

            st.dataframe(
                desc_stats.style.background_gradient(cmap='YlOrRd', axis=1),
                use_container_width=True
            )
            st.caption("count=registros, mean=promedio, std=desviación estándar, min/max=extremos, 25-50-75%=percentiles.")
        else:
            st.warning("No hay columnas numéricas para mostrar estadísticas.")

        st.markdown("**Información de Tipos de Datos:**")
        dtype_df = pd.DataFrame({
            'Columna': df_display.columns,
            'Tipo': df_display.dtypes.astype(str),
            'No Nulos': df_display.count(),
            'Nulos': df_display.isnull().sum(),
            '% Nulos': (df_display.isnull().sum() / len(df_display) * 100).round(2)
        })
        st.dataframe(dtype_df, use_container_width=True, hide_index=True)
        st.caption("Resumen de cada columna. Revisa % Nulos para identificar datos incompletos.")

    with tab3:
        # Unique values for categorical columns
        st.markdown("**Valores Únicos por Columna Categórica:**")
        st.caption("Desglose de cada variable categórica. Útiles para identificar filtros y segmentaciones.")

        categorical_cols = ['Position', 'Seniority', 'Studio', 'Location', 'Engagement Category']

        for col in categorical_cols:
            if col in df_display.columns:
                with st.expander(f"{col} ({df_display[col].nunique()} valores únicos)"):
                    value_counts = df_display[col].value_counts()
                    value_df = pd.DataFrame({
                        'Valor': value_counts.index,
                        'Count': value_counts.values,
                        'Porcentaje': (value_counts.values / len(df_display) * 100).round(2)
                    })
                    st.dataframe(value_df, use_container_width=True, hide_index=True, height=300)

    # ============================================================================
    # D) VISUALIZACIÓN DE DISTRIBUCIONES
    # ============================================================================

    st.markdown('<div class="sub-header">Visualización de Distribuciones</div>', unsafe_allow_html=True)

    # Engagement distribution
    col1, col2 = st.columns(2)

    fig_hist, fig_box = create_distribution_plots(df_display)

    with col1:
        st.plotly_chart(fig_hist, use_container_width=True)
        st.caption("Muestra la frecuencia de cada nivel de engagement. Una curva centrada indica datos balanceados.")

    with col2:
        st.plotly_chart(fig_box, use_container_width=True)
        st.caption("La caja central contiene el 50% de los datos. Los puntos fuera son posibles outliers.")

    # Category distributions
    st.markdown("**Distribuciones por Categorías:**")

    col1, col2 = st.columns(2)

    fig_pos, fig_sen, fig_studio, fig_cat = create_category_distributions(df_display)

    with col1:
        st.plotly_chart(fig_pos, use_container_width=True)
        st.caption("Cantidad de registros por rol. Identifica los roles más representados en el dataset.")
        st.plotly_chart(fig_studio, use_container_width=True)
        st.caption("Los 10 estudios con más registros. Útil para identificar dónde hay más datos disponibles.")

    with col2:
        st.plotly_chart(fig_sen, use_container_width=True)
        st.caption("Distribución por nivel de experiencia. Verifica si hay balance entre niveles.")
        st.plotly_chart(fig_cat, use_container_width=True)
        st.caption("Proporción de empleados en cada nivel de engagement. Colores indican nivel de riesgo.")

    # Temporal evolution
    st.markdown("**Evolución Temporal:**")
    fig_temporal = create_temporal_plot(df_display)
    st.plotly_chart(fig_temporal, use_container_width=True)
    st.caption("Tendencia del engagement promedio en el tiempo. La banda sombreada muestra la variabilidad (±1 desv. estándar).")

    # ============================================================================
    # E) ANÁLISIS DE CALIDAD
    # ============================================================================

    st.markdown('<div class="sub-header">Análisis de Calidad de Datos</div>', unsafe_allow_html=True)

    quality_report = get_quality_report(df_display)

    # Quality score
    quality_score = quality_report.get('quality_score', 0)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        if quality_score >= 95:
            st.markdown(f'<div class="quality-good">Score de Calidad: {quality_score:.2f}%</div>',
                       unsafe_allow_html=True)
        elif quality_score >= 85:
            st.markdown(f'<div class="quality-warning">Score de Calidad: {quality_score:.2f}%</div>',
                       unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="quality-error">Score de Calidad: {quality_score:.2f}%</div>',
                       unsafe_allow_html=True)

    # Warnings
    warnings = quality_report.get('warnings', [])
    if warnings:
        st.markdown("**Advertencias de Calidad:**")
        for warning in warnings:
            st.warning(warning)
    else:
        st.success("No se detectaron problemas de calidad")

    # Detailed quality metrics
    col1, col2 = st.columns(2)

    with col1:
        # Missing values
        missing_vals = quality_report.get('missing_values', {})
        if missing_vals:
            st.markdown("**Valores Faltantes:**")
            missing_df = pd.DataFrame([
                {'Columna': col, 'Count': info['count'], 'Porcentaje': f"{info['percentage']:.2f}%"}
                for col, info in missing_vals.items()
            ])
            st.dataframe(missing_df, use_container_width=True, hide_index=True)
            st.caption("Columnas con datos incompletos. Considera imputar o excluir si el porcentaje es muy alto.")

            # Visualization
            fig_missing = create_quality_visualizations(quality_report)
            if fig_missing:
                st.plotly_chart(fig_missing, use_container_width=True)
                st.caption("Porcentaje de datos faltantes por columna. Valores altos pueden afectar la calidad del modelo.")
        else:
            st.success("No hay valores faltantes")

    with col2:
        # Outliers
        outliers = quality_report.get('outliers', {})
        if outliers:
            st.markdown("**Outliers Detectados:**")
            for col, info in outliers.items():
                st.warning(f"**{col}:** {info['count']} outliers ({info['percentage']:.2f}%)")
                st.caption(f"Límites: [{info['bounds']['lower']:.2f}, {info['bounds']['upper']:.2f}]")
        else:
            st.success("No se detectaron outliers significativos")

        # Invalid values
        invalid_vals = quality_report.get('invalid_values', {})
        if invalid_vals:
            st.markdown("**Valores Inválidos:**")
            for issue, count in invalid_vals.items():
                st.error(f"**{issue}:** {count}")

        # Duplicates
        duplicates = quality_report.get('duplicates', {})
        if duplicates:
            st.markdown("**Duplicados:**")
            st.info(f"Total de filas duplicadas: {duplicates.get('total_duplicate_rows', 0)}")

    # ============================================================================
    # F) EXPORTACIÓN
    # ============================================================================

    st.markdown('<div class="sub-header">Exportación de Datos</div>', unsafe_allow_html=True)

    st.markdown(f"**Registros a exportar:** {len(df_display):,}")

    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        export_format = st.selectbox(
            "Formato",
            options=['csv', 'excel'],
            format_func=lambda x: 'CSV' if x == 'csv' else 'Excel (.xlsx)'
        )

    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing

        if st.button("Generar Exportación", type="primary"):
            with st.spinner("Generando archivo..."):
                output, filename, mime = export_data(df_display, format=export_format)

                st.download_button(
                    label=f"Descargar {filename}",
                    data=output,
                    file_name=filename,
                    mime=mime,
                    type="primary"
                )

                st.success(f"Archivo generado: {filename}")

    with col3:
        st.info("**Tip:** Los datos exportados incluirán todos los filtros aplicados actualmente.")

else:
    # No data loaded message
    st.info("Por favor, carga un dataset para comenzar el análisis.")

    st.markdown("""
    ### Guía de Uso

    1. **Carga de Datos:** Utiliza el dataset por defecto o sube tu propio archivo CSV/Excel
    2. **Aplica Filtros:** Usa el panel lateral para filtrar datos por fecha, position, seniority, etc.
    3. **Explora Estadísticas:** Revisa resúmenes, estadísticas descriptivas y valores únicos
    4. **Visualiza Distribuciones:** Analiza gráficos de distribución y evolución temporal
    5. **Analiza Calidad:** Revisa el score de calidad y detecta problemas en los datos
    6. **Exporta Resultados:** Descarga los datos filtrados en CSV o Excel

    ---

    **Columnas esperadas en el dataset:**
    - Date, Email, Name, Position, Seniority, Location
    - Studio, Client, Project, Team Name
    - Engagement, Engagement Category
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
    Data Explorer | Engagement Prediction System | ITESM
</div>
""", unsafe_allow_html=True)
