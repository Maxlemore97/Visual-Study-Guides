#!/usr/bin/env python3
"""
build_html.py — Generator-Starter für interaktive Lernguides.

    Markdown = QUELLE, HTML = ARTEFAKT. Das HTML NICHT von Hand editieren —
    Inhalt geht ins Markdown, Struktur/Widgets in diesen Generator, dann neu bauen.

Aufruf:
    python build_html.py "<Modul> - Zusammenfassung.md"
    python build_html.py "<Modul> - Zusammenfassung.md" -o out.html
    python build_html.py            # nimmt das erste "*Zusammenfassung.md" im Ordner

Was dieser Starter abdeckt (der wiederverwendbare KERN):
  - Markdown → HTML: Überschriften, Absätze, Listen, Tabellen, Code-Fences,
    ```mermaid```-Blöcke → <pre class="mermaid">.
  - Emoji-Callouts: ein Absatz, der mit 🎯/⭐/💡/🛠️/⚠️ beginnt, wird zur passenden
    .box-Klasse (goal/key/simple/howto/warn).
  - Kapitel: "## N. Titel" → <section class="chapter" id="chN"> + <h2 class="chap">.
  - Stabile Heading-ids via slug(): "### Sub" → <h3 id="chN-sub">.
  - TOC-Generierung aus den Kapitel-Überschriften.
  - CSS/JS-Shell wird aus template.html GELESEN → Template & Generator bleiben in sync.
  - Selbst-verifizierende Zusammenfassung + Tag-Balance-Check auf stdout.

Bewusst NICHT generisch automatisiert (kommen als DATEN bzw. HTML-Passthrough):
  - Formelkarten (🧮) / Framework-Karten (🧩): als fertiges HTML im Markdown
    durchreichen (HTML in Markdown wird unverändert übernommen) ODER hier aus FORMULA/
    FRAMEWORK-Dicts rendern — modul-spezifisch, daher Slot statt Automatik.
  - Diagramme/Glossar/Widgets, die nicht inline im Markdown stehen: in die Dicts unten
    eintragen, nach Kapitelnummer einsortiert (so machen es die per-Modul-Generatoren).

Konventionen im Markdown:
  # Titel                  → Seitentitel / <h1>
  ## 1. Kapitel            → neues Kapitel (Nummer steuert id="ch1")
  ### / #### Unterabschnitt → <h3>/<h4> mit stabiler id
  🎯/⭐/💡/🛠️/⚠️ am Zeilenanfang → Callout-Box
  ```mermaid … ```         → Mermaid-Diagramm
  ```lang … ```            → Code-Block
  | a | b |                → Tabelle (mit Trenner-Zeile |---|---|)
  Q: … / A: …              → Selbsttest (Frage + einklappbare Antwort)
  Rohes HTML im Markdown   → unverändert übernommen (für Formel-/Framework-Karten etc.)
"""

import re
import sys
import html
import pathlib
import argparse

# ---------------------------------------------------------------------------
# DATEN-SLOTS — pro Modul füllen (nach Kapitelnummer). Wie in den per-Modul-
# Generatoren: hier liegen die Dinge, die nicht inline im Markdown stehen.
# ---------------------------------------------------------------------------
MERMAID: dict[int, str] = {}      # {1: 'flowchart LR\n A --> B'}  → ans Kapitelende
GLOSSARY: list[tuple[str, str]] = []  # [('CPU', 'Central Processing Unit …')]
WIDGETS: dict[int, str] = {}      # {3: '<div class="viz viz-…">…</div>'} → ans Kapitelende

CALLOUTS = {  # Emoji am Zeilenanfang → (box-Klasse, Label)
    "🎯": ("goal",   "🎯 Am wichtigsten"),
    "⭐": ("key",    "⭐ Key"),
    "💡": ("simple", "💡 Einfach gesagt"),
    "🛠️": ("howto",  "🛠️ How-to"),
    "🛠": ("howto",  "🛠️ How-to"),
    "⚠️": ("warn",   "⚠️ Stolperstein"),
    "⚠": ("warn",   "⚠️ Stolperstein"),
}


def slug(text: str) -> str:
    """Stabiler Anker: Tags/Entities raus, lowercase, Nicht-Alphanumerik → '-'."""
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text).lower()
    text = re.sub(r"[^a-z0-9äöüß]+", "-", text).strip("-")
    return text or "x"


def inline(text: str) -> str:
    """Inline-Markdown → HTML (auf escaptem Text). Reihenfolge: code, bold, italic, link."""
    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return text


def is_html_block(line: str) -> bool:
    return line.lstrip().startswith("<")


def convert(md: str):
    """Markdown → (body_html, toc_entries, title). Zeilen-basiert, deterministisch."""
    lines = md.split("\n")
    out: list[str] = []
    toc: list[tuple[str, str, str]] = []   # (id, num/label, titel)
    title = "Modul — Zusammenfassung"
    chap_no = 0
    chap_open = False
    i, n = 0, len(lines)

    def close_chapter():
        nonlocal chap_open
        if chap_open:
            if chap_no in MERMAID:
                out.append(f'<figure class="diagram"><pre class="mermaid">\n'
                           f'{html.escape(MERMAID[chap_no])}\n</pre></figure>')
            if chap_no in WIDGETS:
                out.append(WIDGETS[chap_no])
            out.append("</section>")
            chap_open = False

    while i < n:
        line = lines[i]

        # --- Code-/Mermaid-Fence ---
        m = re.match(r"^```(\w*)\s*$", line)
        if m:
            lang = m.group(1)
            i += 1
            buf = []
            while i < n and not re.match(r"^```\s*$", lines[i]):
                buf.append(lines[i]); i += 1
            i += 1  # schliessendes ```
            code = "\n".join(buf)
            if lang == "mermaid":
                out.append(f'<figure class="diagram"><pre class="mermaid">\n'
                           f'{html.escape(code)}\n</pre></figure>')
            else:
                out.append(f"<pre><code>{html.escape(code)}</code></pre>")
            continue

        # --- Rohes HTML unverändert durchreichen (Formel-/Framework-Karten etc.) ---
        if is_html_block(line):
            out.append(line); i += 1
            continue

        # --- Überschriften ---
        h = re.match(r"^(#{1,6})\s+(.*)$", line)
        if h:
            level, txt = len(h.group(1)), h.group(2).strip()
            if level == 1:
                title = re.sub(r"<[^>]+>", "", txt)
                out.append(f'<h1 class="title">{inline(txt)}</h1>')
            elif level == 2:
                close_chapter()
                chap_no += 1
                num_m = re.match(r"^(\d+)\.", txt)
                cid = f"ch{num_m.group(1)}" if num_m else f"ch{chap_no}"
                num = num_m.group(1) if num_m else str(chap_no)
                out.append(f'<section class="chapter" id="{cid}">')
                out.append(f'<h2 class="chap">{inline(txt)}</h2>')
                chap_open = True
                toc.append((cid, num, re.sub(r"^\d+\.\s*", "", re.sub(r"<[^>]+>", "", txt))))
            else:
                cid = f"ch{chap_no}-{slug(txt)}"
                out.append(f'<h{level} id="{cid}">{inline(txt)}</h{level}>')
            i += 1
            continue

        # --- Selbsttest: Q:/A: ---
        mq = re.match(r"^Q:\s*(.*)$", line)
        if mq:
            out.append(f'<div class="qa"><div class="q">{inline(mq.group(1))}</div></div>')
            i += 1
            if i < n:
                ma = re.match(r"^A:\s*(.*)$", lines[i])
                if ma:
                    out.append('<details class="ans"><summary>Antwort</summary>'
                               f'<div class="a">{inline(ma.group(1))}</div></details>')
                    i += 1
            continue

        # --- Callout (Emoji am Zeilenanfang) ---
        stripped = line.lstrip()
        hit = next((e for e in CALLOUTS if stripped.startswith(e)), None)
        if hit:
            cls, lab = CALLOUTS[hit]
            body = stripped[len(hit):].strip()
            body = re.sub(r"^\*\*[^*]+\*\*[:：]?\s*", "", body)  # evtl. eigenes Label entfernen
            out.append(f'<div class="box {cls}"><span class="lab">{lab}</span>{inline(body)}</div>')
            i += 1
            continue

        # --- Tabelle ---
        if line.strip().startswith("|") and i + 1 < n and re.match(r"^\s*\|?[\s:\-|]+\|?\s*$", lines[i + 1]):
            header = [c.strip() for c in line.strip().strip("|").split("|")]
            i += 2  # header + Trenner
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            thead = "".join(f"<th>{inline(c)}</th>" for c in header)
            tbody = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows)
            out.append(f"<table><thead><tr>{thead}</tr></thead><tbody>{tbody}</tbody></table>")
            continue

        # --- Listen ---
        if re.match(r"^\s*[-*]\s+", line) or re.match(r"^\s*\d+\.\s+", line):
            ordered = bool(re.match(r"^\s*\d+\.\s+", line))
            tag = "ol" if ordered else "ul"
            items = []
            while i < n and (re.match(r"^\s*[-*]\s+", lines[i]) or re.match(r"^\s*\d+\.\s+", lines[i])):
                items.append(re.sub(r"^\s*(?:[-*]|\d+\.)\s+", "", lines[i]))
                i += 1
            out.append(f"<{tag}>" + "".join(f"<li>{inline(it)}</li>" for it in items) + f"</{tag}>")
            continue

        # --- Leerzeile / Absatz ---
        if line.strip() == "":
            i += 1
            continue
        para = [line]
        i += 1
        while i < n and lines[i].strip() != "" and not re.match(r"^(#{1,6}\s|```|\s*[-*]\s|\s*\d+\.\s|\||Q:|A:)", lines[i]) and not is_html_block(lines[i]):
            para.append(lines[i]); i += 1
        out.append(f"<p>{inline(' '.join(s.strip() for s in para))}</p>")

    close_chapter()
    return "\n".join(out), toc, title


def extract_shell(template_path: pathlib.Path):
    """<style>…</style> und den letzten <script>…</script>-Block aus template.html holen."""
    tpl = template_path.read_text(encoding="utf-8")
    style = re.search(r"<style>.*?</style>", tpl, re.S)
    scripts = re.findall(r"<script>.*?</script>", tpl, re.S)  # inline scripts (ohne src)
    cdn = re.findall(r'<script src="[^"]+"></script>', tpl)
    if not style or not scripts:
        sys.exit("template.html: <style> oder <script> nicht gefunden.")
    return style.group(0), "\n".join(cdn), "\n".join(scripts)


def build_toc(toc):
    rows = ['<a href="#howto"><span class="num">ℹ️</span>So benutzt du das</a>']
    for cid, num, t in toc:
        rows.append(f'<a href="#{cid}"><span class="num">{num}</span>{html.escape(t)}</a>')
    rows.append('<a href="#glossar"><span class="num">📖</span>Glossar</a>')
    return "\n".join(rows)


def build_glossary():
    if not GLOSSARY:
        return ""
    rows = "".join(f'<p class="g"><b>{html.escape(t)}</b> — {inline(d)}</p>' for t, d in GLOSSARY)
    return ('<section class="chapter" id="glossar"><h2 class="chap">📖 Glossar</h2>'
            f'<div id="glist">{rows}</div></section>')


def check_balance(out_html: str, md: str):
    """Tag-Balance + Code-Fence-Parität — meldet Probleme, blockiert aber nicht."""
    ok = True
    for tag in ("div", "section", "details"):
        o = len(re.findall(rf"<{tag}\b", out_html))
        c = len(re.findall(rf"</{tag}>", out_html))
        flag = "ok" if o == c else "‼️ UNBALANCED"
        if o != c:
            ok = False
        print(f"  <{tag}>: {o} offen / {c} geschlossen … {flag}")
    fences = md.count("\n```")
    fence_ok = "ok" if fences % 2 == 0 else "‼️ ungerade Anzahl ```"
    if fences % 2:
        ok = False
    print(f"  Code-Fences: {fences} … {fence_ok}")
    return ok


def main():
    ap = argparse.ArgumentParser(description="Markdown → interaktiver Lernguide (HTML).")
    ap.add_argument("source", nargs="?", help="Pfad zur <Modul> - Zusammenfassung.md")
    ap.add_argument("-o", "--output", help="Ausgabe-HTML (Default: gleicher Name, .html)")
    ap.add_argument("-t", "--template", default="template.html", help="HTML-Shell (Default: template.html)")
    args = ap.parse_args()

    here = pathlib.Path(__file__).parent
    if args.source:
        src = pathlib.Path(args.source)
    else:
        cands = sorted(here.glob("*Zusammenfassung.md"))
        if not cands:
            sys.exit("Keine Quelle angegeben und kein '*Zusammenfassung.md' gefunden.")
        src = cands[0]
        print(f"Quelle (autom.): {src.name}")
    if not src.exists():
        sys.exit(f"Quelle nicht gefunden: {src}")

    out_path = pathlib.Path(args.output) if args.output else src.with_suffix(".html")
    template_path = (here / args.template) if not pathlib.Path(args.template).is_absolute() else pathlib.Path(args.template)
    if not template_path.exists():
        sys.exit(f"Template nicht gefunden: {template_path}")

    md = src.read_text(encoding="utf-8")
    body, toc, title = convert(md)
    style, cdn, scripts = extract_shell(template_path)
    toc_html = build_toc(toc)
    glossary_html = build_glossary()

    doc = f"""<!doctype html>
<!-- ARTEFAKT — generiert von build_html.py aus {html.escape(src.name)}. NICHT von Hand editieren. -->
<html lang="de" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
{style}
</head>
<body>
<div id="topbar">
  <span class="brand">{html.escape(title)}</span>
  <button id="btn-compact" title="Prosa/Analogien ausblenden">📋 Kompakt</button>
  <button id="btn-dark" title="Hell/Dunkel umschalten">🌙 Dark</button>
</div>
<div class="wrap">
  <nav class="toc" id="toc">
    <h2>Inhalt</h2>
    <input id="navsearch" type="search" placeholder="Kapitel filtern…">
    {toc_html}
  </nav>
  <main>
    <section id="howto">
      <h2 class="chap">ℹ️ So benutzt du das</h2>
      <div class="box simple"><span class="lab">💡 Worum geht's</span>
        Sidebar + Suche zum Navigieren, Dark/Kompakt oben, Antwortboxen im Selbsttest,
        „Export for grading" schickt deine Antworten zurück an Claude.</div>
    </section>
{body}
{glossary_html}
  </main>
</div>
<div id="exportbar"><button id="btn-export">⬇︎ Export for grading</button></div>
{cdn}
{scripts}
</body>
</html>
"""

    out_path.write_text(doc, encoding="utf-8")
    print(f"\n✅ geschrieben: {out_path.name}")
    print(f"   Kapitel: {len(toc)} · Glossar-Einträge: {len(GLOSSARY)} · "
          f"Mermaid: {len(MERMAID)} · Widgets: {len(WIDGETS)}")
    print("Tag-Balance-Check:")
    ok = check_balance(doc, md)
    print("Alles balanciert ✅" if ok else "⚠️ Bitte Unbalancen oben prüfen.")


if __name__ == "__main__":
    main()
