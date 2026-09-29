"""A date-range "timeline slider": a thin strip showing a daily series (so
you can see where there's data), with a highlighted range and two handles
you drag independently to set its start and end. Dragging inside the range
moves both at once.

marimo's own range slider is numeric-only (no date labels), and a
Vega-Lite interval brush can only be redrawn or moved as a whole - so this
is a small anywidget instead. Wrap it with `mo.ui.anywidget(...)`; its
`.value` is `{"start": "YYYY-MM-DD", "end": "YYYY-MM-DD", ...}` and only
changes when a drag ends, so dependent cells don't re-run mid-drag.
"""

from __future__ import annotations

import anywidget
import traitlets

_ESM = r"""
const DAY = 86400000;
const toMs = (iso) => Date.parse(iso + "T00:00:00Z");
const toIso = (ms) => new Date(ms).toISOString().slice(0, 10);
const fmt = (ms) => new Date(ms).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric", timeZone: "UTC" });
const NS = "http://www.w3.org/2000/svg";
const svgEl = (tag, attrs) => {
  const e = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
  return e;
};

function render({ model, el }) {
  const W = model.get("width"), c = model.get("colors");
  const LABEL_H = 18, STRIP_H = 22, AXIS_H = 16, H = LABEL_H + STRIP_H + AXIS_H;
  const lo = toMs(model.get("min_date")), hi = toMs(model.get("max_date"));
  const values = model.get("values");
  const x = (ms) => ((ms - lo) / (hi - lo)) * W;
  const msAt = (px) => Math.round((lo + (px / W) * (hi - lo)) / DAY) * DAY;

  const svg = svgEl("svg", { width: W, height: H, viewBox: `0 0 ${W} ${H}` });
  svg.style.display = "block";
  svg.style.overflow = "visible";
  svg.style.userSelect = "none";
  svg.style.fontFamily = "inherit";

  // header row: label left, the selected range right
  const label = svgEl("text", { x: 0, y: 13, fill: c.muted, "font-size": 13 });
  label.textContent = model.get("label");
  const readout = svgEl("text", { x: W, y: 13, fill: c.fg, "font-size": 13, "text-anchor": "end", "font-weight": 600 });
  svg.append(label, readout);

  // strip: frame + the daily series as an area
  const top = LABEL_H;
  svg.append(svgEl("rect", { x: 0, y: top, width: W, height: STRIP_H, fill: "none", stroke: c.rule, rx: 3 }));
  const vmax = Math.max(...values, 1);
  let d = `M0,${top + STRIP_H}`;
  values.forEach((v, i) => {
    const px = (i / Math.max(values.length - 1, 1)) * W;
    d += ` L${px.toFixed(1)},${(top + STRIP_H - (v / vmax) * (STRIP_H - 3)).toFixed(1)}`;
  });
  d += ` L${W},${top + STRIP_H} Z`;
  svg.append(svgEl("path", { d, fill: c.accent, opacity: 0.35 }));

  // month ticks along the bottom, labelled every quarter
  const first = new Date(lo);
  for (let m = new Date(Date.UTC(first.getUTCFullYear(), first.getUTCMonth() + 1, 1)); m.getTime() <= hi; m.setUTCMonth(m.getUTCMonth() + 1)) {
    const px = x(m.getTime());
    const quarter = m.getUTCMonth() % 3 === 0;
    svg.append(svgEl("line", { x1: px, x2: px, y1: top + STRIP_H, y2: top + STRIP_H + (quarter ? 5 : 3), stroke: c.rule }));
    if (quarter) {
      const t = svgEl("text", { x: px, y: H - 1, fill: c.muted, "font-size": 11, "text-anchor": "middle" });
      t.textContent = m.toLocaleDateString("en-GB", { month: "short", year: "numeric", timeZone: "UTC" });
      svg.append(t);
    }
  }

  // the selected range and its two handles
  const range = svgEl("rect", { y: top, height: STRIP_H, fill: c.accent, "fill-opacity": 0.2, stroke: c.accent, "stroke-width": 1 });
  range.style.cursor = "grab";
  const handle = () => {
    const g = svgEl("g", {});
    g.append(svgEl("line", { y1: top - 2, y2: top + STRIP_H + 2, stroke: c.accent, "stroke-width": 2 }));
    g.append(svgEl("rect", { x: -5, y: top + STRIP_H / 2 - 9, width: 10, height: 18, rx: 3, fill: c.accent, stroke: c.bg, "stroke-width": 1.5 }));
    // a wider invisible grab area than the handle itself
    g.append(svgEl("rect", { x: -9, y: top - 4, width: 18, height: STRIP_H + 8, fill: "transparent" }));
    g.style.cursor = "ew-resize";
    return g;
  };
  const hStart = handle(), hEnd = handle();
  svg.append(range, hStart, hEnd);

  let start = toMs(model.get("start")), end = toMs(model.get("end"));
  const draw = () => {
    range.setAttribute("x", x(start));
    range.setAttribute("width", Math.max(x(end) - x(start), 1));
    hStart.setAttribute("transform", `translate(${x(start)},0)`);
    hEnd.setAttribute("transform", `translate(${x(end)},0)`);
    readout.textContent = `${fmt(start)} – ${fmt(end)}  ·  ${Math.round((end - start) / DAY) + 1} days`;
  };
  draw();

  // Pointer position in the SVG's own units - correct even when the page
  // scales it (CSS zoom/transform), since it's measured against the
  // rendered box.
  const pointerPx = (ev) => {
    const r = svg.getBoundingClientRect();
    return ((ev.clientX - r.left) / r.width) * W;
  };
  const drag = (kind) => (ev) => {
    ev.preventDefault();
    ev.stopPropagation();
    const grabbed = msAt(pointerPx(ev)), s0 = start, e0 = end;
    const move = (mv) => {
      const at = Math.min(Math.max(msAt(pointerPx(mv)), lo), hi);
      if (kind === "start") start = Math.min(at, end);
      else if (kind === "end") end = Math.max(at, start);
      else {
        const shift = Math.min(Math.max(at - grabbed, lo - s0), hi - e0);
        start = s0 + shift;
        end = e0 + shift;
      }
      draw();
    };
    const up = () => {
      window.removeEventListener("pointermove", move);
      window.removeEventListener("pointerup", up);
      model.set("start", toIso(start));
      model.set("end", toIso(end));
      model.save_changes();
    };
    window.addEventListener("pointermove", move);
    window.addEventListener("pointerup", up);
  };
  hStart.addEventListener("pointerdown", drag("start"));
  hEnd.addEventListener("pointerdown", drag("end"));
  range.addEventListener("pointerdown", drag("both"));

  model.on("change:start", () => { start = toMs(model.get("start")); draw(); });
  model.on("change:end", () => { end = toMs(model.get("end")); draw(); });
  el.append(svg);
}
export default { render };
"""


class DateRangeTimeline(anywidget.AnyWidget):
    """See the module docstring. `values` is one number per day from
    `min_date` to `max_date` (e.g. daily energy), drawn as the strip's area."""

    _esm = _ESM
    start = traitlets.Unicode().tag(sync=True)
    end = traitlets.Unicode().tag(sync=True)
    min_date = traitlets.Unicode().tag(sync=True)
    max_date = traitlets.Unicode().tag(sync=True)
    values = traitlets.List(traitlets.Float()).tag(sync=True)
    width = traitlets.Int(750).tag(sync=True)
    label = traitlets.Unicode("Period").tag(sync=True)
    colors = traitlets.Dict().tag(sync=True)
