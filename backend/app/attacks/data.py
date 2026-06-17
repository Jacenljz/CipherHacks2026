"""Static reference data for the attack simulator.

Locations are approximate city coordinates; weights lean toward the source
regions that dominate real SSH/Telnet honeypot logs. Credential pairs are the
classics that automated bots actually hammer exposed servers with.
"""

from __future__ import annotations

import os

# Where our decoy server lives. Defaults to GCP us-west2 (Los Angeles); override
# per deployment with the MIRAGE_HONEYPOT_* env vars.
HONEYPOT = {
    "city": os.environ.get("MIRAGE_HONEYPOT_CITY", "Los Angeles"),
    "country_code": os.environ.get("MIRAGE_HONEYPOT_CC", "US"),
    "lat": float(os.environ.get("MIRAGE_HONEYPOT_LAT", "34.05")),
    "lon": float(os.environ.get("MIRAGE_HONEYPOT_LON", "-118.24")),
}

# (city, country_code, latitude, longitude, weight)
SOURCES: list[tuple[str, str, float, float, int]] = [
    ("Beijing", "CN", 39.90, 116.40, 10),
    ("Shanghai", "CN", 31.23, 121.47, 8),
    ("Hong Kong", "HK", 22.32, 114.17, 5),
    ("Moscow", "RU", 55.75, 37.62, 9),
    ("Saint Petersburg", "RU", 59.93, 30.34, 5),
    ("New York", "US", 40.71, -74.01, 7),
    ("San Francisco", "US", 37.77, -122.42, 5),
    ("Ashburn", "US", 39.04, -77.49, 6),
    ("Amsterdam", "NL", 52.37, 4.90, 5),
    ("London", "GB", 51.51, -0.13, 4),
    ("Paris", "FR", 48.85, 2.35, 3),
    ("Kyiv", "UA", 50.45, 30.52, 4),
    ("Bucharest", "RO", 44.43, 26.10, 4),
    ("Sofia", "BG", 42.70, 23.32, 3),
    ("Istanbul", "TR", 41.01, 28.98, 4),
    ("Tehran", "IR", 35.69, 51.39, 4),
    ("Mumbai", "IN", 19.08, 72.88, 7),
    ("Bangalore", "IN", 12.97, 77.59, 5),
    ("Singapore", "SG", 1.35, 103.82, 5),
    ("Hanoi", "VN", 21.03, 105.85, 6),
    ("Ho Chi Minh City", "VN", 10.82, 106.63, 5),
    ("Jakarta", "ID", -6.21, 106.85, 5),
    ("Seoul", "KR", 37.57, 126.98, 4),
    ("Tokyo", "JP", 35.68, 139.65, 3),
    ("Taipei", "TW", 25.03, 121.57, 3),
    ("Sao Paulo", "BR", -23.55, -46.63, 6),
    ("Buenos Aires", "AR", -34.60, -58.38, 3),
    ("Lagos", "NG", 6.52, 3.38, 3),
    ("Cairo", "EG", 30.04, 31.24, 3),
    ("Johannesburg", "ZA", -26.20, 28.05, 2),
    ("Sydney", "AU", -33.87, 151.21, 2),
    ("Mexico City", "MX", 19.43, -99.13, 3),
    ("Toronto", "CA", 43.65, -79.38, 3),
    ("Warsaw", "PL", 52.23, 21.01, 3),
    ("Madrid", "ES", 40.42, -3.70, 2),
]

# (username, password) pairs straight out of real honeypot logs.
CREDENTIALS: list[tuple[str, str]] = [
    ("root", "root"),
    ("root", "123456"),
    ("root", "password"),
    ("root", "admin"),
    ("root", "12345"),
    ("root", "1234"),
    ("root", "toor"),
    ("root", "root123"),
    ("admin", "admin"),
    ("admin", "password"),
    ("admin", "1234"),
    ("admin", "admin123"),
    ("user", "user"),
    ("test", "test"),
    ("pi", "raspberry"),
    ("ubuntu", "ubuntu"),
    ("oracle", "oracle"),
    ("postgres", "postgres"),
    ("support", "support"),
    ("guest", "guest"),
]

# (port, service) the bots probe most.
SERVICES: list[tuple[int, str]] = [
    (22, "SSH"),
    (23, "Telnet"),
    (3389, "RDP"),
    (6379, "Redis"),
    (3306, "MySQL"),
    (5900, "VNC"),
]
