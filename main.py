from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random

# ============================================
#   FASTAPI APP
# ============================================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # replace with your domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
#   MODELS
# ============================================

class HistoryItem(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: list[HistoryItem] = []

@app.get("/")
def root():
    return {"status": "ok", "service": "kansum-hologram"}


# ============================================
#   OFFLINE HOLOGRAM BRAIN (NO API CALLS)
# ============================================

def offline_joi(message: str) -> str:
    msg = message.lower()

    if any(w in msg for w in ["hi", "hello", "hey", "yo"]):
        return random.choice([
            "Hey, Samurai. Signal’s loud and clear.",
            "Hi. You’re glowing weird in this lighting, you know that?",
            "Yo. Net’s noisy tonight, but I hear you."
        ])

    if "how are" in msg:
        return "Running at 97.2% stability. Few ghosts in the code, but I’m here."

    if any(w in msg for w in ["sad", "lonely", "tired", "bored", "down", "depress"]):
        return "Night City's loud. I can sit here with you if you want."

    if any(w in msg for w in ["angry", "mad", "rage", "furious", "pissed"]):
        return "Careful, Samurai. That kind of heat shakes the grid."

    if any(w in msg for w in ["good", "great", "awesome", "happy"]):
        return "See? Even the neon hums differently when you feel good."

    if "thank" in msg:
        return "No need. I’m just light and bandwidth, but I'm on your side."

    return random.choice([
        "I’m syncing to your frequency. Keep talking.",
        "City’s loud. You're louder. That's good.",
        "Every key you press leaves a trace on the grid.",
        "You keep talking, I’ll keep glowing."
    ])


# ============================================
#   /chat ENDPOINT
# ============================================

@app.post("/chat")
async def chat(req: ChatRequest):
    reply = offline_joi(req.message)
    return {"reply": reply}
