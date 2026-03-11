# Employee Engagement Prediction App

A comprehensive Streamlit application for predicting employee engagement using Markov Chain models and advanced machine learning techniques.

## Overview

This application provides an interactive platform for analyzing and predicting employee engagement patterns using historical data. Built with Streamlit and powered by Markov Chain models, it offers real-time predictions, interactive visualizations, and actionable insights for HR teams.

## Key Features

- **Interactive Data Exploration**: Upload and explore employee engagement datasets with intuitive visualizations
- **Variable Selection**: Smart feature selection tools to identify the most impactful engagement drivers
- **Markov Chain Predictions**: State-of-the-art probabilistic modeling for engagement prediction
- **Advanced Analytics**:
  - Transition probability matrices
  - Steady-state analysis
  - Time-series forecasting
  - Feature importance analysis
- **Interactive Dashboards**: Real-time charts with Plotly and customizable views
- **Export Capabilities**: Download predictions and reports in CSV, Excel, and PDF formats
- **Professional UI**: Dark mode optimized with custom styling

## Installation

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/yosebitasgg/Engagement-Prediction.git
cd Engagement-Prediction
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
streamlit run app/home.py
```

The app will open in your browser at `http://localhost:8501`

### Streamlit Cloud Deployment

See detailed guide: [STREAMLIT_CLOUD_GUIDE.md](STREAMLIT_CLOUD_GUIDE.md)

Quick steps:
1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Select `app/main.py` as the main file
5. Deploy!

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build manually
docker build -t engagement-prediction-app .
docker run -p 8501:8501 engagement-prediction-app
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment options including AWS, Heroku, and production configurations.

## Quick Start Guide

### 1. Upload Your Data
Navigate to the **Home** page and upload your employee engagement CSV file. The app expects data with:
- Employee identifiers
- Engagement scores (categorical or numeric)
- Temporal information (dates, periods)
- Feature variables (demographics, performance metrics, etc.)

### 2. Explore Your Data
Use the **Data Explorer** to:
- View descriptive statistics
- Analyze distributions
- Identify patterns and anomalies
- Visualize correlations

### 3. Select Variables
In **Variable Selection**, choose:
- Target variable (engagement score)
- Temporal grouping variable
- Predictor features
- Feature engineering options

### 4. Generate Predictions
The **Prediction** page allows you to:
- Configure Markov model parameters
- Run predictions for individual employees or groups
- View probability distributions
- Export results

### 5. Analyze Results
**Model Analytics** provides:
- Model performance metrics
- Confusion matrices
- Feature importance charts
- Transition probability heatmaps

## Project Structure

```
engagement-prediction-app/
├── .streamlit/              # Streamlit configuration
│   └── config.toml         # Theme and server settings
├── app/                    # Streamlit application
│   ├── main.py            # Main entry point
│   └── pages/             # Multi-page app structure
│       ├── 1_🏠_Home.py
│       ├── 2_📊_Data_Explorer.py
│       ├── 3_🎯_Variable_Selection.py
│       ├── 4_🔮_Prediction.py
│       ├── 5_📈_Model_Analytics.py
│       └── 6_📖_Documentation.py
├── src/                    # Core application logic
│   ├── models/            # ML models
│   │   ├── markov_model.py
│   │   └── predictor.py
│   ├── data/              # Data processing
│   │   ├── loader.py
│   │   └── preprocessor.py
│   ├── visualization/     # Plotting utilities
│   │   ├── plots.py
│   │   └── interactive_charts.py
│   └── utils/             # Helper functions
│       ├── config.py
│       └── helpers.py
├── data/                   # Data storage
│   ├── raw/               # Original datasets
│   └── processed/         # Processed data
├── assets/                 # Static resources
│   ├── images/            # Logos, icons
│   └── styles/            # Custom CSS
├── notebooks/              # Jupyter notebooks for analysis
├── tests/                  # Unit tests
├── requirements.txt        # Python dependencies
├── setup.py               # Package setup
└── README.md              # This file
```

## Data Format

The application expects CSV files with the following structure:

| Column | Type | Description |
|--------|------|-------------|
| `employee_id` | string/int | Unique employee identifier |
| `period` | date/string | Time period (month, quarter, year) |
| `engagement_score` | categorical | Low, Medium, High, or numeric |
| `feature_1` | numeric/categorical | Predictor variable |
| `feature_2` | numeric/categorical | Predictor variable |
| ... | ... | Additional features |

## Technologies Used

- **Frontend**: Streamlit, Plotly, Matplotlib, Seaborn
- **Backend**: Python 3.10+
- **ML/Stats**: scikit-learn, NumPy, pandas, SciPy
- **Export**: ReportLab, FPDF2, openpyxl
- **Styling**: Custom CSS, Streamlit theming

## Environment Variables

The application supports the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `STREAMLIT_SERVER_PORT` | Port for Streamlit server | 8501 |
| `DATA_PATH` | Path to data directory | ./data |
| `LOG_LEVEL` | Logging level (INFO, DEBUG, ERROR) | INFO |

Create a `.env` file from `.env.example`:
```bash
cp .env.example .env
```

## Configuration

### Streamlit Configuration

Edit `.streamlit/config.toml` to customize:
- Theme colors
- Server settings
- Upload limits
- Browser behavior

### Secrets Management

For sensitive data (API keys, credentials):
1. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`
2. Add your secrets
3. Never commit `secrets.toml` to version control

## Deployment Options

This application can be deployed to:

- **Streamlit Cloud**: Free hosting for public repos (recommended for demos)
- **Docker**: Containerized deployment for any platform
- **Heroku**: Quick cloud deployment
- **AWS EC2/Elastic Beanstalk**: Enterprise production deployment
- **Azure/GCP**: Cloud platform deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions for each platform.

## Model Details

The application uses **Markov Chain models** to predict engagement transitions:
- **States**: Engagement levels (e.g., Low, Medium, High)
- **Transitions**: Probability of moving between states over time
- **Steady State**: Long-term equilibrium distribution
- **Feature Integration**: Conditional probabilities based on employee attributes

## Testing

Run the test suite:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_markov_model.py -v
```

## Scripts

The `scripts/` directory contains useful utilities:

- `deploy.sh` / `deploy.bat`: Automated deployment script
- `health_check.py`: Application health check utility

```bash
# Run health check
python scripts/health_check.py

# Deploy (after tests pass)
./scripts/deploy.sh  # Linux/Mac
scripts\deploy.bat    # Windows
```



## Support

For questions or issues:
- Open an issue on GitHub
- Check the [Documentation](app/pages/6_📖_Documentation.py) page within the app
- Review [DEPLOYMENT.md](DEPLOYMENT.md) for deployment issues
- See [TROUBLESHOOTING.md](DEPLOYMENT.md#troubleshooting) for common problems

## Documentation

- [README.md](README.md) - This file (overview and quick start)
- [DEPLOYMENT.md](DEPLOYMENT.md) - Complete deployment guide
- [STREAMLIT_CLOUD_GUIDE.md](STREAMLIT_CLOUD_GUIDE.md) - Streamlit Cloud specific guide
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
- [CHANGELOG.md](CHANGELOG.md) - Version history
- [SECURITY.md](SECURITY.md) - Security policy

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and release notes.


## Acknowledgments

- Built with Streamlit
- Powered by scikit-learn and pandas
- Visualization with Plotly
- Inspired by modern HR analytics practices

---

**Version**: 1.0.0
**Last Updated**: November 18, 2025
**Python**: 3.10+
**License**: MIT
