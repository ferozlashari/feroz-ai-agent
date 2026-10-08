"""Saare free providers ek hi OpenAI-compatible tareeqe se (auto fallback + vision)."""
import base64
import json
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import httpx
from fastapi import HTTPException

from . import config


def _p(label: str, url: str, key: str, model: str, vision: Optional[str] = None) -> Dict[str, Any]:
    return {"label": label, "url": url, "key": key, "model": model, "vision_model": vision}


PROVIDERS: Dict[str, Dict[str, Any]] = {
    "groq": _p(
        "Groq",
        "https://api.groq.com/openai/v1/chat/completions",
        config.GROQ_API_KEY,
        config.GROQ_MODEL,
        config.GROQ_VISION_MODEL,
    ),
    "gemini": _p(
        "Gemini",
        "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
        config.GEMINI_API_KEY,
        config.GEMINI_MODEL,
        config.GEMINI_MODEL,
    ),
    "cerebras": _p(
        "Cerebras", "https://api.cerebras.ai/v1/chat/completions", config.CEREBRAS_API_KEY, config.CEREBRAS_MODEL
    ),
    "mistral": _p(
        "Mistral",
        "https://api.mistral.ai/v1/chat/completions",
        config.MISTRAL_API_KEY,
        config.MISTRAL_MODEL,
        config.MISTRAL_MODEL,
    ),
    "openrouter": _p(
        "OpenRouter",
        "https://openrouter.ai/api/v1/chat/completions",
        config.OPENROUTER_API_KEY,
        config.OPENROUTER_MODEL,
    ),
    "huggingface": _p(
        "HuggingFace",
        "https://router.huggingface.co/v1/chat/completions",
        config.HF_API_KEY,
        config.HF_CHAT_MODEL,
    ),
    "ollama": _p(
        "Ollama (local)",
        f"{config.OLLAMA_URL}/v1/chat/completions",
        "local" if config.OLLAMA_MODEL else "",
        config.OLLAMA_MODEL,
        config.OLLAMA_VISION_MODEL or None,
    ),
}

# "auto" me is tarteeb se try hota hai; ek fail ho (limit/error) to agla
AUTO_ORDER = ["groq", "gemini", "cerebras", "mistral", "openrouter", "huggingface", "ollama"]
VISION_ORDER = ["gemini", "groq", "mistral", "ollama"]

MAX_IMAGES = 4


class ProviderError(Exception):
    def __init__(self, provider: str, status: int, body: str):
        super().__init__(f"{provider} {status}: {body}")
        self.provider = provider
        self.status = status
        self.body = body


def provider_status() -> Dict[str, bool]:
    return {name: bool(p["key"]) for name, p in PROVIDERS.items()}


def provider_labels() -> Dict[str, str]:
    return {name: p["label"] for name, p in PROVIDERS.items()}


def vision_available() -> List[str]:
    return [n for n in VISION_ORDER if PROVIDERS[n]["key"] and PROVIDERS[n]["vision_model"]]


# ------------------------------------------------------------------ messages


def _image_part(url: str) -> Optional[dict]:
    """/api/uploads/xyz.jpg -> base64 data URL (sirf uploads folder ke andar se)."""
    path = config.UPLOADS_DIR / Path(url).name
    if not path.is_file():
        return None
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    b64 = base64.b64encode(path.read_bytes()).decode()
    return {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}}


def clean_messages(messages: List[dict]) -> Tuple[List[dict], bool]:
    """Frontend ke extra fields hata kar sirf woh rakhta hai jo API samajhti hai."""
    out: List[dict] = []
    has_images = False
    for m in messages:
        role = m.get("role")
        if role not in ("user", "assistant", "tool"):
            continue
        content = str(m.get("content") or "")
        item: Dict[str, Any] = {"role": role, "content": content}
        if role == "user" and m.get("images"):
            parts = [_image_part(u) for u in m["images"][:MAX_IMAGES]]
            parts = [p for p in parts if p]
            if parts:
                has_images = True
                item["content"] = [{"type": "text", "text": content or "Is tasveer ko dekho aur batao."}] + parts
        if role == "assistant" and m.get("tool_calls"):
            item["tool_calls"] = m["tool_calls"]
        if role == "tool":
            item["tool_call_id"] = m.get("tool_call_id") or ""
            if m.get("name"):
                item["name"] = m["name"]
            if not content:
                item["content"] = "(khali natija)"
        out.append(item)
    return out, has_images


def trim_history(messages: List[dict], keep: int = 30) -> List[dict]:
    msgs = list(messages[-keep:])
    # Shuru me tool/adhoora sequence nahi hona chahiye
    while msgs and msgs[0]["role"] != "user":
        msgs.pop(0)
    # Purane bade tool natije chhote kar do (token bachane ke liye)
    cut = max(0, len(msgs) - 8)
    for i in range(cut):
        c = msgs[i].get("content")
        if msgs[i]["role"] == "tool" and isinstance(c, str) and len(c) > 1200:
            msgs[i] = {**msgs[i], "content": c[:1200] + "\n... (purana natija chhota kiya)"}
    return msgs


def _normalize(message: dict) -> dict:
    content = message.get("content") or ""
    if isinstance(content, list):  # kuch providers parts wapas dete hain
        content = "".join(p.get("text", "") for p in content if isinstance(p, dict))
    out: Dict[str, Any] = {"role": "assistant", "content": content}
    calls = message.get("tool_calls")
    if calls:
        norm = []
        for tc in calls:
            fn = tc.get("function", {})
            args = fn.get("arguments", "{}")
            if not isinstance(args, str):
                args = json.dumps(args)
            norm.append(
                {
                    "id": tc.get("id") or f"call_{uuid.uuid4().hex[:12]}",
                    "type": "function",
                    "function": {"name": fn.get("name", ""), "arguments": args or "{}"},
                }
            )
        out["tool_calls"] = norm
    return out


async def _post(provider: str, payload: dict) -> dict:
    p = PROVIDERS[provider]
    headers = {"Authorization": f"Bearer {p['key']}", "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=150) as client:
        r = await client.post(p["url"], json=payload, headers=headers)
    if r.status_code >= 400:
        raise ProviderError(provider, r.status_code, r.text[:400])
    return r.json()


def _order(provider: str, vision: bool) -> List[str]:
    if vision:
        order = vision_available()
        if not order:
            raise HTTPException(
                400,
                "Tasveer samajhne ke liye Gemini ya Groq (ya Mistral/Ollama vision) ki key backend/.env me chahiye.",
            )
        if provider in order:
            order.remove(provider)
            order.insert(0, provider)
        return order

    if provider != "auto" and provider not in PROVIDERS:
        raise HTTPException(400, f"Unknown provider: {provider}")
    wanted = AUTO_ORDER if provider == "auto" else [provider]
    order = [n for n in wanted if PROVIDERS[n]["key"]]
    if not order:
        if provider == "auto":
            raise HTTPException(
                400, "Koi API key set nahi hai. backend/.env me GROQ_API_KEY (ya koi aur free key) daalo."
            )
        raise HTTPException(400, f"{PROVIDERS[provider]['label']} ki key/setting backend/.env me nahi hai.")
    return order


async def chat_completion(
    messages: List[dict],
    provider: str = "auto",
    tools: Optional[List[dict]] = None,
    temperature: float = 0.7,
    vision: bool = False,
) -> Dict[str, Any]:
    order = _order(provider, vision)
    errors: List[str] = []
    for name in order:
        model = PROVIDERS[name]["vision_model"] if vision else PROVIDERS[name]["model"]
        payload: Dict[str, Any] = {"model": model, "messages": messages, "temperature": temperature}
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        for attempt in range(2):
            try:
                data = await _post(name, payload)
                msg = _normalize(data["choices"][0]["message"])
                return {"message": msg, "provider": name, "model": model}
            except ProviderError as e:
                # Llama kabhi kabhi tool call galat format me likhta hai - ek baar dubara try
                if e.status == 400 and "tool_use_failed" in e.body and attempt == 0:
                    continue
                errors.append(f"{PROVIDERS[name]['label']}: {e.status} {e.body[:160]}")
                break
            except (httpx.HTTPError, KeyError, IndexError) as e:
                errors.append(f"{PROVIDERS[name]['label']}: {type(e).__name__} {e}")
                break

    raise HTTPException(502, " | ".join(errors))
