================================================================================
                    QUICK START GUIDE
        Employee Engagement Prediction App
================================================================================

CURRENT LOCATION:
C:\Users\miche\Documents\projects\Globant\engagement-prediction-app

================================================================================
STEP 1: OPEN TERMINAL
================================================================================

Windows:
  • Press Win + R
  • Type: cmd
  • Press Enter

Or use PowerShell/Windows Terminal

================================================================================
STEP 2: NAVIGATE TO PROJECT
================================================================================

cd C:\Users\miche\Documents\projects\Globant\engagement-prediction-app

================================================================================
STEP 3: CREATE VIRTUAL ENVIRONMENT (First time only)
================================================================================

python -m venv venv

Wait for completion (~30 seconds)

================================================================================
STEP 4: ACTIVATE VIRTUAL ENVIRONMENT
================================================================================

Windows CMD:
  venv\Scripts\activate

Windows PowerShell:
  venv\Scripts\Activate.ps1

Linux/Mac:
  source venv/bin/activate

You should see (venv) in your command prompt

================================================================================
STEP 5: INSTALL DEPENDENCIES (First time only)
================================================================================

pip install -r requirements.txt

Wait for installation (~2-5 minutes)

================================================================================
STEP 6: RUN THE APPLICATION
================================================================================

Method 1 - Direct command:
  streamlit run app/main.py

Method 2 - Using script:
  Windows: run.bat
  Linux/Mac: ./run.sh

================================================================================
STEP 7: ACCESS THE APP
================================================================================

The app will automatically open in your browser at:

  http://localhost:8501

If it doesn't open automatically, manually open your browser and go to that URL

================================================================================
TROUBLESHOOTING
================================================================================

Problem: "streamlit: command not found"
Solution: Make sure virtual environment is activated
          Then: pip install streamlit

Problem: "Port 8501 already in use"
Solution: streamlit run app/main.py --server.port 8502

Problem: "Module not found"
Solution: pip install -r requirements.txt

Problem: CSS not loading
Solution: The app will work without CSS (just different styling)

================================================================================
USING THE APP
================================================================================

1. HOME PAGE
   • Upload your CSV data or use the included dataset
   • View data preview

2. DATA EXPLORER
   • Explore dataset statistics
   • View distributions
   • Analyze correlations

3. VARIABLE SELECTION
   • Select target variable (engagement)
   • Choose predictor features
   • Configure model parameters

4. PREDICTION
   • Run Markov model predictions
   • View probability distributions
   • Generate forecasts

5. MODEL ANALYTICS
   • View performance metrics
   • Analyze transition matrices
   • Explore feature importance

6. DOCUMENTATION
   • Learn about methodology
   • View examples
   • Get help

================================================================================
INCLUDED DATASET
================================================================================

Location: data/raw/data_globant_cleaned.csv
Size: 2.4 MB
Ready to use!

================================================================================
STOPPING THE APP
================================================================================

Press Ctrl + C in the terminal where Streamlit is running

================================================================================
RESTARTING THE APP
================================================================================

1. Navigate to project directory (if not already there)
2. Activate virtual environment (if not already active)
3. Run: streamlit run app/main.py

================================================================================
NEXT STEPS AFTER FIRST RUN
================================================================================

1. Explore the different pages
2. Upload your own data
3. Test predictions
4. Review documentation
5. Customize as needed

================================================================================
DEPLOYMENT TO CLOUD (Optional)
================================================================================

To deploy online:
1. Push code to GitHub
2. Go to https://share.streamlit.io
3. Connect your repository
4. Set main file: app/main.py
5. Deploy!

================================================================================
SUPPORT
================================================================================

Documentation: See README.md
Installation Help: See INSTALLATION.md
Project Structure: See PROJECT_STRUCTURE.md
Complete Checklist: See SETUP_CHECKLIST.md

================================================================================
                        READY TO START!
================================================================================

Follow the 6 steps above and you'll be running in ~5 minutes!

Good luck! 🚀

================================================================================
