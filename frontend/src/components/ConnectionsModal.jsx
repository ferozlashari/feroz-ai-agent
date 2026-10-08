import React, { useEffect, useState } from 'react'
import { Check, ExternalLink, Loader2, Trash2, X } from 'lucide-react'
import { api } from '../api'

function PlatformRow({ item, onSaved }) {
  const [open, setOpen] = useState(false)
  const [values, setValues] = useState(() => Object.fromEntries(item.fields.map(([k]) => [k, ''])))
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState('')

  async function save() {
    setBusy(true)
    setErr('')
    try {
      await api.connectionSave(item.platform, values)
      setOpen(false)
      onSaved()
    } catch (e) {
      setErr(e.message)
    } finally {
      setBusy(false)
    }
  }

  async function disconnect() {
    setBusy(true)
    try {
      await api.connectionDelete(item.platform)
      onSaved()
    } catch (e) {
      setErr(e.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="conn-row">
      <div className="conn-head">
        <span className={`dot ${item.connected ? 'ok' : ''}`} />
        <strong>{item.label}</strong>
        <span className="conn-state">{item.connected ? 'Connected' : 'Connected nahi'}</span>
        <button type="button" className="chip" onClick={() => setOpen((o) => !o)}>
          {item.connected ? 'Badlo' : 'Connect karo'}
        </button>
        {item.connected && (
          <button type="button" className="chip chip-ghost" onClick={disconnect} disabled={busy} aria-label="Disconnect">
            <Trash2 size={13} />
          </button>
        )}
      </div>

      {open && (
        <div className="conn-form">
          <p className="muted-note">{item.help}</p>
          {item.fields.map(([key, label]) => (
            <label key={key} className="field">
              <span>{label}</span>
              <input
                type={/token|secret|key/i.test(key) ? 'password' : 'text'}
                value={values[key]}
                autoComplete="off"
                onChange={(e) => setValues((v) => ({ ...v, [key]: e.target.value }))}
              />
            </label>
          ))}
          {err && <div className="err-box"><p>{err}</p></div>}
          <button type="button" className="btn btn-primary" onClick={save} disabled={busy}>
            {busy ? <Loader2 size={15} className="spin" /> : <Check size={15} />} Save
          </button>
        </div>
      )}
    </div>
  )
}

export default function ConnectionsModal({ onClose }) {
  const [items, setItems] = useState(null)
  const [err, setErr] = useState('')

  const load = () =>
    api
      .connections()
      .then((r) => setItems(r.items))
      .catch((e) => setErr(e.message))

  useEffect(() => {
    load()
  }, [])

  return (
    <div className="modal-back" onMouseDown={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal" role="dialog" aria-modal="true" aria-label="Connections">
        <div className="modal-head">
          <h2>Connections</h2>
          <button type="button" className="icon-btn" onClick={onClose} aria-label="Band karo">
            <X size={18} />
          </button>
        </div>
        <div className="modal-body">
          <p className="muted-note">
            Apne khud ke accounts se token le kar yahan daalo. Sirf isi computer ki local file me save hote hain, kahin
            aur nahi jaate. Post/message bhejne se pehle Copilot hamesha Allow/Deny poochta hai.
          </p>
          <p className="muted-note">
            <ExternalLink size={13} style={{ verticalAlign: 'text-bottom' }} /> Har platform ke saamne "Connect karo" dabao,
            wahan link diya hai ke token kahan se milega.
          </p>
          {err && <div className="err-box"><p>{err}</p></div>}
          {items === null ? (
            <div className="thinking"><Loader2 size={15} className="spin" /> Load ho raha hai…</div>
          ) : (
            <div className="conn-list">
              {items.map((it) => (
                <PlatformRow key={it.platform} item={it} onSaved={load} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
