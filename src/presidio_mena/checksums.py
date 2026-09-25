"""Check-digit algorithms for MENA identifiers.

Presidio calls these through each recognizer's ``validate_result``: a candidate
that matches the pattern but fails its checksum is dropped instead of being
reported, which is what keeps precision usable on real documents.

These few functions are deliberately duplicated rather than imported from a
shared package. Both this project and ``glpi-anonymizer`` are meant to be
auditable by people handling personal data, and a one-file dependency chain is
worth more here than the fifty lines it saves.
"""

from __future__ import annotations

import re

_NON_ALNUM = re.compile(r"[^A-Za-z0-9]")


def strip_separators(value: str) -> str:
    """Drop the spaces, dots and dashes people type inside identifiers."""
    return _NON_ALNUM.sub("", value)


def rib_check_key(first_22_digits: str) -> int:
    """Return the expected 2-digit key of a Moroccan RIB.

    ``97 - ((N * 100) mod 97)`` over the first 22 digits, so the key is 1..97.
    """
    return 97 - (int(first_22_digits) * 100) % 97


def is_valid_rib(value: str) -> bool:
    """True if ``value`` is a 24-digit Moroccan RIB carrying a correct key."""
    digits = strip_separators(value)
    if len(digits) != 24 or not digits.isdigit():
        return False
    return rib_check_key(digits[:22]) == int(digits[22:])


def is_valid_iban(value: str) -> bool:
    """Validate an IBAN with the ISO 7064 MOD-97-10 checksum."""
    cleaned = strip_separators(value).upper()
    if not re.fullmatch(r"[A-Z]{2}[0-9]{2}[A-Z0-9]{1,30}", cleaned):
        return False
    rearranged = cleaned[4:] + cleaned[:4]
    # A=10 ... Z=35, which is exactly base-36 parsing of a single character.
    numeric = "".join(str(int(char, 36)) for char in rearranged)
    return int(numeric) % 97 == 1


def is_not_repeated_digits(value: str) -> bool:
    """False when every digit is the same (000000000, A000000, ...).

    Placeholder runs like these appear constantly in test data and forms, and
    are never real identifiers. Only digits are considered, so a letter prefix
    such as a CIN's regional code does not hide the repetition.
    """
    digits = [char for char in value if char.isdigit()]
    if not digits:
        return True
    return len(set(digits)) > 1
