import { useEffect, useRef, useState } from 'react'
import { crackVault, floodVault, getVaultMeta } from '../api'

export default function VaultPanel() {
  const [meta, setMeta] = useState(null)
  const [password, setPassword] = useState('')
  const [result, setResult] = useState(null)
  const [flood, setFlood] = useState([])
  const [busy, setBusy] = useState(false)
  const floodTimer = useRef(null)

  useEffect(() => {
    getVaultMeta().then(setMeta).catch(() => {})
    return () => clearInterval(floodTimer.current)
  }, [])

  async function onCrack() {
    if (!password || busy) return
    setBusy(true)
    try {
      const r = await crackVault(password)
      setResult(r.card)
    } catch {
      /* ignore */
    } finally {
      setBusy(false)
    }
  }

  // Stream bursts of decoys so the fakes visibly pile up — this is what an
  // automated dictionary run looks like to the attacker: endless valid cards.
  function onFlood() {
    setFlood([])
    clearInterval(floodTimer.current)
    let rounds = 0
    floodTimer.current = setInterval(async () => {
      rounds += 1
      try {
        const { results } = await floodVault(12)
        setFlood((prev) => [...results, ...prev].slice(0, 60))
      } catch {
        /* ignore */
      }
      if (rounds >= 8) clearInterval(floodTimer.current)
    }, 600)
  }

  return (
    <div className="panel vault">
      <h2>🍯 Honey Vault</h2>
      {meta && (
        <div className="scheme">
          {meta.scheme} · {meta.iterations.toLocaleString()} iterations
        </div>
      )}
      {meta && <p className="note">{meta.note}</p>}

      <div className="row">
        <input
          type="text"
          placeholder="Enter a password to crack…"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && onCrack()}
        />
        <button className="btn primary" onClick={onCrack} disabled={busy}>
          Crack
        </button>
      </div>
      <div className="actions">
        <button className="btn danger" onClick={onFlood}>
          Run dictionary attack
        </button>
      </div>

      {result && (
        <div className="card">
          <div className="brand">{result.brand}</div>
          <div className="num">{result.number_pretty}</div>
          <div className="meta">
            <span>{result.holder}</span>
            <span>EXP {result.expiry}</span>
            <span>CVV {result.cvv}</span>
          </div>
        </div>
      )}

      {flood.length > 0 && (
        <div className="flood-list">
          {flood.map((r, i) => (
            <div className="flood-row" key={`${r.card.number}-${i}`}>
              <span className="g">{r.guess}</span>
              <span className="n">{r.card.number_pretty}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
