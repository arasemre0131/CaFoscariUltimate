#!/usr/bin/env python3
"""
CA' FOSCARI ULTIMATE - WEB STARTUP SCRIPT
"""
import os
import sys
import subprocess

def install_requirements():
    """Install required packages"""
    print("📦 Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install requirements")
        return False
    return True

def check_files():
    """Check if required files exist"""
    required_files = [
        "main.py",
        "app.py",
        "courses_database.json",
        "templates/base.html",
        "templates/dashboard.html"
    ]

    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)

    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False

    print("✅ All required files found")
    return True

def start_web_server():
    """Start the Flask web server"""
    print("\n🚀 Starting Ca' Foscari Ultimate Web Interface...")
    print("📱 Web interface will be available at: http://localhost:8080")
    print("🔧 Use Ctrl+C to stop the server")
    print("-" * 60)

    try:
        # Run the Flask app
        os.system("python3 app.py")
    except KeyboardInterrupt:
        print("\n👋 Web server stopped")

def main():
    print("""
╔══════════════════════════════════════════════════════════════════╗
║  🌐 CA' FOSCARI ULTIMATE - WEB INTERFACE LAUNCHER               ║
║  Starting modern web frontend for your study system             ║
╚══════════════════════════════════════════════════════════════════╝
    """)

    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"📁 Working directory: {script_dir}")

    # Check files
    if not check_files():
        input("\n❌ Press Enter to exit...")
        return

    # Install requirements
    if not install_requirements():
        input("\n❌ Press Enter to exit...")
        return

    # Start web server
    start_web_server()

if __name__ == "__main__":
    main()