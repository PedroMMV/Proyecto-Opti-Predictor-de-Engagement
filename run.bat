@echo off
REM Quick start script for Windows

echo Starting Engagement Prediction App...
echo.

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo Virtual environment activated
) else (
    echo Warning: Virtual environment not found
    echo Run: python -m venv venv
    echo Then: venv\Scripts\activate.bat
    echo Then: pip install -r requirements.txt
)

echo.
echo Starting Streamlit...
streamlit run app\home.py

pause
