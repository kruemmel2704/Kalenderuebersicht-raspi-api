import sys
from PyQt5.QtWidgets import QApplication
from app.ui import MainWindow
from app.config import api_endpoint

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Check flags for desktop/xrdp mode
    is_desktop = "--desktop" in sys.argv or "--xrdp" in sys.argv
    
    # Target server endpoint
    print(f"Launching native GUI client targeting API: {api_endpoint}")
    window = MainWindow(api_endpoint, is_desktop=is_desktop)
    
    if is_desktop:
        window.showMaximized()
    else:
        window.showFullScreen()
        
    sys.exit(app.exec_())
