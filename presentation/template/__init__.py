"""Nearform-branded helpers for building the talk as a marimo notebook.

Derived from ``presentation/OS at Nearform Event Speaker Template.pptx``.

Typical use, from a notebook in ``presentation/``:

    import marimo as mo
    from template import nf, theme

    app = marimo.App(css_file="template/nearform.css",
                     layout_file="layouts/deck.slides.json")

    nf.title_slide("Building an open-source data platform",
                   event="Open Source Summit - 2026",
                   author="Dario Scanferlato")

``nf`` is the component namespace; ``theme`` holds the colours, fonts and
sizes if you need to style something the components don't cover.
"""

from . import assets
from . import components as nf
from . import theme
from .components import (
    body,
    bullets,
    caption,
    cards,
    closing,
    code,
    eyebrow,
    heading,
    image,
    lead,
    logo,
    metrics,
    quote,
    rule,
    section,
    slide,
    spacer,
    speaker,
    stats,
    title_slide,
    two_col,
)
from .layout import (
    FRAGMENT,
    SKIP,
    SLIDE,
    SUB,
    Cell,
    slides_layout,
    write_slides_layout,
)
from .theme import (
    ACCENTS,
    BLUE,
    LAVENDER,
    MINT,
    NAVY,
    PALE_BLUE,
    PALE_MINT,
    PURPLE,
    SLATE,
    TONES,
    WHITE,
)

__all__ = [
    "nf",
    "theme",
    "assets",
    # components
    "slide",
    "title_slide",
    "section",
    "closing",
    "speaker",
    "heading",
    "eyebrow",
    "lead",
    "body",
    "caption",
    "bullets",
    "stats",
    "metrics",
    "quote",
    "cards",
    "two_col",
    "code",
    "image",
    "logo",
    "rule",
    "spacer",
    # layout
    "Cell",
    "SLIDE",
    "SUB",
    "FRAGMENT",
    "SKIP",
    "slides_layout",
    "write_slides_layout",
    # palette
    "NAVY",
    "MINT",
    "PURPLE",
    "BLUE",
    "LAVENDER",
    "PALE_BLUE",
    "PALE_MINT",
    "SLATE",
    "WHITE",
    "ACCENTS",
    "TONES",
]
