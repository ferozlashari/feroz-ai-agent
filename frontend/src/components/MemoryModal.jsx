import React, { useEffect, useState } from 'react'
import { Loader2, Plus, Trash2, X } from 'lucide-react'
import { api } from '../api'

export default function MemoryModal({ onClose }) {
  const [items, setItems] = useState(null)
  const [text, setText] = useState('')
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState('')

  const load = () =>
    api
      .memoryList()
      .then((r) => setItems(r.items))
      .catch((e) => setErr(e.message))

  useEffect(() => {
    load()
  }, [])

  async function add() {
    const t = text.trim()
    if (!t) return
    setBusy(true)
    try {
      await api.memoryAdd(t)
      setText('')
      await load()
    } catch (e) {
      setErr(e.message)
    } finally {
      setBusy(false)
    }
  }

  async function del(id) {
    setItems((its) => its.filter((i) => i.id !== id))
    try {
      await api.memoryDelete(id)
    } catch (e) {
      setErr(e.message)
      load()
    }
  }

  return (
    <div className="modal-back" onMouseDown={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal" role="dialog" aria-modal="true" aria-label="Yaaddasht">
        <div className="modal-head">
          <h2>Yaaddasht</h2>
          <button type="button" className="icon-btn" onClick={onClose} aria-label="Band karo">
            <X size={18} />
          </button>
        </div>
        <div className="modal-body">
          <p className="muted-note">Ye baatein har chat me AI ko yaad rehti hain. Khud bhi kuch add ya mita sakte ho.</p>
          {err && <div className="err-box"><p>{err}</p></div>}

          <div className="mem-add">
            <input
              value={text}
              dir="auto"
              placeholder="Jaise: Mujhe Python pasand hai, chhote jawab pasand hain…"
              onChange={(e) => setText(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && add()}
            />
            <button type="button" className="btn btn-primary" onClick={add} disabled={busy || !text.trim()}>
              {busy ? <Loader2 size={15} className="spin" /> : <Plus size={15} />}
            </button>
          </div>

          {items === null ? (
            <div className="thinking"><Loader2 size={15} className="spin" /> Load ho raha hai…</div>
          ) : items.length === 0 ? (
            <p className="muted-note">Abhi kuch yaad nahi hai.</p>
          ) : (
            <ul className="mem-list">
              {items.map((it) => (
                <li key={it.id}>
                  <span dir="auto">{it.text}</span>
                  <button type="button" onClick={() => del(it.id)} aria-label="Mitao">
                    <Trash2 size={14} />
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  )
}
