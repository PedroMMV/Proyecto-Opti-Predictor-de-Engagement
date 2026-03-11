# Quick Run Guide - Streamlit App

## How to Run

```bash
cd C:\Users\miche\Documents\projects\Globant\engagement-prediction-app
streamlit run app/Home.py
```

## Structure

```
app/
├── Home.py              # Main entry point (dashboard)
└── pages/
    ├── 2_Data_Explorer.py
    ├── 3_Variable_Selection.py
    ├── 4_Prediction.py
    ├── 5_Model_Analytics.py
    └── 6_Documentation.py
```

## Troubleshooting

### Port already in use
```bash
streamlit run app/Home.py --server.port 8502
```

### Module not found
Run from project root directory.

---
**Version**: 1.0.0
