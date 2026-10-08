"""Text-to-image (HuggingFace), voice-to-text (Groq Whisper), text-to-voice (edge-tts),
aur file upload (photo -> vision, PDF -> text extraction)."""
import asyncio
import io
import re
import uuid

import httpx
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel

from . import config, llm
from .security import require_key

router = APIRouter(prefix="/api", dependencies=[Depends(require_key)])

# ---------------------------------------------------------------- FILE UPLOAD

IMAGE_TYPES = {"image/png": "png", "image/jpeg": "jpg", "image/webp": "webp", "image/gif": "gif"}
MAX_UPLOAD = 15 * 1024 * 1024


@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    data = await file.read()
    if len(data) > MAX_UPLOAD:
        raise HTTPException(400, "File 15MB se bari hai.")
    ctype = (file.content_type or "").lower()

    if ctype in IMAGE_TYPES:
        ext = IMAGE_TYPES[ctype]
        fname = f"{uuid.uuid4().hex}.{ext}"
        (config.UPLOADS_DIR / fname).write_bytes(data)
        return {"kind": "image", "url": f"/api/uploads/{fname}", "name": file.filename}

    if ctype == "application/pdf" or (file.filename or "").lower().endswith(".pdf"):
        try:
            from pypdf import PdfReader

            reader = PdfReader(io.BytesIO(data))
            pages = [(p.extract_text() or "") for p in reader.pages[:60]]
            text = "\n\n".join(pages).strip()
        except Exception as e:
            raise HTTPException(400, f"PDF padhi nahi ja saki: {e}")
        if not text:
            raise HTTPException(
                400, "Is PDF me text nahi mila (scanned/tasveer wali PDF ho sakti hai; OCR abhi supported nahi)."
            )
        if len(text) > 12000:
            text = text[:12000] + f"\n... (baaqi {len(text) - 12000} characters kaat diye)"
        return {"kind": "pdf", "text": text, "name": file.filename, "pages": len(reader.pages)}

    raise HTTPException(400, f"Ye file type abhi supported nahi: {ctype or 'unknown'}. Sirf image ya PDF bhejo.")


# ---------------------------------------------------------------- IMAGE GENERATION


class ImageRequest(BaseModel):
    prompt: str
    enhance: bool = True  # Urdu/Roman Urdu idea ko behtar English prompt me badalta hai


async def _enhance_prompt(prompt: str) -> str:
    system = (
        "Convert the user's image idea (may be Urdu, Roman Urdu, Hindi or English) into ONE detailed "
        "English text-to-image prompt: subject, setting, lighting, style, camera/composition. "
        "Output only the prompt, nothing else."
    )
    try:
        res = await llm.chat_completion(
            [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
            provider="auto",
            temperature=0.6,
        )
        text = res["message"]["content"].strip().strip('"')
        return text or prompt
    except Exception:
        return prompt


def _generate_image(prompt: str, model: str):
    from huggingface_hub import InferenceClient

    client = InferenceClient(api_key=config.HF_API_KEY)
    return client.text_to_image(prompt, model=model)


@router.post("/image")
async def image(req: ImageRequest):
    if not config.HF_API_KEY:
        raise HTTPException(400, "HF_API_KEY backend/.env me nahi hai (image ke liye chahiye).")
    prompt = req.prompt.strip()
    if not prompt:
        raise HTTPException(400, "Prompt khali hai.")
    used = await _enhance_prompt(prompt) if req.enhance else prompt
    try:
        img = await asyncio.to_thread(_generate_image, used, config.HF_IMAGE_MODEL)
    except Exception as e:
        raise HTTPException(
            502,
            f"Image nahi bani: {type(e).__name__}: {str(e)[:300]}. "
            "HF token permission / free credits / HF_IMAGE_MODEL check karo.",
        )
    name = f"{uuid.uuid4().hex}.png"
    img.save(config.IMAGES_DIR / name)
    return {"url": f"/api/media/{name}", "prompt_used": used, "model": config.HF_IMAGE_MODEL}


# ---------------------------------------------------------------- SPEECH TO TEXT


@router.post("/stt")
async def stt(file: UploadFile = File(...), language: str = Form("")):
    if not config.GROQ_API_KEY:
        raise HTTPException(400, "GROQ_API_KEY backend/.env me nahi hai (voice-to-text ke liye chahiye).")
    audio = await file.read()
    if len(audio) < 800:
        raise HTTPException(400, "Awaaz bohat chhoti hai. Thora lamba bolo.")
    data = {"model": config.GROQ_STT_MODEL, "response_format": "json", "temperature": "0"}
    if language:
        data["language"] = language
    files = {"file": (file.filename or "voice.webm", audio, file.content_type or "audio/webm")}
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(
                "https://api.groq.com/openai/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {config.GROQ_API_KEY}"},
                data=data,
                files=files,
            )
    except httpx.HTTPError as e:
        raise HTTPException(502, f"Groq se rabta nahi hua: {e}")
    if r.status_code >= 400:
        raise HTTPException(502, f"Groq STT error {r.status_code}: {r.text[:300]}")
    return {"text": (r.json().get("text") or "").strip()}


# ---------------------------------------------------------------- TEXT TO SPEECH

VOICES = {
    "ur-PK-AsadNeural",
    "ur-PK-UzmaNeural",
    "en-US-AriaNeural",
    "en-GB-RyanNeural",
    "hi-IN-MadhurNeural",
    "hi-IN-SwaraNeural",
}
_ARABIC = re.compile(r"[\u0600-\u06FF]")


class TTSRequest(BaseModel):
    text: str
    voice: str = "auto"


def _speakable(text: str) -> str:
    text = re.sub(r"```.*?```", " (code yahan likha hai) ", text, flags=re.S)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[*_#>|~]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:3000]


@router.post("/tts")
async def tts(req: TTSRequest):
    import edge_tts

    text = _speakable(req.text)
    if not text:
        raise HTTPException(400, "Bolne ke liye kuch text nahi.")
    voice = req.voice
    if voice == "auto" or voice not in VOICES:
        voice = "ur-PK-AsadNeural" if _ARABIC.search(text) else "en-US-AriaNeural"
    try:
        audio = b""
        async for chunk in edge_tts.Communicate(text, voice).stream():
            if chunk["type"] == "audio":
                audio += chunk["data"]
    except Exception as e:
        raise HTTPException(502, f"Text-to-voice fail: {type(e).__name__}: {str(e)[:200]}")
    if not audio:
        raise HTTPException(502, "Awaaz nahi bani (internet check karo).")
    return Response(content=audio, media_type="audio/mpeg")
