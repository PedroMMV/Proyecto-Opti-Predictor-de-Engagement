# Markov Model - Quick Start Guide

Get started with the Markov engagement prediction models in 5 minutes.

## Installation

```bash
# Ensure you have the required dependencies
pip install numpy pandas scipy

# Optional: for running tests
pip install pytest
```

## Quick Start (5 steps)

### Step 1: Import the models

```python
from src.models import (
    MarkovEngagementPredictor,
    prepare_transitions_data,
    predict_employee_engagement
)
import pandas as pd
```

### Step 2: Load your data

```python
# Load the engagement data
data = pd.read_csv('data/data_globant_cleaned.csv')
print(f"Loaded {len(data)} records")
```

### Step 3: Prepare transition data

```python
# Convert time-series data to transitions
transitions = prepare_transitions_data(
    data,
    email_col='Email',
    date_col='Date',
    state_col='Engagement Category',
    feature_cols=['Seniority', 'Studio']
)
print(f"Created {len(transitions)} transitions")
```

### Step 4: Train the model

```python
# Initialize and train the predictor
predictor = MarkovEngagementPredictor()
predictor.fit(transitions, features=['Seniority', 'Studio'])
print("Model trained!")
```

### Step 5: Make predictions

```python
# Predict for a single employee
result = predict_employee_engagement(
    predictor,
    current_state='Alto',
    features={'Seniority': 'Sr', 'Studio': 'Engineering'},
    n_steps=1
)

print(f"\nMost likely next state: {result['most_likely_state']}")
print(f"Probability: {result['most_likely_probability']:.3f}")
print(f"Improvement probability: {result['improvement_probability']:.3f}")
print(f"Deterioration probability: {result['deterioration_probability']:.3f}")
```

## Complete Example

```python
from src.models import (
    MarkovEngagementPredictor,
    prepare_transitions_data,
    predict_employee_engagement,
    batch_predict,
    save_model
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
    feature_cols=['Seniority', 'Studio', 'Position']
)

# 3. Train model
predictor = MarkovEngagementPredictor()
predictor.fit(transitions, features=['Seniority', 'Studio'])

# 4. Single prediction
result = predict_employee_engagement(
    predictor,
    current_state='Alto',
    features={'Seniority': 'Sr', 'Studio': 'Engineering'},
    n_steps=1
)

print(f"Prediction: {result['most_likely_state']} (p={result['most_likely_probability']:.3f})")

# 5. Batch predictions
employees = pd.DataFrame({
    'employee_id': [1, 2, 3, 4],
    'name': ['Alice', 'Bob', 'Charlie', 'Diana'],
    'current_state': ['Alto', 'Medio', 'Bajo', 'Muy Alto'],
    'Seniority': ['Sr', 'Jr', 'Ssr', 'Sr'],
    'Studio': ['Engineering', 'Design', 'Engineering', 'Design']
})

results = batch_predict(
    predictor,
    employees,
    current_state_col='current_state',
    feature_cols=['Seniority', 'Studio']
)

print("\nBatch Predictions:")
print(results[['name', 'current_state', 'predicted_state', 'improvement_probability']])

# 6. Save model for later use
save_model(predictor, 'models/my_engagement_model.pkl')
print("\nModel saved!")
```

## Common Use Cases

### Use Case 1: Predict for a specific employee

```python
result = predict_employee_engagement(
    predictor,
    current_state='Medio',
    features={'Seniority': 'Jr', 'Studio': 'Engineering'},
    n_steps=1,
    include_monte_carlo=False  # Faster without Monte Carlo
)

print(f"Most likely: {result['most_likely_state']}")
print(f"Full distribution: {result['analytical_prediction']}")
```

### Use Case 2: Predict multiple steps ahead

```python
result = predict_employee_engagement(
    predictor,
    current_state='Alto',
    features={'Seniority': 'Sr'},
    n_steps=5,  # Predict 5 steps ahead
    include_monte_carlo=True,
    n_simulations=1000
)

# View trajectory
mc = result['monte_carlo']
print("Expected values over time:")
for i, val in enumerate(mc['expected_values']):
    print(f"  Step {i}: {val:.2f}")
```

### Use Case 3: Compare different scenarios

```python
from src.models import compare_scenarios

scenarios = {
    'Junior Engineer': {'Seniority': 'Jr', 'Studio': 'Engineering'},
    'Senior Engineer': {'Seniority': 'Sr', 'Studio': 'Engineering'},
    'Senior Designer': {'Seniority': 'Sr', 'Studio': 'Design'}
}

comparison = compare_scenarios(
    predictor,
    current_state='Medio',
    scenarios=scenarios,
    metric='improvement_probability'
)

print("\nScenario Comparison:")
print(comparison[['scenario', 'improvement_prob', 'most_likely_state']])
```

### Use Case 4: Analyze feature impact

```python
from src.models import analyze_feature_impact

impact = analyze_feature_impact(
    predictor,
    current_state='Medio',
    feature_name='Seniority',
    metric='improvement_probability'
)

print("\nSeniority Impact on Improvement:")
print(impact[['feature_value', 'improvement_prob']])
```

### Use Case 5: Get confidence intervals

```python
from src.models import calculate_confidence_intervals

ci = calculate_confidence_intervals(
    predictor,
    current_state='Alto',
    features={'Seniority': 'Sr'},
    n_steps=10,
    n_simulations=5000,
    confidence_level=0.95
)

print("\n95% Confidence Intervals:")
print(ci[['step', 'expected_value', 'lower_bound', 'upper_bound']])
```

### Use Case 6: Load a saved model

```python
from src.models import load_model

# Load previously saved model
predictor = load_model('models/my_engagement_model.pkl')

# Use immediately
result = predict_employee_engagement(
    predictor,
    current_state='Alto',
    features={'Seniority': 'Sr'}
)
```

## Running Examples

### Run all examples

```bash
python example_usage.py
```

This will demonstrate:
1. Basic training and prediction
2. Monte Carlo simulation
3. Batch prediction
4. Scenario comparison
5. Feature impact analysis
6. Confidence intervals
7. Model persistence
8. Model evaluation
9. Steady-state analysis

### Run tests

```bash
# Run all tests
pytest tests/test_markov_model.py -v

# Run specific test
pytest tests/test_markov_model.py::TestMarkovEngagementPredictor::test_fit -v
```

## Tips for Best Results

### 1. Data Quality

```python
# Ensure data is clean
data = data.dropna(subset=['Engagement Category'])
data = data[data['Engagement Category'].isin(predictor.states)]
```

### 2. Feature Selection

Start with important features:
```python
# Good starting features
features = ['Seniority', 'Studio']

# Add more if needed
features = ['Seniority', 'Studio', 'Position', 'Location']
```

### 3. Model Validation

Always evaluate on test data:
```python
from src.models import evaluate_model

# Split data
test_transitions = transitions.sample(frac=0.2, random_state=42)
train_transitions = transitions.drop(test_transitions.index)

# Train
predictor.fit(train_transitions, features=['Seniority'])

# Evaluate
metrics = evaluate_model(predictor, test_transitions, features=['Seniority'])
print(f"Accuracy: {metrics['accuracy']:.3f}")
```

### 4. Reproducibility

Use random seeds:
```python
result = predict_employee_engagement(
    predictor,
    current_state='Alto',
    n_simulations=1000,
    random_seed=42  # Always get same results
)
```

## Troubleshooting

### Problem: Import error

**Solution:**
```python
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.models import MarkovEngagementPredictor
```

### Problem: "Model must be fitted"

**Solution:** Call `fit()` before predicting
```python
predictor = MarkovEngagementPredictor()
predictor.fit(transitions, features=['Seniority'])  # Must fit first!
result = predict_employee_engagement(predictor, ...)
```

### Problem: Slow predictions

**Solution:** Disable Monte Carlo for single-step
```python
result = predict_employee_engagement(
    predictor,
    current_state='Alto',
    include_monte_carlo=False  # Much faster
)
```

### Problem: Missing feature value

**Solution:** Model will fall back to base matrix
```python
# Even if 'Expert' wasn't in training data
result = predict_employee_engagement(
    predictor,
    current_state='Alto',
    features={'Seniority': 'Expert'}  # Will use base matrix
)
```

## Next Steps

1. **Read the full guide:** `MARKOV_MODEL_GUIDE.md`
2. **Run examples:** `python example_usage.py`
3. **Run tests:** `pytest tests/test_markov_model.py -v`
4. **Integrate with your app:** Import and use in your application

## Documentation Files

- **QUICKSTART_MARKOV.md** (this file): Quick start guide
- **MARKOV_MODEL_GUIDE.md**: Complete technical documentation
- **MIGRATION_SUMMARY.md**: Migration details and architecture
- **example_usage.py**: 9 comprehensive examples
- **tests/test_markov_model.py**: Unit tests

## Need Help?

- Check the **MARKOV_MODEL_GUIDE.md** for detailed API reference
- Run **example_usage.py** to see all features in action
- Review **tests/test_markov_model.py** for usage patterns

---

**Happy Predicting!**

Generated by Claude Code Assistant - 2025-11-18
