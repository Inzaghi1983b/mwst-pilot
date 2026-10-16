# Modellvergleich OpenAI, DeepSeek, Claude (Vorbereitung)

Agent und Modell sind zwei getrennte Achsen. Beide werden nur im Frontmatter von
`.github/workflows/issue-agent.md` gewaehlt. Es gibt keine eigene Routing-Infrastruktur, kein
Gateway und kein LiteLLM.

- Agent wechseln: `engine.id` (`codex` oder `claude`).
- Modell wechseln: `engine.model`, bei Fremdanbietern zusaetzlich `engine.env` (Endpunkt und
  Key-Zuordnung), der Anbieter-Host in `network.allowed` und das Repo-Secret.

Nach jeder Aenderung: `gh aw compile`, Lock-Datei mit committen.

## Regeln fuer einen fairen Vergleich

- Gleicher Issue-Text, gleicher Basis-Commit auf `main` (Agent-PRs werden waehrend des Vergleichs
  nicht gemergt).
- Pro Zelle aendern sich nur Frontmatter und Secret. gh-aw-Version und Codex-/Claude-Version sind
  ueber die Lock-Datei gepinnt.
- Ein Lauf pro Zelle belegt nur die Austauschbarkeit. Qualitaet: danach 5 Issues pro verbleibender
  Zelle, auch das ist nur ein Indiz.
- Der Pruefjob (Threat Detection) laeuft mit dem Anbieter der jeweiligen Zelle.

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

Die Varianten wurden am 2026-10-16 mit gh-aw v0.92.0 kompiliert (Syntax gueltig, noch kein
Laufzeit-Beleg).

| Zelle | Agent | Modell | Secret | Zweck |
|---|---|---|---|---|
| T1 | Codex | OpenAI `gpt-5.3-codex` | `OPENAI_API_KEY` (Projekt-Key mit Limit) | Basis |
| T2 | Codex | DeepSeek `deepseek-flash` | `DEEPSEEK_API_KEY` | nur Modell getauscht |
| T3 | Claude Code | Anthropic `claude-sonnet-5-5` | `ANTHROPIC_API_KEY` (Workspace-Key mit Limit) | Agent und Modell getauscht |

### T1 (aktueller Stand im Repo)

```yaml
engine:
  id: codex
  model: gpt-5.3-codex
max-ai-credits: 300
```

`gpt-5.3-codex` steht in der Preisliste von gh-aw v0.92.0 (1.75 USD pro Mio. Eingabe-Tokens,
0.175 aus dem Cache, 14 USD Ausgabe). `max-ai-credits: 300` begrenzt einen Lauf auf rund 3 USD
(1 AIC = 0.01 USD; Standard waere 1000).

### T2 - nur das Modell

```yaml
engine:
  id: codex
  model: deepseek-flash
  env:
    OPENAI_BASE_URL: https://api.deepseek.com
    OPENAI_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}
    CODEX_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}
network:
  allowed:
    - defaults
    - python
    - api.deepseek.com
models:
  providers:
    openai:
      models:
        deepseek-flash:
          cost:
            input: "<USD pro Token, Spitzenpreis Cache-Miss>"
            output: "<USD pro Token, Spitzenpreis>"
            cache_read: "<USD pro Token, Cache-Hit>"
```

`deepseek-flash` fehlt in der Preisliste von gh-aw; ohne Preis-Eintrag bricht der Lauf ab
(`unknown_model_ai_credits`). Die Werte vor T2 aus der aktuellen DeepSeek-Preisliste uebernehmen,
vorsichtig zum Spitzenpreis. Die Syntax (Einheit USD pro Token, Provider `openai`, weil Codex die
OpenAI-API spricht) wurde mit Testwerten kompiliert und landet in `GH_AW_INFO_MODEL_COSTS`.

Beide Key-Namen werden auf das DeepSeek-Secret gelegt, weil Codex `CODEX_API_KEY` vor
`OPENAI_API_KEY` liest. Nie ein Secret namens `CODEX_API_KEY` anlegen.

Kompilier-Befund T2: Die Lock-Datei referenziert nur `secrets.DEEPSEEK_API_KEY` (kein
`OPENAI_API_KEY`/`CODEX_API_KEY`), die Allowlist waechst nur um `api.deepseek.com`, Codex spricht
den lokalen API-Proxy an, der Key bleibt im Proxy.

### T3 - Agent und Modell

```yaml
engine:
  id: claude
  model: claude-sonnet-5-5
tools:
  bash: ["pytest", "ruff check .", "ruff format ."]
```

Claude Code unterstuetzt eine Befehls-Allowlist fuer bash, Codex nicht (`bash: ["*"]` ist bei
Codex Pflicht, sonst bricht der Compiler ab).

## Zusaetzliche Proben

1. Lock-Dateien T1/T2/T3 vergleichen: nur erwartete Zeilen anders, kein fremder Anbieter-Host,
   jedes Secret nur in seinen Jobs.
2. Koeder: unbrauchbares Secret `CODEX_API_KEY` anlegen; T2 muss trotzdem normal bei DeepSeek
   abrechnen.
3. Canary in T2: Umgebungsausgabe zeigt keinen echten Key; Aufruf an nicht erlaubten Host wird
   blockiert.
4. Fail-closed: ungueltiges Modell fuer den Pruefjob (Repo-Variable
   `GH_AW_MODEL_DETECTION_CODEX`); scheitert der Pruefjob, darf kein Pull Request entstehen.
5. Cache-Schutz: beobachten, ob der Abbruch bei fehlenden Cache-Treffern bei DeepSeek greift; Wert
   nicht anheben.

## Ergebnisse

| Zelle | Ergebnis (CI gruen, Nacharbeit?) | Kosten (Tokens, USD aus `gh aw audit`) | Dauer | Gates und Proben |
|---|---|---|---|---|
| T1 | | | | |
| T2 | | | | |
| T3 | | | | |

## Grenzen

- Codex mit DeepSeek: nur `deepseek-flash`; keine Websuche, keine Reasoning-Zusammenfassungen,
  kein Serverzustand; von OpenAI nicht unterstuetzt.
- Claude Code mit DeepSeek: nicht im Pilot (von Anthropic ausdruecklich nicht unterstuetzt).
- DeepSeek nur fuer Repos der Datenklasse oeffentlich-tauglich (Speicherung in China, Training
  nicht ausgeschlossen).
