using System;
using System.Collections.Generic;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Interactivity;
using Avalonia.Threading;

namespace CalendarDashboard
{
    public partial class PlaylistDialog : Window
    {
        public PlaylistDialog()
        {
            InitializeComponent();
            LoadDefaultPlaylists();
        }

        private void LoadDefaultPlaylists()
        {
            SearchPlaylists(string.Empty);
        }

        private void OnSearchKeyDown(object? sender, KeyEventArgs e)
        {
            if (e.Key == Key.Enter)
            {
                SearchPlaylists(SearchInput.Text ?? string.Empty);
            }
        }

        private async void SearchPlaylists(string query)
        {
            var response = await ApiService.SearchPlaylistsAsync(query);
            Dispatcher.UIThread.Post(() =>
            {
                PlaylistListBox.ItemsSource = response?.Playlists ?? new List<Playlist>();
            });
        }

        private void OnListBoxDoubleTapped(object? sender, TappedEventArgs e)
        {
            if (PlaylistListBox.SelectedItem is Playlist selected)
            {
                if (!string.IsNullOrEmpty(selected.Uri))
                {
                    ApiService.FireAndForgetPost("play_playlist", new { uri = selected.Uri });
                }
                Close(true);
            }
        }

        private void OnCloseClick(object? sender, RoutedEventArgs e)
        {
            Close(false);
        }
    }
}
