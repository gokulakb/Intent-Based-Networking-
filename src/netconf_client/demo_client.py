"""
Demo NETCONF client for testing without real network devices
"""
import logging
from typing import Dict, List, Optional
import xml.etree.ElementTree as ET
import json

logger = logging.getLogger(__name__)

class DemoNETCONFClient:
    def __init__(self, host: str, port: int, username: str, password: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.connected = False
        self.current_config = {}
        
    def connect(self) -> bool:
        """Simulate connection to device"""
        logger.info(f"Demo: Connecting to {self.host}:{self.port}")
        self.connected = True
        
        # Initialize with demo interfaces
        self.current_config = {
            "interfaces": [
                {
                    "name": "eth0",
                    "ip_address": "192.168.1.10/24",
                    "speed": "1G",
                    "status": "up",
                    "vlan": 100
                },
                {
                    "name": "eth1", 
                    "ip_address": "192.168.1.11/24",
                    "speed": "1G",
                    "status": "up",
                    "vlan": 100
                },
                {
                    "name": "eth2",
                    "ip_address": "192.168.1.12/24", 
                    "speed": "10G",
                    "status": "up",
                    "vlan": 200
                }
            ]
        }
        
        return True
    
    def disconnect(self):
        """Simulate disconnection"""
        self.connected = False
        logger.info("Demo: Disconnected from device")
    
    def send_config(self, config: Dict) -> bool:
        """Simulate sending configuration"""
        if not self.connected:
            logger.error("Not connected to device")
            return False
            
        logger.info("Demo: Applying configuration")
        logger.info(f"Demo Config: {json.dumps(config, indent=2)}")
        
        # Store the configuration
        self.current_config.update(config)
        
        # Simulate successful configuration
        return True
    
    def get_interfaces(self) -> List[Dict]:
        """Get demo interface information"""
        if not self.connected:
            return []
            
        return self.current_config.get("interfaces", [])
    
    def get_config(self) -> Dict:
        """Get current configuration"""
        return self.current_config