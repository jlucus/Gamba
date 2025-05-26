#!/usr/bin/env python3
"""
Simple HTTP server launcher for the Crypto Tips Portfolio Analyzer.
This script starts a local web server to serve the portfolio analysis dashboard.
"""

import http.server
import socketserver
import webbrowser
import os
import sys
import time
from threading import Timer

def open_browser():
    """Open the dashboard in the default browser after a short delay."""
    print("🌐 Opening dashboard in your browser...")
    webbrowser.open('http://localhost:8000/dashboard_launcher.html')

def start_server(port=8000):
    """Start the HTTP server on the specified port."""
    try:
        # Change to the script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        
        # Create server
        handler = http.server.SimpleHTTPRequestHandler
        httpd = socketserver.TCPServer(("", port), handler)
        
        print("🚀 Starting Crypto Tips Portfolio Analyzer Server...")
        print(f"📊 Server running at: http://localhost:{port}")
        print(f"📁 Serving files from: {script_dir}")
        print("\n🎯 Available Pages:")
        print(f"   • Dashboard: http://localhost:{port}/dashboard_launcher.html")
        print(f"   • Advanced Viewer: http://localhost:{port}/advanced_tips_viewer.html")
        print(f"   • Transaction Browser: http://localhost:{port}/tips_viewer.html")
        print(f"   • Portfolio Report: http://localhost:{port}/portfolio_summary_report.md")
        print("\n💡 Press Ctrl+C to stop the server")
        
        # Open browser after 2 seconds
        Timer(2.0, open_browser).start()
        
        # Start serving
        httpd.serve_forever()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        httpd.shutdown()
        sys.exit(0)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {port} is already in use!")
            print(f"💡 Try a different port: python start_server.py --port 8001")
            print(f"🔍 Or check if server is already running at: http://localhost:{port}")
        else:
            print(f"❌ Error starting server: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

def main():
    """Main function with command line argument parsing."""
    port = 8000
    
    # Simple argument parsing
    if len(sys.argv) > 1:
        for i, arg in enumerate(sys.argv):
            if arg == "--port" and i + 1 < len(sys.argv):
                try:
                    port = int(sys.argv[i + 1])
                except ValueError:
                    print("❌ Invalid port number")
                    sys.exit(1)
            elif arg == "--help" or arg == "-h":
                print("🎯 Crypto Tips Portfolio Analyzer Server")
                print("\nUsage:")
                print("  python start_server.py [--port PORT]")
                print("\nOptions:")
                print("  --port PORT    Port number (default: 8000)")
                print("  --help, -h     Show this help message")
                print("\nExamples:")
                print("  python start_server.py")
                print("  python start_server.py --port 8080")
                sys.exit(0)
    
    start_server(port)

if __name__ == "__main__":
    main()
