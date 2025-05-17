from dotenv import load_dotenv
load_dotenv()

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

llm = Ollama(model="llama3")

# 🧠 Session memory (persists until restart or cleared)
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

TOOLS = [
    Tool(
        name="FetchAlphaData",
        func=fetch_alpha_data,
        description=(
            "Fetch Alpha Vantage financial data for a company using a symbol and report type. "
            "MUST check OVERVIEW first in case of any doubts and no specificality in input function"
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
            "(e.g., 'freecashflow', 'ebitda', 'marketcapitalization') is stored in Alphavantage APIs. "
            "This tool MUST be used when the question includes phrases like 'in our data', 'from our database', or "
            "'based on our records'. It returns a dictionary mapping field names to API type or table names."
            "The output received should be interpreted. Field names will not be exact but financial acumen be used"
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
    memory=memory  # 🧠 Add memory support
)

if __name__ == "__main__":
    while True:
        try:
            prompt = input("\nStockAgent > ")
            if prompt.lower() in ("exit", "quit"):
                print("Goodbye!")
                break

            if prompt.lower() in ("clear memory", "reset memory"):
                memory.clear()
                print("🧠 Memory cleared.")
                continue

            # Step 1: Ask LLaMA to classify intent
            routing_decision = llm.invoke(
                f"You are StockAgent. Interpret the user question below.\n"
                f"If the user is requesting data from Supabase or Alpha Vantage or our data "
                f"(e.g. 'in our data', 'validate', 'check from our database'), respond only with: USE_AGENT.\n"
                f"If the user just wants general financial knowledge, respond only with: USE_LLM.\n\n"
                f"User: {prompt}"
            ).strip().upper()

            # Step 2: Route based on LLaMA's output
            if "USE_AGENT" in routing_decision:
                print("using USE_AGENT")
                response = agent.run(prompt)
            else:
                print("not using USE_AGENT")
                response = llm.invoke(
                    f"You are StockAgent, a financial assistant.\n"
                    f"Answer this using only your own knowledge.\n"
                    f"Clearly say this is not verified using Supabase or Alpha Vantage if applicable.\n\n"
                    f"{prompt}"
                )

            print("\n" + str(response))

        except Exception as e:
            print(f"\n⚠️ Agent error: {e}\nRestarting prompt...\n")

# === Shared Routing Function (used by API too) ===
def route_prompt(prompt: str) -> str:
    prompt = prompt.strip()
    if prompt.lower() in ("clear memory", "reset memory"):
        memory.clear()
        return "🧠 Memory cleared."

    routing_decision = llm.invoke(
        f"""You are StockAgent. Interpret the user question below.
If the user is requesting data from Supabase or Alpha Vantage or our data 
(e.g. 'in our data', 'validate', 'check from our database'), respond only with: USE_AGENT.
If the user just wants general financial knowledge, respond only with: USE_LLM.

User: {prompt}"""
    ).strip().upper()

    if "USE_AGENT" in routing_decision:
        return agent.run(prompt)
    else:
        return llm.invoke(
            f"""You are StockAgent, a financial assistant.
Answer this using only your own knowledge.
Clearly say this is not verified using Supabase or Alpha Vantage if applicable.

{prompt}"""
        )

# === Optional FastAPI App ===
try:
    from fastapi import FastAPI
    from pydantic import BaseModel
    from fastapi.middleware.cors import CORSMiddleware

    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    class ChatRequest(BaseModel):
        prompt: str

    @app.post("/chat")
    async def chat(request: ChatRequest):
        return {"response": route_prompt(request.prompt)}

except ImportError:
    app = None  # FastAPI is optional; ignore if not installed