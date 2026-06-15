import os

def load_env(filepath=None):
    if filepath is None:
        # Resolve path relative to this file (app/config.py -> parent -> .env)
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(root_dir, ".env")
        
    env_vars = {}
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split("=", 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    val = parts[1].strip()
                    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                        val = val[1:-1]
                    env_vars[key] = val
                    os.environ[key] = val
    return env_vars

# Load environment
env = load_env()
api_endpoint = os.getenv("API_ENDPOINT", "https://localhost:5000")
if api_endpoint.endswith("/"):
    api_endpoint = api_endpoint[:-1]
