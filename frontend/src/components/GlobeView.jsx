import { useEffect, useRef, useState } from 'react'
import Globe from 'react-globe.gl'

const SERVICE_COLORS = {
  SSH: '#ff3b5c',
  Telnet: '#ffb020',
  RDP: '#22d3ee',
  Redis: '#a855f7',
  MySQL: '#38bdf8',
  VNC: '#f472b6',
}
const colorFor = (service) => SERVICE_COLORS[service] || '#ff3b5c'

export default function GlobeView({ events, honeypot }) {
  const wrapRef = useRef(null)
  const globeRef = useRef(null)
  const [size, setSize] = useState({ width: 800, height: 600 })

  // Keep the globe sized to its container.
  useEffect(() => {
    const el = wrapRef.current
    if (!el) return
    const ro = new ResizeObserver(([entry]) => {
      const { width, height } = entry.contentRect
      setSize({ width, height })
    })
    ro.observe(el)
    return () => ro.disconnect()
  }, [])

  // Auto-rotate + initial camera position.
  useEffect(() => {
    const g = globeRef.current
    if (!g) return
    const controls = g.controls()
    controls.autoRotate = true
    controls.autoRotateSpeed = 0.55
    g.pointOfView({ lat: 25, lng: 12, altitude: 2.5 })
  }, [])

  const arcs = events.map((e) => ({
    startLat: e.lat,
    startLng: e.lon,
    endLat: e.target_lat,
    endLng: e.target_lon,
    color: colorFor(e.service),
  }))

  const points = events.slice(0, 60).map((e) => ({
    lat: e.lat,
    lng: e.lon,
    color: colorFor(e.service),
    size: 0.16,
  }))
  if (honeypot) {
    points.push({ lat: honeypot.lat, lng: honeypot.lon, color: '#39ff14', size: 0.5 })
  }

  const rings = honeypot ? [{ lat: honeypot.lat, lng: honeypot.lon }] : []

  return (
    <div className="globe-wrap" ref={wrapRef}>
      <Globe
        ref={globeRef}
        width={size.width}
        height={size.height}
        backgroundColor="rgba(0,0,0,0)"
        globeImageUrl="//unpkg.com/three-globe/example/img/earth-night.jpg"
        atmosphereColor="#3b82f6"
        atmosphereAltitude={0.18}
        arcsData={arcs}
        arcStartLat={(d) => d.startLat}
        arcStartLng={(d) => d.startLng}
        arcEndLat={(d) => d.endLat}
        arcEndLng={(d) => d.endLng}
        arcColor={(d) => [`${d.color}00`, d.color]}
        arcStroke={0.4}
        arcDashLength={0.45}
        arcDashGap={0.6}
        arcDashInitialGap={() => Math.random()}
        arcDashAnimateTime={1600}
        arcsTransitionDuration={0}
        pointsData={points}
        pointLat={(d) => d.lat}
        pointLng={(d) => d.lng}
        pointColor={(d) => d.color}
        pointAltitude={0.01}
        pointRadius={(d) => d.size}
        pointsMerge={false}
        ringsData={rings}
        ringColor={() => (t) => `rgba(57,255,20,${1 - t})`}
        ringMaxRadius={5}
        ringPropagationSpeed={3}
        ringRepeatPeriod={900}
      />
    </div>
  )
}
