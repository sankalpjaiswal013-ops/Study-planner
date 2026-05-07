# Create virtual environment
python -m venv venv

# Activate it and install dependencies
.\venv\Scripts\activate
pip install -r requirements.txt

Write-Host "Setup complete! To run the app, make sure your virtual environment is activated and run: streamlit run app.py"
