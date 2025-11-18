from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import json
import threading
import time
import logging
import random
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'campus-ibn-secret-key-2024'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Enhanced demo data
demo_interfaces = [
    {"name": "gigabitethernet0/1", "ip_address": "192.168.1.10/24", "speed": "1G", "status": "up", "vlan": 100, "traffic_rx": 0, "traffic_tx": 0, "description": "Faculty Network"},
    {"name": "gigabitethernet0/2", "ip_address": "192.168.1.11/24", "speed": "1G", "status": "up", "vlan": 200, "traffic_rx": 0, "traffic_tx": 0, "description": "Student Network"},
    {"name": "tengigabitethernet0/1", "ip_address": "192.168.1.12/24", "speed": "10G", "status": "up", "vlan": 300, "traffic_rx": 0, "traffic_tx": 0, "description": "Data Center"},
    {"name": "fortygigabitethernet0/1", "ip_address": "192.168.1.13/24", "speed": "40G", "status": "down", "vlan": 400, "traffic_rx": 0, "traffic_tx": 0, "description": "Backbone"},
]

# Network ranges configuration
network_ranges = [
    {"name": "Faculty", "range": "192.168.100.0/24", "vlan": 100, "gateway": "192.168.100.1"},
    {"name": "Student", "range": "192.168.200.0/24", "vlan": 200, "gateway": "192.168.200.1"},
    {"name": "Admin", "range": "192.168.300.0/24", "vlan": 300, "gateway": "192.168.300.1"},
    {"name": "Guest", "range": "192.168.400.0/24", "vlan": 400, "gateway": "192.168.400.1"},
]

class NetworkManager:
    def __init__(self):
        self.device_status = "disconnected"
        self.current_config = None
        self.monitoring_active = False
        self.failover_active = False
        self.failover_groups = []
        self.network_services = {}
        self.security_rules = []
        self.qos_config = {}
    
    def connect_to_device(self):
        """Simulate device connection"""
        logger.info("Connecting to network device...")
        time.sleep(2)
        self.device_status = "connected"
        logger.info("Successfully connected to network device")
        return True
    
    def apply_intent(self, intent_data):
        """Apply enhanced network intent"""
        try:
            logger.info(f"Applying enhanced network intent: {intent_data}")
            time.sleep(3)
            
            # Update interfaces based on intent
            for interface in demo_interfaces:
                if 'interface_speed' in intent_data:
                    interface['speed'] = intent_data['interface_speed']
            
            # Store enhanced configuration
            self.current_config = intent_data
            self.monitoring_active = intent_data.get('monitoring_enabled', True)
            self.failover_active = intent_data.get('failover_enabled', True)
            
            # Process enhanced features
            if 'failover_config' in intent_data:
                self.failover_groups = intent_data['failover_config'].get('groups', [])
            
            if 'network_services' in intent_data:
                self.network_services = intent_data['network_services']
            
            if 'security_rules' in intent_data:
                self.security_rules = intent_data['security_rules']
            
            if 'qos_config' in intent_data:
                self.qos_config = intent_data['qos_config']
            
            logger.info("Enhanced network intent applied successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error applying intent: {e}")
            return False

# Initialize network manager
network_manager = NetworkManager()

@app.route('/')
def index():
    """Main web interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Campus IBN NMS</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .container { max-width: 1400px; margin: 0 auto; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 20px; text-align: center; }
            .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
            .card { background: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            .card h2 { color: #333; margin-bottom: 20px; border-bottom: 2px solid #f0f0f0; padding-bottom: 10px; }
            .form-group { margin-bottom: 15px; }
            .form-group label { display: block; margin-bottom: 5px; font-weight: bold; color: #333; }
            .form-group input, .form-group select, .form-group textarea { width: 100%; padding: 10px; border: 2px solid #e9ecef; border-radius: 5px; font-size: 14px; }
            .form-group input:focus, .form-group select:focus { outline: none; border-color: #007cba; }
            .checkbox-group { display: flex; align-items: center; gap: 10px; margin: 10px 0; }
            .checkbox-group input { width: auto; }
            .btn { background: #007cba; color: white; border: none; padding: 12px 24px; border-radius: 5px; cursor: pointer; font-size: 16px; margin: 5px; }
            .btn:hover { background: #005a87; }
            .btn-success { background: #28a745; }
            .btn-danger { background: #dc3545; }
            .status-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; margin: 2px; }
            .status-connected { background: #28a745; color: white; }
            .status-disconnected { background: #dc3545; color: white; }
            .interface-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px; }
            .interface-card { background: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 4px solid #28a745; }
            .interface-card.down { border-left-color: #dc3545; }
            .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
            .metric-card { background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .metric-value { font-size: 2em; font-weight: bold; color: #007cba; margin: 10px 0; }
            .tab-container { margin: 20px 0; }
            .tabs { display: flex; gap: 10px; margin-bottom: 20px; }
            .tab { padding: 10px 20px; background: #e9ecef; border: none; border-radius: 5px; cursor: pointer; }
            .tab.active { background: #007cba; color: white; }
            .tab-content { display: none; }
            .tab-content.active { display: block; }
            .service-item { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #17a2b8; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎯 Campus Intent-Based Networking NMS</h1>
                <p>Enhanced Automated Network Management System</p>
                <div id="system-status">
                    <span class="status-badge status-disconnected" id="device-status">Disconnected</span>
                    <span class="status-badge" id="monitoring-status">Monitoring: Inactive</span>
                    <span class="status-badge" id="failover-status">Failover: Disabled</span>
                </div>
            </div>

            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">Total Interfaces</div>
                    <div class="metric-value" id="total-interfaces">0</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Active Interfaces</div>
                    <div class="metric-value" id="active-interfaces">0</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">System Health</div>
                    <div class="metric-value" id="health-score">0%</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Network Ranges</div>
                    <div class="metric-value" id="network-ranges-count">0</div>
                </div>
            </div>

            <div class="tab-container">
                <div class="tabs">
                    <button class="tab active" onclick="switchTab('basic')">Basic Configuration</button>
                    <button class="tab" onclick="switchTab('advanced')">Advanced Features</button>
                    <button class="tab" onclick="switchTab('monitoring')">Monitoring</button>
                </div>

                <div id="basic-tab" class="tab-content active">
                    <div class="grid">
                        <div class="card">
                            <h2>📋 Basic Network Intent</h2>
                            <form id="intent-form">
                                <div class="form-group">
                                    <label for="network-name">Network Name:</label>
                                    <input type="text" id="network-name" value="Campus-LAN" required>
                                </div>
                                
                                <div class="form-group">
                                    <label for="network-range">Primary Network Range:</label>
                                    <input type="text" id="network-range" value="192.168.100.0" required>
                                </div>
                                
                                <div class="form-group">
                                    <label for="subnet-mask">Subnet Mask:</label>
                                    <input type="text" id="subnet-mask" value="24" required>
                                </div>
                                
                                <div class="form-group">
                                    <label for="interface-speed">Default Interface Speed:</label>
                                    <select id="interface-speed" required>
                                        <option value="100M">100 Mbps</option>
                                        <option value="1G" selected>1 Gbps</option>
                                        <option value="10G">10 Gbps</option>
                                        <option value="25G">25 Gbps</option>
                                        <option value="40G">40 Gbps</option>
                                        <option value="100G">100 Gbps</option>
                                    </select>
                                </div>
                                
                                <div class="checkbox-group">
                                    <input type="checkbox" id="failover-enabled" checked>
                                    <label for="failover-enabled">Enable Failover System</label>
                                </div>
                                
                                <div class="checkbox-group">
                                    <input type="checkbox" id="monitoring-enabled" checked>
                                    <label for="monitoring-enabled">Enable Monitoring</label>
                                </div>
                                
                                <button type="submit" class="btn">🚀 Apply Network Intent</button>
                            </form>
                        </div>

                        <div class="card">
                            <h2>🔌 Network Interfaces</h2>
                            <div class="interface-grid" id="interfaces-list">
                                <p>Loading interfaces...</p>
                            </div>
                            <button class="btn" onclick="refreshInterfaces()">🔄 Refresh Interfaces</button>
                        </div>
                    </div>
                </div>

                <div id="advanced-tab" class="tab-content">
                    <div class="grid">
                        <div class="card">
                            <h2>🔄 Failover Configuration</h2>
                            <div class="form-group">
                                <label for="failover-primary">Primary Interface:</label>
                                <select id="failover-primary">
                                    <option value="gigabitethernet0/1">gigabitethernet0/1</option>
                                    <option value="gigabitethernet0/2">gigabitethernet0/2</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="failover-backup">Backup Interface:</label>
                                <select id="failover-backup">
                                    <option value="tengigabitethernet0/1">tengigabitethernet0/1</option>
                                    <option value="fortygigabitethernet0/1">fortygigabitethernet0/1</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="failover-threshold">Failover Threshold (seconds):</label>
                                <input type="number" id="failover-threshold" value="5" min="1" max="60">
                            </div>
                        </div>

                        <div class="card">
                            <h2>🛡️ Security Configuration</h2>
                            <div class="form-group">
                                <label for="firewall-action">Firewall Action:</label>
                                <select id="firewall-action">
                                    <option value="allow">Allow</option>
                                    <option value="deny">Deny</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="firewall-source">Source IP:</label>
                                <input type="text" id="firewall-source" value="192.168.100.0/24">
                            </div>
                            <div class="form-group">
                                <label for="firewall-destination">Destination IP:</label>
                                <input type="text" id="firewall-destination" value="any">
                            </div>
                            <button class="btn btn-success" onclick="addFirewallRule()">➕ Add Rule</button>
                        </div>
                    </div>

                    <div class="grid">
                        <div class="card">
                            <h2>📡 Network Services</h2>
                            <div class="form-group">
                                <label for="dns-servers">DNS Servers (comma separated):</label>
                                <input type="text" id="dns-servers" value="8.8.8.8,8.8.4.4">
                            </div>
                            <div class="form-group">
                                <label for="ntp-servers">NTP Servers (comma separated):</label>
                                <input type="text" id="ntp-servers" value="pool.ntp.org">
                            </div>
                            <div class="checkbox-group">
                                <input type="checkbox" id="dhcp-enabled" checked>
                                <label for="dhcp-enabled">Enable DHCP Service</label>
                            </div>
                            <div class="form-group">
                                <label for="dhcp-range">DHCP Range:</label>
                                <input type="text" id="dhcp-range" value="192.168.100.100-192.168.100.200">
                            </div>
                        </div>

                        <div class="card">
                            <h2>⚡ QoS Configuration</h2>
                            <div class="form-group">
                                <label for="qos-voice">Voice Priority Interface:</label>
                                <select id="qos-voice">
                                    <option value="gigabitethernet0/1">gigabitethernet0/1</option>
                                    <option value="">None</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="qos-video">Video Priority Interface:</label>
                                <select id="qos-video">
                                    <option value="gigabitethernet0/2">gigabitethernet0/2</option>
                                    <option value="">None</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label for="qos-data">Data Interface:</label>
                                <select id="qos-data">
                                    <option value="tengigabitethernet0/1">tengigabitethernet0/1</option>
                                    <option value="">None</option>
                                </select>
                            </div>
                        </div>
                    </div>

                    <div class="card">
                        <h2>🌐 Additional Network Ranges</h2>
                        <div id="network-ranges-list">
                            <!-- Network ranges will be populated here -->
                        </div>
                        <button class="btn btn-success" onclick="applyAdvancedConfig()">💾 Apply Advanced Configuration</button>
                    </div>
                </div>

                <div id="monitoring-tab" class="tab-content">
                    <div class="card">
                        <h2>📊 Real-time Monitoring</h2>
                        <div class="metrics-grid">
                            <div class="metric-card">
                                <div class="metric-label">Total Traffic</div>
                                <div class="metric-value" id="total-traffic">0 B</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-label">Packet Loss</div>
                                <div class="metric-value" id="packet-loss">0%</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-label">Latency</div>
                                <div class="metric-value" id="latency">0ms</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-label">Uptime</div>
                                <div class="metric-value" id="uptime">0h</div>
                            </div>
                        </div>
                        <div id="services-status">
                            <h3>🛠️ Services Status</h3>
                            <!-- Services status will be populated here -->
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
        <script>
            const socket = io();
            let startTime = Date.now();

            // Socket event handlers
            socket.on('connect', function() {
                console.log('Connected to server');
                updateDeviceStatus('connected');
            });

            socket.on('device_status', function(data) {
                updateDeviceStatus(data.status);
            });

            socket.on('intent_applied', function(data) {
                alert(data.success ? '✅ ' + data.message : '❌ ' + data.message);
                refreshInterfaces();
                updateMetrics();
            });

            socket.on('metrics_update', function(data) {
                updateInterfaceDisplay(data.interfaces);
                updateMetrics();
            });

            // Tab management
            function switchTab(tabName) {
                // Hide all tabs
                document.querySelectorAll('.tab-content').forEach(tab => {
                    tab.classList.remove('active');
                });
                document.querySelectorAll('.tab').forEach(tab => {
                    tab.classList.remove('active');
                });

                // Show selected tab
                document.getElementById(tabName + '-tab').classList.add('active');
                event.target.classList.add('active');
            }

            // Form submission
            document.getElementById('intent-form').addEventListener('submit', function(e) {
                e.preventDefault();
                applyEnhancedIntent();
            });

            function applyEnhancedIntent() {
                const applyBtn = document.querySelector('#intent-form button');
                applyBtn.disabled = true;
                applyBtn.textContent = '🔄 Applying...';

                const intent = {
                    network_name: document.getElementById('network-name').value,
                    network_range: document.getElementById('network-range').value,
                    subnet_mask: document.getElementById('subnet-mask').value,
                    interface_speed: document.getElementById('interface-speed').value,
                    failover_enabled: document.getElementById('failover-enabled').checked,
                    monitoring_enabled: document.getElementById('monitoring-enabled').checked,
                    failover_config: {
                        primary: document.getElementById('failover-primary').value,
                        backup: document.getElementById('failover-backup').value,
                        threshold: document.getElementById('failover-threshold').value
                    },
                    network_services: {
                        dns_servers: document.getElementById('dns-servers').value.split(','),
                        ntp_servers: document.getElementById('ntp-servers').value.split(','),
                        dhcp_enabled: document.getElementById('dhcp-enabled').checked,
                        dhcp_range: document.getElementById('dhcp-range').value
                    },
                    qos_config: {
                        voice: document.getElementById('qos-voice').value,
                        video: document.getElementById('qos-video').value,
                        data: document.getElementById('qos-data').value
                    },
                    security_rules: getSecurityRules()
                };

                fetch('/api/intent', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(intent)
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showAlert('✅ ' + data.message, 'success');
                    } else {
                        showAlert('❌ ' + data.message, 'error');
                    }
                })
                .catch(error => {
                    showAlert('❌ Network error: ' + error, 'error');
                })
                .finally(() => {
                    applyBtn.disabled = false;
                    applyBtn.textContent = '🚀 Apply Network Intent';
                });
            }

            function applyAdvancedConfig() {
                // Apply only advanced configuration
                const advancedConfig = {
                    failover_config: {
                        primary: document.getElementById('failover-primary').value,
                        backup: document.getElementById('failover-backup').value,
                        threshold: document.getElementById('failover-threshold').value
                    },
                    network_services: {
                        dns_servers: document.getElementById('dns-servers').value.split(','),
                        ntp_servers: document.getElementById('ntp-servers').value.split(','),
                        dhcp_enabled: document.getElementById('dhcp-enabled').checked,
                        dhcp_range: document.getElementById('dhcp-range').value
                    },
                    qos_config: {
                        voice: document.getElementById('qos-voice').value,
                        video: document.getElementById('qos-video').value,
                        data: document.getElementById('qos-data').value
                    },
                    security_rules: getSecurityRules()
                };

                fetch('/api/advanced-config', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(advancedConfig)
                })
                .then(response => response.json())
                .then(data => {
                    showAlert(data.success ? '✅ Advanced configuration applied!' : '❌ ' + data.message, 
                             data.success ? 'success' : 'error');
                });
            }

            function getSecurityRules() {
                // In a real implementation, this would collect multiple rules
                return [{
                    action: document.getElementById('firewall-action').value,
                    source: document.getElementById('firewall-source').value,
                    destination: document.getElementById('firewall-destination').value
                }];
            }

            function addFirewallRule() {
                alert('Firewall rule added to configuration (will be applied with main intent)');
            }

            // Utility functions
            function updateDeviceStatus(status) {
                const statusElement = document.getElementById('device-status');
                statusElement.textContent = status;
                statusElement.className = `status-badge ${status === 'connected' ? 'status-connected' : 'status-disconnected'}`;
            }

            function showAlert(message, type) {
                // Simple alert for demo
                alert(message);
            }

            function refreshInterfaces() {
                fetch('/api/interfaces')
                    .then(response => response.json())
                    .then(data => {
                        updateInterfaceDisplay(data.interfaces);
                    })
                    .catch(error => {
                        showAlert('❌ Failed to load interfaces: ' + error, 'error');
                    });
            }

            function updateInterfaceDisplay(interfaces) {
                const interfacesList = document.getElementById('interfaces-list');
                
                if (interfaces && interfaces.length > 0) {
                    interfacesList.innerHTML = interfaces.map(iface => `
                        <div class="interface-card ${iface.status === 'down' ? 'down' : ''}">
                            <h3>${iface.name}</h3>
                            <p><strong>IP:</strong> ${iface.ip_address}</p>
                            <p><strong>Speed:</strong> ${iface.speed}</p>
                            <p><strong>VLAN:</strong> ${iface.vlan}</p>
                            <p><strong>Description:</strong> ${iface.description || 'N/A'}</p>
                            <p><strong>Traffic RX/TX:</strong> ${formatBytes(iface.traffic_rx)} / ${formatBytes(iface.traffic_tx)}</p>
                            <span class="status-badge ${iface.status === 'up' ? 'status-connected' : 'status-disconnected'}">
                                ${iface.status.toUpperCase()}
                            </span>
                        </div>
                    `).join('');
                } else {
                    interfacesList.innerHTML = '<p>No interface data available</p>';
                }
            }

            function updateMetrics() {
                fetch('/api/metrics')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('total-interfaces').textContent = data.total_interfaces;
                        document.getElementById('active-interfaces').textContent = data.up_interfaces;
                        document.getElementById('health-score').textContent = data.health_score + '%';
                        document.getElementById('network-ranges-count').textContent = data.network_ranges || 4;
                        document.getElementById('total-traffic').textContent = formatBytes(data.total_traffic);
                        document.getElementById('packet-loss').textContent = '0%';
                        document.getElementById('latency').textContent = '5ms';
                        
                        // Calculate uptime
                        const uptimeMs = Date.now() - startTime;
                        const uptimeHours = Math.floor(uptimeMs / (1000 * 60 * 60));
                        document.getElementById('uptime').textContent = uptimeHours + 'h';
                    });
            }

            function formatBytes(bytes) {
                if (bytes === 0) return '0 B';
                const k = 1024;
                const sizes = ['B', 'KB', 'MB', 'GB'];
                const i = Math.floor(Math.log(bytes) / Math.log(k));
                return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
            }

            function loadNetworkRanges() {
                const container = document.getElementById('network-ranges-list');
                container.innerHTML = networkRanges.map(range => `
                    <div class="service-item">
                        <h4>${range.name} Network</h4>
                        <p><strong>Range:</strong> ${range.range}</p>
                        <p><strong>VLAN:</strong> ${range.vlan}</p>
                        <p><strong>Gateway:</strong> ${range.gateway}</p>
                    </div>
                `).join('');
            }

            // Initialize
            document.addEventListener('DOMContentLoaded', function() {
                refreshInterfaces();
                updateMetrics();
                loadNetworkRanges();
                
                // Update metrics every 5 seconds
                setInterval(updateMetrics, 5000);
                
                // Update system status every 10 seconds
                setInterval(() => {
                    fetch('/api/status')
                        .then(response => response.json())
                        .then(data => {
                            updateDeviceStatus(data.device_status);
                            document.getElementById('monitoring-status').textContent = 
                                'Monitoring: ' + (data.monitoring === 'active' ? 'Active' : 'Inactive');
                            document.getElementById('failover-status').textContent = 
                                'Failover: ' + (data.failover === 'enabled' ? 'Enabled' : 'Disabled');
                        });
                }, 10000);
            });

            // Global variable for network ranges
            const networkRanges = [
                {name: "Faculty", range: "192.168.100.0/24", vlan: 100, gateway: "192.168.100.1"},
                {name: "Student", range: "192.168.200.0/24", vlan: 200, gateway: "192.168.200.1"},
                {name: "Admin", range: "192.168.50.0/24", vlan: 50, gateway: "192.168.50.1"},
                {name: "Guest", range: "192.168.99.0/24", vlan: 99, gateway: "192.168.99.1"}
            ];
        </script>
    </body>
    </html>
    """

@app.route('/api/intent', methods=['POST'])
def apply_intent():
    """Apply enhanced network intent API endpoint"""
    try:
        intent_data = request.json
        logger.info(f"Received enhanced intent: {intent_data}")
        
        # Validate required fields
        required_fields = ['network_name', 'network_range', 'subnet_mask', 'interface_speed']
        for field in required_fields:
            if field not in intent_data:
                return jsonify({
                    'success': False, 
                    'message': f'Missing required field: {field}'
                }), 400
        
        # Apply intent
        success = network_manager.apply_intent(intent_data)
        
        if success:
            # Broadcast update to all connected clients
            socketio.emit('intent_applied', {
                'success': True,
                'message': 'Enhanced network intent applied successfully',
                'config': intent_data
            })
            
            return jsonify({
                'success': True, 
                'message': 'Enhanced intent applied successfully'
            })
        else:
            return jsonify({
                'success': False, 
                'message': 'Failed to apply intent'
            }), 500
            
    except Exception as e:
        logger.error(f"API error: {e}")
        return jsonify({
            'success': False, 
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/api/advanced-config', methods=['POST'])
def apply_advanced_config():
    """Apply only advanced configuration"""
    try:
        config_data = request.json
        logger.info(f"Applying advanced configuration: {config_data}")
        
        # Update network manager with advanced config
        if 'failover_config' in config_data:
            network_manager.failover_groups = [config_data['failover_config']]
        
        if 'network_services' in config_data:
            network_manager.network_services = config_data['network_services']
        
        if 'qos_config' in config_data:
            network_manager.qos_config = config_data['qos_config']
        
        if 'security_rules' in config_data:
            network_manager.security_rules = config_data['security_rules']
        
        return jsonify({
            'success': True,
            'message': 'Advanced configuration applied successfully'
        })
        
    except Exception as e:
        logger.error(f"Advanced config error: {e}")
        return jsonify({
            'success': False,
            'message': f'Error applying advanced config: {str(e)}'
        }), 500

@app.route('/api/interfaces')
def get_interfaces():
    """Get interface information"""
    # Update traffic stats for demo
    for interface in demo_interfaces:
        if interface['status'] == 'up':
            interface['traffic_rx'] += random.randint(1000, 10000)
            interface['traffic_tx'] += random.randint(500, 5000)
    
    return jsonify({'interfaces': demo_interfaces})

@app.route('/api/status')
def get_status():
    """Get system status"""
    return jsonify({
        'device_status': network_manager.device_status,
        'monitoring': 'active' if network_manager.monitoring_active else 'inactive',
        'failover': 'enabled' if network_manager.failover_active else 'disabled',
        'current_config': network_manager.current_config
    })

@app.route('/api/metrics')
def get_metrics():
    """Get enhanced system metrics"""
    total_interfaces = len(demo_interfaces)
    up_interfaces = sum(1 for i in demo_interfaces if i['status'] == 'up')
    total_traffic = sum(i['traffic_rx'] + i['traffic_tx'] for i in demo_interfaces)
    
    return jsonify({
        'total_interfaces': total_interfaces,
        'up_interfaces': up_interfaces,
        'down_interfaces': total_interfaces - up_interfaces,
        'total_traffic': total_traffic,
        'health_score': round((up_interfaces / total_interfaces) * 100, 1),
        'network_ranges': len(network_ranges),
        'failover_groups': len(network_manager.failover_groups),
        'security_rules': len(network_manager.security_rules)
    })

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info('Client connected')
    socketio.emit('device_status', {'status': network_manager.device_status})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info('Client disconnected')

def start_background_tasks():
    """Start background monitoring tasks"""
    def connect_device():
        """Connect to device in background"""
        time.sleep(1)
        network_manager.connect_to_device()
        socketio.emit('device_status', {'status': network_manager.device_status})
    
    def update_metrics():
        """Update metrics periodically"""
        while True:
            time.sleep(5)
            if network_manager.monitoring_active:
                # Update interface traffic
                for interface in demo_interfaces:
                    if interface['status'] == 'up':
                        interface['traffic_rx'] += random.randint(100, 1000)
                        interface['traffic_tx'] += random.randint(50, 500)
                
                # Broadcast metrics update
                socketio.emit('metrics_update', {
                    'interfaces': demo_interfaces,
                    'timestamp': time.time()
                })
    
    # Start background threads
    connect_thread = threading.Thread(target=connect_device, daemon=True)
    metrics_thread = threading.Thread(target=update_metrics, daemon=True)
    
    connect_thread.start()
    metrics_thread.start()

# Start background tasks when module loads
start_background_tasks()

if __name__ == '__main__':
    logger.info("Starting Enhanced Campus IBN NMS Web UI")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)