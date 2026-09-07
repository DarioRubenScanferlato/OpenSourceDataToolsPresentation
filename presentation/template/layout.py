"""Generate marimo's slides-layout file for a deck.

marimo stores the slides layout next to the notebook as
``layouts/<notebook>.slides.json`` and the notebook points at it with
``marimo.App(layout_file="layouts/<notebook>.slides.json")``. There is no
``marimo run --layout slides`` flag, so this file has to be on disk and in
version control for the deck to open as slides.

You can build the layout by hand in ``marimo edit`` (app-preview dropdown ->
Slides) and marimo will write this file for you. Use this module when you'd
rather keep the deck structure - especially speaker notes - in code, next to
the cells they belong to.

Schema (marimo 0.24):

    {"type": "slides",
     "data": {"cells": [{"type": ..., "speakerNotes": ..., "showCode": ...}],
              "deck": {"transition": ..., "verticalAlign": ...}}}

``cells`` must have one entry per cell in the notebook, in notebook order -
marimo warns and ignores the layout if the counts disagree.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Literal

CellType = Literal["slide", "sub-slide", "fragment", "skip"]
Transition = Literal["none", "fade", "slide", "convex", "concave", "zoom"]
VerticalAlign = Literal["top", "center", "bottom"]

CELL_TYPES = ("slide", "sub-slide", "fragment", "skip")
TRANSITIONS = ("none", "fade", "slide", "convex", "concave", "zoom")
VERTICAL_ALIGNS = ("top", "center", "bottom")


@dataclass
class Cell:
    """One cell's role in the deck.

    Args:
        type: ``slide`` starts a new slide, ``sub-slide`` nests one vertically
            beneath the previous slide, ``fragment`` reveals on the next click
            without advancing, ``skip`` hides the cell (imports, setup, helpers).
        notes: speaker notes, shown in reveal's speaker view (``S``).
        show_code: show this cell's source on the slide. Only has an effect when
            the code reaches the browser - ``marimo edit``, or
            ``marimo run --include-code``.
    """

    type: CellType = "slide"
    notes: str = ""
    show_code: bool = False

    def to_json(self) -> dict[str, object]:
        out: dict[str, object] = {"type": self.type}
        if self.notes:
            out["speakerNotes"] = self.notes
        if self.show_code:
            out["showCode"] = True
        return out


#: Shorthands, so a deck spec reads as a list rather than a wall of constructors.
SLIDE = Cell("slide")
SUB = Cell("sub-slide")
FRAGMENT = Cell("fragment")
SKIP = Cell("skip")


def _coerce(cell: Cell | CellType | str) -> Cell:
    if isinstance(cell, Cell):
        if cell.type not in CELL_TYPES:
            raise ValueError(f"unknown cell type {cell.type!r}; expected one of {CELL_TYPES}")
        return cell
    if cell not in CELL_TYPES:
        raise ValueError(f"unknown cell type {cell!r}; expected one of {CELL_TYPES}")
    return Cell(cell)  # type: ignore[arg-type]


def slides_layout(
    cells: Iterable[Cell | CellType | str],
    transition: Transition = "none",
    vertical_align: VerticalAlign = "top",
) -> dict[str, object]:
    """Build the layout dict.

    ``transition`` and ``vertical_align`` are deck-level only - marimo has no
    per-slide override for either.
    """
    if transition not in TRANSITIONS:
        raise ValueError(f"unknown transition {transition!r}; expected one of {TRANSITIONS}")
    if vertical_align not in VERTICAL_ALIGNS:
        raise ValueError(
            f"unknown vertical_align {vertical_align!r}; expected one of {VERTICAL_ALIGNS}"
        )
    return {
        "type": "slides",
        "data": {
            "cells": [_coerce(c).to_json() for c in cells],
            "deck": {"transition": transition, "verticalAlign": vertical_align},
        },
    }


def write_slides_layout(
    notebook: str | Path,
    cells: Iterable[Cell | CellType | str],
    transition: Transition = "none",
    vertical_align: VerticalAlign = "top",
) -> Path:
    """Write ``layouts/<notebook>.slides.json`` beside ``notebook``.

    Returns the path written. Add the returned relative path to the notebook's
    ``marimo.App(layout_file=...)``.
    """
    nb = Path(notebook)
    target = nb.parent / "layouts" / f"{nb.stem}.slides.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = slides_layout(cells, transition=transition, vertical_align=vertical_align)
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return target
