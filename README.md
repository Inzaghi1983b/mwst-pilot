# mwst-pilot

Kleine Python-Bibliothek fuer Schweizer MWST- und Rappenbetraege. Das Repo ist zugleich der Pilot
fuer eine autonome Entwicklungs-Pipeline auf GitHub-Bordmitteln.

## Ablauf

1. Ein Mensch schreibt ein Issue und setzt das Label `agent`.
2. GitHub Agentic Workflows startet den Coding-Agenten (Codex mit DeepSeek Flash) in einer
   abgeschotteten Umgebung: Agent-Job nur mit Leserechten, Netzwerk nur ueber Allowlist, API-Key
   nur im Proxy.
3. Der Agent setzt das Issue um und fuehrt `ruff` und `pytest` aus, bis beide gruen sind
   (hoechstens drei Korrekturrunden, Regeln in `AGENTS.md`).
4. Ein Pruefjob (Threat Detection) kontrolliert das Ergebnis. Erst danach erstellt ein eigener
   Job mit Schreibrechten einen Draft-Pull-Request.
5. CI (`.github/workflows/ci.yml`) prueft den Pull Request unabhaengig. Bei Agenten-PRs wartet
   dieser Lauf auf einen Freigabeklick ("Approve and run" im Pull Request).
6. Ein Mensch prueft, setzt "Ready for review" und merged. Es gibt keinen automatischen Merge.

Ergebnis des Pilotlaufs (Kosten, Laufzeit, Autonomie): `docs/modellvergleich.md`, Abschnitt
"Ergebnisse".

## Grenzen im Pilot

- Nachbesserung passiert im Agenten-Lauf (gleiche Pruefungen wie CI). Faellt CI danach trotzdem
  rot aus, gibt es noch keinen automatischen zweiten Lauf; gh-aw bietet dafuer nur Bausteine
  (`workflow_run`, Slash-Command mit `push-to-pull-request-branch`).
- Pull Requests aus dem Workflow entstehen mit dem `GITHUB_TOKEN`. Ihr CI-Lauf wartet auf einen
  Freigabeklick; GitHub bietet keine Einstellung dafuer. Nur dieser `pull_request`-Lauf erfuellt
  den Pflicht-Check `test`: Ein per `workflow_dispatch` gestarteter Lauf zaehlt nicht (getestet).
  Ohne Klick ginge es nur mit einem zusaetzlichen Token (PAT oder GitHub App). Entscheid: Der Klick
  bleibt. CI bekommt nie Secrets oder Schreibrechte, weil dort Agenten-Code laeuft.
- `main` verlangt einen Pull Request und den gruenen Check `test`, aber keine Review-Freigabe.
  Den Merge-Entscheid traegt die Praxis "nur der Mensch merged".
- Kostenbremsen: Agent hoechstens 50 AI-Credits (rund 0.50 USD) pro Lauf, Pruefjob 20, alle Laeufe
  zusammen 200 pro 24 Stunden, Laufzeit hoechstens 30 Minuten. Harte Grenze ist das
  Prepaid-Guthaben des DeepSeek-Kontos (Details in `docs/modellvergleich.md`).

## Entwicklung lokal

```
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements-dev.txt
.venv\Scripts\ruff check .
.venv\Scripts\pytest
```

## Dateien

- `src/mwst/` - Bibliothek
- `tests/` - Tests
- `AGENTS.md` - Regeln fuer jeden Coding-Agenten, unabhaengig von Agent und Modell
- `.github/workflows/issue-agent.md` - Agentic Workflow (Quelle); `.lock.yml` ist kompiliert
- `.github/workflows/ci.yml` - CI
- `docs/modellvergleich.md` - Modellvergleich OpenAI, DeepSeek, Claude (T2 belegt)

Datenklasse: oeffentlich-tauglich. Keine Personen- oder Kundendaten, keine produktiven Secrets.
