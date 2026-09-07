"""Slide builders in the Nearform template's visual language.

Every function returns ``mo.Html``, so they compose with each other and with
anything else marimo can render (dataframes, charts, ``mo.ui`` elements):

    import marimo as mo
    from template import nf

    nf.slide(
        nf.stats([("15m+", "Downloads"), ("166+", "Packages")]),
        mo.ui.altair_chart(chart),
        title="Where the data comes from",
        page=4,
    )

The slide archetypes map onto the pptx like this:

    pptx slide 1        -> title_slide()
    pptx slide 2        -> speaker()
    pptx slides 3, 8    -> section() / closing()
    pptx slides 4, 5    -> stats(), quote()
    pptx slides 6, 7    -> metrics(), two_col()
    pptx slide 9        -> section(tone="pale")

Sizes are deck-relative (see ``theme``), so a slide holds the template's
proportions on a laptop, a projector, or in marimo's vertical layout.
``slide()`` establishes the container those units resolve against - build
content inside a ``slide()`` rather than returning it from a cell on its own.
"""

from __future__ import annotations

import html
from typing import Any, Iterable, Sequence

import marimo as mo

from . import theme as t

__all__ = [
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
]

_S = t.SPACE


# --------------------------------------------------------------------------
# internals
# --------------------------------------------------------------------------


def _style(**kw: Any) -> str:
    """``color="red", font_size="2cqw"`` -> ``color:red;font-size:2cqw``."""
    return ";".join(
        f"{k.replace('_', '-')}:{v}" for k, v in kw.items() if v is not None
    )


def _render(obj: Any) -> str:
    """Anything -> an HTML string. Bare strings are treated as markdown."""
    if obj is None:
        return ""
    if isinstance(obj, str):
        return mo.as_html(mo.md(obj)).text
    return mo.as_html(obj).text


def _text(value: str, mark: bool, accent: str) -> str:
    """Escape a heading and optionally append the trailing-underscore motif."""
    out = html.escape(value)
    if mark:
        out += f'<span style="color:{accent}">{t.MARK}</span>'
    return out


def _div(style: str, inner: str) -> str:
    return f'<div style="{style}">{inner}</div>'


# --------------------------------------------------------------------------
# the frame
# --------------------------------------------------------------------------


def slide(
    *content: Any,
    title: str | None = None,
    kicker: str | None = None,
    tone: str = t.DEFAULT_TONE,
    page: int | str | None = None,
    align: str = "top",
    gap: str = _S["gap"],
    mark: bool = True,
) -> mo.Html:
    """The general-purpose content slide.

    Args:
        content: anything renderable; bare strings are markdown.
        title: slide title, at the template's 22pt heading size.
        kicker: small label above the title (the template's "Nearform OSS").
        tone: ``navy`` (default), ``mint``, ``pale`` or ``white``.
        page: slide number, drawn bottom-left after an em dash as in the deck.
        align: ``top`` (default) or ``center``.
        gap: vertical rhythm between blocks, as a CSS length.
        mark: append the accent ``_`` motif to the title.
    """
    tn = t.tone(tone)
    blocks: list[str] = []
    if kicker:
        blocks.append(eyebrow(kicker, tone=tone).text)
    if title:
        blocks.append(heading(title, tone=tone, mark=mark).text)
    blocks.extend(_render(c) for c in content)

    inner = _div(
        _style(display="flex", flex_direction="column", gap=gap), "".join(blocks)
    )
    if page is not None:
        inner += _page_number(page, tn)

    # Two boxes on purpose: the outer one *is* the container that every `cqw`
    # length inside resolves against, and an element's own cqw lengths would
    # resolve against its parent instead - so all the sizing lives on the inner.
    frame = _div(
        _style(
            box_sizing="border-box",
            position="relative",
            min_height=t.SLIDE_MIN_HEIGHT,
            padding=f"{_S['margin_top']} {_S['margin_x']} {_S['margin_bottom']}",
            display="flex",
            flex_direction="column",
            justify_content="center" if align == "center" else "flex-start",
        ),
        inner,
    )
    return mo.Html(
        f'<div data-nf-slide data-nf-tone="{tn.name}" style="{_style(
            box_sizing="border-box",
            container_type="inline-size",
            width="100%",
            background=tn.bg,
            color=tn.fg,
            font_family=t.SANS,
            line_height="1.45",
        )}">{frame}</div>'
    )


def _page_number(page: int | str, tn: t.Tone) -> str:
    return _div(
        _style(
            position="absolute",
            left=_S["margin_x"],
            bottom=_S["margin_bottom"],
            font_size=t.SIZE["small"],
            color=tn.muted,
            letter_spacing="0.04em",
        ),
        f'<span style="color:{tn.accent}">&#8212;</span>&nbsp;&nbsp;{html.escape(str(page))}',
    )


# --------------------------------------------------------------------------
# the named archetypes
# --------------------------------------------------------------------------


def title_slide(
    title: str,
    event: str | None = None,
    author: str | None = None,
    tone: str = "navy",
    mark: bool = False,
) -> mo.Html:
    """The opening slide: mint 56pt title on navy, event and author beneath.

    Mirrors pptx slide 1 ("Making an amazing presentation").
    """
    tn = t.tone(tone)
    meta = ""
    if event:
        meta += _div(
            _style(color=tn.accent, font_size=t.SIZE["lead"]), html.escape(event)
        )
    if author:
        meta += _div(
            _style(color=tn.fg, font_size=t.SIZE["lead"]), html.escape(author)
        )
    if meta:
        meta = _div(_style(margin_top=_S["gap_lg"]), meta)

    heading_html = (
        f'<h1 style="{_style(
            margin="0",
            color=tn.accent,
            font_size=t.SIZE["display"],
            font_weight=t.WEIGHT["light"],
            line_height="1.0",
            letter_spacing="-0.02em",
            max_width="76%",
        )}">{_text(title, mark, tn.fg)}</h1>'
    )
    return slide(mo.Html(heading_html + meta), tone=tone, align="center")


def section(
    title: str,
    kicker: str | None = None,
    tone: str = "mint",
    page: int | str | None = None,
    mark: bool = True,
) -> mo.Html:
    """A section break: navy 38pt title on the mint field (pptx slides 3, 8)."""
    tn = t.tone(tone)
    blocks = ""
    if kicker:
        blocks += eyebrow(kicker, tone=tone).text
    blocks += (
        f'<h2 style="{_style(
            margin="0",
            color=tn.fg,
            font_size=t.SIZE["title"],
            font_weight=t.WEIGHT["light"],
            line_height="1.1",
            letter_spacing="-0.01em",
            max_width="70%",
        )}">{_text(title, mark, tn.accent)}</h2>'
    )
    return slide(mo.Html(blocks), tone=tone, page=page)


def closing(
    title: str = "Questions", tone: str = "mint", page: int | str | None = None
) -> mo.Html:
    """The closing slide. Same frame as :func:`section` (pptx slide 8)."""
    return section(title, tone=tone, page=page)


def speaker(
    name: str,
    role: str,
    handle: str | None = None,
    photo: Any = None,
    note: str | None = None,
    bio: Iterable[str] | None = None,
    links: Sequence[tuple[str, str]] | None = None,
    tone: str = "navy",
    page: int | str | None = None,
    ratio: tuple[int, int] = (3, 2),
) -> mo.Html:
    """The "who is talking" slide (pptx slide 2).

    Args:
        name: your name, at the template's heading size.
        role: the line under it, in the accent colour.
        handle: a single contact line - email, or an @handle.
        photo: anything renderable - ``assets.img(...)``, ``mo.image(...)``,
            or a QR code you generated in an earlier cell.
        note: a small muted aside.
        bio: background lines, rendered as the template's marked list. Markdown
            works. Keep them short - six is about what the slide holds.
        links: ``(label, value)`` pairs on one row at the bottom, e.g.
            ``[("LinkedIn", "dario-scanferlato")]``.
        tone: slide tone.
        page: slide number.
        ratio: text-to-photo column split.
    """
    tn = t.tone(tone)
    left = _div(
        _style(
            font_size=t.SIZE["heading"],
            font_weight=t.WEIGHT["medium"],
            color=tn.fg,
        ),
        html.escape(name),
    ) + _div(
        _style(
            font_size=t.SIZE["subhead"], color=tn.accent, margin_top=_S["tight"]
        ),
        html.escape(role),
    )
    if handle:
        left += _div(
            _style(
                font_size=t.SIZE["body"], color=tn.muted, margin_top=_S["gap"]
            ),
            html.escape(handle),
        )
    if note:
        left += _div(
            _style(
                font_size=t.SIZE["small"],
                color=tn.muted,
                margin_top=_S["gap_sm"],
                max_width="34ch",
            ),
            html.escape(note),
        )
    if bio:
        left += _div(
            _style(margin_top=_S["gap"]),
            bullets(bio, tone=tone, size=t.SIZE["small"]).text,
        )
    if links:
        row = "".join(
            _div(
                _style(color=tn.muted, font_size=t.SIZE["small"]),
                f"{html.escape(label)}: "
                f'<span style="color:{tn.fg}">{html.escape(value)}</span>',
            )
            for label, value in links
        )
        left += _div(
            _style(
                display="flex",
                flex_wrap="wrap",
                gap=f"{_S['gap_sm']} {_S['gap_lg']}",
                margin_top=_S["gap"],
            ),
            row,
        )
    if photo is None:
        return slide(mo.Html(left), tone=tone, page=page, align="center")
    return slide(
        two_col(mo.Html(left), photo, ratio=ratio),
        tone=tone,
        page=page,
        align="center",
    )


# --------------------------------------------------------------------------
# text
# --------------------------------------------------------------------------


def heading(text: str, tone: str = t.DEFAULT_TONE, mark: bool = True) -> mo.Html:
    """A content-slide title (22pt in the template)."""
    tn = t.tone(tone)
    return mo.Html(
        f'<h2 style="{_style(
            margin="0",
            color=tn.fg,
            font_size=t.SIZE["heading"],
            font_weight=t.WEIGHT["medium"],
            line_height="1.2",
            letter_spacing="-0.01em",
        )}">{_text(text, mark, tn.accent)}</h2>'
    )


def eyebrow(text: str, tone: str = t.DEFAULT_TONE) -> mo.Html:
    """The small uppercase label above a title."""
    tn = t.tone(tone)
    return mo.Html(
        _div(
            _style(
                color=tn.accent,
                font_size=t.SIZE["small"],
                font_weight=t.WEIGHT["medium"],
                text_transform="uppercase",
                letter_spacing="0.12em",
                margin_bottom=f"-{_S['gap_sm']}",
            ),
            html.escape(text),
        )
    )


def lead(text: str, tone: str = t.DEFAULT_TONE) -> mo.Html:
    """A single emphasised sentence (15pt)."""
    tn = t.tone(tone)
    return mo.Html(
        f'<p style="{_style(
            margin="0",
            color=tn.fg,
            font_size=t.SIZE["lead"],
            font_weight=t.WEIGHT["light"],
            line_height="1.4",
            max_width="60ch",
        )}">{html.escape(text)}</p>'
    )


def body(text: str, tone: str = t.DEFAULT_TONE) -> mo.Html:
    """Body copy (12pt). Markdown is honoured."""
    tn = t.tone(tone)
    return mo.Html(
        _div(
            _style(color=tn.fg, font_size=t.SIZE["body"], max_width="70ch"),
            _render(text),
        )
    )


def caption(text: str, tone: str = t.DEFAULT_TONE) -> mo.Html:
    """A footnote or source line (8pt, muted)."""
    tn = t.tone(tone)
    return mo.Html(
        _div(
            _style(
                color=tn.muted, font_size=t.SIZE["caption"], line_height="1.5"
            ),
            _render(text),
        )
    )


def bullets(
    items: Iterable[str],
    tone: str = t.DEFAULT_TONE,
    marker: str = t.MARK,
    size: str | None = None,
) -> mo.Html:
    """A list with the template's accent marker instead of a bullet glyph."""
    tn = t.tone(tone)
    rows = "".join(
        f'<li style="{_style(display="flex", gap=_S["gap_sm"], align_items="baseline")}">'
        f'<span style="{_style(color=tn.accent, font_weight=t.WEIGHT["bold"], flex="0 0 auto")}">'
        f"{html.escape(marker)}</span>"
        f'<span style="{_style(color=tn.fg)}">{mo.as_html(mo.md(item)).text}</span>'
        f"</li>"
        for item in items
    )
    return mo.Html(
        f'<ul style="{_style(
            margin="0",
            padding="0",
            list_style="none",
            display="flex",
            flex_direction="column",
            gap=_S["gap_sm"],
            font_size=size or t.SIZE["body"],
            max_width="70ch",
        )}">{rows}</ul>'
    )


# --------------------------------------------------------------------------
# numbers
# --------------------------------------------------------------------------


def stats(
    items: Sequence[tuple[str, str] | tuple[str, str, str]],
    tone: str = t.DEFAULT_TONE,
    columns: int | None = None,
    size: str | None = None,
) -> mo.Html:
    """The big-number row from pptx slides 4 and 5.

    Each item is ``(value, label)`` or ``(value, label, note)`` - e.g.
    ``[("15m+", "Downloads"), ("166+", "Packages", "maintained by us")]``.

    ``size`` overrides the value size, which defaults to the template's 18pt.
    Pass ``theme.pt(40)`` for a single headline number.
    """
    tn = t.tone(tone)
    cells = []
    for item in items:
        value, label, *rest = item
        note = rest[0] if rest else None
        cell = _div(
            _style(
                color=tn.accent,
                font_size=size or t.SIZE["subhead"],
                font_weight=t.WEIGHT["black"],
                line_height="1.1",
            ),
            html.escape(value),
        ) + _div(
            _style(
                color=tn.fg, font_size=t.SIZE["small"], margin_top=_S["tight"]
            ),
            html.escape(label),
        )
        if note:
            cell += _div(
                _style(
                    color=tn.muted,
                    font_size=t.SIZE["caption"],
                    margin_top=_S["tight"],
                ),
                html.escape(note),
            )
        cells.append(_div("", cell))

    n = columns or len(cells) or 1
    return mo.Html(
        _div(
            _style(
                display="grid",
                grid_template_columns=f"repeat({n}, 1fr)",
                gap=_S["gap"],
            ),
            "".join(cells),
        )
    )


def metrics(
    items: Sequence[tuple[str, str]],
    tone: str = t.DEFAULT_TONE,
    columns: int = 2,
) -> mo.Html:
    """The 2x2 metric panel from pptx slides 6 and 7 (value over label, ruled)."""
    tn = t.tone(tone)
    cells = "".join(
        _div(
            _style(border_top=f"1px solid {tn.rule}", padding_top=_S["gap_sm"]),
            _div(
                _style(
                    color=tn.fg,
                    font_size=t.SIZE["subhead"],
                    font_weight=t.WEIGHT["medium"],
                ),
                html.escape(value),
            )
            + _div(
                _style(
                    color=tn.muted,
                    font_size=t.SIZE["small"],
                    margin_top=_S["tight"],
                ),
                html.escape(label),
            ),
        )
        for value, label in items
    )
    return mo.Html(
        _div(
            _style(
                display="grid",
                grid_template_columns=f"repeat({columns}, 1fr)",
                gap=f"{_S['gap']} {_S['gap_lg']}",
            ),
            cells,
        )
    )


def quote(
    text: str,
    author: str | None = None,
    role: str | None = None,
    tone: str = t.DEFAULT_TONE,
) -> mo.Html:
    """A pull quote in Bitter, the template's serif (pptx slides 4, 6, 7)."""
    tn = t.tone(tone)
    out = (
        f'<blockquote style="{_style(
            margin="0",
            font_family=t.SERIF,
            font_size=t.SIZE["heading"],
            font_weight=t.WEIGHT["light"],
            line_height="1.35",
            color=tn.fg,
            max_width="48ch",
        )}">&ldquo;{html.escape(text)}&rdquo;</blockquote>'
    )
    if author:
        attribution = html.escape(author)
        if role:
            attribution += (
                f'<span style="color:{tn.muted}">, {html.escape(role)}</span>'
            )
        out += _div(
            _style(
                margin_top=_S["gap"],
                font_size=t.SIZE["small"],
                color=tn.accent,
            ),
            f"&#8212;&nbsp;{attribution}",
        )
    return mo.Html(_div("", out))


# --------------------------------------------------------------------------
# layout
# --------------------------------------------------------------------------


def cards(
    items: Sequence[tuple[str, str]],
    tone: str = t.DEFAULT_TONE,
    columns: int | None = None,
) -> mo.Html:
    """Tinted blocks of ``(title, body)``. Body text is markdown."""
    tn = t.tone(tone)
    tint = "rgba(255,255,255,0.05)" if tone == "navy" else "rgba(0,14,56,0.05)"
    cells = "".join(
        _div(
            _style(
                background=tint,
                border_radius=_S["radius"],
                padding=f"{_S['gap_sm']} {_S['gap']}",
            ),
            _div(
                _style(
                    color=tn.accent,
                    font_size=t.SIZE["body"],
                    font_weight=t.WEIGHT["bold"],
                    margin_bottom=_S["tight"],
                ),
                html.escape(title),
            )
            + _div(
                _style(
                    color=tn.fg, font_size=t.SIZE["small"], line_height="1.5"
                ),
                mo.as_html(mo.md(text)).text,
            ),
        )
        for title, text in items
    )
    n = columns or min(len(items), 3) or 1
    return mo.Html(
        _div(
            _style(
                display="grid",
                grid_template_columns=f"repeat({n}, 1fr)",
                gap=_S["gap"],
            ),
            cells,
        )
    )


def two_col(
    left: Any,
    right: Any,
    ratio: tuple[int, int] = (1, 1),
    gap: str = _S["gap_lg"],
    align: str = "start",
) -> mo.Html:
    """Two columns. ``ratio=(3, 2)`` gives a 60/40 split."""
    return mo.Html(
        _div(
            _style(
                display="grid",
                grid_template_columns=f"{ratio[0]}fr {ratio[1]}fr",
                gap=gap,
                align_items=align,
            ),
            f"<div>{_render(left)}</div><div>{_render(right)}</div>",
        )
    )


def code(source: str, language: str = "python", tone: str = t.DEFAULT_TONE) -> mo.Html:
    """A syntax-highlighted block sized for the deck.

    This is for code you want to *show*. To show the code of the cell you are
    on, use marimo's own toggle (``C`` in slides mode) instead.
    """
    import textwrap

    tn = t.tone(tone)
    rendered = mo.as_html(
        mo.md(f"```{language}\n{textwrap.dedent(source).strip()}\n```")
    ).text
    return mo.Html(
        _div(
            _style(font_size=t.SIZE["body"], line_height="1.5", color=tn.fg),
            rendered,
        )
    )


def image(src: str, alt: str = "", rounded: bool = True, width: str = "100%") -> mo.Html:
    """An image sized to a column, with the template's rounded frame."""
    return mo.Html(
        f'<img src="{html.escape(src, quote=True)}" alt="{html.escape(alt, quote=True)}" '
        f'style="{_style(
            width=width,
            display="block",
            border_radius=_S["radius"] if rounded else None,
            object_fit="cover",
        )}">'
    )


def logo(tone: str = t.DEFAULT_TONE, size: str | None = None) -> mo.Html:
    """The ``N_`` wordmark, set as type the way the template does it."""
    tn = t.tone(tone)
    return mo.Html(
        f'<span style="{_style(
            font_size=size or t.SIZE["subhead"],
            font_weight=t.WEIGHT["black"],
            color=tn.fg,
            letter_spacing="-0.02em",
        )}">N<span style="color:{tn.accent}">{t.MARK}</span></span>'
    )


def rule(tone: str = t.DEFAULT_TONE) -> mo.Html:
    """A hairline divider."""
    tn = t.tone(tone)
    return mo.Html(
        f'<hr style="{_style(border="none", border_top=f"1px solid {tn.rule}", margin="0")}">'
    )


def spacer(height: str = _S["gap"]) -> mo.Html:
    """Vertical space, as a CSS length."""
    return mo.Html(f'<div style="height:{height}"></div>')
