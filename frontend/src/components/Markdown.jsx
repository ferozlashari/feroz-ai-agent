import React, { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeHighlight from 'rehype-highlight'
import { Check, Copy } from 'lucide-react'

export async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text)
    return true
  } catch {
    // http (LAN) par clipboard API nahi hoti - purana tareeqa
    const ta = document.createElement('textarea')
    ta.value = text
    ta.style.position = 'fixed'
    ta.style.opacity = '0'
    document.body.appendChild(ta)
    ta.select()
    let ok = false
    try {
      ok = document.execCommand('copy')
    } catch {
      ok = false
    }
    document.body.removeChild(ta)
    return ok
  }
}

export function CopyButton({ text, label = 'Copy', className = 'chip' }) {
  const [done, setDone] = useState(false)
  return (
    <button
      type="button"
      className={className}
      onClick={async () => {
        if (await copyText(text)) {
          setDone(true)
          setTimeout(() => setDone(false), 1500)
        }
      }}
    >
      {done ? <Check size={14} /> : <Copy size={14} />}
      <span>{done ? 'Copy ho gaya' : label}</span>
    </button>
  )
}

function nodeText(node) {
  if (node == null || node === false) return ''
  if (typeof node === 'string' || typeof node === 'number') return String(node)
  if (Array.isArray(node)) return node.map(nodeText).join('')
  if (node.props) return nodeText(node.props.children)
  return ''
}

function Pre({ children }) {
  const codeEl = React.Children.toArray(children)[0]
  const cls = codeEl?.props?.className || ''
  const lang = (/language-([\w+-]+)/.exec(cls) || [])[1] || 'code'
  const inner = codeEl?.props?.children
  return (
    <div className="codeblock">
      <div className="codehead">
        <span>{lang}</span>
        <CopyButton text={nodeText(inner).replace(/\n$/, '')} className="chip chip-ghost" />
      </div>
      <pre>
        <code className={cls}>{inner}</code>
      </pre>
    </div>
  )
}

// dir="auto" ki wajah se Urdu (right-to-left) paragraph khud sahi taraf se dikhta hai
const auto = (Tag) =>
  function AutoDir({ node, ...props }) {
    return <Tag dir="auto" {...props} />
  }

const components = {
  pre: Pre,
  p: auto('p'),
  li: auto('li'),
  h1: auto('h1'),
  h2: auto('h2'),
  h3: auto('h3'),
  h4: auto('h4'),
  blockquote: auto('blockquote'),
  a: ({ node, ...props }) => <a {...props} target="_blank" rel="noreferrer" />,
  table: ({ node, ...props }) => (
    <div className="tablewrap">
      <table {...props} />
    </div>
  ),
}

export default function Markdown({ children }) {
  return (
    <div className="md">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[[rehypeHighlight, { ignoreMissing: true }]]}
        components={components}
      >
        {children || ''}
      </ReactMarkdown>
    </div>
  )
}
