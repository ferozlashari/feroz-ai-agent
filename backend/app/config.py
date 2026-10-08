import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _env(name: str, default: str = "") -> str:
    value = os.getenv(name)
    return value.strip() if value and value.strip() else default


def _flag(name: str) -> bool:
    return _env(name, "false").lower() in ("1", "true", "yes", "on")


# ---- chat providers
GROQ_API_KEY = _env("GROQ_API_KEY")
GEMINI_API_KEY = _env("GEMINI_API_KEY")
CEREBRAS_API_KEY = _env("CEREBRAS_API_KEY")
MISTRAL_API_KEY = _env("MISTRAL_API_KEY")
OPENROUTER_API_KEY = _env("OPENROUTER_API_KEY")
HF_API_KEY = _env("HF_API_KEY")
OLLAMA_MODEL = _env("OLLAMA_MODEL")
OLLAMA_VISION_MODEL = _env("OLLAMA_VISION_MODEL")
OLLAMA_URL = _env("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")

# ---- models
GROQ_MODEL = _env("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_VISION_MODEL = _env("GROQ_VISION_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")
GROQ_STT_MODEL = _env("GROQ_STT_MODEL", "whisper-large-v3-turbo")
GEMINI_MODEL = _env("GEMINI_MODEL", "gemini-2.5-flash")
CEREBRAS_MODEL = _env("CEREBRAS_MODEL", "gpt-oss-120b")
MISTRAL_MODEL = _env("MISTRAL_MODEL", "mistral-small-latest")
OPENROUTER_MODEL = _env("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct:free")
HF_CHAT_MODEL = _env("HF_CHAT_MODEL", "meta-llama/Llama-3.3-70B-Instruct")
HF_IMAGE_MODEL = _env("HF_IMAGE_MODEL", "black-forest-labs/FLUX.1-schnell")

# ---- search / security services
TAVILY_API_KEY = _env("TAVILY_API_KEY")
BRAVE_API_KEY = _env("BRAVE_API_KEY")
VT_API_KEY = _env("VT_API_KEY")
NVD_API_KEY = _env("NVD_API_KEY")

# ---- safety
ACCESS_KEY = _env("ACCESS_KEY")
ALLOW_AUTO_EXEC = _flag("ALLOW_AUTO_EXEC")
AUTO_APPROVE_FETCH = _flag("AUTO_APPROVE_FETCH")
ASSISTANT_NAME = _env("ASSISTANT_NAME", "Feroz")

CORS_ORIGINS = [
    o.strip()
    for o in _env("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
    if o.strip()
]

# ---- folders
DATA_DIR = BASE_DIR / "data"
IMAGES_DIR = DATA_DIR / "images"
UPLOADS_DIR = DATA_DIR / "uploads"
DB_PATH = DATA_DIR / "feroz.db"
WORKSPACE_DIR = Path(_env("WORKSPACE_DIR", str(BASE_DIR / "workspace"))).resolve()

for _d in (DATA_DIR, IMAGES_DIR, UPLOADS_DIR, WORKSPACE_DIR):
    _d.mkdir(parents=True, exist_ok=True)
