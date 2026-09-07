"""Images and other files the deck carries with it.

Everything lives in ``presentation/images/`` — headshots, logos, QR codes,
diagrams. Refer to a file by name and nothing has to know an absolute path:

    from template import assets, nf

    nf.speaker(
        name="Dario Scanferlato",
        role="Senior Data Engineer @ Nearform",
        photo=assets.img("profilepic.jpg", rounded=True),
    )

``img()`` goes through ``mo.image``, so marimo serves the bytes itself - the
deck works offline and keeps working after ``marimo export html``.

A missing file renders a labelled placeholder instead of raising, so a deck
under construction still presents. Pass ``strict=True`` to fail loudly instead,
which is what you want in a pre-talk check.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import marimo as mo

from . import theme as t

__all__ = ["images_dir", "path", "img", "exists", "listing"]

IMAGES_DIRNAME = "images"


def images_dir() -> Path:
    """The deck's images folder: ``presentation/images``.

    Resolved from this package's own location rather than the working
    directory, so it is the same folder whether the caller is a notebook, a
    script, or a test - and regardless of where the marimo server was started.
    """
    return Path(__file__).resolve().parent.parent / IMAGES_DIRNAME


#: Tried in order when a name's own extension doesn't match a file on disk.
IMAGE_SUFFIXES = (".svg", ".png", ".webp", ".jpg", ".jpeg", ".gif", ".avif")


def path(name: str | Path) -> Path:
    """Absolute path to an asset.

    Forgiving about how the name is written, because all of these mean the same
    file and it isn't worth remembering which one is "right":

        "profilepic.jpg"
        "images/profilepic.jpg"
        "presentation/images/profilepic.jpg"
        "/absolute/path/to/profilepic.jpg"

    The extension is a hint, not a requirement: ask for ``logos/powerbi.png``
    and you get ``logos/powerbi.svg`` if that is what's on disk. A logo you
    find as an SVG and one you find as a PNG shouldn't need a code change.

    Returns the name as given (resolved into the images folder) when nothing
    matches, so callers can report a path the reader recognises.
    """
    candidate = Path(name)
    if not candidate.is_absolute():
        parts = candidate.parts
        # Drop a leading path that just restates where the images folder is.
        for prefix in (("presentation", IMAGES_DIRNAME), (IMAGES_DIRNAME,)):
            if parts[: len(prefix)] == prefix:
                parts = parts[len(prefix) :]
                break
        candidate = images_dir().joinpath(*parts) if parts else images_dir()

    if candidate.is_file():
        return candidate
    for suffix in IMAGE_SUFFIXES:
        alternative = candidate.with_suffix(suffix)
        if alternative.is_file():
            return alternative
    return candidate


def exists(name: str | Path) -> bool:
    """Whether ``images/<name>`` is on disk."""
    return path(name).is_file()


def listing() -> list[str]:
    """Every file in the images folder, sorted - handy when a name is wrong."""
    directory = images_dir()
    if not directory.is_dir():
        return []
    return sorted(p.name for p in directory.iterdir() if p.is_file() and not p.name.startswith("."))


def img(
    name: str | Path,
    width: str = "100%",
    rounded: bool = True,
    alt: str = "",
    strict: bool = False,
    **kwargs: Any,
) -> mo.Html:
    """Render ``images/<name>``.

    Args:
        name: file name inside ``presentation/images/`` (see :func:`path`
            for the spellings it accepts).
        width: any CSS length; the deck's units work here too.
        rounded: apply the template's corner radius.
        alt: alt text.
        strict: raise ``FileNotFoundError`` if the file is missing, instead of
            rendering a placeholder.
        kwargs: passed through to ``mo.image``.
    """
    target = path(name)
    if not target.is_file():
        if strict:
            available = ", ".join(listing()) or "(the folder is empty)"
            raise FileNotFoundError(
                f"{target} not found. Files in {images_dir()}: {available}"
            )
        return placeholder(name, width=width)

    # mo.image's own `rounded` is a fixed 4px; use the template's radius instead.
    # Its `style` is a dict of CSS properties, not a style string.
    css: dict[str, str] = {"display": "block", "object-fit": "cover"}
    if rounded:
        css["border-radius"] = t.SPACE["radius"]
    css.update(kwargs.pop("style", None) or {})
    return mo.image(
        src=target,
        alt=alt or target.name,
        width=width,
        rounded=False,
        style=css,
        **kwargs,
    )


def placeholder(name: str, width: str = "100%", tone: str = t.DEFAULT_TONE) -> mo.Html:
    """A labelled box standing in for an image that isn't there yet."""
    tn = t.tone(tone)
    # One child element, not bare text nodes: the box is a flex container, and
    # loose text runs would each become their own flex item and spread apart.
    return mo.Html(
        f'<div style="width:{width};aspect-ratio:1;display:flex;align-items:center;'
        f"justify-content:center;box-sizing:border-box;"
        f"padding:{t.SPACE['gap']};border:1px dashed {tn.accent};"
        f"border-radius:{t.SPACE['radius']};color:{tn.muted};"
        f'font-size:{t.SIZE["small"]};line-height:1.5">'
        f'<span style="text-align:center">drop '
        f'<strong style="color:{tn.accent}">{name}</strong><br>'
        f"into presentation/images/</span></div>"
    )
