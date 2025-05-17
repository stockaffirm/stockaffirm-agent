import requests

def fetch_script_from_github(raw_url: str) -> str:
    try:
        response = requests.get(raw_url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"Error fetching from GitHub: {e}"
