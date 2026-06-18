"""Unit tests for the Honey Encryption core (server-credential vault).

These prove the property that makes Chaff work: every key — right or wrong —
yields a believable credential, and the real one only comes back for the correct
password.
"""

import unittest

from app.honey import (
    ACCOUNTS,
    SEED_SPACE,
    decode_seed,
    honey_decrypt,
    honey_encrypt,
)

# Small iteration count keeps the tests fast; production uses far more.
TEST_ITERATIONS = 1_000

_USERNAMES = {u for u, _ in ACCOUNTS}


class DteTests(unittest.TestCase):
    def test_decode_produces_complete_credential(self):
        for seed in (0, 1, 7, 12345, SEED_SPACE - 1, SEED_SPACE // 2):
            cred = decode_seed(seed)
            self.assertIn(cred.username, _USERNAMES)
            self.assertTrue(cred.kind)
            self.assertTrue(cred.host.endswith(".internal"))
            self.assertEqual(len(cred.secret), 28)
            self.assertTrue(cred.secret.isalnum())

    def test_decode_is_deterministic(self):
        self.assertEqual(decode_seed(424242).to_dict(), decode_seed(424242).to_dict())

    def test_seed_wraps_into_space(self):
        self.assertEqual(decode_seed(SEED_SPACE + 5).to_dict(), decode_seed(5).to_dict())


class HoneyEncryptionTests(unittest.TestCase):
    def setUp(self):
        self.real_seed = 839571243017 % SEED_SPACE
        self.real_secret = decode_seed(self.real_seed).secret
        self.password = "correct horse battery staple"
        self.blob = honey_encrypt(
            self.password, self.real_seed, iterations=TEST_ITERATIONS
        )

    def test_correct_password_recovers_real_credential(self):
        cred = honey_decrypt(self.password, self.blob)
        self.assertEqual(cred.secret, self.real_secret)

    def test_wrong_password_yields_valid_but_different_credential(self):
        cred = honey_decrypt("wrong-password", self.blob)
        self.assertEqual(len(cred.secret), 28)
        self.assertIn(cred.username, _USERNAMES)
        self.assertNotEqual(cred.secret, self.real_secret)

    def test_decryption_is_deterministic(self):
        first = honey_decrypt("guess-123", self.blob)
        second = honey_decrypt("guess-123", self.blob)
        self.assertEqual(first.to_dict(), second.to_dict())

    def test_brute_force_drowns_in_distinct_plausible_secrets(self):
        secrets = {
            honey_decrypt(f"attempt-{i}", self.blob).secret for i in range(60)
        }
        self.assertGreater(len(secrets), 50)
        self.assertTrue(all(len(s) == 28 for s in secrets))

    def test_ciphertext_is_within_seed_space(self):
        self.assertGreaterEqual(self.blob["ciphertext"], 0)
        self.assertLess(self.blob["ciphertext"], SEED_SPACE)


if __name__ == "__main__":
    unittest.main()
