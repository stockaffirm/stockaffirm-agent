# StockAffirm Agent (Enhanced Overview)

This repository contains the intelligent agent backend for [StockAffirm](https://stockaffirm.com).  
It leverages LangChain + LLaMA 3 (via Ollama) + Supabase to offer:

- ✅ Conversational stock screening
- ✅ Field-level financial data validation
- ✅ Python script logic introspection
- ✅ Context-aware tool triggering

---

## 💡 What This Agent Does

### Natural Interaction → Smart Execution

1. **You Ask:**  
   > _"What is the free cash flow of AMD in our data?"_

2. **LLaMA 3 Decides:**  
   - Interprets your intent
   - Determines if agent tools should be triggered

3. **Agent Tools Are Used If Needed:**  
   - `FieldMapper` → maps field to table (e.g. `freecashflow` → `cash_flow_latest_yearly`)
   - `FetchAlphaData` → fetches from Alpha Vantage
   - `RunManualCheck` → compares with Supabase data
   - `DescribeScript` → introspects logic from GitHub scripts

---

## 🧠 Intelligent Routing

Prompts are routed by LLaMA using this logic:

- `USE_LLM`: If it can confidently answer using trained knowledge
- `USE_AGENT`: If prompt references “in our data”, “validate”, “Supabase”, etc.

Rephrased prompts (with resolved symbols, fields) are then passed to the agent.

---

## 🔧 Core Agent Tools (in `/tools`)

| Tool | What It Does |
|------|---------------|
| `fetch_alpha_data()` | Fetches financial data from Alpha Vantage |
| `run_manual_check()` | Compares calculated vs fetched vs stored Supabase value |
| `describe_script()` | Extracts logic from GitHub Python script |
| `get_field_to_table_map()` | Dynamically maps fields to source tables from uploaded text files |
| `llm_explainer.py` (optional) | Summarizes financial values in plain English |

---

## 📁 Folder Structure

```
stockaffirm-agent/
├── .venv/                   # Python virtual env
├── tools/                  # Modular tool logic
│   ├── alpha_fetcher.py
│   ├── field_mapper.py
│   ├── tester_tool.py
│   └── ...
├── data/                   # Sample AlphaVantage TXT files
├── main.py                 # LLaMA-agent entrypoint
├── start.sh                # Agent + Ollama launcher
├── requirements.txt
├── .env
└── README.md
```

---

## 🚀 Server Setup

Follow instructions in the previous sections to:
- Clone the repo
- Install system + Python dependencies
- Launch with `./start.sh`

---

## 🧪 Current Status

- ✅ `field_mapper.py` dynamically scans all uploaded sample `.txt` files
- ✅ `.env` provides Supabase + Git access
- ✅ LLaMA 3 via Ollama provides smart intent routing
- ✅ Agent tools are modular and trigger based on rephrased prompt

---

## 📘 What's Next (Suggestions)

- Add `SymbolLookup` tool (company → ticker)
- Add a FastAPI layer to expose this as a web service
- Add output formatting (Markdown, tabular) for CLI and web

---

## 📬 Maintainer

Author: Prasad Menon  
Agent Project: [StockAffirm](https://github.com/stockaffirm/stockaffirm-agent)