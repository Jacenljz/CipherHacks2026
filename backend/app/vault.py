"""The demo vault: a breached server's real credential, protected by Honey
Encryption.

The owner's password lives only on the server and is never exposed. An attacker
can POST any guess to /api/vault/crack and always gets a believable credential
back — with no signal telling them whether it was the real one.
"""

from __future__ import annotations

import os
import random
import uuid

from .honey import SEED_SPACE, decode_seed, honey_decrypt, honey_encrypt

# Secret known only to the legitimate owner (server-side only, never returned).
VAULT_PASSWORD = os.environ.get("CHAFF_VAULT_PASSWORD", "Ch4ff-Tr0ub4dor&3")
# Stable seed of the one real credential the vault protects (override via env).
REAL_SEED = int(os.environ.get("CHAFF_REAL_SEED", "839571243017")) % SEED_SPACE
VAULT_ITERATIONS = int(os.environ.get("CHAFF_VAULT_ITERATIONS", "120000"))

_BLOB = honey_encrypt(VAULT_PASSWORD, REAL_SEED, iterations=VAULT_ITERATIONS)

# Dictionary an automated attacker would throw at the vault.
WORDLIST = [
    "123456", "password", "root", "admin", "toor", "letmein", "changeme",
    "qwerty", "P@ssw0rd", "root123", "admin123", "welcome", "monkey",
    "dragon", "111111", "iloveyou", "sunshine", "master", "shadow",
    "superman", "hunter2", "summer2024", "passw0rd", "123123", "qazwsx",
    "trustno1", "server2024", "postgres", "redis", "docker",
]

CHALLENGE_SIZE = 6
_decoys_served = 0
_challenges: dict[str, int] = {}


def metadata() -> dict:
    return {
        "label": "prod-db-01 — root credential vault",
        "records": 1,
        "scheme": "Honey Encryption (PBKDF2-HMAC-SHA256 + DTE)",
        "iterations": VAULT_ITERATIONS,
        "note": (
            "Every password decrypts to a valid credential. Only the owner's "
            "password returns the real one — and nothing reveals which result "
            "that is."
        ),
    }


def crack(password: str) -> dict:
    """Authentic Honey Encryption decryption of a single guess."""
    return {"guess": password, "record": honey_decrypt(password, _BLOB).to_dict()}


def _random_guess() -> str:
    guess = random.choice(WORDLIST)
    if random.random() < 0.4:
        guess += str(random.randint(0, 9999))
    return guess


def decoys_served() -> int:
    """Total number of believable decoy credentials Chaff has handed out."""
    return _decoys_served


def flood(count: int) -> list[dict]:
    """Simulate an automated dictionary run.

    A wrong password makes the recovered seed uniform over the seed space, so we
    draw uniform seeds directly here — mathematically identical to what real
    brute force yields, but without paying the PBKDF2 cost thousands of times.
    The real seed is skipped so the flood only ever shows decoys.
    """
    global _decoys_served
    count = max(1, min(count, 200))
    results = []
    for _ in range(count):
        seed = random.randrange(SEED_SPACE)
        if seed == REAL_SEED:
            seed = (seed + 1) % SEED_SPACE
        results.append({"guess": _random_guess(), "record": decode_seed(seed).to_dict()})
    _decoys_served += len(results)
    return results


def challenge(n: int = CHALLENGE_SIZE) -> dict:
    """Build a 'spot the real credential' round: one designated-real record among
    decoys. All are equally valid and plausible; the player cannot tell which is
    the secret. The real index is kept server-side.
    """
    global _decoys_served
    seeds: set[int] = set()
    while len(seeds) < n:
        seeds.add(random.randrange(SEED_SPACE))
    records = [decode_seed(s).to_dict() for s in seeds]
    real_index = random.randrange(n)
    cid = uuid.uuid4().hex
    if len(_challenges) > 100:
        _challenges.clear()
    _challenges[cid] = real_index
    _decoys_served += n - 1
    return {"id": cid, "records": records}


def guess_challenge(cid: str, index: int) -> dict:
    """Resolve a challenge guess; reveals the real index. A correct guess was
    only ever luck — there is no signal to distinguish the records."""
    if cid not in _challenges:
        return {"expired": True, "correct": False, "real_index": -1}
    real_index = _challenges.pop(cid)
    return {"expired": False, "correct": index == real_index, "real_index": real_index}
