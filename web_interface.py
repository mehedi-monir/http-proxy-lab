from flask import Flask, render_template, request, jsonify
import threading
import time
from proxy_server import proxy_server_instance

app = Flask(__name__)
server_thread = None

@app.route('/')
def index():
    stats = proxy_server_instance.get_stats()
    blocked_sites = sorted(list(proxy_server_instance.blocked_sites))
    return render_template('index.html', 
                         stats=stats, 
                         blocked_sites=blocked_sites,
                         server_running=proxy_server_instance.is_running)

@app.route('/logs')
def logs():
    cursor = proxy_server_instance.conn.cursor()
    cursor.execute('''
        SELECT client_ip, url, method, status_code, blocked, timestamp 
        FROM access_logs 
        ORDER BY timestamp DESC 
        LIMIT 200
    ''')
    logs_data = cursor.fetchall()
    return render_template('logs.html', logs=logs_data)

@app.route('/api/start', methods=['POST'])
def start_server():
    global server_thread
    if not proxy_server_instance.is_running:
        server_thread = threading.Thread(target=proxy_server_instance.start_server)
        server_thread.daemon = True
        server_thread.start()
        time.sleep(1)
        return jsonify({'status': 'success', 'message': 'Proxy server started on port 8080'})
    return jsonify({'status': 'error', 'message': 'Server already running'})

@app.route('/api/stop', methods=['POST'])
def stop_server():
    if proxy_server_instance.is_running:
        proxy_server_instance.stop_server()
        return jsonify({'status': 'success', 'message': 'Proxy server stopped'})
    return jsonify({'status': 'error', 'message': 'Server not running'})

@app.route('/api/block-site', methods=['POST'])
def block_site():
    data = request.get_json()
    pattern = data.get('pattern', '').strip()
    
    if not pattern:
        return jsonify({'status': 'error', 'message': 'Please enter a website URL'})
    
    if proxy_server_instance.add_blocked_site(pattern):
        return jsonify({'status': 'success', 'message': f'Blocked: {pattern}'})
    else:
        return jsonify({'status': 'error', 'message': f'Already blocked: {pattern}'})

@app.route('/api/unblock-site', methods=['POST'])
def unblock_site():
    data = request.get_json()
    pattern = data.get('pattern', '').strip()
    
    if proxy_server_instance.remove_blocked_site(pattern):
        return jsonify({'status': 'success', 'message': f'Unblocked: {pattern}'})
    else:
        return jsonify({'status': 'error', 'message': f'Not found: {pattern}'})

@app.route('/api/stats')
def get_stats():
    stats = proxy_server_instance.get_stats()
    stats['server_running'] = proxy_server_instance.is_running
    stats['blocked_sites'] = sorted(list(proxy_server_instance.blocked_sites))
    return jsonify(stats)

@app.route('/api/clear-cache', methods=['POST'])
def clear_cache():
    cursor = proxy_server_instance.conn.cursor()
    cursor.execute("DELETE FROM cache")
    proxy_server_instance.conn.commit()
    return jsonify({'status': 'success', 'message': 'Cache cleared successfully'})

@app.route('/api/clear-logs', methods=['POST'])
def clear_logs():
    cursor = proxy_server_instance.conn.cursor()
    cursor.execute("DELETE FROM access_logs")
    proxy_server_instance.conn.commit()
    return jsonify({'status': 'success', 'message': 'Logs cleared successfully'})

@app.route('/api/quick-block', methods=['POST'])
def quick_block():
    """Quick block popular websites"""
    data = request.get_json()
    site = data.get('site', '')
    
    site_mappings = {
        'youtube': 'youtube.com',
        'facebook': 'facebook.com',
        'twitter': 'twitter.com',
        'instagram': 'instagram.com'
    }
    
    if site in site_mappings:
        pattern = site_mappings[site]
        if proxy_server_instance.add_blocked_site(pattern):
            return jsonify({'status': 'success', 'message': f'Blocked {site.title()}'})
        return jsonify({'status': 'error', 'message': f'{site.title()} already blocked'})
    
    return jsonify({'status': 'error', 'message': 'Invalid site'})

def run_web_interface():
    """Start the web interface"""
    print(" Web interface: http://localhost:5000")
    app.run(host='localhost', port=5000, debug=False, use_reloader=False)

if __name__ == '__main__':
    run_web_interface()