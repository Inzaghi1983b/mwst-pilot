from decimal import Decimal

from mwst import SAETZE


def test_saetze_sind_aktuelle_schweizer_saetze():
    assert SAETZE == {
        "normal": Decimal("8.1"),
        "reduziert": Decimal("2.6"),
        "beherbergung": Decimal("3.8"),
    }


def test_saetze_sind_decimal_nicht_float():
    assert all(isinstance(satz, Decimal) for satz in SAETZE.values())
