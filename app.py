from flask import Flask, render_template_string, jsonify
from network_sim import monitor
 
app = Flask(__name__)
 
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Industrial Network Security Monitor</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',Arial,sans-serif;background:#0a0e17;color:#c8d6e5}
.header{background:linear-gradient(135deg,#1a1f36,#0d1117);padding:20px 30px;
  border-bottom:2px solid #00b4d8;display:flex;justify-content:space-between;align-items:center}
.header h1{color:#00b4d8;font-size:22px}
.header .status{color:#00e676;font-size:14px}
.dashboard{padding:20px 30px}
.kpi-row{display:grid;grid-template-columns:repeat(4,1fr);gap:15px;margin-bottom:20px}
.kpi{background:#141a2e;border-radius:10px;padding:18px;border-left:4px solid #00b4d8}
.kpi .label{font-size:12px;color:#8899aa;text-transform:uppercase;letter-spacing:1px}
.kpi .value{font-size:28px;font-weight:700;color:#e8f0fe;margin-top:4px}
.kpi.critical{border-left-color:#e74c3c}
.kpi.critical .value{color:#e74c3c}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:15px;margin-bottom:20px}
.panel{background:#141a2e;border-radius:10px;padding:18px}
.panel h3{color:#00b4d8;font-size:15px;margin-bottom:12px;
  border-bottom:1px solid #1e2a4a;padding-bottom:8px}
table{width:100%;border-collapse:collapse;font-size:13px}
th{text-align:left;color:#8899aa;padding:8px 6px;border-bottom:1px solid #1e2a4a;font-weight:600}
td{padding:7px 6px;border-bottom:1px solid #0d1117}
.badge{padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600}
.badge-critical{background:#5c1a1a;color:#ff6b6b}
.badge-high{background:#5c3a1a;color:#ffa06b}
.badge-medium{background:#5c5a1a;color:#ffd06b}
.badge-online{background:#1a5c2a;color:#6bff8b}
.badge-warning{background:#5c5a1a;color:#ffd06b}
.badge-ok{background:#1a5c2a;color:#6bff8b}
.badge-blocked{background:#5c1a1a;color:#ff6b6b}
.traffic-log{max-height:350px;overflow-y:auto}
.footer{text-align:center;padding:15px;color:#556;font-size:12px}
.refresh-btn{background:#00b4d8;color:#0a0e17;border:none;padding:8px 16px;
  border-radius:6px;cursor:pointer;font-weight:600;font-size:13px}
.refresh-btn:hover{background:#00d4f8}
</style></head><body>
<div class="header">
  <h1>&#128274; Industrial Network Security Monitor</h1>
  <div><span class="status">&#9679; MONITORING ACTIVE</span>
  &nbsp;<button class="refresh-btn" onclick="refresh()">&#8635; Refresh</button></div>
</div>
<div class="dashboard">
  <div class="kpi-row" id="kpis"></div>
  <div class="grid-2">
    <div class="panel"><h3>&#128225; Device Status</h3>
      <table id="devices"><thead><tr><th>Device</th><th>Type</th>
      <th>Protocol</th><th>IP</th><th>Status</th><th>Alerts</th></tr></thead>
      <tbody></tbody></table></div>
    <div class="panel"><h3>&#9888; Security Alerts</h3>
      <table id="alerts"><thead><tr><th>Time</th><th>Attack Type</th>
      <th>Severity</th><th>Target</th></tr></thead>
      <tbody></tbody></table></div>
  </div>
  <div class="panel"><h3>&#128200; Traffic Log (Last 50)</h3>
    <div class="traffic-log">
      <table id="traffic"><thead><tr><th>Time</th><th>Source</th>
      <th>Destination</th><th>Protocol</th><th>Port</th><th>Bytes</th>
      <th>Status</th></tr></thead><tbody></tbody></table></div></div>
</div>
<div class="footer">Industrial Network Security Monitor | ICS/SCADA Cybersecurity
 | Oscar Vincent Dbritto </div>
<script>
async function refresh(){
  const r=await fetch('/api/data');const d=await r.json();
  document.getElementById('kpis').innerHTML=[
    kpi('Total Packets',d.stats.total_packets.toLocaleString(),''),
    kpi('Blocked',d.stats.blocked_packets,'critical'),
    kpi('Active Connections',d.stats.active_connections,''),
    kpi('Uptime',d.stats.uptime_hours+'h',''),
  ].join('');
  const db=document.querySelector('#devices tbody');
  db.innerHTML=d.devices.map(v=>
    '<tr><td>'+v.name+'</td><td>'+v.type+'</td><td>'+v.protocol+
    '</td><td>'+v.ip+'</td><td><span class="badge badge-'+
    v.status.toLowerCase()+'">'+v.status+'</span></td><td>'+v.alerts+'</td></tr>'
  ).join('');
  const ab=document.querySelector('#alerts tbody');
  ab.innerHTML=d.alerts.slice(0,15).map(a=>
    '<tr><td>'+a.timestamp+'</td><td>'+a.alert_type+
    '</td><td><span class="badge badge-'+a.severity.toLowerCase()+
    '">'+a.severity+'</span></td><td>'+a.dst_device+'</td></tr>'
  ).join('');
  const tb=document.querySelector('#traffic tbody');
  tb.innerHTML=d.traffic.slice(0,50).map(t=>
    '<tr><td>'+t.timestamp+'</td><td>'+t.src_device+'</td><td>'+
    t.dst_device+'</td><td>'+t.protocol+'</td><td>'+t.port+
    '</td><td>'+t.bytes+'</td><td><span class="badge badge-'+
    t.status.toLowerCase()+'">'+t.status+'</span></td></tr>'
  ).join('');
}
function kpi(l,v,cls){return '<div class="kpi '+(cls||'')+
  '"><div class="label">'+l+'</div><div class="value">'+v+'</div></div>';}
refresh();setInterval(refresh,5000);
</script></body></html>"""
 
@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)
 
@app.route("/api/data")
def api_data():
    monitor.generate_traffic(20)
    return jsonify({
        "stats":monitor.stats,
        "devices":monitor.get_device_status(),
        "alerts":monitor.alerts[-50:],
        "traffic":monitor.traffic_log[:50],
    })
 
if __name__=="__main__":
    app.run(debug=True, port=5000)