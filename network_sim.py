import random
from datetime import datetime, timedelta
 
INDUSTRIAL_DEVICES = [
    {"id":"PLC-001","name":"Siemens S7-1500","type":"PLC",
     "protocol":"OPC UA","ip":"192.168.1.10","port":4840},
    {"id":"PLC-002","name":"Allen-Bradley CompactLogix","type":"PLC",
     "protocol":"EtherNet/IP","ip":"192.168.1.11","port":44818},
    {"id":"HMI-001","name":"Siemens TP700 Comfort","type":"HMI",
     "protocol":"OPC UA","ip":"192.168.1.20","port":4840},
    {"id":"RTU-001","name":"Schneider Modbus RTU","type":"RTU",
     "protocol":"Modbus TCP","ip":"192.168.1.30","port":502},
    {"id":"RTU-002","name":"ABB Remote I/O","type":"RTU",
     "protocol":"Modbus TCP","ip":"192.168.1.31","port":502},
    {"id":"MQTT-001","name":"Mosquitto Broker","type":"Broker",
     "protocol":"MQTT","ip":"192.168.1.50","port":1883},
    {"id":"SCADA-001","name":"WinCC OA Server","type":"SCADA",
     "protocol":"OPC UA","ip":"192.168.1.100","port":4840},
    {"id":"EWS-001","name":"Engineering Workstation","type":"EWS",
     "protocol":"SSH/HTTPS","ip":"192.168.1.200","port":22},
]
 
ATTACK_TYPES = [
    {"name":"Port Scan","severity":"Medium",
     "desc":"Sequential connection attempts on multiple ports"},
    {"name":"Unauthorized Modbus Write","severity":"Critical",
     "desc":"Write command from unknown IP to Modbus device"},
    {"name":"OPC UA Brute Force","severity":"High",
     "desc":"Repeated authentication failures on OPC UA server"},
    {"name":"MQTT Topic Injection","severity":"High",
     "desc":"Publishing to restricted control topics"},
    {"name":"ARP Spoofing","severity":"Critical",
     "desc":"MAC address conflict detected on network segment"},
    {"name":"Firmware Upload Attempt","severity":"Critical",
     "desc":"Unauthorized firmware upload to PLC detected"},
    {"name":"Replay Attack","severity":"High",
     "desc":"Duplicate packet sequence detected"},
    {"name":"DNS Tunneling","severity":"Medium",
     "desc":"Suspicious DNS query patterns detected"},
]
 
class NetworkMonitor:
    def __init__(self):
        self.devices = INDUSTRIAL_DEVICES.copy()
        self.alerts = []
        self.traffic_log = []
        self.stats = {"total_packets":0,"blocked_packets":0,
                      "active_connections":0,"uptime_hours":0}
 
    def generate_traffic(self, n=50):
        new_traffic = []
        for _ in range(n):
            src = random.choice(self.devices)
            dst = random.choice([d for d in self.devices if d["id"]!=src["id"]])
            ts = datetime.now()-timedelta(seconds=random.randint(0,300))
            is_suspicious = random.random() < 0.08
            entry = {
                "timestamp":ts.strftime("%Y-%m-%d %H:%M:%S"),
                "src_ip":src["ip"],"src_device":src["name"],
                "dst_ip":dst["ip"],"dst_device":dst["name"],
                "protocol":random.choice([src["protocol"],dst["protocol"]]),
                "port":dst["port"],
                "bytes":random.randint(64,4096),
                "status":"BLOCKED" if is_suspicious else "OK",
                "suspicious":is_suspicious,
            }
            if is_suspicious:
                attack = random.choice(ATTACK_TYPES)
                entry["alert_type"]=attack["name"]
                entry["severity"]=attack["severity"]
                entry["alert_desc"]=attack["desc"]
                self.alerts.append(entry)
            new_traffic.append(entry)
        self.traffic_log = new_traffic + self.traffic_log
        self.traffic_log = self.traffic_log[:500]
        self.stats["total_packets"]+=n
        self.stats["blocked_packets"]+=sum(1 for t in new_traffic if t["suspicious"])
        self.stats["active_connections"]=random.randint(12,25)
        self.stats["uptime_hours"]=round(random.uniform(100,999),1)
        return new_traffic
 
    def get_device_status(self):
        statuses = []
        for d in self.devices:
            n_alerts=sum(1 for a in self.alerts[-100:] if a.get("dst_ip")==d["ip"])
            status=("Critical" if n_alerts>3 else "Warning" if n_alerts>0 else "Online")
            statuses.append({**d,"status":status,"alerts":n_alerts})
        return statuses
 
monitor = NetworkMonitor()
monitor.generate_traffic(200)
