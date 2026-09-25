"""Presidio recognizers for Moroccan identifiers.

Each class is a standard :class:`~presidio_analyzer.PatternRecognizer`, so they
drop into an existing Presidio deployment without any change to the pipeline.

Two conventions are followed throughout:

* **Entity names carry the ISO country prefix** — ``MA_CIN``, ``MA_RIB`` — the
  same shape Presidio uses for ``US_SSN`` or ``ES_NIF``.
* **Context words are multilingual.** Moroccan documents mix French, Arabic and
  English in the same paragraph, so the context list that boosts a score has to
  as well.
"""

from __future__ import annotations

from typing import ClassVar

from presidio_analyzer import Pattern, PatternRecognizer

from .checksums import is_not_repeated_digits, is_valid_iban, is_valid_rib

MA = "ma"


class MoroccanCINRecognizer(PatternRecognizer):
    """Moroccan national identity card number (CIN / CNIE).

    One or two letters encoding the region of first issue, then 5 or 6 digits
    (``A123456``, ``BE12345``). There is no check digit in the printed number,
    so the score stays moderate and leans on context words to rise.
    """

    COUNTRY_CODE: ClassVar[str | None] = MA

    PATTERNS: ClassVar[list[Pattern]] = [
        # Two letters is the more distinctive shape, so it scores higher than
        # the single-letter form, which collides with part numbers.
        Pattern("CIN (two letters)", r"\b[A-Z]{2}\d{5,6}\b", 0.5),
        Pattern("CIN (one letter)", r"\b[A-Z]\d{5,6}\b", 0.35),
    ]

    # Presidio's context enhancer compares single token lemmas, so each entry
    # has to be one word: a multi-word phrase would never match.
    CONTEXT: ClassVar[list[str]] = [
        "cin",
        "cnie",
        "carte",
        "nationale",
        "national",
        "identite",
        "identité",
        "identity",
        "card",
        "بطاقة",
        "التعريف",
        "الوطنية",
    ]

    def __init__(
        self,
        patterns: list[Pattern] | None = None,
        context: list[str] | None = None,
        supported_language: str = "en",
        supported_entity: str = "MA_CIN",
    ) -> None:
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns if patterns else self.PATTERNS,
            context=context if context else self.CONTEXT,
            supported_language=supported_language,
            # Case matters: lowercase runs in prose are words far more often
            # than identifiers, so the default IGNORECASE is dropped here.
            global_regex_flags=0,
        )

    def invalidate_result(self, pattern_text: str) -> bool | None:
        """Reject placeholder numbers such as ``A000000``."""
        return not is_not_repeated_digits(pattern_text)


class MoroccanPhoneRecognizer(PatternRecognizer):
    """Moroccan phone number, mobile or landline.

    Nine national digits after the country code, beginning with 5 (landline)
    or 6/7 (mobile). Accepts ``+212``, ``00212`` or a national leading zero,
    with spaces, dots or dashes between groups.
    """

    COUNTRY_CODE: ClassVar[str | None] = MA

    PATTERNS: ClassVar[list[Pattern]] = [
        # An explicit country code is unambiguous, so it scores highest.
        Pattern(
            "MA phone (international)",
            r"(?<![\d+])(?:\+|00)212[\s.\-]?[5-7](?:[\s.\-]?\d){8}(?!\d)",
            0.7,
        ),
        Pattern(
            "MA phone (national)",
            r"(?<![\d+])0[5-7](?:[\s.\-]?\d){8}(?!\d)",
            0.5,
        ),
    ]

    CONTEXT: ClassVar[list[str]] = [
        "tel",
        "tél",
        "telephone",
        "téléphone",
        "portable",
        "mobile",
        "gsm",
        "fixe",
        "phone",
        "contact",
        "joindre",
        "appeler",
        "هاتف",
        "الهاتف",
        "محمول",
    ]

    def __init__(
        self,
        patterns: list[Pattern] | None = None,
        context: list[str] | None = None,
        supported_language: str = "en",
        supported_entity: str = "MA_PHONE_NUMBER",
    ) -> None:
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns if patterns else self.PATTERNS,
            context=context if context else self.CONTEXT,
            supported_language=supported_language,
        )

    def invalidate_result(self, pattern_text: str) -> bool | None:
        """Reject runs like ``0600000000``."""
        return not is_not_repeated_digits(pattern_text)


class MoroccanRIBRecognizer(PatternRecognizer):
    """Moroccan bank account number (RIB): 24 digits ending in a mod-97 key.

    The key is what makes this reliable — an arbitrary 24-digit string has
    roughly a 1-in-97 chance of passing, so asset tags and order references are
    left alone.
    """

    COUNTRY_CODE: ClassVar[str | None] = MA

    PATTERNS: ClassVar[list[Pattern]] = [
        # Low base score on purpose: validate_result raises a confirmed match
        # to full confidence, and drops everything that fails the key.
        Pattern("MA RIB (24 digits)", r"(?<!\d)(?:\d[\s.\-]?){23}\d(?!\d)", 0.3),
    ]

    CONTEXT: ClassVar[list[str]] = [
        "rib",
        "compte",
        "banque",
        "bancaire",
        "virement",
        "account",
        "bank",
        "حساب",
        "بنكي",
    ]

    def __init__(
        self,
        patterns: list[Pattern] | None = None,
        context: list[str] | None = None,
        supported_language: str = "en",
        supported_entity: str = "MA_RIB",
    ) -> None:
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns if patterns else self.PATTERNS,
            context=context if context else self.CONTEXT,
            supported_language=supported_language,
        )

    def validate_result(self, pattern_text: str) -> bool | None:
        """Confirm the mod-97 key. False makes Presidio discard the match."""
        return is_valid_rib(pattern_text)


class MoroccanIBANRecognizer(PatternRecognizer):
    """Moroccan IBAN: ``MA`` + 2 check digits + the 24-digit RIB.

    Presidio ships a generic ``IbanRecognizer``; this one exists so that a
    Moroccan IBAN is reported as ``MA_IBAN`` alongside the other MENA entities,
    and so it still works in deployments that disable the generic recognizer.
    """

    COUNTRY_CODE: ClassVar[str | None] = MA

    PATTERNS: ClassVar[list[Pattern]] = [
        Pattern("MA IBAN", r"\bMA[\s]?\d{2}(?:[\s]?[A-Z0-9]){24}\b", 0.3),
    ]

    CONTEXT: ClassVar[list[str]] = [
        "iban",
        "rib",
        "compte",
        "banque",
        "virement",
        "swift",
        "bic",
        "bank",
        "حساب",
        "بنكي",
    ]

    def __init__(
        self,
        patterns: list[Pattern] | None = None,
        context: list[str] | None = None,
        supported_language: str = "en",
        supported_entity: str = "MA_IBAN",
    ) -> None:
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns if patterns else self.PATTERNS,
            context=context if context else self.CONTEXT,
            supported_language=supported_language,
        )

    def validate_result(self, pattern_text: str) -> bool | None:
        """Confirm the ISO 7064 MOD-97-10 checksum."""
        return is_valid_iban(pattern_text)


class MoroccanICERecognizer(PatternRecognizer):
    """Moroccan company identifier (ICE): 15 digits.

    Nine digits for the company, four for the establishment, two control
    characters. The control characters are not publicly specified, so only
    placeholder runs can be rejected; the score relies on context.
    """

    COUNTRY_CODE: ClassVar[str | None] = MA

    PATTERNS: ClassVar[list[Pattern]] = [
        Pattern("MA ICE (15 digits)", r"(?<!\d)(?:\d[\s.\-]?){14}\d(?!\d)", 0.4),
    ]

    CONTEXT: ClassVar[list[str]] = [
        "ice",
        "identifiant",
        "entreprise",
        "societe",
        "société",
        "facture",
        "company",
        "المقاول",
        "المعرف",
    ]

    def __init__(
        self,
        patterns: list[Pattern] | None = None,
        context: list[str] | None = None,
        supported_language: str = "en",
        supported_entity: str = "MA_ICE",
    ) -> None:
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns if patterns else self.PATTERNS,
            context=context if context else self.CONTEXT,
            supported_language=supported_language,
        )

    def invalidate_result(self, pattern_text: str) -> bool | None:
        """Reject placeholder runs such as ``000000000000000``."""
        return not is_not_repeated_digits(pattern_text)
