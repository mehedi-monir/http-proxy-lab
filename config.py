# Proxy Server Configuration

# Server settings
PROXY_HOST = 'localhost'
PROXY_PORT = 8080
WEB_INTERFACE_HOST = 'localhost'
WEB_INTERFACE_PORT = 5000

# Cache settings
CACHE_ENABLED = True
CACHE_DURATION = 300  # 5 minutes in seconds
MAX_CACHE_SIZE = 100  # Maximum number of cached items

# Security settings
MAX_REQUEST_SIZE = 8192  # 8KB
CONNECTION_TIMEOUT = 30  # seconds

# Logging settings
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# Database settings
DATABASE_FILE = 'proxy_server.db'

# Default blocked sites (can be empty initially)
DEFAULT_BLOCKED_SITES = []