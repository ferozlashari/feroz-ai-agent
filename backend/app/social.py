"""Har platform ki official API se post/message bhejta hai - sirf jab user ne khud
Settings > Connections me apna token diya ho. Koi bhi function unauthorized access nahi karta."""
from typing import Optional

import httpx

from . import connections, oauth1

UA = "Mozilla/5.0 (compatible; FerozAgent/1.0)"


def _need(platform: str) -> dict:
    data = connections.get(platform)
    if not data:
        label = connections.PLATFORMS[platform]["label"]
        raise ValueError(f"{label} connect nahi hai. Settings > Connections me token daalo.")
    return data


# ------------------------------------------------------------------ GitHub


def github_create_issue(repo: str, title: str, body: str = "") -> str:
    d = _need("github")
    repo = repo.strip().strip("/")
    r = httpx.post(
        f"https://api.github.com/repos/{repo}/issues",
        json={"title": title, "body": body},
        headers={"Authorization": f"Bearer {d['token']}", "Accept": "application/vnd.github+json", "User-Agent": UA},
        timeout=25,
    )
    if r.status_code >= 400:
        raise ValueError(f"GitHub error {r.status_code}: {r.text[:300]}")
    j = r.json()
    return f"Issue ban gaya: {j.get('html_url')}"


def github_create_gist(description: str, filename: str, content: str, public: bool = False) -> str:
    d = _need("github")
    r = httpx.post(
        "https://api.github.com/gists",
        json={"description": description, "public": public, "files": {filename: {"content": content}}},
        headers={"Authorization": f"Bearer {d['token']}", "Accept": "application/vnd.github+json", "User-Agent": UA},
        timeout=25,
    )
    if r.status_code >= 400:
        raise ValueError(f"GitHub error {r.status_code}: {r.text[:300]}")
    j = r.json()
    return f"Gist ban gaya: {j.get('html_url')}"


def github_list_repos() -> str:
    d = _need("github")
    r = httpx.get(
        "https://api.github.com/user/repos",
        params={"per_page": 20, "sort": "updated"},
        headers={"Authorization": f"Bearer {d['token']}", "Accept": "application/vnd.github+json", "User-Agent": UA},
        timeout=25,
    )
    if r.status_code >= 400:
        raise ValueError(f"GitHub error {r.status_code}: {r.text[:300]}")
    repos = r.json()
    if not repos:
        return "Koi repo nahi mila."
    return "\n".join(f"- {x['full_name']} ({'private' if x['private'] else 'public'})" for x in repos)


# ------------------------------------------------------------------ Twitter / X


def twitter_post(text: str) -> str:
    d = _need("twitter")
    url = "https://api.twitter.com/2/tweets"
    header = oauth1.build_header("POST", url, d["api_key"], d["api_secret"], d["access_token"], d["access_secret"])
    r = httpx.post(url, json={"text": text}, headers={"Authorization": header, "Content-Type": "application/json"}, timeout=25)
    if r.status_code >= 400:
        raise ValueError(f"Twitter/X error {r.status_code}: {r.text[:300]}")
    j = r.json().get("data", {})
    tid = j.get("id", "")
    return f"Tweet ho gaya (id: {tid})."


# ------------------------------------------------------------------ LinkedIn


def linkedin_post(text: str) -> str:
    d = _need("linkedin")
    urn = d.get("person_urn", "").strip()
    if not urn:
        raise ValueError("LinkedIn Person URN missing hai (Settings > Connections).")
    body = {
        "author": urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }
    r = httpx.post(
        "https://api.linkedin.com/v2/ugcPosts",
        json=body,
        headers={
            "Authorization": f"Bearer {d['access_token']}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        },
        timeout=25,
    )
    if r.status_code >= 400:
        raise ValueError(f"LinkedIn error {r.status_code}: {r.text[:300]}")
    return f"LinkedIn par post ho gaya (id: {r.headers.get('x-restli-id', 'ok')})."


# ------------------------------------------------------------------ Facebook Page


def facebook_post(message: str, link: Optional[str] = None) -> str:
    d = _need("facebook")
    payload = {"message": message, "access_token": d["page_token"]}
    if link:
        payload["link"] = link
    r = httpx.post(f"https://graph.facebook.com/v21.0/{d['page_id']}/feed", data=payload, timeout=25)
    if r.status_code >= 400:
        raise ValueError(f"Facebook error {r.status_code}: {r.text[:300]}")
    return f"Facebook Page par post ho gaya (id: {r.json().get('id')})."


# ------------------------------------------------------------------ Instagram (image + caption)


def instagram_post(image_url: str, caption: str = "") -> str:
    d = _need("instagram")
    base = f"https://graph.facebook.com/v21.0/{d['ig_user_id']}"
    r1 = httpx.post(f"{base}/media", data={"image_url": image_url, "caption": caption, "access_token": d["page_token"]}, timeout=30)
    if r1.status_code >= 400:
        raise ValueError(f"Instagram (step 1) error {r1.status_code}: {r1.text[:300]}")
    creation_id = r1.json().get("id")
    r2 = httpx.post(f"{base}/media_publish", data={"creation_id": creation_id, "access_token": d["page_token"]}, timeout=30)
    if r2.status_code >= 400:
        raise ValueError(f"Instagram (step 2) error {r2.status_code}: {r2.text[:300]}")
    return f"Instagram par post ho gaya (id: {r2.json().get('id')})."


# ------------------------------------------------------------------ WhatsApp Business Cloud API


def whatsapp_send(to: str, message: str) -> str:
    d = _need("whatsapp")
    to = "".join(ch for ch in to if ch.isdigit())
    if not to:
        raise ValueError("WhatsApp number ghalat hai (sirf digits, country code samet - jaise 923001234567).")
    r = httpx.post(
        f"https://graph.facebook.com/v21.0/{d['phone_id']}/messages",
        json={"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": message}},
        headers={"Authorization": f"Bearer {d['token']}", "Content-Type": "application/json"},
        timeout=25,
    )
    if r.status_code >= 400:
        raise ValueError(
            f"WhatsApp error {r.status_code}: {r.text[:300]} "
            "(WhatsApp sandbox me pehle receiver ko aapko template message ya 'hi' bhejna padta hai - Meta ka 24-ghante ka rule)."
        )
    return "WhatsApp message bhej diya."
