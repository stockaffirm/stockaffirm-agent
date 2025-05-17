import requests

API_KEY = "SD2BHB9D9ARCGK44"
BASE_URL = "https://www.alphavantage.co/query"

def fetch_alpha_data(symbol_and_type: str) -> str:
    """
    Input should be: 'AMD OVERVIEW' or 'MSFT INCOME_STATEMENT'
    """
    try:
        parts = symbol_and_type.strip().split()
        if len(parts) != 2:
            return "Please format as: SYMBOL FUNCTION (e.g., AMD OVERVIEW)"
        symbol, function = parts
        params = {
            "function": function.upper(),
            "symbol": symbol.upper(),
            "apikey": API_KEY
        }
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        return str(response.json())
    except Exception as e:
        return f"Alpha Vantage error: {e}"

if __name__ == "__main__":
    print(fetch_alpha_data("AMD OVERVIEW"))
