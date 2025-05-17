import requests
import json
from typing import Union, Tuple


API_KEY = "SD2BHB9D9ARCGK44"
BASE_URL = "https://www.alphavantage.co/query"

def map_natural_to_function(query: str) -> Union[Tuple[str, str], str]:
    """Maps human prompt like 'Show cash flow for AMD' to (symbol, function)"""
    query = query.lower()

    # Function mapping
    if "balance" in query:
        function = "BALANCE_SHEET"
    elif "income" in query:
        function = "INCOME_STATEMENT"
    elif "cash" in query:
        function = "CASH_FLOW"
    elif "overview" in query or "info" in query:
        function = "OVERVIEW"
    else:
        return "Could not determine financial function (overview, balance, income, cash)."

    # Symbol extraction (very basic)
    words = query.split()
    symbol = next((word.upper() for word in words if len(word) <= 5 and word.isalpha()), None)
    if not symbol:
        return "Could not find stock symbol."

    return symbol, function

def fetch_alpha_data(query: str) -> str:
    try:
        result = map_natural_to_function(query)
        if isinstance(result, str):
            return result  # error string
        symbol, function = result

        params = {
            "function": function,
            "symbol": symbol,
            "apikey": API_KEY
        }
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        # ✅ Option 1: extract key fields and return summary
        data = response.json()

        summary_fields = [
            "Symbol", "Name", "Sector", "Industry",
            "PERatio", "PEGRatio", "MarketCapitalization", "DividendYield"
        ]

        summary = {k: data.get(k, "N/A") for k in summary_fields}
        return json.dumps(summary, indent=2)

    except Exception as e:
        return f"Alpha Vantage error: {e}"


if __name__ == "__main__":
    print(fetch_alpha_data("AMD OVERVIEW"))
