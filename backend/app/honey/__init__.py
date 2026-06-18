"""Honey Encryption for a breached server's credential vault.

This package implements a Honey Encryption scheme (Juels & Ristenpart, 2014):
every decryption key — right or wrong — yields a *believable* server credential,
so an attacker who brute-forces the vault drowns in plausible fakes and can never
tell which result (if any) is the real one.
"""

from .dte import SEED_SPACE, ACCOUNTS, decode_seed, FakeCredential
from .encryption import DEFAULT_ITERATIONS, honey_encrypt, honey_decrypt

__all__ = [
    "SEED_SPACE",
    "ACCOUNTS",
    "decode_seed",
    "FakeCredential",
    "DEFAULT_ITERATIONS",
    "honey_encrypt",
    "honey_decrypt",
]
