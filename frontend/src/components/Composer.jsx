import React, { useEffect, useRef } from 'react'
import { ArrowUp, Loader2, Mic, Paperclip, Square } from 'lucide-react'
import Attachments from './Attachments.jsx'

const isTouch = typeof window !== 'undefined' && window.matchMedia?.('(pointer: coarse)').matches

export default function Composer({
  value,
  onChange,
  onSend,
  busy,
  blocked,
  placeholder,
  recording,
  transcribing,
  onMic,
  attachments,
  onRemoveAttachment,
  onPickFiles,
  showAttach,
}) {
  const ref = useRef(null)
  const fileRef = useRef(null)

  useEffect(() => {
    const el = ref.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 200) + 'px'
  }, [value])

  const uploading = attachments.some((a) => a.uploading)
  const canSend = (value.trim().length > 0 || attachments.length > 0) && !busy && !blocked && !uploading

  return (
    <div className="composer-wrap">
      <Attachments items={attachments} onRemove={onRemoveAttachment} />
      <div className={`composer ${recording ? 'is-recording' : ''}`}>
        {showAttach && (
          <>
            <input
              ref={fileRef}
              type="file"
              accept="image/png,image/jpeg,image/webp,image/gif,application/pdf"
              multiple
              hidden
              onChange={(e) => {
                if (e.target.files?.length) onPickFiles(e.target.files)
                e.target.value = ''
              }}
            />
            <button
              type="button"
              className="round attach"
              onClick={() => fileRef.current?.click()}
              disabled={blocked}
              aria-label="Photo ya PDF lagao"
              title="Photo ya PDF lagao"
            >
              <Paperclip size={18} />
            </button>
          </>
        )}
        <textarea
          ref={ref}
          rows={1}
          dir="auto"
          value={value}
          placeholder={recording ? 'Sun raha hoon… bol kar dobara mic dabao' : placeholder}
          disabled={blocked}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey && !isTouch) {
              e.preventDefault()
              if (canSend) onSend()
            }
          }}
        />
        <button
          type="button"
          className={`round mic ${recording ? 'on' : ''}`}
          onClick={onMic}
          disabled={transcribing || busy}
          aria-label={recording ? 'Recording rokho' : 'Bol kar likho'}
          title="Voice se likho"
        >
          {transcribing ? <Loader2 size={18} className="spin" /> : recording ? <Square size={16} /> : <Mic size={18} />}
        </button>
        <button type="button" className="round send" onClick={onSend} disabled={!canSend} aria-label="Bhejo">
          {busy ? <Loader2 size={18} className="spin" /> : <ArrowUp size={19} />}
        </button>
      </div>
    </div>
  )
}
