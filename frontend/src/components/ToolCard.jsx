import React from 'react'
import {
  Award,
  BookOpen,
  Brain,
  Briefcase,
  Check,
  CloudSun,
  FileText,
  FolderOpen,
  Github,
  Globe,
  Hash,
  Instagram,
  KeyRound,
  Link2,
  Linkedin,
  Loader2,
  MessageCircle,
  Search,
  Shield,
  ShieldCheck,
  Terminal,
  Twitter,
  Wrench,
  X,
} from 'lucide-react'

const META = {
  write_file: { title: 'File likhna', Icon: FileText },
  run_command: { title: 'Command chalana', Icon: Terminal },
  read_file: { title: 'File padhna', Icon: FileText },
  list_files: { title: 'Files dekhna', Icon: FolderOpen },
  web_search: { title: 'Internet search', Icon: Search },
  fetch_url: { title: 'Webpage kholna', Icon: Globe },
  wikipedia: { title: 'Wikipedia', Icon: BookOpen },
  weather: { title: 'Mausam', Icon: CloudSun },
  remember: { title: 'Yaad rakhna', Icon: Brain },
  recall_memory: { title: 'Yaaddasht dekhna', Icon: Brain },
  check_password_strength: { title: 'Password check', Icon: KeyRound },
  generate_password: { title: 'Password banana', Icon: KeyRound },
  hash_text: { title: 'Hash nikalna', Icon: Hash },
  virustotal_lookup: { title: 'VirusTotal check', Icon: Shield },
  cve_lookup: { title: 'CVE search', Icon: Shield },
  headers_scan: { title: 'Security headers check', Icon: Shield },
  connections_status: { title: 'Connections dekhna', Icon: Link2 },
  job_search: { title: 'Job search', Icon: Briefcase },
  draft_cover_letter: { title: 'Cover letter likhna', Icon: Award },
  github_create_issue: { title: 'GitHub issue banana', Icon: Github },
  github_create_gist: { title: 'GitHub gist banana', Icon: Github },
  github_list_repos: { title: 'GitHub repos dekhna', Icon: Github },
  post_twitter: { title: 'Twitter/X par post', Icon: Twitter },
  post_linkedin: { title: 'LinkedIn par post', Icon: Linkedin },
  post_facebook: { title: 'Facebook par post', Icon: Link2 },
  post_instagram: { title: 'Instagram par post', Icon: Instagram },
  send_whatsapp: { title: 'WhatsApp message', Icon: MessageCircle },
}

const HIDE_VALUE = new Set(['password']) // card par password chhupa do

function Detail({ name, args }) {
  if (name === 'write_file') {
    const content = String(args?.content ?? '')
    const shown = content.length > 1500 ? content.slice(0, 1500) + '\n… (aage ka hissa chupa hai)' : content
    return (
      <>
        <div className="tool-line">
          <code>{args?.path}</code>
        </div>
        <pre className="tool-pre">{shown}</pre>
      </>
    )
  }
  if (name === 'run_command') {
    return (
      <pre className="tool-pre">
        <span className="prompt">$ </span>
        {args?.command}
      </pre>
    )
  }
  const entries = Object.entries(args || {})
  if (entries.length === 0) {
    return (
      <div className="tool-line">
        <code>.</code>
      </div>
    )
  }
  return (
    <div className="tool-kv">
      {entries.map(([k, v]) => (
        <div key={k} className="tool-line">
          <span className="k">{k}</span>
          <code>{HIDE_VALUE.has(k) ? '••••••••' : typeof v === 'string' ? v : JSON.stringify(v)}</code>
        </div>
      ))}
    </div>
  )
}

export default function ToolCard({ m, onAllow, onDeny, disabled }) {
  const meta = META[m.name] || { title: m.name, Icon: Wrench }
  const { Icon } = meta
  return (
    <div className={`tool tool-${m.status}`}>
      <div className="tool-head">
        <span className="tool-ico">{m.status === 'pending' ? <ShieldCheck size={16} /> : <Icon size={16} />}</span>
        <strong>{meta.title}</strong>
        <span className="tool-state">
          {m.status === 'pending' && 'Ijazat chahiye'}
          {m.status === 'running' && (
            <>
              <Loader2 size={13} className="spin" /> chal raha hai
            </>
          )}
          {m.status === 'done' && (
            <>
              <Check size={13} /> ho gaya
            </>
          )}
          {m.status === 'denied' && (
            <>
              <X size={13} /> deny kiya
            </>
          )}
          {m.status === 'error' && 'error'}
        </span>
      </div>

      <Detail name={m.name} args={m.args} />

      {m.status === 'pending' && (
        <div className="tool-actions">
          <button type="button" className="btn btn-allow" disabled={disabled} onClick={onAllow}>
            Allow
          </button>
          <button type="button" className="btn btn-deny" disabled={disabled} onClick={onDeny}>
            Deny
          </button>
        </div>
      )}

      {(m.status === 'done' || m.status === 'error') && m.content && (
        <details className="tool-result">
          <summary>Natija dekho</summary>
          <pre className="tool-pre">{m.content}</pre>
        </details>
      )}
    </div>
  )
}
