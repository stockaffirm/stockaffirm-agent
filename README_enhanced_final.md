# StockAffirm Agent

This project defines a modular conversational AI agent for intelligent stock data analysis, validation, and reasoning using:

- LangChain agents
- LLaMA 3 via Ollama
- Supabase backend
- Custom field mapping tools
- Intelligent tool routing logic
- Command-line (CLI) + FastAPI support

## 🧠 Agent Capabilities

- Answer questions from its own knowledge (via LLaMA)
- Detect when to fetch data from Supabase or Alpha Vantage
- Use tools like:
  - `FetchAlphaData`: gets financials from AV
  - `RunManualCheck`: verifies if a table field is calculated right
  - `EvaluateBuyability`: applies stock selection rules
  - `FieldMapper`: maps fields to files/tables
  - `DescribeScript`: summarizes what a script does
- Memory: recent prompt context is maintained in session
- Clean modular folder layout (`/tools/`)

---

## 🧪 Dual Execution Modes

You can run the agent:

**In CLI mode:**
```bash
./start_cli.sh
```

**As an API (for use at chat.stockaffirm.com):**
```bash
./start.sh
# or
pm2 start "python3 -m uvicorn main:app --host 0.0.0.0 --port 8501" --name stockaffirm --interpreter none
```

The same `main.py` supports both modes.

---

## 📁 Folder Structure

```
.
├── main.py                 # Unified CLI + API agent
├── agent_api.py (DEPRECATED)
├── tools/                  # All LangChain tools used by agent
│   ├── alpha_fetcher.py
│   ├── field_mapper.py
│   ├── logic_tool.py
│   └── tester_tool.py
├── start.sh                # Web server mode
├── start_cli.sh            # CLI terminal mode
├── requirements.txt
├── .env
├── README.md
```

---

## 🌍 Live Deployment Info

- **Server IP**: `http://85.190.254.222`
- **API Endpoint**: `http://85.190.254.222:8501/chat`
- **Test locally**: `curl -X POST http://localhost:8501/chat -H "Content-Type: application/json" -d '{"prompt": "Where is EBITDA in our data?"}'`
- **Deployment method**: PM2 (Process Manager for Node/Python)
- **Agent process**: `pm2 start "python3 -m uvicorn main:app --host 0.0.0.0 --port 8501" --name stockaffirm --interpreter none`

---

## 🔁 Auto-Deploy via GitHub Webhook

- `deploy-hook.js` runs on port **9000** via PM2:
  ```bash
  pm2 start deploy-hook.js --name deploy-hook
  ```
- GitHub Webhook sends POST to:
  ```
  http://chat.stockaffirm.com/webhook
  ```
- Hook runs:
  ```bash
  git pull && pm2 restart stockaffirm
  ```
- Nginx reverse proxy forwards `/webhook` to `localhost:9000`

---

## 🛠 Fixes Applied During Setup

- ✅ Fixed `pm2` treating `uvicorn` as Node.js:
  - Used: `--interpreter none`
- ✅ Installed missing `dotenv` inside `.venv`:
  ```bash
  pip install python-dotenv
  ```
- ✅ Installed `uvicorn` inside `.venv`
- ✅ Confirmed `main.py` exposes `app = FastAPI()`
- ✅ CLI still supported via `start_cli.sh`