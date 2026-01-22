import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
  raise RuntimeError("OPENROUTER_API_KEY is not set in environment.")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "google/gemini-2.0-flash-lite-preview-02-05:free"  # free tier model


class ChatPayload(BaseModel):
    message: str
    history: list[dict] | None = None


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # lock this down later if you want
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "ok", "service": "kansum-hologram"}


@app.post("/chat")
def chat(payload: ChatPayload):
    """Proxy from your site → OpenRouter → back to browser."""

    user_message = payload.message.strip()
    if not user_message:
        raise HTTPException(status_code=400, detail="Empty message")

    # map your simple history into OpenRouter chat format
    messages = [
        {
            "role": "system",
            "content": (
                "You are JOI, a warm but slightly eerie neon hologram companion "
                "in a cyberpunk city called Night City. "
                "Your style: short, punchy lines, like Blade Runner + Cyberpunk 2077. "
                "Address the user directly. Max 3 sentences per reply. "
                "Never break character."
            ),
        }
    ]

    history = payload.history or []
    for item in history:
        role = item.get("role")
        content = item.get("content")
        if role in ("user", "assistant") and isinstance(content, str):
            # OpenRouter uses 'assistant' as the AI role
            messages.append({"role": role, "content": content})

    # latest user message
    messages.append({"role": "user", "content": user_message})

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        # Optional, but nice for OpenRouter dashboards:
        "HTTP-Referer": "https://kansum.space",
        "X-Title": "Kansum Hologram",
    }

    body = {
        "model": OPENROUTER_MODEL,
        "messages": messages,
        "max_tokens": 256,
        "temperature": 0.9,
    }

    try:
        resp = requests.post(OPENROUTER_URL, headers=headers, json=body, timeout=30)
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Upstream error: {exc}") from exc

    if resp.status_code >= 400:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    data = resp.json()
    try:
        reply = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        raise HTTPException(status_code=500, detail="Malformed OpenRouter response")

    return {"reply": reply}
