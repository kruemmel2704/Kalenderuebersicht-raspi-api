# Kalenderübersicht - Native Python GUI Client (PyQt5)

Dieser Client lädt die Kalender- und Spotify-Ansicht als native PyQt5-Desktopanwendung und bedient sich über eine API direkt am entfernten Flask-Server. Es wird **kein Webbrowser (Chromium)** und **kein Flask** auf dem Raspberry Pi benötigt. Dies spart extrem viel Arbeitsspeicher (RAM) und CPU-Leistung auf dem Pi.

## Voraussetzungen

* **Hardware**: Raspberry Pi mit angeschlossenem Bildschirm (HDMI, DSI, etc.).
* **Betriebssystem**: Raspberry Pi OS Lite (nur CLI).
* **Netzwerk**: SSH-Verbindung eingerichtet und Zugriff auf den laufenden Flask-Server.

## Installation

Verbinde dich per SSH mit deinem Raspberry Pi und installiere die Grafik-Bibliotheken, PyQt5 sowie die Python-Netzwerkmodule:

```bash
sudo apt update
sudo apt install -y xinit xserver-xorg python3-pyqt5 python3-requests python3-dotenv
```

*(Optional)* Falls du Berechtigungsprobleme beim Zugriff auf Eingabegeräte oder das Display hast, füge deinen Benutzer den entsprechenden Gruppen hinzu und starte den Pi neu:

```bash
sudo usermod -a -G video,input $USER
sudo reboot
```

## Konfiguration

1. Kopiere alle Dateien aus diesem Verzeichnis (inkl. dem `static/`-Ordner) auf deinen Raspberry Pi (z. B. nach `/opt/Kalenderuebersicht-raspi-api/`).
2. Passe die Datei `.env` an und trage den API-Endpoint deines Flask-Servers ein:

```env
API_ENDPOINT=https://<IP-DEINES-SERVERS>:5000
```

## Starten des Dashboards

### 1. Auf dem direkt angebundenen Bildschirm (CLI-only / Lite OS)
Wenn du per SSH verbunden bist und den X-Server direkt auf dem HDMI-Ausgang des Pi starten willst:

```bash
xinit python3 run.py -- -nocursor
```
*Das Skript öffnet sich automatisch im Vollbildmodus ohne Mauszeiger auf dem physikalischen Monitor.*

### 2. Auf einer laufenden XRDP-Desktop-Sitzung
Wenn du dich per Remote Desktop (XRDP) verbindest und die Anwendung dort im Fenster maximiert testen willst, führe folgenden Befehl aus (passe `:10.0` an deine tatsächliche RDP-Display-Nummer an):

```bash
DISPLAY=:10.0 python3 run.py --desktop
```

---

## Funktionsweise des Launchers (`run.py`)

1. **Konfiguration**: Lädt den API-Endpoint aus der `.env`-Datei.
2. **Hintergrund-Thread (`ApiWorker`)**: Fragt die API-Endpunkte (`/api/events` alle 10 Sek., `/api/spotify` alle 3 Sek.) im Hintergrund ab. Dadurch friert die Benutzeroberfläche bei Netzwerkschwankungen niemals ein.
3. **16:9 Seitenverhältnis-Garantie (`RatioWidget`)**: Die Anwendung erzwingt ein exaktes 16:9-Seitenverhältnis. Wenn dein Monitor ein anderes Format hat oder du das Fenster ziehst, zentriert sich das Dashboard automatisch und zeigt schwarze Balken an den Rändern (Letterbox/Pillarbox).
4. **Spotify-Steuerung**: Über die Buttons ⏮, ▶/⏸, ⏭ und das Playlist-Menü (☰) wird Spotify per API gesteuert. Der Lautstärkeregler passt die Spotify-Lautstärke in Echtzeit an.

## Beenden

Drücke `Ctrl + C` in deiner SSH-Session (oder schließe das Fenster in XRDP), um die Anwendung sauber zu beenden.
