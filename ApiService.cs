using System;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

namespace CalendarDashboard
{
    public static class ApiService
    {
        private static readonly HttpClient _client;

        static ApiService()
        {
            var handler = new HttpClientHandler
            {
                ServerCertificateCustomValidationCallback = (message, cert, chain, errors) => true
            };
            _client = new HttpClient(handler)
            {
                Timeout = TimeSpan.FromSeconds(5)
            };
        }

        public static async Task<EventsResponse?> GetEventsAsync()
        {
            try
            {
                string url = $"{Config.ApiEndpoint}/api/events";
                string json = await _client.GetStringAsync(url);
                return JsonSerializer.Deserialize<EventsResponse>(json);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error fetching events: {ex.Message}");
                return null;
            }
        }

        public static async Task<SpotifyState?> GetSpotifyStateAsync()
        {
            try
            {
                string url = $"{Config.ApiEndpoint}/api/spotify";
                string json = await _client.GetStringAsync(url);
                return JsonSerializer.Deserialize<SpotifyState>(json);
            }
            catch (Exception)
            {
                // Ignore transient network errors for Spotify as in Python
                return null;
            }
        }

        public static void FireAndForgetPost(string subPath, object? jsonPayload = null)
        {
            Task.Run(async () =>
            {
                try
                {
                    string url = $"{Config.ApiEndpoint}/api/spotify/{subPath}";
                    if (jsonPayload != null)
                    {
                        string json = JsonSerializer.Serialize(jsonPayload);
                        var content = new StringContent(json, Encoding.UTF8, "application/json");
                        await _client.PostAsync(url, content);
                    }
                    else
                    {
                        await _client.PostAsync(url, null);
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Async POST error to {subPath}: {ex.Message}");
                }
            });
        }

        public static async Task<PlaylistsResponse?> SearchPlaylistsAsync(string query)
        {
            try
            {
                string url = $"{Config.ApiEndpoint}/api/spotify/playlists?q={Uri.EscapeDataString(query)}";
                string json = await _client.GetStringAsync(url);
                return JsonSerializer.Deserialize<PlaylistsResponse>(json);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error searching playlists: {ex.Message}");
                return null;
            }
        }
    }
}
