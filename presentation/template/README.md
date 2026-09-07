# Nearform deck template for marimo

Helpers for building the talk as a marimo notebook that presents in the Nearform
house style. Everything here was derived from
[`../OS at Nearform Event Speaker Template.pptx`](../OS%20at%20Nearform%20Event%20Speaker%20Template.pptx) —
palette and fonts from `ppt/theme/theme1.xml` ("NearForm Master Base"), sizes and
spacing measured off its nine slides.

```
template/
  theme.py        palette, type scale, spacing, and the stylesheet generator
  components.py   the slide builders (imported as `nf`)
  assets.py       loads images from presentation/images/
  layout.py       generates layouts/<deck>.slides.json, incl. speaker notes
  nearform.css    generated — hand to marimo.App(css_file=...)
images/           headshots, logos, QR codes, diagrams
```

`../example_deck.py` is a working deck that uses every helper. Copy it as the
starting point for the real talk.

## Quick start

```python
import marimo

app = marimo.App(
    css_file="template/nearform.css",
    layout_file="layouts/my_deck.slides.json",
)

@app.cell
def _():
    import marimo as mo
    from template import nf, theme
    return mo, nf, theme

@app.cell
def _(nf):
    nf.title_slide(
        "Building an open-source data platform",
        event="Open Source Summit - 2026",
        author="Dario Scanferlato, Nearform",
    )
    return
```

One slide per cell. Run it with:

```bash
uv run marimo edit presentation/my_deck.py
```

and switch the app-preview dropdown to **Slides**, or present it directly with:

```bash
uv run marimo run presentation/my_deck.py --include-code --no-show-tracebacks
```

`--include-code` is what makes marimo's `C` key able to reveal a cell's source on
the slide; without it the source never reaches the browser.

## What the template gave us

| | |
|---|---|
| Navy `#000E38` | `dk1`/`dk2` — the default slide background |
| Mint `#00E5A4` | `accent1` — section breaks, numbers, the `_` motif |
| Purple `#8950FF`, Blue `#166BFF` | `accent2`/`accent3` |
| Lavender `#DDCAFF`, Pale blue `#E8F0FF`, Pale mint `#E5FCF5` | `accent4`–`accent6` |
| Inter (Light/Medium/Black) | all UI and body text |
| Bitter | pull quotes only (slides 4, 6, 7) |
| 10in × 5.625in | = 960×540, exactly reveal.js's base viewport |
| 9% / 17.4% | left margin and title baseline, held by every slide |
| Trailing `_` | the motif on titles ("OSS at Nearform_", "Questions_") |

Four tones are available — `navy` (default), `mint`, `pale`, `white` — each with
its own foreground, muted, accent and rule colours. Pass `tone=` to any builder.

## The builders

| Function | pptx slide | What it makes |
|---|---|---|
| `title_slide(title, event, author)` | 1 | mint 56pt title on navy |
| `speaker(name, role, handle, photo, note)` | 2 | who's talking, optional photo/QR |
| `section(title, kicker)` | 3 | navy title on the mint field |
| `closing(title="Questions")` | 8 | the same, for the end |
| `slide(*content, title, kicker, tone, page)` | — | the general frame |
| `stats([(value, label, note), ...])` | 4, 5 | the big-number row |
| `metrics([(value, label), ...])` | 6, 7 | the ruled 2×2 panel |
| `quote(text, author, role)` | 4, 6, 7 | pull quote in Bitter |
| `cards([(title, body), ...])` | — | tinted blocks |
| `two_col(left, right, ratio=(3, 2))` | 6, 7 | column split |
| `bullets([...])` | — | list with the `_` marker |
| `heading` `eyebrow` `lead` `body` `caption` | — | the type scale |
| `code(source, language)` | — | a code panel |
| `image(src, alt)` `logo()` `rule()` `spacer()` | — | odds and ends |

Everything returns `mo.Html`, so anything marimo renders — a dataframe, an
Altair chart, `mo.ui.run_button()` — drops straight into `slide(...)`:

```python
nf.slide(
    nf.two_col(nf.bullets([...]), mo.ui.altair_chart(chart), ratio=(2, 3)),
    title="Where the data comes from",
    kicker="Ingestion",
    page=7,
)
```

Bare strings passed to `slide()`, `body()`, `bullets()` and `cards()` are
markdown, so `**bold**` and links work.

### Images

Headshots, logos, QR codes and diagrams live in `presentation/images/`.
`assets.img()` loads one by name:

```python
from template import assets, nf

nf.speaker(
    name="Dario Ruben Scanferlato",
    role="Senior Data Engineer @ Nearform",
    photo=assets.img("profilepic.jpg"),
)
```

It goes through `mo.image`, so marimo serves the bytes itself — offline-safe and
still correct after `marimo export html`. `"profilepic.jpg"`,
`"images/profilepic.jpg"` and `"presentation/images/profilepic.jpg"` all resolve
to the same file, as does an absolute path.

A **missing** file renders a dashed placeholder naming what to drop where,
rather than raising — a half-built deck still presents. Before the talk, flip
that to a hard failure:

```python
assets.img("profilepic.jpg", strict=True)   # FileNotFoundError, and lists what's there
```

`assets.listing()` shows what's in the folder when a name doesn't match.

### Sizing

Type and spacing are in `cqw` — percent of the slide's own width — not px.
marimo hands reveal.js a stage sized to the window rather than a fixed 960px
one, so a px scale would be 8% of the deck on a projector and 20% in a narrow
pane. `slide()` declares the container those units resolve against, which is why
content belongs inside a `slide()` rather than returned from a cell on its own.

`theme.pt(38)` converts a pptx point size to the same scale if you need a size
the components don't cover.

## Speaker notes and slide order

marimo keeps the deck structure in `layouts/<deck>.slides.json`, which you can
build by hand in the app preview — or generate from code, which keeps the notes
in the repo and reviewable:

```python
from template import SKIP, Cell, write_slides_layout

write_slides_layout(
    "presentation/my_deck.py",
    [
        SKIP,                                                  # the import cell
        Cell(notes="Open cold. Name the talk, not yourself."),
        Cell(notes="30 seconds on me, then move."),
        Cell(type="fragment", notes="Reveal on click."),
        Cell(type="sub-slide", notes="Only if someone asks."),
    ],
    transition="none",
)
```

One entry per cell, in notebook order — marimo ignores the layout if the counts
disagree. `SKIP` hides a cell (imports, setup, helpers); `sub-slide` nests
vertically under the previous slide, which is a good home for a backup slide you
only reach if asked. Speaker view is reveal's `S` key.

## Before you present

- **Pin marimo.** Slides rendering has changed across patch releases; the
  version this was built against is `0.24.0`. Don't upgrade after the dry run.
- **Run locally, not from WASM.** `marimo export html-wasm` still fetches Pyodide
  from a CDN, and DuckDB extensions don't load under Pyodide, so no `s3://`.
- **Don't touch the layout dropdown live** — switching slides→vertical blanks the
  screen until restart (marimo#10159).
- **Slides that overflow scroll rather than shrink.** There is no clamp option
  (marimo#10306). If you see marimo's "Scroll for more" pill, cut content or
  split the slide.
- **Test the `S` speaker-notes window on the actual laptop.** The popup is known
  to hang at "Connecting…" in current Chromium/Firefox (marimo#10081).
- Add `--no-show-tracebacks` so a failing cell doesn't put a stack trace on the
  projector.

## Fonts

Inter and Bitter are not installed on this machine, so the deck currently renders
in Helvetica Neue and Georgia — metrically close, nothing reflows, but it isn't
quite the brand. For the real thing, install both as system fonts (they're on
Google Fonts, and Inter is in the Nearform Brand Hub) before the talk. No CSS
change is needed; the font stacks in `theme.py` pick them up. Don't `@import`
from a font CDN — the talk should run offline.

## Regenerating the stylesheet

`nearform.css` is generated. Edit `theme.py`, then:

```bash
uv run python -c "import sys; sys.path.insert(0, 'presentation'); from template import theme; theme.write_css()"
```

The components carry their own inline styles and mostly render correctly without
the stylesheet. What it adds is the part inline styles can't reach: full-bleed
slide backgrounds (the reveal `<section>` sits above our markup), the letterbox
colour, and overriding marimo's prose sizes so markdown inherits the deck's type
scale. Attach it — a deck without it has undersized headings and oversized body
text.
