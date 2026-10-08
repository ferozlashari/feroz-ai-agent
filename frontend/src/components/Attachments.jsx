import React from 'react'
import { File as FileIcon, Loader2, X } from 'lucide-react'

// Composer ke upar chhote thumbnails - jo images/PDF bheje jaane wale hain
export default function Attachments({ items, onRemove }) {
  if (!items.length) return null
  return (
    <div className="attach-row">
      {items.map((a) => (
        <div key={a.id} className="attach-chip">
          {a.uploading ? (
            <Loader2 size={16} className="spin" />
          ) : a.kind === 'image' ? (
            <img src={a.url} alt={a.name} />
          ) : (
            <FileIcon size={16} />
          )}
          <span dir="auto">{a.name}</span>
          <button type="button" onClick={() => onRemove(a.id)} aria-label="Hatao">
            <X size={13} />
          </button>
        </div>
      ))}
    </div>
  )
}
