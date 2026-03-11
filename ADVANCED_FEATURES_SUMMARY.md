# Advanced Features Documentation

Documentación completa de las características avanzadas del sistema de predicción de engagement.

## Tabla de Contenidos

1. [Sistema de Sesiones](#sistema-de-sesiones)
2. [Sistema de Exportación](#sistema-de-exportación)
3. [Gestión de Caché](#gestión-de-caché)
4. [Monitoreo de Performance](#monitoreo-de-performance)
5. [Funciones Auxiliares](#funciones-auxiliares)
6. [Optimizaciones de Streamlit](#optimizaciones-de-streamlit)
7. [Configuración](#configuración)
8. [Testing](#testing)
9. [Troubleshooting](#troubleshooting)

---

## Sistema de Sesiones

### SessionManager

Gestiona sesiones de usuario, historial y configuraciones de manera persistente.

#### Características

- Persistencia en archivos JSON
- Auto-guardado periódico
- Gestión de historial de predicciones
- Preferencias de usuario
- Limpieza automática de sesiones antiguas
- Compresión de sesiones
- Sistema de backups

#### Uso Básico

```python
from src.utils.session_manager import get_session_manager

# Obtener instancia
session_mgr = get_session_manager()

# Guardar sesión
session_data = {
    'model_config': {...},
    'predictions_count': 5,
    'last_prediction': {...}
}
session_mgr.save_session('user_session_001', session_data, user='john_doe')

# Cargar sesión
loaded_session = session_mgr.load_session('user_session_001')

# Obtener todas las sesiones
all_sessions = session_mgr.get_all_sessions()

# Eliminar sesión
session_mgr.delete_session('user_session_001')
```

#### Gestión de Historial

```python
# Guardar predicción en historial
prediction_data = {
    'timestamp': '2024-01-01T12:00:00',
    'current_state': 'Medium',
    'prediction': 0.75,
    'probabilities': {...}
}
session_mgr.save_prediction_to_history(prediction_data)

# Obtener historial
history = session_mgr.get_prediction_history(limit=10)

# Exportar historial
export_path = session_mgr.export_history(format='csv')  # o 'json'

# Limpiar historial
session_mgr.clear_history()
```

#### Preferencias de Usuario

```python
# Guardar preferencias
preferences = {
    'theme': 'dark',
    'default_time_horizon': 10,
    'auto_save': True,
    'chart_style': 'plotly'
}
session_mgr.save_user_preferences(preferences)

# Cargar preferencias
prefs = session_mgr.load_user_preferences()
```

#### Estadísticas

```python
stats = session_mgr.get_session_stats()
# Retorna:
# {
#     'total_sessions': 25,
#     'total_predictions': 150,
#     'total_size_mb': 5.2,
#     'oldest_session': '2024-01-01T...',
#     'newest_session': '2024-03-15T...'
# }
```

---

## Sistema de Exportación

### ExportManager

Genera reportes profesionales en múltiples formatos.

#### Formatos Soportados

- PDF (reportes completos con gráficos)
- Excel (múltiples hojas con formato)
- CSV (datos tabulares)
- JSON (datos estructurados)

#### Uso Básico

```python
from src.utils.export_manager import get_export_manager

export_mgr = get_export_manager()

# Exportar a PDF
pdf_path = export_mgr.export_to_pdf(
    data=prediction_result,
    report_type='prediction',
    filename='report_2024.pdf'
)

# Exportar a Excel
excel_path = export_mgr.export_to_excel(
    data=summary_data,
    filename='analysis.xlsx'
)

# Exportar a CSV
csv_path = export_mgr.export_to_csv(
    data=dataframe,
    filename='data.csv'
)

# Exportar a JSON
json_path = export_mgr.export_to_json(
    data=prediction_data,
    filename='results.json'
)
```

#### Generar Reporte Completo

```python
# Genera PDF, Excel y JSON automáticamente
files = export_mgr.generate_full_report(
    prediction_result=results,
    include_charts=True
)

# Retorna:
# {
#     'pdf': '/path/to/report.pdf',
#     'excel': '/path/to/report.xlsx',
#     'json': '/path/to/report.json'
# }
```

#### Resumen Ejecutivo

```python
executive_data = {
    'kpis': {
        'Total Users': 10000,
        'Avg Engagement': 0.67,
        'Growth Rate': 0.15
    },
    'insights': [
        'Engagement ha incrementado 15% este mes',
        'Los usuarios activos superaron la meta',
        'Se recomienda mantener estrategias actuales'
    ]
}

pdf_path = export_mgr.generate_executive_summary(executive_data)
```

---

## Gestión de Caché

### CacheManager

Sistema de caché inteligente para optimizar performance.

#### Características

- Caché en memoria (LRU)
- Caché en disco (persistente)
- TTL configurable
- Estadísticas de hit/miss
- Limpieza automática
- Caché especializado para matrices, predicciones y gráficos

#### Uso Básico

```python
from src.utils.cache_manager import get_cache_manager

cache_mgr = get_cache_manager()

# Cachear datos
cache_mgr.cache_data(
    key='my_key',
    data={'value': 123},
    ttl=3600  # 1 hora
)

# Recuperar datos
cached = cache_mgr.get_cached_data('my_key')

# Invalidar caché
cache_mgr.invalidate_cache('my_key')

# Limpiar todo
cache_mgr.clear_all_cache()
```

#### Caché de Matrices

```python
# Cachear matriz de transición
matrix_data = [[0.1, 0.3, 0.6], ...]
conditions = {'state': 'Medium', 'context': 'mobile'}

cache_mgr.cache_matrix('transition', conditions, matrix_data)

# Recuperar matriz
cached_matrix = cache_mgr.get_cached_matrix('transition', conditions)
```

#### Caché de Predicciones

```python
model_params = {
    'current_state': 'Medium',
    'time_horizon': 10,
    'context': {'device': 'mobile'}
}

cache_mgr.cache_prediction(model_params, prediction_result, ttl=1800)

# Recuperar predicción
cached_pred = cache_mgr.get_cached_prediction(model_params)
```

#### Estadísticas de Caché

```python
stats = cache_mgr.get_cache_stats()
# {
#     'hits': 150,
#     'misses': 25,
#     'total_requests': 175,
#     'hit_rate': 85.7,
#     'memory_cache_size': 45,
#     'disk_cache_size': 120
# }
```

#### Limpieza

```python
# Limpiar entradas expiradas
removed = cache_mgr.cleanup_expired()

# Comprimir sesiones antiguas
compressed = cache_mgr.compress_old_sessions(days_threshold=7)
```

---

## Monitoreo de Performance

### PerformanceMonitor

Monitorea y registra el rendimiento de la aplicación.

#### Características

- Medición de tiempo de operaciones
- Tracking de uso de memoria
- Logging a archivos
- Generación de reportes
- Context managers para medición
- Estadísticas agregadas

#### Uso Básico

```python
from src.utils.performance_monitor import get_performance_monitor

perf_monitor = get_performance_monitor()

# Medir con timer manual
perf_monitor.start_timer('data_loading')
# ... cargar datos ...
duration = perf_monitor.end_timer('data_loading')

# Medir con context manager
with perf_monitor.measure('model_training'):
    # ... entrenar modelo ...
    pass

# Log de operación manual
perf_monitor.log_operation(
    'prediction',
    duration_ms=250.5,
    metadata={'model': 'markov', 'states': 3}
)
```

#### Decorator para Medir Funciones

```python
from src.utils.performance_monitor import measure_time

@measure_time('my_function')
def expensive_operation():
    # ... código ...
    pass
```

#### Tracking de Memoria

```python
memory_info = perf_monitor.track_memory_usage()
# {
#     'rss_mb': 150.5,
#     'vms_mb': 200.3,
#     'percent': 2.5
# }
```

#### Generar Reportes

```python
# Estadísticas agregadas
stats = perf_monitor.get_performance_stats()

# Reporte completo
report = perf_monitor.generate_performance_report()
# {
#     'timestamp': '2024-01-01T12:00:00',
#     'system': {...},
#     'app': {...},
#     'operations': {...},
#     'slowest_operations': [...]
# }

# Exportar métricas
perf_monitor.export_metrics(format='json', filename='metrics.json')
```

#### Log de Errores

```python
try:
    # ... código que puede fallar ...
    pass
except Exception as e:
    perf_monitor.log_error(e, context={'user': 'john', 'operation': 'predict'})
```

---

## Funciones Auxiliares

### Helpers Module

Colección de funciones útiles para el sistema.

#### Validación

```python
from src.utils.helpers import *

# Validar email
is_valid = validate_email('user@example.com')

# Validar rango de fechas
is_valid = validate_date_range('2024-01-01', '2024-12-31')

# Validar esquema de DataFrame
is_valid, missing = validate_dataframe_schema(
    df,
    required_columns=['user_id', 'date', 'engagement']
)

# Validar probabilidad
is_valid = validate_probability(0.75)
```

#### Formateo

```python
# Formatear porcentaje
formatted = format_percentage(0.753, decimals=2)  # "75.30%"

# Formatear moneda
formatted = format_currency(1234.56, currency='USD')  # "$1,234.56"

# Formatear fecha
formatted = format_datetime(datetime.now(), format_type='long')

# Formatear número con magnitud
formatted = format_number(1500000)  # "1.5M"

# Formatear duración
formatted = format_duration(3665)  # "1h 1m 5s"

# Formatear tamaño de archivo
formatted = format_file_size(1048576)  # "1.0 MB"
```

#### Conversión

```python
# Convertir unidades de tiempo
hours = convert_time_units(120, from_unit='m', to_unit='h')  # 2.0

# Engagement category <-> numeric
numeric = engagement_category_to_numeric('High')  # 2
category = numeric_to_engagement_category(0.8)  # 'High'

# String a booleano
bool_val = str_to_bool('true')  # True
```

#### Análisis

```python
# Calcular cambio porcentual
delta = calculate_delta_percentage(150, 100)  # 50.0

# Obtener tendencia
trend = get_trend_direction([1, 2, 3, 4, 5])  # '↑'

# Detectar anomalías
anomalies = detect_anomalies(series, method='iqr', threshold=1.5)

# Calcular promedio móvil
ma = calculate_moving_average(series, window=7)

# Tasa de crecimiento
growth = calculate_growth_rate([100, 110, 121], periods=2)
```

#### Data Manipulation

```python
# Agregar por período
aggregated = aggregate_by_period(
    df,
    date_column='date',
    period='month',
    agg_func='mean'
)

# Crear tabla pivote
pivoted = pivot_engagement_data(
    df,
    index='user_id',
    columns='date',
    values='engagement'
)

# Rellenar fechas faltantes
filled = fill_missing_dates(
    df,
    date_column='date',
    freq='D',
    fill_method='ffill'
)

# Normalizar columna
normalized = normalize_column(df, 'engagement', method='minmax')
```

---

## Optimizaciones de Streamlit

### Caché de Streamlit

```python
from src.utils.streamlit_cache import *

# Decorator para cachear predicciones
@cache_predictions(ttl=1800)
def predict(model, data):
    return model.predict(data)

# Decorator para cachear carga de datos
@cache_data_load(ttl=3600)
def load_data(file_path):
    return pd.read_csv(file_path)

# Decorator para cachear modelos
@cache_model(ttl=7200)
def load_model():
    return MarkovModel()

# Limpiar caché
clear_cache(cache_type='data')  # 'data', 'resource', o None
```

### Procesamiento Asíncrono

```python
from src.utils.async_processor import get_async_processor, run_with_progress

async_proc = get_async_processor()

# Ejecutar en background
future = async_proc.run_in_background(
    heavy_function,
    arg1,
    arg2,
    callback=on_complete
)

# Monte Carlo asíncrono
future = async_proc.monte_carlo_async(
    model,
    config,
    n_simulations=10000,
    progress_callback=update_progress
)

# Procesar en batches
results = async_proc.batch_process(
    process_item,
    items,
    batch_size=100,
    progress_callback=update_progress
)

# Con progress bar en Streamlit
result = run_with_progress(
    heavy_function,
    arg1,
    arg2,
    progress_text="Processing..."
)
```

### Lazy Loading

```python
from src.utils.lazy_loader import *

# Lazy load de gráfico
lazy_load_chart(
    create_chart_function,
    data,
    expander_label="View Chart",
    expanded=False
)

# Lazy load de componente
lazy_load_component(
    render_component,
    data,
    checkbox_label="Show Details",
    default_value=False
)

# Lazy load de tabs
lazy_load_tab({
    'Overview': lambda: show_overview(),
    'Details': lambda: show_details(),
    'Charts': lambda: show_charts()
})

# Renderizado condicional
conditional_render(
    condition=show_advanced,
    render_function=render_advanced_options,
    fallback=render_basic_options
)

# Paginación
paginated_render(
    items=large_list,
    render_function=render_item,
    items_per_page=10
)
```

---

## Configuración

### Archivo config.py

Configuraciones centralizadas del sistema.

#### Secciones Principales

```python
from src.utils.config import *

# Obtener configuración de una sección
cache_config = get_config('cache')
export_config = get_config('export')
session_config = get_config('session')

# Verificar feature flags
if is_feature_enabled('enable_monte_carlo'):
    # ... ejecutar Monte Carlo ...
    pass

# Obtener TTL de caché
ttl = get_cache_ttl('predictions')  # 1800 segundos

# Obtener directorio de datos
data_dir = get_data_dir('exports')
```

#### Configuraciones Disponibles

- `CACHE_CONFIG`: Configuración de caché
- `EXPORT_CONFIG`: Configuración de exportación
- `SESSION_CONFIG`: Configuración de sesiones
- `MONITORING_CONFIG`: Configuración de monitoreo
- `MARKOV_CONFIG`: Configuración del modelo Markov
- `DATA_CONFIG`: Configuración de procesamiento de datos
- `STREAMLIT_CONFIG`: Configuración de Streamlit
- `VIZ_CONFIG`: Configuración de visualizaciones
- `FEATURE_FLAGS`: Flags de características

#### Variables de Entorno

Configurar a través de variables de entorno:

```bash
export ENVIRONMENT=production
export DEBUG=false
export DB_HOST=localhost
export DB_PORT=5432
```

---

## Testing

### Ejecutar Tests

```bash
# Todos los tests
pytest tests/test_advanced_features.py -v

# Tests específicos
pytest tests/test_advanced_features.py::TestSessionManager -v
pytest tests/test_advanced_features.py::TestCacheManager -v

# Con coverage
pytest tests/test_advanced_features.py --cov=src/utils --cov-report=html
```

### Fixtures Disponibles

- `temp_dir`: Directorio temporal
- `session_manager`: SessionManager instanciado
- `export_manager`: ExportManager instanciado
- `cache_manager`: CacheManager instanciado
- `performance_monitor`: PerformanceMonitor instanciado
- `sample_data`: Datos de ejemplo
- `sample_dataframe`: DataFrame de ejemplo

---

## Troubleshooting

### Problemas Comunes

#### 1. Caché no funciona

**Síntoma**: Los datos no se cachean correctamente.

**Solución**:
```python
# Verificar que el caché esté habilitado
from src.utils.config import is_feature_enabled
print(is_feature_enabled('enable_cache'))

# Limpiar caché corrupto
cache_mgr.clear_all_cache()

# Verificar permisos de escritura
import os
cache_dir = "data/cache"
print(os.access(cache_dir, os.W_OK))
```

#### 2. Sesiones no se guardan

**Síntoma**: Las sesiones desaparecen después de reiniciar.

**Solución**:
```python
# Verificar que el directorio existe
from pathlib import Path
sessions_dir = Path("data/sessions")
sessions_dir.mkdir(parents=True, exist_ok=True)

# Deshabilitar auto-cleanup temporalmente
session_mgr = SessionManager(auto_cleanup=False)

# Verificar estadísticas
print(session_mgr.get_session_stats())
```

#### 3. Exportación PDF falla

**Síntoma**: Error al generar PDF.

**Solución**:
```bash
# Instalar dependencias faltantes
pip install reportlab Pillow

# Verificar instalación
python -c "import reportlab; print(reportlab.Version)"
```

#### 4. Performance Monitor consume mucha memoria

**Síntoma**: Alto uso de memoria.

**Solución**:
```python
# Deshabilitar file logging
perf_monitor = PerformanceMonitor(
    enable_file_logging=False,
    enable_memory_tracking=False
)

# Resetear estadísticas periódicamente
perf_monitor.reset_stats()

# Limpiar logs antiguos
perf_monitor.cleanup_old_logs(days=7)
```

#### 5. Streamlit caché no limpia

**Síntoma**: Caché de Streamlit crece indefinidamente.

**Solución**:
```python
import streamlit as st

# Botón para limpiar caché
if st.button("Clear Cache"):
    st.cache_data.clear()
    st.cache_resource.clear()
    st.success("Cache cleared!")
```

### Logs y Debugging

#### Habilitar Logging Detallado

```python
import logging

# Configurar nivel de log
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Logger específico
logger = logging.getLogger('src.utils.cache_manager')
logger.setLevel(logging.DEBUG)
```

#### Verificar Salud del Sistema

```python
from src.utils.session_manager import get_session_manager
from src.utils.cache_manager import get_cache_manager
from src.utils.performance_monitor import get_performance_monitor

# Session stats
print("Sessions:", get_session_manager().get_session_stats())

# Cache stats
print("Cache:", get_cache_manager().get_cache_stats())

# Performance stats
print("Performance:", get_performance_monitor().get_performance_stats())
```

---

## Best Practices

### 1. Gestión de Sesiones

- Usar `auto_save_session()` cada 5 minutos
- Limpiar sesiones >30 días automáticamente
- Hacer backup antes de operaciones críticas

### 2. Caché

- Usar TTL apropiados según tipo de datos
- Limpiar caché expirado periódicamente
- Monitorear hit rate (objetivo: >80%)

### 3. Exportación

- Validar datos antes de exportar
- Incluir timestamp en nombres de archivo
- Comprimir archivos grandes

### 4. Monitoreo

- Revisar logs diariamente
- Establecer alertas para operaciones lentas (>5s)
- Exportar métricas semanalmente

### 5. Performance

- Usar lazy loading para componentes pesados
- Procesar en background cuando sea posible
- Cachear agresivamente predicciones

---

## Recursos Adicionales

- [Streamlit Caching Guide](https://docs.streamlit.io/library/advanced-features/caching)
- [ReportLab Documentation](https://www.reportlab.com/docs/reportlab-userguide.pdf)
- [pytest Documentation](https://docs.pytest.org/)

---

## Changelog

### v1.0.0 (2024-01-01)
- Implementación inicial de SessionManager
- Sistema de exportación PDF/Excel
- CacheManager con LRU
- PerformanceMonitor
- Helpers completos
- Tests unitarios

---

## Soporte

Para reportar bugs o solicitar features:
- GitHub Issues: [link]
- Email: support@example.com
- Documentación: [link]
