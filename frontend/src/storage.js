// Sab data sirf aapke browser (localStorage) me rehta hai.
export const K_SETTINGS = 'feroz.settings.v1'
export const K_CHATS = 'feroz.chats.v1'
export const K_ACTIVE = 'feroz.active.v1'

export const defaultSettings = {
  provider: 'auto', // auto | groq | gemini | cerebras | mistral | openrouter | huggingface | ollama
  replyStyle: 'auto', // auto | roman_urdu | urdu | english
  userName: '',
  customInstructions: '',
  accessKey: '',
  autoSpeak: false,
  autoSend: true,
  voice: 'auto',
  sttLang: '',
  temperature: 0.7,
}

export const uid = () => Math.random().toString(36).slice(2, 10) + Date.now().toString(36)

export function loadSettings() {
  try {
    return { ...defaultSettings, ...JSON.parse(localStorage.getItem(K_SETTINGS) || '{}') }
  } catch {
    return { ...defaultSettings }
  }
}

export function saveSettings(s) {
  try {
    localStorage.setItem(K_SETTINGS, JSON.stringify(s))
  } catch {
    /* ignore */
  }
}

export function newChat(mode = 'chat') {
  return { id: uid(), title: 'Nayi chat', mode, messages: [], updated: Date.now() }
}

export function loadChats() {
  try {
    const raw = JSON.parse(localStorage.getItem(K_CHATS) || '[]')
    if (!Array.isArray(raw)) return []
    // Page reload ho jaye to "running" wale actions dobara ijazat maangen
    return raw.map((c) => ({
      ...c,
      messages: (c.messages || []).map((m) => (m.status === 'running' ? { ...m, status: 'pending' } : m)),
    }))
  } catch {
    return []
  }
}

export function saveChats(chats) {
  try {
    localStorage.setItem(K_CHATS, JSON.stringify(chats))
  } catch (e) {
    console.warn('Chats save nahi hui (storage full?)', e)
  }
}
