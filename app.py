from flask import Flask, render_template, jsonify, request, send_file, session, redirect, url_for
from flask_socketio import SocketIO, emit
from datetime import datetime, timedelta
import threading
import time
import random
import sqlite3
from io import StringIO, BytesIO
import os
import csv

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

# ============ DATABASE SETUP ============
def init_db():
    """Initialize database with correct schema"""
    conn = sqlite3.connect('iot_botnet.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL)''')
    
    # Attacks table with country column
    c.execute('''CREATE TABLE IF NOT EXISTS attacks
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp DATETIME,
                  source_ip TEXT,
                  destination_ip TEXT,
                  attack_type TEXT,
                  severity INTEGER,
                  protocol TEXT,
                  status TEXT,
                  country TEXT)''')
    
    # Devices table
    c.execute('''CREATE TABLE IF NOT EXISTS devices
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  device_id TEXT UNIQUE,
                  device_type TEXT,
                  ip_address TEXT,
                  status TEXT,
                  risk_score INTEGER)''')
    
    # Insert default admin
    c.execute("SELECT * FROM users WHERE username='admin'")
    if not c.fetchone():
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                 ('admin', 'admin123'))
    
    # Generate sample devices
    c.execute("SELECT COUNT(*) FROM devices")
    if c.fetchone()[0] == 0:
        device_types = ['Camera', 'Router', 'Smart TV', 'Thermostat', 'Doorbell', 'Speaker', 'Light', 'Hub']
        for i in range(1200):
            risk = random.randint(0, 100)
            status = 'compromised' if risk > 70 else 'active'
            c.execute("INSERT INTO devices (device_id, device_type, ip_address, status, risk_score) VALUES (?, ?, ?, ?, ?)",
                     (f'IOT_{i:04d}', random.choice(device_types), f'192.168.1.{i+2}', status, risk))
    
    conn.commit()
    conn.close()
    print("✅ Database initialized")

init_db()

# ============ GEOGRAPHIC DATA ============
COUNTRIES = ['China', 'Russia', 'USA', 'Brazil', 'India', 'Others']
COUNTRY_COLORS = {
    'China': '#dc3545',
    'Russia': '#ff6b6b',
    'USA': '#ffc107',
    'Brazil': '#17a2b8',
    'India': '#28a745',
    'Others': '#6c757d'
}

def get_country_from_ip(ip):
    """Simulate getting country from IP address"""
    weights = [28, 21, 15, 11, 8, 17]
    return random.choices(COUNTRIES, weights=weights)[0]

def get_attack_geographic_origin():
    """Get attack distribution by geographic origin"""
    conn = sqlite3.connect('iot_botnet.db')
    c = conn.cursor()
    
    c.execute("SELECT country, COUNT(*) FROM attacks GROUP BY country")
    db_counts = dict(c.fetchall())
    conn.close()
    
    default_counts = {
        'China': 342, 'Russia': 256, 'USA': 189,
        'Brazil': 134, 'India': 98, 'Others': 207
    }
    
    geo_data = {}
    for country in COUNTRIES:
        attacks = db_counts.get(country, default_counts.get(country, 0))
        geo_data[country] = {
            'attacks': attacks,
            'percentage': 0,
            'color': COUNTRY_COLORS[country]
        }
    
    total = sum(v['attacks'] for v in geo_data.values())
    if total > 0:
        for country in geo_data:
            geo_data[country]['percentage'] = round(geo_data[country]['attacks'] / total * 100, 1)
    
    return geo_data

# ============ GLOBAL VARIABLES ============
attack_counter = 0
total_attacks = 0

# ============ SIMULATION FUNCTION ============
def simulate_real_time_attacks():
    global attack_counter, total_attacks
    
    attack_types = ['Mirai', 'DDoS', 'Brute Force', 'DNS Tunnel', 'Port_Scan']
    protocols = ['TCP', 'UDP', 'HTTP', 'HTTPS', 'DNS']
    
    while True:
        time.sleep(random.uniform(1, 3))
        
        if random.random() < 0.4:
            attack_counter += 1
            total_attacks += 1
            
            source_ip = f'{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}'
            country = get_country_from_ip(source_ip)
            
            attack = {
                'id': attack_counter,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'attack_type': random.choice(attack_types),
                'severity': random.randint(1, 10),
                'source_ip': source_ip,
                'destination_ip': f'192.168.{random.randint(1,10)}.{random.randint(2,254)}',
                'protocol': random.choice(protocols),
                'status': random.choice(['detected', 'blocked', 'mitigated']),
                'country': country
            }
            
            conn = sqlite3.connect('iot_botnet.db')
            c = conn.cursor()
            c.execute('''INSERT INTO attacks (timestamp, source_ip, destination_ip, attack_type, severity, protocol, status, country)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                      (attack['timestamp'], attack['source_ip'], attack['destination_ip'],
                       attack['attack_type'], attack['severity'], attack['protocol'], 
                       attack['status'], attack['country']))
            conn.commit()
            conn.close()
            
            socketio.emit('new_attack', attack)
            socketio.emit('counter_update', {'counter': attack_counter, 'total': total_attacks})
            socketio.emit('geo_update', get_attack_geographic_origin())
            
            print(f"⚔️ Attack #{total_attacks}: {attack['attack_type']} from {country}")

threading.Thread(target=simulate_real_time_attacks, daemon=True).start()
print("🚀 Attack simulation started")

# ============ HELPER FUNCTIONS ============
def get_dashboard_stats():
    conn = sqlite3.connect('iot_botnet.db')
    c = conn.cursor()
    
    try:
        c.execute("SELECT COUNT(*) FROM attacks")
        total_attacks_db = c.fetchone()[0] or 0
        
        c.execute("SELECT COUNT(*) FROM attacks WHERE timestamp > datetime('now', '-1 hour')")
        active_threats = c.fetchone()[0] or 0
        
        c.execute("SELECT COUNT(DISTINCT attack_type) FROM attacks")
        botnets_detected = c.fetchone()[0] or 0
        
        c.execute("SELECT COUNT(*) FROM devices")
        total_devices = c.fetchone()[0] or 0
        
        c.execute("SELECT COUNT(*) FROM devices WHERE status='compromised'")
        compromised = c.fetchone()[0] or 0
        
        c.execute("SELECT AVG(risk_score) FROM devices")
        avg_risk = c.fetchone()[0] or 0
        network_health = max(0, min(100, 100 - avg_risk))
        
        c.execute("SELECT attack_type, COUNT(*) FROM attacks GROUP BY attack_type")
        attack_dist = dict(c.fetchall())
        
        conn.close()
        
        return {
            'total_attacks': total_attacks_db,
            'active_threats': active_threats,
            'botnets_detected': botnets_detected,
            'total_devices': total_devices,
            'compromised_devices': compromised,
            'network_health': int(network_health),
            'attack_distribution': attack_dist,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        print(f"Error: {e}")
        conn.close()
        return {
            'total_attacks': 0,
            'active_threats': 0,
            'botnets_detected': 0,
            'total_devices': 1200,
            'compromised_devices': 0,
            'network_health': 89,
            'attack_distribution': {},
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

def get_recent_attacks(limit=20):
    conn = sqlite3.connect('iot_botnet.db')
    c = conn.cursor()
    c.execute("SELECT id, timestamp, source_ip, destination_ip, attack_type, severity, protocol, status, country FROM attacks ORDER BY timestamp DESC LIMIT ?", (limit,))
    attacks = c.fetchall()
    conn.close()
    
    return [{
        'id': a[0],
        'timestamp': a[1],
        'source_ip': a[2],
        'destination_ip': a[3],
        'attack_type': a[4],
        'severity': a[5],
        'protocol': a[6],
        'status': a[7],
        'country': a[8] if len(a) > 8 and a[8] else 'Unknown'
    } for a in attacks]

def get_all_devices():
    conn = sqlite3.connect('iot_botnet.db')
    c = conn.cursor()
    c.execute("SELECT device_id, device_type, ip_address, status, risk_score FROM devices LIMIT 50")
    devices = c.fetchall()
    conn.close()
    
    return [{
        'device_id': d[0],
        'device_type': d[1],
        'ip_address': d[2],
        'status': d[3],
        'risk_score': d[4]
    } for d in devices]

# ============ ROUTES ============
@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    return render_template('dashboard.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login_page'))

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    conn = sqlite3.connect('iot_botnet.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()
    
    if user:
        session['user'] = username
        return jsonify({'success': True})
    return jsonify({'success': False}), 401

@app.route('/api/stats')
def api_stats():
    return jsonify(get_dashboard_stats())

@app.route('/api/geo-attacks')
def api_geo_attacks():
    return jsonify(get_attack_geographic_origin())

@app.route('/api/attacks')
def api_attacks():
    limit = request.args.get('limit', 20, type=int)
    return jsonify(get_recent_attacks(limit))

@app.route('/api/attacks/recent')
def api_attacks_recent():
    limit = request.args.get('limit', 20, type=int)
    return jsonify(get_recent_attacks(limit))

@app.route('/api/devices')
def api_devices():
    return jsonify(get_all_devices())

@app.route('/api/export/csv')
def export_csv():
    """Export attacks to CSV without pandas"""
    conn = sqlite3.connect('iot_botnet.db')
    c = conn.cursor()
    
    # Get all attacks
    c.execute("SELECT * FROM attacks ORDER BY timestamp DESC")
    attacks = c.fetchall()
    
    # Get column names
    c.execute("PRAGMA table_info(attacks)")
    columns = [col[1] for col in c.fetchall()]
    conn.close()
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Write headers
    writer.writerow(columns)
    
    # Write data
    writer.writerows(attacks)
    
    output.seek(0)
    return send_file(
        BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'iot_attacks_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@app.route('/api/clear', methods=['POST'])
def clear_attacks():
    global total_attacks, attack_counter
    conn = sqlite3.connect('iot_botnet.db')
    c = conn.cursor()
    c.execute("DELETE FROM attacks")
    conn.commit()
    conn.close()
    total_attacks = 0
    attack_counter = 0
    socketio.emit('attacks_cleared')
    socketio.emit('geo_update', get_attack_geographic_origin())
    return jsonify({'success': True})

@app.route('/live_data')
def live_data():
    conn = sqlite3.connect('iot_botnet.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM attacks")
    attack_count = c.fetchone()[0] or 0
    conn.close()
    
    return jsonify({
        'traffic': 800 + (attack_count % 300),
        'status': 'ATTACK' if attack_count > 0 else 'SAFE',
        'attack': attack_count
    })

# ============ SOCKET.IO EVENTS ============
@socketio.on('connect')
def handle_connect():
    print(f"✅ Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    print(f"❌ Client disconnected")

# ============ START SERVER ============
if __name__ == '__main__':
    print("\n" + "="*60)
    print("🛡️ IoT BOTNET DETECTION SYSTEM")
    print("="*60)
    print("📍 URL: http://localhost:5000")
    print("🔑 Login: admin / admin123")
    print("="*60 + "\n")
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)