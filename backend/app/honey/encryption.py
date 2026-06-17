"""Honey Encryption built on top of the credit-card DTE.

Construction (simplified Juels & Ristenpart, 2014):

    encrypt:  seed       = DTE.encode(card)
              pad        = PBKDF2(password, salt)  mod SEED_SPACE
              ciphertext = (seed + pad)            mod SEED_SPACE

    decrypt:  seed'      = (ciphertext - pad')     mod SEED_SPACE
              card'      = DTE.decode(seed')

For the correct password ``pad' == pad`` so ``seed' == seed`` and the real card
comes back. For any wrong password ``pad'`` is pseudo-random, so ``seed'`` is
~uniform over the seed space and ``DTE.decode`` returns an unrelated but fully
believable card. The attacker has no oracle to tell the cases apart.

PBKDF2 also makes every guess costly, so the scheme resists brute force twice
over: by cost, and by hiding success.
"""

from __future__ import annotations

import hashlib
import secrets

from .dte import SEED_SPACE, decode_seed, encode_card, FakeCard

DEFAULT_ITERATIONS = 100_000
_SALT_BYTES = 16
_DERIVED_BYTES = 32


def _pad(password: str, salt: bytes, iterations: int) -> int:
    """Derive a seed-space-sized pad from the password using PBKDF2-HMAC-SHA256."""
    derived = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, iterations, dklen=_DERIVED_BYTES
    )
    # `_DERIVED_BYTES` (256 bits) is far larger than SEED_SPACE (~34 bits), so
    # reducing mod SEED_SPACE introduces only negligible modulo bias.
    return int.from_bytes(derived, "big") % SEED_SPACE


def honey_encrypt(
    password: str, card_number: str, iterations: int = DEFAULT_ITERATIONS
) -> dict:
    """Honey-encrypt a real card number under ``password``.

    Returns a JSON-serialisable blob: salt (hex), ciphertext (int), iterations.
    """
    seed = encode_card(card_number)
    salt = secrets.token_bytes(_SALT_BYTES)
    ciphertext = (seed + _pad(password, salt, iterations)) % SEED_SPACE
    return {"salt": salt.hex(), "ciphertext": ciphertext, "iterations": iterations}


def honey_decrypt(password: str, blob: dict) -> FakeCard:
    """Decrypt with any password; always returns a believable card."""
    salt = bytes.fromhex(blob["salt"])
    iterations = int(blob["iterations"])
    seed = (int(blob["ciphertext"]) - _pad(password, salt, iterations)) % SEED_SPACE
    return decode_seed(seed)
