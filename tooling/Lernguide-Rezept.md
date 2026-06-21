# Interaktiven Lernguide für ein neues Modul bauen — allgemeines Rezept

Dies ist die modul-agnostische Konsolidierung des erprobten Verfahrens, mit dem die
Guides in diesem Repo entstanden sind (**Betriebssysteme, Computertechnik 2, IIS2,
Physik Engines, SWEN2**). Folge dem Ablauf mit **Claude Code**, um für ein beliebiges
Modul denselben interaktiven Lernguide zu erzeugen. Die Phasen sind generisch; die
modul-spezifischen Entscheidungen fallen in **Phase 0** und unter „Pro Modul anpassen".

> **Quelle vs. Artefakt:** `<Modul> - Zusammenfassung.md` ist die **Quelle**,
> `<Modul> - Zusammenfassung.html` ist ein **Artefakt** eines deterministischen
> Generators `build_html.py`. **Das HTML nicht von Hand editieren** — Änderungen gehen
> ins Markdown (Inhalt) bzw. in den Generator (Struktur/Widgets), dann neu bauen.
> Die kanonische HTML-Struktur steht in [`template.html`](./template.html); der
> Generator-Starter in [`build_html.py`](./build_html.py).

## Was am Ende herauskommt
- **`<Modul> - Zusammenfassung.md`** — ein kombinierter Lernguide. Pro Thema zwei
  Unterabschnitte: **Erklärung** (Diagramme-als-Text, zentrale Begriffe/Befehle,
  Alltags-Analogien) und **Übungen** (Fragen, **mit der Lösung als Dropdown direkt
  unter jeder Frage**). ⚠️ Der frühere separate Sammelblock „Übungen — Lösungen" ist
  **deprecated** — er driftet leicht und zwingt zum Hin- und Herspringen; die Lösung
  gehört unter ihre Frage (siehe HTML-Baustein „Einklappbare Lösungen").
- **`<Modul> - Zusammenfassung.html`** — die interaktive Version: klebrige Sidebar mit
  Scroll-Spy, Diagramme, farbige Callouts, Klick-zum-Aufdecken der Lösungen, ein
  **Antwortfeld unter jeder Frage + „Export for grading"**, eine **Mock-Prüfung**,
  **Lab-Fragen** in ihren Kapiteln, ein **durchsuchbares Glossar**, **Sprunglinks von
  jeder Antwort zum exakten Abschnitt**, **Hover-Tooltips auf jeder Abkürzung** und
  **kleine, nutzer-getaktete Widgets** für die dynamischen Konzepte.
- *(optional)* **`Spicker.tex`** — ein dichter A4-Spickzettel (nur wenn in der
  Prüfung erlaubt — **vorher abklären**).

## Vor dem Start
1. Material je Thema in **einen Ordner, ein Unterordner pro Thema**: Vorlesungsfolien
   (PDF), Lab-/Übungsblätter (PDF), das **Lehrbuch** (PDF) falls vorhanden. Ordner in
   **Claude Code** öffnen. **Roh vs. editierbar trennen** (`Vorlesung/`+`Lab/` roh,
   `Notizen/` ist deins).
2. **PDF-Textextraktion.** Claude liest PDFs direkt; wenn der Backend bricht, ist
   **ghostscript** (kommt mit TeX) der verlässliche Fallback:
   ```bash
   gs -q -dNOPAUSE -dBATCH -sDEVICE=txtwrite -dFirstPage=A -dLastPage=B \
      -sOutputFile=/tmp/out.txt "Foliensatz.pdf"
   ```
   `txtwrite` verstümmelt Umlaute — Diagrammseiten lieber als **Bild mit dem Read-Tool**
   lesen und als Mermaid/CSS nachbauen. Bei langen Lehrbüchern den
   **PDF-Seite-vs-Druckseite-Offset einmal bestimmen** (`PDF-Seite = Druckseite + Offset`).
3. *(optional)* LaTeX (`pdflatex`) nur falls du den `Spicker.tex` willst.

---

## Der Ablauf — Prompts an Claude, in Reihenfolge
Arbeite **Thema für Thema / Kapitel für Kapitel**, speichere nach jedem — so verliert
eine Unterbrechung nie fertige Arbeit.

**Phase 0 — planen & entscheiden.**
> „Ich lerne `<Modul>`. Bau (a) einen kombinierten Markdown-Lernguide mit pro Thema
> Erklärung → Übungen → Übungen+Lösungen, und (b) optional einen dichten Ein-A4-LaTeX-
> Spicker. Frag mich nach Sprache, eine-Datei-vs-viele und Spicker-Dichte. Arbeite
> Thema für Thema und speichere nach jedem."

**Phase 1 — Markdown-Guide bauen.** Jedes Thema aus den Folien (+ Labs). Dann
selbsterklärend machen:
> „Für jeden Befehl/Fachbegriff/jede Abkürzung eine Ein-Zeilen-Erklärung *was es ist
> und wozu* — im Kapitel, wo es zuerst auftaucht. Setze keine Begriffe voraus. Stell
> sicher, dass alles zum Lösen der Übungen in der Erklärung darüber steht."
>
> ⏩ **Tempo:** Phase 1 parallelisiert sauber — **ein Subagent pro Thema** (die nicht
> überlappen), jeder gibt seinen Abschnitt **als finale Nachricht** zurück, der
> Hauptagent konkateniert. (Hintergrund-Subagents können keinen Write-Prompt
> beantworten → zurückgeben statt selbst schreiben.)

**Phase 2 — aus Lehrbuch / kanonischen Quellen anreichern.**
> „Geh das/die maßgebliche(n) Quelle(n) kapitelweise durch und fülle Wichtiges nach,
> das die Folien überspringen. Markiere die wichtigste Idee pro Kapitel mit einer
> 🎯-Zeile unter der Überschrift und prüfungskritische Punkte inline mit ⭐ Key."
>
> Bei mehreren Frameworks: **Terminologie-Drift vereinheitlichen** (z. B. „Sprint" ↔
> „Iteration", „Story" ↔ „PBI") auf eine Leit-Notation, Abweichungen als ⚠️ vermerken.

**Phase 3 — in interaktives HTML umwandeln (via Generator).**
> „Erzeuge das HTML aus dem Markdown mit `build_html.py`. **CSS-Box-Diagramme statt ASCII/Mermaid**
> (` ```flow `/` ```compare3 `/` ```entity `/` ```formula `), **Tabellendaten als echte `<table>`**,
> **sparsame** farbige Callouts (nur 🎯 wichtigste / ⭐ Key / ⚠️ Gotcha als Akzent — Begriffsdefinitionen
> als `#### Term` + Prosa, NICHT als 🧩-Box), einklappbare Lösungen direkt unter jeder Frage, klebrige
> Sidebar mit Scroll-Spy und durchsuchbarem Glossar. Markdown ist die einzige Quelle, HTML ist
> Build-Artefakt — bau kapitelweise im Generator."

**Phase 4 — Übung & Selbstbewertung.**
> „Antwortbox unter jede Frage (auto-gespeichert) und ein schwebender ‚Export for
> grading'-Button (Markdown-Download). Ein Kapitel mit gemischter Mock-Prüfung,
> gewichtet nach Prüfungsrelevanz. Lab-/Projekt-Fragen ans Ende des Kapitels, zu dem sie
> gehören, unter ‚🧪 Lab-Fragen'. Kurzer ‚So benutzt du das'-Abschnitt zuoberst."
>
> ⚠️ **Prüfungsformat zwingend abklären** (open/closed book, Hilfsmittel,
> schriftlich/mündlich, Dauer, Gewichtung). Schriftlich → gewichtete Mock-Prüfung +
> Timer; mündlich → 🎲 Prüfer-Modus (Zufallsfrage, Countdown, „Antwort zeigen" erst nach
> lautem Beantworten).

**Phase 5 — Sprunglinks (jede Antwort → ihre Erklärung).**
> „Gib jedem `<h3>`/`<h4>` eine stabile `id`. Dann unter jede Antwort einen Link zum
> exakten Abschnitt: `📖 Oben erklärt: <Abschnitt> ↗`. **Kapitelweise und jedes Ziel von
> Hand** — nicht per Keyword automatch, das verlinkt den falschen Abschnitt."

**Phase 6 — Glossar-Tooltips auf Abkürzungen.**
> „Skript, das beim Laden das Glossar liest und jede Abkürzung im Fliesstext in ein
> `<abbr>` mit eigener Hover-Card wrappt. Überspringe Code, Diagramme, das Glossar
> selbst, Links, Inputs und Widgets. Lies die Akronyme aus dem Glossar, damit es in sync
> bleibt." (Plus **„drei verwechselbare Begriffe"-Boxen** für die Klassiker.)

**Phase 7 — interaktive Animationen für dynamische Konzepte.**
> „Für Konzepte mit Schritten/Zustand/Zeit/Vorher-Nachher: ein kleines Widget.
> **Nutzer-getaktet** (Step/Next/Reset), **nie Autoplay**. **anime.js via CDN** mit
> **Feature-Check**, sodass jedes Widget auch ohne anime.js als Step-Through läuft.
> `prefers-reduced-motion` respektieren, Controls im Druck ausblenden."
>
> Animation **verdient ihren Platz nur, wenn sich das Konzept über die Zeit ändert** —
> für statische Fakten ist sie Lärm. Bewährte Formen: **State Machine** (Klick =
> Trigger, illegale Übergänge = disabled Buttons), **Gantt/Scheduler**,
> **Step-Through-Tracer** (eine Anomalie *sehen* lassen), **Lookup-/Zoom-Walk**,
> **Save/Restore-Stagger**, **A-vs-B-Stepper**, **Tabbed A/B/C-Stepper** (mehrere
> verwandte Szenarien in einem Widget — Tabs wechseln das Szenario, Step/Reset takten;
> ideal für „dasselbe Beispiel über N Algorithmen/Strategien", z. B. Nested-Loop ↔
> Sort-Merge ↔ Hash Join, oder Predicate-Pushdown Plan-Ebene ↔ Parquet-Scan),
> **„Hardware-Map-Journey"** (Marker wandert durch Komponenten-Boxen). Bei
> Monospace-/ASCII-Datenblöcken im Widget `white-space:pre; overflow-x:auto` (Demo:
> `.viz .data` in `template.html`) — so bleibt die Spaltenausrichtung und scrollt mobil.

**Phase 8 — lernen, dann bewerten *und anreichern*.** HTML öffnen, Antworten tippen,
**Export for grading**, mit **„grade these"** zurück an Claude. Claude bewertet, gibt
die perfekte Version, und ergänzt **für alles Falsche neue Callout-Boxen in der
*Erklärung darüber*** — nicht nur im Lösungsschlüssel. Das macht aus Bewerten Lernen.

**Phase 8b (optional) — Altklausur / Past-Paper als eigenes Kapitel.** Liegt eine alte
Prüfung vor (PDF/Bild), als **eigenes Kapitel** ans Ende aufnehmen: jede Originalfrage
im Wortlaut + **erklärte Musterlösung als Dropdown** (gleiche `<details>`-Mechanik wie
der Selbsttest). Sehr lernwirksam, weil es Format, Punkteverteilung und typische Fallen
1:1 trainiert. Pro Frage: knappe Aufgabenstellung, dann Lösung mit *Begründung* (nicht
nur Ergebnis), Diagramme/SQL wo passend, und einem ⭐/⚠️ zur typischen Falle. MC-Aufgaben
mit Richtig/Falsch **und Begründung je Aussage**. Im Markdown als normales `## N.`-Kapitel.

---

## Entscheidungen vorab
- **Sprache** (Fachbegriffe bleiben meist englisch).
- **Eine kombinierte Datei** vs. pro-Thema-Dateien (eine ist leichter durchsuch-/navigierbar).
- **Diagrammdichte** (grosszügig vs. wenige Kern-Diagramme).
- **Übungen + Lösungen behalten** — ja, sie werden zum Selbsttest.
- **HTML vs. LaTeX** für interaktiv — HTML gewinnt (Diagramme, einklappbare Lösungen,
  Antwortbox/Export, Tooltips, Sprunglinks); LaTeX nur für den statischen `Spicker`.
- **Prüfungsformat** — falls nirgends dokumentiert, in Phase 4 zwingend nachfragen.

## HTML-Bausteine
Die kanonische Struktur liegt vollständig in [`template.html`](./template.html) — dort
ist jede Komponente einmal vorgeführt. Kurzüberblick:
- **Prosa zuerst, Boxen als Akzent.** Den Hauptteil tragen `### Titel`, `#### Untertitel`,
  normale Absätze und Listen; Callout-Boxen nur für 🎯 Kernidee / ⭐ Faustregel / ⚠️ Falle.
  Faustregel: besteht ein Abschnitt fast nur aus Boxen, ist zu viel in Callouts gepackt
  (Demo „Fliesstext, Titel, Untertitel & Listen" in `template.html`). **Tabellarische Daten
  als echte Markdown-/HTML-`<table>`**, nicht als ASCII im `<pre>`.
- **Callout-Boxen** `.box.goal/.key/.simple/.howto/.warn` (+ `.box.formula`, `.box.framework`,
  `.box.concept`). `.box.concept` (🧩) = freiform Architektur-/Konzeptkarte für „Was/Aufgabe/
  Beispiel/Merke" ohne das starre Framework-Raster. ⚠️ **Boxen sparsam!** Default ist normale
  Prosa (`#### Term` + Absatz); Boxen nur als Akzent (🎯 1×/Kapitel, ⭐ prüfungskritisch, ⚠️ Falle).
  Begriffsdefinitionen gehören NICHT in 🧩-Boxen, sonst „alles hervorgehoben = nichts hervorgehoben".
- **Generator-Direktiven für wiederverwendbare CSS-Komponenten** (kompakte Daten → gestyltes HTML,
  statt ASCII im `<pre>`): ` ```flow ` (Pipeline/Loop aus Boxen; 1 Zeile/Schritt `Titel | Untertext`,
  erste Zeile `loop` = Zyklus), ` ```compare3 ` (drei verwechselbare Begriffe; `Term | Abgrenzung`,
  `!…` = Verwechslung), ` ```entity ` (Mini-DB-Tabelle; Zeile 1 = Name, Spalten `pk:`/`fk:`/`meas:`),
  ` ```star ` (Star-Schema; Zeile 1 = `FaktTabelle | Mass1, Mass2`, Folgezeilen = Dimensionen),
  ` ```formula ` (🧮-Karte; Zeile 1 = Ausdruck, `var | Bedeutung | Herkunft`, `=…` = Einsetz-Beispiel).
  ` ```html ` reicht rohes HTML durch (Escape-Hatch). Demos + CSS in `template.html`.
- **Diagramm-Entscheidung** (was → welche Form): **Tabellendaten → echte `<table>`** (NIE ASCII im `<pre>`);
  **Ablauf/Pipeline/Loop → ` ```flow `**; **drei verwechselbare Begriffe → ` ```compare3 `**;
  **einzelne DB-Tabelle → ` ```entity `, Star-Schema → ` ```star `**; **Formel → ` ```formula `**; rohe ASCII-Kunst nur als
  allerletzter Ausweg. ⚠️ **Kein Doppel-Diagramm**: zeigt eine CSS-`flow` die Pipeline schon, KEIN zusätzliches
  Mermaid derselben Sache (Redundanz = Lärm). Ziel: am Ende **0 `pre.ascii`** ausser echter Zeichen-Kunst.
- **Formelkarten** (`.box.formula`): nie nur den Ausdruck. Vier Teile — (1) Formel im
  Monospace-Block `.fla` (`white-space:pre-wrap`); (2) `.fvar`-Aufschlüsselung je Symbol
  *was es ist* + „↳ wo:" (gegeben / zählen / berechnen / Konstante / Unbekannte);
  (3) gerechnete **Einsetzen**-Zeile `.ex`; (4) **Adjust**-Zeile `.adj` (wie sich's
  ändert + die klassische Falle).
- **Framework-/Entscheidungsregel-Karten** (`.box.framework`) für qualitative Module:
  `Was · Wann · Beispiel · Falle · vs` (Abgrenzung zur Schwester-Idee).
- **Mermaid via CDN**, Diagramme als `<pre class="mermaid">`; hand-gebaute CSS-Boxen für
  was Mermaid schlecht kann (Pyramiden, Memory-Layouts).
- **Einklappbare Lösungen** `<details class="ans">` **direkt unter jeder `<div class="qa">`-Frage**
  (nicht als Sammelblock am Kapitelende). Für Past-Paper/Altklausur dieselbe Mechanik.
- **Sidebar-TOC + Scroll-Spy** via `IntersectionObserver`.
- **Glossar** als `<p class="g"><b>TERM</b> — Definition.</p>` in `#glist`. **Live-Suche in der
  Sidebar** (`#glsearch` → `#glres`): tippt man, erscheinen Treffer als klickbare Liste; Klick
  scrollt zum Eintrag und lässt ihn kurz aufblinken (`.g.hit`). Im `template.html` fertig verdrahtet.
- **Mobile-Härtung** (`@media(max-width:860px)`): Sidebar stapelt oben, Eingaben `font-size:16px`
  (verhindert iOS-Auto-Zoom), Tabellen/`pre`/`figure.diagram`/`.viz .data` `overflow-x:auto`,
  Headings skaliert. Alles im `template.html`-`<style>`.
- **Antwortboxen + Export**: Script injiziert `textarea.myans` (localStorage) und einen
  „Export"-Button, der alle Antworten als Markdown sammelt, kopiert und herunterlädt.
- **Stabile Heading-ids** `id="ch<N>-<slug>"` als Sprunglink-Ziele.
- **Sprunglinks** `<div class="ref">📖 Oben erklärt: <a href="#ch…">Abschnitt ↗</a></div>`.
- **Glossar-Tooltips**: TreeWalker wrappt Akronyme (`/^[A-Z][A-Z0-9]{1,9}$/`,
  Wortgrenzen, längste zuerst) in `<abbr class="gl" data-def="…">`; **eigene Hover-Card**
  (`#gl-tip`), **nicht** das native `title`. Skip: `PRE/CODE/SCRIPT/NAV/INPUT/…`,
  `#glist`, `.mermaid`, `.viz`.
- **Widgets**: je ein `.viz .viz-<name>`-Block, anime.js einmal via CDN, jedes Widget
  feature-checkt `typeof anime` + `prefers-reduced-motion` und fällt auf
  Instant-Snap/Step-Through zurück. **Tabbed A/B/C-Stepper** (`.tabs`/`.tab`/`.strip`/`.stp`/
  `.data`) für mehrere Szenarien in einem Widget — Demo + CSS in `template.html`. Self-contained:
  jedes Widget bringt sein eigenes `<script>`-IIFE mit den Szenario-Daten mit.
- **Dark- + Kompakt-Toggle** (beide localStorage); Kompakt blendet Prosa/Analogien/
  Widgets aus → dichtes Repetitions-Skelett.

## Markdown = Quelle, HTML = Artefakt
- **`python build_html.py`** baut das HTML aus dem Markdown. Der Generator besitzt alle
  Struktur (Markdown→HTML, Emoji-Callouts → `.box`-Klassen, Auto-Heading-`id`s via
  `slug()`). **Diagramme, Glossar, Widgets liegen als Daten im Generator**
  (`MERMAID = {kap: "<src>"}`, Glossar-Zeilen, Widget-Blöcke), nach Kapitel einsortiert.
  Am Ende gibt er eine **selbst-verifizierende Zusammenfassung + Tag-Balance-Check** aus.
- **Anreicherung** läuft als **separate, idempotente Anchor-Patch-Skripte** über das
  Markdown — verankert an einem **exakten existierenden Substring**, überspringt wenn
  schon vorhanden:
  ```
  H|<exakter Anker-Text>|<neue #### Überschrift davor>
  C|<exakter Anker-Text>|<💡/⚠️/⭐ Callout danach>
  ```

## Pro Modul anpassen — quantitativ vs. qualitativ
| Quantitatives Modul (BSY, CT2, Physik Engines) | Qualitatives Modul (SWEN2, Teile von IIS2) |
|---|---|
| **Formelkarten 🧮** + ggf. Live-KaTeX-Rechner zentral | **Framework-/Entscheidungsregel-Karten 🧩** + **Vergleichstabellen** zentral |
| Simulationen (Scheduler, Stoss, ADC, Page-Replacement) | **Prozess-Stepper** (TDD-Zyklus, Scrum-Sprint, CI/CD, Kanban) |
| Einheiten-/Vorzeichen-Fallen | **Terminologie-Drift** zwischen Frameworks (⚠️) |
| Ein Lehrbuch | oft **mehrere kanonische Bücher**, je Thema die maßgebliche Quelle |

- **Vergleichstabellen** („X vs. Y vs. Z") sind bei qualitativen Modulen das wichtigste
  Format überhaupt.
- **„Drei verwechselbare Begriffe"-Boxen** sind das Lern-Gold (z. B. CI vs. CD vs.
  Continuous Deployment; DoR vs. DoD; deadlock vs. livelock vs. starvation).
- **Worked-Calculation immer mitzeigen**: jedes rechnende Widget druckt die volle
  Arithmetik mit den aktuellen Werten — die zugehörige 🧮/🧩-Karte wird zum lebenden Beispiel.

## Tipps & Gotchas (modul-übergreifend bestätigt)
- **Formeln/Konzepte so erklären, dass man sie *anwenden* kann**, nicht nur wiedererkennt:
  je Variable/Element *was es ist*, *woher der Wert kommt* bzw. *wann man es einsetzt*,
  ein konkretes Beispiel, die typische Verwechslung.
- **Markdown nicht hart umbrechen** — eine Zeile pro Absatz/Listenpunkt (manuelle
  ~80-Zeichen-Umbrüche reflowen schlecht).
- **Export-Whitespace normalisieren**: `&nbsp;` wird beim `textContent`-Lesen zu U+00A0;
  beim Erfassen `qEl.textContent.replace(/\s+/g,' ').trim()` (JS `\s` matcht U+00A0).
- **Cross-Linking nie per Keyword automatchen** — ids in Masse setzen ist ok, die
  Ziel-Wahl jeder Antwort von Hand, Kapitel für Kapitel.
- **Skripten ja — aber nie eine *Wahl* dem Skript überlassen.** Bei voll spezifizierten
  `old → new`-Paaren: in einem Python-Pass anwenden, aber **nur wenn `old` genau einmal
  vorkommt** (`count == 1`-Guard), fehlende/mehrdeutige Paare **überspringen + melden**.
- **Jedes *rechnende* Widget zuerst in Node verifizieren** (Scheduler, Page-Replacement,
  Little's Law: `Durchlaufzeit·Durchsatz = WIP`), Invarianten asserten, Loop-Cap gegen
  Hänger. Dann *dieselben* Funktionen ins Widget kopieren.
- **Widget-CSS scopen** (`.viz` + `.viz-<name>`); `:not()` für geteilte Controls;
  CSS-Spezifität beachten (gleich spezifische Regeln entscheidet die Quell-Reihenfolge).
- **Eigene Hover-Card schlägt natives `title`** (langsam, ungestylt).
- **Animationen: progressive enhancement, immer.** Eine Wache überall:
  `if (reduced || typeof anime === 'undefined') { Endzustand sofort } else { animiere }`.
  Nur dynamische Konzepte, nutzer-getaktet, kein Autoplay.
- **`<`, `>`, `&` escapen** beim Einbau in HTML (`&lt; &gt; &amp;`).
- **`extract_shell()` muss HTML-Kommentare strippen** (`re.sub(r"<!--.*?-->","",tpl,flags=re.S)` VOR den
  `<style>`/`<script>`-Regexes). Der Template-Kommentar enthält den Text „<style>/<script>" und wird sonst
  mitgegriffen → Kommentar + `<html><head>` landen im `<head>` und zerschiessen das Layout. (Hart gelernt; im Starter gefixt.)
- **Boxen sind selten, nicht der Default.** Begriffsdefinitionen → `#### Term` + Prosa, NICHT 🧩. Faustregel:
  am Ende sollten **Absätze > Boxen** sein und 🧩 ≈ 0. „Wenn alles hervorgehoben ist, ist nichts hervorgehoben."
- **Fortgeschrittene Ansichts-Patterns** (Referenz-Implementierung: `Notizen/build_html.py`): **Ansichts-Modi**
  (Voll / Theorie / Fragen / Kompakt) via `html.mode-*` + Body-Zonen `.zone.theory`/`.zone.exercises`
  (Generator wickelt Erklärung vs. Übungen); **„So benutzt du das" als Modal** hinter ?-Icon statt Sektion;
  **Mock-Prüfung mit Inline-Antwortfeldern + eigenem Export** (nur die gezogenen Fragen). Bei Bedarf portieren.
- **Cloud-Sync-Ordner** (ProtonDrive/Dropbox) können die Datei zwischen Read und Edit
  umschreiben → direkt vor jedem Edit neu lesen.
- **Struktur per grep verifizieren** nach jedem Pass (Themen-Header, `## Erklärung/
  Übungen/Lösungen`, `.qa`, `<details>`-Parität, Sprunglinks-vs-Antworten,
  `<div>`-Balance, Code-Fence-Parität). Spinnt die Shell-`grep`: `/usr/bin/grep`.
- **Lab-Sheets**: nur die *bewertbaren* Fragen ziehen („erkläre/warum/was beobachtest
  du"), reine „mach X"-Schritte weglassen, jede ans Ende des passenden Kapitels.

## Hilft es, alte `build_html.py`-Skripte als Referenz zu behalten?
**Ja — aber mit Augenmaß.** Die per-Modul-Generatoren enthalten Modul-*Daten* (Diagramme,
Glossar, Widgets), sind also nicht 1:1 wiederverwendbar; ihr Wert ist **strukturell**
(`slug()`, `MERMAID`-Dict, Widget-IIFE-Muster, Tag-Balance-Check). Der wiederverwendbare
Kern steckt im Starter [`build_html.py`](./build_html.py). Eigene alte Skripte als
Nachschlage-Beispiele in `Referenz Material/` ablegen (bleibt gitignored).

## Schnell-Checkliste
- [ ] **Phase 0** — Sprache / eine Datei / Diagrammdichte / HTML; Material je Thema sortiert
- [ ] **Phase 1** — kombiniertes `<Modul> - Zusammenfassung.md`, pro Thema Erklärung/Übungen/Lösungen (1 Subagent pro Thema)
- [ ] **Phase 2** — angereichert aus Lehrbuch/kanonischen Quellen (🎯 + ⭐), Terminologie vereinheitlicht (⚠️)
- [ ] **Phase 3** — interaktives HTML via `build_html.py` (Mermaid, Callouts, Sidebar, Glossar, Formel-/Framework-Karten, Dark/Kompakt)
- [ ] **Phase 4** — Antwortboxen + Export, **Prüfungsformat abklären**, Mock/Prüfer-Modus, Lab-Fragen pro Kapitel
- [ ] **Phase 5** — stabile Heading-ids + handverlesene Antwort→Erklärung-Sprunglinks
- [ ] **Phase 6** — Glossar-Tooltips + „drei verwechselbare Begriffe"-Boxen
- [ ] **Phase 7** — nutzer-getaktete anime.js-Widgets (feature-checked, kein Autoplay)
- [ ] **Phase 8** — Lern-Loop: Antworten → Export → „grade these" → bewerten *und* anreichern
