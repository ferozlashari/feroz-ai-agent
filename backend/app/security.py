import secrets

from fastapi import Header, HTTPException

from . import config


async def require_key(x_access_key: str = Header(default="")) -> None:
    """Agar .env me ACCESS_KEY set hai to har request par header check hoga."""
    if config.ACCESS_KEY and not secrets.compare_digest(
        x_access_key.encode("utf-8"), config.ACCESS_KEY.encode("utf-8")
    ):
        raise HTTPException(
            status_code=401,
            detail="Access key galat ya missing hai. Settings me sahi key daalo.",
        )
