from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from . import config, llm, tools
from .routes_chat import router as chat_router
from .routes_connectors import router as connectors_router
from .routes_media import router as media_router

app = FastAPI(title=f"{config.ASSISTANT_NAME} - Personal AI Copilot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(media_router)
app.include_router(connectors_router)
app.mount("/api/media", StaticFiles(directory=str(config.IMAGES_DIR)), name="media")
app.mount("/api/uploads", StaticFiles(directory=str(config.UPLOADS_DIR)), name="uploads")


@app.get("/api/status")
async def status():
    return {
        "name": config.ASSISTANT_NAME,
        "providers": llm.provider_status(),
        "provider_labels": llm.provider_labels(),
        "vision_providers": llm.vision_available(),
        "access_key_required": bool(config.ACCESS_KEY),
        "auto_approved_tools": tools.AUTO_APPROVED,
        "image_model": config.HF_IMAGE_MODEL,
        "workspace": str(config.WORKSPACE_DIR),
        "security_tools": bool(config.VT_API_KEY) or True,  # hash/password/CVE hamesha maujood
    }
