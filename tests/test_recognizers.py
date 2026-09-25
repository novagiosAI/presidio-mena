from __future__ import annotations

import pytest

from presidio_mena import (
    MoroccanCINRecognizer,
    MoroccanIBANRecognizer,
    MoroccanICERecognizer,
    MoroccanPhoneRecognizer,
    MoroccanRIBRecognizer,
    rib_check_key,
)

VALID_IBAN = "MA64011519000001205000534921"


def make_rib(first_22: str = "0123456789012345678901") -> str:
    return first_22 + f"{rib_check_key(first_22):02d}"


def detect(recognizer, text: str, entity: str | None = None):
    """Run one recognizer standalone, the way Presidio calls it."""
    entities = [entity] if entity else recognizer.supported_entities
    return recognizer.analyze(text, entities)


class TestCIN:
    @pytest.fixture
    def recognizer(self):
        return MoroccanCINRecognizer()

    @pytest.mark.parametrize("cin", ["A123456", "BE12345", "AB123456", "K98765"])
    def test_detects_valid_shapes(self, recognizer, cin):
        assert detect(recognizer, f"CIN {cin}")

    def test_two_letter_form_scores_higher(self, recognizer):
        """The two-letter shape is more distinctive, so it must score above."""
        two = detect(recognizer, "BE12345")[0]
        one = detect(recognizer, "B123456")[0]
        assert two.score > one.score

    def test_lowercase_is_ignored(self, recognizer):
        assert not detect(recognizer, "the word abc12345 here")

    def test_placeholder_is_rejected(self, recognizer):
        """A000000 is a form placeholder, not an identity number."""
        assert not detect(recognizer, "CIN A000000")

    def test_entity_name_follows_presidio_convention(self, recognizer):
        assert recognizer.supported_entities == ["MA_CIN"]

    def test_country_is_tagged(self, recognizer):
        assert MoroccanCINRecognizer.COUNTRY_CODE == "ma"


class TestPhone:
    @pytest.fixture
    def recognizer(self):
        return MoroccanPhoneRecognizer()

    @pytest.mark.parametrize(
        "number",
        [
            "0612345678",
            "0712345678",
            "0522334455",
            "+212612345678",
            "+212 6 12 34 56 78",
            "00212612345678",
            "06 12 34 56 78",
            "06-12-34-56-78",
        ],
    )
    def test_detects_moroccan_numbers(self, recognizer, number):
        assert detect(recognizer, f"tel {number}"), number

    @pytest.mark.parametrize("number", ["0812345678", "0112345678"])
    def test_rejects_impossible_prefixes(self, recognizer, number):
        assert not detect(recognizer, number)

    def test_international_form_scores_higher(self, recognizer):
        """An explicit +212 is unambiguous; a bare 0... is not."""
        international = detect(recognizer, "+212612345678")[0]
        national = detect(recognizer, "0612345678")[0]
        assert international.score > national.score

    def test_placeholder_is_rejected(self, recognizer):
        assert not detect(recognizer, "0000000000")


class TestRIB:
    @pytest.fixture
    def recognizer(self):
        return MoroccanRIBRecognizer()

    def test_detects_a_valid_rib(self, recognizer):
        assert detect(recognizer, f"RIB {make_rib()}")

    def test_rejects_a_bad_check_key(self, recognizer):
        """This is the whole point: 24 digits is not enough."""
        valid = make_rib()
        broken = valid[:22] + ("00" if valid[22:] != "00" else "11")
        assert not detect(recognizer, broken)

    def test_validation_raises_the_score_to_certainty(self, recognizer):
        """A confirmed checksum should outrank the pattern's base score."""
        result = detect(recognizer, make_rib())[0]
        assert result.score > MoroccanRIBRecognizer.PATTERNS[0].score
        assert result.score >= 0.9

    def test_tolerates_grouping(self, recognizer):
        valid = make_rib()
        spaced = " ".join(valid[i : i + 4] for i in range(0, 24, 4))
        assert detect(recognizer, f"RIB {spaced}")

    def test_arbitrary_24_digit_numbers_are_mostly_rejected(self, recognizer):
        """Asset tags must survive an anonymization pass."""
        rejected = sum(not detect(recognizer, f"{n:024d}") for n in range(1000, 1200))
        assert rejected >= 190


class TestIBAN:
    @pytest.fixture
    def recognizer(self):
        return MoroccanIBANRecognizer()

    def test_detects_a_valid_iban(self, recognizer):
        assert detect(recognizer, f"IBAN {VALID_IBAN}")

    def test_rejects_wrong_check_digits(self, recognizer):
        assert not detect(recognizer, "MA65011519000001205000534921")

    def test_tolerates_grouping(self, recognizer):
        grouped = "MA64 0115 1900 0001 2050 0053 4921"
        assert detect(recognizer, grouped)


class TestICE:
    @pytest.fixture
    def recognizer(self):
        return MoroccanICERecognizer()

    def test_detects_15_digits(self, recognizer):
        assert detect(recognizer, "ICE 001234567000089")

    def test_ignores_other_lengths(self, recognizer):
        assert not detect(recognizer, "12345678")

    def test_placeholder_is_rejected(self, recognizer):
        assert not detect(recognizer, "000000000000000")


class TestNoFalsePositives:
    """Ordinary helpdesk and invoice prose must come through untouched."""

    @pytest.fixture
    def recognizers(self):
        return [
            MoroccanCINRecognizer(),
            MoroccanPhoneRecognizer(),
            MoroccanRIBRecognizer(),
            MoroccanIBANRecognizer(),
            MoroccanICERecognizer(),
        ]

    @pytest.mark.parametrize(
        "text",
        [
            "The printer on floor 3 is jammed again",
            "Error code 500 after restart",
            "Invoice total 1250.00 MAD paid on 2026-01-15",
            "Server rebooted at 14:35, uptime 12 days",
        ],
    )
    def test_ordinary_text_yields_nothing(self, recognizers, text):
        for recognizer in recognizers:
            assert not detect(recognizer, text), (recognizer.name, text)
