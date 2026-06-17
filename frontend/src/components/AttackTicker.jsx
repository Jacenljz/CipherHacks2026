import { flag } from '../util'

export default function AttackTicker({ events }) {
  return (
    <div className="panel">
      <h2>Live Attacks</h2>
      <div className="ticker">
        {events.slice(0, 12).map((e) => (
          <div className="tick" key={e.id}>
            <span className="flag">{flag(e.country_code)}</span>
            <span className="src">{e.city}</span>
            <span className="svc">{e.service}:{e.port}</span>
            <span className="cred">{e.username ? `${e.username}/${e.password}` : 'connect'}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
