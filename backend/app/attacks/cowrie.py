"""Adapter that turns a real Cowrie honeypot's JSON log into Chaff events.

Cowrie (https://github.com/cowrie/cowrie) writes one JSON object per line. We
care about its login attempts; each is mapped to the same event shape the globe
already consumes, so swapping the simulator for real data is a drop-in change:

    export CHAFF_COWRIE_LOG=/path/to/cowrie/var/log/cowrie/cowrie.json

Geolocation uses MaxMind GeoLite2 when available (set CHAFF_GEOIP_DB and
`pip install geoip2`); otherwise it falls back to a deterministic location
derived from the IP so the globe still lights up.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone

from .data import HONEYPOT, SOURCES

try:  # optional dependency, only needed for precise geolocation
    import geoip2.database
except Exception:  # noqa: BLE001
    geoip2 = None

_ATTACK_EVENTS = {
    "cowrie.login.failed",
    "cowrie.login.success",
    "cowrie.session.connect",
}
_PROTOCOL_SERVICE = {"ssh": (22, "SSH"), "telnet": (23, "Telnet")}
_reader = None  # cached GeoIP reader (or False once we know there isn't one)


def _geoip_reader():
    global _reader
    if _reader is not None:
        return _reader or None
    db = os.environ.get("CHAFF_GEOIP_DB")
    if not db or geoip2 is None:
        _reader = False
        return None
    try:
        _reader = geoip2.database.Reader(db)
    except Exception:  # noqa: BLE001
        _reader = False
    return _reader or None


def _fallback_geo(ip: str):
    """Deterministically map an IP to a plausible location (no GeoIP DB needed)."""
    h = int(hashlib.sha256(ip.encode("utf-8")).hexdigest(), 16)
    city, cc, lat, lon, _ = SOURCES[h % len(SOURCES)]
    lat = max(-85.0, min(85.0, lat + (((h >> 8) % 1000) / 100.0 - 5.0)))
    lon = max(-180.0, min(180.0, lon + (((h >> 18) % 1000) / 100.0 - 5.0)))
    return city, cc, lat, lon


def resolve_geo(ip: str):
    """Return (city, country_code, lat, lon) for an IP."""
    reader = _geoip_reader()
    if reader is not None:
        try:
            resp = reader.city(ip)
            if resp.location.latitude is not None and resp.location.longitude is not None:
                return (
                    resp.city.name or resp.country.name or ip,
                    resp.country.iso_code or "??",
                    float(resp.location.latitude),
                    float(resp.location.longitude),
                )
        except Exception:  # noqa: BLE001
            pass
    return _fallback_geo(ip)


def parse_cowrie_event(obj: dict, geo=resolve_geo) -> dict | None:
    """Map one Cowrie log object to AttackEvent fields, or None if irrelevant."""
    if obj.get("eventid") not in _ATTACK_EVENTS:
        return None
    ip = obj.get("src_ip")
    if not ip:
        return None
    city, cc, lat, lon = geo(ip)
    port, service = _PROTOCOL_SERVICE.get((obj.get("protocol") or "ssh").lower(), (22, "SSH"))
    return {
        "timestamp": obj.get("timestamp") or datetime.now(timezone.utc).isoformat(),
        "ip": ip,
        "city": city,
        "country_code": cc,
        "lat": lat,
        "lon": lon,
        "target_lat": HONEYPOT["lat"],
        "target_lon": HONEYPOT["lon"],
        "port": port,
        "service": service,
        "username": obj.get("username", ""),
        "password": obj.get("password", ""),
    }


class CowrieTailer:
    """Incrementally read newly-appended login events from a Cowrie JSON log."""

    def __init__(self, path: str, geo=resolve_geo) -> None:
        self.path = path
        self.geo = geo
        self._pos = 0

    def poll(self) -> list[dict]:
        """Return AttackEvent-field dicts for lines added since the last poll."""
        events: list[dict] = []
        try:
            with open(self.path, "r", encoding="utf-8", errors="ignore") as handle:
                handle.seek(self._pos)
                for line in handle:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    fields = parse_cowrie_event(obj, self.geo)
                    if fields:
                        events.append(fields)
                self._pos = handle.tell()
        except FileNotFoundError:
            pass
        return events
