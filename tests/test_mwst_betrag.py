from decimal import Decimal

import pytest

from mwst import SAETZE, mwst_betrag


@pytest.mark.parametrize(
    ("netto", "satz", "erwartet"),
    [
        (Decimal("100.00"), "normal", Decimal("8.10")),
        (Decimal("100.00"), "reduziert", Decimal("2.60")),
        (Decimal("100.00"), "beherbergung", Decimal("3.80")),
        (Decimal("250.00"), "normal", Decimal("20.25")),
        (Decimal("250.00"), "reduziert", Decimal("6.50")),
        (Decimal("250.00"), "beherbergung", Decimal("9.50")),
    ],
)
def test_mwst_betrag_fuer_alle_saetze(netto, satz, erwartet):
    assert mwst_betrag(netto, satz) == erwartet


def test_mwst_betrag_rundet_mitte_aufwaerts_auf_025():
    # 25.00 * 8.1 % = 2.025, genau in der Mitte zwischen 2.00 und 2.05.
    assert mwst_betrag(Decimal("25.00"), "normal") == Decimal("2.05")


def test_mwst_betrag_rundet_mitte_aufwaerts_auf_075():
    # 75.00 * 8.1 % = 6.075, genau in der Mitte zwischen 6.05 und 6.10.
    assert mwst_betrag(Decimal("75.00"), "normal") == Decimal("6.10")


def test_mwst_betrag_rundet_ab_unterhalb_der_mitte():
    # 25.00 * 2.6 % = 0.65, bereits ein Vielfaches von 0.05.
    assert mwst_betrag(Decimal("25.00"), "reduziert") == Decimal("0.65")


def test_mwst_betrag_bei_netto_null_ist_null():
    assert mwst_betrag(Decimal("0"), "normal") == Decimal("0.00")


@pytest.mark.parametrize("satz", list(SAETZE))
def test_mwst_betrag_bei_netto_null_fuer_alle_saetze(satz):
    assert mwst_betrag(Decimal("0.00"), satz) == Decimal("0.00")


def test_mwst_betrag_negatives_netto_loest_valueerror_aus():
    with pytest.raises(ValueError):
        mwst_betrag(Decimal("-1.00"), "normal")


def test_mwst_betrag_unbekannter_satz_loest_valueerror_aus():
    with pytest.raises(ValueError):
        mwst_betrag(Decimal("100.00"), "ermassigt")
