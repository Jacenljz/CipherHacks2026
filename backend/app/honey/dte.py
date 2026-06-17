"""Distribution-Transforming Encoder (DTE) for credit cards.

The DTE is a bijection between a uniform *seed* space and the space of
believable credit cards. Because the mapping is a bijection onto valid cards,
decoding a uniformly random seed (what a wrong key produces) yields a uniformly
random — but entirely plausible — card.

A card is fully determined by:
  * a 6-digit issuer prefix (BIN), chosen from a fixed table, and
  * a 9-digit account number,
followed by a computed Luhn check digit (16 digits total).

Presentation fields (cardholder name, expiry, CVV) are derived deterministically
from the seed so every fake looks complete and distinct.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, asdict

from .luhn import luhn_check_digit

# (6-digit BIN prefix, brand label). These are illustrative issuer ranges.
BINS: list[tuple[str, str]] = [
    ("453201", "Visa"),
    ("414720", "Visa"),
    ("401288", "Visa"),
    ("424242", "Visa"),
    ("510510", "Mastercard"),
    ("520082", "Mastercard"),
    ("555555", "Mastercard"),
    ("222300", "Mastercard"),
    ("601100", "Discover"),
    ("650000", "Discover"),
]

ACCOUNT_DIGITS = 9
_ACCOUNT_RANGE = 10**ACCOUNT_DIGITS
# Size of the seed space: one slot per (BIN, account) pair.
SEED_SPACE = len(BINS) * _ACCOUNT_RANGE

_FIRST_NAMES = [
    "James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael",
    "Linda", "David", "Elizabeth", "William", "Barbara", "Richard", "Susan",
    "Wei", "Mei", "Carlos", "Sofia", "Ahmed", "Fatima",
]
_LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Chen", "Wang", "Kim", "Patel",
    "Nguyen", "Khan", "Silva", "Schmidt", "Rossi", "Dubois",
]


@dataclass(frozen=True)
class FakeCard:
    """A believable credit card produced by the DTE."""

    number: str
    brand: str
    holder: str
    expiry: str
    cvv: str

    @property
    def number_pretty(self) -> str:
        """Group the 16 digits into blocks of four for display."""
        return " ".join(self.number[i : i + 4] for i in range(0, len(self.number), 4))

    def to_dict(self) -> dict:
        data = asdict(self)
        data["number_pretty"] = self.number_pretty
        return data


def _derive_identity(seed: int) -> tuple[str, str, str]:
    """Derive a deterministic (holder, expiry, CVV) triple from the seed."""
    digest = hashlib.sha256(seed.to_bytes(8, "big")).digest()
    holder = f"{_FIRST_NAMES[digest[0] % len(_FIRST_NAMES)]} {_LAST_NAMES[digest[1] % len(_LAST_NAMES)]}"
    month = (digest[2] % 12) + 1
    year = 26 + (digest[3] % 6)  # 2026..2031
    expiry = f"{month:02d}/{year:02d}"
    cvv = f"{int.from_bytes(digest[4:6], 'big') % 1000:03d}"
    return holder, expiry, cvv


def decode_seed(seed: int) -> FakeCard:
    """Map a seed in [0, SEED_SPACE) to a believable, Luhn-valid card."""
    seed %= SEED_SPACE
    bin_index = seed % len(BINS)
    account = seed // len(BINS)
    prefix, brand = BINS[bin_index]
    body = f"{prefix}{account:0{ACCOUNT_DIGITS}d}"  # 15 digits
    number = body + luhn_check_digit(body)  # 16 digits
    holder, expiry, cvv = _derive_identity(seed)
    return FakeCard(number=number, brand=brand, holder=holder, expiry=expiry, cvv=cvv)


def encode_card(number: str) -> int:
    """Inverse of :func:`decode_seed`: map a real card number back to its seed."""
    digits = number.replace(" ", "")
    if len(digits) != 16 or not digits.isdigit():
        raise ValueError("card number must be 16 digits")
    prefix = digits[:6]
    account = int(digits[6:15])
    try:
        bin_index = next(i for i, (p, _) in enumerate(BINS) if p == prefix)
    except StopIteration as exc:
        raise ValueError(f"unknown issuer prefix: {prefix}") from exc
    return account * len(BINS) + bin_index
