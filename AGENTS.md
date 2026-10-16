# AGENTS.md - Regeln fuer jeden Coding-Agenten in diesem Repo

Diese Datei gilt unabhaengig vom Agenten (Codex, Claude Code oder andere) und vom Modell.

## Projekt

Kleine Python-Bibliothek fuer Schweizer MWST- und Rappenbetraege.

- Code: `src/mwst/`
- Tests: `tests/` (pytest)
- Python 3.12, keine Laufzeit-Abhaengigkeiten

## Fachregeln

- Geldbetraege immer mit `decimal.Decimal`, nie mit `float`.
- Rappenrundung auf 5 Rappen (0.05 CHF), kaufmaennisch (`ROUND_HALF_UP`): genau in der Mitte wird
  aufgerundet.
- MWST-Saetze kommen aus `mwst.SAETZE`; keine Saetze doppelt im Code.
- Ungueltige Eingaben (z. B. negative Betraege, unbekannte Saetze) loesen `ValueError` aus.
- Jede oeffentliche Funktion hat Typangaben und einen Docstring.

## Arbeitsablauf

1. Aufgabe aus dem Issue lesen. Unklarheit nicht raten: Annahme im Pull-Request-Text nennen.
2. Nur `src/` und `tests/` aendern. README nur, wenn die Aufgabe es verlangt.
3. Fuer jede neue Funktion Tests schreiben, inklusive Grenzfaelle aus dem Issue.
4. Vor dem Abschluss alle drei Pruefungen ausfuehren und gruen machen:
   - `ruff check .`
   - `ruff format --check .` (bei Bedarf vorher `ruff format .`)
   - `pytest`
5. Bleibt eine Pruefung nach drei Korrekturrunden rot: aufhoeren und den Fehler im
   Pull-Request-Text offen beschreiben, nicht Tests abschwaechen oder loeschen.

## Verboten

- Aenderungen an `.github/`, `AGENTS.md`, `pyproject.toml` oder `requirements-dev.txt`.
- Tests loeschen, ueberspringen oder Erwartungen aufweichen, damit sie gruen werden.
- Neue Abhaengigkeiten, Netzwerkzugriffe, Secrets oder Zugangsdaten im Code.
- Personen- oder Kundendaten. Dieses Repo ist fuer oeffentlich-taugliche Daten eingestuft.
