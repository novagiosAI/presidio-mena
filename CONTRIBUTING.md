# Contributing to presidio-mena

Thanks for taking the time to contribute. **New MENA recognizers are the most useful
contribution** — the package is named `mena`, not `morocco`, on purpose.

## Getting set up

```bash
git clone https://github.com/novagiosAI/presidio-mena.git
cd presidio-mena
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Before opening a pull request

```bash
pytest
ruff check .
ruff format .
mypy
```

## Adding a recognizer

1. Subclass `PatternRecognizer` in `recognizers.py`.
2. **Name the entity with the ISO country prefix** — `DZ_NIN`, `TN_CIN` — matching
   Presidio's own `US_SSN` / `ES_NIF` convention, and set `COUNTRY_CODE`.
3. **If the identifier has a check digit, implement `validate_result()`.** Put the
   algorithm in `checksums.py`. Score the pattern low and let the checksum raise it:
   this is what makes the package usable unattended.
   If it has no check digit, implement `invalidate_result()` at least to reject
   placeholder runs.
4. **Context words must be single tokens.** Presidio's enhancer compares one token
   lemma at a time, so `"carte nationale"` never matches — add `"carte"` and
   `"nationale"` separately. Include the French, Arabic and English forms.
5. Register it in `registry.py` and add the entity to `MENA_ENTITIES`.
6. Add tests covering: values that must be found, near-misses that must not, and
   ordinary prose that must yield nothing. Add an end-to-end case in
   `test_integration_presidio.py`.

Document your source for the format in a comment. A recognizer built on a guessed
format is worse than none.

## Design principles

1. **Follow Presidio's conventions.** Anything surprising defeats the purpose of a
   drop-in package.
2. **Validate whenever the format allows it.** Check digits exist so look-alikes can
   be rejected.
3. **No false positives on ordinary text.** A tool that shreds invoice references
   gets switched off, and then it protects nothing.

## Security issues

Do not open a public issue for a vulnerability. See [SECURITY.md](SECURITY.md).

## License

By contributing, you agree that your contributions are licensed under the
[Apache License 2.0](LICENSE).
