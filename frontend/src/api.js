// Thin client for the Chaff backend. All URLs are relative so the same build
// works behind the Vite dev proxy and when served directly by FastAPI.

export async function fetchJSON(path, options) {
  const res = await fetch(path, options)
  if (!res.ok) throw new Error(`${path} -> ${res.status}`)
  return res.json()
}

const jsonPost = (path, body) =>
  fetchJSON(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })

export const getVaultMeta = () => fetchJSON('/api/vault')
export const crackVault = (password) => jsonPost('/api/vault/crack', { password })
export const floodVault = (count) => jsonPost('/api/vault/flood', { count })
export const challengeVault = (n = 6) => jsonPost('/api/vault/challenge', { n })
export const guessChallenge = (id, index) =>
  jsonPost('/api/vault/challenge/guess', { id, index })

// Open the live attack stream. `handlers` maps message type -> callback.
export function connectAttackStream(handlers) {
  const proto = window.location.protocol === 'https:' ? 'wss' : 'ws'
  const ws = new WebSocket(`${proto}://${window.location.host}/ws/attacks`)
  ws.onmessage = (ev) => {
    const msg = JSON.parse(ev.data)
    handlers[msg.type]?.(msg)
  }
  return ws
}
