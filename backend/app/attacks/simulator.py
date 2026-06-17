"""Generate a realistic stream of brute-force attempts for the globe."""

from __future__ import annotations

import random
from collections import Counter, deque
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone

from .data import CREDENTIALS, HONEYPOT, SERVICES, SOURCES

_SOURCE_WEIGHTS = [weight for *_, weight in SOURCES]


def _fake_public_ip() -> str:
    """Fabricate a plausible, publicly-routable-looking IPv4 for display."""
    first = random.choice([c for c in range(1, 224) if c not in (10, 127)])
    return f"{first}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"


@dataclass(frozen=True)
class AttackEvent:
    id: int
    timestamp: str
    ip: str
    city: str
    country_code: str
    lat: float
    lon: float
    target_lat: float
    target_lon: float
    port: int
    service: str
    username: str
    password: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AttackSimulator:
    """Stateful generator that also tracks leaderboards."""

    recent_limit: int = 200
    _next_id: int = 1
    total: int = 0
    _recent: deque = field(default_factory=lambda: deque(maxlen=200))
    _passwords: Counter = field(default_factory=Counter)
    _countries: Counter = field(default_factory=Counter)
    _usernames: Counter = field(default_factory=Counter)

    def random_event(self) -> AttackEvent:
        city, country_code, lat, lon, _ = random.choices(SOURCES, _SOURCE_WEIGHTS)[0]
        username, password = random.choice(CREDENTIALS)
        port, service = random.choice(SERVICES)

        event = AttackEvent(
            id=self._next_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            ip=_fake_public_ip(),
            city=city,
            country_code=country_code,
            lat=lat,
            lon=lon,
            target_lat=HONEYPOT["lat"],
            target_lon=HONEYPOT["lon"],
            port=port,
            service=service,
            username=username,
            password=password,
        )

        self._next_id += 1
        self.total += 1
        self._recent.append(event)
        self._passwords[password] += 1
        self._countries[country_code] += 1
        self._usernames[username] += 1
        return event

    @staticmethod
    def _top(counter: Counter, limit: int) -> list[dict]:
        return [{"value": value, "count": count} for value, count in counter.most_common(limit)]

    def stats(self) -> dict:
        return {
            "total": self.total,
            "top_passwords": self._top(self._passwords, 8),
            "top_countries": self._top(self._countries, 8),
            "top_usernames": self._top(self._usernames, 8),
        }

    def recent(self) -> list[dict]:
        return [event.to_dict() for event in self._recent]
