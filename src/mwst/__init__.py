"""Schweizer MWST- und Rappen-Hilfsfunktionen (Pilot-Bibliothek)."""

from decimal import ROUND_HALF_UP, Decimal

__version__ = "0.1.0"

# MWST-Saetze in Prozent, gueltig seit 1. Januar 2024.
SAETZE: dict[str, Decimal] = {
    "normal": Decimal("8.1"),
    "reduziert": Decimal("2.6"),
    "beherbergung": Decimal("3.8"),
}

# Rundungsschritt fuer Rappenbetraege: 5 Rappen = 0.05 CHF.
_RAPPEN_SCHRITT = Decimal("0.05")


def mwst_betrag(netto: Decimal, satz: str) -> Decimal:
    """Berechnet den MWST-Betrag und rundet ihn auf 5 Rappen.

    Der MWST-Betrag ergibt sich aus ``netto`` multipliziert mit dem Prozentsatz
    ``satz``. Das Ergebnis wird kaufmaennisch auf 5 Rappen gerundet
    (``ROUND_HALF_UP``): genau in der Mitte wird aufgerundet.

    Args:
        netto: Nettobetrag in CHF, nicht negativ.
        satz: Schluessel aus ``SAETZE`` ("normal", "reduziert", "beherbergung").

    Returns:
        MWST-Betrag in CHF, auf 5 Rappen gerundet.

    Raises:
        ValueError: Wenn ``netto`` negativ oder ``satz`` unbekannt ist.
    """
    if netto < 0:
        raise ValueError("netto darf nicht negativ sein")
    if satz not in SAETZE:
        raise ValueError(f"unbekannter MWST-Satz: {satz!r}")
    betrag = netto * SAETZE[satz] / Decimal(100)
    gerundet = (betrag / _RAPPEN_SCHRITT).quantize(Decimal(1), rounding=ROUND_HALF_UP)
    return gerundet * _RAPPEN_SCHRITT
