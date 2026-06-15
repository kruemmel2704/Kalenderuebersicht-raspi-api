import time
import requests
import threading

# PyQt5 imports
from PyQt5.QtCore import QThread, pyqtSignal

# 2. Worker Thread for Asynchronous API Fetching
class ApiWorker(QThread):
    events_ready = pyqtSignal(dict)
    spotify_ready = pyqtSignal(dict)
    connection_error = pyqtSignal(str)

    def __init__(self, endpoint):
        super().__init__()
        self.endpoint = endpoint
        self.running = True

    def run(self):
        last_event_fetch = 0
        last_spotify_fetch = 0

        while self.running:
            now = time.time()
            # Fetch events every 10 seconds
            if now - last_event_fetch >= 10:
                try:
                    r = requests.get(f"{self.endpoint}/api/events", timeout=5, verify=False)
                    if r.status_code == 200:
                        self.events_ready.emit(r.json())
                        last_event_fetch = now
                except Exception as e:
                    self.connection_error.emit(f"Events Fehler: {str(e)}")

            # Fetch Spotify every 3 seconds
            if now - last_spotify_fetch >= 3:
                try:
                    r = requests.get(f"{self.endpoint}/api/spotify", timeout=3, verify=False)
                    if r.status_code == 200:
                        self.spotify_ready.emit(r.json())
                        last_spotify_fetch = now
                except Exception as e:
                    # Ignore Spotify disconnects during transient states, just log
                    pass

            time.sleep(1)

# Helper function to run POST requests in background
def fire_and_forget(url, json_data=None):
    def worker():
        try:
            if json_data:
                requests.post(url, json=json_data, timeout=3, verify=False)
            else:
                requests.post(url, timeout=3, verify=False)
        except Exception as e:
            print(f"Async POST error to {url}: {e}")
    threading.Thread(target=worker, daemon=True).start()
