"""
Unit tests for Markov engagement prediction models.

Run with: pytest tests/test_markov_model.py -v
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import (
    MarkovEngagementPredictor,
    predict_employee_engagement,
    batch_predict,
    compare_scenarios,
    prepare_transitions_data,
    calculate_transition_matrix,
    save_model,
    load_model,
)


@pytest.fixture
def sample_transitions():
    """Create sample transition data for testing."""
    np.random.seed(42)
    states = ['Bajo', 'Medio', 'Alto', 'Muy Alto']

    transitions = []
    for _ in range(200):
        curr = np.random.choice(states)
        # Bias towards staying or improving
        if curr == 'Bajo':
            next_state = np.random.choice(['Bajo', 'Medio', 'Alto'], p=[0.4, 0.5, 0.1])
        elif curr == 'Medio':
            next_state = np.random.choice(['Bajo', 'Medio', 'Alto'], p=[0.2, 0.5, 0.3])
        elif curr == 'Alto':
            next_state = np.random.choice(['Medio', 'Alto', 'Muy Alto'], p=[0.2, 0.5, 0.3])
        else:  # Muy Alto
            next_state = np.random.choice(['Alto', 'Muy Alto'], p=[0.3, 0.7])

        transitions.append({
            'current_state': curr,
            'next_state': next_state,
            'Seniority': np.random.choice(['Jr', 'Ssr', 'Sr']),
            'Studio': np.random.choice(['Engineering', 'Design'])
        })

    return pd.DataFrame(transitions)


@pytest.fixture
def fitted_predictor(sample_transitions):
    """Create a fitted predictor for testing."""
    predictor = MarkovEngagementPredictor()
    predictor.fit(sample_transitions, features=['Seniority', 'Studio'])
    return predictor


class TestMarkovEngagementPredictor:
    """Test the core MarkovEngagementPredictor class."""

    def test_initialization(self):
        """Test predictor initialization."""
        predictor = MarkovEngagementPredictor()

        assert predictor.states == ['Bajo', 'Medio', 'Alto', 'Muy Alto']
        assert predictor.engagement_map == {
            'Muy Alto': 4, 'Alto': 3, 'Medio': 2, 'Bajo': 1
        }
        assert not predictor.is_fitted
        assert predictor.transition_matrix is None

    def test_custom_initialization(self):
        """Test initialization with custom states."""
        custom_states = ['Low', 'High']
        custom_map = {'Low': 1, 'High': 2}

        predictor = MarkovEngagementPredictor(
            states=custom_states,
            engagement_map=custom_map
        )

        assert predictor.states == custom_states
        assert predictor.engagement_map == custom_map

    def test_fit(self, sample_transitions):
        """Test model fitting."""
        predictor = MarkovEngagementPredictor()
        predictor.fit(sample_transitions, features=['Seniority'])

        assert predictor.is_fitted
        assert predictor.transition_matrix is not None
        assert predictor.transition_matrix.shape == (4, 4)
        assert 'Seniority' in predictor.conditional_matrices

        # Check probabilities sum to 1
        for i in range(4):
            assert np.isclose(predictor.transition_matrix[i].sum(), 1.0)

    def test_predict_next_state(self, fitted_predictor):
        """Test single-step prediction."""
        result = fitted_predictor.predict_next_state('Alto')

        assert isinstance(result, dict)
        assert set(result.keys()) == set(fitted_predictor.states)
        assert np.isclose(sum(result.values()), 1.0)
        assert all(0 <= p <= 1 for p in result.values())

    def test_predict_most_likely(self, fitted_predictor):
        """Test most likely state prediction."""
        state, prob = fitted_predictor.predict_most_likely('Medio')

        assert state in fitted_predictor.states
        assert 0 <= prob <= 1

    def test_multi_step_prediction(self, fitted_predictor):
        """Test multi-step prediction."""
        result = fitted_predictor.predict_next_state('Bajo', n_steps=3)

        assert isinstance(result, dict)
        assert np.isclose(sum(result.values()), 1.0)

    def test_conditional_prediction(self, fitted_predictor):
        """Test prediction with features."""
        result = fitted_predictor.predict_next_state(
            'Alto',
            features_dict={'Seniority': 'Sr', 'Studio': 'Engineering'}
        )

        assert isinstance(result, dict)
        assert np.isclose(sum(result.values()), 1.0)

    def test_simulate_trajectory(self, fitted_predictor):
        """Test Monte Carlo simulation."""
        results = fitted_predictor.simulate_trajectory(
            initial_state='Medio',
            n_steps=5,
            n_simulations=100,
            random_seed=42
        )

        assert 'trajectories' in results
        assert 'state_probabilities' in results
        assert 'expected_values' in results
        assert 'confidence_intervals' in results

        assert len(results['trajectories']) == 100
        assert len(results['trajectories'][0]) == 6  # initial + 5 steps
        assert len(results['expected_values']) == 6

    def test_calculate_steady_state(self, fitted_predictor):
        """Test steady-state calculation."""
        steady_state = fitted_predictor.calculate_steady_state()

        assert isinstance(steady_state, dict)
        assert set(steady_state.keys()) == set(fitted_predictor.states)
        assert np.isclose(sum(steady_state.values()), 1.0)
        assert all(0 <= p <= 1 for p in steady_state.values())

    def test_analyze_stability(self, fitted_predictor):
        """Test stability analysis."""
        stability = fitted_predictor.analyze_stability()

        assert 'is_ergodic' in stability
        assert 'is_aperiodic' in stability
        assert 'eigenvalues' in stability
        assert 'convergence_rate' in stability

        assert isinstance(stability['is_ergodic'], bool)
        assert isinstance(stability['is_aperiodic'], bool)

    def test_improvement_probability(self, fitted_predictor):
        """Test improvement probability calculation."""
        prob = fitted_predictor.calculate_improvement_probability('Medio')

        assert isinstance(prob, float)
        assert 0 <= prob <= 1

    def test_deterioration_probability(self, fitted_predictor):
        """Test deterioration probability calculation."""
        prob = fitted_predictor.calculate_deterioration_probability('Alto')

        assert isinstance(prob, float)
        assert 0 <= prob <= 1

    def test_invalid_state_raises_error(self, fitted_predictor):
        """Test that invalid state raises ValueError."""
        with pytest.raises(ValueError, match="Invalid state"):
            fitted_predictor.predict_next_state('Invalid State')

    def test_unfitted_predictor_raises_error(self):
        """Test that unfitted predictor raises error."""
        predictor = MarkovEngagementPredictor()

        with pytest.raises(RuntimeError, match="must be fitted"):
            predictor.predict_next_state('Alto')


class TestHighLevelFunctions:
    """Test high-level API functions."""

    def test_predict_employee_engagement(self, fitted_predictor):
        """Test comprehensive prediction function."""
        result = predict_employee_engagement(
            fitted_predictor,
            current_state='Alto',
            features={'Seniority': 'Sr'},
            n_steps=1,
            include_monte_carlo=False
        )

        assert 'current_state' in result
        assert 'analytical_prediction' in result
        assert 'most_likely_state' in result
        assert 'improvement_probability' in result
        assert 'deterioration_probability' in result
        assert result['current_state'] == 'Alto'

    def test_predict_employee_engagement_with_mc(self, fitted_predictor):
        """Test prediction with Monte Carlo."""
        result = predict_employee_engagement(
            fitted_predictor,
            current_state='Medio',
            n_steps=3,
            n_simulations=100,
            include_monte_carlo=True,
            random_seed=42
        )

        assert 'monte_carlo' in result
        assert 'trajectories' in result['monte_carlo']

    def test_batch_predict(self, fitted_predictor):
        """Test batch prediction."""
        employees = pd.DataFrame({
            'employee_id': [1, 2, 3],
            'current_state': ['Alto', 'Medio', 'Bajo'],
            'Seniority': ['Sr', 'Jr', 'Ssr']
        })

        results = batch_predict(
            fitted_predictor,
            employees,
            current_state_col='current_state',
            feature_cols=['Seniority']
        )

        assert len(results) == 3
        assert 'predicted_state' in results.columns
        assert 'improvement_probability' in results.columns
        assert 'employee_id' in results.columns

    def test_compare_scenarios(self, fitted_predictor):
        """Test scenario comparison."""
        scenarios = {
            'Junior': {'Seniority': 'Jr'},
            'Senior': {'Seniority': 'Sr'}
        }

        comparison = compare_scenarios(
            fitted_predictor,
            current_state='Medio',
            scenarios=scenarios,
            metric='improvement_probability'
        )

        assert len(comparison) == 2
        assert 'scenario' in comparison.columns
        assert 'most_likely_state' in comparison.columns
        assert 'metric_value' in comparison.columns

    def test_prepare_transitions_data(self):
        """Test transition data preparation."""
        # Create sample time-series data
        data = pd.DataFrame({
            'Email': ['emp1@test.com', 'emp1@test.com', 'emp2@test.com', 'emp2@test.com'],
            'Date': ['2023-01-01', '2023-01-02', '2023-01-01', '2023-01-02'],
            'Engagement Category': ['Alto', 'Muy Alto', 'Medio', 'Alto'],
            'Seniority': ['Sr', 'Sr', 'Jr', 'Jr']
        })

        transitions = prepare_transitions_data(
            data,
            email_col='Email',
            date_col='Date',
            state_col='Engagement Category',
            feature_cols=['Seniority']
        )

        assert len(transitions) == 2  # 2 employees, 1 transition each
        assert 'current_state' in transitions.columns
        assert 'next_state' in transitions.columns
        assert 'Seniority' in transitions.columns
        assert transitions.iloc[0]['current_state'] == 'Alto'
        assert transitions.iloc[0]['next_state'] == 'Muy Alto'


class TestModelPersistence:
    """Test model saving and loading."""

    def test_save_and_load_model(self, fitted_predictor, tmp_path):
        """Test model persistence."""
        # Save model
        model_path = tmp_path / "test_model.pkl"
        save_model(fitted_predictor, model_path)

        assert model_path.exists()

        # Load model
        loaded_predictor = load_model(model_path)

        assert loaded_predictor.is_fitted
        assert loaded_predictor.states == fitted_predictor.states
        assert np.allclose(
            loaded_predictor.transition_matrix,
            fitted_predictor.transition_matrix
        )

    def test_load_nonexistent_model_raises_error(self):
        """Test that loading nonexistent model raises error."""
        with pytest.raises(FileNotFoundError):
            load_model('nonexistent_model.pkl')


class TestMatrixUtilities:
    """Test matrix utility functions."""

    def test_calculate_transition_matrix(self, sample_transitions):
        """Test standalone transition matrix calculation."""
        states = ['Bajo', 'Medio', 'Alto', 'Muy Alto']
        matrix = calculate_transition_matrix(sample_transitions, states)

        assert matrix.shape == (4, 4)
        for i in range(4):
            assert np.isclose(matrix[i].sum(), 1.0)


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_single_transition_per_state(self):
        """Test with minimal data."""
        transitions = pd.DataFrame({
            'current_state': ['Bajo', 'Medio', 'Alto'],
            'next_state': ['Medio', 'Alto', 'Muy Alto']
        })

        predictor = MarkovEngagementPredictor()
        predictor.fit(transitions)

        assert predictor.is_fitted
        assert predictor.transition_matrix is not None

    def test_missing_current_state_column(self):
        """Test error when required column is missing."""
        bad_data = pd.DataFrame({
            'state': ['Alto', 'Medio'],
            'next': ['Muy Alto', 'Alto']
        })

        predictor = MarkovEngagementPredictor()
        with pytest.raises(ValueError, match="must contain"):
            predictor.fit(bad_data)

    def test_empty_dataframe(self):
        """Test with empty DataFrame."""
        empty_df = pd.DataFrame({
            'current_state': [],
            'next_state': []
        })

        predictor = MarkovEngagementPredictor()
        predictor.fit(empty_df)

        # Should handle gracefully (uniform distribution fallback)
        assert predictor.is_fitted

    def test_reproducibility_with_seed(self, fitted_predictor):
        """Test that random seed ensures reproducibility."""
        result1 = predict_employee_engagement(
            fitted_predictor,
            current_state='Medio',
            n_steps=5,
            n_simulations=100,
            random_seed=42
        )

        result2 = predict_employee_engagement(
            fitted_predictor,
            current_state='Medio',
            n_steps=5,
            n_simulations=100,
            random_seed=42
        )

        # Should be identical
        assert result1['monte_carlo']['trajectories'] == result2['monte_carlo']['trajectories']


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
