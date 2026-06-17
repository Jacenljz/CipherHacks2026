import { useEffect, useState } from 'react'
import { challengeVault, guessChallenge } from '../api'

// Peer-interactive proof: pick which card is "the real secret". You can't —
// every card is an equally valid Honey-Encryption output.
export default function SpotTheReal() {
  const [round, setRound] = useState(null)
  const [picked, setPicked] = useState(null)
  const [result, setResult] = useState(null)
  const [busy, setBusy] = useState(false)

  async function newRound() {
    setBusy(true)
    setPicked(null)
    setResult(null)
    try {
      setRound(await challengeVault(6))
    } catch {
      /* ignore */
    } finally {
      setBusy(false)
    }
  }

  useEffect(() => {
    newRound()
  }, [])

  async function pick(i) {
    if (result || !round) return
    setPicked(i)
    try {
      setResult(await guessChallenge(round.id, i))
    } catch {
      /* ignore */
    }
  }

  return (
    <div className="panel">
      <h2>🎴 Spot the Real Card</h2>
      <p className="note">
        One of these is the real secret; the other five are Honey-Encryption
        decoys. Can you tell which is real?
      </p>
      <div className="spot-grid">
        {round?.cards.map((c, i) => {
          let cls = 'spot-card'
          if (result) {
            if (i === result.real_index) cls += ' real'
            else if (i === picked) cls += ' wrong'
          } else if (i === picked) {
            cls += ' picked'
          }
          return (
            <button key={i} className={cls} onClick={() => pick(i)} disabled={!!result}>
              <span className="brand">{c.brand}</span>
              <span className="num">{c.number_pretty}</span>
              <span className="sub">
                {c.holder} · {c.expiry}
              </span>
            </button>
          )
        })}
      </div>
      {result && (
        <div className={`spot-verdict ${result.correct ? 'ok' : 'no'}`}>
          <span>
            {result.correct
              ? 'You guessed right — but only by luck. Nothing distinguished it from the decoys.'
              : "Wrong — and that's exactly the point. Every card is equally real."}
          </span>
          <button className="btn" onClick={newRound} disabled={busy}>
            New round
          </button>
        </div>
      )}
    </div>
  )
}
