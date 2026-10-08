import React, { useEffect, useRef, useState } from 'react'
import { Image as ImageIcon, Menu, MessageSquare, ShieldCheck } from 'lucide-react'
import { api } from './api'
import {
  K_ACTIVE,
  loadChats,
  loadSettings,
  newChat,
  saveChats,
  saveSettings,
  uid,
} from './storage'
import { useRecorder } from './hooks/useRecorder'
import Sidebar from './components/Sidebar.jsx'
import Message, { Thinking } from './components/Message.jsx'
import ToolCard from './components/ToolCard.jsx'
import Composer from './components/Composer.jsx'
import SettingsModal from './components/SettingsModal.jsx'
import MemoryModal from './components/MemoryModal.jsx'
import ConnectionsModal from './components/ConnectionsModal.jsx'

const MODES = [
  { id: 'chat', label: 'Chat', Icon: MessageSquare },
  { id: 'copilot', label: 'Copilot', Icon: ShieldCheck },
  { id: 'image', label: 'Image', Icon: ImageIcon },
]

const HINTS = {
  chat: {
    line: 'Sawal poochho, code likhwao, kuch samjhao, ya internet par dhoondo.',
    ideas: [
      'Python me ek todo app ka poora code likh do',
      'Aaj Karachi ka mausam kya hai?',
      'React me login form banao jo validation kare',
    ],
    placeholder: 'Kuch bhi poochho, code maango, ya photo/PDF lagao…',
  },
  copilot: {
    line: 'Files banata hoon, commands chalata hoon, internet se cheezein la sakta hoon, security scan kar sakta hoon, aur (apki ijazat/connection se) GitHub, LinkedIn, Twitter, Facebook, Instagram, WhatsApp par kaam kar sakta hoon — har khatarnaak kaam se pehle Allow/Deny.',
    ideas: [
      'Ek HTML calculator banao aur workspace me save karo',
      'React developer job Karachi me dhoondo',
      'Mere GitHub repos dikhao',
    ],
    placeholder: 'Bolo kya banana, dhoondna, post karna ya check karna hai…',
  },
  image: {
    line: 'Jo tasveer soch rahe ho likh do — Urdu, Roman Urdu ya English me.',
    ideas: [
      'Lahore ki Badshahi Masjid ka sunset, cinematic',
      'Ek chhota robot chai pi raha hai, cartoon style',
      'Pahari gaon barish me, oil painting',
    ],
    placeholder: 'Tasveer ka khayal likho…',
  },
}

const isOpenTool = (m) => m.role === 'tool' && (m.status === 'pending' || m.status === 'running')

function safeParse(s) {
  try {
    const v = JSON.parse(s || '{}')
    return v && typeof v === 'object' ? v : {}
  } catch {
    return {}
  }
}

// UI ke messages ko backend ke format me badalna
function toApi(messages) {
  return messages
    .filter((m) => !m.error)
    .map((m) => {
      if (m.role === 'tool') return { role: 'tool', tool_call_id: m.tool_call_id, name: m.name, content: m.content || '' }
      if (m.role === 'assistant')
        return { role: 'assistant', content: m.content || '', ...(m.tool_calls ? { tool_calls: m.tool_calls } : {}) }
      const out = { role: 'user', content: m.content }
      if (m.images?.length) out.images = m.images
      return out
    })
}

export default function App() {
  const [settings, setSettings] = useState(loadSettings)
  const [status, setStatus] = useState(null)
  const [statusError, setStatusError] = useState('')

  const initial = useRef(null)
  if (initial.current === null) {
    const c = loadChats()
    initial.current = c.length ? c : [newChat()]
  }
  const [chats, _setChats] = useState(initial.current)
  const chatsRef = useRef(initial.current)
  const [activeId, setActiveId] = useState(() => {
    const saved = localStorage.getItem(K_ACTIVE)
    return initial.current.some((c) => c.id === saved) ? saved : initial.current[0].id
  })

  const [input, setInput] = useState('')
  const [attachments, setAttachments] = useState([])
  const [busy, setBusy] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const [showMemory, setShowMemory] = useState(false)
  const [showConnections, setShowConnections] = useState(false)
  const [toast, setToast] = useState('')
  const [speakingId, setSpeakingId] = useState(null)
  const audioRef = useRef(null)
  const scrollRef = useRef(null)

  const active = chats.find((c) => c.id === activeId) || chats[0]
  const name = status?.name || 'Feroz'
  const hint = HINTS[active.mode] || HINTS.chat
  const pendingTools = active.messages.some(isOpenTool)

  // ---------- state helpers (ref ki wajah se async loops me purana state nahi milta)
  const setChats = (updater) => {
    const next = typeof updater === 'function' ? updater(chatsRef.current) : updater
    chatsRef.current = next
    _setChats(next)
    saveChats(next)
  }
  const getChat = (id) => chatsRef.current.find((c) => c.id === id)
  const setMsgs = (id, fn) =>
    setChats((cs) => cs.map((c) => (c.id === id ? { ...c, messages: fn(c.messages), updated: Date.now() } : c)))
  const patchMsg = (id, msgId, patch) => setMsgs(id, (ms) => ms.map((m) => (m.id === msgId ? { ...m, ...patch } : m)))
  const flash = (text) => {
    setToast(text)
    setTimeout(() => setToast(''), 3500)
  }

  useEffect(() => saveSettings(settings), [settings])
  useEffect(() => localStorage.setItem(K_ACTIVE, active.id), [active.id])
  useEffect(() => {
    api
      .status()
      .then((s) => {
        setStatus(s)
        setStatusError('')
      })
      .catch((e) => setStatusError(e.message))
  }, [])
  useEffect(() => {
    const el = scrollRef.current
    if (el) el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' })
  }, [active.messages.length, busy, active.id])

  // ---------- attachments (photo / PDF)
  async function pickFiles(fileList) {
    const files = Array.from(fileList).slice(0, 4 - attachments.length)
    if (files.length === 0) return flash('Ek waqt me zyada se zyada 4 files.')
    const placeholders = files.map((f) => ({ id: uid(), name: f.name, uploading: true, kind: f.type.startsWith('image/') ? 'image' : 'pdf' }))
    setAttachments((a) => [...a, ...placeholders])
    for (let i = 0; i < files.length; i++) {
      const ph = placeholders[i]
      try {
        const r = await api.upload(files[i])
        setAttachments((a) => a.map((x) => (x.id === ph.id ? { ...x, uploading: false, ...r } : x)))
      } catch (e) {
        setAttachments((a) => a.filter((x) => x.id !== ph.id))
        flash(e.message)
      }
    }
  }
  const removeAttachment = (id) => setAttachments((a) => a.filter((x) => x.id !== id))

  // ---------- awaaz (voice)
  const recorder = useRecorder({
    language: settings.sttLang,
    onError: (e) => flash(e.message),
    onResult: (text) => {
      if (!text) return flash('Awaaz samajh nahi aayi, dobara bolo.')
      if (settings.autoSend) send(text)
      else setInput((prev) => (prev ? prev + ' ' : '') + text)
    },
  })

  function stopSpeak() {
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current = null
    }
    setSpeakingId(null)
  }

  async function speak(text, id) {
    stopSpeak()
    setSpeakingId(id)
    try {
      const blob = await api.tts(text, settings.voice)
      const url = URL.createObjectURL(blob)
      const audio = new Audio(url)
      audioRef.current = audio
      const done = () => {
        setSpeakingId((cur) => (cur === id ? null : cur))
        URL.revokeObjectURL(url)
      }
      audio.onended = done
      audio.onerror = done
      await audio.play()
    } catch (e) {
      setSpeakingId(null)
      flash(e.message)
    }
  }

  // ---------- errors
  function handleError(chatId, e, retryable = false) {
    if (e.status === 401) setShowSettings(true)
    setMsgs(chatId, (ms) => [
      ...ms,
      { id: uid(), role: 'assistant', error: true, retryable, content: e.message || String(e) },
    ])
  }

  // ---------- chat + copilot loop
  async function execTool(chatId, msgId) {
    const t = getChat(chatId)?.messages.find((m) => m.id === msgId)
    if (!t) return
    patchMsg(chatId, msgId, { status: 'running' })
    try {
      const r = await api.exec(t.name, t.args)
      patchMsg(chatId, msgId, { status: 'done', content: r.result })
    } catch (e) {
      patchMsg(chatId, msgId, { status: 'error', content: `Error: ${e.message}` })
      if (e.status === 401) setShowSettings(true)
    }
  }

  async function maybeContinue(chatId, depth) {
    const chat = getChat(chatId)
    if (!chat || chat.messages.some(isOpenTool)) return
    if (depth > 25) {
      flash('Bohat zyada tool steps ho gaye, ruk gaya. "Jaari rakho" likh kar aage barhao.')
      return
    }
    await runChat(chatId, depth)
  }

  async function runChat(chatId, depth = 0) {
    setBusy(true)
    try {
      const chat = getChat(chatId)
      const res = await api.chat({
        messages: toApi(chat.messages),
        provider: settings.provider,
        mode: chat.mode === 'copilot' ? 'copilot' : 'chat',
        temperature: settings.temperature,
        reply_style: settings.replyStyle,
        custom_instructions: settings.customInstructions,
        user_name: settings.userName,
      })
      const m = res.message
      const calls = m.tool_calls || []
      const assistant = {
        id: uid(),
        role: 'assistant',
        content: m.content || '',
        tool_calls: calls.length ? calls : undefined,
        provider: res.provider,
      }
      const toolMsgs = calls.map((tc) => ({
        id: uid(),
        role: 'tool',
        tool_call_id: tc.id,
        name: tc.function.name,
        args: safeParse(tc.function.arguments),
        status: 'pending',
        content: '',
      }))
      setMsgs(chatId, (ms) => [...ms, assistant, ...toolMsgs])

      if (toolMsgs.length) {
        const auto = status?.auto_approved_tools || ['web_search']
        for (const t of toolMsgs) if (auto.includes(t.name)) await execTool(chatId, t.id)
        await maybeContinue(chatId, depth + 1)
      } else if (settings.autoSpeak && assistant.content) {
        speak(assistant.content, assistant.id)
      }
    } catch (e) {
      handleError(chatId, e, true)
    } finally {
      setBusy(false)
    }
  }

  async function decide(chatId, msgId, allow) {
    if (busy) return
    setBusy(true)
    try {
      if (allow) await execTool(chatId, msgId)
      else patchMsg(chatId, msgId, { status: 'denied', content: 'User ne is action ki ijazat nahi di.' })
      await maybeContinue(chatId, 0)
    } finally {
      setBusy(false)
    }
  }

  async function retry(chatId, msgId) {
    if (busy) return
    setMsgs(chatId, (ms) => ms.filter((m) => m.id !== msgId))
    await runChat(chatId)
  }

  async function makeImage(chatId, prompt) {
    setBusy(true)
    try {
      const r = await api.image(prompt)
      setMsgs(chatId, (ms) => [
        ...ms,
        { id: uid(), role: 'assistant', content: `Image banayi: ${r.prompt_used}`, image: r.url, provider: 'huggingface' },
      ])
    } catch (e) {
      handleError(chatId, e)
    } finally {
      setBusy(false)
    }
  }

  async function send(raw) {
    const typed = typeof raw === 'string' ? raw : input
    const text = typed.trim()
    const atts = typeof raw === 'string' ? [] : attachments
    if (atts.some((a) => a.uploading)) return flash('Files abhi upload ho rahi hain, thora ruko.')
    if (!text && atts.length === 0) return
    if (busy) return
    const chat = getChat(active.id)
    if (chat.messages.some(isOpenTool)) return flash('Pehle upar wale action par Allow ya Deny dabao.')
    stopSpeak()
    setInput('')
    setAttachments([])

    const images = atts.filter((a) => a.kind === 'image').map((a) => a.url)
    const pdfs = atts.filter((a) => a.kind === 'pdf')
    let content = text
    for (const p of pdfs) {
      content += `\n\n[Attached PDF: ${p.name} (${p.pages} pages)]\n${p.text}`
    }
    if (!content.trim() && images.length) content = 'Is tasveer ko dekho aur batao ke ismein kya hai.'

    setChats((cs) =>
      cs.map((c) =>
        c.id === chat.id
          ? {
              ...c,
              title: c.messages.length === 0 ? (text || pdfs[0]?.name || 'Tasveer').slice(0, 40) : c.title,
              messages: [
                ...c.messages,
                { id: uid(), role: 'user', content, images, files: pdfs.map((p) => p.name) },
              ],
              updated: Date.now(),
            }
          : c,
      ),
    )
    if (chat.mode === 'image') await makeImage(chat.id, text)
    else await runChat(chat.id)
  }

  // ---------- chats
  function createChat() {
    const c = newChat(active.mode)
    setChats((cs) => [c, ...cs])
    setActiveId(c.id)
    setSidebarOpen(false)
    setInput('')
    setAttachments([])
  }

  function deleteChat(id) {
    let rest = chatsRef.current.filter((c) => c.id !== id)
    if (rest.length === 0) rest = [newChat()]
    setChats(rest)
    if (id === activeId) setActiveId(rest[0].id)
  }

  function setMode(mode) {
    setChats((cs) => cs.map((c) => (c.id === active.id ? { ...c, mode } : c)))
    setAttachments([])
  }

  function clearAll() {
    if (!window.confirm('Sab chats hamesha ke liye mit jayengi. Pakka?')) return
    const c = newChat()
    setChats([c])
    setActiveId(c.id)
    setShowSettings(false)
  }

  const greeting = settings.userName ? `Assalam o Alaikum, ${settings.userName}` : 'Assalam o Alaikum'
  const showThinking = busy && !pendingTools

  return (
    <div className="app">
      <Sidebar
        name={name}
        chats={chats}
        activeId={active.id}
        open={sidebarOpen}
        status={status}
        onSelect={(id) => {
          setActiveId(id)
          setSidebarOpen(false)
        }}
        onNew={createChat}
        onDelete={deleteChat}
        onSettings={() => {
          setShowSettings(true)
          setSidebarOpen(false)
        }}
        onMemory={() => {
          setShowMemory(true)
          setSidebarOpen(false)
        }}
        onConnections={() => {
          setShowConnections(true)
          setSidebarOpen(false)
        }}
      />
      {sidebarOpen && <div className="scrim" onClick={() => setSidebarOpen(false)} />}

      <main className="main">
        <header className="topbar">
          <button type="button" className="icon-btn menu-btn" onClick={() => setSidebarOpen(true)} aria-label="Menu">
            <Menu size={20} />
          </button>
          <div className="topbar-title" dir="auto">
            {active.title}
          </div>
          <div className="modes" role="tablist" aria-label="Mode">
            {MODES.map(({ id, label, Icon }) => (
              <button
                key={id}
                type="button"
                role="tab"
                aria-selected={active.mode === id}
                className={`mode ${active.mode === id ? 'on' : ''}`}
                onClick={() => setMode(id)}
              >
                <Icon size={15} />
                <span>{label}</span>
              </button>
            ))}
          </div>
        </header>

        {statusError && (
          <div className="banner">
            {statusError} — backend folder me <code>uvicorn app.main:app --port 8000</code> chalao.
          </div>
        )}

        <div className="scroll" ref={scrollRef}>
          <div className="thread">
            {active.messages.length === 0 && (
              <section className="hero">
                <h1>{greeting}</h1>
                <p>{hint.line}</p>
                {active.mode === 'copilot' && status?.workspace && (
                  <p className="ws">
                    Workspace: <code>{status.workspace}</code>
                  </p>
                )}
                <ul className="ideas">
                  {hint.ideas.map((t) => (
                    <li key={t}>
                      <button type="button" onClick={() => send(t)} disabled={busy}>
                        {t}
                      </button>
                    </li>
                  ))}
                </ul>
              </section>
            )}

            {active.messages.map((m) => {
              if (m.role === 'tool')
                return (
                  <ToolCard
                    key={m.id}
                    m={m}
                    disabled={busy}
                    onAllow={() => decide(active.id, m.id, true)}
                    onDeny={() => decide(active.id, m.id, false)}
                  />
                )
              if (m.role === 'assistant' && !m.content && !m.image && !m.error) return null
              return (
                <Message
                  key={m.id}
                  m={m}
                  name={name}
                  speaking={speakingId === m.id}
                  onSpeak={() => speak(m.content, m.id)}
                  onStop={stopSpeak}
                  onRetry={() => retry(active.id, m.id)}
                />
              )
            })}

            {showThinking && <Thinking label={active.mode === 'image' ? 'Tasveer ban rahi hai…' : 'Soch raha hoon…'} />}
          </div>
        </div>

        <Composer
          value={input}
          onChange={setInput}
          onSend={() => send()}
          busy={busy}
          blocked={pendingTools}
          placeholder={pendingTools ? 'Pehle upar Allow ya Deny dabao…' : hint.placeholder}
          recording={recorder.recording}
          transcribing={recorder.transcribing}
          onMic={recorder.toggle}
          attachments={attachments}
          onRemoveAttachment={removeAttachment}
          onPickFiles={pickFiles}
          showAttach={active.mode !== 'image'}
        />
      </main>

      {showSettings && (
        <SettingsModal
          settings={settings}
          setSettings={setSettings}
          status={status}
          onClose={() => {
            setShowSettings(false)
            api.status().then(setStatus).catch(() => {})
          }}
          onClearAll={clearAll}
        />
      )}
      {showMemory && <MemoryModal onClose={() => setShowMemory(false)} />}
      {showConnections && <ConnectionsModal onClose={() => setShowConnections(false)} />}
      {toast && <div className="toast" role="status">{toast}</div>}
    </div>
  )
}
