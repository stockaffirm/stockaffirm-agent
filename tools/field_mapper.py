import os
from pathlib import Path

def get_field_to_table_map() -> dict:
    data_dir = Path(__file__).parent.parent / "data"
    output_mapping = {}
    seen_fields = set()

    # File type mapping for friendly table names
    file_map = {
        "overview": "overview",
        "INCOME_STATEMENT": "income_statement_latest_yearly",
        "BALANCE_SHEET": "balance_sheet_latest_yearly",
        "CASH_FLOW": "cash_flow_latest_yearly"
    }

    for file in data_dir.glob("*.txt"):
        table_name = None
        for key in file_map:
            if key in file.stem.upper():
                table_name = file_map[key]
                break
        if not table_name:
            continue

        with open(file, "r", encoding="utf-8") as f:
            try:
                raw_text = f.read()
                for line in raw_text.splitlines():
                    if ":" in line:
                        key = line.split(":")[0].strip().strip('",').lower()
                        if key and key not in seen_fields:
                            output_mapping[key] = table_name
                            seen_fields.add(key)
            except Exception as e:
                print(f"Failed to parse {file.name}: {e}")

    return output_mapping

# ✅ For standalone testing
if __name__ == "__main__":
    mapping = get_field_to_table_map()
    for field, source in mapping.items():
        print(f"{field:<30} -> {source}")
