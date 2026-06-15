using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace CalendarDashboard
{
    public class TravelTime
    {
        [JsonPropertyName("driving")]
        public string? Driving { get; set; }

        [JsonPropertyName("walking")]
        public string? Walking { get; set; }
    }

    public class Event
    {
        [JsonPropertyName("date_str")]
        public string? DateStr { get; set; }

        [JsonPropertyName("time_str")]
        public string? TimeStr { get; set; }

        [JsonPropertyName("summary")]
        public string? Summary { get; set; }

        [JsonPropertyName("location")]
        public string? Location { get; set; }

        [JsonPropertyName("assignee")]
        public string? Assignee { get; set; }

        [JsonPropertyName("travel_time")]
        public TravelTime? TravelTime { get; set; }
    }

    public class EventsResponse
    {
        [JsonPropertyName("last_update")]
        public string? LastUpdate { get; set; }

        [JsonPropertyName("events")]
        public List<Event>? Events { get; set; }
    }

    public class SpotifyState
    {
        [JsonPropertyName("track")]
        public string? Track { get; set; }

        [JsonPropertyName("artist")]
        public string? Artist { get; set; }

        [JsonPropertyName("is_playing")]
        public bool IsPlaying { get; set; }

        [JsonPropertyName("volume")]
        public int Volume { get; set; }

        [JsonPropertyName("error")]
        public string? Error { get; set; }

        [JsonPropertyName("auth_required")]
        public bool AuthRequired { get; set; }
    }

    public class PlaylistOwner
    {
        [JsonPropertyName("display_name")]
        public string? DisplayName { get; set; }
    }

    public class Playlist
    {
        [JsonPropertyName("name")]
        public string? Name { get; set; }

        [JsonPropertyName("owner")]
        public PlaylistOwner? Owner { get; set; }

        [JsonPropertyName("uri")]
        public string? Uri { get; set; }
    }

    public class PlaylistsResponse
    {
        [JsonPropertyName("playlists")]
        public List<Playlist>? Playlists { get; set; }
    }
}
