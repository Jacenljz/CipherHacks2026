"""Luhn checksum helpers.

Every card number Mirage produces ends with a valid Luhn check digit, so an
attacker cannot filter out the fakes by validating the checksum — they all pass.
"""

from __future__ import annotations


def _luhn_sum(digits: str) -> int:
    """Sum used by the Luhn algorithm, doubling every second digit from the right."""
    total = 0
    # `reversed` so that "every second digit" is counted from the rightmost digit.
    for index, char in enumerate(reversed(digits)):
        value = int(char)
        if index % 2 == 1:
            value *= 2
            if value > 9:
                value -= 9
        total += value
    return total


def luhn_check_digit(payload: str) -> str:
    """Return the single check digit that makes ``payload + check`` Luhn-valid."""
    if not payload.isdigit():
        raise ValueError("payload must contain only digits")
    # The check digit sits in an even position (from the right) of the final
    # number, so it is added to the sum without doubling.
    remainder = _luhn_sum(payload + "0") % 10
    return str((10 - remainder) % 10)


def is_luhn_valid(number: str) -> bool:
    """Return True if ``number`` passes the Luhn checksum."""
    if not number or not number.isdigit():
        return False
    return _luhn_sum(number) % 10 == 0
