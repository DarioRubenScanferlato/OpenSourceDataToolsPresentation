# Agent instructions

## Slides (`presentation/*.py`, marimo slides layout)

- **Every slide must fit on one screen.** At a 16:9 full-screen size the
  presenter must never have to scroll: if marimo shows its "Scroll for more"
  pill, the slide is too tall. marimo does not shrink slides to fit
  (marimo#10306), so cut content, tighten spacing (`pad_top`, `gap`), make
  code or diagrams smaller, or split the slide into a sub-slide.
- **Check it, don't assume it.** After changing a slide, render the deck
  (`.claude/launch.json` → `os-data-platform-deck`) at a 16:9 viewport such as
  1280x720, go to the slide (`location.hash = "#/<h>/<v>"`) and confirm nothing
  overflows - including slides with clicks (fragments) in their final state.
- **Speaker notes and slide types live in
  `presentation/layouts/<deck>.slides.json`, one entry per cell, by
  position.** When adding, removing or moving cells, keep the entries aligned
  with their cells, or the notes end up on the wrong slides.
- **If the notebook is open in a running marimo session, edit cells through
  that session** (the `marimo-pair` skill), not by writing the `.py` file:
  the session overwrites file edits on its next save.
