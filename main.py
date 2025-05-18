from dotenv import load_dotenv
load_dotenv()

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from langchain_community.llms import Ollama
from langchain.agents import initialize_agent, Tool
from langchain.memory import ConversationBufferMemory
from tools.supabase_tool import query_supabase
from tools.logic_tool import evaluate_buyability
from tools.script_describer import describe_script
from tools.tester_tool import run_manual_check
from tools.stock_picker import suggest_stocks_by_strategy
from tools.alpha_fetcher import fetch_alpha_data
from tools.field_mapper import get_field_to_table_map

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import AsyncGenerator
import asyncio

llm = Ollama(model="llama3")
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

TOOLS = [
    Tool(
        name="FetchAlphaData",
        func=fetch_alpha_data,
        description=(
            "Fetch Alpha Vantage financial data for a company using a symbol"
            "MUST check OVERVIEW first in case of to know specifically in which FUNCTION is the field"
            "The output received should be interpreted. Field names will not be exact but financial acumen be used"
            "Required format: '<SYMBOL> <FUNCTION>', for example:\n"
            "- 'AAPL OVERVIEW'\n"
            "- 'AMD INCOME_STATEMENT'\n"
            "- 'TSLA CASH_FLOW'\n"
            "Do NOT call this tool without specifying both a symbol and one of: OVERVIEW, INCOME_STATEMENT, BALANCE_SHEET, CASH_FLOW."
        )
    ),
    Tool(
        name="RunManualCheck",
        func=run_manual_check,
        description="Check if a specific field (like ebitda_1) for a stock symbol (e.g. AMD) in a Supabase table is correctly populated. Format: Check <field> for <symbol> in <table>.",
    ),
    Tool(
        name="EvaluateBuyability",
        func=evaluate_buyability,
        description="Evaluate whether a stock is buyable based on symbol."
    ),
    Tool(
        name="DescribeScript",
        func=describe_script,
        description="Explain what a Python script does. Paste script as input."
    ),
    Tool(
        name="SuggestStocksByStrategy",
        func=suggest_stocks_by_strategy,
        description="Suggest stock symbols based on a high-level strategy like 'undervalued tech stocks'."
    ),
    Tool(
        name="FieldMapper",
        func=lambda _: get_field_to_table_map(),
        description=(
            "Use this tool if the question involves locating where a specific financial field "
            "If you already located the field in Alphavantage, do not call this tool"
            "(e.g., 'freecashflow', 'ebitda', 'marketcapitalization') is stored in Alphavantage APIs. "
            "This tool would suffice the requirement to check where a field existing in alphavantage or API"
            "This tool MUST be used when the question includes phrases like 'in our data', 'from our database', or "
            "'based on our records'. It returns a dictionary mapping field names to API type or table names."
            "The output received should be interpreted. Field names will not be exact but financial acumen be used"
            "match the input or field requested to the closest in the output of this tool"
            "ALWAYS follow with:\n"
            "Action: FieldMapper\n"
            "Action Input: 'fieldname'\n"
            "Then use the result to continue tool selection or validation."
        )
    )
]

agent = initialize_agent(
    tools=TOOLS,
    llm=llm,
    agent="zero-shot-react-description",
    verbose=True,
    handle_parsing_errors=True,
    memory=memory
)

def route_prompt(prompt: str) -> str:
    prompt = prompt.strip()
    if prompt.lower() in ("clear memory", "reset memory"):
        memory.clear()
        return "Memory cleared."

    routing_decision = llm.invoke(
        f"You are StockAgent. Interpret the user question below.\n"
        f"If the user is requesting data from Supabase or Alpha Vantage or our data, respond only with: USE_AGENT.\n"
        f"you have to interpret each input and use your financial wisdom and reach out to the agents with proper information."
        f"If it's general financial knowledge, respond only with: USE_LLM.\n\n"
        f"User: {prompt}"
    ).strip().upper()

    if "USE_AGENT" in routing_decision:
        return agent.invoke(prompt)
    return llm.invoke(
        f"You are StockAgent, a financial assistant.\n"
        f"Answer this using only your own knowledge.\n"
        f"Clearly state if this is not verified using Supabase or Alpha Vantage.\n\n"
        f"{prompt}"
    )

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/", response_class=HTMLResponse)
async def root():
    return HTMLResponse(content="""
    <html><head><title>StockAffirm Agent</title></head>
    <body style="font-family:sans-serif;padding:2rem;">
        <h2>Welcome to StockAffirm Agent</h2>
        <p>Visit <a href='/chat'>/chat</a> to interact.</p>
    </body></html>
    """)

@app.get("/chat", response_class=HTMLResponse)
async def chat_form():
    return HTMLResponse(content="""
    <html>
    <head>
      <title>Chat</title>
      <script>
        function showLoading() {
          document.getElementById("status").innerText = "🧠 Checking... please wait";
        }
      </script>
    </head>
    <body style="font-family:sans-serif;padding:2rem;">
        <h2>StockAffirm Agent</h2>
        <form method="post" action="/chat" onsubmit="showLoading()">
            <input type="text" name="prompt" style="width:60%;padding:0.5rem;" placeholder="Ask a question..." />
            <button type="submit" style="padding:0.5rem 1rem;">Submit</button>
        </form>
        <p id="status" style="margin-top:1rem;font-style:italic;"></p>
    </body>
    </html>
    """)

@app.post("/chat", response_class=StreamingResponse)
async def stream_chat(request: Request):
    form = await request.form()
    prompt = form.get("prompt", "")

    async def stream_response() -> AsyncGenerator[bytes, None]:
        yield b"<html><body style='font-family:sans-serif;padding:2rem;'>"
        yield f"<h2>StockAffirm Agent</h2><p><b>Prompt:</b> {prompt}</p>".encode()
        yield b"<p><b>Response:</b><pre style='white-space:pre-wrap;background:#f4f4f4;padding:1rem;'>"

        try:
            yield b"Checking...\n"
            for _ in range(3):
                await asyncio.sleep(5)
                yield b"Still checking...\n"

            result = route_prompt(prompt)
            for line in result.splitlines():
                yield (line + "\n").encode()
                await asyncio.sleep(0.05)
        except Exception as e:
            yield f"Error: {str(e)}".encode()

        yield b"</pre></p></body></html>"

    return StreamingResponse(stream_response(), media_type="text/html")

if __name__ == "__main__":
    while True:
        try:
            prompt = input("\nStockAgent > ")
            if prompt.lower() in ("exit", "quit"):
                print("Goodbye!")
                break
            print(route_prompt(prompt))
        except Exception as e:
            print(f"\nAgent error: {e}\nRestarting...\n")
