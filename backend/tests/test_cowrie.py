"""Tests for the Cowrie honeypot log adapter."""

import json
import os
import tempfile
import unittest

from app.attacks.cowrie import CowrieTailer, parse_cowrie_event, resolve_geo

LOGIN = {
    "eventid": "cowrie.login.failed",
    "src_ip": "203.0.113.7",
    "username": "root",
    "password": "123456",
    "protocol": "ssh",
    "timestamp": "2026-06-17T10:00:00Z",
}
NOISE = {"eventid": "cowrie.client.version", "src_ip": "203.0.113.7"}
CONNECT = {
    "eventid": "cowrie.session.connect",
    "src_ip": "203.0.113.7",
    "protocol": "telnet",
}

EVENT_FIELDS = {
    "timestamp", "ip", "city", "country_code", "lat", "lon",
    "target_lat", "target_lon", "port", "service", "username", "password",
}


class ParseTests(unittest.TestCase):
    def test_login_is_parsed_with_all_fields(self):
        fields = parse_cowrie_event(LOGIN)
        self.assertEqual(set(fields), EVENT_FIELDS)
        self.assertEqual(fields["ip"], "203.0.113.7")
        self.assertEqual(fields["username"], "root")
        self.assertEqual(fields["password"], "123456")
        self.assertEqual((fields["port"], fields["service"]), (22, "SSH"))

    def test_telnet_protocol(self):
        fields = parse_cowrie_event({**LOGIN, "protocol": "telnet"})
        self.assertEqual((fields["port"], fields["service"]), (23, "Telnet"))

    def test_non_attack_event_ignored(self):
        self.assertIsNone(parse_cowrie_event(NOISE))

    def test_connection_event_parsed_without_credentials(self):
        fields = parse_cowrie_event(CONNECT)
        self.assertIsNotNone(fields)
        self.assertEqual((fields["port"], fields["service"]), (23, "Telnet"))
        self.assertEqual(fields["username"], "")
        self.assertEqual(fields["password"], "")

    def test_event_without_ip_ignored(self):
        self.assertIsNone(parse_cowrie_event({"eventid": "cowrie.login.failed"}))


class GeoFallbackTests(unittest.TestCase):
    def test_deterministic_and_in_bounds(self):
        first = resolve_geo("198.51.100.23")
        second = resolve_geo("198.51.100.23")
        self.assertEqual(first, second)
        _, _, lat, lon = first
        self.assertTrue(-90 <= lat <= 90)
        self.assertTrue(-180 <= lon <= 180)


class TailerTests(unittest.TestCase):
    def test_reads_only_new_login_lines(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        try:
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(json.dumps(LOGIN) + "\n")
                handle.write("this is not json\n")
                handle.write(json.dumps(NOISE) + "\n")

            tailer = CowrieTailer(path)
            first = tailer.poll()
            self.assertEqual(len(first), 1)  # only the login line, noise skipped
            self.assertEqual(tailer.poll(), [])  # nothing new

            with open(path, "a", encoding="utf-8") as handle:
                handle.write(json.dumps({**LOGIN, "username": "admin"}) + "\n")
            second = tailer.poll()
            self.assertEqual(len(second), 1)
            self.assertEqual(second[0]["username"], "admin")
        finally:
            os.remove(path)


if __name__ == "__main__":
    unittest.main()
