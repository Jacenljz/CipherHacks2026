"""Mask profanity in attacker-supplied strings.

Honeypot input is whatever the internet (and curious testers) throw at it, so
usernames/passwords can be offensive. We mask known bad words before they reach
the public leaderboard / live feed, keeping the demo presentable while still
showing authentic attack data.
"""

from __future__ import annotations

import re

# Only the genuinely toxic words (the c-word + slurs) are masked. Common swears
# like "fuck" are intentionally left visible as authentic attacker rage. Curated
# so the substrings don't appear inside innocent passwords.
_BAD = [
    "cunt", "nigger", "nigga", "faggot", "retard", "tranny",
]
_PATTERN = re.compile("|".join(re.escape(w) for w in _BAD), re.IGNORECASE)


def clean(text: str) -> str:
    """Replace any profane substring with asterisks of the same length."""
    if not text:
        return text
    return _PATTERN.sub(lambda m: "*" * len(m.group()), text)
