"""Unit tests for the Honey Encryption core.

These prove the property that makes Mirage work: every key — right or wrong —
yields a believable, Luhn-valid card, and the real card only comes back for the
correct password.
"""

import unittest

from app.honey import (
    SEED_SPACE,
    decode_seed,
    encode_card,
    honey_decrypt,
    honey_encrypt,
    is_luhn_valid,
    luhn_check_digit,
)

# Small iteration count keeps the tests fast; production uses far more.
TEST_ITERATIONS = 1_000


class LuhnTests(unittest.TestCase):
    def test_known_valid_card(self):
        self.assertTrue(is_luhn_valid("4242424242424242"))

    def test_single_digit_flip_breaks_validity(self):
        self.assertFalse(is_luhn_valid("4242424242424241"))

    def test_check_digit_makes_payload_valid(self):
        for payload in ("424242424242424", "510510510510510", "000000000000000"):
            check = luhn_check_digit(payload)
            self.assertTrue(is_luhn_valid(payload + check))

    def test_rejects_non_digits(self):
        self.assertFalse(is_luhn_valid("4242-4242"))


class DteTests(unittest.TestCase):
    def test_decode_is_always_luhn_valid(self):
        for seed in (0, 1, 7, 12345, SEED_SPACE - 1, SEED_SPACE // 2):
            card = decode_seed(seed)
            self.assertEqual(len(card.number), 16)
            self.assertTrue(is_luhn_valid(card.number), seed)

    def test_encode_decode_round_trip(self):
        for seed in (0, 1, 9, 10, 999, 4242424243, SEED_SPACE - 1):
            card = decode_seed(seed)
            self.assertEqual(encode_card(card.number), seed % SEED_SPACE)

    def test_decode_produces_complete_identity(self):
        card = decode_seed(123456789)
        self.assertRegex(card.expiry, r"^\d{2}/\d{2}$")
        self.assertRegex(card.cvv, r"^\d{3}$")
        self.assertIn(" ", card.holder)


class HoneyEncryptionTests(unittest.TestCase):
    def setUp(self):
        self.real_card = decode_seed(4242424243).number  # 4242 4242 4242 4242
        self.password = "correct horse battery staple"
        self.blob = honey_encrypt(
            self.password, self.real_card, iterations=TEST_ITERATIONS
        )

    def test_correct_password_recovers_real_card(self):
        card = honey_decrypt(self.password, self.blob)
        self.assertEqual(card.number, self.real_card)

    def test_wrong_password_yields_valid_but_different_card(self):
        card = honey_decrypt("wrong-password", self.blob)
        self.assertTrue(is_luhn_valid(card.number))
        self.assertNotEqual(card.number, self.real_card)

    def test_decryption_is_deterministic(self):
        first = honey_decrypt("guess-123", self.blob)
        second = honey_decrypt("guess-123", self.blob)
        self.assertEqual(first.number, second.number)

    def test_brute_force_drowns_in_distinct_plausible_cards(self):
        numbers = {
            honey_decrypt(f"attempt-{i}", self.blob).number for i in range(60)
        }
        # Almost every guess should yield a fresh, valid card.
        self.assertGreater(len(numbers), 50)
        self.assertTrue(all(is_luhn_valid(n) for n in numbers))

    def test_ciphertext_is_within_seed_space(self):
        self.assertGreaterEqual(self.blob["ciphertext"], 0)
        self.assertLess(self.blob["ciphertext"], SEED_SPACE)


if __name__ == "__main__":
    unittest.main()
