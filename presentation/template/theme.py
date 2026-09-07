"""Nearform brand tokens, lifted from the event speaker template.

Source: ``presentation/OS at Nearform Event Speaker Template.pptx``
  - palette + fonts: ``ppt/theme/theme1.xml`` ("NearForm Master Base")
  - geometry:        ``ppt/presentation.xml`` sldSz 9144000x5143500 EMU = 10in x 5.625in
  - type sizes:      measured off slides 1-9

The deck is 10in x 5.625in, which maps 1:1 onto marimo's reveal.js base
viewport of 960x540 px (96 px per inch). Every size below is therefore
``points_from_the_pptx * 96/72``.

Run ``python -m template.theme`` to regenerate ``nearform.css``.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# --------------------------------------------------------------------------
# Palette  (theme1.xml colour scheme)
# --------------------------------------------------------------------------

NAVY = "#000E38"  # dk1 / dk2 - the primary dark background
MINT = "#00E5A4"  # accent1  - the signature Nearform accent
PURPLE = "#8950FF"  # accent2
BLUE = "#166BFF"  # accent3, also the hyperlink colour
LAVENDER = "#DDCAFF"  # accent4
PALE_BLUE = "#E8F0FF"  # accent5
PALE_MINT = "#E5FCF5"  # accent6
SLATE = "#31416F"  # lt2 - muted text
MUTED = "#526288"  # lt2 in the "Nearform 1.0" variant
WHITE = "#FFFFFF"

#: Ordered accents, for charts and anything that needs a categorical ramp.
ACCENTS = (MINT, PURPLE, BLUE, LAVENDER, PALE_BLUE, PALE_MINT)


# --------------------------------------------------------------------------
# Tones - the four slide backgrounds the template actually uses
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Tone:
    """A slide background and the text colours that sit on it."""

    name: str
    bg: str
    fg: str  # primary text
    muted: str  # secondary text
    accent: str  # numbers, markers, the trailing underscore
    rule: str  # hairlines and dividers


TONES: dict[str, Tone] = {
    # slides 1, 5, 6, 7 - the default
    "navy": Tone("navy", NAVY, WHITE, "#8F9AB8", MINT, "#1E2A54"),
    # slides 3, 8 - section breaks and "Questions_"
    "mint": Tone("mint", MINT, NAVY, SLATE, NAVY, "#00B37F"),
    # slide 9 - resources / appendix
    "pale": Tone("pale", PALE_MINT, NAVY, MUTED, BLUE, "#C6EFE0"),
    # for dense content that wants maximum contrast
    "white": Tone("white", WHITE, NAVY, MUTED, BLUE, "#DDE3F0"),
}

DEFAULT_TONE = "navy"


def tone(name: str) -> Tone:
    """Look up a tone by name, with a useful error for typos."""
    try:
        return TONES[name]
    except KeyError:
        raise ValueError(
            f"unknown tone {name!r}; expected one of {', '.join(TONES)}"
        ) from None


# --------------------------------------------------------------------------
# Typography
# --------------------------------------------------------------------------

#: Inter is the brand face. It is *not* installed on this machine, so the
#: stack degrades to Helvetica Neue, which is metrically close enough that
#: nothing reflows. See README for self-hosting Inter.
SANS = (
    "'Inter', 'Inter var', -apple-system, BlinkMacSystemFont, "
    "'Helvetica Neue', Arial, sans-serif"
)
#: Bitter is the template's pull-quote serif (slides 4, 6, 7).
SERIF = "'Bitter', Georgia, 'Times New Roman', serif"
MONO = "var(--marimo-monospace-font), ui-monospace, SFMono-Regular, Menlo, monospace"

# --------------------------------------------------------------------------
# Geometry
#
# The design canvas is the pptx's own: 960x540. marimo does *not* hand reveal a
# fixed 960px stage though - it sizes the stage to the window and scales from
# there, so a length in px would be 8% of the deck on a laptop and 20% on a
# narrow pane. Everything below is therefore expressed in `cqw` (percent of the
# slide's own width), which holds the template's proportions at any deck size.
# `slide()` declares the container that `cqw` resolves against.
# --------------------------------------------------------------------------

DECK_W = 960
DECK_H = 540
PT = 96 / 72  # 1 PowerPoint point in canvas pixels


def scale(canvas_px: float) -> str:
    """Convert a length on the 960x540 canvas into a deck-relative unit."""
    return f"{canvas_px / DECK_W * 100:.4g}cqw"


def pt(points: float) -> str:
    """Convert a pptx point size into a deck-relative unit."""
    return scale(points * PT)


# Sizes measured off the template, in points.
SIZE = {
    "display": pt(56),  # slide 1 title
    "title": pt(38),  # section titles, slides 3 and 8
    "heading": pt(22),  # speaker name, slide 2
    "subhead": pt(18),  # stat values, handles
    "lead": pt(15),  # slide 1 subtitle
    "body": pt(12),  # body copy, slides 5-7
    "small": pt(10),  # stat captions
    "caption": pt(8),  # footnotes, quote attribution
}

WEIGHT = {"light": 300, "regular": 400, "medium": 500, "bold": 700, "black": 900}

# Spacing, measured off the template as a fraction of the deck.
SPACE = {
    "margin_x": scale(86),  # 9.0% - every text block starts here
    "margin_top": scale(94),  # 17.4% - the title baseline on content slides
    "margin_bottom": scale(48),
    "gap": scale(24),  # the template's repeating vertical rhythm
    "gap_lg": scale(48),
    "gap_sm": scale(12),
    "tight": scale(6),
    "radius": scale(12),
}

#: 16:9, so a slide keeps the deck's shape even in marimo's vertical layout.
SLIDE_MIN_HEIGHT = f"{DECK_H / DECK_W * 100:.4g}cqw"

#: The trailing-underscore motif ("OSS at Nearform_", "Questions_", the "N_" mark).
MARK = "_"


# --------------------------------------------------------------------------
# Stylesheet
# --------------------------------------------------------------------------


def css() -> str:
    """The stylesheet to hand to ``marimo.App(css_file=...)``.

    Components carry their own inline styles, so they render correctly with or
    without this file. What the stylesheet adds is the things inline styles
    cannot reach: full-bleed slide backgrounds (the reveal ``<section>`` sits
    above our markup), the marimo font variables, and quieting marimo's cell
    chrome inside a deck.

    Only ``--marimo-*-font`` is stable public API. The reveal selectors below
    are best-effort and may need a nudge after a marimo upgrade - which is a
    reason to pin marimo for a talk.
    """
    tone_rules = "\n".join(
        f'.reveal .slides > section:has([data-nf-tone="{t.name}"]),\n'
        f'.reveal-viewport:has(.slides > section.present [data-nf-tone="{t.name}"]) {{\n'
        f"  background: {t.bg};\n"
        f"}}"
        for t in TONES.values()
    )
    return f"""\
/* Nearform deck theme - generated by template/theme.py, do not hand-edit.
   Regenerate with: python -m template.theme */

:root {{
  --marimo-text-font: {SANS};
  --marimo-heading-font: {SANS};
  --nf-navy: {NAVY};
  --nf-mint: {MINT};
  --nf-purple: {PURPLE};
  --nf-blue: {BLUE};
  --nf-pale-mint: {PALE_MINT};
}}

/* The deck letterboxes on a projector: reveal keeps 16:9 and leaves bars top
   and bottom. Paint them navy so they read as a frame, not as a bug. */
.reveal-viewport {{
  background: {NAVY};
}}

/* ...and the page behind the deck, but only on a page that is showing one, so
   this never touches marimo's editor chrome. */
body:has(.mo-slide) {{
  background: {NAVY};
}}

/* Full-bleed slide backgrounds. The reveal <section> sits above our markup,
   so a slide's tone has to be set from here to reach the slide's own edges. */
{tone_rules}

/* Let a slide own the whole 960x540 frame: no cell chrome, no gutters. */
.reveal .slides > section:has([data-nf-slide]) .marimo-cell,
.reveal .slides > section:has([data-nf-slide]) .Cell,
.reveal .slides > section:has([data-nf-slide]) .output-area {{
  background: transparent;
  border: none;
  box-shadow: none;
  padding: 0;
  margin: 0;
}}

/* marimo renders markdown output with a max-width; slides want the full deck. */
.reveal .slides > section:has([data-nf-slide]) .markdown {{
  max-width: none;
}}

/* marimo's prose styles size paragraphs and list items themselves, which
   overrides the deck's type scale. Inside a slide, text inherits instead - the
   components' own inline sizes still win, since those are inline styles. */
[data-nf-slide] :is(p, li, ul, ol, span, strong, em, a, blockquote,
                    .markdown, .paragraph) {{
  font-size: inherit;
  line-height: inherit;
}}
[data-nf-slide] :is(p, .paragraph) {{
  margin: 0;
}}

/* Same for colour: prose tints bold text and links for a light page, which
   disappears on navy. Take the slide's own colours instead. */
[data-nf-slide] :is(strong, b, em, i, p, li, span) {{
  color: inherit;
}}
[data-nf-slide] a {{
  color: inherit;
  text-decoration: underline;
  text-underline-offset: 0.15em;
}}

[data-nf-slide] {{
  font-family: {SANS};
  -webkit-font-smoothing: antialiased;
}}

/* Code panel. marimo's syntax colours are tuned for a light background, so a
   code block stays a light card rather than fighting the palette - it reads as
   a deliberate panel on the navy field. */
[data-nf-slide] :is(pre, code) {{
  font-family: {MONO};
  font-size: inherit;
}}
[data-nf-slide] .codehilite {{
  background: {PALE_BLUE};
  border-radius: 1.25cqw;
  padding: 1.5cqw 2cqw;
  overflow-x: auto;
}}
[data-nf-slide] .codehilite pre {{
  background: none;
  margin: 0;
  padding: 0;
}}
"""


CSS_PATH = Path(__file__).with_name("nearform.css")


def write_css(path: str | Path | None = None) -> Path:
    """Write :func:`css` to disk. Defaults to ``template/nearform.css``."""
    target = Path(path) if path is not None else CSS_PATH
    target.write_text(css(), encoding="utf-8")
    return target


if __name__ == "__main__":
    print(f"wrote {write_css()}")
