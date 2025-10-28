#!/usr/bin/env python3
"""
PerpPatrol Dashboard Launcher
Ensures proper Python path setup for imports
"""

import sys
import os
import subprocess

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Set PYTHONPATH environment variable
os.environ['PYTHONPATH'] = project_root

if __name__ == "__main__":
    # Run streamlit with proper environment
    cmd = [
        sys.executable, "-m", "streamlit", "run", 
        "src/bot/telemetry/dashboard.py",
        "--server.port", "8501",
        "--server.headless", "false"
    ]
    
    print("🚀 Starting PerpPatrol Dashboard...")
    print(f"📁 Project root: {project_root}")
    print(f"🐍 Python path: {sys.path[0]}")
    print("🌐 Dashboard will be available at: http://localhost:8501")
    print("-" * 60)
    
    subprocess.run(cmd)
