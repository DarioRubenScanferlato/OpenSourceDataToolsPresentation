"""A D3 "bar chart race": one bar per category, re-ranked and re-scaled
frame by frame with animated transitions, plus play/pause, a scrubber,
hover tooltips and click-to-highlight.

It is the deck's example of a hand-coded JavaScript visualization - the kind
of animation a BI tool can't do - so it uses D3 itself rather than Vega.
D3 is vendored (``template/vendor/``, ISC licence) and inlined into the
widget's module, so the slide works offline. Wrap it with
``mo.ui.anywidget(...)``.
"""

from __future__ import annotations

from pathlib import Path

import anywidget
import traitlets

_VENDOR = Path(__file__).with_name("vendor")

# The vendored file is d3's UMD build: run as part of an ES module it finds no
# `exports`/`define` and attaches itself to `globalThis.d3`.
_D3 = (_VENDOR / "d3.v7.9.0.min.js").read_text(encoding="utf-8")

_ESM = r"""
const d3 = globalThis.d3;

function render({ model, el }) {
  const W = model.get("width"), H = model.get("height");
  const c = model.get("colors");
  const labels = model.get("labels");
  const colors = model.get("plant_colors");
  const dates = model.get("dates");
  const values = model.get("values");     // [frame][category], cumulative
  const steps = model.get("steps");       // [frame][category], this frame's increment
  const unit = model.get("unit");
  const frameMs = model.get("frame_ms");
  const n = labels.length, last = dates.length - 1;
  const M = { top: 66, right: 78, bottom: 8, left: 150 };
  const rowH = (H - M.top - M.bottom) / n;
  // header: title + running total on the left, the current month on the right

  const root = document.createElement("div");
  root.className = "nf-race";
  root.style.cssText = `position:relative;width:${W}px;font-family:inherit;color:${c.fg};user-select:none;`;
  root.innerHTML = `<style>
    .nf-race .tick line { stroke: ${c.rule}; }
    .nf-race .tick text { fill: ${c.muted}; font-size: 12px; }
    .nf-race .domain { display: none; }
    .nf-race button { font: inherit; font-size: 14px; font-weight: 700; color: ${c.bg};
      background: ${c.accent}; border: 0; border-radius: 999px; padding: 6px 16px; cursor: pointer; min-width: 92px; }
    .nf-race input[type=range] { flex: 1; accent-color: ${c.accent}; }
  </style>`;
  el.appendChild(root);

  const svg = d3.select(root).append("svg")
    .attr("width", W).attr("height", H).attr("viewBox", `0 0 ${W} ${H}`)
    .style("display", "block").style("overflow", "visible");

  svg.append("text").attr("x", M.left).attr("y", 16)
    .attr("fill", c.fg).attr("font-size", 16).attr("font-weight", 700).text(model.get("title"));
  const axisG = svg.append("g").attr("transform", `translate(0,${M.top - 8})`);
  const barsG = svg.append("g");
  const dateLabel = svg.append("text")
    .attr("x", W).attr("y", 30).attr("text-anchor", "end")
    .attr("fill", c.fg).attr("font-size", 34).attr("font-weight", 800)
    .style("font-variant-numeric", "tabular-nums");
  const totalLabel = svg.append("text")
    .attr("x", M.left).attr("y", 38)
    .attr("fill", c.muted).attr("font-size", 14).style("font-variant-numeric", "tabular-nums");

  const tip = d3.select(root).append("div").style("position", "absolute").style("pointer-events", "none")
    .style("background", c.panel).style("border", `1px solid ${c.rule}`).style("border-radius", "8px")
    .style("padding", "6px 10px").style("font-size", "13px").style("line-height", "1.4").style("opacity", 0);

  const controls = d3.select(root).append("div")
    .style("display", "flex").style("gap", "14px").style("align-items", "center").style("margin-top", "10px");
  const button = controls.append("button");
  const scrub = controls.append("input").attr("type", "range").attr("min", 0).attr("max", last).attr("step", 1);

  const x = d3.scaleLinear().range([M.left, W - M.right]);
  const fmtDate = d3.utcFormat("%b %Y");
  const parse = d3.utcParse("%Y-%m-%d");
  const fmt = d3.format(",.1f");
  let frame = 0, playing = false, timer = null, selected = null;

  function rows() {
    return barsG.selectAll("g.bar").data(d3.range(n), (p) => p).join((enter) => {
      const g = enter.append("g").attr("class", "bar").style("cursor", "pointer");
      g.append("rect").attr("x", M.left).attr("y", 3).attr("height", rowH - 6).attr("rx", 4)
        .attr("fill", (p) => colors[p]).attr("width", 0);
      g.append("text").attr("class", "name").attr("x", M.left - 10).attr("y", rowH / 2).attr("dy", "0.35em")
        .attr("text-anchor", "end").attr("fill", c.fg).attr("font-size", 14).text((p) => labels[p]);
      g.append("text").attr("class", "val").attr("y", rowH / 2).attr("dy", "0.35em").attr("x", M.left + 6)
        .attr("fill", c.fg).attr("font-size", 13).attr("font-weight", 700).style("font-variant-numeric", "tabular-nums");
      g.on("mousemove", (ev, p) => {
        const [mx, my] = d3.pointer(ev, root);
        tip.style("opacity", 1).style("left", `${mx + 14}px`).style("top", `${my + 10}px`)
          .html(`<b style="color:${colors[p]}">${labels[p]}</b><br>${fmt(values[frame][p])} ${unit} so far` +
                `<br><span style="color:${c.muted}">+${fmt(steps[frame][p] * 1000)} MWh this week</span>`);
      }).on("mouseleave", () => tip.style("opacity", 0))
        .on("click", (ev, p) => { selected = selected === p ? null : p; highlight(); });
      return g;
    });
  }

  function highlight() {
    barsG.selectAll("g.bar").transition().duration(200)
      .attr("opacity", (p) => (selected === null || p === selected ? 1 : 0.25));
  }

  function draw(f, dur) {
    const vals = values[f];
    const order = d3.range(n).sort((a, b) => vals[b] - vals[a]);
    const rank = []; order.forEach((p, r) => (rank[p] = r));
    x.domain([0, Math.max(d3.max(vals) * 1.04, 1e-9)]);
    const t = svg.transition().duration(dur).ease(d3.easeLinear);
    axisG.transition(t).call(d3.axisTop(x).ticks(5).tickSize(-(H - M.top - M.bottom + 4)).tickFormat(d3.format(",~g")));
    const g = rows();
    g.transition(t).attr("transform", (p) => `translate(0,${M.top + rank[p] * rowH})`);
    g.select("rect").transition(t).attr("width", (p) => Math.max(0, x(vals[p]) - M.left));
    g.select("text.val").transition(t).attr("x", (p) => x(vals[p]) + 6)
      .textTween(function (p) {
        const i = d3.interpolateNumber(this.__v ?? 0, vals[p]);
        this.__v = vals[p];
        return (k) => fmt(i(k));
      });
    dateLabel.text(fmtDate(parse(dates[f])));
    totalLabel.text(`total ${fmt(d3.sum(vals))} ${unit}`);
    scrub.property("value", f);
  }

  function setPlaying(on) {
    playing = on;
    clearTimeout(timer);
    button.text(on ? "❚❚ Pause" : frame >= last ? "↺ Replay" : "▶ Play");
    if (on) tick();
  }
  function tick() {
    if (!playing) return;
    if (frame >= last) return setPlaying(false);
    frame += 1;
    draw(frame, frameMs);
    timer = setTimeout(tick, frameMs);
  }

  button.on("click", () => {
    if (playing) return setPlaying(false);
    if (frame >= last) { frame = 0; draw(0, 300); }
    setPlaying(true);
  });
  scrub.on("input", function () { setPlaying(false); frame = +this.value; draw(frame, 120); setPlaying(false); });

  draw(frame, 0);
  setPlaying(false);
  return () => clearTimeout(timer);
}

export default { render };
"""


class BarChartRace(anywidget.AnyWidget):
    """Animated, ranked bars over time.

    ``values[f][p]`` is category ``p``'s running total at frame ``f``
    (``dates[f]``, ISO), ``steps[f][p]`` the increment in that frame - shown
    in the tooltip. ``labels`` and ``plant_colors`` are aligned with the
    categories; ``colors`` is the deck palette (fg, muted, rule, bg, panel,
    accent).
    """

    _esm = _D3 + "\n" + _ESM

    title = traitlets.Unicode("").tag(sync=True)
    labels = traitlets.List(traitlets.Unicode()).tag(sync=True)
    plant_colors = traitlets.List(traitlets.Unicode()).tag(sync=True)
    dates = traitlets.List(traitlets.Unicode()).tag(sync=True)
    values = traitlets.List(traitlets.List(traitlets.Float())).tag(sync=True)
    steps = traitlets.List(traitlets.List(traitlets.Float())).tag(sync=True)
    unit = traitlets.Unicode("").tag(sync=True)
    frame_ms = traitlets.Int(220).tag(sync=True)
    width = traitlets.Int(760).tag(sync=True)
    height = traitlets.Int(360).tag(sync=True)
    colors = traitlets.Dict().tag(sync=True)
