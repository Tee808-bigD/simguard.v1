import { useEffect, useRef, useState, useCallback } from "react"
export function useWebSocket(onMessage) {
  const wsRef = useRef(null)
  const [connected, setConnected] = useState(false)
  const timerRef = useRef(null)
  const cbRef = useRef(onMessage)
  useEffect(() => { cbRef.current = onMessage }, [onMessage])
  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return
    const proto = window.location.protocol === "https:" ? "wss:" : "ws:"
    try {
      wsRef.current = new WebSocket(proto + "//" + window.location.host + "/ws/alerts")
      wsRef.current.onopen = () => setConnected(true)
      wsRef.current.onmessage = e => { try { cbRef.current(JSON.parse(e.data)) } catch(err){} }
      wsRef.current.onclose = () => { setConnected(false); timerRef.current = setTimeout(connect, 3000) }
      wsRef.current.onerror = () => wsRef.current?.close()
    } catch(e) { timerRef.current = setTimeout(connect, 3000) }
  }, [])
  useEffect(() => { connect(); return () => { clearTimeout(timerRef.current); wsRef.current?.close() } }, [connect])
  useEffect(() => { const i = setInterval(() => { if (wsRef.current?.readyState === WebSocket.OPEN) wsRef.current.send("ping") }, 30000); return () => clearInterval(i) }, [])
  return { connected }
}
