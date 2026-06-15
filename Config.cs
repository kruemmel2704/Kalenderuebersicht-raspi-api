using System;
using System.IO;
using dotenv.net;

namespace CalendarDashboard
{
    public static class Config
    {
        public static string ApiEndpoint { get; private set; } = "https://localhost:5000";

        static Config()
        {
            // Resolve .env path
            string baseDir = AppContext.BaseDirectory;
            string envPath = Path.Combine(baseDir, ".env");
            
            // Fallback for local launch
            if (!File.Exists(envPath))
            {
                envPath = Path.Combine(Directory.GetCurrentDirectory(), ".env");
            }

            if (File.Exists(envPath))
            {
                try
                {
                    DotEnv.Load(new DotEnvOptions(envFilePaths: new[] { envPath }));
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error loading .env: {ex.Message}");
                }
            }

            string? endpoint = Environment.GetEnvironmentVariable("API_ENDPOINT");
            if (!string.IsNullOrEmpty(endpoint))
            {
                ApiEndpoint = endpoint;
            }

            if (ApiEndpoint.EndsWith("/"))
            {
                ApiEndpoint = ApiEndpoint.Substring(0, ApiEndpoint.Length - 1);
            }
            
            Console.WriteLine($"Target API Endpoint: {ApiEndpoint}");
        }
    }
}
