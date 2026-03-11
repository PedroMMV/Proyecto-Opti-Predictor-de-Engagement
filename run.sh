#!/bin/bash
# Quick start script for Linux/Mac

echo "Starting Engagement Prediction App..."
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "Virtual environment activated"
else
    echo "Warning: Virtual environment not found"
    echo "Run: python -m venv venv"
    echo "Then: source venv/bin/activate"
    echo "Then: pip install -r requirements.txt"
fi

echo ""
echo "Starting Streamlit..."
streamlit run app/home.py
