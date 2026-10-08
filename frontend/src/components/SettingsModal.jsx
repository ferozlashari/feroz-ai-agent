import React from 'react'
import { X } from 'lucide-react'

const PROVIDERS = [
  ['auto', 'Auto (jo chale usi se)'],
  ['groq', 'Groq'],
  ['gemini', 'Gemini'],
  ['cerebras', 'Cerebras'],
  ['mistral', 'Mistral'],
  ['openrouter', 'OpenRouter (free models)'],
  ['huggingface', 'HuggingFace'],
  ['ollama', 'Ollama (apne computer par)'],
]

export default function SettingsModal({ settings, setSettings, status, onClose, onClearAll }) {
  const set = (k, v) => setSettings({ ...settings, [k]: v })
  return (
    <div className="modal-back" onMouseDown={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal" role="dialog" aria-modal="true" aria-label="Settings">
        <div className="modal-head">
          <h2>Settings</h2>
          <button type="button" className="icon-btn" onClick={onClose} aria-label="Band karo">
            <X size={18} />
          </button>
        </div>

        <div className="modal-body">
          <label className="field">
            <span>Access key</span>
            <input
              type="password"
              value={settings.accessKey}
              onChange={(e) => set('accessKey', e.target.value)}
              placeholder="backend/.env wali ACCESS_KEY"
              autoComplete="off"
            />
            <small>
              {status?.access_key_required
                ? 'Backend "locked" hai - yahan sahi key daalni zaroori hai.'
                : 'Bilkul optional hai: backend/.env me ACCESS_KEY khali hai, is liye app bina password khula hai.'}
            </small>
          </label>

          <label className="field">
            <span>AI provider</span>
            <select value={settings.provider} onChange={(e) => set('provider', e.target.value)}>
              {PROVIDERS.map(([v, l]) => (
                <option key={v} value={v}>
                  {l}
                  {v !== 'auto' && status && !status.providers?.[v] ? ' (key/setup nahi)' : ''}
                </option>
              ))}
            </select>
            <small>
              Auto me pehle Groq, phir Gemini, Cerebras, Mistral, OpenRouter, HuggingFace, Ollama try hota hai.
              Photo bheji jaaye to khud vision wale provider (Gemini/Groq) par chala jata hai.
            </small>
          </label>

          <label className="field">
            <span>Jawab ki zubaan</span>
            <select value={settings.replyStyle} onChange={(e) => set('replyStyle', e.target.value)}>
              <option value="auto">Jaise main likhoon</option>
              <option value="roman_urdu">Roman Urdu</option>
              <option value="urdu">اردو</option>
              <option value="sindhi">سنڌي</option>
              <option value="english">English</option>
            </select>
          </label>

          <label className="field">
            <span>Aapka naam</span>
            <input value={settings.userName} onChange={(e) => set('userName', e.target.value)} placeholder="Optional" />
          </label>

          <label className="field">
            <span>Khaas hidayaat</span>
            <textarea
              rows={3}
              value={settings.customInstructions}
              onChange={(e) => set('customInstructions', e.target.value)}
              placeholder="Jaise: Main Python aur React seekh raha hoon, code me comments Urdu me likho."
            />
          </label>

          <label className="field">
            <span>Creativity: {Number(settings.temperature).toFixed(1)}</span>
            <input
              type="range"
              min="0"
              max="1.2"
              step="0.1"
              value={settings.temperature}
              onChange={(e) => set('temperature', Number(e.target.value))}
            />
            <small>Code ke liye kam, kahani/idea ke liye zyada rakho.</small>
          </label>

          <div className="split">
            <label className="field">
              <span>Bolne wali awaaz</span>
              <select value={settings.voice} onChange={(e) => set('voice', e.target.value)}>
                <option value="auto">Auto</option>
                <option value="ur-PK-AsadNeural">Urdu — Asad</option>
                <option value="ur-PK-UzmaNeural">Urdu — Uzma</option>
                <option value="en-US-AriaNeural">English — Aria</option>
                <option value="en-GB-RyanNeural">English — Ryan</option>
                <option value="hi-IN-MadhurNeural">Hindi — Madhur</option>
                <option value="hi-IN-SwaraNeural">Hindi — Swara</option>
              </select>
            </label>
            <label className="field">
              <span>Main kis zubaan me bolta hoon</span>
              <select value={settings.sttLang} onChange={(e) => set('sttLang', e.target.value)}>
                <option value="">Auto</option>
                <option value="ur">Urdu</option>
                <option value="sd">Sindhi</option>
                <option value="en">English</option>
                <option value="hi">Hindi</option>
              </select>
            </label>
          </div>

          <small className="muted-note">
            Note: bolne wali awaaz (TTS) me abhi Sindhi ki apni awaaz nahi hai - Sindhi text likha/bola jayega, sunne ke liye
            Urdu awaaz use hogi.
          </small>

          <label className="check">
            <input type="checkbox" checked={settings.autoSpeak} onChange={(e) => set('autoSpeak', e.target.checked)} />
            <span>Jawab khud bol kar sunao</span>
          </label>
          <label className="check">
            <input type="checkbox" checked={settings.autoSend} onChange={(e) => set('autoSend', e.target.checked)} />
            <span>Voice ke baad message khud bhej do</span>
          </label>

          <div className="danger-zone">
            <button type="button" className="btn btn-deny" onClick={onClearAll}>
              Sab chats mita do
            </button>
            {status?.workspace && <small>Copilot ka workspace: {status.workspace}</small>}
            <small>
              Mobile/doosre device se kholna ho to running PC ke IP par jao: <code>http://[is-computer-ka-IP]:5173</code> (usi WiFi par).
            </small>
          </div>
        </div>
      </div>
    </div>
  )
}
