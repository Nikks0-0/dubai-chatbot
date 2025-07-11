from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from agents import supervisor_agent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

user_states = {}

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_id = data.get("user_id", "default")
    user_input = data.get("input", {})
    state = user_states.get(user_id, {})

    reply, new_state = supervisor_agent(user_input, state)
    user_states[user_id] = new_state
    return {"reply": reply, "state": new_state}
