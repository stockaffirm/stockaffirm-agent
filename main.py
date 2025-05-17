from dotenv import load_dotenv
load_dotenv()

from langchain_community.llms import Ollama
from langchain.agents import initialize_agent, Tool
from tools.supabase_tool import query_supabase
from tools.logic_tool import evaluate_buyability
from tools.script_describer import describe_script
from tools.tester_tool import run_manual_check
from tools.stock_picker import suggest_stocks_by_strategy
from tools.alpha_fetcher import fetch_alpha_data

llm = Ollama(model="llama3")

TOOLS = [
    Tool(
        name="FetchAlphaData",
        func=fetch_alpha_data,
        description=(
            "Fetch financial data for a public company. Accepts prompts like: \n"
            "- 'Show Apple\'s balance sheet' → AAPL BALANCE_SHEET\n"
            "- 'Get income statement for Microsoft' → MSFT INCOME_STATEMENT\n"
            "- 'Overview of Tesla' → TSLA OVERVIEW\n"
            "Maps company names to known stock tickers using internal logic."
        ),
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
    )
]

agent = initialize_agent(
    tools=TOOLS,
    llm=llm,
    agent="zero-shot-react-description",
    verbose=True,
    handle_parsing_errors=True
)

if __name__ == "__main__":
    while True:
        try:
            prompt = input("\nStockAgent > ")
            if prompt.lower() in ("exit", "quit"):
                print("Goodbye!")
                break

            # If user says "check in our data" or similar, use tools
            if any(phrase in prompt.lower() for phrase in ["check in our data", "verify", "supabase", "runmanual", "manually validate", "fetch alpha", "use our data"]):
                response = agent.run(prompt)
            else:
                # Let LLaMA answer naturally and clearly state its source
                response = llm.invoke(
                    f"You are StockAgent, a financial assistant. "
                    f"Answer the following question using only your pre-trained knowledge. "
                    f"DO NOT use Supabase, Alpha Vantage, or internal tools. "
                    f"If this answer is not verified from live data, state that clearly.\n\n"
                    f"Question: {prompt}"
                )

            print("\n" + str(response))

        except Exception as e:
            print(f"\n\u26a0\ufe0f Agent error: {e}\nRestarting prompt...\n")
