"""Honey Encryption for credit-card data.

This package implements a Honey Encryption scheme (Juels & Ristenpart, 2014):
every decryption key — right or wrong — yields a *believable* credit card, so
an attacker who brute-forces the vault drowns in plausible fakes and can never
tell which result (if any) is the real one.
"""

from .luhn import is_luhn_valid, luhn_check_digit
from .dte import SEED_SPACE, BINS, decode_seed, encode_card, FakeCard
from .encryption import DEFAULT_ITERATIONS, honey_encrypt, honey_decrypt

__all__ = [
    "is_luhn_valid",
    "luhn_check_digit",
    "SEED_SPACE",
    "BINS",
    "decode_seed",
    "encode_card",
    "FakeCard",
    "DEFAULT_ITERATIONS",
    "honey_encrypt",
    "honey_decrypt",
]
