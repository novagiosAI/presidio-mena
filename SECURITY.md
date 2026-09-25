# Security Policy

## Supported versions

| Version | Supported |
|---|---|
| 0.1.x | ✅ |

Until 1.0, security fixes are released on the latest minor version only.

## Reporting a vulnerability

**Please do not open a public GitHub issue for security problems.**

- GitHub → **Security** tab → *Report a vulnerability* (private advisory), or
- email **security@novagios.com**

We aim to acknowledge within 5 business days and to ship a fix or give a timeline
within 30 days.

**Never include real personal data in a report.** To show a failing input, build a
fake identifier with a valid check digit — `rib_check_key()` will compute one for any
22 digits you invent.

## Scope

This package contributes recognizers to Presidio. It opens no network connections,
reads no files, and stores nothing. Its only dependency is `presidio-analyzer`.

The security-relevant behaviour is **detection quality**, and both failure modes
matter:

- A **false negative** leaves personal data in a document its owner believes is
  anonymized. Report these as security issues.
- A **false positive** destroys data, which is a correctness bug — report it as a
  normal issue.

## What this package does not protect against

Recognizers reduce risk; they do not remove it. Under GDPR and Moroccan law 09-08,
an automatically anonymized document is not automatically lawful to publish:

- CIN and ICE carry no publicly specified check digit, so detection there rests on
  shape and context and will miss some values.
- Names, prose addresses and indirect identifiers are Presidio's NER job, not this
  package's.
- A person can still be re-identified from a combination of fields that are each
  individually harmless.

Review a sample of any dataset before releasing it.
