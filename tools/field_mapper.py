import os
from pathlib import Path
from collections import defaultdict

def get_field_to_table_map() -> dict:
    data_dir = Path(__file__).parent.parent / "data"
    output_mapping = defaultdict(list)

    # File type mapping for friendly table names
    file_map = {
        "OVERVIEW": "OVERVIEW",
        "INCOME_STATEMENT": "INCOME_STATEMENT",
        "BALANCE_SHEET": "BALANCE_SHEET",
        "CASH_FLOW": "CASH_FLOW"
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
                        if key and table_name not in output_mapping[key]:
                            output_mapping[key].append(table_name)
            except Exception as e:
                print(f"Failed to parse {file.name}: {e}")

    return dict(output_mapping)

# ✅ For standalone testing
if __name__ == "__main__":
    mapping = get_field_to_table_map()
    for field, sources in mapping.items():
        print(f"{field:<30} -> {', '.join(sources)}")
