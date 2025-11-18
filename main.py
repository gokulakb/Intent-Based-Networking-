#!/usr/bin/env python3
"""
Campus IBN NMS - Main Application Entry Point
"""

import logging
import sys
import os
import time
from pathlib import Path

# Add src to path - Windows compatible
current_dir = Path(__file__).parent
src_path = current_dir / 'src'
sys.path.insert(0, str(src_path))

def setup_directories():
    """Create necessary directories"""
    directories = ['logs', 'data', 'configs', 'src/web_ui/templates']
    for directory in directories:
        dir_path = Path(directory)
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def setup_logging():
    """Setup logging configuration"""
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_dir / 'app.log', encoding='utf-8')
        ]
    )
    
    return logging.getLogger(__name__)

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = {
        'flask': 'Flask',
        'flask_socketio': 'Flask-SocketIO', 
        'prometheus_client': 'prometheus-client',
        'yaml': 'PyYAML',
        'dotenv': 'python-dotenv'
    }
    
    missing_packages = []
    for package, display_name in required_packages.items():
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(display_name)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        return False
    
    return True

def create_default_config():
    """Create default configuration file if it doesn't exist"""
    config_file = Path('configs') / 'default.yaml'
    if not config_file.exists():
        config_file.parent.mkdir(exist_ok=True)
        default_config = """# Campus IBN NMS Configuration
netconf_devices:
  - host: "localhost"
    port: 830
    username: "admin"
    password: "admin"

monitoring:
  prometheus_port: 8000
  scrape_interval: 30

web_ui:
  host: "0.0.0.0"
  port: 5000
  debug: true
"""
        config_file.write_text(default_config.strip())
        print(f"✓ Created default config: {config_file}")

def display_banner():
    """Display application banner"""
    banner = """
╔════════════════════════════════════════════════════════════════╗
║               ENHANCED CAMPUS IBN NMS SYSTEM                  ║
║            Intent-Based Networking Management                  ║
╠════════════════════════════════════════════════════════════════╣
║ Features:                                                      ║
║  • Intent-Based Configuration                                  ║
║  • Network Speed Management (100M - 100G)                      ║
║  • IP Range & Subnet Management                                ║
║  • Automatic Failover & Recovery                               ║
║  • Real-time Monitoring & Metrics                              ║
║  • Security & Firewall Rules                                   ║
║  • QoS Configuration                                           ║
║  • Network Services (DNS, DHCP, NTP)                          ║
╚════════════════════════════════════════════════════════════════╝
"""
    print(banner)

def main():
    """Main application entry point"""
    
    # Display banner
    display_banner()
    
    # Setup environment
    print("🔧 Setting up environment...")
    setup_directories()
    create_default_config()
    
    # Setup logging
    logger = setup_logging()
    
    # Check dependencies
    print("📦 Checking dependencies...")
    if not check_dependencies():
        print("\nPlease install dependencies using:")
        print("pip install -r requirements.txt")
        return
    
    try:
        # Import and start the application
        print("🚀 Starting Enhanced Campus IBN NMS...")
        
        from web_ui.app import app, socketio
        
        logger.info("Enhanced application components imported successfully")
        
        print("\n🎯 ENHANCED CAMPUS IBN NMS STARTED SUCCESSFULLY!")
        print("🌐 Web Interface:  http://localhost:5000")
        print("📊 Metrics:        http://localhost:8000")
        print("📝 Logs:          ./logs/app.log")
        print("="*60)
        print("💡 Features: Basic Config • Advanced Features • Monitoring")
        print("💡 Press Ctrl+C to stop the application")
        print("="*60 + "\n")
        
        # Start the web server
        logger.info("Starting Enhanced Flask-SocketIO server")
        socketio.run(
            app, 
            host='0.0.0.0', 
            port=5000, 
            debug=True,
            allow_unsafe_werkzeug=True
        )
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        print(f"\n❌ ERROR: Could not import application modules")
        print(f"Details: {e}")
        
    except KeyboardInterrupt:
        print("\n🔄 Shutting down Campus IBN NMS...")
        logger.info("Application shutdown by user")
        print("✓ Campus IBN NMS stopped successfully")
        
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        print(f"\n💥 Fatal error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()