"""Copilot ke saare tools. File likhna, command chalana, aur internet par kuch bhi bhejna
(fetch_url, run_command) hamesha user ki Allow/Deny ijazat se guzarte hain."""
import asyncio
import json
import subprocess
from typing import Any, Dict, List

from . import config, connections, jobs, memory, security_tools, social, webtools, wsutil

# Ye tools bina poochhe chal jaate hain (sirf padhna/search - kisi cheez ko badalte nahi)
AUTO_APPROVED = [
    "web_search", "wikipedia", "weather", "list_files", "read_file", "remember", "recall_memory",
    "connections_status", "job_search", "draft_cover_letter", "github_list_repos",
    "check_password_strength", "generate_password", "hash_text", "virustotal_lookup", "cve_lookup", "headers_scan",
]
if config.AUTO_APPROVE_FETCH:
    AUTO_APPROVED.append("fetch_url")
if config.ALLOW_AUTO_EXEC:
    AUTO_APPROVED += ["write_file", "run_command"]

CHAT_MODE_TOOLS = ["web_search", "wikipedia", "weather", "fetch_url", "job_search", "draft_cover_letter"]  # simple chat me bhi milte hain

TOOL_SPECS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Internet par search karo (taaza maloomat, news, docs).",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "max_results": {"type": "integer", "description": "default 5"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_url",
            "description": "Ek webpage ya PDF ka poora content padho (jab koi link diya ho ya search ke baad us link ko kholna ho).",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string"},
                    "include_links": {"type": "boolean", "description": "Page ke andar ke links bhi do"},
                },
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "wikipedia",
            "description": "Wikipedia se kisi topic ka khulasa lao.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}, "lang": {"type": "string", "description": "e.g. en, ur, hi"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "weather",
            "description": "Kisi shehar ka mojooda mausam aur 3-din ka forecast.",
            "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "remember",
            "description": "Koi ahem baat lambi muddat ke liye yaad rakho (dusri chats me bhi yaad rahegi). Jab user kahe 'yaad rakho' ya khud koi zaroori pasand/tafseel bataye.",
            "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "recall_memory",
            "description": "Pehle yaad rakhi hui baaton me dhoondo.",
            "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "Workspace ke ek folder ki files aur folders ki list.",
            "parameters": {"type": "object", "properties": {"path": {"type": "string", "description": "default '.'"}}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Workspace se ek text file padho.",
            "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Workspace me file banao ya purani ko poori tarah replace karo. Folder khud ban jaate hain.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Workspace folder me shell command chalao (python script, pip install, npm, git waghaira). 60s limit.",
            "parameters": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_password_strength",
            "description": "Ek password ki mazbooti check karo (sirf local hisaab, kahin bheja nahi jaata).",
            "parameters": {"type": "object", "properties": {"password": {"type": "string"}}, "required": ["password"]},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_password",
            "description": "Mazboot random password banao.",
            "parameters": {
                "type": "object",
                "properties": {"length": {"type": "integer"}, "symbols": {"type": "boolean"}},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "hash_text",
            "description": "Text ka hash nikalo (md5/sha1/sha256/sha512).",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string"}, "algo": {"type": "string"}},
                "required": ["text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "virustotal_lookup",
            "description": "File hash, domain ya IP ki reputation VirusTotal se check karo (malware/phishing scan, sirf padhna).",
            "parameters": {"type": "object", "properties": {"target": {"type": "string"}}, "required": ["target"]},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cve_lookup",
            "description": "Kisi software/library me maloom security kamzoriyan (CVE) dhoondo, defensive patching ke liye.",
            "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "headers_scan",
            "description": "Apni website ke security headers check karo (HSTS, CSP waghaira) - khud ki site audit karne ke liye.",
            "parameters": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "connections_status",
            "description": "Dekho kaunse social/job platforms connect hain (Settings > Connections).",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "job_search",
            "description": "Job listings dhoondo (Remotive - remote jobs, aur agar Adzuna connected ho to location-based bhi).",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "location": {"type": "string"},
                    "remote_only": {"type": "boolean"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "draft_cover_letter",
            "description": "Job ke liye cover letter ka draft likho (apply khud user karega, ye sirf text banata hai).",
            "parameters": {
                "type": "object",
                "properties": {
                    "job_title": {"type": "string"},
                    "company": {"type": "string"},
                    "background": {"type": "string", "description": "Candidate ka tajurba/skills"},
                    "tone": {"type": "string"},
                },
                "required": ["job_title", "company", "background"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "github_create_issue",
            "description": "GitHub repo me issue banao. Pehle user ka apna GitHub connected hona chahiye.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo": {"type": "string", "description": "owner/repo"},
                    "title": {"type": "string"},
                    "body": {"type": "string"},
                },
                "required": ["repo", "title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "github_create_gist",
            "description": "GitHub par ek gist (code snippet) banao.",
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "filename": {"type": "string"},
                    "content": {"type": "string"},
                    "public": {"type": "boolean"},
                },
                "required": ["filename", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "github_list_repos",
            "description": "User ke GitHub repos ki list.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "post_twitter",
            "description": "Twitter/X par apne connected account se tweet post karo.",
            "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "post_linkedin",
            "description": "LinkedIn par apne connected account se text post karo.",
            "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "post_facebook",
            "description": "Apne connected Facebook Page par post karo.",
            "parameters": {
                "type": "object",
                "properties": {"message": {"type": "string"}, "link": {"type": "string"}},
                "required": ["message"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "post_instagram",
            "description": "Apne connected Instagram Business account par ek tasveer (public image URL) post karo.",
            "parameters": {
                "type": "object",
                "properties": {"image_url": {"type": "string"}, "caption": {"type": "string"}},
                "required": ["image_url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_whatsapp",
            "description": "WhatsApp Business API se ek text message bhejo (apne connected number se).",
            "parameters": {
                "type": "object",
                "properties": {"to": {"type": "string", "description": "Country code samet number"}, "message": {"type": "string"}},
                "required": ["to", "message"],
            },
        },
    },
]


def specs_for(mode: str) -> List[dict]:
    if mode == "copilot":
        return TOOL_SPECS
    if mode == "chat":
        return [t for t in TOOL_SPECS if t["function"]["name"] in CHAT_MODE_TOOLS]
    return []


def _run_command(command: str) -> str:
    try:
        proc = subprocess.run(
            command,
            shell=True,
            cwd=str(config.WORKSPACE_DIR),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
            env=wsutil.clean_env(),
        )
    except subprocess.TimeoutExpired:
        return "Command 60 second me khatam nahi hui, roak di gayi."
    out = ""
    if proc.stdout:
        out += proc.stdout
    if proc.stderr:
        out += ("\n[stderr]\n" if out else "[stderr]\n") + proc.stderr
    out = out.strip() or "(koi output nahi)"
    return wsutil.clip(f"exit code: {proc.returncode}\n{out}")


def _list_files(path: str = ".") -> str:
    target = wsutil.safe_path(path)
    if not target.exists():
        return f"Folder nahi mila: {path}"
    if not target.is_dir():
        return f"Ye folder nahi hai: {path}"
    entries = sorted(target.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
    if not entries:
        return "(folder khali hai)"
    out = [f"{p.name}/" if p.is_dir() else f"{p.name}  ({p.stat().st_size} bytes)" for p in entries[:200]]
    if len(entries) > 200:
        out.append(f"... aur {len(entries) - 200} items")
    return "\n".join(out)


def _read_file(path: str) -> str:
    target = wsutil.safe_path(path)
    if not target.is_file():
        return f"File nahi mili: {path}"
    return wsutil.clip(target.read_text(encoding="utf-8", errors="replace"))


def _write_file(path: str, content: str) -> str:
    target = wsutil.safe_path(path)
    if target == config.WORKSPACE_DIR:
        return "File ka naam do."
    target.parent.mkdir(parents=True, exist_ok=True)
    existed = target.exists()
    target.write_text(content, encoding="utf-8")
    return f"{'Update' if existed else 'Nayi file bani'}: {path} ({len(content)} characters)"


def _remember(text: str) -> str:
    mid = memory.add(text)
    return f"Yaad rakh liya (#{mid})." if mid else "Kuch yaad rakhne ke liye nahi mila."


def _recall(query: str) -> str:
    rows = memory.search(query)
    if not rows:
        return "Kuch yaad nahi aaya."
    return "\n".join(f"- {r['text']}" for r in rows)


def _connections_status() -> str:
    items = connections.status()
    lines = [f"{'✓' if it['connected'] else '✗'} {it['label']}" for it in items]
    return "\n".join(lines)


HANDLERS = {
    "web_search": lambda a: webtools.web_search(str(a.get("query", "")), int(a.get("max_results", 5) or 5)),
    "fetch_url": lambda a: webtools.fetch_url(str(a.get("url", "")), include_links=bool(a.get("include_links"))),
    "wikipedia": lambda a: webtools.wikipedia(str(a.get("query", "")), str(a.get("lang", "en"))),
    "weather": lambda a: webtools.weather(str(a.get("city", ""))),
    "remember": lambda a: _remember(str(a.get("text", ""))),
    "recall_memory": lambda a: _recall(str(a.get("query", ""))),
    "list_files": lambda a: _list_files(str(a.get("path", "."))),
    "read_file": lambda a: _read_file(str(a.get("path", ""))),
    "write_file": lambda a: _write_file(str(a.get("path", "")), str(a.get("content", ""))),
    "run_command": lambda a: _run_command(str(a.get("command", ""))),
    "check_password_strength": lambda a: security_tools.check_password_strength(str(a.get("password", ""))),
    "generate_password": lambda a: security_tools.generate_password(int(a.get("length", 16) or 16), bool(a.get("symbols", True))),
    "hash_text": lambda a: security_tools.hash_text(str(a.get("text", "")), str(a.get("algo", "sha256"))),
    "virustotal_lookup": lambda a: security_tools.virustotal_lookup(str(a.get("target", ""))),
    "cve_lookup": lambda a: security_tools.cve_lookup(str(a.get("query", ""))),
    "headers_scan": lambda a: security_tools.headers_scan(str(a.get("url", ""))),
    "connections_status": lambda a: _connections_status(),
    "job_search": lambda a: jobs.search(str(a.get("query", "")), str(a.get("location", "")), bool(a.get("remote_only", False))),
    "github_create_issue": lambda a: social.github_create_issue(str(a.get("repo", "")), str(a.get("title", "")), str(a.get("body", ""))),
    "github_create_gist": lambda a: social.github_create_gist(
        str(a.get("description", "")), str(a.get("filename", "snippet.txt")), str(a.get("content", "")), bool(a.get("public", False))
    ),
    "github_list_repos": lambda a: social.github_list_repos(),
    "post_twitter": lambda a: social.twitter_post(str(a.get("text", ""))),
    "post_linkedin": lambda a: social.linkedin_post(str(a.get("text", ""))),
    "post_facebook": lambda a: social.facebook_post(str(a.get("message", "")), a.get("link") or None),
    "post_instagram": lambda a: social.instagram_post(str(a.get("image_url", "")), str(a.get("caption", ""))),
    "send_whatsapp": lambda a: social.whatsapp_send(str(a.get("to", "")), str(a.get("message", ""))),
}

ASYNC_HANDLERS = {
    "draft_cover_letter": lambda a: jobs.draft_cover_letter(
        str(a.get("job_title", "")), str(a.get("company", "")), str(a.get("background", "")), str(a.get("tone", "professional"))
    ),
}


async def execute_tool(name: str, arguments: Dict[str, Any]) -> str:
    if not isinstance(arguments, dict):
        try:
            arguments = json.loads(arguments)
        except Exception:
            arguments = {}
    if name in ASYNC_HANDLERS:
        try:
            return await ASYNC_HANDLERS[name](arguments)
        except Exception as e:
            return f"Error: {type(e).__name__}: {e}"
    handler = HANDLERS.get(name)
    if not handler:
        return f"Error: unknown tool '{name}'"
    try:
        return await asyncio.to_thread(handler, arguments)
    except Exception as e:  # LLM ko error dikhao taake wo khud sudhaar kare
        return f"Error: {type(e).__name__}: {e}"
