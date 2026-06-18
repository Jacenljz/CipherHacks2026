"""Tests for the profanity mask on attacker-supplied strings."""

import unittest

from app.attacks.sanitize import clean


class SanitizeTests(unittest.TestCase):
    def test_masks_toxic_words(self):
        # The c-word and slurs are masked; same length out.
        self.assertEqual(clean("cunt"), "****")
        self.assertEqual(clean("CUNT_xx"), "****_xx")

    def test_keeps_mild_swears(self):
        # Common attacker rage stays visible (intentional).
        for word in ("fuck", "fuck_you", "shit", "bitch"):
            self.assertEqual(clean(word), word)

    def test_keeps_clean_passwords(self):
        for pw in ("admin", "root", "123456", "password", "qwerty", "letmein"):
            self.assertEqual(clean(pw), pw)

    def test_handles_empty(self):
        self.assertEqual(clean(""), "")
