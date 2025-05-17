# StockAffirm Agent

This is the agent backend for [StockAffirm](https://stockaffirm.com). It uses LangChain + Ollama (LLaMA 3) to power stock screening, data validation, and Python-based logic analysis via Supabase.

---

## ⚙️ Requirements

- Python 3.8+
- Ubuntu 22.04 recommended (for server deploy)
- Supabase project (used as backend DB)
- [Ollama](https://ollama.com) installed (for LLaMA 3 local inference)

---

## 📦 Folder Structure

```
stockaffirm-agent/
│
├── .venv/                   # Python virtual environment
├── tools/                  # All functional agent modules
├── main.py                 # CLI entrypoint
├── start.sh                # Launch Ollama + agent
├── requirements.txt        # Locked deps
├── requirements-minimal.txt# Editable version
└── .env                    # Supabase + script config
```

---

## 🚀 Setup Instructions (for new server)

### 1. Clone the Repo

```bash
ssh root@85.190.254.222
git clone https://github.com/stockaffirm/stockaffirm-agent.git
cd stockaffirm-agent
```

### 2. Install System Dependencies

```bash
sudo apt update && sudo apt install -y git curl python3-pip python3-venv
```

### 3. Install Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3
```

> 💡 This downloads the `llama3` model. ~8GB.

---

## 🧠 Run the Agent

### 4. Create and Activate Virtual Env

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 5. Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 6. Setup `.env`

Create a `.env` file in the project root:

```
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_KEY=your_supabase_anon_or_service_key
GIT_SCRIPT_URL=https://raw.githubusercontent.com/youruser/yourrepo/branch/path/to/script.py
```

✅ Or use the provided `.env.template` and rename it:
```bash
cp .env.template .env
```

---

## ▶️ 7. Run It

```bash
./start.sh
```

This will:
- Launch Ollama in the background
- Start your LangChain CLI agent

---

## 🌀 Optional (Run with tmux)

```bash
tmux new -s agent ./start.sh
# Ctrl+B D to detach, `tmux attach -t agent` to return
```

---

## 🧠 Tools Available in CLI

- `RunManualCheck Check <field> for <symbol> in <table>`
- `FetchAlphaData AMD OVERVIEW`
- `DescribeScript ...`
- `SuggestStocksBasedOn ...`

---

## 🔒 Tips

- Do **not** commit your actual `.env`
- Add a `.env.template` to share structure safely
- Use `pm2` or `systemd` to daemonize if needed

---

## 📬 Questions?

Contact: `prasadmenon@silcontechlabs.com`  
Agent Source: [github.com/stockaffirm/stockaffirm-agent](https://github.com/stockaffirm/stockaffirm-agent)
