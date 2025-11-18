from prometheus_client import start_http_server, Gauge, Counter, Info
import time
import threading
import requests
import json

class NetworkMonitor:
    def __init__(self, port=8000):
        self.port = port
        self.setup_metrics()
    
    def setup_metrics(self):
        """Setup Prometheus metrics"""
        # Interface metrics
        self.interface_speed = Gauge('network_interface_speed_mbps', 
                                   'Interface speed in Mbps', ['interface'])
        self.interface_status = Gauge('network_interface_status', 
                                    'Interface status (1=up, 0=down)', ['interface'])
        self.interface_traffic = Gauge('network_interface_traffic_bytes',
                                     'Interface traffic in bytes', ['interface', 'direction'])
        
        # Network range metrics
        self.ip_usage = Gauge('network_ip_usage_percent',
                            'IP address usage percentage', ['subnet'])
        
        # Failover metrics
        self.failover_status = Gauge('network_failover_active',
                                   'Failover status (1=active, 0=inactive)', ['group'])
        self.failover_events = Counter('network_failover_events_total',
                                     'Total failover events', ['group'])
        
        # System info
        self.network_info = Info('network_system', 'Network system information')
    
    def start_monitoring(self):
        """Start monitoring server"""
        start_http_server(self.port)
        print(f"Monitoring server started on port {self.port}")
        
        # Start background monitoring
        monitor_thread = threading.Thread(target=self._collect_metrics, daemon=True)
        monitor_thread.start()
    
    def _collect_metrics(self):
        """Collect and update metrics continuously"""
        while True:
            try:
                # Simulate metric collection
                self._update_interface_metrics()
                self._update_failover_metrics()
                self._update_network_info()
                
                time.sleep(30)  # Collect every 30 seconds
                
            except Exception as e:
                print(f"Metric collection error: {e}")
                time.sleep(60)
    
    def _update_interface_metrics(self):
        """Update interface metrics"""
        # Simulated interface data - replace with actual device queries
        interfaces = [
            {"name": "eth0", "speed": 1000, "status": 1, "traffic_tx": 1500000, "traffic_rx": 2000000},
            {"name": "eth1", "speed": 1000, "status": 1, "traffic_tx": 800000, "traffic_rx": 1200000},
            {"name": "eth2", "speed": 10000, "status": 1, "traffic_tx": 5000000, "traffic_rx": 4500000},
        ]
        
        for interface in interfaces:
            self.interface_speed.labels(interface=interface['name']).set(interface['speed'])
            self.interface_status.labels(interface=interface['name']).set(interface['status'])
            self.interface_traffic.labels(interface=interface['name'], direction='tx').set(interface['traffic_tx'])
            self.interface_traffic.labels(interface=interface['name'], direction='rx').set(interface['traffic_rx'])
    
    def _update_failover_metrics(self):
        """Update failover metrics"""
        # Simulated failover data
        self.failover_status.labels(group='primary_failover').set(1)
    
    def _update_network_info(self):
        """Update network information"""
        self.network_info.info({
            'version': '1.0',
            'system': 'Campus IBN NMS',
            'vendor': 'OpenSource'
        })