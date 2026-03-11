# Advanced Features Setup Guide

Guía paso a paso para configurar e implementar las características avanzadas.

## Índice

1. [Instalación](#instalación)
2. [Verificación](#verificación)
3. [Configuración](#configuración)
4. [Integración con Streamlit](#integración-con-streamlit)
5. [Testing](#testing)
6. [Deployment](#deployment)

---

## Instalación

### 1. Instalar Dependencias

```bash
cd engagement-prediction-app

# Instalar todas las dependencias
pip install -r requirements.txt

# Verificar instalación de psutil (nuevo)
python -c "import psutil; print(f'psutil {psutil.version_info}')"
```

### 2. Verificar Estructura de Directorios

Los directorios se crean automáticamente al importar config.py, pero puedes verificar:

```bash
# En Windows
dir data
dir data\sessions
dir data\cache
dir data\exports
dir data\logs

# En Linux/Mac
ls -la data/
ls -la data/sessions/
ls -la data/cache/
ls -la data/exports/
ls -la data/logs/
```

### 3. Verificar Archivos Creados

```bash
# Utilidades principales
ls src/utils/session_manager.py
ls src/utils/export_manager.py
ls src/utils/cache_manager.py
ls src/utils/performance_monitor.py

# Utilidades Streamlit
ls src/utils/streamlit_cache.py
ls src/utils/async_processor.py
ls src/utils/lazy_loader.py

# Configuración
ls src/utils/config.py
ls src/utils/helpers.py

# Tests
ls tests/test_advanced_features.py

# Documentación
ls ADVANCED_FEATURES.md
ls ADVANCED_FEATURES_SUMMARY.md
```

---

## Verificación

### 1. Ejecutar Tests

```bash
# Todos los tests
pytest tests/test_advanced_features.py -v

# Tests específicos
pytest tests/test_advanced_features.py::TestSessionManager -v

# Con coverage
pytest tests/test_advanced_features.py --cov=src/utils --cov-report=html

# Ver reporte de coverage
# Windows: start htmlcov/index.html
# Linux/Mac: open htmlcov/index.html
```

### 2. Ejecutar Demo

```bash
# Demo interactiva
python examples/advanced_features_demo.py
```

Deberías ver output similar a:

```
============================================================
ADVANCED FEATURES DEMONSTRATION
Engagement Prediction System v1.0.0
============================================================

==================================================
DEMO: Session Management
==================================================

1. Guardando sesión...
✓ Sesión guardada

2. Cargando sesión...
✓ Sesión cargada: demo_user

...
```

### 3. Verificación Manual en Python

```python
# test_import.py
import sys
sys.path.insert(0, 'src')

# Importar módulos
from src.utils import (
    get_session_manager,
    get_export_manager,
    get_cache_manager,
    get_performance_monitor
)

# Verificar que funcionan
session_mgr = get_session_manager()
print("✓ SessionManager OK")

export_mgr = get_export_manager()
print("✓ ExportManager OK")

cache_mgr = get_cache_manager()
print("✓ CacheManager OK")

perf = get_performance_monitor()
print("✓ PerformanceMonitor OK")

print("\n✓ Todos los módulos importados exitosamente")
```

Ejecutar:
```bash
python test_import.py
```

---

## Configuración

### 1. Configurar Variables de Entorno (Opcional)

Crear archivo `.env` en la raíz del proyecto:

```bash
# .env
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# Database (futuro)
# DB_HOST=localhost
# DB_PORT=5432
# DB_NAME=engagement_db
```

### 2. Configurar Streamlit Secrets (Producción)

Copiar el ejemplo de secrets:

```bash
# Windows
copy .streamlit\secrets.toml.example .streamlit\secrets.toml

# Linux/Mac
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Editar `.streamlit/secrets.toml` con tus valores:

```toml
[general]
app_name = "Engagement Prediction System"
environment = "production"
secret_key = "tu-secret-key-segura-aqui"

# Agregar otros secrets según necesites
```

**IMPORTANTE**: Asegurar que `secrets.toml` esté en `.gitignore`:

```bash
# Verificar .gitignore
grep "secrets.toml" .gitignore

# Si no está, agregar
echo ".streamlit/secrets.toml" >> .gitignore
```

### 3. Ajustar Configuración (config.py)

Editar `src/utils/config.py` según tus necesidades:

```python
# Ejemplo: Ajustar TTLs de caché
CACHE_TTL = {
    'data': 7200,  # 2 horas en lugar de 1
    'model': 14400,  # 4 horas en lugar de 2
    'predictions': 3600,  # 1 hora en lugar de 30 min
    'charts': 1200,  # 20 minutos en lugar de 10
}

# Ejemplo: Ajustar límites de sesiones
SESSION_CONFIG = {
    'max_sessions': 500,  # Incrementar de 100
    'session_ttl_days': 60,  # 60 días en lugar de 30
}
```

---

## Integración con Streamlit

### 1. Importar en tu App Streamlit

```python
# app.py (o tu archivo principal de Streamlit)
import streamlit as st
from src.utils import (
    get_session_manager,
    get_export_manager,
    get_cache_manager,
    get_performance_monitor,
    cache_predictions,
    lazy_load_chart
)

# Inicializar managers
@st.cache_resource
def init_managers():
    return {
        'session': get_session_manager(),
        'export': get_export_manager(),
        'cache': get_cache_manager(),
        'perf': get_performance_monitor()
    }

managers = init_managers()
```

### 2. Implementar Auto-guardado de Sesiones

```python
# En tu Streamlit app
import streamlit as st
from src.utils import get_session_manager

# Obtener session manager
session_mgr = get_session_manager()

# Guardar estado de la sesión
if st.session_state.get('session_id'):
    session_data = {
        'model_config': st.session_state.get('model_config', {}),
        'predictions_count': st.session_state.get('predictions_count', 0),
        'last_prediction': st.session_state.get('last_prediction')
    }

    # Auto-guardar cada cambio importante
    session_mgr.save_session(
        st.session_state.session_id,
        session_data,
        user=st.session_state.get('user', 'anonymous')
    )
```

### 3. Agregar Botones de Exportación

```python
# En tu Streamlit app
import streamlit as st
from src.utils import get_export_manager

export_mgr = get_export_manager()

# Agregar en sidebar o al final de resultados
st.subheader("Exportar Resultados")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📄 PDF"):
        with st.spinner("Generando PDF..."):
            pdf_path = export_mgr.export_to_pdf(
                prediction_result,
                report_type='prediction'
            )
            st.success(f"PDF generado: {pdf_path}")

            # Crear download button
            with open(pdf_path, 'rb') as f:
                st.download_button(
                    "Descargar PDF",
                    f,
                    file_name="prediction_report.pdf",
                    mime="application/pdf"
                )

with col2:
    if st.button("📊 Excel"):
        excel_path = export_mgr.export_to_excel(prediction_result)
        with open(excel_path, 'rb') as f:
            st.download_button(
                "Descargar Excel",
                f,
                file_name="prediction_report.xlsx",
                mime="application/vnd.ms-excel"
            )

with col3:
    if st.button("📋 CSV"):
        csv_path = export_mgr.export_to_csv(prediction_df)
        with open(csv_path, 'rb') as f:
            st.download_button(
                "Descargar CSV",
                f,
                file_name="prediction_data.csv",
                mime="text/csv"
            )

with col4:
    if st.button("💾 JSON"):
        json_path = export_mgr.export_to_json(prediction_result)
        with open(json_path, 'rb') as f:
            st.download_button(
                "Descargar JSON",
                f,
                file_name="prediction_data.json",
                mime="application/json"
            )
```

### 4. Implementar Lazy Loading de Gráficos

```python
from src.utils import lazy_load_chart
import plotly.graph_objects as go

# En lugar de renderizar directamente
# st.plotly_chart(fig)

# Usar lazy loading
lazy_load_chart(
    lambda: st.plotly_chart(create_complex_chart(), use_container_width=True),
    expander_label="📈 Ver Gráfico de Trayectoria",
    expanded=False,
    spinner_text="Generando gráfico..."
)
```

### 5. Cachear Predicciones

```python
from src.utils import cache_predictions

@cache_predictions(ttl=1800)  # 30 minutos
def predict_engagement(model, current_state, time_horizon):
    """Función cacheada de predicción"""
    return model.predict(current_state, time_horizon)

# Usar en Streamlit
result = predict_engagement(model, current_state, time_horizon)
```

### 6. Mostrar Estadísticas en Sidebar

```python
# En sidebar
with st.sidebar:
    st.subheader("📊 Estadísticas del Sistema")

    # Cache stats
    cache_stats = managers['cache'].get_cache_stats()
    st.metric("Cache Hit Rate", f"{cache_stats['hit_rate']:.1f}%")
    st.metric("Caché Size", cache_stats['memory_cache_size'])

    # Session stats
    session_stats = managers['session'].get_session_stats()
    st.metric("Sesiones Activas", session_stats['total_sessions'])
    st.metric("Predicciones Totales", session_stats['total_predictions'])

    # Performance stats
    perf_stats = managers['perf'].get_performance_stats()
    if perf_stats:
        avg_time = sum(s['avg_ms'] for s in perf_stats.values()) / len(perf_stats)
        st.metric("Avg Response Time", f"{avg_time:.0f}ms")
```

---

## Testing

### Ejecutar Tests Completos

```bash
# Instalar pytest si no está
pip install pytest pytest-cov

# Ejecutar todos los tests
pytest tests/ -v

# Solo tests de advanced features
pytest tests/test_advanced_features.py -v

# Con coverage report
pytest tests/test_advanced_features.py --cov=src/utils --cov-report=html --cov-report=term

# Ver coverage report en navegador
# Windows
start htmlcov/index.html

# Linux/Mac
open htmlcov/index.html
```

### Ejecutar Tests Específicos

```bash
# Solo SessionManager
pytest tests/test_advanced_features.py::TestSessionManager -v

# Solo CacheManager
pytest tests/test_advanced_features.py::TestCacheManager -v

# Un test específico
pytest tests/test_advanced_features.py::TestCacheManager::test_cache_and_retrieve_data -v
```

### Crear Tests Adicionales

```python
# tests/test_my_integration.py
import pytest
from src.utils import get_session_manager, get_cache_manager

def test_session_and_cache_integration():
    """Test integración entre sesión y caché"""
    session_mgr = get_session_manager()
    cache_mgr = get_cache_manager()

    # Test logic here
    assert True
```

---

## Deployment

### 1. Preparar para Streamlit Cloud

Verificar que estos archivos estén listos:

```bash
# Verificar requirements.txt tiene todas las deps
cat requirements.txt

# Verificar .streamlit/config.toml
cat .streamlit/config.toml

# Verificar secrets.toml.example (NO subir secrets.toml)
cat .streamlit/secrets.toml.example
```

### 2. Configurar Secrets en Streamlit Cloud

1. Ve a https://share.streamlit.io/
2. Deploy tu app
3. En Settings > Secrets, pega el contenido de tu `secrets.toml`

### 3. Variables de Entorno

Si usas variables de entorno, configúralas en Streamlit Cloud:

```toml
# En Streamlit Cloud Secrets
[env]
ENVIRONMENT = "production"
DEBUG = "false"
LOG_LEVEL = "WARNING"
```

### 4. Ajustar para Producción

Editar `src/utils/config.py`:

```python
# En load_environment_config()
if env == 'production':
    # Configuraciones de producción
    MONITORING_CONFIG['log_level'] = 'WARNING'
    CACHE_CONFIG['max_memory_cache_size'] = 500
    SESSION_CONFIG['max_sessions'] = 1000

    # Deshabilitar features pesadas si es necesario
    FEATURE_FLAGS['enable_monte_carlo'] = False  # Si es muy pesado
```

### 5. Optimizaciones para Streamlit Cloud

```python
# En tu app principal
import streamlit as st

# Configurar página
st.set_page_config(
    page_title="Engagement Prediction",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Limitar uso de memoria
from src.utils import get_cache_manager
cache_mgr = get_cache_manager(
    max_memory_cache_size=50,  # Reducir en cloud
    enable_disk_cache=False  # Deshabilitar disk cache en cloud
)
```

---

## Troubleshooting

### Problema: ModuleNotFoundError

```bash
# Verificar PYTHONPATH
echo $PYTHONPATH  # Linux/Mac
echo %PYTHONPATH%  # Windows

# Agregar directorio raíz
export PYTHONPATH="${PYTHONPATH}:/path/to/engagement-prediction-app"
```

### Problema: Permisos de Escritura

```bash
# Verificar permisos de directorios
ls -la data/

# Dar permisos si es necesario (Linux/Mac)
chmod -R 755 data/

# En Windows, verificar permisos en propiedades del folder
```

### Problema: Tests Fallan

```bash
# Limpiar cache de pytest
pytest --cache-clear

# Re-instalar dependencias
pip install -r requirements.txt --force-reinstall

# Verificar versión de Python
python --version  # Debe ser 3.8+
```

### Problema: Streamlit Cloud Out of Memory

Reducir uso de memoria en `config.py`:

```python
CACHE_CONFIG['max_memory_cache_size'] = 25
SESSION_CONFIG['max_sessions'] = 50
MONITORING_CONFIG['enable_file_logging'] = False
```

---

## Mantenimiento

### Limpieza Periódica

```python
# Script de limpieza
# cleanup.py
from src.utils import get_session_manager, get_cache_manager

session_mgr = get_session_manager()
cache_mgr = get_cache_manager()

# Limpiar sesiones antiguas
session_mgr._cleanup_old_sessions()

# Limpiar caché expirado
cache_mgr.cleanup_expired()

# Comprimir sesiones
session_mgr.compress_old_sessions(days_threshold=7)

print("✓ Limpieza completada")
```

Ejecutar semanalmente:
```bash
python cleanup.py
```

### Monitoreo de Logs

```bash
# Ver logs recientes
tail -f data/logs/performance_$(date +%Y%m%d).log

# Buscar errores
grep ERROR data/logs/*.log

# Ver estadísticas
python -c "
from src.utils import get_performance_monitor
perf = get_performance_monitor()
print(perf.generate_performance_report())
"
```

---

## Recursos Adicionales

- [Documentación Completa](ADVANCED_FEATURES.md)
- [Resumen de Implementación](ADVANCED_FEATURES_SUMMARY.md)
- [Demo Interactiva](examples/advanced_features_demo.py)
- [Tests Unitarios](tests/test_advanced_features.py)

---

## Soporte

Si encuentras problemas:

1. Revisar [Troubleshooting en ADVANCED_FEATURES.md](ADVANCED_FEATURES.md#troubleshooting)
2. Ejecutar tests: `pytest tests/test_advanced_features.py -v`
3. Revisar logs: `data/logs/`
4. Ejecutar demo: `python examples/advanced_features_demo.py`

---

**Última Actualización**: 18 de Noviembre, 2025
**Versión**: 1.0.0
