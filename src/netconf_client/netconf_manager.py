from ncclient import manager
import xml.dom.minidom
import json
import logging
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NETCONFClient:
    def __init__(self, host: str, port: int, username: str, password: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.connection = None
    
    def connect(self) -> bool:
        """Establish NETCONF connection"""
        try:
            self.connection = manager.connect(
                host=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                hostkey_verify=False,
                device_params={'name': 'default'},
                timeout=30
            )
            logger.info(f"Connected to {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Close NETCONF connection"""
        if self.connection:
            self.connection.close_session()
            logger.info("Disconnected from device")
    
    def send_config(self, config: Dict) -> bool:
        """Send configuration to device"""
        try:
            # Convert config to XML
            config_xml = self._dict_to_xml(config)
            
            # Send edit-config operation
            reply = self.connection.edit_config(target='running', config=config_xml)
            logger.info("Configuration applied successfully")
            return True
            
        except Exception as e:
            logger.error(f"Configuration failed: {e}")
            return False
    
    def get_interfaces(self) -> List[Dict]:
        """Get current interface configurations"""
        try:
            filter_xml = """
            <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
                <interface/>
            </interfaces>
            """
            reply = self.connection.get_config(source='running', filter=filter_xml)
            return self._parse_interfaces(reply.xml)
        except Exception as e:
            logger.error(f"Failed to get interfaces: {e}")
            return []
    
    def _dict_to_xml(self, config: Dict) -> str:
        """Convert dictionary configuration to XML"""
        # Simplified XML conversion - in practice, use proper YANG to XML mapping
        root = ET.Element("config", xmlns="urn:ietf:params:xml:ns:netconf:base:1.0")
        network_elem = ET.SubElement(root, "network", xmlns="http://campus-ibn/ns/network")
        
        self._build_xml(network_elem, config.get('network', {}))
        
        return ET.tostring(root, encoding='utf-8').decode()
    
    def _build_xml(self, parent, data):
        """Recursively build XML from dictionary"""
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, list):
                    for item in value:
                        elem = ET.SubElement(parent, key)
                        self._build_xml(elem, item)
                else:
                    elem = ET.SubElement(parent, key)
                    self._build_xml(elem, value)
        else:
            parent.text = str(data)
    
    def _parse_interfaces(self, xml_data: str) -> List[Dict]:
        """Parse interface information from XML response"""
        # Implement XML to dictionary parsing
        interfaces = []
        try:
            dom = xml.dom.minidom.parseString(xml_data)
            interface_nodes = dom.getElementsByTagName("interface")
            
            for interface in interface_nodes:
                name = self._get_text_value(interface, "name")
                ip = self._get_text_value(interface, "ip-address")
                speed = self._get_text_value(interface, "speed")
                
                if name:
                    interfaces.append({
                        "name": name,
                        "ip_address": ip,
                        "speed": speed,
                        "status": "up"
                    })
                    
        except Exception as e:
            logger.error(f"Failed to parse interfaces: {e}")
        
        return interfaces
    
    def _get_text_value(self, parent, tag_name: str) -> str:
        """Extract text value from XML element"""
        elements = parent.getElementsByTagName(tag_name)
        if elements and elements[0].firstChild:
            return elements[0].firstChild.nodeValue
        return ""