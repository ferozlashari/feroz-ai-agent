import React from 'react'
import { FileText, Loader2, RotateCcw, Square, Volume2 } from 'lucide-react'
import Markdown, { CopyButton } from './Markdown.jsx'

export default function Message({ m, name, speaking, onSpeak, onStop, onRetry }) {
  if (m.role === 'user') {
    return (
      <div className="msg user">
        <div className="user-col">
          {m.images?.length > 0 && (
            <div className="user-images">
              {m.images.map((src) => (
                <a key={src} href={src} target="_blank" rel="noreferrer">
                  <img src={src} alt="Attachment" loading="lazy" />
                </a>
              ))}
            </div>
          )}
          {m.files?.length > 0 && (
            <div className="user-files">
              {m.files.map((f) => (
                <span key={f} className="filepill">
                  <FileText size={13} /> {f}
                </span>
              ))}
            </div>
          )}
          {m.content && (
            <div className="bubble" dir="auto">
              {m.content}
            </div>
          )}
        </div>
      </div>
    )
  }

  if (m.error) {
    return (
      <div className="msg error">
        <div className="err-box">
          <strong>Masla aa gaya</strong>
          <p>{m.content}</p>
          {m.retryable && (
            <button type="button" className="chip" onClick={onRetry}>
              <RotateCcw size={14} /> Dubara koshish
            </button>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="msg assistant">
      <div className="who">
        <span className="who-name">{name}</span>
        {m.provider && <span className="who-meta">{m.provider}</span>}
      </div>

      {m.image ? (
        <figure className="genimg">
          <a href={m.image} target="_blank" rel="noreferrer">
            <img src={m.image} alt="Generated" loading="lazy" />
          </a>
          <figcaption dir="auto">{m.content}</figcaption>
        </figure>
      ) : (
        <Markdown>{m.content}</Markdown>
      )}

      {m.content && !m.image && (
        <div className="actions">
          {speaking ? (
            <button type="button" className="chip" onClick={onStop}>
              <Square size={13} /> Ruko
            </button>
          ) : (
            <button type="button" className="chip" onClick={onSpeak}>
              <Volume2 size={14} /> Suno
            </button>
          )}
          <CopyButton text={m.content} />
        </div>
      )}
    </div>
  )
}

export function Thinking({ label }) {
  return (
    <div className="msg assistant">
      <div className="thinking">
        <Loader2 size={15} className="spin" /> {label}
      </div>
    </div>
  )
}
