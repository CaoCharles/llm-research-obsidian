import os
from functools import lru_cache
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

load_dotenv()

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
MAX_SYSTEM_INSTRUCTION_CHARS = int(
    os.getenv("MAX_SYSTEM_INSTRUCTION_CHARS", "120000")
)
DEFAULT_ORIGINS = (
    "https://caocharles.github.io,http://localhost:8000,"
    "http://127.0.0.1:8000"
)
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", DEFAULT_ORIGINS).split(",")
    if origin.strip()
]


def _backend_name() -> str:
    if os.getenv("GEMINI_API_KEY"):
        return "gemini-api"
    if os.getenv("GOOGLE_CLOUD_PROJECT"):
        return "vertex-ai"
    return "unconfigured"


@lru_cache(maxsize=1)
def get_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        return genai.Client(api_key=api_key)

    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    if project:
        return genai.Client(
            vertexai=True,
            project=project,
            location=os.getenv("GOOGLE_CLOUD_LOCATION", "global"),
        )

    raise RuntimeError(
        "Set GEMINI_API_KEY or GOOGLE_CLOUD_PROJECT before starting the service."
    )


app = FastAPI(title="LLM Research Gemini Chatbot", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)


class ChatMessagePart(BaseModel):
    text: str = Field(min_length=1, max_length=100_000)


class ChatMessage(BaseModel):
    role: Literal["user", "model"]
    parts: list[ChatMessagePart]


class ChatRequest(BaseModel):
    history: list[ChatMessage] = Field(default_factory=list, max_length=30)
    message: str = Field(min_length=1, max_length=10_000)
    system_instruction: str | None = None


@app.get("/")
@app.get("/api/health")
def health() -> dict[str, object]:
    backend = _backend_name()
    return {
        "status": "ok" if backend != "unconfigured" else "degraded",
        "service": "Gemini Chatbot Proxy",
        "backend": backend,
        "model": MODEL_NAME,
    }


@app.post("/api/chat")
def chat_endpoint(request: ChatRequest) -> dict[str, str]:
    contents = [
        types.Content(
            role=message.role,
            parts=[types.Part(text=part.text) for part in message.parts],
        )
        for message in request.history
    ]
    contents.append(
        types.Content(role="user", parts=[types.Part(text=request.message)])
    )

    system_instruction = request.system_instruction
    if system_instruction:
        system_instruction = system_instruction[:MAX_SYSTEM_INSTRUCTION_CHARS]

    try:
        response = get_client().models.generate_content(
            model=MODEL_NAME,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2,
            ),
        )
        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")
        return {"text": response.text}
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        # Keep provider details in Cloud Run logs without leaking credentials.
        print(f"Gemini request failed: {type(exc).__name__}: {exc}")
        raise HTTPException(
            status_code=502,
            detail="Gemini is temporarily unavailable.",
        ) from exc
