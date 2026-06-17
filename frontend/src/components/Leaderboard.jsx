import { flag } from '../util'

function Bars({ items, render }) {
  const max = Math.max(1, ...items.map((i) => i.count))
  return (
    <div>
      {items.map((i) => (
        <div className="bar-row" key={i.value}>
          <div className="label">
            <span className="v">{render ? render(i.value) : i.value}</span>
            <span className="c">{i.count}</span>
          </div>
          <div className="bar">
            <span style={{ width: `${(i.count / max) * 100}%` }} />
          </div>
        </div>
      ))}
    </div>
  )
}

export default function Leaderboard({ stats }) {
  const passwords = stats?.top_passwords || []
  const countries = stats?.top_countries || []
  return (
    <div className="panel">
      <h2>Attacker Leaderboard</h2>
      <div className="cols">
        <div>
          <h3>Top passwords</h3>
          <Bars items={passwords} />
        </div>
        <div>
          <h3>Top origins</h3>
          <Bars items={countries} render={(cc) => `${flag(cc)} ${cc}`} />
        </div>
      </div>
    </div>
  )
}
