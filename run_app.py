#!/usr/bin/env python3
"""
AGRIVISION Application Launcher
Run this script to start the AGRIVISION Smart Agriculture System
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'streamlit',
        'pandas', 
        'numpy',
        'sklearn',  # Changed from scikit-learn to sklearn
        'plotly',
        'joblib',
        'folium'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"{package} - OK")
        except ImportError:
            missing_packages.append(package)
            print(f"{package} - MISSING")
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Please install them using: pip install -r requirements.txt")
        return False
    
    print("\nAll dependencies are installed!")
    return True

def check_models():
    """Check if ML model files exist"""
    model_files = [
        'models/crop_recommendation_model.pkl',
        'models/crop_encoder.pkl',
        'models/irrigation_model.pkl',
        'models/irrigation_preprocessor.pkl',
        'models/yield_prediction_model.pkl',
        'models/yield_preprocessor.pkl'
    ]
    
    missing_models = []
    
    for model_file in model_files:
        if os.path.exists(model_file):
            print(f"{model_file} - OK")
        else:
            missing_models.append(model_file)
            print(f"{model_file} - MISSING")
    
    if missing_models:
        print(f"\nMissing model files: {', '.join(missing_models)}")
        print("The application will run but some features may not work properly.")
        return False
    
    print("\nAll model files are present!")
    return True

def setup_database():
    """Initialize the database"""
    try:
        from database import Database
        db = Database()
        print("Database initialized successfully!")
        return True
    except Exception as e:
        print(f"Database initialization failed: {e}")
        return False

def start_application():
    """Start the Streamlit application"""
    print("\nStarting AGRIVISION Application...")
    print("=" * 50)
    
    # Change to the application directory
    app_dir = Path(__file__).parent
    os.chdir(app_dir)
    
    # Start Streamlit
    try:
        # Run streamlit in a subprocess
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            "main.py", 
            "--server.port", "8501",
            "--server.headless", "false",
            "--browser.gatherUsageStats", "false"
        ]
        
        print(f"Opening application in browser...")
        print(f"URL: http://localhost:8501")
        print(f"Admin Panel: http://localhost:8501?admin=true")
        print("=" * 50)
        
        # Open browser after a short delay
        def open_browser():
            time.sleep(3)
            webbrowser.open("http://localhost:8501")
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Start the application
        subprocess.run(cmd, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"Failed to start application: {e}")
        return False
    except KeyboardInterrupt:
        print("\nApplication stopped by user")
        return True
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def main():
    """Main launcher function"""
    print("AGRIVISION - Smart Agriculture Decision Support System")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Check models
    check_models()
    
    # Setup database
    if not setup_database():
        return False
    
    print("\nPre-flight checks completed!")
    
    # Start the application
    try:
        return start_application()
    except KeyboardInterrupt:
        print("\nGoodbye!")
        return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
