"""End-to-end tests through a real Presidio AnalyzerEngine.

These prove the package is a drop-in: the recognizers register, run inside the
full pipeline alongside Presidio's own, and their results anonymize correctly.
"""

from __future__ import annotations

import pytest

from presidio_mena import MENA_ENTITIES, register_mena_recognizers, rib_check_key

presidio_analyzer = pytest.importorskip("presidio_analyzer")
AnalyzerEngine = presidio_analyzer.AnalyzerEngine
RecognizerRegistry = presidio_analyzer.RecognizerRegistry


def make_rib(first_22: str = "0123456789012345678901") -> str:
    return first_22 + f"{rib_check_key(first_22):02d}"


@pytest.fixture(scope="module")
def analyzer():
    """A full Presidio analyzer with the MENA recognizers added."""
    engine = AnalyzerEngine()
    register_mena_recognizers(engine)
    return engine


def entities_found(analyzer, text: str) -> set[str]:
    return {result.entity_type for result in analyzer.analyze(text, language="en")}


class TestRegistration:
    def test_registers_on_an_analyzer_engine(self, analyzer):
        supported = set(analyzer.get_supported_entities(language="en"))
        assert set(MENA_ENTITIES).issubset(supported)

    def test_registers_on_a_bare_registry(self):
        registry = RecognizerRegistry()
        registry.load_predefined_recognizers()
        added = register_mena_recognizers(registry)
        assert len(added) == len(MENA_ENTITIES)

    def test_can_register_several_languages(self):
        registry = RecognizerRegistry()
        added = register_mena_recognizers(registry, languages=["en", "fr"])
        assert len(added) == 2 * len(MENA_ENTITIES)
        assert {r.supported_language for r in added} == {"en", "fr"}


class TestDetectionInFullPipeline:
    def test_finds_a_cin(self, analyzer):
        assert "MA_CIN" in entities_found(analyzer, "Sa CIN est BE12345.")

    def test_finds_a_phone_number(self, analyzer):
        assert "MA_PHONE_NUMBER" in entities_found(
            analyzer, "Appelez le 0612345678 demain."
        )

    def test_finds_a_valid_rib(self, analyzer):
        assert "MA_RIB" in entities_found(analyzer, f"RIB: {make_rib()}")

    def test_finds_an_ice(self, analyzer):
        assert "MA_ICE" in entities_found(analyzer, "ICE 001234567000089")

    def test_does_not_break_presidio_built_ins(self, analyzer):
        """Adding our recognizers must not shadow the standard ones."""
        found = entities_found(analyzer, "Write to john.doe@example.com")
        assert "EMAIL_ADDRESS" in found

    def test_mixed_document(self, analyzer):
        text = (
            "Client BE12345, tel 0612345678, "
            f"RIB {make_rib()}, ICE 001234567000089, "
            "email a.benali@example.ma"
        )
        found = entities_found(analyzer, text)
        assert {"MA_CIN", "MA_PHONE_NUMBER", "MA_RIB", "MA_ICE"}.issubset(found)
        assert "EMAIL_ADDRESS" in found


class TestContextBoost:
    def test_context_word_raises_confidence(self, analyzer):
        """Presidio's context mechanism must work through our recognizers."""
        without = analyzer.analyze(
            "Reference B123456 archived", language="en", entities=["MA_CIN"]
        )
        with_context = analyzer.analyze(
            "Carte nationale B123456 archived", language="en", entities=["MA_CIN"]
        )
        assert without and with_context
        assert with_context[0].score > without[0].score


class TestAnonymization:
    def test_results_anonymize_end_to_end(self, analyzer):
        anonymizer_module = pytest.importorskip("presidio_anonymizer")
        engine = anonymizer_module.AnonymizerEngine()

        text = f"CIN BE12345 et RIB {make_rib()}"
        results = analyzer.analyze(text, language="en")
        output = engine.anonymize(text=text, analyzer_results=results)

        assert "BE12345" not in output.text
        assert make_rib() not in output.text
