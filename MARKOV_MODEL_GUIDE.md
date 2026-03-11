# Advanced Features - Quick Reference

Sistema de características avanzadas enterprise-level para Engagement Prediction System.

## Índice Rápido

- [Instalación](#instalación-rápida)
- [Uso Básico](#uso-básico)
- [Módulos](#módulos-disponibles)
- [Documentación](#documentación-completa)

---

## Instalación Rápida

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Verificar instalación
python examples/advanced_features_demo.py

# 3. Ejecutar tests
pytest tests/test_advanced_features.py -v
```

---

## Uso Básico

### Importar Todo

```python
from src.utils import (
    # Session Management
    get_session_manager,

    # Export Management
    get_export_manager,

    # Cache Management
    get_cache_manager,

    # Performance Monitoring
    get_performance_monitor,

    # Streamlit Utilities
    cache_predictions,
    lazy_load_chart,
    run_with_progress,

    # Helpers
    format_percentage,
    format_number,
    validate_email,
    calculate_delta_percentage
)
```

### 1. Sesiones

```python
session_mgr = get_session_manager()

# Guardar
session_mgr.save_session('session_001', data)

# Cargar
session = session_mgr.load_session('session_001')

# Historial
session_mgr.save_prediction_to_history(prediction)
history = session_mgr.get_prediction_history(limit=10)
```

### 2. Exportación

```python
export_mgr = get_export_manager()

# PDF
export_mgr.export_to_pdf(data, 'prediction')

# Excel
export_mgr.export_to_excel(data)

# Todo
files = export_mgr.generate_full_report(prediction_result)
```

### 3. Caché

```python
cache_mgr = get_cache_manager()

# Cachear
cache_mgr.cache_data('key', data, ttl=3600)

# Recuperar
cached = cache_mgr.get_cached_data('key')

# Stats
stats = cache_mgr.get_cache_stats()
```

### 4. Performance

```python
perf = get_performance_monitor()

# Medir
with perf.measure('operation'):
    # ... código ...
    pass

# Stats
stats = perf.get_performance_stats()
```

### 5. Streamlit

```python
# Cachear predicciones
@cache_predictions(ttl=1800)
def predict(model, data):
    return model.predict(data)

# Lazy load
lazy_load_chart(
    create_chart,
    expander_label="View Chart"
)

# Progress bar
result = run_with_progress(
    heavy_function,
    args,
    progress_text="Processing..."
)
```

---

## Módulos Disponibles

### Core Managers

| Módulo | Descripción | Singleton |
|--------|-------------|-----------|
| `SessionManager` | Gestión de sesiones | ✅ |
| `ExportManager` | Exportación reportes | ✅ |
| `CacheManager` | Caché inteligente | ✅ |
| `PerformanceMonitor` | Monitoreo performance | ✅ |

### Utilities

| Módulo | Funciones | Descripción |
|--------|-----------|-------------|
| `helpers` | 40+ | Validación, formateo, análisis |
| `config` | - | Configuración centralizada |
| `streamlit_cache` | 5 | Decorators de caché |
| `async_processor` | - | Procesamiento asíncrono |
| `lazy_loader` | 6 | Lazy loading componentes |

---

## Documentación Completa

### Guías Principales

1. **[ADVANCED_FEATURES.md](ADVANCED_FEATURES.md)** - Documentación completa
   - Guías de uso detalladas
   - Ejemplos de código
   - API reference
   - Best practices
   - Troubleshooting

2. **[ADVANCED_FEATURES_SUMMARY.md](ADVANCED_FEATURES_SUMMARY.md)** - Resumen
   - Resumen ejecutivo
   - Lista de features
   - Estructura de archivos
   - Métricas

3. **[ADVANCED_FEATURES_SETUP.md](ADVANCED_FEATURES_SETUP.md)** - Setup
   - Instalación paso a paso
   - Verificación
   - Configuración
   - Integración
   - Deployment

4. **[IMPLEMENTATION_REPORT_ADVANCED.md](IMPLEMENTATION_REPORT_ADVANCED.md)** - Reporte
   - Reporte técnico completo
   - Métricas de implementación
   - Status de features

### Ejemplos y Tests

- **Demo**: `examples/advanced_features_demo.py`
- **Tests**: `tests/test_advanced_features.py`

---

## Features Principales

### ✅ Session Management
- Persistencia en JSON
- Auto-guardado
- Historial de predicciones
- Preferencias de usuario
- Backups automáticos

### ✅ Export Management
- PDF profesionales
- Excel multi-sheet
- CSV y JSON
- Gráficos embebidos
- Reportes ejecutivos

### ✅ Cache Management
- LRU en memoria
- Persistencia en disco
- TTL configurable
- Estadísticas hit/miss
- Limpieza automática

### ✅ Performance Monitoring
- Timing de operaciones
- Tracking de memoria
- Logging a archivos
- Reportes detallados
- Context managers

### ✅ Streamlit Optimizations
- Smart caching
- Async processing
- Lazy loading
- Progress tracking

### ✅ Helper Functions
- 40+ funciones auxiliares
- Validación
- Formateo
- Conversión
- Análisis de datos

---

## Quick Commands

```bash
# Ejecutar demo
python examples/advanced_features_demo.py

# Ejecutar tests
pytest tests/test_advanced_features.py -v

# Con coverage
pytest tests/test_advanced_features.py --cov=src/utils

# Limpiar caché
python -c "from src.utils import get_cache_manager; get_cache_manager().clear_all_cache()"

# Ver stats
python -c "from src.utils import get_session_manager; print(get_session_manager().get_session_stats())"
```

---

## Integración con Streamlit

### Template Básico

```python
import streamlit as st
from src.utils import (
    get_session_manager,
    get_export_manager,
    cache_predictions
)

# Init
st.set_page_config(page_title="My App", layout="wide")

# Managers
session_mgr = get_session_manager()
export_mgr = get_export_manager()

# Cache predictions
@cache_predictions(ttl=1800)
def predict(data):
    return model.predict(data)

# Main app
st.title("My App")

# Your code here...

# Export button
if st.button("Export"):
    pdf = export_mgr.export_to_pdf(result, 'prediction')
    st.success(f"Exported: {pdf}")
```

---

## Configuration

### Archivo: `src/utils/config.py`

```python
from src.utils.config import (
    get_config,
    is_feature_enabled,
    get_cache_ttl,
    CACHE_CONFIG,
    FEATURE_FLAGS
)

# Obtener config
cache_config = get_config('cache')

# Verificar feature
if is_feature_enabled('enable_cache'):
    # ...
    pass

# TTL de caché
ttl = get_cache_ttl('predictions')
```

---

## Estructura de Directorios

```
engagement-prediction-app/
├── src/utils/
│   ├── session_manager.py      # ✅ Session management
│   ├── export_manager.py       # ✅ Export reports
│   ├── cache_manager.py        # ✅ Intelligent cache
│   ├── performance_monitor.py  # ✅ Performance monitoring
│   ├── helpers.py              # ✅ Helper functions
│   ├── config.py               # ✅ Configuration
│   ├── streamlit_cache.py      # ✅ Streamlit cache
│   ├── async_processor.py      # ✅ Async processing
│   └── lazy_loader.py          # ✅ Lazy loading
├── tests/
│   └── test_advanced_features.py  # ✅ 33+ tests
├── examples/
│   └── advanced_features_demo.py  # ✅ Interactive demo
├── data/                       # Auto-created
│   ├── sessions/
│   ├── history/
│   ├── cache/
│   ├── exports/
│   └── logs/
└── Documentation
    ├── ADVANCED_FEATURES.md
    ├── ADVANCED_FEATURES_SUMMARY.md
    ├── ADVANCED_FEATURES_SETUP.md
    └── IMPLEMENTATION_REPORT_ADVANCED.md
```

---

## Troubleshooting Rápido

### Problema: Tests fallan

```bash
# Reinstalar deps
pip install -r requirements.txt --force-reinstall

# Limpiar cache
pytest --cache-clear

# Verificar Python version
python --version  # Debe ser 3.8+
```

### Problema: Import error

```python
# Verificar que estés en el directorio correcto
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
```

### Problema: Permisos

```bash
# Linux/Mac
chmod -R 755 data/

# Windows: Verificar permisos en propiedades del folder
```

---

## Soporte

### Recursos

- 📖 [Documentación Completa](ADVANCED_FEATURES.md)
- 🚀 [Guía de Setup](ADVANCED_FEATURES_SETUP.md)
- 📊 [Resumen](ADVANCED_FEATURES_SUMMARY.md)
- 📋 [Reporte Técnico](IMPLEMENTATION_REPORT_ADVANCED.md)

### Troubleshooting

Ver sección de Troubleshooting en:
- [ADVANCED_FEATURES.md#troubleshooting](ADVANCED_FEATURES.md#troubleshooting)
- [ADVANCED_FEATURES_SETUP.md#troubleshooting](ADVANCED_FEATURES_SETUP.md#troubleshooting)

### Contact

Si encuentras problemas:
1. Revisar documentación
2. Ejecutar demo: `python examples/advanced_features_demo.py`
3. Ejecutar tests: `pytest tests/test_advanced_features.py -v`
4. Revisar logs: `data/logs/`

---

## Changelog

### v1.0.0 (2025-11-18)
- ✅ Initial release
- ✅ SessionManager implemented
- ✅ ExportManager implemented
- ✅ CacheManager implemented
- ✅ PerformanceMonitor implemented
- ✅ 40+ helper functions
- ✅ Streamlit optimizations
- ✅ 33+ unit tests
- ✅ Complete documentation

---

## License

Parte del proyecto Engagement Prediction System.

---

**Version**: 1.0.0
**Status**: ✅ Production Ready
**Last Updated**: 18 de Noviembre, 2025
