"""The demo vault: one real card, protected by Honey Encryption.

The owner's password lives only on the server and is never exposed. An attacker
can POST any guess to /api/vault/crack and always gets a believable card back —
with no signal telling them whether it was the real one.
"""

from __future__ import annotations

import os
import random

from .honey import SEED_SPACE, decode_seed, encode_card, honey_decrypt, honey_encrypt

# Secret known only to the legitimate owner (server-side only, never returned).
VAULT_PASSWORD = os.environ.get("MIRAGE_VAULT_PASSWORD", "M1rage-Tr0ub4dor&3")
# The single real record the vault protects.
REAL_CARD = os.environ.get("MIRAGE_REAL_CARD", "4242424242424242")
VAULT_ITERATIONS = int(os.environ.get("MIRAGE_VAULT_ITERATIONS", "120000"))

_REAL_SEED = encode_card(REAL_CARD)
_BLOB = honey_encrypt(VAULT_PASSWORD, REAL_CARD, iterations=VAULT_ITERATIONS)

# Dictionary an automated attacker would throw at the vault.
WORDLIST = [
    "123456", "password", "12345678", "qwerty", "abc123", "monkey", "letmein",
    "dragon", "111111", "baseball", "iloveyou", "trustno1", "sunshine", "master",
    "welcome", "shadow", "ashley", "football", "jesus", "ninja", "mustang",
    "password1", "admin", "root", "hunter2", "summer2024", "p@ssw0rd", "123123",
    "qwerty123", "superman",
]


def metadata() -> dict:
    return {
        "label": "ACME Corp — customer card vault",
        "records": 1,
        "scheme": "Honey Encryption (PBKDF2-HMAC-SHA256 + DTE)",
        "iterations": VAULT_ITERATIONS,
        "note": (
            "Every password decrypts to a valid card. Only the owner's password "
            "returns the real one — and nothing reveals which result that is."
        ),
    }


def crack(password: str) -> dict:
    """Authentic Honey Encryption decryption of a single guess."""
    card = honey_decrypt(password, _BLOB)
    return {"guess": password, "card": card.to_dict()}


def _random_guess() -> str:
    guess = random.choice(WORDLIST)
    if random.random() < 0.4:
        guess += str(random.randint(0, 9999))
    return guess


def flood(count: int) -> list[dict]:
    """Simulate an automated dictionary run.

    A wrong password makes the recovered seed uniform over the seed space, so we
    draw uniform seeds directly here — mathematically identical to what real
    brute force yields, but without paying the PBKDF2 cost thousands of times.
    The real seed is skipped so the flood only ever shows decoys.
    """
    count = max(1, min(count, 200))
    results = []
    for _ in range(count):
        seed = random.randrange(SEED_SPACE)
        if seed == _REAL_SEED:
            seed = (seed + 1) % SEED_SPACE
        results.append({"guess": _random_guess(), "card": decode_seed(seed).to_dict()})
    return results
