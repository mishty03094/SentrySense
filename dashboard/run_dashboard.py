"""
Simple script to run the SentrySense Dashboard
Handles setup and launches Streamlit
"""

import subprocess
import sys
import os

def check_requirements():
    """Check if required packages are installed"""
    required_packages = ['streamlit', 'plotly', 'pandas']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Install them with: pip install streamlit plotly pandas")
        return False
    
    return True

def run_setup():
    """Run the setup script"""
    try:
        from setup import main as setup_main
        setup_main()
    except Exception as e:
        print(f"⚠️ Setup warning: {e}")

def main():
    """Main function to run the dashboard"""
    print("🛡️ SentrySense Dashboard Launcher")
    print("=" * 40)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Run setup
    run_setup()
    
    # Launch Streamlit
    print("\n🚀 Launching dashboard...")
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error launching dashboard: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")

if __name__ == "__main__":
    main()
