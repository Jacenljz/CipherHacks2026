"""Tests for the profanity mask on attacker-supplied strings."""

import unittest

from app.attacks.sanitize import clean


class SanitizeTests(unittest.TestCase):
    def test_masks_profanity(self):
        self.assertEqual(clean("fuck"), "****")
        self.assertEqual(clean("FUCK_you"), "****_you")
        self.assertEqual(clean("----fuck----"), "----****----")

    def test_keeps_clean_passwords(self):
        for pw in ("admin", "root", "123456", "password", "qwerty", "letmein"):
            self.assertEqual(clean(pw), pw)

    def test_handles_empty(self):
        self.assertEqual(clean(""), "")
