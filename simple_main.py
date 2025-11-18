#!/usr/bin/env python3
"""
Campus IBN NMS - Simple Starter
"""

import os
import sys
from pathlib import Path

# Add src to path
current_dir = Path(__file__).parent
src_path = current_dir / 'src'
sys.path.insert(0, str(src_path))

# Create directories
Path('logs').mkdir(exist_ok=True)
Path('src/web_ui/templates').mkdir(parents=True, exist_ok=True)

print("🚀 Starting Campus IBN NMS...")

try:
    from web_ui.app import app, socketio
    print("✅ Application loaded successfully!")
    print("🌐 Web Interface: http://localhost:5000")
    print("💡 Press Ctrl+C to stop")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Installing dependencies...")
    os.system(f"{sys.executable} -m pip install -r requirements.txt")
    print("Please run the application again.")
    
except Exception as e:
    print(f"❌ Error: {e}")