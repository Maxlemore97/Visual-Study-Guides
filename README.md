# Visual Study Guides

Clean, single-file HTML study guides — each one a self-contained webpage with a
sticky table of contents, colour-coded callouts (goal / key idea / simplified /
how-to / warning) and syntax-highlighted code. Open any file in a browser; no
build step, no dependencies.

## Guides

| Topic | Language | Open |
|-------|----------|------|
| Betriebssysteme (Operating Systems) — Zusammenfassung | 🇩🇪 German | [View](https://maxlemore97.github.io/Visual-Study-Guides/Betriebssysteme%20-%20Zusammenfassung.html) · [Source](./Betriebssysteme%20-%20Zusammenfassung.html) |
| CT 2 — Zusammenfassung | 🇩🇪 German | [View](https://maxlemore97.github.io/Visual-Study-Guides/CT%202%20-%20Zusammenfassung.html) · [Source](./CT%202%20-%20Zusammenfassung.html) |
| IIS2 — Zusammenfassung | 🇩🇪 German | [View](https://maxlemore97.github.io/Visual-Study-Guides/IIS2%20-%20Zusammenfassung.html) · [Source](./IIS2%20-%20Zusammenfassung.html) |
| Physik Engines — Zusammenfassung | 🇩🇪 German | [View](https://maxlemore97.github.io/Visual-Study-Guides/Physik%20Engines%20-%20Zusammenfassung.html) · [Source](./Physik%20Engines%20-%20Zusammenfassung.html) |
| SWEN2 — Zusammenfassung | 🇩🇪 German | [View](https://maxlemore97.github.io/Visual-Study-Guides/SWEN2%20-%20Zusammenfassung.html) · [Source](./SWEN2%20-%20Zusammenfassung.html) |

> The **View** links work once GitHub Pages is enabled for this repo
> (Settings → Pages → deploy from `main`, root). Until then, download the file
> and open it locally.

## Viewing locally

Clone the repo and open any `.html` file directly in your browser:

```bash
git clone https://github.com/Maxlemore97/Visual-Study-Guides.git
cd Visual-Study-Guides
open "Betriebssysteme - Zusammenfassung.html"   # macOS (use xdg-open on Linux)
```

## Adding a new guide

The full, battle-tested method lives in **[`Lernguide-Rezept.md`](./Lernguide-Rezept.md)**
(German) — an 8-phase recipe for turning a module's slides into an interactive guide.
Two reusable starting points come with it:

- **[`template.html`](./template.html)** — an all-in-one demo template showing every
  reusable component (callouts, formula/framework cards, self-test, glossary tooltips,
  Mermaid, dark/compact toggle, answer-box + export, a widget stub). Copy it to
  `<Module> - Zusammenfassung.html` and fill in your chapters.
- **[`build_html.py`](./build_html.py)** — a Markdown-first generator: write
  `<Module> - Zusammenfassung.md`, run `python build_html.py "<Module> - Zusammenfassung.md"`,
  and it emits the HTML using the same CSS/JS shell as `template.html` (so the two stay
  in sync). The HTML is a build artifact — edit the Markdown, not the HTML.

Then:

1. Add the new `<Module> - Zusammenfassung.html` to the repo root.
2. Add a row to the **Guides** table above.
3. Commit — that's it.

## License

Free to use for studying. Attribution appreciated.
