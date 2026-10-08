import React from 'react'
import { Brain, Image as ImageIcon, Link2, MessageSquare, Plus, Settings, ShieldCheck, Trash2 } from 'lucide-react'

const ICONS = { chat: MessageSquare, copilot: ShieldCheck, image: ImageIcon }

export default function Sidebar({ name, chats, activeId, open, status, onSelect, onNew, onDelete, onSettings, onMemory, onConnections }) {
  const sorted = [...chats].sort((a, b) => b.updated - a.updated)
  const providers = Object.entries(status?.provider_labels || {})
  return (
    <aside className={`sidebar ${open ? 'open' : ''}`}>
      <div className="brand">
        <span className="mark" aria-hidden="true" />
        <span className="brand-name">{name}</span>
      </div>

      <button type="button" className="btn btn-primary new" onClick={onNew}>
        <Plus size={16} /> Nayi chat
      </button>

      <nav className="chatlist" aria-label="Chats">
        {sorted.map((c) => {
          const Icon = ICONS[c.mode] || MessageSquare
          return (
            <div key={c.id} className={`chatitem ${c.id === activeId ? 'active' : ''}`}>
              <button type="button" className="chatbtn" onClick={() => onSelect(c.id)} title={c.title}>
                <Icon size={15} />
                <span dir="auto">{c.title}</span>
              </button>
              <button type="button" className="del" onClick={() => onDelete(c.id)} aria-label="Chat mitao">
                <Trash2 size={14} />
              </button>
            </div>
          )
        })}
      </nav>

      <div className="side-foot">
        {providers.length > 0 && (
          <div className="providers">
            {providers.map(([key, label]) => (
              <span
                key={key}
                className={`prov ${status?.providers?.[key] ? 'ok' : ''}`}
                title={status?.providers?.[key] ? 'Key mojood' : 'Key nahi'}
              >
                <i /> {label}
              </span>
            ))}
          </div>
        )}
        <button type="button" className="btn btn-quiet" onClick={onMemory}>
          <Brain size={16} /> Yaaddasht
        </button>
        <button type="button" className="btn btn-quiet" onClick={onConnections}>
          <Link2 size={16} /> Connections
        </button>
        <button type="button" className="btn btn-quiet" onClick={onSettings}>
          <Settings size={16} /> Settings
        </button>
      </div>
    </aside>
  )
}
