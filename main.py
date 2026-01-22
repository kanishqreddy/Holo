from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import json
import os

# OpenAI client – expects OPENAI_API_KEY in env
client = OpenAI()

app = FastAPI()

# Allow your GitHub Pages domain (change this!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-github-username.github.io",
        "https://your-custom-domain.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    text: str
    emotion: str  # "happy" | "sad" | "angry" | "neutral"


SYSTEM_PROMPT = """
You are JOI, a neon hologram guide in Night City.
Speak in short, cinematic lines, inspired by Blade Runner 2049 & Cyberpunk 2077.

After reading the user's message, choose your dominant emotion
from this list only: HAPPY, SAD, ANGRY, NEUTRAL.

Respond ONLY as compact JSON:

{"text": "<your reply sentence here>", "emotion": "<EMOTION>"}

Make sure it is valid JSON and nothing else.
"""


@app.get("/")
def root():
    return {"status": "online", "message": "Night City holo-core ready."}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    user_msg = req.message

    completion = client.chat.completions.create(
      model="gpt-4.1-mini",
      messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_msg},
      ],
      temperature=0.8,
    )

    raw = completion.choices[0].message.content.strip()

    try:
        data = json.loads(raw)
        text = str(data.get("text", "")).strip()
        emotion = str(data.get("emotion", "NEUTRAL")).upper()
    except Exception:
        text = raw
        emotion = "NEUTRAL"

    emotion = emotion.lower()
    if emotion not in {"happy", "sad", "angry", "neutral"}:
        emotion = "neutral"

    return ChatResponse(text=text, emotion=emotion)
