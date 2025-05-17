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
import requests

API_KEY = "SD2BHB9D9ARCGK44"
BASE_URL = "https://www.alphavantage.co/query"

def fetch_alpha_data(query: str) -> str:
    try:
        tokens = query.strip().split()
        if len(tokens) != 2:
            return "❌ Invalid input format. Please use: '<SYMBOL> <FUNCTION>' (e.g., 'AAPL OVERVIEW')."

        symbol, function = tokens
        function = function.upper()

        if function not in {"OVERVIEW", "INCOME_STATEMENT", "BALANCE_SHEET", "CASH_FLOW"}:
            return (
                f"❌ '{function}' is not a valid Alpha Vantage function.\n"
                f"Choose one of: OVERVIEW, INCOME_STATEMENT, BALANCE_SHEET, CASH_FLOW."
            )

        params = {
            "function": function,
            "symbol": symbol,
            "apikey": API_KEY
        }

        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()

        data = response.json()

        # Try to summarize important values for overview
        if function == "OVERVIEW":
            summary_keys = [
                "Name", "Symbol", "Sector", "Industry", "MarketCapitalization", "PERatio", "PEGRatio", "DividendYield"
            ]
            summary = {k: data.get(k, "N/A") for k in summary_keys}
            return "\n".join([f"{k}: {v}" for k, v in summary.items()])

        return str(data)

    except requests.exceptions.RequestException as e:
        return f"🌐 Network error: {e}"
    except Exception as e:
        return f"⚠️ Alpha Vantage error: {e}"


if __name__ == "__main__":
    print(fetch_alpha_data("AMD OVERVIEW"))
