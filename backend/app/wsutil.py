"""Workspace ke helper: safe path, output clip, aur secrets-saaf environment."""
import os
import re
from pathlib import Path

from . import config

_SECRET_NAME = re.compile(r"(KEY|TOKEN|SECRET|PASSWORD|PASSWD|ACCESS|CREDENTIAL)", re.I)


def safe_path(rel: str) -> Path:
    rel = (rel or ".").strip() or "."
    root = config.WORKSPACE_DIR
    target = (root / rel).resolve()
    if target != root and root not in target.parents:
        raise ValueError("Ye path workspace se bahar hai - ijazat nahi.")
    return target


def clip(text: str, limit: int = 8000) -> str:
    if len(text) > limit:
        return text[:limit] + f"\n... (baaqi {len(text) - limit} characters kaat diye)"
    return text


def clean_env() -> dict:
    """Commands ko API keys/secrets nazar na aayen."""
    return {k: v for k, v in os.environ.items() if not _SECRET_NAME.search(k)}
