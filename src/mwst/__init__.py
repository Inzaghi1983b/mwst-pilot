"""Schweizer MWST- und Rappen-Hilfsfunktionen (Pilot-Bibliothek)."""

from decimal import Decimal

__version__ = "0.1.0"

# MWST-Saetze in Prozent, gueltig seit 1. Januar 2024.
SAETZE: dict[str, Decimal] = {
    "normal": Decimal("8.1"),
    "reduziert": Decimal("2.6"),
    "beherbergung": Decimal("3.8"),
}
