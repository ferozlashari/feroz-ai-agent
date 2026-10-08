"""Social/job platform connections manage karna - tokens sirf is computer ki local DB me."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from . import connections
from .security import require_key

router = APIRouter(prefix="/api/connections", dependencies=[Depends(require_key)])


@router.get("")
async def list_connections():
    return {"items": connections.status()}


class SaveRequest(BaseModel):
    platform: str
    data: dict


@router.post("")
async def save_connection(req: SaveRequest):
    if req.platform not in connections.PLATFORMS:
        raise HTTPException(400, f"Unknown platform: {req.platform}")
    needed = [f for f, _ in connections.PLATFORMS[req.platform]["fields"]]
    cleaned = {k: str(req.data.get(k, "")).strip() for k in needed}
    if not all(cleaned.values()):
        raise HTTPException(400, "Sab fields bharo.")
    connections.save(req.platform, cleaned)
    return {"ok": True}


@router.delete("/{platform}")
async def delete_connection(platform: str):
    connections.remove(platform)
    return {"ok": True}
