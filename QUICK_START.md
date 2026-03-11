# Installation Guide

Complete guide to setting up the Employee Engagement Prediction App.

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Virtual environment tool (venv or conda)
- 500MB free disk space
- Web browser (Chrome, Firefox, or Edge recommended)

## Step-by-Step Installation

### 1. Navigate to Project Directory

```bash
cd C:\Users\miche\Documents\projects\Globant\engagement-prediction-app
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Upgrade pip

```bash
python -m pip install --upgrade pip
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Streamlit (web framework)
- Pandas & NumPy (data processing)
- Plotly, Matplotlib, Seaborn (visualization)
- Scikit-learn, SciPy (machine learning)
- ReportLab, FPDF (PDF export)
- And other required packages

**Expected installation time:** 2-5 minutes

### 5. Verify Installation

```bash
python -c "import streamlit; print(streamlit.__version__)"
```

Should output: `1.31.0` or higher

### 6. Configure Environment (Optional)

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` to customize settings if needed.

## Running the Application

### Option 1: Direct Command

```bash
streamlit run app/main.py
```

### Option 2: Using Startup Scripts

**Windows:**
```bash
run.bat
```

**Linux/Mac:**
```bash
chmod +x run.sh
./run.sh
```

### Option 3: Python Module

```bash
python -m streamlit run app/main.py
```

## Accessing the Application

Once running, the app will automatically open in your browser at:

```
http://localhost:8501
```

If it doesn't open automatically, manually navigate to that URL.

## Troubleshooting

### Issue: ModuleNotFoundError

**Solution:** Ensure virtual environment is activated and dependencies are installed:
```bash
pip install -r requirements.txt
```

### Issue: Port 8501 already in use

**Solution:** Use a different port:
```bash
streamlit run app/main.py --server.port 8502
```

### Issue: Streamlit not found

**Solution:** Install Streamlit explicitly:
```bash
pip install streamlit>=1.31.0
```

### Issue: CSS not loading

**Solution:** Check that `assets/styles/custom.css` exists. The app will run without it but with default styling.

### Issue: Data file not found

**Solution:** Verify dataset location:
```bash
ls data/raw/data_globant_cleaned.csv
```

## Verifying the Installation

Run the following checks:

### 1. Check Python Version
```bash
python --version
```
Should be 3.9 or higher

### 2. Check Installed Packages
```bash
pip list
```

### 3. Test Data Loading
```bash
python -c "import pandas as pd; df = pd.read_csv('data/raw/data_globant_cleaned.csv'); print(f'Dataset loaded: {len(df)} rows')"
```

### 4. Run Tests (Optional)
```bash
python -m pytest tests/ -v
```

## Directory Structure Verification

Ensure the following structure exists:

```
engagement-prediction-app/
├── .streamlit/config.toml          ✓
├── app/main.py                     ✓
├── app/pages/ (6 files)            ✓
├── src/models/ (3 files)           ✓
├── src/data/ (3 files)             ✓
├── src/visualization/ (3 files)    ✓
├── src/utils/ (3 files)            ✓
├── data/raw/data_globant_cleaned.csv  ✓
├── assets/styles/custom.css        ✓
├── requirements.txt                ✓
└── README.md                       ✓
```

## Next Steps

After successful installation:

1. **Start the app** using one of the methods above
2. **Navigate to Home page** to upload or select data
3. **Explore the Data Explorer** to understand your dataset
4. **Select variables** for modeling
5. **Run predictions** using the Markov model
6. **Analyze results** in the Model Analytics page

## Deployment to Streamlit Cloud

To deploy this app online:

1. Push code to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. Go to [share.streamlit.io](https://share.streamlit.io)

3. Click "New app"

4. Select your repository

5. Set main file path: `app/main.py`

6. Click "Deploy"

The app will be live at: `https://<your-app-name>.streamlit.app`

## Updating the Application

To update dependencies:

```bash
pip install --upgrade -r requirements.txt
```

To pull latest changes (if using git):

```bash
git pull origin main
pip install -r requirements.txt  # Update dependencies
```

## Uninstallation

To remove the application:

1. Deactivate virtual environment:
   ```bash
   deactivate
   ```

2. Delete the project directory:
   ```bash
   # Navigate to parent directory first
   rm -rf engagement-prediction-app  # Linux/Mac
   rmdir /s engagement-prediction-app  # Windows
   ```

## Support

For issues or questions:
- Check `README.md` for documentation
- Review `CONTRIBUTING.md` for guidelines
- Open an issue on GitHub
- Consult the in-app Documentation page

---

**Installation Guide Version:** 1.0.0
**Last Updated:** November 18, 2025
