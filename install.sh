#!/bin/bash

# Configuration
REPO="kruemmel2704/Kalenderuebersicht-raspi-api"
VERSION="v1.0.0"
ZIP_FILE="CalendarDashboard-linux-arm64.zip"
URL="https://github.com/$REPO/releases/download/$VERSION/$ZIP_FILE"
INSTALL_DIR="$HOME/calendar_dashboard"
ORIG_DIR=$(pwd)

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

# 3. Download the release ZIP archive
echo "Lade Release-Paket herunter..."
DOWNLOAD_SUCCESS=false

if command -v curl &> /dev/null; then
    curl -L "$URL" -o "$ZIP_FILE"
elif command -v wget &> /dev/null; then
    wget "$URL" -O "$ZIP_FILE"
fi

# Verify if it is a valid zip file
if [ -f "$ZIP_FILE" ] && unzip -t "$ZIP_FILE" &> /dev/null; then
    DOWNLOAD_SUCCESS=true
fi

if [ "$DOWNLOAD_SUCCESS" = true ]; then
    echo "Entpacke Paket..."
    cd "$INSTALL_DIR" || exit 1
    unzip -o "$ORIG_DIR/$ZIP_FILE"
    rm "$ORIG_DIR/$ZIP_FILE"
else
    echo ""
    echo "HINWEIS: Das vorkompilierte Release-Paket v1.0.0 wurde auf GitHub nicht gefunden"
    echo "(evtl. wurde das Release v1.0.0 auf GitHub noch nicht veröffentlicht)."
    echo "Kompiliere das Projekt stattdessen lokal aus dem Quellcode..."
    echo ""
    
    if [ -f "$ORIG_DIR/CalendarDashboard.csproj" ]; then
        echo "Kompiliere das lokale Projekt..."
        dotnet publish "$ORIG_DIR/CalendarDashboard.csproj" -c Release --self-contained true -p:PublishSingleFile=true -o "$INSTALL_DIR"
    else
        echo "Klone das Repository von GitHub..."
        TEMP_CLONE_DIR=$(mktemp -d)
        git clone "https://github.com/$REPO.git" "$TEMP_CLONE_DIR"
        if [ -d "$TEMP_CLONE_DIR" ] && [ -f "$TEMP_CLONE_DIR/CalendarDashboard.csproj" ]; then
            echo "Kompiliere das geklonte Projekt..."
            dotnet publish "$TEMP_CLONE_DIR/CalendarDashboard.csproj" -c Release --self-contained true -p:PublishSingleFile=true -o "$INSTALL_DIR"
            rm -rf "$TEMP_CLONE_DIR"
        else
            echo "Fehler: Das Repository konnte nicht geklont werden oder enthält kein C#-Projekt."
            [ -f "$ZIP_FILE" ] && rm "$ZIP_FILE"
            exit 1
        fi
    fi
    [ -f "$ZIP_FILE" ] && rm "$ZIP_FILE"
fi

# 5. Make executable and configure
cd "$INSTALL_DIR" || exit 1
chmod +x CalendarDashboard

# Create an initial .env file if it does not exist
if [ ! -f ".env" ]; then
    if [ -f "$ORIG_DIR/.env" ]; then
        cp "$ORIG_DIR/.env" .env
    else
        echo "API_ENDPOINT=https://localhost:5000" > .env
    fi
fi

echo "Installation abgeschlossen!"
echo ""

# 6. Ask for test run in XRDP
read -p "Möchtest du das Programm testweise über XRDP starten? (y/n): " run_xrdp

if [[ "$run_xrdp" =~ ^[Yy]$ ]]; then
    # Detect current DISPLAY
    DETECTED_DISPLAY=$DISPLAY
    if [ -z "$DETECTED_DISPLAY" ]; then
        DETECTED_DISPLAY=":10.0"
    fi
    
    read -p "Welche Display-Nummer soll verwendet werden? (Standard: $DETECTED_DISPLAY): " input_display
    DISPLAY_NUM=${input_display:-$DETECTED_DISPLAY}
    
    echo "Starte Dashboard auf Display $DISPLAY_NUM..."
    echo "Drücke STRG+C im Terminal, um das Programm zu beenden."
    
    DISPLAY="$DISPLAY_NUM" ./CalendarDashboard
else
    echo "Installation abgeschlossen. Du kannst das Dashboard manuell im Installationsordner starten:"
    echo "cd $INSTALL_DIR && ./CalendarDashboard"
fi
