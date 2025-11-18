import threading
import time
import logging
from typing import Dict, List, Callable
from prometheus_client import Gauge, Counter

logger = logging.getLogger(__name__)

class FailoverManager:
    def __init__(self, netconf_client, monitoring_system):
        self.netconf_client = netconf_client
        self.monitoring_system = monitoring_system
        self.failover_groups = {}
        self.is_running = False
        self.monitor_thread = None
        
        # Prometheus metrics
        self.failover_status = Gauge('failover_manager_status', 'Failover manager status')
        self.failover_switch_count = Counter('failover_switch_events_total', 
                                           'Total failover switch events', ['group'])
    
    def add_failover_group(self, group_config: Dict):
        """Add a failover group"""
        group_name = group_config['name']
        self.failover_groups[group_name] = {
            'config': group_config,
            'primary_interfaces': group_config.get('primary-interfaces', []),
            'backup_interfaces': group_config.get('backup-interfaces', []),
            'current_active': group_config.get('primary-interfaces', [])[0] if group_config.get('primary-interfaces') else None,
            'failure_count': 0,
            'recovery_count': 0
        }
        logger.info(f"Added failover group: {group_name}")
    
    def start_monitoring(self):
        """Start failover monitoring"""
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.failover_status.set(1)
        logger.info("Failover monitoring started")
    
    def stop_monitoring(self):
        """Stop failover monitoring"""
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.failover_status.set(0)
        logger.info("Failover monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.is_running:
            try:
                for group_name, group_data in self.failover_groups.items():
                    self._check_group_health(group_name, group_data)
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Failover monitoring error: {e}")
                time.sleep(30)
    
    def _check_group_health(self, group_name: str, group_data: Dict):
        """Check health of failover group interfaces"""
        active_interface = group_data['current_active']
        
        if active_interface and not self._check_interface_health(active_interface):
            logger.warning(f"Interface {active_interface} in group {group_name} is down")
            group_data['failure_count'] += 1
            
            # Trigger failover after 3 consecutive failures
            if group_data['failure_count'] >= 3:
                self._trigger_failover(group_name, group_data)
        else:
            # Reset failure count on successful check
            group_data['failure_count'] = 0
            
            # Check if we can failback to primary
            if active_interface in group_data['backup_interfaces']:
                self._check_failback(group_name, group_data)
    
    def _check_interface_health(self, interface_name: str) -> bool:
        """Check if interface is healthy"""
        # Simulate interface health check
        # In real implementation, ping the interface or check via SNMP/NETCONF
        try:
            # For demo, assume 90% of interfaces are healthy
            import random
            return random.random() > 0.1
        except:
            return False
    
    def _trigger_failover(self, group_name: str, group_data: Dict):
        """Trigger failover to backup interface"""
        current_active = group_data['current_active']
        backup_interface = self._select_backup_interface(group_data)
        
        if backup_interface and backup_interface != current_active:
            logger.info(f"Failover: Switching from {current_active} to {backup_interface} in group {group_name}")
            
            # Deactivate current interface
            self._deactivate_interface(current_active)
            
            # Activate backup interface
            self._activate_interface(backup_interface)
            
            # Update group state
            group_data['current_active'] = backup_interface
            group_data['failure_count'] = 0
            
            # Update metrics
            self.failover_switch_count.labels(group=group_name).inc()
            
            logger.info(f"Failover completed for group {group_name}")
    
    def _check_failback(self, group_name: str, group_data: Dict):
        """Check if we can failback to primary interface"""
        primary_interface = group_data['primary_interfaces'][0] if group_data['primary_interfaces'] else None
        current_active = group_data['current_active']
        
        if primary_interface and current_active != primary_interface:
            if self._check_interface_health(primary_interface):
                group_data['recovery_count'] += 1
                
                # Failback after 5 consecutive successful checks
                if group_data['recovery_count'] >= 5:
                    self._trigger_failback(group_name, group_data, primary_interface)
            else:
                group_data['recovery_count'] = 0
    
    def _trigger_failback(self, group_name: str, group_data: Dict, primary_interface: str):
        """Trigger failback to primary interface"""
        current_active = group_data['current_active']
        
        logger.info(f"Failback: Switching from {current_active} to {primary_interface} in group {group_name}")
        
        # Deactivate current backup interface
        self._deactivate_interface(current_active)
        
        # Activate primary interface
        self._activate_interface(primary_interface)
        
        # Update group state
        group_data['current_active'] = primary_interface
        group_data['recovery_count'] = 0
        
        logger.info(f"Failback completed for group {group_name}")
    
    def _select_backup_interface(self, group_data: Dict) -> str:
        """Select appropriate backup interface"""
        backup_interfaces = group_data['backup_interfaces']
        current_active = group_data['current_active']
        
        # Select first available backup interface that's not the current active
        for interface in backup_interfaces:
            if interface != current_active and self._check_interface_health(interface):
                return interface
        
        return backup_interfaces[0] if backup_interfaces else None
    
    def _deactivate_interface(self, interface_name: str):
        """Deactivate an interface"""
        logger.info(f"Deactivating interface: {interface_name}")
        # Implement actual interface deactivation via NETCONF
    
    def _activate_interface(self, interface_name: str):
        """Activate an interface"""
        logger.info(f"Activating interface: {interface_name}")
        # Implement actual interface activation via NETCONF