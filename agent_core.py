from langchain_community.llms import Ollama
from langchain.agents import initialize_agent, Tool
from langchain.memory import ConversationBufferMemory

from tools.alpha_fetcher import fetch_alpha_data
from tools.tester_tool import run_manual_check
from tools.logic_tool import evaluate_buyability
from tools.script_describer import describe_script
from tools.stock_picker import suggest_stocks_by_strategy
from tools.field_mapper import get_field_to_table_map

# 🧠 Shared Memory
llm = Ollama(model="llama3")
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

TOOLS = [
    Tool(
        name="FetchAlphaData",
        func=fetch_alpha_data,
        description="Fetch financial data from Alpha Vantage. Format: '<SYMBOL> <FUNCTION>' like 'AAPL OVERVIEW'."
    ),
    Tool(
        name="RunManualCheck",
        func=run_manual_check,
        description="Check if a specific field (like ebitda_1) for a stock symbol in a Supabase table is correctly populated."
    ),
    Tool(
        name="EvaluateBuyability",
        func=evaluate_buyability,
        description="Evaluate whether a stock is buyable based on symbol."
    ),
    Tool(
        name="DescribeScript",
        func=describe_script,
        description="Explain what a Python script does."
    ),
    Tool(
        name="SuggestStocksByStrategy",
        func=suggest_stocks_by_strategy,
        description="Suggest stock symbols based on a strategy like 'undervalued tech stocks'."
    ),
    Tool(
        name="FieldMapper",
        func=lambda _: get_field_to_table_map(),
        description="Returns a dictionary mapping financial fields to Supabase table names."
    ),
]

agent = initialize_agent(
    tools=TOOLS,
    llm=llm,
    agent="zero-shot-react-description",
    verbose=True,
    handle_parsing_errors=True,
    memory=memory,
)

# 🧠 Unified routing function
def route_prompt(prompt: str) -> str:
    prompt = prompt.strip()
    if prompt.lower() in ("clear memory", "reset memory"):
        memory.clear()
        return "🧠 Memory cleared."

    routing_decision = llm.invoke(
        f"You are StockAgent. Interpret the user question below.\n"
        f"If the user is requesting data from Supabase or Alpha Vantage or our data, respond: USE_AGENT.\n"
        f"Otherwise respond: USE_LLM.\n\n"
        f"User: {prompt}"
    ).strip().upper()

    if "USE_AGENT" in routing_decision:
        return agent.run(prompt)
    else:
        return llm.invoke(
            f"You are StockAgent, a financial assistant.\n"
            f"Answer this using only your own knowledge.\n"
            f"Clearly say this is not verified using Supabase or Alpha Vantage if applicable.\n\n"
            f"{prompt}"
        )