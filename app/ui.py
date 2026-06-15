import os
import sys
import time
import threading
import requests
from datetime import datetime, timedelta

# PyQt5 imports
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QSlider, QPushButton, QDialog, QLineEdit, QListWidget,
    QListWidgetItem, QGridLayout, QSizePolicy
)
from PyQt5.QtGui import QPixmap

# Internal package imports
from app.worker import ApiWorker, fire_and_forget

# Helper to recursively clear layouts
def clear_layout(layout):
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                sub_layout = item.layout()
                if sub_layout is not None:
                    clear_layout(sub_layout)

# 3. Custom Centering 16:9 Aspect Ratio Container Widget
class RatioWidget(QWidget):
    def __init__(self, child_widget, parent=None):
        super().__init__(parent)
        self.child = child_widget
        self.child.setParent(self)
        self.aspect_ratio = 16.0 / 9.0
        self.setStyleSheet("background-color: #000000;") # Black letterbox borders

    def resizeEvent(self, event):
        w = self.width()
        h = self.height()
        
        if w / h > self.aspect_ratio:
            # Screen is wider than 16:9 (Pillarbox)
            new_h = h
            new_w = int(h * self.aspect_ratio)
        else:
            # Screen is narrower than 16:9 (Letterbox)
            new_w = w
            new_h = int(w / self.aspect_ratio)
            
        x = (w - new_w) // 2
        y = (h - new_h) // 2
        self.child.setGeometry(x, y, new_w, new_h)

# 4. Spotify Playlist Dialog Selection Panel
class PlaylistDialog(QDialog):
    def __init__(self, endpoint, parent=None):
        super().__init__(parent)
        self.endpoint = endpoint
        self.setWindowTitle("Spotify Playlists")
        self.resize(500, 400)
        self.setStyleSheet("""
            QDialog {
                background-color: #102a4e;
                border: 2px solid #2a4365;
                border-radius: 12px;
            }
            QLineEdit {
                background-color: #1a365d;
                border: 1px solid #2a4365;
                border-radius: 8px;
                color: #ffffff;
                padding: 8px;
                font-size: 13px;
            }
            QListWidget {
                background-color: #1a365d;
                border: 1px solid #2a4365;
                border-radius: 8px;
                color: #ffffff;
                padding: 5px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #2a4365;
            }
            QListWidget::item:hover {
                background-color: #007bb5;
                border-radius: 6px;
            }
            QPushButton {
                background-color: #1DB954;
                color: #000000;
                font-weight: bold;
                border-radius: 8px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #1ed760;
            }
        """)

        layout = QVBoxLayout()
        
        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nach Playlists suchen...")
        self.search_input.returnPressed.connect(self.search_playlists)
        layout.addWidget(self.search_input)

        # Playlist results list
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.play_selected)
        layout.addWidget(self.list_widget)

        # Cancel button
        close_btn = QPushButton("Schließen")
        close_btn.setStyleSheet("background-color: #cbd5e1; color: #000000;")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        self.setLayout(layout)
        
        # Load default playlists
        self.search_playlists()

    def search_playlists(self):
        query = self.search_input.text()
        self.list_widget.clear()
        
        # Fetch playlists in thread
        def perform_search():
            try:
                r = requests.get(f"{self.endpoint}/api/spotify/playlists", params={"q": query}, timeout=4, verify=False)
                if r.status_code == 200:
                    playlists = r.json().get("playlists", [])
                    # Update UI in main thread safety
                    QTimer.singleShot(0, lambda: self.display_playlists(playlists))
            except Exception as e:
                print(f"Search fetch error: {e}")

        threading.Thread(target=perform_search, daemon=True).start()

    def display_playlists(self, playlists):
        for pl in playlists:
            if not pl:
                continue
            name = pl.get("name", "Unbekannt")
            owner = pl.get("owner", {}).get("display_name", "Unbekannt")
            uri = pl.get("uri", "")
            
            item = QListWidgetItem(f"{name} (Von {owner})")
            item.setData(Qt.UserRole, uri)
            self.list_widget.addItem(item)

    def play_selected(self, item):
        uri = item.data(Qt.UserRole)
        # Play playlist on remote server API
        fire_and_forget(f"{self.endpoint}/api/spotify/play_playlist", json_data={"uri": uri})
        self.accept()

# 5. Main Calendar UI Dashboard Widget
class CalendarWidget(QWidget):
    def __init__(self, endpoint):
        super().__init__()
        self.endpoint = endpoint
        self.setObjectName("CalendarContainer")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(32, 32, 32, 32)
        main_layout.setSpacing(24)

        # --- HEADER AREA ---
        header = QHBoxLayout()
        
        # Logo (scaled)
        self.logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", "logo.png")
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path)
            self.logo_label.setPixmap(pix.scaled(200, 65, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        header.addWidget(self.logo_label)

        # Title / Date Middle column
        title_col = QVBoxLayout()
        title_col.setAlignment(Qt.AlignCenter)
        
        self.title_lbl = QLabel("Wochenplan")
        self.title_lbl.setObjectName("MainTitle")
        self.title_lbl.setStyleSheet("color: #ffffff; font-size: 40px; font-weight: bold;")
        title_col.addWidget(self.title_lbl)

        self.date_lbl = QLabel("Heute ist ...")
        self.date_lbl.setObjectName("SubTitle")
        self.date_lbl.setStyleSheet("color: #94a3b8; font-size: 18px; font-weight: 500;")
        title_col.addWidget(self.date_lbl)
        
        header.addLayout(title_col)

        # Status & Digital Clock Right column
        right_col = QVBoxLayout()
        right_col.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        self.clock_lbl = QLabel("00:00:00")
        self.clock_lbl.setStyleSheet("""
            color: #cbd5e1;
            font-size: 24px;
            font-weight: bold;
            background-color: #1a365d;
            border: 1px solid #2a4365;
            border-radius: 8px;
            padding: 8px 16px;
        """)
        right_col.addWidget(self.clock_lbl)

        self.status_lbl = QLabel("Live Sync")
        self.status_lbl.setStyleSheet("""
            color: #64748b;
            font-size: 14px;
            background-color: rgba(30, 41, 59, 0.5);
            border: 1px solid #2a4365;
            border-radius: 15px;
            padding: 6px 12px;
        """)
        right_col.addWidget(self.status_lbl)

        header.addLayout(right_col)
        main_layout.addLayout(header)

        # --- EVENT GRID AREA ---
        self.grid_layout = QHBoxLayout()
        self.grid_layout.setSpacing(20)
        self.columns = []

        # Create 5 columns
        for i in range(5):
            col_frame = QFrame()
            col_frame.setStyleSheet("background-color: transparent;")
            col_layout = QVBoxLayout(col_frame)
            col_layout.setContentsMargins(0, 0, 0, 0)
            col_layout.setSpacing(16)
            
            # Column Header label
            hdr_lbl = QLabel("Lade...")
            hdr_lbl.setStyleSheet("""
                color: #e2e8f0;
                font-weight: bold;
                font-size: 20px;
                border-bottom: 2px solid #2a4365;
                padding-bottom: 8px;
            """)
            col_layout.addWidget(hdr_lbl)

            # Scroll area for events inside this column
            scroll = QScrollArea()
            scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet("background: transparent; border: none;")
            
            scroll_widget = QWidget()
            scroll_widget.setStyleSheet("background: transparent;")
            scroll_layout = QVBoxLayout(scroll_widget)
            scroll_layout.setContentsMargins(0, 0, 0, 0)
            scroll_layout.setSpacing(12)
            scroll_layout.setAlignment(Qt.AlignTop)
            
            scroll.setWidget(scroll_widget)
            col_layout.addWidget(scroll)

            self.grid_layout.addWidget(col_frame)
            self.columns.append({
                "header": hdr_lbl,
                "layout": scroll_layout
            })

        main_layout.addLayout(self.grid_layout, stretch=1)

        # --- SPOTIFY FOOTER PLAYER ---
        self.spotify_footer = QFrame()
        self.spotify_footer.setObjectName("SpotifyFooter")
        self.spotify_footer.setStyleSheet("""
            QFrame#SpotifyFooter {
                background-color: #1a365d;
                border-top: 1px solid #2a4365;
                border-radius: 12px;
            }
        """)
        self.spotify_layout = QHBoxLayout(self.spotify_footer)
        self.spotify_layout.setContentsMargins(20, 15, 20, 15)
        self.spotify_layout.setSpacing(16)

        # Spotify logo / Icon
        self.sp_logo = QLabel("Spotify")
        self.sp_logo.setStyleSheet("color: #1DB954; font-weight: bold; font-size: 18px;")
        self.spotify_layout.addWidget(self.sp_logo)

        # Track details text
        self.track_info = QLabel("Keine Wiedergabe aktiv")
        self.track_info.setStyleSheet("color: #e2e8f0; font-size: 16px; font-weight: 500;")
        self.spotify_layout.addWidget(self.track_info, stretch=1)

        # Playback control buttons
        self.btn_prev = QPushButton("⏮")
        self.btn_play = QPushButton("▶")
        self.btn_next = QPushButton("⏭")
        self.btn_playlist = QPushButton("☰")

        for btn in [self.btn_prev, self.btn_play, self.btn_next, self.btn_playlist]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #e2e8f0;
                    border: none;
                    font-size: 22px;
                    width: 40px;
                    height: 40px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.1);
                    border-radius: 20px;
                }
            """)
            self.spotify_layout.addWidget(btn)

        self.btn_prev.clicked.connect(self.spotify_prev)
        self.btn_play.clicked.connect(self.spotify_play_pause)
        self.btn_next.clicked.connect(self.spotify_next)
        self.btn_playlist.clicked.connect(self.open_playlists)

        # Volume slider
        self.vol_slider = QSlider(Qt.Horizontal)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(50)
        self.vol_slider.setFixedWidth(120)
        self.vol_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px;
                background: #475569;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                width: 14px;
                height: 14px;
                background: #1DB954;
                border-radius: 7px;
                margin: -4px 0;
            }
        """)
        self.vol_slider.valueChanged.connect(self.change_volume)
        self.spotify_layout.addWidget(self.vol_slider)

        main_layout.addWidget(self.spotify_footer)

        self.setLayout(main_layout)

        # Clock setup
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)
        self.update_clock()

    def update_clock(self):
        self.clock_lbl.setText(datetime.now().strftime("%H:%M:%S"))
        # Set date header
        day_names = ["Sonntag", "Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag"]
        d = datetime.now()
        day_name = day_names[int(d.strftime("%w"))]
        date_str = d.strftime("%d. %B %Y")
        self.date_lbl.setText(f"Heute ist {day_name}, der {date_str}")

    # --- SPOTIFY CONTROL TRIGGERS ---
    def spotify_prev(self):
        fire_and_forget(f"{self.endpoint}/api/spotify/previous")

    def spotify_next(self):
        fire_and_forget(f"{self.endpoint}/api/spotify/next")

    def spotify_play_pause(self):
        fire_and_forget(f"{self.endpoint}/api/spotify/play_pause")

    def change_volume(self, val):
        fire_and_forget(f"{self.endpoint}/api/spotify/volume", json_data={"volume": val})

    def open_playlists(self):
        dialog = PlaylistDialog(self.endpoint, self)
        dialog.exec_()

    # --- DATA BINDING UPDATES ---
    def update_events_ui(self, data):
        # Update last sync timestamp
        last_upd = data.get("last_update", "N/A")
        self.status_lbl.setText(f"● Live Sync ({last_upd})")
        self.status_lbl.setStyleSheet("color: #10b981; font-size: 14px; background-color: rgba(30, 41, 59, 0.5); border: 1px solid #2a4365; border-radius: 15px; padding: 6px 12px;")

        # Set up dates for 5 columns starting from Today
        today = datetime.now().date()
        day_names = ["Sonntag", "Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag"]
        
        days_headers = []
        days_date_strings = []
        for i in range(5):
            d = today + timedelta(days=i)
            date_str = d.strftime("%d.%m.")
            days_date_strings.append(date_str)
            
            display_name = day_names[int(d.strftime("%w"))]
            if i == 0:
                display_name = "Heute"
            elif i == 1:
                display_name = "Morgen"
            days_headers.append(f"{display_name}, {date_str}")

        # Group fetched events
        grouped_events = {d: [] for d in days_date_strings}
        for ev in data.get("events", []):
            d_str = ev.get("date_str")
            if d_str in grouped_events:
                grouped_events[d_str].append(ev)

        # Redraw each column
        for i in range(5):
            col = self.columns[i]
            d_str = days_date_strings[i]
            col["header"].setText(days_headers[i])
            
            clear_layout(col["layout"])
            events = grouped_events[d_str]

            if not events:
                # Show no events card
                no_ev = QFrame()
                no_ev.setObjectName("NoEventsCard")
                no_ev.setStyleSheet("border: 2px dashed #2a4365; border-radius: 12px; padding: 20px;")
                no_ev_lay = QVBoxLayout(no_ev)
                no_ev_lay.setAlignment(Qt.AlignCenter)
                lbl = QLabel("Keine Termine")
                lbl.setStyleSheet("color: #94a3b8; font-size: 16px; font-weight: 500;")
                no_ev_lay.addWidget(lbl)
                col["layout"].addWidget(no_ev)
            else:
                for ev in events:
                    card = QFrame()
                    card.setObjectName("EventCard")
                    card.setStyleSheet("""
                        QFrame#EventCard {
                            background-color: #1a365d;
                            border: 1px solid #2a4365;
                            border-radius: 12px;
                        }
                        QFrame#EventCard:hover {
                            border: 1px solid #475569;
                            background-color: #244273;
                        }
                    """)
                    card_lay = QVBoxLayout(card)
                    card_lay.setContentsMargins(16, 16, 16, 16)
                    card_lay.setSpacing(8)

                    # Time and travel badges
                    time_row = QHBoxLayout()
                    time_lbl = QLabel(ev.get("time_str", ""))
                    time_lbl.setStyleSheet("color: #60a5fa; font-weight: bold; font-size: 16px;")
                    time_row.addWidget(time_lbl)

                    travel = ev.get("travel_time")
                    if travel:
                        if travel.get("driving"):
                            t_badge = QLabel(f"🚗 {travel['driving']}")
                            t_badge.setStyleSheet("""
                                color: #10b981;
                                background-color: rgba(16, 185, 129, 0.15);
                                border: 1px solid rgba(16, 185, 129, 0.3);
                                border-radius: 8px;
                                padding: 2px 6px;
                                font-weight: bold;
                                font-size: 12px;
                            """)
                            time_row.addWidget(t_badge)
                        if travel.get("walking"):
                            w_badge = QLabel(f"🚶 {travel['walking']}")
                            w_badge.setStyleSheet("""
                                color: #3b82f6;
                                background-color: rgba(59, 130, 246, 0.15);
                                border: 1px solid rgba(59, 130, 246, 0.3);
                                border-radius: 8px;
                                padding: 2px 6px;
                                font-weight: bold;
                                font-size: 12px;
                            """)
                            time_row.addWidget(w_badge)

                    card_lay.addLayout(time_row)

                    # Title
                    title = QLabel(ev.get("summary", ""))
                    title.setWordWrap(True)
                    title.setStyleSheet("color: #e2e8f0; font-weight: bold; font-size: 17px;")
                    card_lay.addWidget(title)

                    # Location
                    loc = ev.get("location")
                    if loc:
                        loc_lbl = QLabel(f"📍 {loc}")
                        loc_lbl.setWordWrap(True)
                        loc_lbl.setStyleSheet("color: #94a3b8; font-size: 14px;")
                        card_lay.addWidget(loc_lbl)

                    # Assignee
                    assign = ev.get("assignee")
                    if assign:
                        ass_lbl = QLabel(f"wird erledigt von: {assign}")
                        ass_lbl.setStyleSheet("color: #94a3b8; font-size: 14px; font-style: italic;")
                        card_lay.addWidget(ass_lbl)

                    col["layout"].addWidget(card)

            # Push cards up
            col["layout"].addStretch(1)

    def update_spotify_ui(self, data):
        # Update Spotify player state
        if data.get("error") or data.get("auth_required"):
            self.track_info.setText("Spotify-Verknüpfung erforderlich")
            self.btn_play.setText("▶")
            return
            
        track = data.get("track")
        artist = data.get("artist")
        is_playing = data.get("is_playing", False)
        volume = data.get("volume", 50)

        if track:
            self.track_info.setText(f"{track} - {artist}")
            self.btn_play.setText("⏸" if is_playing else "▶")
            # Update slider value block signals temporarily to avoid loops
            self.vol_slider.blockSignals(True)
            self.vol_slider.setValue(volume)
            self.vol_slider.blockSignals(False)
        else:
            self.track_info.setText("Keine Wiedergabe aktiv")
            self.btn_play.setText("▶")

    def show_connection_error(self, err_msg):
        self.status_lbl.setText("● Offline (Reconnecting...)")
        self.status_lbl.setStyleSheet("color: #ef4444; font-size: 14px; background-color: rgba(30, 41, 59, 0.5); border: 1px solid #2a4365; border-radius: 15px; padding: 6px 12px;")

# 6. Main Entry Point Window
class MainWindow(QMainWindow):
    def __init__(self, endpoint, is_desktop=False):
        super().__init__()
        self.setWindowTitle("Calendar Dashboard")
        self.is_desktop = is_desktop
        
        # Explicitly set the window size to 1920x1080
        self.resize(1920, 1080)

        # Inner calendar layout widget
        self.calendar = CalendarWidget(endpoint)

        # Wrapped inside Aspect Ratio 16:9 container
        self.ratio_container = RatioWidget(self.calendar, self)
        self.setCentralWidget(self.ratio_container)

        self.init_theme()

        # Start API Background Thread
        self.worker = ApiWorker(endpoint)
        self.worker.events_ready.connect(self.calendar.update_events_ui)
        self.worker.spotify_ready.connect(self.calendar.update_spotify_ui)
        self.worker.connection_error.connect(self.calendar.show_connection_error)
        self.worker.start()

    def init_theme(self):
        # Apply style sheet
        self.setStyleSheet("""
            * {
                font-family: 'Inter', 'Segoe UI', -apple-system, Helvetica, Arial, sans-serif;
            }
            QMainWindow {
                background-color: #000000;
            }
            QWidget#CalendarContainer {
                background-color: #102a4e;
            }
        """)

    def closeEvent(self, event):
        # Stop workers on close
        self.worker.running = False
        self.worker.quit()
        self.worker.wait()
        super().closeEvent(event)
