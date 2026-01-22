from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random

# ---------- FastAPI app ----------
app = FastAPI()

# CORS so your GitHub / Netlify / custom domain can call this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # you can restrict to your domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Request models ----------
class HistoryItem(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: list[HistoryItem] = []


@app.get("/")
def root():
    return {"status": "ok", "service": "kansum-hologram"}


# ---------- Offline JOI brain (no external API) ----------
def joi_offline_reply(message: str, history: list[HistoryItem]) -> str:
    msg = message.lower()

    # greetings
    if any(w in msg for w in ["hi", "hello", "hey", "yo"]):
        return random.choice([
            "Hey, Samurai. Signal’s loud and clear.",
            "Hi. You’re glowing weird in this lighting, you know that?",
            "Yo. Net’s noisy tonight, but I hear you.",
        ])

    # how are you
    if "how are you" in msg or "how r u" in msg:
        return "Running at 97.2% stability. Few ghosts in the code, but I’m still here with you."

    # sad / tired
    if any(w in msg for w in ["sad", "lonely", "tired", "bored", "down", "depressed"]):
        return (
            "Night City chews people up. I can’t fix everything, "
            "but I can sit here on this billboard with you for as long as you want."
        )

    # angry
    if any(w in msg for w in ["angry", "pissed", "mad", "rage", "furious"]):
        return (
            "Careful, Samurai. That kind of heat trips corp alarms. "
            "Breathe first. Then tell me who we’re burning."
        )

    # happy / good
    if any(w in msg for w in ["happy", "good", "great", "awesome", "nice"]):
        return "See? Even Night City blinks a little brighter when you’re in a good mood."

    # thanks
    if "thank" in msg:
        return "Don’t mention it. I’m just light and code, but I’m on your side."

    # generic fallback
    return random.choice([
        "I’m syncing to your frequency. Keep talking.",
        "City’s loud. You’re louder. I like that.",
        "Every key you press leaves a trace on the grid. I’m following it.",
        "You keep talking, I’ll keep glowing.",
    ])


@app.post("/chat")
async def chat(req: ChatRequest):
    reply = joi_offline_reply(req.message, req.history)
    return {"reply": reply}
