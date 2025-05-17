import requests
import json
from typing import Union, Tuple

API_KEY = "SD2BHB9D9ARCGK44"
BASE_URL = "https://www.alphavantage.co/query"


def map_natural_to_function(query: str) -> Union[Tuple[str, str], str]:
    """Maps natural language like 'Show cash flow for AMD' to (symbol, function)"""
    query = query.lower()

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

    # Try to extract a stock symbol (simple assumption: short all-caps word)
    words = query.split()
    symbol = next((word.upper() for word in words if len(word) <= 5 and word.isalpha()), None)
    if not symbol:
        return "Could not find stock symbol."

    return symbol, function


def fetch_alpha_data(query: str) -> str:
    try:
        tokens = query.strip().split()
        if len(tokens) != 2:
            return "❌ Invalid input format. Use: '<SYMBOL> <FUNCTION>' (e.g., 'AAPL OVERVIEW')."

        symbol, function = tokens
        symbol = symbol.strip().upper().replace("'", "").replace('"', "")
        function = function.strip().upper().replace("'", "").replace('"', "")

        valid_functions = {"OVERVIEW", "INCOME_STATEMENT", "BALANCE_SHEET", "CASH_FLOW"}
        if function not in valid_functions:
            return (
                f"❌ '{function}' is not a valid Alpha Vantage function.\n"
                f"Choose one of: {', '.join(valid_functions)}."
            )

        params = {
            "function": function,
            "symbol": symbol,
            "apikey": API_KEY
        }

        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        # Handle empty response
        if not data or all(v == "None" or v == "N/A" or v is None for v in data.values()):
            return (
                f"⚠️ Alpha Vantage returned no usable data for '{symbol}' using function '{function}'.\n"
                f"Partial response preview:\n{json.dumps(data, indent=2)[:800]}"
            )

        if function == "OVERVIEW":
            summary_keys = [
                "Name", "Symbol", "Sector", "Industry",
                "MarketCapitalization", "PERatio", "PEGRatio", "DividendYield"
            ]
            summary = {k: data.get(k, "N/A") for k in summary_keys}
            return "\n".join(f"{k}: {v}" for k, v in summary.items())

        return json.dumps(data, indent=2)

    except requests.exceptions.RequestException as e:
        return f"🌐 Network error: {e}"
    except Exception as e:
        return f"⚠️ Alpha Vantage error: {e}"


if __name__ == "__main__":
    print(fetch_alpha_data("AMD OVERVIEW"))
