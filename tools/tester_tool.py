from tools.alpha_fetcher import fetch_alpha_data
from tools.git_agent import fetch_script_from_github
from supabase import create_client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def run_manual_check(instruction: str) -> str:
    """
    Format: 'Check <field> for <symbol> in <table>'
    Optional fallback: uses GitHub if script not found locally
    """
    try:
        parts = instruction.strip().split()
        if len(parts) < 5:
            return "Format: Check <field> for <symbol> in <table>"

        field, symbol, table = parts[1], parts[3], parts[5]

        # Step 1: Supabase value
        db_data = supabase.from_(table).select(field).eq("symbol", symbol.upper()).order("created_at", desc=True).limit(1).execute()
        if not db_data.data:
            return f"No record for {symbol} in {table}"
        db_value = db_data.data[0].get(field)

        # Step 2: Alpha Vantage source
        source_data = fetch_alpha_data(f"{symbol} INCOME_STATEMENT")
        if "error" in source_data or "annualReports" not in source_data:
            return "Failed to fetch Alpha Vantage data"

        av_report = source_data["annualReports"][0]
        av_value = av_report.get("ebitda")

        # Step 3: Try local script logic (you can expand later)
        try:
            with open("scripts/income_statement.py") as f:
                code = f.read()
        except FileNotFoundError:
            # Fallback to GitHub
            raw_url = os.getenv("GIT_SCRIPT_URL")  # optional
            code = fetch_script_from_github(raw_url or "")

        # Step 4: Return comparison (replace w/ real logic later)
        return (
            f"{symbol} → {field} comparison:\n"
            f"  Supabase: {db_value}\n"
            f"  Source:   {av_value}\n"
            f"{'✅ MATCH' if str(db_value) == str(av_value) else '❌ MISMATCH'}"
        )
    except Exception as e:
        return f"Tester error: {e}"
