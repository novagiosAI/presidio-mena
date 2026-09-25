# Changelog

All notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] — 2026-09-19

First public release.

### Added

- Five Presidio recognizers for Moroccan identifiers: `MA_CIN`, `MA_PHONE_NUMBER`,
  `MA_RIB`, `MA_IBAN`, `MA_ICE`, each tagged with `COUNTRY_CODE = "ma"` and named
  following Presidio's `US_SSN` / `ES_NIF` convention.
- **Check-digit validation through `validate_result()`**: mod-97 for RIB and
  ISO 7064 MOD-97-10 for IBAN. A confirmed value is raised to full confidence and a
  failing one is discarded, so only about 1 in 97 arbitrary 24-digit numbers is
  reported as a bank account.
- Placeholder rejection via `invalidate_result()` for CIN, phone and ICE
  (`A000000`, `0000000000`, ...).
- Multilingual single-token context words (French, Arabic, English) so Presidio's
  context enhancer actually boosts scores on Moroccan documents.
- `register_mena_recognizers()` accepting an `AnalyzerEngine` or a
  `RecognizerRegistry`, with multi-language registration.
- Full type annotations with a `py.typed` marker; passes `mypy --strict`.
- 47 tests, including end-to-end runs through a real `AnalyzerEngine` and
  `AnonymizerEngine`.
- CI across Python 3.10–3.13 with `pytest`, `ruff` and `mypy`.

[Unreleased]: https://github.com/novagiosAI/presidio-mena/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/novagiosAI/presidio-mena/releases/tag/v0.1.0
