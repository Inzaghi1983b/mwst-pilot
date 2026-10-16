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
5. CI (`.github/workflows/ci.yml`) prueft den Pull Request unabhaengig. Bei Agenten-PRs stoesst
   `.github/workflows/ci-anstossen.yml` CI an, sobald der Agentenlauf erfolgreich endet.
6. Ein Mensch prueft und merged. Es gibt keinen automatischen Merge.

## Grenzen im Pilot

- Nachbesserung passiert im Agenten-Lauf (gleiche Pruefungen wie CI). Faellt CI danach trotzdem
  rot aus, gibt es noch keinen automatischen zweiten Lauf; gh-aw bietet dafuer nur Bausteine
  (`workflow_run`, Slash-Command mit `push-to-pull-request-branch`).
- Pull Requests aus dem Workflow entstehen mit dem `GITHUB_TOKEN`; ihr eigener CI-Lauf wartet auf
  einen Freigabeklick, und nur dieser Lauf erfuellt den Pflicht-Check. `ci-anstossen.yml` gibt ihn
  ohne Secret frei, nur fuer die PR des gerade abgeschlossenen Laufs und nur, wenn sie allein
  `src/` und `tests/` aendert. Lehnt GitHub die Freigabe ab, startet er CI per `workflow_dispatch`
  (Ergebnis sichtbar, zaehlt aber nicht als Pflicht-Check); dann braucht es den Klick. Er checkt
  keinen PR-Code aus. Damit laeuft Agenten-Code in CI, bevor ein Mensch ihn sieht. Darum gilt: CI
  und jeder andere Workflow, der auf Agenten-Branches laeuft, bekommt nie Secrets oder
  Schreibrechte.
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
- `.github/workflows/ci-anstossen.yml` - gibt CI fuer Agenten-PRs frei (Rueckfall: workflow_dispatch)
- `docs/modellvergleich.md` - Vorbereitung Modellvergleich OpenAI, DeepSeek, Claude

Datenklasse: oeffentlich-tauglich. Keine Personen- oder Kundendaten, keine produktiven Secrets.
