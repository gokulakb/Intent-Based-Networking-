import json
import yaml
from typing import Dict, List, Any
from pydantic import BaseModel, ValidationError
import xml.etree.ElementTree as ET

class NetworkIntent(BaseModel):
    network_name: str
    network_range: str
    subnet_mask: str
    interface_speed: str
    vlans: List[Dict[str, Any]]
    failover_enabled: bool = True
    monitoring_enabled: bool = True

class InterfaceConfig(BaseModel):
    name: str
    speed: str
    ip_address: str
    vlan: int
    failover_priority: int
    enabled: bool = True

class FailoverGroup(BaseModel):
    name: str
    primary_interfaces: List[str]
    backup_interfaces: List[str]

class IntentProcessor:
    def __init__(self):
        self.supported_speeds = ["100M", "1G", "10G", "25G", "40G", "100G"]
        
    def validate_intent(self, intent_data: Dict) -> tuple[bool, List[str]]:
        """Validate high-level intent"""
        errors = []
        
        try:
            intent = NetworkIntent(**intent_data)
        except ValidationError as e:
            errors.append(f"Intent validation failed: {e}")
            return False, errors
        
        # Validate network range
        if not self._validate_network_range(intent.network_range, intent.subnet_mask):
            errors.append("Invalid network range or subnet mask")
        
        # Validate interface speed
        if intent.interface_speed not in self.supported_speeds:
            errors.append(f"Unsupported interface speed. Supported: {self.supported_speeds}")
        
        return len(errors) == 0, errors
    
    def _validate_network_range(self, network_range: str, subnet_mask: str) -> bool:
        """Validate IP network range"""
        try:
            import ipaddress
            network = ipaddress.IPv4Network(f"{network_range}/{subnet_mask}", strict=False)
            return network.is_private
        except:
            return False
    
    def generate_network_config(self, intent: Dict) -> Dict:
        """Generate network configuration from intent"""
        validated, errors = self.validate_intent(intent)
        if not validated:
            raise ValueError(f"Intent validation failed: {errors}")
        
        config = {
            "network": {
                "interfaces": [],
                "network-ranges": {
                    "ip-range": []
                },
                "failover-system": {
                    "enabled": intent.get("failover_enabled", True),
                    "failover-groups": []
                },
                "monitoring": {
                    "enabled": intent.get("monitoring_enabled", True)
                }
            }
        }
        
        # Generate interface configurations
        interfaces = self._generate_interfaces(intent)
        config["network"]["interfaces"] = interfaces
        
        # Generate network ranges
        ip_range = {
            "name": f"{intent['network_name']}_main",
            "subnet": f"{intent['network_range']}/{intent['subnet_mask']}",
            "vlan-id": intent['vlans'][0]['id'] if intent['vlans'] else 1
        }
        config["network"]["network-ranges"]["ip-range"].append(ip_range)
        
        # Generate failover groups
        if intent.get("failover_enabled", True):
            failover_groups = self._generate_failover_groups(interfaces)
            config["network"]["failover-system"]["failover-groups"] = failover_groups
        
        return config
    
    def _generate_interfaces(self, intent: Dict) -> List[Dict]:
        """Generate interface configurations"""
        interfaces = []
        base_ip = intent['network_range'].split('.')
        
        # Create physical interfaces
        for i in range(4):  # Create 4 sample interfaces
            interface = {
                "name": f"eth{i}",
                "enabled": True,
                "speed": intent['interface_speed'],
                "mtu": 1500,
                "ip-address": f"{base_ip[0]}.{base_ip[1]}.{base_ip[2]}.{i+10}/24",
                "vlan": intent['vlans'][0]['id'] if intent['vlans'] else 1,
                "failover-priority": i + 1
            }
            interfaces.append(interface)
        
        return interfaces
    
    def _generate_failover_groups(self, interfaces: List[Dict]) -> List[Dict]:
        """Generate failover group configurations"""
        if len(interfaces) >= 2:
            return [{
                "name": "primary_failover",
                "primary-interfaces": [interfaces[0]["name"]],
                "backup-interfaces": [interfaces[1]["name"]]
            }]
        return []