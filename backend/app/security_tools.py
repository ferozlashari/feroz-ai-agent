"""Sirf defensive cybersecurity tools: reputation check, CVE lookup, password/hash utils.
Koi cracking, exploit-building ya unauthorized-access tool yahan nahi hai — aur na kabhi hoga."""
import hashlib
import math
import re
import secrets
import string

import httpx

from . import config

# ------------------------------------------------------------------ hash / password


def hash_text(text: str, algo: str = "sha256") -> str:
    algo = (algo or "sha256").lower().replace("-", "")
    if algo not in hashlib.algorithms_guaranteed:
        return f"Ye algorithm nahi milta: {algo}. Try: md5, sha1, sha256, sha512"
    h = hashlib.new(algo)
    h.update((text or "").encode("utf-8"))
    return f"{algo}: {h.hexdigest()}"


def check_password_strength(password: str) -> str:
    pw = password or ""
    if not pw:
        return "Password khali hai."
    classes = sum(
        bool(re.search(p, pw)) for p in [r"[a-z]", r"[A-Z]", r"[0-9]", r"[^a-zA-Z0-9]"]
    )
    pool = (
        (26 if re.search(r"[a-z]", pw) else 0)
        + (26 if re.search(r"[A-Z]", pw) else 0)
        + (10 if re.search(r"[0-9]", pw) else 0)
        + (33 if re.search(r"[^a-zA-Z0-9]", pw) else 0)
    )
    entropy = len(pw) * math.log2(pool) if pool else 0
    common = {"password", "123456", "qwerty", "admin", "letmein", "welcome", "iloveyou", "12345678"}
    is_common = pw.lower() in common
    if is_common:
        level = "bohat kamzor (common password list me hai)"
    elif entropy < 35:
        level = "kamzor"
    elif entropy < 60:
        level = "theek-thaak"
    elif entropy < 80:
        level = "mazboot"
    else:
        level = "bohat mazboot"
    tips = []
    if len(pw) < 12:
        tips.append("kam az kam 12 characters rakho")
    if classes < 3:
        tips.append("bade/chhote huroof, number aur symbol mix karo")
    if is_common:
        tips.append("ye password internet par sab se aam leaked passwords me shamil hai - bilkul mat use karo")
    return (
        f"Length: {len(pw)} | Andazan entropy: {entropy:.0f} bits | Darja: {level}\n"
        + ("Mashware: " + "; ".join(tips) if tips else "Acha password hai.")
    )


def generate_password(length: int = 16, symbols: bool = True) -> str:
    length = max(8, min(int(length or 16), 128))
    alphabet = string.ascii_letters + string.digits + ("!@#$%^&*()-_=+[]{}" if symbols else "")
    while True:
        pw = "".join(secrets.choice(alphabet) for _ in range(length))
        if (
            any(c.islower() for c in pw)
            and any(c.isupper() for c in pw)
            and any(c.isdigit() for c in pw)
            and (not symbols or any(c in "!@#$%^&*()-_=+[]{}" for c in pw))
        ):
            return pw


# ------------------------------------------------------------------ reputation / CVE

_IP_RE = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")
_HASH_RE = re.compile(r"^[a-fA-F0-9]{32,64}$")


def virustotal_lookup(target: str) -> str:
    """Ek file hash, domain ya IP ki reputation VirusTotal se check karta hai (sirf padhna)."""
    if not config.VT_API_KEY:
        return "VT_API_KEY backend/.env me nahi hai. Free key: virustotal.com/gui/join-signup"
    target = (target or "").strip()
    if _HASH_RE.match(target):
        kind = "files"
    elif _IP_RE.match(target):
        kind = "ip_addresses"
    else:
        kind = "domains"
    try:
        r = httpx.get(
            f"https://www.virustotal.com/api/v3/{kind}/{target}",
            headers={"x-apikey": config.VT_API_KEY},
            timeout=25,
        )
    except httpx.HTTPError as e:
        return f"VirusTotal se rabta nahi hua: {e}"
    if r.status_code == 404:
        return f"'{target}' VirusTotal ke database me nahi mila (matlab ye check nahi hua abhi tak)."
    if r.status_code >= 400:
        return f"VirusTotal error {r.status_code}: {r.text[:200]}"
    attrs = r.json().get("data", {}).get("attributes", {})
    stats = attrs.get("last_analysis_stats", {})
    reputation = attrs.get("reputation")
    return (
        f"Target: {target} ({kind})\n"
        f"Malicious: {stats.get('malicious', 0)} | Suspicious: {stats.get('suspicious', 0)} | "
        f"Harmless: {stats.get('harmless', 0)} | Undetected: {stats.get('undetected', 0)}\n"
        f"Reputation score: {reputation if reputation is not None else 'N/A'}"
    )


def cve_lookup(query: str) -> str:
    """NVD se CVE dhoondta hai — 'CVE-2024-1234' ID ya keyword (jaise 'log4j') dono chalega."""
    query = (query or "").strip()
    headers = {"apiKey": config.NVD_API_KEY} if config.NVD_API_KEY else {}
    params = (
        {"cveId": query.upper()}
        if re.match(r"^CVE-\d{4}-\d+$", query.upper())
        else {"keywordSearch": query, "resultsPerPage": 5}
    )
    try:
        r = httpx.get("https://services.nvd.nist.gov/rest/json/cves/2.0", params=params, headers=headers, timeout=25)
    except httpx.HTTPError as e:
        return f"NVD se rabta nahi hua: {e}"
    if r.status_code == 403:
        return "NVD ne rate-limit kiya (bina key sirf ~5 request/30s milti hain). Thori der ruk kar dubara koshish karo."
    if r.status_code >= 400:
        return f"NVD error {r.status_code}: {r.text[:200]}"
    items = r.json().get("vulnerabilities", [])
    if not items:
        return f"'{query}' ke liye koi CVE nahi mila."
    out = []
    for it in items[:5]:
        cve = it.get("cve", {})
        cid = cve.get("id", "")
        desc = next((d["value"] for d in cve.get("descriptions", []) if d.get("lang") == "en"), "")
        metrics = cve.get("metrics", {})
        sev = ""
        for key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
            if metrics.get(key):
                m = metrics[key][0]["cvssData"]
                sev = f"CVSS {m.get('baseScore')} ({m.get('baseSeverity', m.get('severity', ''))})"
                break
        out.append(f"{cid} {('- ' + sev) if sev else ''}\n{desc[:400]}")
    return "\n\n".join(out)


def headers_scan(url: str) -> str:
    """Kisi website ke security headers check karta hai (khud ki site audit karne ke liye)."""
    from .webtools import assert_public_url, UA

    url = url if url.startswith(("http://", "https://")) else "https://" + url
    assert_public_url(url)
    try:
        r = httpx.get(url, timeout=20, headers={"User-Agent": UA}, follow_redirects=True)
    except httpx.HTTPError as e:
        return f"Site khuli nahi: {e}"
    wanted = [
        "strict-transport-security",
        "content-security-policy",
        "x-frame-options",
        "x-content-type-options",
        "referrer-policy",
        "permissions-policy",
    ]
    lines = [f"{url} -> HTTP {r.status_code}\n"]
    for h in wanted:
        val = r.headers.get(h)
        lines.append(f"{'✓' if val else '✗ GHAYAB'}  {h}: {val or ''}")
    server = r.headers.get("server")
    if server:
        lines.append(f"\nServer header (ye chhupana behtar hai): {server}")
    return "\n".join(lines)
