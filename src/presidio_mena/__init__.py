from .checksums import is_valid_iban, is_valid_rib, rib_check_key
from .recognizers import (
    MoroccanCINRecognizer,
    MoroccanIBANRecognizer,
    MoroccanICERecognizer,
    MoroccanPhoneRecognizer,
    MoroccanRIBRecognizer,
)
from .registry import MENA_ENTITIES, mena_recognizers, register_mena_recognizers

__version__ = "0.1.0"

__all__ = [
    "MoroccanCINRecognizer",
    "MoroccanPhoneRecognizer",
    "MoroccanRIBRecognizer",
    "MoroccanIBANRecognizer",
    "MoroccanICERecognizer",
    "register_mena_recognizers",
    "mena_recognizers",
    "MENA_ENTITIES",
    "is_valid_rib",
    "is_valid_iban",
    "rib_check_key",
]
