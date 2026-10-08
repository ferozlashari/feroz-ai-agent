import { loadSettings } from './storage'

function makeError(message, status) {
  const err = new Error(message)
  err.status = status
  return err
}

async function request(path, init = {}) {
  const { accessKey } = loadSettings()
  const headers = { ...(init.headers || {}) }
  if (accessKey) headers['X-Access-Key'] = accessKey

  let res
  try {
    res = await fetch(`/api${path}`, { ...init, headers })
  } catch {
    throw makeError('Backend se rabta nahi ho raha. Kya backend (port 8000) chal raha hai?', 0)
  }

  if (!res.ok) {
    let detail = ''
    try {
      const j = await res.json()
      detail = typeof j.detail === 'string' ? j.detail : JSON.stringify(j.detail)
    } catch {
      detail = res.statusText
    }
    throw makeError(detail || `Error ${res.status}`, res.status)
  }
  return res
}

const post = (body) => ({
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(body),
})

const extFor = (type = '') =>
  type.includes('mp4') ? 'm4a' : type.includes('ogg') ? 'ogg' : type.includes('wav') ? 'wav' : 'webm'

export const api = {
  status: () => request('/status').then((r) => r.json()),
  chat: (body) => request('/chat', post(body)).then((r) => r.json()),
  exec: (name, args) => request('/tools/execute', post({ name, arguments: args || {} })).then((r) => r.json()),
  image: (prompt) => request('/image', post({ prompt, enhance: true })).then((r) => r.json()),
  tts: (text, voice) => request('/tts', post({ text, voice })).then((r) => r.blob()),
  stt: (blob, language) => {
    const form = new FormData()
    form.append('file', blob, `voice.${extFor(blob.type)}`)
    form.append('language', language || '')
    return request('/stt', { method: 'POST', body: form }).then((r) => r.json())
  },
  upload: (file) => {
    const form = new FormData()
    form.append('file', file)
    return request('/upload', { method: 'POST', body: form }).then((r) => r.json())
  },
  memoryList: () => request('/memory').then((r) => r.json()),
  memoryAdd: (text) => request('/memory', post({ text })).then((r) => r.json()),
  memoryDelete: (id) => request(`/memory/${id}`, { method: 'DELETE' }).then((r) => r.json()),
  connections: () => request('/connections').then((r) => r.json()),
  connectionSave: (platform, data) => request('/connections', post({ platform, data })).then((r) => r.json()),
  connectionDelete: (platform) => request(`/connections/${platform}`, { method: 'DELETE' }).then((r) => r.json()),
}
