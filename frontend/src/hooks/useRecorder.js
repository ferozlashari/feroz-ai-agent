import { useRef, useState } from 'react'
import { api } from '../api'

// Mic se awaaz record karke backend (Groq Whisper) se text banata hai.
export function useRecorder({ onResult, onError, language }) {
  const [recording, setRecording] = useState(false)
  const [transcribing, setTranscribing] = useState(false)
  const recRef = useRef(null)
  const chunks = useRef([])
  // Hamesha latest callbacks use karne ke liye
  const cb = useRef({})
  cb.current = { onResult, onError, language }

  async function start() {
    if (!navigator.mediaDevices?.getUserMedia) {
      cb.current.onError?.(new Error('Mic sirf localhost ya https par chalta hai.'))
      return
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mime = ['audio/webm;codecs=opus', 'audio/webm', 'audio/mp4'].find((t) =>
        window.MediaRecorder?.isTypeSupported?.(t),
      )
      const rec = new MediaRecorder(stream, mime ? { mimeType: mime } : undefined)
      chunks.current = []
      rec.ondataavailable = (e) => e.data && e.data.size > 0 && chunks.current.push(e.data)
      rec.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop())
        const blob = new Blob(chunks.current, { type: rec.mimeType || 'audio/webm' })
        setTranscribing(true)
        try {
          const { text } = await api.stt(blob, cb.current.language)
          cb.current.onResult?.(text)
        } catch (e) {
          cb.current.onError?.(e)
        } finally {
          setTranscribing(false)
        }
      }
      rec.start()
      recRef.current = rec
      setRecording(true)
    } catch (e) {
      cb.current.onError?.(new Error('Mic ki ijazat nahi mili ya mic nahi mila.'))
    }
  }

  function stop() {
    const rec = recRef.current
    if (rec && rec.state !== 'inactive') rec.stop()
    setRecording(false)
  }

  return { recording, transcribing, toggle: () => (recording ? stop() : start()) }
}
