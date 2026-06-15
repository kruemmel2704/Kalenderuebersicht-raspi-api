import os
import sys
import threading
import http.server
import socketserver
import subprocess

# 1. Safe helper to parse .env file (no external dependencies required)
def load_env(filepath=".env"):
    env_vars = {}
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split("=", 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    val = parts[1].strip()
                    # Strip surrounding quotes
                    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                        val = val[1:-1]
                    env_vars[key] = val
                    os.environ[key] = val
    return env_vars

# Load environment
env = load_env()

# Try python-dotenv as a fallback if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

api_endpoint = os.getenv("API_ENDPOINT")
if not api_endpoint:
    print("WARNING: API_ENDPOINT is not set in your .env file!")
    print("Creating default .env template...")
    with open(".env", "w", encoding="utf-8") as f:
        f.write("# Enter the HTTPS/HTTP URL of your Flask server here\n")
        f.write("API_ENDPOINT=https://localhost:5000\n")
    api_endpoint = "https://localhost:5000"
    print("Please edit the .env file with your actual API endpoint IP/Domain, and then restart.")

# Clean trailing slash from the endpoint
if api_endpoint.endswith("/"):
    api_endpoint = api_endpoint[:-1]

print(f"Starting calendar client targeting API: {api_endpoint}")

# 2. Write dynamic config.js file
config_content = f'window.API_ENDPOINT = "{api_endpoint}";\n'
os.makedirs("static", exist_ok=True)
with open("static/config.js", "w", encoding="utf-8") as f:
    f.write(config_content)
print("Updated static/config.js configuration.")

# 3. Define port and directory to serve
PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Override to silence excessive logging in headless environment
        super().__init__(*args, directory=DIRECTORY, **kwargs)
        
    def log_message(self, format, *args):
        # Only log issues, don't spam terminal with 200 GET requests
        if args[1] != '200':
            super().log_message(format, *args)

# 4. Start local HTTP server in a background thread
def serve_forever():
    socketserver.TCPServer.allow_reuse_address = True
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"Serving local client files at http://localhost:{PORT}")
            httpd.serve_forever()
    except Exception as e:
        print(f"Error starting local HTTP server: {e}")
        sys.exit(1)

server_thread = threading.Thread(target=serve_forever, daemon=True)
server_thread.start()

# 5. Start chromium-browser via xinit
# Let's locate the chromium binary
chrome_bin = "/usr/bin/chromium-browser"
if not os.path.exists(chrome_bin):
    chrome_bin = "/usr/bin/chromium"
    if not os.path.exists(chrome_bin):
        chrome_bin = "chromium-browser" # Fallback to path lookup

# Common Chromium flags optimized for Raspberry Pi Lite Kiosk displays
kiosk_command = [
    "xinit",
    chrome_bin,
    "--kiosk",
    "--noerrdialogs",
    "--disable-infobars",
    "--no-sandbox",
    "--ignore-certificate-errors",
    "--allow-running-insecure-content",
    "--disable-session-crashed-bubble",
    "--disable-translate",
    "--disable-features=Translate",
    "--check-for-update-interval=31536000",
    "--user-data-dir=/tmp/chromium_kiosk",
    f"http://localhost:{PORT}/",
    "--",
    "-nocursor"
]

print(f"Launching screen view command: {' '.join(kiosk_command)}")
try:
    subprocess.run(kiosk_command, check=True)
except FileNotFoundError:
    print("\n[ERROR] xinit or chromium-browser not found.")
    print("Please install display requirements on your Raspberry Pi Lite:")
    print("  sudo apt update")
    print("  sudo apt install -y xinit xserver-xorg chromium-browser")
except subprocess.CalledProcessError as e:
    print(f"\n[ERROR] X server / browser execution exited with error code: {e.returncode}")
    print("If you are running this over SSH, make sure you have permissions (e.g. are in 'video' and 'input' groups) or try run as root.")
