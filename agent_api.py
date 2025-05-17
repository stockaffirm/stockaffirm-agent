from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Reuse all logic from your existing main.py
from main import agent, llm, memory

app = FastAPI()

# CORS setup for frontend (adjust origin in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic schema
class ChatRequest(BaseModel):
    prompt: str

@app.post("/chat")
async def chat(request: ChatRequest):
    prompt = request.prompt.strip()

    if prompt.lower() in ("clear memory", "reset memory"):
        memory.clear()
        return {"response": "🧠 Memory cleared."}

    routing_decision = llm.invoke(
        f"You are StockAgent. Interpret the user question below.\n"
        f"If the user is requesting data from Supabase or Alpha Vantage or our data "
        f"(e.g. 'in our data', 'validate', 'check from our database'), respond only with: USE_AGENT.\n"
        f"If the user just wants general financial knowledge, respond only with: USE_LLM.\n\n"
        f"User: {prompt}"
    ).strip().upper()

    if "USE_AGENT" in routing_decision:
        result = agent.run(prompt)
    else:
        result = llm.invoke(
            f"You are StockAgent, a financial assistant.\n"
            f"Answer this using only your own knowledge.\n"
            f"Clearly say this is not verified using Supabase or Alpha Vantage if applicable.\n\n"
            f"{prompt}"
        )

    return {"response": result}
