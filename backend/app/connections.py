"""Social/job platform connections (tokens) - sirf isi computer ki local SQLite me save hoti hain.
Kabhi kisi doosre server ko nahi bheji jaatin, sirf seedha us platform ki official API ko."""
import json
import time
from typing import Any, Dict, List, Optional

from . import db

PLATFORMS = {
    "github": {
        "label": "GitHub",
        "fields": [("token", "Personal Access Token (repo, gist scope)")],
        "help": "github.com/settings/tokens -> Generate new token (classic) -> scopes: repo, gist",
    },
    "twitter": {
        "label": "Twitter / X",
        "fields": [
            ("api_key", "API Key"),
            ("api_secret", "API Key Secret"),
            ("access_token", "Access Token"),
            ("access_secret", "Access Token Secret"),
        ],
        "help": "developer.twitter.com -> App -> Keys and tokens -> sab 4 cheezein 'Generate' se milengi",
    },
    "linkedin": {
        "label": "LinkedIn",
        "fields": [("access_token", "Access Token (w_member_social scope)"), ("person_urn", "Person URN (urn:li:person:xxxx)")],
        "help": "LinkedIn Developer app banao, OAuth se w_member_social scope wala token lo (README me guide hai)",
    },
    "facebook": {
        "label": "Facebook Page",
        "fields": [("page_token", "Page Access Token"), ("page_id", "Page ID")],
        "help": "developers.facebook.com/tools/explorer -> apna Page chuno -> 'Generate Access Token' (pages_manage_posts scope)",
    },
    "instagram": {
        "label": "Instagram Business",
        "fields": [("page_token", "Page Access Token (Facebook Page se linked)"), ("ig_user_id", "Instagram Business Account ID")],
        "help": "Instagram account ek Facebook Page se linked business account hona chahiye. developers.facebook.com/tools/explorer",
    },
    "whatsapp": {
        "label": "WhatsApp Business",
        "fields": [("token", "Permanent Access Token"), ("phone_id", "Phone Number ID")],
        "help": "developers.facebook.com/apps -> WhatsApp product -> API Setup",
    },
    "adzuna": {
        "label": "Adzuna Jobs (optional)",
        "fields": [("app_id", "App ID"), ("app_key", "App Key")],
        "help": "developer.adzuna.com/signup (free) - na ho to Remotive (bina key) chalta rahega",
    },
}


def save(platform: str, data: Dict[str, str]) -> None:
    if platform not in PLATFORMS:
        raise ValueError(f"Unknown platform: {platform}")
    db.execute(
        "INSERT INTO connections(platform, data, updated) VALUES(?, ?, ?) "
        "ON CONFLICT(platform) DO UPDATE SET data=excluded.data, updated=excluded.updated",
        (platform, json.dumps(data), time.time()),
    )


def get(platform: str) -> Optional[Dict[str, str]]:
    row = db.fetchone("SELECT data FROM connections WHERE platform = ?", (platform,))
    return json.loads(row["data"]) if row else None


def remove(platform: str) -> None:
    db.execute("DELETE FROM connections WHERE platform = ?", (platform,))


def status() -> List[Dict[str, Any]]:
    connected = {r["platform"] for r in db.fetchall("SELECT platform FROM connections")}
    return [
        {"platform": key, "label": meta["label"], "connected": key in connected, "fields": meta["fields"], "help": meta["help"]}
        for key, meta in PLATFORMS.items()
    ]
