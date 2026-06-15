# Kalenderübersicht - Raspberry Pi Client (Lite OS / CLI)

Dieser Client lädt die Kalender- und Spotify-Ansicht lokal im Kiosk-Modus und bedient sich über eine API direkt am entfernten Flask-Server. Es wird **kein Flask** auf dem Raspberry Pi benötigt.

## Voraussetzungen

* **Hardware**: Raspberry Pi mit angeschlossenem Bildschirm (HDMI, DSI, etc.).
* **Betriebssystem**: Raspberry Pi OS Lite (nur CLI).
* **Netzwerk**: SSH-Verbindung eingerichtet und Zugriff auf den laufenden Flask-Server.

## Installation

Verbinde dich per SSH mit deinem Raspberry Pi und installiere die benötigten Grafik- und Browser-Pakete (für den X-Server und Chromium):

```bash
sudo apt update
sudo apt install -y xinit xserver-xorg chromium-browser
```

*(Optional)* Falls du Berechtigungsprobleme beim Zugriff auf Eingabegeräte oder das Display hast, füge deinen Benutzer den entsprechenden Gruppen hinzu und starte den Pi neu:

```bash
sudo usermod -a -G video,input $USER
sudo reboot
```

## Konfiguration

1. Kopiere alle Dateien aus diesem Verzeichnis auf deinen Raspberry Pi.
2. Passe die Datei `.env` an und trage den API-Endpoint deines Flask-Servers ein:

```env
API_ENDPOINT=https://<IP-DEINES-SERVERS>:5000
```

*Hinweis: Da der Flask-Server standardmäßig selbstsignierte SSL-Zertifikate verwendet, ignoriert Chromium beim Start automatisch Zertifikatsfehler (`--ignore-certificate-errors`), sodass der Datenabruf reibungslos funktioniert.*

## Starten des Dashboards

Starte das Dashboard direkt über deine SSH-Konsole:

```bash
python3 run.py
```

### Funktionsweise des Launchers (`run.py`):
1. Liest die `.env` Datei aus.
2. Erstellt dynamisch eine JavaScript-Konfiguration (`static/config.js`), die den API-Endpoint für die AJAX-Abrufe definiert.
3. Startet einen extrem leichtgewichtigen, in Python integrierten Webserver auf Port `8000` im Hintergrund, um die lokalen HTML/JS/CSS-Dateien auszuliefern.
4. Startet per `xinit` den X-Server direkt auf dem angeschlossenen Bildschirm und lädt Chromium im Vollbild-Kioskmodus (`--kiosk`) mit ausgeblendetem Mauszeiger.
5. Das Dashboard holt sich alle Termine und steuert Spotify über die API des angegebenen Flask-Servers.

## Beenden

Drücke einfach `Ctrl + C` in deiner SSH-Session, um Chromium und den lokalen Server sauber zu beenden.
