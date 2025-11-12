"""
Startup script for Project RawHorse
Handles server startup and browser launching
"""
import os
import sys
import socket
import webbrowser
import time
import threading
import subprocess
from pathlib import Path


def find_free_port(start_port=8000, end_port=8100):
    """Find an available port in the specified range"""
    for port in range(start_port, end_port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    raise RuntimeError("No free ports available in range")


def wait_for_server(host, port, timeout=30):
    """Wait for server to be ready"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, port))
                return True
        except (socket.error, ConnectionRefusedError):
            time.sleep(0.5)
    return False


def open_browser(url):
    """Open browser after a short delay"""
    time.sleep(2)
    webbrowser.open(url)


def main():
    """Main startup function"""
    print("=" * 60)
    print("Project RawHorse")
    print("Starting application...")
    print("=" * 60)
    
    # Get the directory where the executable is located
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        app_dir = Path(sys._MEIPASS)
        data_dir = Path(sys.executable).parent / "data"
    else:
        # Running as script
        app_dir = Path(__file__).parent
        data_dir = app_dir / "data"
    
    # Ensure data directory exists
    data_dir.mkdir(exist_ok=True)
    
    # Find free port
    port = find_free_port()
    host = '127.0.0.1'
    url = f"http://{host}:{port}"
    
    print(f"\nServer will start on: {url}")
    print(f"Data directory: {data_dir}")
    
    # Start browser opener in background
    browser_thread = threading.Thread(target=open_browser, args=(url,))
    browser_thread.daemon = True
    browser_thread.start()
    
    # Change to backend directory
    backend_dir = app_dir / "backend"
    os.chdir(backend_dir)
    
    # Set environment variables
    os.environ['UAP_DATA_DIR'] = str(data_dir)
    os.environ['UAP_PORT'] = str(port)
    
    print("\nInitializing database and loading data...")
    print("This may take a few moments on first run...")
    print("\nPress Ctrl+C to stop the server\n")
    
    # Start uvicorn server
    import uvicorn
    from main import app
    
    try:
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            access_log=False
        )
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        print("Thank you for using Project RawHorse!")
    except Exception as e:
        print(f"\n\nError starting server: {e}")
        print("\nPress Enter to exit...")
        input()
        sys.exit(1)


if __name__ == "__main__":
    main()
