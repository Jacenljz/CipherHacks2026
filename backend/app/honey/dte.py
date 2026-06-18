"""Distribution-Transforming Encoder (DTE) for server credentials.

The honeypot poses as a breached server / database. Its "loot" is a vault of
service credentials and secrets. The DTE maps a uniform seed to a believable
credential, so decrypting any key — right or wrong — yields a plausible (but
fake) secret. Brute force just drowns the attacker in convincing decoys.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, asdict

# 40-bit seed space. A power of two, so reducing a hash mod SEED_SPACE is
# perfectly uniform (no modulo bias) and the decoy pool is effectively endless.
SEED_SPACE = 1 << 40

# (account, service kind) — the kind of credentials a real server actually holds.
ACCOUNTS: list[tuple[str, str]] = [
    ("postgres", "PostgreSQL"),
    ("root", "SSH"),
    ("admin", "Admin Panel"),
    ("mysql", "MySQL"),
    ("redis", "Redis"),
    ("svc_deploy", "CI/CD"),
    ("aws_prod", "AWS IAM"),
    ("backup", "Backup"),
    ("jenkins", "Jenkins"),
    ("oracle", "Oracle DB"),
    ("api_gw", "API Gateway"),
    ("vault", "Secrets Vault"),
    ("mongo", "MongoDB"),
    ("elastic", "Elasticsearch"),
    ("grafana", "Grafana"),
    ("rabbitmq", "RabbitMQ"),
]

_HOST_PREFIXES = ["db-prod", "app-node", "vault", "cache", "gw", "worker", "k8s", "bastion"]
_B62 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"


@dataclass(frozen=True)
class FakeCredential:
    """A believable leaked credential produced by the DTE."""

    kind: str
    host: str
    username: str
    secret: str

    def to_dict(self) -> dict:
        return asdict(self)


def _token(digest: bytes, length: int = 28) -> str:
    """A base62 secret/token string derived from a digest."""
    n = int.from_bytes(digest, "big")
    out = []
    for _ in range(length):
        n, r = divmod(n, 62)
        out.append(_B62[r])
    return "".join(out)


def decode_seed(seed: int) -> FakeCredential:
    """Map a seed in [0, SEED_SPACE) to a believable server credential."""
    seed %= SEED_SPACE
    username, kind = ACCOUNTS[seed % len(ACCOUNTS)]
    h = hashlib.sha256(seed.to_bytes(8, "big")).digest()
    host = f"{_HOST_PREFIXES[h[0] % len(_HOST_PREFIXES)]}-{h[1] % 24 + 1:02d}.internal"
    return FakeCredential(kind=kind, host=host, username=username, secret=_token(h))
