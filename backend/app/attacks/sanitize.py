"""Mask profanity in attacker-supplied strings.

Honeypot input is whatever the internet (and curious testers) throw at it, so
usernames/passwords can be offensive. We mask known bad words before they reach
the public leaderboard / live feed, keeping the demo presentable while still
showing authentic attack data.
"""

from __future__ import annotations

import re

# Curated so the substrings don't appear inside common innocent passwords
# (e.g. no bare "ass" — it lives inside "password").
_BAD = [
    "motherfuck", "fuck", "shit", "bitch", "cunt", "pussy", "nigger", "nigga",
    "faggot", "asshole", "whore", "slut", "dildo", "blowjob", "penis", "vagina",
    "dick", "cock", "porn", "retard", "bastard", "wank",
]
_PATTERN = re.compile("|".join(re.escape(w) for w in _BAD), re.IGNORECASE)


def clean(text: str) -> str:
    """Replace any profane substring with asterisks of the same length."""
    if not text:
        return text
    return _PATTERN.sub(lambda m: "*" * len(m.group()), text)
