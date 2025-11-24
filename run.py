#!/usr/bin/env python3
"""
HTTP Proxy Server Launcher
Starts both the web interface and proxy server
"""

from web_interface import run_web_interface
import sys

def print_banner():
    """Print startup banner"""
    banner = """
    HTTP WEB PROXY SERVER WITH FILTERING 
    """
    print(banner)
    print(" Web Interface: http://localhost:5000")
    print(" Proxy Server: localhost:8080")
    print("\n" + "="*50)
    print(" SETUP INSTRUCTIONS:")
    print("="*50)
    print("1. Open browser → http://localhost:5000")
    print("2. Click 'Start Server' button")
    print("3. Configure browser proxy settings:")
    print("   • HTTP Proxy: localhost")
    print("   • Port: 8080")
    print("4. Add websites to block list")
    print("5. Start browsing!")
    print("\n Press Ctrl+C to stop\n")

def main():
    """Main entry point"""
    try:
        print_banner()
        run_web_interface()
    except KeyboardInterrupt:
        print("\n\n Shutting down proxy server...")
        print(" Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()