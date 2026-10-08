# Feroz — Personal AI Agent

Aapka apna AI saathi: general sawal-jawab, har qism ka code, internet search, webpage/PDF padhna, photo samajhna,
text-to-image, voice-to-text, text-to-voice, lambi yaaddasht, defensive cybersecurity tools, job search, aur
**apni ijazat/connection se** GitHub, LinkedIn, Twitter/X, Facebook, Instagram aur WhatsApp par kaam karna —
sab **Copilot mode** ke Allow/Deny ijazat ke saath.

- **Backend:** FastAPI (Python) · **Frontend:** React + Vite
- **Zubaanein:** Roman Urdu, اردو (Urdu), سنڌي (Sindhi), English
- **Chat AI (free tiers, ek waqt me jo chuno wahi use hota hai):** Groq · Gemini · Cerebras · Mistral · OpenRouter · HuggingFace · Ollama (offline)
- **Voice:** Groq Whisper (voice-to-text) + edge-tts (text-to-voice)
- **Image:** HuggingFace FLUX
- **Access key:** bilkul optional — khali chhoro to bina password chalta hai (apne akele PC ke liye)

## 1. Free keys (kam az kam EK chat provider chahiye)

| Service | Link | `.env` |
|---|---|---|
| Groq (tez, voice + vision) | console.groq.com/keys | `GROQ_API_KEY` |
| Gemini (photo/vision) | aistudio.google.com/apikey | `GEMINI_API_KEY` |
| Cerebras | cloud.cerebras.ai | `CEREBRAS_API_KEY` |
| Mistral | console.mistral.ai/api-keys | `MISTRAL_API_KEY` |
| OpenRouter (`:free` models) | openrouter.ai/keys | `OPENROUTER_API_KEY` |
| HuggingFace (image + chat) | huggingface.co/settings/tokens | `HF_API_KEY` |
| Ollama (offline) | ollama.com → `ollama pull llama3.2` | `OLLAMA_MODEL` |
| Tavily/Brave search (optional) | app.tavily.com / brave.com/search/api | `.env` |
| VirusTotal / NVD (optional) | virustotal.com / nvd.nist.gov | `.env` |

Social/job platform tokens `.env` me **nahi** jaate — app khulne ke baad Sidebar → **Connections** se daalo (zyada mehfooz).

## 2. Chalao (local)

Zaroorat: **Python 3.10+**, **Node.js 18+**.
**Windows:** `start.bat` double click · **Mac/Linux:** `./start.sh`
Server par chalana ho to **DEPLOY.md** dekho.

Pehli baar `backend/.env` ban jayegi — keys daalo, phir dobara start karo.
Browser: **http://localhost:5173**

Haath se:
```bash
cd backend && python -m venv venv && venv\Scripts\activate   # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt && copy .env.example .env    # Mac/Linux: cp
uvicorn app.main:app --port 8000 --reload
# naye terminal me:
cd frontend && npm install && npm run dev
```

## 3. Kya kya kar sakta hai

**Chat mode** — sawal-jawab, code, internet search + webpage/PDF padhna (source ke saath), photo (📎) samajhna, yaaddasht.

**Copilot mode** (ijazat ke saath) — files/commands + upar wala sab + social/job tools:
- `write_file`, `run_command`, `fetch_url` aur **har social-media post/message** par pehle Allow/Deny aata hai.
- Padhne wale tools (search, list_files, connections_status, job_search) seedhe chalte hain.
- Ek jawab me 25 tool-steps tak khud chal sakta hai.

**Defensive cybersecurity** — VirusTotal reputation, CVE lookup (NVD), apni website ke security headers,
password strength/generator, hash. **Sirf difaai maqsad ke liye** — hacking/exploit/unauthorized access ka koi tool nahi hai.

**Social media & jobs (Sidebar → Connections se apna token do)**
| Platform | Kya karta hai | Token kahan se |
|---|---|---|
| GitHub | Issue/gist banana, repos dekhna | github.com/settings/tokens |
| Twitter/X | Tweet post karna | developer.twitter.com → Keys and tokens |
| LinkedIn | Text post karna | LinkedIn Developer app (OAuth, neeche guide) |
| Facebook | Apni Page par post | developers.facebook.com/tools/explorer |
| Instagram | Business account par photo+caption post | Facebook Page se linked IG Business account |
| WhatsApp | Text message bhejna | developers.facebook.com → WhatsApp product |
| Adzuna (jobs) | Location-based job search | developer.adzuna.com/signup |

Har token sirf **isi computer ki local file** (`backend/data/feroz.db`) me save hota hai. Kabhi kisi teesre server ko nahi jaata.

> **LinkedIn ka token thora mushkil hai** (LinkedIn manual token generator nahi deta): developer app banao (developer.linkedin.com),
> "Share on LinkedIn" product add karo, phir OAuth 2.0 se `w_member_social` scope wala token lo
> (Postman/OAuth tool se ek dafa generate karke yahan paste kar sakte ho).

**Job search** — Remotive (bina key) + Adzuna (free key). **`draft_cover_letter`** sirf letter ka text likhta hai —
**auto-apply/form-fill nahi karta**; apply link diya jata hai, submit aap khud karte hain (kai job-sites is se allow bhi nahi karti automation).

**Image / Voice** — Image mode: FLUX. Mic: Groq Whisper. *Suno*: edge-tts.

## 4. Hifazat (zaroor parho)

- Files sirf `backend/workspace` me; bahar ke paths block. Commands ko API keys nazar nahi aatin, par Allow se pehle command parho.
- `fetch_url` public internet ke liye; private/local addresses block (SSRF hifazat). Internet ka content "untrusted" mana jata hai.
- Social/job tools **sirf** aapke apne diye hue token se chalte hain — kisi doosre account me nahi ja sakte.
- Server par host karo to **`ACCESS_KEY` zaroor set karo** aur HTTPS lagao — DEPLOY.md dekho.

## 5. Jo main jaan-boojh kar NAHI bana sakta

- Video/tasveer "leak" karne ka koi system — kisi ki privacy tor'na nuqsan-deh hai.
- "Kisi ka hacked account wapis lene" ka automated/unauthorized tool. Agar **aapka apna** account hack ho:
  har platform ka official recovery page use karo:
  [Facebook](https://www.facebook.com/hacked) · [Instagram](https://help.instagram.com/368191326593075) ·
  [LinkedIn](https://www.linkedin.com/help/linkedin/answer/a1341336) · [Twitter/X](https://help.x.com/forms/account-access) ·
  [WhatsApp](https://faq.whatsapp.com/1246245282925970) · [GitHub](https://github.com/contact/account-recovery)

## 6. Masle aur hal

| Masla | Hal |
|---|---|
| Backend se rabta nahi | Backend terminal chal raha hai? Port 8000 free? |
| 401 | Settings me `.env` wali `ACCESS_KEY`, ya `.env` me khali karke lock hata do |
| Model not found | Provider console me naya model naam dekh kar `.env` me likho |
| Social post fail | Sidebar → Connections me token check karo; platform ki error message me wajah likhi hoti hai |
| WhatsApp error | Sandbox rule: pehle receiver khud number ko "hi" bheje / template approve ho (Meta ka 24-ghante rule) |
| Rate limit (429) | Free tier ki hadd; provider "Auto" rakho ya thori der ruko |

## Folder structure
```
backend/app/  main.py · routes_chat.py · routes_media.py · routes_connectors.py
              llm.py (7 providers) · tools.py · webtools.py · security_tools.py
              social.py (GitHub/Twitter/LinkedIn/FB/IG/WhatsApp) · oauth1.py (Twitter signing)
              jobs.py · connections.py · memory.py · db.py · prompts.py · config.py
frontend/src/ App.jsx · api.js · components/ (Sidebar, Message, ToolCard, Composer, Attachments,
              MemoryModal, ConnectionsModal, SettingsModal)
```

## Jo abhi nahi hai (sach)
Ghanton chalne wala background agent (25 steps/response tak) · streaming jawab · scanned-PDF OCR ·
auto-apply job forms · Instagram text-only post (sirf photo+caption, Meta ki API ki hadd hai) ·
chats sirf browser me save hoti hain (server backup nahi).
