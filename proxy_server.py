import socket
import threading
import re
import sqlite3
import select
from datetime import datetime
from urllib.parse import urlparse

class HTTPProxyServer:
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.blocked_sites = set()
        self.is_running = False
        self.server_socket = None
        self.conn = None
        
        self.init_database()
        self.load_blocked_sites()
        print(f" Proxy Server Initialized on {host}:{port}")
        
    def init_database(self):
        """Initialize SQLite database for persistent storage"""
        self.conn = sqlite3.connect('proxy_server.db', check_same_thread=False)
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blocked_sites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url_pattern TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS access_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_ip TEXT,
                url TEXT,
                method TEXT,
                status_code INTEGER,
                blocked INTEGER DEFAULT 0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cache (
                url TEXT PRIMARY KEY,
                content BLOB,
                content_type TEXT,
                expires TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    def load_blocked_sites(self):
        """Load blocked sites from database"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT url_pattern FROM blocked_sites")
        results = cursor.fetchall()
        self.blocked_sites = {row[0] for row in results}
        print(f" Loaded {len(self.blocked_sites)} blocked sites")
    
    def normalize_domain(self, host):
        """Normalize domain for comparison"""
        if not host:
            return ""
        # Remove www. prefix
        host = host.lower().strip()
        if host.startswith('www.'):
            host = host[4:]
        return host
    
    def is_blocked(self, host):
        """Check if host is blocked - FIXED VERSION"""
        if not host:
            return False
        
        normalized_host = self.normalize_domain(host)
        print(f"🔍 Checking: {normalized_host}")
        
        # Define YouTube-related domains
        youtube_domains = {
            'youtube.com',
            'youtu.be',
            'ytimg.com',
            'googlevideo.com',
            'ggpht.com',
            'youtube-nocookie.com',
            'youtubei.googleapis.com'
        }
        
        for pattern in self.blocked_sites:
            normalized_pattern = self.normalize_domain(pattern)
            
            # Check if pattern is for YouTube
            if 'youtube' in normalized_pattern:
                # Block all YouTube-related domains
                for yt_domain in youtube_domains:
                    if yt_domain in normalized_host or normalized_host.endswith('.' + yt_domain):
                        print(f" BLOCKED: {host} (YouTube-related)")
                        return True
            
            # Exact domain match
            if normalized_host == normalized_pattern:
                print(f"🚫 BLOCKED: {host} (exact match)")
                return True
            
            # Subdomain match (e.g., pattern "example.com" blocks "www.example.com")
            if normalized_host.endswith('.' + normalized_pattern):
                print(f"🚫 BLOCKED: {host} (subdomain match)")
                return True
            
            # Regex pattern match
            try:
                if re.search(normalized_pattern, normalized_host, re.IGNORECASE):
                    print(f"🚫 BLOCKED: {host} (regex match)")
                    return True
            except re.error:
                pass
        
        print(f"✅ ALLOWED: {host}")
        return False
    
    def add_blocked_site(self, pattern):
        """Add a site to block list"""
        pattern = pattern.strip().lower()
        
        # Remove protocol
        if '://' in pattern:
            pattern = pattern.split('://', 1)[1]
        
        # Remove path
        if '/' in pattern:
            pattern = pattern.split('/')[0]
        
        # Remove www.
        if pattern.startswith('www.'):
            pattern = pattern[4:]
        
        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO blocked_sites (url_pattern) VALUES (?)", (pattern,))
            self.conn.commit()
            self.blocked_sites.add(pattern)
            print(f" Blocked: {pattern}")
            return True
        except sqlite3.IntegrityError:
            print(f" Already blocked: {pattern}")
            return False
    
    def remove_blocked_site(self, pattern):
        """Remove a site from block list"""
        pattern = pattern.strip().lower()
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM blocked_sites WHERE url_pattern = ?", (pattern,))
        self.conn.commit()
        if cursor.rowcount > 0:
            self.blocked_sites.discard(pattern)
            print(f" Unblocked: {pattern}")
            return True
        return False
    
    def log_access(self, client_ip, url, method, status_code, blocked=0):
        """Log access attempt"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO access_logs (client_ip, url, method, status_code, blocked)
            VALUES (?, ?, ?, ?, ?)
        ''', (client_ip, url, method, status_code, blocked))
        self.conn.commit()

    def handle_https_request(self, client_socket, host, port):
        """Handle HTTPS CONNECT requests"""
        try:
            # Check if blocked
            if self.is_blocked(host):
                response = "HTTP/1.1 403 Forbidden\r\n\r\n🚫 This website is blocked by the proxy server."
                client_socket.send(response.encode())
                self.log_access("localhost", f"https://{host}", "CONNECT", 403, 1)
                return
            
            # Send connection established
            client_socket.send(b"HTTP/1.1 200 Connection Established\r\n\r\n")
            
            # Connect to target
            target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_socket.settimeout(10)
            target_socket.connect((host, port))
            
            self.log_access("localhost", f"https://{host}", "CONNECT", 200, 0)
            
            # Tunnel data
            self.tunnel_data(client_socket, target_socket)
            
        except Exception as e:
            print(f"HTTPS Error: {e}")
        finally:
            try:
                client_socket.close()
            except:
                pass

    def tunnel_data(self, client_socket, target_socket):
        """Tunnel data between client and target"""
        sockets = [client_socket, target_socket]
        
        while True:
            try:
                read_sockets, _, _ = select.select(sockets, [], [], 5)
                
                if not read_sockets:
                    break
                
                for sock in read_sockets:
                    try:
                        data = sock.recv(8192)
                        if not data:
                            return
                        
                        if sock is client_socket:
                            target_socket.send(data)
                        else:
                            client_socket.send(data)
                    except:
                        return
                        
            except Exception:
                break
    
    def handle_client(self, client_socket, client_address):
        """Handle client connection"""
        try:
            request = client_socket.recv(8192).decode('utf-8', errors='ignore')
            
            if not request:
                return
            
            first_line = request.split('\n')[0]
            parts = first_line.split()
            if len(parts) < 2:
                return

            method = parts[0]
            
            # Handle HTTPS CONNECT
            if method.upper() == 'CONNECT':
                host_port = parts[1].split(':')
                host = host_port[0]
                port = int(host_port[1]) if len(host_port) > 1 else 443
                self.handle_https_request(client_socket, host, port)
                return
            
            # Handle HTTP
            if len(parts) < 3:
                return
                
            url = parts[1]
            if '://' not in url:
                url = 'http://' + url
                
            parsed_url = urlparse(url)
            host = parsed_url.hostname
            
            # Check if blocked
            if self.is_blocked(host):
                response = "HTTP/1.1 403 Forbidden\r\n\r\n🚫 This website is blocked."
                client_socket.send(response.encode())
                self.log_access(client_address[0], url, method, 403, 1)
                return
            
            # Forward request
            port = parsed_url.port or 80
            target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_socket.settimeout(10)
            target_socket.connect((host, port))
            target_socket.send(request.encode())
            
            response = b""
            while True:
                data = target_socket.recv(8192)
                if not data:
                    break
                response += data
            
            client_socket.send(response)
            self.log_access(client_address[0], url, method, 200, 0)
            target_socket.close()
                
        except Exception as e:
            print(f"Error: {e}")
        finally:
            try:
                client_socket.close()
            except:
                pass
    
    def start_server(self):
        """Start the proxy server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.is_running = True
            
            print(f"✅ Proxy server running on {self.host}:{self.port}")
            
            while self.is_running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address),
                        daemon=True
                    )
                    client_thread.start()
                except socket.error:
                    break
                    
        except Exception as e:
            print(f"Server error: {e}")
            self.is_running = False
    
    def stop_server(self):
        """Stop the proxy server"""
        self.is_running = False
        if self.server_socket:
            self.server_socket.close()
        print("🛑 Proxy server stopped")
    
    def get_stats(self):
        """Get server statistics"""
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM access_logs")
        total_requests = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM access_logs WHERE blocked = 1")
        blocked_requests = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM cache WHERE expires > datetime('now')")
        cached_items = cursor.fetchone()[0]
        
        return {
            'total_requests': total_requests,
            'blocked_requests': blocked_requests,
            'cached_items': cached_items,
            'blocked_sites_count': len(self.blocked_sites)
        }

# Global instance
proxy_server_instance = HTTPProxyServer()