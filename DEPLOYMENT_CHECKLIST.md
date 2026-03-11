# Markov Chain Model - Technical Guide

Complete documentation for the Markov chain-based employee engagement prediction models.

## Overview

This guide covers the professional implementation of Markov chain models located in `src/models/`. The implementation provides production-ready tools for predicting employee engagement transitions using both analytical and Monte Carlo simulation approaches.

## Architecture

### Core Components

1. **`markov_model.py`**: Core `MarkovEngagementPredictor` class
2. **`predictor.py`**: High-level API functions for ease of use
3. **`__init__.py`**: Package exports and version management

### Model Flow

```
Raw Data → prepare_transitions_data() → Transitions DataFrame
                                              ↓
                              MarkovEngagementPredictor.fit()
                                              ↓
                        Trained Model (transition matrices)
                                              ↓
                              predict_employee_engagement()
                                              ↓
                              Predictions + Analytics
```

## Quick Start

### Installation

```python
# No special installation needed - just ensure dependencies are installed
pip install numpy pandas scipy
```

### Basic Example

```python
from src.models import (
    MarkovEngagementPredictor,
    prepare_transitions_data,
    predict_employee_engagement
)
import pandas as pd

# 1. Load data
data = pd.read_csv('data/data_globant_cleaned.csv')

# 2. Prepare transitions
transitions = prepare_transitions_data(
    data,
    email_col='Email',
    date_col='Date',
    state_col='Engagement Category',
    feature_cols=['Seniority', 'Studio']
)

# 3. Train model
predictor = MarkovEngagementPredictor()
predictor.fit(transitions, features=['Seniority', 'Studio'])

# 4. Make prediction
result = predict_employee_engagement(
    predictor,
    current_state='Alto',
    features={'Seniority': 'Sr', 'Studio': 'Engineering'},
    n_steps=1
)

print(f"Most likely: {result['most_likely_state']}")
print(f"Improvement prob: {result['improvement_probability']:.3f}")
```

## Detailed API Reference

### MarkovEngagementPredictor

#### Initialization

```python
predictor = MarkovEngagementPredictor(
    states=['Bajo', 'Medio', 'Alto', 'Muy Alto'],
    engagement_map={'Muy Alto': 4, 'Alto': 3, 'Medio': 2, 'Bajo': 1}
)
```

**Parameters:**
- `states` (List[str], optional): List of engagement states
- `engagement_map` (Dict[str, int], optional): Mapping from states to numeric values

#### Methods

##### fit()

Train the model on transition data.

```python
predictor.fit(
    transitions_df,           # DataFrame with 'current_state', 'next_state'
    features=['Seniority']    # List of features for conditional matrices
)
```

**Parameters:**
- `transitions_df` (pd.DataFrame): Must contain `current_state` and `next_state` columns
- `features` (List[str], optional): Feature columns for creating conditional matrices

**Returns:** self (for method chaining)

**Example:**
```python
transitions = pd.DataFrame({
    'current_state': ['Alto', 'Medio', 'Alto'],
    'next_state': ['Muy Alto', 'Alto', 'Alto'],
    'Seniority': ['Sr', 'Jr', 'Sr']
})

predictor.fit(transitions, features=['Seniority'])
```

##### predict_next_state()

Get probability distribution over next states.

```python
probs = predictor.predict_next_state(
    current_state='Alto',
    features_dict={'Seniority': 'Sr'},
    n_steps=1
)
# Returns: {'Bajo': 0.05, 'Medio': 0.15, 'Alto': 0.60, 'Muy Alto': 0.20}
```

**Parameters:**
- `current_state` (str): Current engagement state
- `features_dict` (Dict[str, Any], optional): Feature values
- `n_steps` (int): Number of steps ahead (default: 1)

**Returns:** Dict[str, float] mapping states to probabilities

##### predict_most_likely()

Get the most likely next state.

```python
state, prob = predictor.predict_most_likely(
    current_state='Medio',
    features_dict={'Seniority': 'Jr'},
    n_steps=1
)
# Returns: ('Alto', 0.45)
```

**Returns:** Tuple of (most_likely_state, probability)

##### simulate_trajectory()

Run Monte Carlo simulation.

```python
results = predictor.simulate_trajectory(
    initial_state='Alto',
    features_dict={'Seniority': 'Sr'},
    n_steps=10,
    n_simulations=1000,
    random_seed=42
)
```

**Returns:** Dictionary containing:
- `trajectories`: List of simulated state sequences
- `state_probabilities`: Time-series of state probabilities (DataFrame)
- `expected_values`: Expected engagement value at each step
- `confidence_intervals`: 95% CI for engagement values

##### calculate_steady_state()

Calculate long-term equilibrium distribution.

```python
steady = predictor.calculate_steady_state()
# Returns: {'Bajo': 0.10, 'Medio': 0.25, 'Alto': 0.45, 'Muy Alto': 0.20}
```

##### analyze_stability()

Analyze Markov chain properties.

```python
stability = predictor.analyze_stability()
```

**Returns:** Dictionary with:
- `is_ergodic`: Whether all states are reachable
- `is_aperiodic`: Whether chain is aperiodic
- `eigenvalues`: Eigenvalues of transition matrix
- `convergence_rate`: Speed of convergence to steady state

##### calculate_improvement_probability()

Calculate probability of engagement improving.

```python
prob = predictor.calculate_improvement_probability(
    current_state='Medio',
    features_dict={'Studio': 'Engineering'},
    n_steps=1
)
# Returns: 0.35
```

##### calculate_deterioration_probability()

Calculate probability of engagement worsening.

```python
prob = predictor.calculate_deterioration_probability(
    current_state='Alto',
    features_dict={'Studio': 'Design'},
    n_steps=1
)
# Returns: 0.15
```

### High-Level Functions

#### predict_employee_engagement()

Comprehensive prediction with all analytics.

```python
result = predict_employee_engagement(
    predictor,
    current_state='Alto',
    features={'Seniority': 'Sr', 'Studio': 'Engineering'},
    n_steps=3,
    n_simulations=1000,
    include_monte_carlo=True,
    random_seed=42
)
```

**Returns:** Dictionary with:
- `current_state`: Input state
- `features`: Input features
- `analytical_prediction`: Probability distribution
- `most_likely_state`: Most probable state
- `most_likely_probability`: Probability of most likely
- `improvement_probability`: P(engagement increases)
- `deterioration_probability`: P(engagement decreases)
- `stability_probability`: P(stays in same state)
- `monte_carlo`: Simulation results (if enabled)

#### batch_predict()

Predict for multiple employees efficiently.

```python
employees = pd.DataFrame({
    'employee_id': [1, 2, 3],
    'current_state': ['Alto', 'Medio', 'Bajo'],
    'Seniority': ['Sr', 'Jr', 'Ssr']
})

results = batch_predict(
    predictor,
    employees,
    current_state_col='current_state',
    feature_cols=['Seniority'],
    n_steps=1
)
```

**Returns:** DataFrame with original data plus:
- `predicted_state`: Most likely next state
- `prediction_probability`: Probability of prediction
- `improvement_probability`: P(improvement)
- `deterioration_probability`: P(deterioration)

#### compare_scenarios()

What-if scenario analysis.

```python
scenarios = {
    'Junior': {'Seniority': 'Jr'},
    'Senior': {'Seniority': 'Sr'}
}

comparison = compare_scenarios(
    predictor,
    current_state='Medio',
    scenarios=scenarios,
    metric='improvement_probability'
)
```

**Returns:** DataFrame ranked by metric with columns:
- `scenario`: Scenario name
- `features`: Feature dictionary
- `most_likely_state`: Predicted state
- `improvement_prob`: Improvement probability
- `deterioration_prob`: Deterioration probability
- `expected_value`: Expected engagement value
- `metric_value`: Value of comparison metric

#### calculate_confidence_intervals()

Get uncertainty bounds for trajectories.

```python
ci = calculate_confidence_intervals(
    predictor,
    current_state='Alto',
    n_steps=10,
    n_simulations=10000,
    confidence_level=0.95
)
```

**Returns:** DataFrame with:
- `step`: Time step
- `expected_value`: Mean engagement value
- `median`: Median value
- `lower_bound`: Lower CI bound
- `upper_bound`: Upper CI bound
- `std_dev`: Standard deviation

#### analyze_feature_impact()

Understand feature influence on predictions.

```python
impact = analyze_feature_impact(
    predictor,
    current_state='Medio',
    feature_name='Seniority',
    metric='improvement_probability'
)
```

**Returns:** DataFrame ranked by metric showing impact of each feature value.

#### save_model() / load_model()

Model persistence.

```python
# Save
save_model(predictor, 'models/my_model.pkl', include_metadata=True)

# Load
predictor = load_model('models/my_model.pkl')
```

#### prepare_transitions_data()

Convert time-series data to transitions format.

```python
transitions = prepare_transitions_data(
    data,
    email_col='Email',
    date_col='Date',
    state_col='Engagement Category',
    feature_cols=['Seniority', 'Studio'],
    sort_by_date=True
)
```

**Returns:** DataFrame with:
- `current_state`: Current engagement state
- `next_state`: Next engagement state
- Additional feature columns

#### evaluate_model()

Evaluate model performance.

```python
metrics = evaluate_model(
    predictor,
    test_transitions,
    features=['Seniority']
)
```

**Returns:** Dictionary with:
- `accuracy`: Proportion correct predictions
- `top2_accuracy`: Proportion in top 2
- `log_likelihood`: Average log-likelihood
- `perplexity`: Perplexity measure

## Advanced Usage

### Custom States

```python
custom_predictor = MarkovEngagementPredictor(
    states=['Poor', 'Fair', 'Good', 'Excellent'],
    engagement_map={'Poor': 1, 'Fair': 2, 'Good': 3, 'Excellent': 4}
)
```

### Multi-Feature Conditional Models

```python
# Train with multiple features
predictor.fit(transitions, features=['Seniority', 'Studio', 'Position'])

# Predict with feature combinations
result = predict_employee_engagement(
    predictor,
    current_state='Alto',
    features={
        'Seniority': 'Sr',
        'Studio': 'Engineering',
        'Position': 'Tech Lead'
    }
)
```

### Long-Term Forecasting

```python
# Predict 30 steps ahead with confidence intervals
ci = calculate_confidence_intervals(
    predictor,
    current_state='Medio',
    features={'Seniority': 'Jr'},
    n_steps=30,
    n_simulations=10000
)

# Plot trajectory
import matplotlib.pyplot as plt
plt.plot(ci['step'], ci['expected_value'], label='Expected')
plt.fill_between(ci['step'], ci['lower_bound'], ci['upper_bound'],
                 alpha=0.3, label='95% CI')
plt.legend()
plt.show()
```

### Feature Impact Dashboard

```python
# Analyze all features
for feature in ['Seniority', 'Studio', 'Position']:
    impact = analyze_feature_impact(
        predictor,
        current_state='Medio',
        feature_name=feature,
        metric='improvement_probability'
    )
    print(f"\n{feature} Impact:")
    print(impact[['feature_value', 'improvement_prob']])
```

## Best Practices

### Data Preparation

1. **Sufficient Sample Size**: Aim for at least 100 transitions per feature combination
2. **Temporal Ordering**: Always sort by date before creating transitions
3. **Data Quality**: Remove invalid states and handle missing values

```python
# Good practice
data = data.dropna(subset=['Engagement Category'])
data = data[data['Engagement Category'].isin(predictor.states)]
transitions = prepare_transitions_data(data, sort_by_date=True)
```

### Model Training

1. **Start Simple**: Train base model first, then add features
2. **Validate Matrices**: Check conditional matrices have sufficient data

```python
# Train base model
predictor_base = MarkovEngagementPredictor()
predictor_base.fit(transitions)

# Train with features
predictor_full = MarkovEngagementPredictor()
predictor_full.fit(transitions, features=['Seniority'])

# Compare
base_metrics = evaluate_model(predictor_base, test_data)
full_metrics = evaluate_model(predictor_full, test_data, features=['Seniority'])
```

### Predictions

1. **Use Appropriate Method**:
   - Analytical for single-step predictions (faster)
   - Monte Carlo for uncertainty quantification

2. **Set Random Seeds**: For reproducibility

```python
# Reproducible simulation
result = predict_employee_engagement(
    predictor,
    current_state='Alto',
    n_steps=5,
    n_simulations=1000,
    random_seed=42
)
```

### Performance

1. **Cache Models**: Load once, reuse many times
2. **Batch Operations**: Use `batch_predict()` for multiple employees
3. **Limit Simulations**: 1000-5000 often sufficient for stable results

## Troubleshooting

### Issue: "Model must be fitted before making predictions"

**Cause:** Trying to predict before calling `fit()`

**Solution:**
```python
predictor = MarkovEngagementPredictor()
predictor.fit(transitions)  # Must fit first!
result = predict_employee_engagement(predictor, ...)
```

### Issue: "Insufficient data for feature combination"

**Cause:** Too few samples for a specific feature value

**Solutions:**
1. Collect more data
2. Reduce number of features
3. Combine rare feature values

### Issue: Probabilities don't sum to 1.0

**Cause:** Floating-point precision

**Solution:** This is normal and safe to ignore (typically differs by < 1e-10)

### Issue: Slow Monte Carlo simulations

**Solutions:**
1. Reduce `n_simulations`
2. Use analytical predictions for single-step
3. Enable parallel processing (future feature)

```python
# Fast single-step prediction
result = predict_employee_engagement(
    predictor,
    current_state='Alto',
    include_monte_carlo=False  # Much faster
)
```

## Code Examples

See `example_usage.py` for comprehensive examples including:
1. Basic training and prediction
2. Monte Carlo simulation
3. Batch prediction
4. Scenario comparison
5. Feature impact analysis
6. Confidence intervals
7. Model persistence
8. Model evaluation
9. Steady-state analysis

Run examples:
```bash
python example_usage.py
```

## Technical Details

### Transition Matrix Calculation

Transition probability matrix P where P[i,j] = P(next_state=j | current_state=i)

Calculated from transition counts:
```
P[i,j] = count(i→j) / sum_k(count(i→k))
```

### Conditional Matrices

Separate transition matrices for each feature value:
```
P_seniority=Sr[i,j] = P(next_state=j | current_state=i, seniority=Sr)
```

### Multi-Step Predictions

n-step transition probabilities via matrix power:
```
P^n = P × P × ... × P  (n times)
```

### Steady-State Calculation

Solve eigenvector equation:
```
π × P = π
sum(π) = 1
```

Where π is the steady-state distribution.

### Monte Carlo Simulation

1. Start from initial state
2. For each step:
   - Sample next state from transition probabilities
   - Move to sampled state
3. Repeat for n_simulations trajectories
4. Calculate statistics over all trajectories

## Version History

- **1.0.0** (2025-11-18): Initial production release

## Support

For issues or questions, contact the Globant Analytics Team.

---

**Last Updated:** 2025-11-18
**Status:** Production Ready
