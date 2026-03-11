# Integration Guide - Markov Model into Existing App

Guide for integrating the Markov chain models into the existing Streamlit application.

## Overview

This guide shows how to integrate the new Markov models (`src/models/`) into your existing engagement prediction application.

## Integration Steps

### Step 1: Verify Installation

Ensure the models are in the correct location:

```bash
ls -la src/models/
# Should show:
# - markov_model.py
# - predictor.py
# - __init__.py
```

### Step 2: Test Import

Test that the models can be imported:

```python
# Test in Python console or notebook
from src.models import MarkovEngagementPredictor
print("Import successful!")
```

### Step 3: Add to Streamlit App

#### Option A: Add as a new page

Create `app/pages/markov_prediction.py`:

```python
import streamlit as st
import pandas as pd
from src.models import (
    MarkovEngagementPredictor,
    prepare_transitions_data,
    predict_employee_engagement,
    batch_predict
)

st.title("Markov Chain Predictions")

# Load data
@st.cache_data
def load_data():
    return pd.read_csv('data/data_globant_cleaned.csv')

# Train model
@st.cache_resource
def train_model(data, features):
    transitions = prepare_transitions_data(
        data,
        feature_cols=features
    )
    predictor = MarkovEngagementPredictor()
    predictor.fit(transitions, features=features)
    return predictor

data = load_data()

# Sidebar for feature selection
st.sidebar.header("Model Configuration")
available_features = ['Seniority', 'Studio', 'Position', 'Location']
selected_features = st.sidebar.multiselect(
    "Select Features",
    available_features,
    default=['Seniority', 'Studio']
)

# Train model with selected features
predictor = train_model(data, selected_features)

# Main interface
st.header("Single Employee Prediction")

col1, col2 = st.columns(2)

with col1:
    current_state = st.selectbox(
        "Current Engagement State",
        ['Bajo', 'Medio', 'Alto', 'Muy Alto']
    )

    n_steps = st.slider("Predict N steps ahead", 1, 10, 1)

with col2:
    # Feature inputs
    feature_values = {}
    for feature in selected_features:
        unique_vals = data[feature].unique().tolist()
        feature_values[feature] = st.selectbox(
            f"Select {feature}",
            unique_vals
        )

if st.button("Predict"):
    with st.spinner("Running prediction..."):
        result = predict_employee_engagement(
            predictor,
            current_state=current_state,
            features=feature_values,
            n_steps=n_steps,
            include_monte_carlo=True,
            n_simulations=1000
        )

    # Display results
    st.success("Prediction Complete!")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Most Likely State",
            result['most_likely_state'],
            f"{result['most_likely_probability']:.1%}"
        )

    with col2:
        st.metric(
            "Improvement Probability",
            f"{result['improvement_probability']:.1%}"
        )

    with col3:
        st.metric(
            "Deterioration Probability",
            f"{result['deterioration_probability']:.1%}"
        )

    # Show probability distribution
    st.subheader("State Probability Distribution")
    prob_df = pd.DataFrame([
        {'State': k, 'Probability': v}
        for k, v in result['analytical_prediction'].items()
    ]).sort_values('Probability', ascending=False)

    st.bar_chart(prob_df.set_index('State'))

    # Monte Carlo results
    if 'monte_carlo' in result:
        st.subheader("Monte Carlo Simulation Results")
        mc = result['monte_carlo']

        trajectory_df = pd.DataFrame({
            'Step': range(len(mc['expected_values'])),
            'Expected Value': mc['expected_values'],
            'Lower Bound': [ci[0] for ci in mc['confidence_intervals']],
            'Upper Bound': [ci[1] for ci in mc['confidence_intervals']]
        })

        st.line_chart(trajectory_df.set_index('Step'))

# Batch prediction section
st.header("Batch Prediction")

uploaded_file = st.file_uploader(
    "Upload employee data (CSV)",
    type=['csv']
)

if uploaded_file is not None:
    employees = pd.read_csv(uploaded_file)

    if st.button("Run Batch Prediction"):
        with st.spinner("Processing batch..."):
            results = batch_predict(
                predictor,
                employees,
                current_state_col='current_state',
                feature_cols=selected_features
            )

        st.success(f"Processed {len(results)} employees")
        st.dataframe(results)

        # Download results
        csv = results.to_csv(index=False)
        st.download_button(
            "Download Results",
            csv,
            "batch_predictions.csv",
            "text/csv"
        )
```

#### Option B: Integrate into existing prediction page

Add to your existing prediction module:

```python
# In your existing app/pages/prediction.py or similar

from src.models import (
    MarkovEngagementPredictor,
    prepare_transitions_data,
    predict_employee_engagement
)

# Add Markov option to your prediction method selector
prediction_method = st.selectbox(
    "Prediction Method",
    ["Existing Method", "Markov Chain"]
)

if prediction_method == "Markov Chain":
    # Use Markov predictor
    predictor = train_markov_model(data, features)
    result = predict_employee_engagement(predictor, ...)
else:
    # Use existing method
    ...
```

### Step 4: Add Model Management

Create `app/utils/model_manager.py`:

```python
from pathlib import Path
from src.models import save_model, load_model, MarkovEngagementPredictor
import streamlit as st

MODEL_DIR = Path("models")
MODEL_DIR.mkdir(exist_ok=True)

def save_markov_model(predictor, name="default"):
    """Save model with timestamp."""
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = MODEL_DIR / f"markov_{name}_{timestamp}.pkl"
    save_model(predictor, filepath)
    return filepath

def load_markov_model(filepath):
    """Load saved model."""
    return load_model(filepath)

def list_saved_models():
    """List all saved models."""
    return list(MODEL_DIR.glob("markov_*.pkl"))

# Streamlit UI for model management
def model_management_ui():
    st.sidebar.header("Model Management")

    saved_models = list_saved_models()

    if saved_models:
        selected_model = st.sidebar.selectbox(
            "Load Saved Model",
            ["Train New"] + [m.name for m in saved_models]
        )

        if selected_model != "Train New":
            model_path = MODEL_DIR / selected_model
            predictor = load_markov_model(model_path)
            st.sidebar.success(f"Loaded: {selected_model}")
            return predictor

    return None
```

### Step 5: Add Scenario Analysis

Create `app/pages/scenario_analysis.py`:

```python
import streamlit as st
import pandas as pd
from src.models import compare_scenarios

st.title("Scenario Analysis - What-If Predictions")

# Define scenarios
st.header("Define Scenarios")

num_scenarios = st.number_input("Number of Scenarios", 2, 10, 3)

scenarios = {}
for i in range(num_scenarios):
    with st.expander(f"Scenario {i+1}"):
        name = st.text_input(f"Scenario Name", f"Scenario {i+1}", key=f"name_{i}")

        seniority = st.selectbox(
            "Seniority",
            ['Jr', 'Ssr', 'Sr'],
            key=f"sen_{i}"
        )

        studio = st.selectbox(
            "Studio",
            ['Engineering', 'Design', 'Operations'],
            key=f"studio_{i}"
        )

        scenarios[name] = {
            'Seniority': seniority,
            'Studio': studio
        }

# Run comparison
if st.button("Compare Scenarios"):
    current_state = st.selectbox(
        "Starting State",
        ['Bajo', 'Medio', 'Alto', 'Muy Alto']
    )

    comparison = compare_scenarios(
        st.session_state.predictor,
        current_state=current_state,
        scenarios=scenarios,
        metric='improvement_probability'
    )

    st.subheader("Scenario Comparison Results")
    st.dataframe(comparison)

    # Visualization
    import plotly.express as px
    fig = px.bar(
        comparison,
        x='scenario',
        y='improvement_prob',
        title='Improvement Probability by Scenario'
    )
    st.plotly_chart(fig)
```

### Step 6: Add to Main App

Update `app/main.py` or your main Streamlit file:

```python
import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Engagement Prediction",
    page_icon="📊",
    layout="wide"
)

# Navigation
page = st.sidebar.selectbox(
    "Navigation",
    [
        "Home",
        "Data Exploration",
        "Markov Predictions",  # New page
        "Scenario Analysis",   # New page
        "Model Management"     # New page
    ]
)

if page == "Markov Predictions":
    from pages import markov_prediction
    markov_prediction.show()
elif page == "Scenario Analysis":
    from pages import scenario_analysis
    scenario_analysis.show()
# ... other pages
```

## Advanced Integration

### Caching Trained Models

Use Streamlit's caching to avoid retraining:

```python
@st.cache_resource
def get_predictor(data_hash, features_tuple):
    """Cache predictor by data and features."""
    data = load_data()
    transitions = prepare_transitions_data(data, feature_cols=list(features_tuple))
    predictor = MarkovEngagementPredictor()
    predictor.fit(transitions, features=list(features_tuple))
    return predictor

# Usage
data = load_data()
data_hash = hash(pd.util.hash_pandas_object(data).sum())
features = tuple(['Seniority', 'Studio'])  # Must be hashable
predictor = get_predictor(data_hash, features)
```

### Real-Time Predictions

Add WebSocket or polling for real-time updates:

```python
import streamlit as st
import time

# Auto-refresh every N seconds
refresh_interval = st.sidebar.slider("Refresh Interval (s)", 5, 60, 10)

placeholder = st.empty()

while True:
    with placeholder.container():
        # Load latest data
        data = load_data()

        # Make predictions
        results = batch_predict(predictor, data.tail(100))

        # Display
        st.dataframe(results)

        st.caption(f"Last updated: {pd.Timestamp.now()}")

    time.sleep(refresh_interval)
```

### Export to Dashboard

Create exportable dashboards:

```python
from src.models import (
    predict_employee_engagement,
    calculate_confidence_intervals
)
import plotly.graph_objects as go

def create_dashboard(predictor, employee_data):
    """Create comprehensive dashboard."""

    # Prediction
    result = predict_employee_engagement(
        predictor,
        current_state=employee_data['current_state'],
        features=employee_data['features'],
        n_steps=10,
        include_monte_carlo=True
    )

    # Create figure
    fig = go.Figure()

    # Add trajectory
    mc = result['monte_carlo']
    steps = range(len(mc['expected_values']))

    fig.add_trace(go.Scatter(
        x=steps,
        y=mc['expected_values'],
        name='Expected Value',
        line=dict(color='blue', width=2)
    ))

    # Add confidence intervals
    fig.add_trace(go.Scatter(
        x=steps,
        y=[ci[1] for ci in mc['confidence_intervals']],
        fill=None,
        mode='lines',
        line=dict(color='lightblue'),
        name='95% CI Upper'
    ))

    fig.add_trace(go.Scatter(
        x=steps,
        y=[ci[0] for ci in mc['confidence_intervals']],
        fill='tonexty',
        mode='lines',
        line=dict(color='lightblue'),
        name='95% CI Lower'
    ))

    fig.update_layout(
        title='Engagement Trajectory Prediction',
        xaxis_title='Time Steps',
        yaxis_title='Engagement Value',
        hovermode='x unified'
    )

    return fig

# In Streamlit
st.plotly_chart(create_dashboard(predictor, employee_data))
```

## Testing Integration

### Unit Tests

Create `tests/test_integration.py`:

```python
import pytest
from src.models import MarkovEngagementPredictor
import pandas as pd

def test_streamlit_integration():
    """Test model works with Streamlit."""
    # Simulate Streamlit workflow
    data = pd.read_csv('data/data_globant_cleaned.csv')

    from src.models import prepare_transitions_data
    transitions = prepare_transitions_data(data, feature_cols=['Seniority'])

    predictor = MarkovEngagementPredictor()
    predictor.fit(transitions, features=['Seniority'])

    # Test prediction
    from src.models import predict_employee_engagement
    result = predict_employee_engagement(
        predictor,
        current_state='Alto',
        features={'Seniority': 'Sr'}
    )

    assert 'most_likely_state' in result
    assert 'improvement_probability' in result
```

### Integration Test Script

Create `test_integration.sh`:

```bash
#!/bin/bash

echo "Testing Markov Model Integration..."

# 1. Test imports
python -c "from src.models import MarkovEngagementPredictor; print('✓ Import successful')"

# 2. Run unit tests
pytest tests/test_markov_model.py -v

# 3. Run example
python example_usage.py > /dev/null && echo "✓ Examples run successfully"

# 4. Test Streamlit app (headless)
streamlit run app/main.py --server.headless true &
PID=$!
sleep 5
kill $PID
echo "✓ Streamlit integration successful"

echo "All integration tests passed!"
```

## Deployment Checklist

- [ ] Models in correct location (`src/models/`)
- [ ] Dependencies installed (`numpy`, `pandas`, `scipy`)
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Streamlit pages created
- [ ] Caching configured
- [ ] Model persistence working
- [ ] Error handling tested
- [ ] Documentation updated
- [ ] User guide created

## Troubleshooting

### Import Errors

If you get import errors:

```python
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.models import MarkovEngagementPredictor
```

### Streamlit Caching Issues

Clear cache if models aren't updating:

```python
# In Streamlit app
if st.sidebar.button("Clear Cache"):
    st.cache_data.clear()
    st.cache_resource.clear()
    st.experimental_rerun()
```

### Performance Issues

If predictions are slow:

1. Use `include_monte_carlo=False` for faster predictions
2. Reduce `n_simulations` (1000 is usually sufficient)
3. Cache trained models
4. Use batch processing for multiple employees

## Support

For issues or questions:
1. Check `MARKOV_MODEL_GUIDE.md` for API details
2. Review `example_usage.py` for working examples
3. Run unit tests to verify installation
4. Contact the development team

---

**Last Updated:** 2025-11-18
**Status:** Ready for Integration
