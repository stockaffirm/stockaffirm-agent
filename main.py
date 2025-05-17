# stockaffirm-agent/main.py
from dotenv import load_dotenv
load_dotenv()

from langchain.agents import initialize_agent, Tool
from langchain_community.llms import Ollama
from tools.supabase_tool import query_supabase
from tools.logic_tool import evaluate_buyability
from tools.llm_explainer import explain_result
from tools.script_describer import describe_script
from tools.tester_tool import run_manual_check
from tools.stock_picker import suggest_stocks_by_strategy
from tools.alpha_fetcher import fetch_alpha_data


llm = Ollama(model="llama3")

TOOLS = [
    Tool(
        name="QuerySupabase",
        func=query_supabase,
        description="Fetch data from a specific Supabase table by symbol."
    ),
    Tool(
        name="EvaluateBuyability",
        func=evaluate_buyability,
        description="Evaluate if a stock is buyable using logic rules."
    ),
    Tool(
        name="ExplainResult",
        func=explain_result,
        description="Explain logic outcomes in natural language."
    ),
    Tool(
        name="DescribeScript",
        func=describe_script,
        description="Describe what a Python script does."
    ),
    Tool(
        name="RunManualCheck",
        func=run_manual_check,
        description="Verify if a Supabase field is correctly populated using source data and Python logic."
    ),
    Tool(
        name="SuggestStocksByStrategy",
        func=suggest_stocks_by_strategy,
        description="Suggest stocks based on a sector and strategy."
    ),
    Tool(
        name="FetchAlphaData",
        func=fetch_alpha_data,
        description="Fetch Alpha Vantage data. Format: SYMBOL FUNCTION (e.g. AMD OVERVIEW or NVDA CASH_FLOW)"
    )

]

agent = initialize_agent(
    tools=TOOLS,
    llm=llm,
    agent="zero-shot-react-description",
    verbose=True
)

if __name__ == "__main__":
    while True:
        prompt = input("\nStockAgent > ")
        if prompt.lower() in ("exit", "quit"): break
        response = agent.run(prompt)
        print("\n" + response)
