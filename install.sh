#!/bin/bash

# Configuration
REPO="kruemmel2704/Kalenderuebersicht-raspi-api"
VERSION="v1.0.0"
ZIP_FILE="CalendarDashboard-linux-arm64.zip"
URL="https://github.com/$REPO/releases/download/$VERSION/$ZIP_FILE"
INSTALL_DIR="$HOME/calendar_dashboard"

echo "=== Calendar Dashboard Installer ==="
echo "Zielverzeichnis: $INSTALL_DIR"
echo "Version: $VERSION"
echo ""

# 1. Install required system dependencies for .NET, Avalonia, SkiaSharp and extracting
echo "Installiere erforderliche Systembibliotheken für .NET und Avalonia/Skia..."
sudo apt-get update && sudo apt-get install -y \
    unzip \
    libfontconfig1 \
    libfreetype6 \
    libicu-dev \
    libssl-dev \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxext6 \
    libxi6

# 2. Create installation directory
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR" || exit 1

# 3. Download the release ZIP archive
echo "Lade Release-Paket herunter..."
if command -v curl &> /dev/null; then
    curl -L "$URL" -o "$ZIP_FILE"
elif command -v wget &> /dev/null; then
    wget "$URL" -O "$ZIP_FILE"
else
    echo "Fehler: Weder curl noch wget sind installiert. Bitte installiere eins davon."
    exit 1
fi

# Check if download succeeded
if [ ! -f "$ZIP_FILE" ] || [ ! -s "$ZIP_FILE" ]; then
    echo "Fehler beim Herunterladen des Release-Archivs."
    echo "Bitte vergewissere dich, dass der Release v1.0.0 auf GitHub veröffentlicht wurde und die Datei $ZIP_FILE hochgeladen ist."
    exit 1
fi

# 4. Extract package
echo "Entpacke Paket..."
unzip -o "$ZIP_FILE"
rm "$ZIP_FILE"

# 5. Make executable
chmod +x CalendarDashboard
echo "Installation abgeschlossen!"
echo ""

# 6. Ask for test run in XRDP
read -p "Möchtest du das Programm testweise über XRDP starten? (y/n): " run_xrdp

if [[ "$run_xrdp" =~ ^[Yy]$ ]]; then
    # Detect current DISPLAY
    DETECTED_DISPLAY=$DISPLAY
    if [ -z "$DETECTED_DISPLAY" ]; then
        # Default fallback for XRDP sessions
        DETECTED_DISPLAY=":10.0"
    fi
    
    read -p "Welche Display-Nummer soll verwendet werden? (Standard: $DETECTED_DISPLAY): " input_display
    DISPLAY_NUM=${input_display:-$DETECTED_DISPLAY}
    
    echo "Starte Dashboard auf Display $DISPLAY_NUM..."
    echo "Drücke STRG+C im Terminal, um das Programm zu beenden."
    
    # Run application
    DISPLAY="$DISPLAY_NUM" ./CalendarDashboard
else
    echo "Installation abgeschlossen. Du kannst das Dashboard manuell im Installationsordner starten:"
    echo "cd $INSTALL_DIR && ./CalendarDashboard"
fi
