using System;
using System.Collections.Generic;
using System.IO;
using System.Threading.Tasks;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Controls.Primitives;
using Avalonia.Interactivity;
using Avalonia.Media;
using Avalonia.Media.Imaging;
using Avalonia.Threading;
using Material.Icons;


namespace CalendarDashboard
{
    public partial class MainWindow : Window
    {
        private bool _running = true;
        private bool _isUpdatingVolume = false;

        public MainWindow()
        {
            InitializeComponent();

            // Set window size & state from config
            Width = Config.Width;
            Height = Config.Height;
            WindowState = Config.Fullscreen ? WindowState.FullScreen : WindowState.Normal;

            RootGrid.SizeChanged += OnRootGridSizeChanged;
            LoadAssets();
            
            // Start clock timer
            var clockTimer = new DispatcherTimer
            {
                Interval = TimeSpan.FromSeconds(1)
            };
            clockTimer.Tick += (s, e) => UpdateClock();
            clockTimer.Start();
            UpdateClock();

            // Start polling loops
            StartPollingLoops();
        }

        private void LoadAssets()
        {
            string baseDir = AppContext.BaseDirectory;
            
            // Resolve background image
            string bgPath = Path.Combine(baseDir, "static", "background.png");
            if (!File.Exists(bgPath))
            {
                bgPath = Path.Combine(Directory.GetCurrentDirectory(), "static", "background.png");
            }

            if (File.Exists(bgPath))
            {
                try
                {
                    var bitmap = new Bitmap(bgPath);
                    CalendarContainer.Background = new ImageBrush(bitmap) { Stretch = Stretch.Fill };
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error loading background image: {ex.Message}");
                    CalendarContainer.Background = Brush.Parse("#102a4e");
                }
            }
            else
            {
                CalendarContainer.Background = Brush.Parse("#102a4e");
            }

            // Resolve logo image
            string logoPath = Path.Combine(baseDir, "static", "logo.png");
            if (!File.Exists(logoPath))
            {
                logoPath = Path.Combine(Directory.GetCurrentDirectory(), "static", "logo.png");
            }

            if (File.Exists(logoPath))
            {
                try
                {
                    LogoImage.Source = new Bitmap(logoPath);
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error loading logo image: {ex.Message}");
                }
            }
        }

        private void OnRootGridSizeChanged(object? sender, SizeChangedEventArgs e)
        {
            double targetRatio = (double)Config.Width / Config.Height;
            double w = e.NewSize.Width;
            double h = e.NewSize.Height;
            
            double newW, newH;
            if (w / h > targetRatio)
            {
                newH = h;
                newW = h * targetRatio;
            }
            else
            {
                newW = w;
                newH = w / targetRatio;
            }
            
            CalendarContainer.Width = newW;
            CalendarContainer.Height = newH;
        }

        private void UpdateClock()
        {
            ClockLabel.Text = DateTime.Now.ToString("HH:mm:ss");
            
            string[] dayNames = { "Sonntag", "Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag" };
            DateTime d = DateTime.Now;
            string dayName = dayNames[(int)d.DayOfWeek];
            string dateStr = d.ToString("dd. MMMM yyyy");
            DateLabel.Text = $"Heute ist {dayName}, der {dateStr}";
        }

        private void StartPollingLoops()
        {
            // Events polling loop (every 10 seconds)
            Task.Run(async () =>
            {
                while (_running)
                {
                    var data = await ApiService.GetEventsAsync();
                    if (data != null)
                    {
                        Dispatcher.UIThread.Post(() => UpdateEventsUI(data));
                    }
                    else
                    {
                        Dispatcher.UIThread.Post(() => ShowConnectionError());
                    }
                    await Task.Delay(10000);
                }
            });

            // Spotify polling loop (every 3 seconds)
            Task.Run(async () =>
            {
                while (_running)
                {
                    var data = await ApiService.GetSpotifyStateAsync();
                    if (data != null)
                    {
                        Dispatcher.UIThread.Post(() => UpdateSpotifyUI(data));
                    }
                    await Task.Delay(3000);
                }
            });
        }

        private void UpdateEventsUI(EventsResponse data)
        {
            string lastUpd = data.LastUpdate ?? "N/A";
            StatusLabel.Text = $"● Live Sync ({lastUpd})";
            StatusLabel.Foreground = Brush.Parse("#10b981");
            StatusBorder.Background = Brush.Parse("#801e293b");

            DateTime today = DateTime.Today;
            string[] dayNames = { "Sonntag", "Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag" };

            var colHeaders = new[] { ColHeader0, ColHeader1, ColHeader2, ColHeader3, ColHeader4 };
            var colPanels = new[] { ColPanel0, ColPanel1, ColPanel2, ColPanel3, ColPanel4 };
            var daysDateStrings = new List<string>();
            var daysHeaders = new List<string>();

            for (int i = 0; i < 5; i++)
            {
                DateTime d = today.AddDays(i);
                string dateStr = d.ToString("dd.MM.");
                daysDateStrings.Add(dateStr);

                string displayName = dayNames[(int)d.DayOfWeek];
                if (i == 0) displayName = "Heute";
                else if (i == 1) displayName = "Morgen";

                daysHeaders.Add($"{displayName}, {dateStr}");
            }

            var groupedEvents = new Dictionary<string, List<Event>>();
            foreach (var dStr in daysDateStrings)
            {
                groupedEvents[dStr] = new List<Event>();
            }

            if (data.Events != null)
            {
                foreach (var ev in data.Events)
                {
                    if (ev.DateStr != null && groupedEvents.ContainsKey(ev.DateStr))
                    {
                        groupedEvents[ev.DateStr].Add(ev);
                    }
                }
            }

            for (int i = 0; i < 5; i++)
            {
                colHeaders[i].Text = daysHeaders[i];
                var panel = colPanels[i];
                panel.Children.Clear();
                
                string dStr = daysDateStrings[i];
                var events = groupedEvents[dStr];

                if (events.Count == 0)
                {
                    var noEvBorder = new Border
                    {
                        BorderBrush = Brush.Parse("#2a4365"),
                        BorderThickness = new Thickness(2),
                        CornerRadius = new CornerRadius(12),
                        Padding = new Thickness(20),
                        Background = Brushes.Transparent,
                    };
                    noEvBorder.Child = new TextBlock
                    {
                        Text = "Keine Termine",
                        Foreground = Brush.Parse("#94a3b8"),
                        FontSize = 16,
                        FontWeight = FontWeight.Medium,
                        HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Center
                    };
                    panel.Children.Add(noEvBorder);
                }
                else
                {
                    foreach (var ev in events)
                    {
                        var cardBorder = new Border
                        {
                            Background = Brush.Parse("#1a365d"),
                            BorderBrush = Brush.Parse("#2a4365"),
                            BorderThickness = new Thickness(1),
                            CornerRadius = new CornerRadius(12),
                            Padding = new Thickness(16),
                            Margin = new Thickness(0, 0, 0, 12)
                        };

                        cardBorder.PointerEntered += (s, e) =>
                        {
                            cardBorder.Background = Brush.Parse("#244273");
                            cardBorder.BorderBrush = Brush.Parse("#475569");
                        };
                        cardBorder.PointerExited += (s, e) =>
                        {
                            cardBorder.Background = Brush.Parse("#1a365d");
                            cardBorder.BorderBrush = Brush.Parse("#2a4365");
                        };

                        var cardLayout = new StackPanel { Spacing = 8 };

                        var timeRow = new Grid();
                        timeRow.Children.Add(new TextBlock
                        {
                            Text = ev.TimeStr ?? string.Empty,
                            Foreground = Brush.Parse("#60a5fa"),
                            FontWeight = FontWeight.Bold,
                            FontSize = 16,
                            HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Left
                        });

                        var badgesPanel = new StackPanel
                        {
                            Orientation = Avalonia.Layout.Orientation.Horizontal,
                            Spacing = 6,
                            HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Right
                        };

                        if (ev.TravelTime != null)
                        {
                            if (!string.IsNullOrEmpty(ev.TravelTime.Driving))
                            {
                                var carBadge = new Border
                                {
                                    Background = Brush.Parse("#2610b981"), // 15% opacity green
                                    BorderBrush = Brush.Parse("#4D10b981"), // 30% opacity green
                                    BorderThickness = new Thickness(1),
                                    CornerRadius = new CornerRadius(8),
                                    Padding = new Thickness(6, 2)
                                };
                                carBadge.Child = new TextBlock
                                {
                                    Text = $"🚗 {ev.TravelTime.Driving}",
                                    Foreground = Brush.Parse("#10b981"),
                                    FontWeight = FontWeight.Bold,
                                    FontSize = 12
                                };
                                badgesPanel.Children.Add(carBadge);
                            }
                            if (!string.IsNullOrEmpty(ev.TravelTime.Walking))
                            {
                                var walkBadge = new Border
                                {
                                    Background = Brush.Parse("#263b82f6"), // 15% opacity blue
                                    BorderBrush = Brush.Parse("#4D3b82f6"), // 30% opacity blue
                                    BorderThickness = new Thickness(1),
                                    CornerRadius = new CornerRadius(8),
                                    Padding = new Thickness(6, 2)
                                };
                                walkBadge.Child = new TextBlock
                                {
                                    Text = $"🚶 {ev.TravelTime.Walking}",
                                    Foreground = Brush.Parse("#3b82f6"),
                                    FontWeight = FontWeight.Bold,
                                    FontSize = 12
                                };
                                badgesPanel.Children.Add(walkBadge);
                            }
                        }
                        timeRow.Children.Add(badgesPanel);
                        cardLayout.Children.Add(timeRow);

                        cardLayout.Children.Add(new TextBlock
                        {
                            Text = ev.Summary ?? string.Empty,
                            Foreground = Brush.Parse("#e2e8f0"),
                            FontWeight = FontWeight.Bold,
                            FontSize = 17,
                            TextWrapping = TextWrapping.Wrap
                        });

                        if (!string.IsNullOrEmpty(ev.Location))
                        {
                            cardLayout.Children.Add(new TextBlock
                            {
                                Text = $"📍 {ev.Location}",
                                Foreground = Brush.Parse("#94a3b8"),
                                FontSize = 14,
                                TextWrapping = TextWrapping.Wrap
                            });
                        }

                        if (!string.IsNullOrEmpty(ev.Assignee))
                        {
                            cardLayout.Children.Add(new TextBlock
                            {
                                Text = $"wird erledigt von: {ev.Assignee}",
                                Foreground = Brush.Parse("#94a3b8"),
                                FontSize = 14,
                                FontStyle = FontStyle.Italic
                            });
                        }

                        cardBorder.Child = cardLayout;
                        panel.Children.Add(cardBorder);
                    }
                }
            }
        }

        private void UpdateSpotifyUI(SpotifyState data)
        {
            if (data.AuthRequired || !string.IsNullOrEmpty(data.Error))
            {
                TrackInfoLabel.Text = "Spotify-Verknüpfung erforderlich";
                PlayPauseIcon.Kind = MaterialIconKind.Play;
                return;
            }

            if (!string.IsNullOrEmpty(data.Track))
            {
                TrackInfoLabel.Text = $"{data.Track} - {data.Artist}";
                PlayPauseIcon.Kind = data.IsPlaying ? MaterialIconKind.Pause : MaterialIconKind.Play;

                _isUpdatingVolume = true;
                VolSlider.Value = data.Volume;
                _isUpdatingVolume = false;
            }
            else
            {
                TrackInfoLabel.Text = "Keine Wiedergabe aktiv";
                PlayPauseIcon.Kind = MaterialIconKind.Play;
            }
        }

        private void ShowConnectionError()
        {
            StatusLabel.Text = "● Offline (Reconnecting...)";
            StatusLabel.Foreground = Brush.Parse("#ef4444");
            StatusBorder.Background = Brush.Parse("#801e293b");
        }

        private void OnPrevClick(object? sender, RoutedEventArgs e)
        {
            ApiService.FireAndForgetPost("previous");
        }

        private void OnPlayClick(object? sender, RoutedEventArgs e)
        {
            ApiService.FireAndForgetPost("play_pause");
        }

        private void OnNextClick(object? sender, RoutedEventArgs e)
        {
            ApiService.FireAndForgetPost("next");
        }

        private async void OnPlaylistClick(object? sender, RoutedEventArgs e)
        {
            var dialog = new PlaylistDialog();
            await dialog.ShowDialog(this);
        }

        private void OnVolumeChanged(object? sender, RangeBaseValueChangedEventArgs e)
        {
            if (_isUpdatingVolume) return;
            if (sender is Slider slider)
            {
                ApiService.FireAndForgetPost("volume", new { volume = (int)slider.Value });
            }
        }

        protected override void OnClosed(EventArgs e)
        {
            _running = false;
            base.OnClosed(e);
        }
    }
}