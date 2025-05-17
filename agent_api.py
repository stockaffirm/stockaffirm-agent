from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from agent_core import route_prompt, memory

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class ChatRequest(BaseModel):
    prompt: str

@app.post("/chat")
async def chat(request: ChatRequest):
    if request.prompt.strip().lower() in ("clear memory", "reset memory"):
        memory.clear()
        return {"response": "🧠 Memory cleared."}
    return {"response": route_prompt(request.prompt)}
