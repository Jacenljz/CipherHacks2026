import { useEffect, useMemo, useRef, useState } from 'react'
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

  // Cache one stable arc object per event id, so globe.gl keeps each arc's dash
  // animation flowing continuously instead of rebuilding (and restarting) every
  // arc whenever a new attack arrives — that's what made it look like a carousel.
  const arcCache = useRef(new Map())
  const arcs = useMemo(() => {
    const cache = arcCache.current
    const live = new Set()
    const list = events.map((e) => {
      live.add(e.id)
      let arc = cache.get(e.id)
      if (!arc) {
        const c = colorFor(e.service)
        arc = {
          startLat: e.lat,
          startLng: e.lon,
          endLat: e.target_lat,
          endLng: e.target_lon,
          color: [`${c}00`, c],
          dashInitialGap: Math.random() * 4,
        }
        cache.set(e.id, arc)
      }
      return arc
    })
    for (const id of cache.keys()) {
      if (!live.has(id)) cache.delete(id)
    }
    return list
  }, [events])

  const points = useMemo(() => {
    const pts = events.slice(0, 60).map((e) => ({
      lat: e.lat,
      lng: e.lon,
      color: colorFor(e.service),
      size: 0.16,
    }))
    if (honeypot) {
      pts.push({ lat: honeypot.lat, lng: honeypot.lon, color: '#39ff14', size: 0.5 })
    }
    return pts
  }, [events, honeypot])

  const rings = useMemo(
    () => (honeypot ? [{ lat: honeypot.lat, lng: honeypot.lon }] : []),
    [honeypot],
  )

  return (
    <div className="globe-wrap" ref={wrapRef}>
      <Globe
        ref={globeRef}
        width={size.width}
        height={size.height}
        backgroundColor="rgba(0,0,0,0)"
        globeImageUrl="/earth-night.jpg"
        atmosphereColor="#3b82f6"
        atmosphereAltitude={0.18}
        arcsData={arcs}
        arcStartLat={(d) => d.startLat}
        arcStartLng={(d) => d.startLng}
        arcEndLat={(d) => d.endLat}
        arcEndLng={(d) => d.endLng}
        arcColor={(d) => d.color}
        arcStroke={0.5}
        arcDashLength={0.4}
        arcDashGap={2}
        arcDashInitialGap={(d) => d.dashInitialGap}
        arcDashAnimateTime={2200}
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
