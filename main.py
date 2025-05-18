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
    Tool("FetchAlphaData", fetch_alpha_data, "Fetch financials via Alpha Vantage."),
    Tool("RunManualCheck", run_manual_check, "Check if a field is correctly calculated in Supabase."),
    Tool("EvaluateBuyability", evaluate_buyability, "Apply stock selection rules."),
    Tool("DescribeScript", describe_script, "Explain Python script logic."),
    Tool("SuggestStocksByStrategy", suggest_stocks_by_strategy, "Suggest stocks based on strategy."),
    Tool("FieldMapper", lambda _: get_field_to_table_map(), "Map fields to data tables or APIs.")
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
