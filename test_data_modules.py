"""
Tests for Advanced Features
Tests para SessionManager, ExportManager, CacheManager, PerformanceMonitor
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import json
import time
from datetime import datetime, timedelta

# Importar los módulos a testear
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.utils.session_manager import SessionManager, SessionMetadata
from src.utils.export_manager import ExportManager
from src.utils.cache_manager import CacheManager, CacheEntry
from src.utils.performance_monitor import PerformanceMonitor
from src.utils import helpers
from src.utils import config


# ========================================
# FIXTURES
# ========================================

@pytest.fixture
def temp_dir(tmp_path):
    """Directorio temporal para tests"""
    return tmp_path


@pytest.fixture
def session_manager(temp_dir):
    """SessionManager para tests"""
    return SessionManager(
        sessions_dir=str(temp_dir / "sessions"),
        history_dir=str(temp_dir / "history"),
        backup_dir=str(temp_dir / "backups"),
        auto_cleanup=False
    )


@pytest.fixture
def export_manager(temp_dir):
    """ExportManager para tests"""
    return ExportManager(
        output_dir=str(temp_dir / "exports"),
        temp_dir=str(temp_dir / "temp")
    )


@pytest.fixture
def cache_manager(temp_dir):
    """CacheManager para tests"""
    return CacheManager(
        cache_dir=str(temp_dir / "cache"),
        enable_disk_cache=True
    )


@pytest.fixture
def performance_monitor(temp_dir):
    """PerformanceMonitor para tests"""
    return PerformanceMonitor(
        logs_dir=str(temp_dir / "logs"),
        enable_file_logging=True
    )


@pytest.fixture
def sample_data():
    """Datos de ejemplo"""
    return {
        'prediction': 0.75,
        'current_state': 'Medium',
        'time_horizon': 10,
        'probabilities': {
            'Low': 0.15,
            'Medium': 0.35,
            'High': 0.50
        }
    }


@pytest.fixture
def sample_dataframe():
    """DataFrame de ejemplo"""
    return pd.DataFrame({
        'user_id': range(100),
        'date': pd.date_range('2024-01-01', periods=100),
        'engagement': np.random.rand(100)
    })


# ========================================
# TESTS: SessionManager
# ========================================

class TestSessionManager:
    """Tests para SessionManager"""

    def test_save_and_load_session(self, session_manager):
        """Test guardar y cargar sesión"""
        session_id = "test_session_001"
        session_data = {'test': 'data', 'value': 123}

        # Guardar
        assert session_manager.save_session(session_id, session_data)

        # Cargar
        loaded_data = session_manager.load_session(session_id)
        assert loaded_data is not None
        assert loaded_data['data']['test'] == 'data'
        assert loaded_data['data']['value'] == 123

    def test_get_all_sessions(self, session_manager):
        """Test obtener todas las sesiones"""
        # Crear varias sesiones
        for i in range(5):
            session_manager.save_session(f"session_{i}", {'index': i})

        sessions = session_manager.get_all_sessions()
        assert len(sessions) == 5

    def test_delete_session(self, session_manager):
        """Test eliminar sesión"""
        session_id = "delete_me"
        session_manager.save_session(session_id, {'data': 'test'})

        # Eliminar
        assert session_manager.delete_session(session_id)

        # Verificar que no existe
        loaded = session_manager.load_session(session_id)
        assert loaded is None

    def test_save_prediction_to_history(self, session_manager, sample_data):
        """Test guardar predicción en historial"""
        assert session_manager.save_prediction_to_history(sample_data)

        history = session_manager.get_prediction_history()
        assert len(history) > 0
        assert history[0]['prediction'] == 0.75

    def test_export_history(self, session_manager, sample_data):
        """Test exportar historial"""
        # Agregar algunas predicciones
        for i in range(3):
            session_manager.save_prediction_to_history(sample_data)

        # Exportar como JSON
        export_path = session_manager.export_history(format='json')
        assert export_path is not None
        assert Path(export_path).exists()

    def test_user_preferences(self, session_manager):
        """Test guardar y cargar preferencias"""
        prefs = {'theme': 'dark', 'language': 'en'}

        assert session_manager.save_user_preferences(prefs)

        loaded_prefs = session_manager.load_user_preferences()
        assert loaded_prefs['theme'] == 'dark'
        assert loaded_prefs['language'] == 'en'


# ========================================
# TESTS: ExportManager
# ========================================

class TestExportManager:
    """Tests para ExportManager"""

    def test_export_to_json(self, export_manager, sample_data):
        """Test exportar a JSON"""
        output_path = export_manager.export_to_json(sample_data)

        assert Path(output_path).exists()

        # Verificar contenido
        with open(output_path, 'r') as f:
            loaded = json.load(f)
        assert loaded['prediction'] == 0.75

    def test_export_to_csv(self, export_manager, sample_dataframe):
        """Test exportar a CSV"""
        output_path = export_manager.export_to_csv(sample_dataframe)

        assert Path(output_path).exists()

        # Verificar contenido
        df = pd.read_csv(output_path)
        assert len(df) == 100
        assert 'user_id' in df.columns

    def test_export_to_excel(self, export_manager, sample_data):
        """Test exportar a Excel"""
        output_path = export_manager.export_to_excel(sample_data)

        assert Path(output_path).exists()

        # Verificar que se puede leer
        df = pd.read_excel(output_path, sheet_name='Summary')
        assert len(df) > 0

    def test_export_to_pdf(self, export_manager, sample_data):
        """Test exportar a PDF"""
        output_path = export_manager.export_to_pdf(
            sample_data,
            report_type='prediction'
        )

        assert Path(output_path).exists()


# ========================================
# TESTS: CacheManager
# ========================================

class TestCacheManager:
    """Tests para CacheManager"""

    def test_cache_and_retrieve_data(self, cache_manager):
        """Test cachear y recuperar datos"""
        key = "test_key"
        data = {'value': 123}

        # Cachear
        assert cache_manager.cache_data(key, data)

        # Recuperar
        cached_data = cache_manager.get_cached_data(key)
        assert cached_data is not None
        assert cached_data['value'] == 123

    def test_cache_expiration(self, cache_manager):
        """Test expiración de caché"""
        key = "expire_me"
        data = "test data"

        # Cachear con TTL muy corto
        cache_manager.cache_data(key, data, ttl=1)

        # Debe existir inmediatamente
        assert cache_manager.get_cached_data(key) == "test data"

        # Esperar a que expire
        time.sleep(1.1)

        # No debe existir
        assert cache_manager.get_cached_data(key) is None

    def test_invalidate_cache(self, cache_manager):
        """Test invalidar caché"""
        key = "invalidate_me"
        cache_manager.cache_data(key, "data")

        # Invalidar
        assert cache_manager.invalidate_cache(key)

        # No debe existir
        assert cache_manager.get_cached_data(key) is None

    def test_clear_all_cache(self, cache_manager):
        """Test limpiar todo el caché"""
        # Cachear varios items
        for i in range(5):
            cache_manager.cache_data(f"key_{i}", f"data_{i}")

        # Limpiar todo
        assert cache_manager.clear_all_cache()

        # Verificar que no existen
        for i in range(5):
            assert cache_manager.get_cached_data(f"key_{i}") is None

    def test_cache_stats(self, cache_manager):
        """Test estadísticas de caché"""
        # Cachear y recuperar datos
        cache_manager.cache_data("key1", "data1")
        cache_manager.get_cached_data("key1")  # hit
        cache_manager.get_cached_data("key2")  # miss

        stats = cache_manager.get_cache_stats()
        assert stats['hits'] >= 1
        assert stats['misses'] >= 1
        assert 'hit_rate' in stats

    def test_cache_matrix(self, cache_manager):
        """Test cachear matriz"""
        matrix_type = "transition"
        conditions = {'state': 'Medium', 'context': 'test'}
        matrix_data = [[0.1, 0.3, 0.6], [0.2, 0.4, 0.4], [0.3, 0.3, 0.4]]

        # Cachear
        assert cache_manager.cache_matrix(matrix_type, conditions, matrix_data)

        # Recuperar
        cached_matrix = cache_manager.get_cached_matrix(matrix_type, conditions)
        assert cached_matrix is not None
        assert len(cached_matrix) == 3


# ========================================
# TESTS: PerformanceMonitor
# ========================================

class TestPerformanceMonitor:
    """Tests para PerformanceMonitor"""

    def test_timer(self, performance_monitor):
        """Test timer de operaciones"""
        operation = "test_operation"

        performance_monitor.start_timer(operation)
        time.sleep(0.1)  # Simular trabajo
        duration = performance_monitor.end_timer(operation)

        assert duration is not None
        assert duration >= 100  # Al menos 100ms

    def test_measure_context_manager(self, performance_monitor):
        """Test context manager para medir"""
        with performance_monitor.measure("test_context"):
            time.sleep(0.05)

        stats = performance_monitor.get_performance_stats()
        assert "test_context" in stats

    def test_log_operation(self, performance_monitor):
        """Test log de operación"""
        performance_monitor.log_operation(
            "test_op",
            duration_ms=150.5,
            metadata={'key': 'value'}
        )

        stats = performance_monitor.get_performance_stats()
        assert "test_op" in stats
        assert stats["test_op"]["count"] >= 1

    def test_generate_performance_report(self, performance_monitor):
        """Test generar reporte"""
        # Ejecutar algunas operaciones
        for i in range(3):
            with performance_monitor.measure(f"op_{i}"):
                time.sleep(0.01)

        report = performance_monitor.generate_performance_report()
        assert 'operations' in report
        assert 'system' in report
        assert 'app' in report

    def test_log_error(self, performance_monitor):
        """Test log de error"""
        try:
            raise ValueError("Test error")
        except Exception as e:
            performance_monitor.log_error(e, context={'test': True})

        # Verificar que se registró
        assert len(performance_monitor.errors) > 0


# ========================================
# TESTS: Helpers
# ========================================

class TestHelpers:
    """Tests para funciones helper"""

    def test_validate_email(self):
        """Test validación de email"""
        assert helpers.validate_email("test@example.com")
        assert not helpers.validate_email("invalid-email")

    def test_validate_date_range(self):
        """Test validación de rango de fechas"""
        start = "2024-01-01"
        end = "2024-12-31"
        assert helpers.validate_date_range(start, end)

        # Rango inválido
        assert not helpers.validate_date_range(end, start)

    def test_format_percentage(self):
        """Test formateo de porcentaje"""
        assert helpers.format_percentage(0.75) == "75.0%"
        assert helpers.format_percentage(0.123, decimals=2) == "12.30%"

    def test_format_number(self):
        """Test formateo de número"""
        assert helpers.format_number(1500) == "1.5K"
        assert helpers.format_number(1500000) == "1.5M"
        assert helpers.format_number(1500000000) == "1.5B"

    def test_calculate_delta_percentage(self):
        """Test cálculo de cambio porcentual"""
        delta = helpers.calculate_delta_percentage(150, 100)
        assert delta == 50.0

    def test_get_trend_direction(self):
        """Test dirección de tendencia"""
        increasing = [1, 2, 3, 4, 5]
        assert helpers.get_trend_direction(increasing) == '↑'

        decreasing = [5, 4, 3, 2, 1]
        assert helpers.get_trend_direction(decreasing) == '↓'

    def test_detect_anomalies(self):
        """Test detección de anomalías"""
        normal_data = pd.Series([1, 2, 3, 4, 5, 4, 3, 2, 1])
        data_with_outlier = pd.Series([1, 2, 3, 4, 100, 4, 3, 2, 1])

        anomalies = helpers.detect_anomalies(data_with_outlier, method='iqr')
        assert anomalies.any()  # Debe detectar al menos una anomalía


# ========================================
# TESTS: Config
# ========================================

class TestConfig:
    """Tests para configuración"""

    def test_get_config(self):
        """Test obtener configuración"""
        cache_config = config.get_config('cache')
        assert 'default_ttl' in cache_config

    def test_is_feature_enabled(self):
        """Test verificar feature"""
        assert config.is_feature_enabled('enable_cache') in [True, False]

    def test_get_cache_ttl(self):
        """Test obtener TTL de caché"""
        ttl = config.get_cache_ttl('data')
        assert ttl > 0


# ========================================
# RUN TESTS
# ========================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
