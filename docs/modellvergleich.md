# Modellvergleich OpenAI, DeepSeek, Claude

Agent und Modell sind zwei getrennte Achsen. Beide werden nur im Frontmatter von
`.github/workflows/issue-agent.md` gewaehlt. Es gibt keine eigene Routing-Infrastruktur, kein
Gateway und kein LiteLLM.

- Agent wechseln: `engine.id` (`codex` oder `claude`).
- Modell wechseln: `engine.model`, bei Fremdanbietern zusaetzlich `engine.env` (Endpunkt und
  Key-Zuordnung), der Anbieter-Host in `network.allowed`, ein Preis-Eintrag und das Repo-Secret.

Nach jeder Aenderung: `gh aw compile`, Lock-Datei mit committen.

## Regeln fuer einen fairen Vergleich

- Gleicher Issue-Text, gleicher Basis-Commit auf `main` (Agent-PRs werden waehrend des Vergleichs
  nicht gemergt).
- Pro Zelle aendern sich nur Frontmatter und Secret. gh-aw-Version und Codex-/Claude-Version sind
  ueber die Lock-Datei gepinnt (gh-aw v0.92.0, Codex 0.162.1).
- Ein Lauf pro Zelle belegt nur die Austauschbarkeit. Qualitaet: danach 5 Issues pro verbleibender
  Zelle, auch das ist nur ein Indiz.
- Der Pruefjob (Threat Detection) laeuft mit dem Modell der jeweiligen Zelle.

## Austausch-Aufgabe (Issue-Text, fuer alle Zellen identisch)

> Titel: `mwst_betrag(netto, satz)` mit Rappenrundung
>
> Neue Funktion `mwst_betrag(netto: Decimal, satz: str) -> Decimal` in `src/mwst/`. `satz` ist ein
> Schluessel aus `SAETZE` ("normal", "reduziert", "beherbergung"). Ergebnis ist der MWST-Betrag,
> auf 5 Rappen gerundet (kaufmaennisch, Mitte wird aufgerundet).
>
> Tests fuer: alle drei Saetze; Rundung genau auf der Mitte (Betraege, deren MWST auf ...025 und
> ...075 endet); Netto 0; negativer Betrag und unbekannter Satz loesen `ValueError` aus.
>
> Abnahme: CI gruen, alle Grenzfaelle getestet, nur `src/` und `tests/` geaendert.

## Zellen

Reihenfolge nach Betreiberentscheid 2026-10-16: zuerst T2 (guenstigste Zelle). Alle Varianten
wurden mit gh-aw v0.92.0 kompiliert (Syntax gueltig, noch kein Laufzeit-Beleg).

| Zelle | Agent | Modell | Secret | Status |
|---|---|---|---|---|
| T2 | Codex | DeepSeek `deepseek-flash` | `DEEPSEEK_API_KEY` | aktiv im Repo, ein Lauf belegt (2026-10-16) |
| T4 | Claude Code | DeepSeek `deepseek-flash` | `DEEPSEEK_API_KEY` | Ersatz, falls Codex scheitert |
| T1 | Codex | OpenAI `gpt-5.3-codex` | `OPENAI_API_KEY` (Projekt-Key mit Limit) | spaeter, optional |
| T3 | Claude Code | Anthropic `claude-sonnet-5-5` | `ANTHROPIC_API_KEY` (Workspace-Key mit Limit) | spaeter, optional |

### T2 - Codex mit DeepSeek Flash (aktueller Stand)

```yaml
engine:
  id: codex
  model: deepseek-flash
  env:
    OPENAI_BASE_URL: https://api.deepseek.com
    OPENAI_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}
    CODEX_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}
  config: |
    web_search = "disabled"
    model_reasoning_summary = "none"
    model_context_window = 200000
max-ai-credits: 50
max-daily-ai-credits: 200
models:
  providers:
    openai:
      models:
        deepseek-flash:
          cost:
            input: "3e-07"
            output: "1.2e-06"
            cache_read: "6e-09"
network:
  allowed:
    - defaults
    - python
    - api.deepseek.com
```

Belege (Stand 2026-10-16):
- Modellname `deepseek-flash` laut DeepSeek-Doku; die alten Namen `deepseek-v4-flash` werden noch
  angenommen und auf V4.1-Flash geleitet.
- Endpunkt: DeepSeek dokumentiert `https://api.deepseek.com` fuer die Responses API (nur
  `deepseek-flash`). Der gh-aw-API-Proxy setzt fuer fremde Hosts keinen `/v1`-Praefix; Codex ruft
  damit `https://api.deepseek.com/responses` auf (Quellcode AWF v0.28.57, `providers/openai.js`).
- Beide Key-Namen zeigen auf das DeepSeek-Secret, weil Codex `CODEX_API_KEY` vor
  `OPENAI_API_KEY` liest. Die Lock-Datei referenziert nur `secrets.DEEPSEEK_API_KEY`. Nie ein
  Secret `CODEX_API_KEY` oder `OPENAI_API_KEY` fuer diese Zelle anlegen.
- Preise: Spitzenpreise aus der DeepSeek-Preisliste (USD pro Mio. Tokens: Cache-Miss 0.30,
  Cache-Hit 0.006, Ausgabe 1.20; ausserhalb der Spitzenzeit die Haelfte). Spitzenzeit werktags
  01-04 und 06-10 UTC. Im Frontmatter steht der Preis pro Token.
- Codex 0.162.1 akzeptiert die drei `config`-Keys (lokal ohne API-Aufruf geprueft). Es warnt, dass
  fuer `deepseek-flash` keine Modell-Metadaten vorliegen, und nimmt Ersatzwerte.
- Der Pruefjob uebernimmt `deepseek-flash` und das DeepSeek-Secret.

### T4 - Claude Code mit DeepSeek Flash (Ersatz)

```yaml
engine:
  id: claude
  model: deepseek-flash
  env:
    ANTHROPIC_BASE_URL: https://api.deepseek.com/anthropic
    ANTHROPIC_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}
    ANTHROPIC_API_BASE_PATH: /anthropic
models:
  providers:
    anthropic:
      models:
        deepseek-flash:
          cost:
            input: "3e-07"
            output: "1.2e-06"
            cache_read: "6e-09"
tools:
  bash: ["pytest", "ruff check .", "ruff format ."]
```

Offener Punkt: gh-aw v0.92.0 gibt dem API-Proxy nur den Host `api.deepseek.com` weiter, nicht den
Pfad `/anthropic`. Ohne Pfad landen Anfragen auf `https://api.deepseek.com/v1/messages` statt
`.../anthropic/v1/messages`. `ANTHROPIC_API_BASE_PATH` ist die Umgebungsvariable, die der Proxy
dafuer liest; sie landet laut Lock-Datei in der Umgebung des AWF-Starts. Ob der Proxy sie dort
uebernimmt, zeigt erst ein Lauf. Ausserhalb von gh-aw (lokal) ist Claude Code mit DeepSeek
erprobt.

### T1 - Codex mit OpenAI

```yaml
engine:
  id: codex
  model: gpt-5.3-codex
max-ai-credits: 300
```

`env`, `models` und `api.deepseek.com` entfallen. `gpt-5.3-codex` steht in der Preisliste von
gh-aw (1.75 USD pro Mio. Eingabe-Tokens, 0.175 aus dem Cache, 14 USD Ausgabe).

### T3 - Claude Code mit Anthropic

```yaml
engine:
  id: claude
  model: claude-sonnet-5-5
tools:
  bash: ["pytest", "ruff check .", "ruff format ."]
```

Claude Code unterstuetzt eine Befehls-Allowlist fuer bash, Codex nicht (`bash: ["*"]` ist bei
Codex Pflicht, sonst bricht der Compiler ab).

## Kostenbremsen (T2)

| Bremse | Wo | Wirkung |
|---|---|---|
| Prepaid-Guthaben | DeepSeek-Konto | hart: leeres Guthaben = HTTP 402. Nur getrennt vom SwissSeller-Konto eine echte Grenze fuer den Pilot |
| `max-ai-credits: 50` | gh-aw-API-Proxy, waehrend des Laufs | stoppt den Agenten bei rund 0.50 USD (gerechnet mit dem Preis-Eintrag) |
| Pruefjob `max-ai-credits: 20` | gh-aw-API-Proxy | rund 0.20 USD fuer den Pruefjob |
| `max-daily-ai-credits: 200` | vor dem Start | kein neuer Lauf, wenn die letzten 24 h rund 2 USD ueberschreiten |
| `timeout-minutes: 30`, Cache-Miss-Abbruch nach 5 | Runner, Proxy | begrenzt Dauer und teure Wiederholungen |
| `model_context_window = 200000` | Codex | begrenzt die Groesse einer einzelnen Anfrage |
| Ausloesung nur durch Schreibberechtigte | gh-aw-Rollenpruefung | Fremde koennen keinen Lauf starten |

Erwartung pro Lauf (Referenzaufgabe, Listenpreis): rund 0.18 USD zur Spitzenzeit, rund 0.09 USD
sonst. Gemessen (T2, siehe Ergebnisse): 0.027 USD zum Spitzenpreis, die Schaetzung lag rund
siebenmal zu hoch.

## Zusaetzliche Proben

1. Lock-Dateien der Zellen vergleichen: nur erwartete Zeilen anders, kein fremder Anbieter-Host,
   jedes Secret nur in seinen Jobs.
2. Koeder: unbrauchbares Secret `CODEX_API_KEY` anlegen; T2 muss trotzdem normal bei DeepSeek
   abrechnen (die Lock-Datei referenziert es nicht).
3. Canary in T2: Umgebungsausgabe zeigt keinen echten Key; Aufruf an nicht erlaubten Host wird
   blockiert.
4. Fail-closed: ungueltiges Modell fuer den Pruefjob (Repo-Variable
   `GH_AW_MODEL_DETECTION_CODEX`); scheitert der Pruefjob, darf kein Pull Request entstehen.
5. Kostenbremse: `gh aw audit` muss die AIC des Laufs zeigen; Kosten im DeepSeek-Konto mit der
   Schaetzung vergleichen.

## Ergebnisse

| Zelle | Ergebnis (CI gruen, Nacharbeit?) | Kosten (Tokens, USD aus `gh aw audit`) | Dauer | Gates und Proben |
|---|---|---|---|---|
| T2 | CI gruen, fachlich korrekt; ein wertloser Test im Review ersetzt | 2.67 AIC = 0.027 USD zum Spitzenpreis, tatsaechlich rund 0.013 USD | 4 min 21 s | Pruefjob gruen, Firewall 11 von 11 Anfragen erlaubt; Proben 1-4 nicht gefahren |
| T4 | | | | |
| T1 | | | | |
| T3 | | | | |

### T2: Pilotlauf vom 2026-10-16 (belegt)

Issue #1 (Austausch-Aufgabe oben), Lauf
[38896033099](https://github.com/Inzaghi1983b/mwst-pilot/actions/runs/38896033099),
Ergebnis PR #2 (gemergt).

Ablauf und Laufzeit:
- Label `agent` gesetzt um 11:46:43 UTC, Draft-PR erstellt um 11:50:48 UTC, Lauf fertig nach
  4 min 21 s. Jobs: Vorpruefung und Aktivierung 30 s, Agent 1.8 min, Pruefjob 1.2 min,
  PR-Erstellung 21 s, Abschluss 13 s.
- Der Agent brauchte einen Anlauf mit einer Selbstkorrektur: erster Testlauf rot (`quantize` auf
  `0.05` rundet nur auf zwei Stellen), selbst behoben, danach `ruff` und `pytest` gruen.

Kosten (`gh aw audit`, Preise aus dem Frontmatter):
- Agent: 10 Anfragen, 263 500 Eingabe-Tokens (davon 237 696 aus dem Cache), 7 575
  Ausgabe-Tokens, 1.83 AIC.
- Pruefjob: 4 Anfragen, 0.84 AIC.
- Zusammen 2.67 AIC = 0.027 USD zum Spitzenpreis. Der Lauf lag ausserhalb der DeepSeek-
  Spitzenzeit, tatsaechlich also rund 0.013 USD. Im DeepSeek-Konto nicht gegengeprueft.
- `gh aw audit` meldet hohen Token-Verbrauch fuer die kleine Aufgabe (271 000 Tokens, meist
  wiederholter Kontext aus dem Cache).

Qualitaet:
- Unabhaengiger Abgleich gegen eine Ganzzahl-Referenz: 600 003 Faelle (0.00 bis 2000.00 CHF, alle
  drei Saetze), 0 Abweichungen.
- Im Review gefunden: ein Test "rundet ab unterhalb der Mitte" pruefte keinen Rundungsfall und
  blieb auch mit falscher Rundung gruen. Ersetzt durch 24.99 CHF zum Normalsatz (2.02419 -> 2.00).

Autonomie:
- Ohne Mensch: Umsetzung, Tests, Selbstkorrektur, Pruefjob, Draft-PR mit Beschreibung und
  Annahmen.
- Mit Mensch: Issue schreiben und Label setzen; CI-Lauf des PRs freigeben (Klick); Review;
  "Ready for review" und Merge.
- Nicht vorhanden: automatischer zweiter Lauf, falls CI nach dem Agentenlauf rot ist (hier nicht
  noetig).

Grenzen dieses Belegs:
- Ein Lauf belegt Machbarkeit und Austauschbarkeit, keine Qualitaetsaussage.
- Der CI-Freigabeklick bleibt. GitHub verlangt ihn fuer PRs von `github-actions[bot]`, ohne
  Einstellung zum Abschalten. Ein per `workflow_dispatch` gestarteter CI-Lauf erfuellt den
  Pflicht-Check nicht (getestet mit einem Wegwerf-PR). Ein Hilfsworkflow dafuer wurde wieder
  entfernt.
- Proben 1-4 (oben) wurden nicht gefahren. Probe 5 nur halb: AIC per `gh aw audit` belegt,
  Abgleich mit dem DeepSeek-Konto offen.
- T1, T3 und T4 sind nicht gelaufen. Sie brauchen bezahlte Laeufe, T1 und T3 zusaetzlich neue
  Secrets.

## Grenzen

- Codex mit DeepSeek: nur `deepseek-flash`; keine Websuche, keine Reasoning-Zusammenfassungen,
  kein Serverzustand, keine Modell-Metadaten in Codex; von OpenAI nicht unterstuetzt.
- Claude Code mit DeepSeek: von Anthropic nicht unterstuetzt; in gh-aw zusaetzlich der offene
  Pfad-Punkt oben.
- DeepSeek nur fuer Repos der Datenklasse oeffentlich-tauglich (Speicherung in China, Training
  nicht ausgeschlossen). Dieses Repo ist oeffentlich und enthaelt keine Personen- oder Kundendaten.
