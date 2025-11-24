# HTTP Web Proxy Server with Website Filtering

A full-featured HTTP/HTTPS proxy server with web-based management interface, website blocking capabilities, caching, and comprehensive logging.

## 🌟 Features

- ✅ **HTTP & HTTPS Support** - Full support for both protocols
- 🚫 **Website Blocking** - Block any website with pattern matching
- 💾 **Caching System** - Cache responses to improve performance
- 📊 **Real-time Statistics** - Monitor requests, blocks, and cache hits
- 📋 **Access Logging** - Detailed logs of all proxy activity
- 🎨 **Modern Web UI** - Beautiful, responsive dashboard
- ⚡ **Quick Actions** - One-click blocking for popular sites
- 🔄 **Auto-refresh** - Live statistics updates

## 📋 Requirements

- Python 3.7+
- Flask 2.3.0+
- SQLite3 (included with Python)

## 🚀 Installation

### 1. Clone or Download the Project
```bash
git clone <your-repo-url>
cd proxy-server
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

or install manually:
```bash
pip install Flask==2.3.0
```

### 3. Run the Server
```bash
python run.py
```

## 📖 How to Use

### Step 1: Start the Web Interface

Run the server:
```bash
python run.py
```

Open your browser and go to:
```
http://localhost:5000
```

### Step 2: Start the Proxy Server

Click the **"Start Server"** button in the web interface. The proxy will start on port 8080.

### Step 3: Configure Your Browser

#### Firefox:
1. Open **Settings** → **Network Settings**
2. Select **Manual proxy configuration**
3. Enter:
   - HTTP Proxy: `localhost`
   - Port: `8080`
4. Check **"Also use this proxy for HTTPS"**
5. Click **OK**

#### Chrome:
1. Open **Settings** → **System** → **Open proxy settings**
2. Click **LAN Settings**
3. Check **"Use a proxy server"**
4. Enter:
   - Address: `localhost`
   - Port: `8080`
5. Click **OK**

### Step 4: Block Websites

#### Quick Block (Popular Sites):
- Click on **Quick Action** buttons:
  - YouTube
  - Facebook
  - Twitter
  - Instagram

#### Custom Block:
1. Enter website URL in the input field (e.g., `reddit.com`)
2. Click **"Block Site"**

### Step 5: Browse the Internet

All your traffic will now go through the proxy. Blocked sites will show a "403 Forbidden" message.

## 🎯 Features Explained

### Website Blocking
- Supports domain blocking (e.g., `youtube.com`)
- Automatically blocks subdomains (e.g., `m.youtube.com`, `www.youtube.com`)
- Special YouTube blocking includes all related domains (`ytimg.com`, `googlevideo.com`, etc.)

### Statistics Dashboard
- **Total Requests**: All requests through the proxy
- **Blocked Requests**: Requests to blocked websites
- **Cached Items**: Number of responses in cache
- **Blocked Sites**: Total number of blocked patterns

### Access Logs
- View all proxy activity
- See which sites were accessed
- Filter blocked vs. allowed requests
- Timestamps for all activity

### Cache System
- Automatically caches HTTP responses
- 5-minute cache duration
- Improves loading speed for repeated visits
- Can be cleared from dashboard

## 📁 Project Structure
```
proxy-server/
├── run.py                 # Main launcher
├── proxy_server.py        # Proxy server core logic
├── web_interface.py       # Flask web application
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── proxy_server.db        # SQLite database (auto-created)
├── templates/
│   ├── index.html        # Main dashboard
│   └── logs.html         # Logs viewer
└── static/
    ├── style.css         # Styling
    └── script.js         # Frontend JavaScript
```

## 🔧 Configuration

Edit `config.py` to customize:
```python
PROXY_PORT = 8080              # Proxy server port
WEB_INTERFACE_PORT = 5000      # Web UI port
CACHE_DURATION = 300           # Cache duration (seconds)
CONNECTION_TIMEOUT = 30        # Connection timeout
```

## 🐛 Troubleshooting

### Port Already in Use
If port 8080 or 5000 is already in use:
1. Stop the conflicting application
2. Or change ports in `config.py`

### YouTube Still Works
Make sure:
1. Proxy is running (check dashboard status)
2. Browser is configured correctly
3. You've added `youtube.com` to block list
4. Try restarting the browser

### Browser Can't Connect
1. Check proxy server status in dashboard
2. Verify proxy settings in browser:
   - HTTP Proxy: `localhost`
   - Port: `8080`
3. Try restarting the proxy server

### Sites Load Slowly
1. Clear the cache from dashboard
2. Check your internet connection
3. Some HTTPS sites may be slower due to tunneling

## 💡 Tips

1. **Use Quick Block buttons** for popular sites
2. **Monitor logs** to see what's being blocked
3. **Clear cache** if experiencing issues
4. **Check statistics** to track proxy usage
5. **Restart browser** after changing proxy settings

## 🔒 Security Notes

- This proxy does NOT provide anonymity
- HTTPS traffic is tunneled but not inspected
- Logs store all accessed URLs
- Suitable for local use and testing
- Not recommended for production without additional security

## 📝 Database Schema

The project uses SQLite with three tables:

1. **blocked_sites**: Stores blocked URL patterns
2. **access_logs**: Logs all proxy requests
3. **cache**: Stores cached responses

## 🎓 Educational Purpose

This project is designed for:
- Learning about HTTP/HTTPS protocols
- Understanding proxy servers
- Web development with Flask
- Network programming in Python
- Database integration

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section
2. Review logs in the web interface
3. Check console output for errors

## 📄 License

This project is for educational purposes. Feel free to modify and use as needed.

## ✅ Checklist for Submission

- [ ] All code files present
- [ ] Dependencies installed (`requirements.txt`)
- [ ] Server starts without errors
- [ ] Web interface accessible
- [ ] Proxy blocks websites correctly
- [ ] Logs are being recorded
- [ ] README.md is complete
- [ ] Screenshots/demo ready

---

**Created for Computer Networks Lab - HTTP Web Proxy Server Project**

*Presentation Date: [Your Date]*
*Student: [Your Name]*
*Course: [Your Course]*