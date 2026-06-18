import { useEffect, useRef, useState } from 'react'
import GlobeView from './components/GlobeView'
import VaultPanel from './components/VaultPanel'
import SpotTheReal from './components/SpotTheReal'
import Leaderboard from './components/Leaderboard'
import AttackTicker from './components/AttackTicker'
import { connectAttackStream } from './api'

const MAX_EVENTS = 70

export default function App() {
  const [events, setEvents] = useState([])
  const [stats, setStats] = useState(null)
  const [honeypot, setHoneypot] = useState(null)
  const wsRef = useRef(null)

  useEffect(() => {
    const ws = connectAttackStream({
      init: (m) => {
        setHoneypot(m.honeypot)
        setStats(m.stats)
        setEvents(m.events.slice(-MAX_EVENTS).reverse())
      },
      attack: (m) => setEvents((prev) => [m.event, ...prev].slice(0, MAX_EVENTS)),
      stats: (m) => setStats(m.stats),
    })
    wsRef.current = ws
    return () => ws.close()
  }, [])

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <h1>
            CHAFF<span className="dot">.</span>
          </h1>
          <span className="tag">
            Live cyber-deception battlestation · attackers steal only believable lies
          </span>
        </div>
        <div className="counters">
          <div className="counter">
            <div className="num">{(stats?.total ?? 0).toLocaleString()}</div>
            <div className="lbl">Attacks captured</div>
          </div>
          <div className="counter">
            <div className="num fake">{(stats?.decoys_served ?? 0).toLocaleString()}</div>
            <div className="lbl">Decoys served</div>
          </div>
        </div>
      </header>

      <div className="layout">
        <div className="globe-col">
          <GlobeView events={events} honeypot={honeypot} />
          <div className="globe-hint">
            Each arc is a real brute-force attempt against our honeypot. Anything an
            attacker steals from the vault is Honey-Encrypted — every crack yields a
            different, believable fake.
          </div>
        </div>
        <aside className="sidebar">
          <VaultPanel />
          <SpotTheReal />
          <Leaderboard stats={stats} />
          <AttackTicker events={events} />
        </aside>
      </div>
    </div>
  )
}
