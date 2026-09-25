"""One-line registration of the MENA recognizers into a Presidio pipeline."""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from presidio_analyzer import AnalyzerEngine, EntityRecognizer, RecognizerRegistry

from .recognizers import (
    MoroccanCINRecognizer,
    MoroccanIBANRecognizer,
    MoroccanICERecognizer,
    MoroccanPhoneRecognizer,
    MoroccanRIBRecognizer,
)

#: Every entity this package can report.
MENA_ENTITIES: tuple[str, ...] = (
    "MA_CIN",
    "MA_PHONE_NUMBER",
    "MA_RIB",
    "MA_IBAN",
    "MA_ICE",
)


def mena_recognizers(
    supported_language: str = "en",
) -> list[EntityRecognizer]:
    """Build one instance of every MENA recognizer.

    Presidio matches recognizers to text by language, so a pipeline handling
    French and Arabic documents needs this called once per language code it
    is configured with.
    """
    return [
        MoroccanCINRecognizer(supported_language=supported_language),
        MoroccanPhoneRecognizer(supported_language=supported_language),
        MoroccanRIBRecognizer(supported_language=supported_language),
        MoroccanIBANRecognizer(supported_language=supported_language),
        MoroccanICERecognizer(supported_language=supported_language),
    ]


def register_mena_recognizers(
    target: AnalyzerEngine | RecognizerRegistry,
    languages: Sequence[str] | Iterable[str] = ("en",),
) -> list[EntityRecognizer]:
    """Add the MENA recognizers to an analyzer or a registry.

    Accepts either an :class:`AnalyzerEngine` or its
    :class:`RecognizerRegistry`, so it fits both the quick path and a
    hand-assembled pipeline. Returns the recognizers that were added.

    Example:
        >>> from presidio_analyzer import AnalyzerEngine
        >>> from presidio_mena import register_mena_recognizers
        >>> analyzer = AnalyzerEngine()
        >>> register_mena_recognizers(analyzer)  # doctest: +ELLIPSIS
        [...]
    """
    registry = target.registry if isinstance(target, AnalyzerEngine) else target

    added: list[EntityRecognizer] = []
    for language in languages:
        for recognizer in mena_recognizers(supported_language=language):
            registry.add_recognizer(recognizer)
            added.append(recognizer)
    return added
