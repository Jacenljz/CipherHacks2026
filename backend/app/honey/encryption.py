"""Honey Encryption over server-credential seeds.

    encrypt:  ciphertext = (seed + PBKDF2(password, salt)) mod SEED_SPACE
    decrypt:  seed'      = (ciphertext - PBKDF2(password, salt)) mod SEED_SPACE
              cred'      = DTE.decode(seed')

Any password yields a valid seed -> a believable credential. Only the owner's
password recovers the real one, and nothing distinguishes the cases. PBKDF2 also
makes every guess costly, so brute force fails twice over: by cost, and by hiding
success in a sea of plausible decoys.
"""

from __future__ import annotations

import hashlib
import secrets

from .dte import SEED_SPACE, FakeCredential, decode_seed

DEFAULT_ITERATIONS = 100_000
_SALT_BYTES = 16
_DERIVED_BYTES = 32


def _pad(password: str, salt: bytes, iterations: int) -> int:
    """Derive a seed-space-sized pad from the password using PBKDF2-HMAC-SHA256."""
    derived = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, iterations, dklen=_DERIVED_BYTES
    )
    # SEED_SPACE is a power of two, so taking the low bits is exactly uniform.
    return int.from_bytes(derived, "big") % SEED_SPACE


def honey_encrypt(
    password: str, seed: int, iterations: int = DEFAULT_ITERATIONS
) -> dict:
    """Honey-encrypt the real credential's seed under ``password``."""
    salt = secrets.token_bytes(_SALT_BYTES)
    ciphertext = (seed + _pad(password, salt, iterations)) % SEED_SPACE
    return {"salt": salt.hex(), "ciphertext": ciphertext, "iterations": iterations}


def honey_decrypt(password: str, blob: dict) -> FakeCredential:
    """Decrypt with any password; always returns a believable credential."""
    salt = bytes.fromhex(blob["salt"])
    iterations = int(blob["iterations"])
    seed = (int(blob["ciphertext"]) - _pad(password, salt, iterations)) % SEED_SPACE
    return decode_seed(seed)
