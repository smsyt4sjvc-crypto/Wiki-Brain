#!/usr/bin/env python3
"""Chips vs credit — one static page: is AI chip demand flattening, and is financing
stress rising for the two kinds of AI borrower (cash-flow giants vs debt-funded)?

    python3 tools/chips_credit_html.py        # -> docs/chips-credit.html

Inputs (all in the repo, numbers baked in at build time — the page does not refresh):
  data/chips/tsmc_monthly_revenue.csv          TSMC monthly revenue, SEC 6-K
  data/fragility/series/{ccc_oas,ig_oas}.csv   ICE BofA option-adjusted spreads (percent)
  data/chips/fred/*.csv                        FRED: DGS10, IG/CCC effective yields
  data/fragility/cds_panel.csv                 ICE Clear Credit 5Y CDS (model spreads)
Refresh: re-pull FRED into data/chips/fred/, add TSMC months, run icc_cds.py, re-run.
"""
import csv, json, os, statistics as st, datetime as dt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *a: os.path.join(ROOT, *a)
IPO = "2025-03-28"          # CoreWeave IPO = the start of the window
MID = "2026-06-30"
CF4 = ["GOOGL", "AMZN", "MSFT", "META"]


def series(path):
    out = {}
    with open(path) as f:
        for r in csv.reader(f):
            try:
                out[r[0]] = float(r[1])
            except (ValueError, IndexError):
                pass
    return out


def last_on_or_before(d, day):
    ks = [k for k in d if k <= day]
    return d[max(ks)] if ks else None


def mavg(d, month):
    v = [x for k, x in d.items() if k.startswith(month)]
    return st.mean(v) if v else None


def corr(a, b):
    ma, mb = st.mean(a), st.mean(b)
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    den = (sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b)) ** .5
    return num / den if den else 0.0


def daily_corr(spr, rate, start):
    days = sorted(k for k in spr if k >= start and k in rate)
    da, db = [], []
    for p, q in zip(days, days[1:]):
        da.append(spr[q] - spr[p]); db.append(rate[q] - rate[p])
    return corr(da, db), len(da)


# ---------------------------------------------------------------- data
ts = {r["month"]: float(r["revenue_ntd_bn"]) for r in csv.DictReader(open(P("data/chips/tsmc_monthly_revenue.csv")))}
ccc = series(P("data/fragility/series/ccc_oas.csv"))
ig = series(P("data/fragility/series/ig_oas.csv"))
y10 = series(P("data/chips/fred/DGS10.csv"))
igey = series(P("data/chips/fred/BAMLC0A0CMEY.csv"))
cccey = series(P("data/chips/fred/BAMLH0A3HYCEY.csv"))

months = sorted(ts)
base_t = sum(ts[m] for m in ("2025-01", "2025-02", "2025-03")) / 3
base_c, base_i = mavg(ccc, "2025-03"), mavg(ig, "2025-03")


def month_end(m):
    y, mo = map(int, m.split("-"))
    nxt = dt.date(y + (mo == 12), mo % 12 + 1, 1)
    return (nxt - dt.timedelta(days=1)).isoformat()


demand = []      # 3-month average revenue, indexed, placed at month end
for i, m in enumerate(months):
    if m < "2025-03":
        continue
    t3 = sum(ts[x] for x in months[i - 2:i + 1]) / 3
    demand.append([month_end(m), round(100 * t3 / base_t, 1), round(t3, 1)])
cccx = [[d, round(100 * v / base_c, 1), round(v * 100)] for d, v in sorted(ccc.items()) if d >= "2025-03-01"]
igx = [[d, round(100 * v / base_i, 1), round(v * 100)] for d, v in sorted(ig.items()) if d >= "2025-03-01"]

bars = []
for m in months:
    if m < "2025-03":
        continue
    y, mo = m.split("-")
    prev_m = months[months.index(m) - 1]
    yy = f"{int(y) - 1}-{mo}"
    bars.append({"m": m, "v": ts[m],
                 "mm": round(100 * (ts[m] / ts[prev_m] - 1), 1),
                 "yy": round(100 * (ts[m] / ts[yy] - 1), 1) if yy in ts else None})


def qsum(y, q):
    return sum(ts[f"{y}-{3 * (q - 1) + k:02d}"] for k in (1, 2, 3))


quarters = [{"q": f"Q{q}'26", "yy": round(100 * (qsum(2026, q) / qsum(2025, q) - 1), 1),
             "months": [f"2026-{3 * (q - 1) + k:02d}" for k in (1, 2, 3)]} for q in (1, 2, 3)]

# decomposition: change in all-in yield = Treasury part (yield - spread) + spread part
last_c = max(ccc)
decomp = []
for tier, ey, oas in (("Cash-flow tier · investment-grade index", igey, ig),
                      ("Debt-funded tier · CCC junk index", cccey, ccc)):
    for lab, start in (("since the IPO, 3/28/25", IPO), ("since 6/30/26", MID)):
        dy = last_on_or_before(ey, last_c) - last_on_or_before(ey, start)
        ds = last_on_or_before(oas, last_c) - last_on_or_before(oas, start)
        decomp.append({"tier": tier, "win": lab, "total": round(dy, 2),
                       "spread": round(ds, 2), "rates": round(dy - ds, 2),
                       "key": "s3" if "Cash" in tier else "s2"})

# CDS: one contract (Dec-2031) from 9/28, indexed
cds = {}
with open(P("data/fragility/cds_panel.csv")) as f:
    for r in csv.DictReader(f):
        if r["maturity"] == "2031-12-20" and r["date"] >= "2026-09-28":
            cds.setdefault(r["date"], {})[r["ticker"]] = float(r["spread_bp"])
cds_days = sorted(d for d in cds if all(t in cds[d] for t in CF4 + ["CRWV", "ORCL"]))
d0 = cds_days[0]
cf_avg = {d: st.mean(cds[d][t] for t in CF4) for d in cds_days}
cds_series = {
    "CRWV": [[d, round(100 * cds[d]["CRWV"] / cds[d0]["CRWV"], 1), round(cds[d]["CRWV"], 1)] for d in cds_days],
    "ORCL": [[d, round(100 * cds[d]["ORCL"] / cds[d0]["ORCL"], 1), round(cds[d]["ORCL"], 1)] for d in cds_days],
    "CF": [[d, round(100 * cf_avg[d] / cf_avg[d0], 1), round(cf_avg[d], 1)] for d in cds_days],
}
d1 = cds_days[-1]
gap0, gap1 = cds[d0]["CRWV"] - cf_avg[d0], cds[d1]["CRWV"] - cf_avg[d1]

rc_ipo, n_ipo = daily_corr(ccc, y10, IPO)
rc_aug, n_aug = daily_corr(ccc, y10, "2026-08-01")
ri_ipo, _ = daily_corr(ig, y10, IPO)

dem_last = demand[-1][1]
ccc_last_x = round(100 * ccc[last_c] / base_c, 1)
ccc_sep = round(100 * mavg(ccc, "2026-09") / base_c, 1)
gap_sep = round(demand[-1][1] - ccc_sep, 1)
gap_now = round(dem_last - ccc_last_x, 1)

DATA = {"demand": demand, "ccc": cccx, "ig": igx, "bars": bars, "quarters": quarters,
        "decomp": decomp, "cds": cds_series}

ckeys = ["2026-09-30", last_c]
F = {
    "q3": quarters[2]["yy"], "q2": quarters[1]["yy"], "q1": quarters[0]["yy"],
    "sep_mm": bars[-1]["mm"], "dem_last": dem_last, "ccc_sep": ccc_sep, "ccc_now": ccc_last_x,
    "gap_sep": gap_sep, "gap_now": gap_now,
    "ccc_930": ccc["2026-09-30"], "ccc_last": ccc[last_c], "last_c": last_c,
    "y10_930": y10["2026-09-30"], "y10_last": last_on_or_before(y10, last_c),
    "y10_lastd": max(k for k in y10 if k <= last_c),
    "crwv0": cds[d0]["CRWV"], "crwv1": cds[d1]["CRWV"], "orcl0": cds[d0]["ORCL"], "orcl1": cds[d1]["ORCL"],
    "cf0": cf_avg[d0], "cf1": cf_avg[d1], "gap0": gap0, "gap1": gap1, "d0": d0, "d1": d1,
    "rc_ipo": rc_ipo, "rc_aug": rc_aug, "ri_ipo": ri_ipo, "n_ipo": n_ipo, "n_aug": n_aug,
}
igI, igM, ccI, ccM = decomp      # order: IG since IPO, IG since 6/30, CCC since IPO, CCC since 6/30
F["ccc_sep_bp"] = round(mavg(ccc, "2026-09") * 100)


def pct(part, whole):
    return round(100 * part / whole) if whole else 0


def d_us(iso):
    y, m, d = iso.split("-")
    return f"{int(m)}/{int(d)}"


# ---------------------------------------------------------------- page
CSS = """
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Serif:wght@400;500&display=swap');
:root{
  --ground:#f4f6f7; --card:#ffffff; --card-2:#f7f9fa;
  --line:#e2e6ea; --line-soft:#eef1f4;
  --ink:#101418; --ink-2:#4a5560; --ink-3:#6f7c88; --ink-faint:#9aa5b1;
  --accent:#2f5d8c; --pos:#0f7a3d; --neg:#b3261e;
  --s1:#2a78d6; --s2:#eb6834; --s3:#1baf7a; --s4:#eda100;
  --shadow:0 1px 2px rgba(16,20,24,.05), 0 8px 24px -14px rgba(16,20,24,.16);
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    color-scheme:dark;
    --ground:#0e1216; --card:#161b21; --card-2:#1b2129;
    --line:#252c34; --line-soft:#1e242b;
    --ink:#eef2f5; --ink-2:#a7b3bf; --ink-3:#7d8b98; --ink-faint:#5b6873;
    --accent:#7aa8d8; --pos:#5cc98a; --neg:#f2857c;
    --s1:#3987e5; --s2:#d95926; --s3:#199e70; --s4:#c98500;
    --shadow:0 1px 2px rgba(0,0,0,.42), 0 8px 24px -14px rgba(0,0,0,.7);
  }
}
:root[data-theme="dark"]{
  color-scheme:dark;
  --ground:#0e1216; --card:#161b21; --card-2:#1b2129;
  --line:#252c34; --line-soft:#1e242b;
  --ink:#eef2f5; --ink-2:#a7b3bf; --ink-3:#7d8b98; --ink-faint:#5b6873;
  --accent:#7aa8d8; --pos:#5cc98a; --neg:#f2857c;
  --s1:#3987e5; --s2:#d95926; --s3:#199e70; --s4:#c98500;
  --shadow:0 1px 2px rgba(0,0,0,.42), 0 8px 24px -14px rgba(0,0,0,.7);
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--ground);color:var(--ink);
  font-family:"IBM Plex Sans",ui-sans-serif,-apple-system,"Segoe UI",Roboto,sans-serif;
  font-size:14px;line-height:1.5}
.wrap{max-width:980px;margin:0 auto;padding-block:30px 72px;
  padding-left:max(16px, env(safe-area-inset-left, 0px));
  padding-right:max(16px, env(safe-area-inset-right, 0px));
  display:flex;flex-direction:column;gap:18px}
.mono{font-family:"IBM Plex Mono",ui-monospace,monospace}
.eyebrow{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:10.5px;
  letter-spacing:.16em;text-transform:uppercase;color:var(--ink-3)}
h1{font-size:25px;line-height:1.18;margin:4px 0 6px;letter-spacing:-.018em;font-weight:600;text-wrap:balance}
.meta{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:11.5px;color:var(--ink-3)}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;
  padding:20px 22px;box-shadow:var(--shadow);min-width:0}
h2{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:10.5px;text-transform:uppercase;
  letter-spacing:.14em;color:var(--ink-3);margin:0 0 6px;font-weight:500}
h3{font-size:16.5px;line-height:1.3;margin:0 0 12px;font-weight:600;text-wrap:balance}
.lede{font-family:"IBM Plex Serif",Georgia,serif;font-size:19px;line-height:1.36;font-weight:500;
  margin:0;text-wrap:balance}
.qa{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}
.q{border-top:2px solid var(--line);padding-top:12px;min-width:0}
.q .ask{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:10.5px;letter-spacing:.08em;
  text-transform:uppercase;color:var(--ink-3)}
.q .ans{font-size:20px;font-weight:600;margin:4px 0 6px;letter-spacing:-.01em}
.q p{margin:0;color:var(--ink-2);font-size:13px;line-height:1.58}
.money{display:flex;flex-direction:column;gap:10px;margin:0;padding:0;list-style:none}
.money li{display:grid;grid-template-columns:150px minmax(0,1fr);gap:14px;padding:10px 0;
  border-bottom:1px solid var(--line-soft)}
.money li:last-child{border-bottom:0}
.money b{font-size:13px}
.money span{color:var(--ink-2);font-size:13px;line-height:1.58}
.note{color:var(--ink-2);font-size:12.5px;line-height:1.6;margin:10px 0 0;max-width:78ch}
.legend{display:flex;flex-wrap:wrap;gap:6px 16px;margin:2px 0 8px;font-size:12px;color:var(--ink-2)}
.legend i{display:inline-block;width:14px;height:3px;border-radius:2px;vertical-align:middle;margin-right:6px}
.legend i.pale{opacity:.4;height:8px}
.legend i.solid{height:8px}
.chart{position:relative;width:100%}
.chart svg{display:block;width:100%;overflow:visible}
.chart text{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:10.5px;fill:var(--ink-3)}
.chart text.lab{font-family:"IBM Plex Sans",ui-sans-serif,sans-serif;font-size:11.5px;fill:var(--ink-2);font-weight:500}
.chart text.val{fill:var(--ink);font-weight:600}
.tip{position:absolute;pointer-events:none;background:var(--card);border:1px solid var(--line);
  border-radius:8px;box-shadow:var(--shadow);padding:8px 10px;font-size:12px;line-height:1.45;
  color:var(--ink);min-width:150px;z-index:2}
.tip .h{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:10.5px;color:var(--ink-3);margin-bottom:3px}
.tip .r{display:flex;align-items:center;gap:7px;white-space:nowrap}
.tip .r i{width:8px;height:8px;border-radius:50%;flex:none}
.tip .r b{margin-left:auto;padding-left:10px;font-family:"IBM Plex Mono",ui-monospace,monospace;font-weight:500}
.dc{display:flex;flex-direction:column;gap:14px;margin-top:6px}
.dc .row{display:flex;flex-direction:column;gap:5px}
.dc .rl{display:flex;justify-content:space-between;gap:10px;font-size:12.5px;color:var(--ink-2)}
.dc .rl b{white-space:nowrap;color:var(--ink);font-family:"IBM Plex Mono",ui-monospace,monospace;font-weight:600}
.dc .trk{position:relative;height:18px}
.dc .seg{position:absolute;top:0;height:18px;border-radius:2px}
.dc .zero{position:absolute;top:-4px;bottom:-4px;width:1px;background:var(--ink-faint)}
.dc .sub{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:11px;color:var(--ink-3)}
details{margin-top:10px}
summary{cursor:pointer;font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:11px;color:var(--accent)}
.tw{overflow-x:auto;margin-top:8px}
table{border-collapse:collapse;font-size:12px;width:100%}
th,td{text-align:right;padding:6px 8px;border-bottom:1px solid var(--line-soft);white-space:nowrap;
  font-variant-numeric:tabular-nums}
th:first-child,td:first-child{text-align:left}
thead th{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:10px;font-weight:500;
  color:var(--ink-3);text-transform:uppercase;letter-spacing:.06em}
ul.cav{margin:0;padding-left:18px;color:var(--ink-2);font-size:12.5px;line-height:1.6}
ul.cav li{margin:4px 0}
.src{font-size:11.5px;color:var(--ink-3);line-height:1.6}
a{color:var(--accent)}
@media (max-width:760px){
  .qa{grid-template-columns:minmax(0,1fr)}
  .money li{grid-template-columns:minmax(0,1fr);gap:2px}
  .card{padding:16px 15px}
  h1{font-size:22px}
}
"""

JS = r"""
const D = JSON.parse(document.getElementById('d').textContent);
const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const NS = 'http://www.w3.org/2000/svg';
const T = s => Date.parse(s + 'T12:00:00Z');
const MON = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
const fmtD = s => { const [y,m,d] = s.split('-'); return MON[+m-1] + ' ' + (+d) + ', ' + y; };
const fmtM = s => { const [y,m] = s.split('-'); return MON[+m-1] + ' ' + y; };
function el(tag, at, parent){ const e = document.createElementNS(NS, tag);
  for (const k in at) e.setAttribute(k, at[k]); if (parent) parent.appendChild(e); return e; }
function nice(lo, hi, n){ const span = hi - lo, step0 = span / n, p = Math.pow(10, Math.floor(Math.log10(step0)));
  const step = [1,2,2.5,5,10].map(k => k*p).find(s => s >= step0);
  const a = Math.floor(lo/step)*step, b = Math.ceil(hi/step)*step, t = [];
  for (let v = a; v <= b + 1e-9; v += step) t.push(+v.toFixed(6)); return t; }
function tipAt(box, tip, x, y){ const w = box.clientWidth, tw = tip.offsetWidth;
  let left = x + 14; if (left + tw > w) left = Math.max(0, x - tw - 14);
  tip.style.left = left + 'px'; tip.style.top = Math.max(0, y - 10) + 'px'; }

function lineChart(id, cfg){
  const box = document.getElementById(id); box.innerHTML = '';
  const W = box.clientWidth, H = W < 520 ? 230 : 280;
  const m = {l: 34, r: W < 520 ? 92 : 132, t: 10, b: 24};
  const svg = el('svg', {viewBox: `0 0 ${W} ${H}`, height: H, role: 'img', 'aria-label': cfg.aria}, box);
  const all = cfg.series.flatMap(s => s.pts);
  const x0 = Math.min(...all.map(p => T(p[0]))), x1 = Math.max(...all.map(p => T(p[0])));
  const ys = all.map(p => p[1]).concat(cfg.base != null ? [cfg.base] : []);
  const ticks = nice(Math.min(...ys), Math.max(...ys), 4);
  const y0 = ticks[0], y1 = ticks[ticks.length-1];
  const X = t => m.l + (t - x0) / (x1 - x0) * (W - m.l - m.r);
  const Y = v => m.t + (1 - (v - y0) / (y1 - y0)) * (H - m.t - m.b);
  ticks.forEach(v => { el('line', {x1: m.l, x2: W - m.r, y1: Y(v), y2: Y(v), stroke: css('--line-soft'), 'stroke-width': 1}, svg);
    const t = el('text', {x: m.l - 6, y: Y(v) + 3.5, 'text-anchor': 'end'}, svg); t.textContent = v; });
  if (cfg.base != null) el('line', {x1: m.l, x2: W - m.r, y1: Y(cfg.base), y2: Y(cfg.base), stroke: css('--ink-faint'), 'stroke-dasharray': '3 3', 'stroke-width': 1}, svg);
  // x ticks
  cfg.xticks.forEach(s => { const x = X(T(s)); const t = el('text', {x, y: H - 6, 'text-anchor': 'middle'}, svg);
    t.textContent = cfg.xfmt(s); el('line', {x1: x, x2: x, y1: H - m.b, y2: H - m.b + 4, stroke: css('--line'), 'stroke-width': 1}, svg); });
  el('line', {x1: m.l, x2: W - m.r, y1: H - m.b, y2: H - m.b, stroke: css('--line'), 'stroke-width': 1}, svg);
  const surf = css('--card');
  cfg.series.forEach(s => {
    const d = s.pts.map((p, i) => (i ? 'L' : 'M') + X(T(p[0])).toFixed(1) + ' ' + Y(p[1]).toFixed(1)).join(' ');
    el('path', {d, fill: 'none', stroke: css(s.c), 'stroke-width': 2, 'stroke-linejoin': 'round', 'stroke-linecap': 'round'}, svg);
    if (s.markers && (W >= 520 || s.pts.length < 15)) s.pts.forEach(p => el('circle', {cx: X(T(p[0])), cy: Y(p[1]), r: 4, fill: css(s.c), stroke: surf, 'stroke-width': 2}, svg));
  });
  // direct labels at the right end, de-collided
  const ends = cfg.series.map(s => { const p = s.pts[s.pts.length-1]; return {s, x: X(T(p[0])), y: Y(p[1]), v: p[1]}; })
    .sort((a, b) => a.y - b.y);
  ends.forEach((e, i) => { e.ly = i ? Math.max(e.y, ends[i-1].ly + 26) : Math.max(e.y, m.t + 8); });
  const over = ends.length ? ends[ends.length-1].ly - (H - m.b - 14) : 0;
  if (over > 0) ends.forEach(e => { e.ly -= over; });
  ends.forEach(e => {
    const g = el('g', {}, svg);
    el('circle', {cx: e.x, cy: e.y, r: 4, fill: css(e.s.c), stroke: surf, 'stroke-width': 2}, g);
    const tx = W - m.r + 10;
    const v = el('text', {x: tx, y: e.ly - 1, class: 'val'}, g); v.textContent = e.v.toFixed(0) + (cfg.unit || '');
    const l = el('text', {x: tx, y: e.ly + 12, class: 'lab'}, g); l.textContent = e.s.short; });
  // hover
  const tip = document.createElement('div'); tip.className = 'tip'; tip.hidden = true; box.appendChild(tip);
  const cross = el('line', {y1: m.t, y2: H - m.b, stroke: css('--ink-faint'), 'stroke-width': 1, visibility: 'hidden'}, svg);
  const dots = cfg.series.map(s => el('circle', {r: 4, fill: css(s.c), stroke: surf, 'stroke-width': 2, visibility: 'hidden'}, svg));
  const hit = el('rect', {x: m.l, y: 0, width: W - m.l - m.r, height: H, fill: 'transparent'}, svg);
  function near(pts, t){ let best = null, bd = Infinity;
    for (const p of pts){ const d = Math.abs(T(p[0]) - t); if (d < bd){ bd = d; best = p; } } return [best, bd]; }
  function move(ev){ const r = svg.getBoundingClientRect(); const px = ev.clientX - r.left;
    const t = x0 + (px - m.l) / (W - m.l - m.r) * (x1 - x0);
    const rows = []; let tx = null;
    cfg.series.forEach((s, i) => { const [p, dd] = near(s.pts, t);
      const ok = dd < (s.tol || 4) * 864e5;
      if (ok){ dots[i].setAttribute('cx', X(T(p[0]))); dots[i].setAttribute('cy', Y(p[1])); dots[i].setAttribute('visibility', 'visible');
        if (tx == null || i === (cfg.hdr || 0)) tx = p[0]; rows.push(`<div class="r"><i style="background:${css(s.c)}"></i>${s.short}<b>${cfg.tipv(s, p)}</b></div>`); }
      else dots[i].setAttribute('visibility', 'hidden'); });
    if (!rows.length){ tip.hidden = true; cross.setAttribute('visibility', 'hidden'); return; }
    const cx = Math.min(Math.max(px, m.l), W - m.r);
    cross.setAttribute('x1', cx); cross.setAttribute('x2', cx); cross.setAttribute('visibility', 'visible');
    tip.innerHTML = `<div class="h">${fmtD(tx)}</div>` + rows.join(''); tip.hidden = false;
    tipAt(box, tip, cx, ev.clientY - r.top); }
  hit.addEventListener('pointermove', move); hit.addEventListener('pointerdown', move);
  hit.addEventListener('pointerleave', () => { tip.hidden = true; cross.setAttribute('visibility', 'hidden');
    dots.forEach(d => d.setAttribute('visibility', 'hidden')); });
}

function barChart(id){
  const box = document.getElementById(id); box.innerHTML = '';
  const W = box.clientWidth, H = W < 520 ? 220 : 250, m = {l: 34, r: 8, t: 22, b: 40};
  const svg = el('svg', {viewBox: `0 0 ${W} ${H}`, height: H, role: 'img', 'aria-label': 'TSMC monthly revenue, March 2025 to September 2026'}, box);
  const B = D.bars, n = B.length, ticks = nice(0, Math.max(...B.map(b => b.v)), 4), top = ticks[ticks.length-1];
  const bw = (W - m.l - m.r) / n, Y = v => m.t + (1 - v / top) * (H - m.t - m.b);
  ticks.forEach(v => { el('line', {x1: m.l, x2: W - m.r, y1: Y(v), y2: Y(v), stroke: css('--line-soft')}, svg);
    const t = el('text', {x: m.l - 6, y: Y(v) + 3.5, 'text-anchor': 'end'}, svg); t.textContent = v; });
  const c = css('--s1'), rects = [];
  B.forEach((b, i) => { const x = m.l + i * bw + 1, w = Math.max(2, bw - 2), y = Y(b.v), h = Y(0) - y, r = Math.min(4, w / 2);
    const d = `M${x} ${Y(0)} V${y + r} Q${x} ${y} ${x + r} ${y} H${x + w - r} Q${x + w} ${y} ${x + w} ${y + r} V${Y(0)} Z`;
    rects.push(el('path', {d, fill: c}, svg));
    const mo = +b.m.split('-')[1];
    if (mo === 1 || mo === 7 || i === 0){ const t = el('text', {x: x + w / 2, y: H - m.b + 13, 'text-anchor': 'middle'}, svg);
      t.textContent = MON[mo - 1] + " '" + b.m.slice(2, 4); } });
  el('line', {x1: m.l, x2: W - m.r, y1: Y(0), y2: Y(0), stroke: css('--line')}, svg);
  D.quarters.forEach(q => { const i0 = B.findIndex(b => b.m === q.months[0]), i2 = B.findIndex(b => b.m === q.months[2]);
    const x = m.l + (i0 + i2 + 1) / 2 * bw;
    const t = el('text', {x, y: H - 5, 'text-anchor': 'middle', class: 'lab'}, svg);
    t.textContent = (W < 520 ? '' : q.q + ' ') + '+' + Math.round(q.yy) + '%';
    el('line', {x1: m.l + i0 * bw + 2, x2: m.l + (i2 + 1) * bw - 2, y1: H - m.b + 19, y2: H - m.b + 19, stroke: css('--ink-faint')}, svg); });
  const lb = B[n - 1], lt = el('text', {x: m.l + (n - .5) * bw, y: Y(lb.v) - 6, 'text-anchor': 'end', class: 'val'}, svg);
  lt.textContent = lb.v.toFixed(0);
  const tip = document.createElement('div'); tip.className = 'tip'; tip.hidden = true; box.appendChild(tip);
  B.forEach((b, i) => { const hr = el('rect', {x: m.l + i * bw, y: m.t, width: bw, height: H - m.t - m.b, fill: 'transparent'}, svg);
    const show = ev => { const r = svg.getBoundingClientRect();
      rects.forEach((p, j) => p.setAttribute('opacity', j === i ? 1 : .45));
      tip.innerHTML = `<div class="h">${fmtM(b.m)}</div><div class="r">Revenue<b>NT$${b.v.toFixed(1)}B</b></div>` +
        `<div class="r">vs prior month<b>${b.mm > 0 ? '+' : ''}${b.mm}%</b></div>` +
        (b.yy != null ? `<div class="r">vs a year earlier<b>${b.yy > 0 ? '+' : ''}${b.yy}%</b></div>` : '');
      tip.hidden = false; tipAt(box, tip, m.l + (i + .5) * bw, ev.clientY - r.top); };
    hr.addEventListener('pointermove', show); hr.addEventListener('pointerdown', show);
    hr.addEventListener('pointerleave', () => { tip.hidden = true; rects.forEach(p => p.setAttribute('opacity', 1)); }); });
}

function decomp(id){
  const box = document.getElementById(id); box.innerHTML = '';
  const lo = Math.min(0, ...D.decomp.map(r => Math.min(r.rates, r.spread))) - .1;
  const hi = Math.max(...D.decomp.map(r => r.rates + Math.max(0, r.spread))) + .2;
  const P = v => (v - lo) / (hi - lo) * 100;
  let html = '';
  D.decomp.forEach(r => {
    const c = `var(--${r.key})`, segs = [];
    // rates from zero; positive spread stacks after it with a 2px surface gap; negative spread runs left of zero
    if (r.rates >= 0) segs.push([P(0), P(r.rates), c, .4]); else segs.push([P(r.rates), P(0), c, .4]);
    if (r.spread >= 0) segs.push([P(Math.max(0, r.rates)), P(Math.max(0, r.rates) + r.spread), c, 1]);
    else segs.push([P(Math.min(0, r.rates) + r.spread), P(Math.min(0, r.rates)), c, 1]);
    const share = r.total ? Math.round(100 * r.rates / r.total) : 0;
    html += `<div class="row"><div class="rl"><span>${r.tier} · ${r.win}</span><b>${r.total > 0 ? '+' : ''}${r.total.toFixed(2)} pts</b></div>` +
      `<div class="trk" title="Treasury part ${r.rates.toFixed(2)} · credit spread ${r.spread.toFixed(2)}">` + segs.map(s => `<div class="seg" style="left:calc(${s[0]}% + 1px);width:calc(${Math.max(0, s[1] - s[0])}% - 2px);background:${s[2]};opacity:${s[3]}"></div>`).join('') +
      `<div class="zero" style="left:${P(0)}%"></div></div>` +
      `<div class="sub">Treasury part ${r.rates > 0 ? '+' : ''}${r.rates.toFixed(2)} · credit spread ${r.spread > 0 ? '+' : ''}${r.spread.toFixed(2)} · ` +
      (r.spread < 0 ? 'rates = all of the rise (the spread fell)' : `rates = ${share}% of the rise`) + `</div></div>`;
  });
  box.innerHTML = html;
}

const MT = ['2025-04-01','2025-07-01','2025-10-01','2026-01-01','2026-04-01','2026-07-01','2026-10-01'];
const qfmt = s => { const [y, m] = s.split('-'); return MON[+m-1] + " '" + y.slice(2); };
function draw(){
  const narrow = document.getElementById('c1').clientWidth < 520;
  lineChart('c1', {aria: 'Chip demand vs credit spreads, indexed to March 2025', base: 100, xticks: narrow ? MT.filter((_, i) => i % 2 === 0) : MT, xfmt: qfmt, hdr: 1,
    series: [
      {pts: D.demand, c: '--s1', short: 'Chip demand', markers: true, tol: 20},
      {pts: D.ccc, c: '--s2', short: 'Junk spread'},
      {pts: D.ig, c: '--s3', short: 'IG spread'}],
    tipv: (s, p) => s.short === 'Chip demand' ? `${p[1]} (${fmtM(p[0]).slice(0, 3)}, NT$${p[2]}B/mo)` : `${p[1]} (${p[2]}bp)`});
  barChart('c2');
  decomp('c3');
  const cd = D.cds.CRWV.map(p => p[0]);
  lineChart('c4', {aria: 'Five-year CDS since September 28, indexed', base: 100, xticks: [cd[0], cd[Math.floor(cd.length/2)], cd[cd.length-1]],
    xfmt: s => { const [y, m, d] = s.split('-'); return (+m) + '/' + (+d); },
    series: [
      {pts: D.cds.CRWV, c: '--s2', short: 'CoreWeave', markers: true, tol: 2},
      {pts: D.cds.CF, c: '--s3', short: 'Cash-flow four', markers: true, tol: 2},
      {pts: D.cds.ORCL, c: '--s4', short: 'Oracle', markers: true, tol: 2}],
    tipv: (s, p) => `${p[1]} (${p[2].toLocaleString()}bp)`});
}
draw();
let rt; window.addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(draw, 120); });
if (window.matchMedia) matchMedia('(prefers-color-scheme: dark)').addEventListener('change', draw);
new MutationObserver(draw).observe(document.documentElement, {attributes: true, attributeFilter: ['data-theme']});
"""


def sgn(v, nd=0):
    s = f"{v:+.{nd}f}"
    return s.replace("-", "−")


def table_rows():
    rows = []
    idx = {d[0][:7]: d for d in DATA["demand"]}
    for b in DATA["bars"]:
        m = b["m"]
        c, g = mavg(ccc, m), mavg(ig, m)
        rows.append(f"<tr><td>{m}</td><td>{b['v']:.1f}</td><td>{idx[m][1]:.1f}</td>"
                    f"<td>{round(c * 100)}</td><td>{100 * c / base_c:.1f}</td>"
                    f"<td>{round(g * 100)}</td><td>{100 * g / base_i:.1f}</td></tr>")
    c, g = mavg(ccc, "2026-10"), mavg(ig, "2026-10")
    rows.append(f"<tr><td>2026-10 (to {d_us(last_c)})</td><td>n/a</td><td>n/a</td><td>{round(c * 100)}</td>"
                f"<td>{100 * c / base_c:.1f}</td><td>{round(g * 100)}</td><td>{100 * g / base_i:.1f}</td></tr>")
    return "".join(rows)


def cds_rows():
    out = []
    for d in cds_days:
        out.append(f"<tr><td>{d}</td><td>{cds[d]['CRWV']:,.1f}</td><td>{cds[d]['ORCL']:.1f}</td>"
                   + "".join(f"<td>{cds[d][t]:.1f}</td>" for t in CF4) + f"<td>{cf_avg[d]:.1f}</td></tr>")
    return "".join(out)


built = dt.datetime.now(dt.timezone(dt.timedelta(hours=-7))).strftime("%Y-%m-%d %-I:%M%p PT").lower().replace("pt", "PT")
html = f"""<title>Chips vs Credit</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>{CSS}</style>
<div class="wrap">
  <header>
    <div class="eyebrow">Wiki-Brain · AI demand vs AI financing · since CoreWeave's IPO (3/28/2025)</div>
    <h1>Chip demand is still climbing. Credit stress is catching up, and only for the borrowers without the cash.</h1>
    <div class="meta">credit through {last_c} · TSMC revenue through Sep 2026 · CDS through {d1} · built {built}</div>
  </header>

  <section class="card">
    <div class="qa">
      <div class="q"><div class="ask">Is chip demand flattening?</div><div class="ans">No. It sped up.</div>
        <p>TSMC revenue grew {F['q1']:.0f}% from a year earlier in Q1 2026, {F['q2']:.0f}% in Q2 and <b>{F['q3']:.0f}%</b> in Q3
        (in Taiwan dollars; +41% in US dollars). September was flat on August ({sgn(F['sep_mm'],1)}%), which is one month.
        TSMC guided Q4 up another 12–16% on Q3, in US dollars.</p></div>
      <div class="q"><div class="ask">Is the spread flattening?</div><div class="ans">Demand vs stress: yes, fast.</div>
        <p>Through September demand pulled away from credit stress: the gap between the lines in Chart 1 reached
        {F['gap_sep']:.0f} points. Junk spreads then went from a September average of {F['ccc_sep_bp']:,}bp to {F['ccc_last']*100:,.0f}bp on {d_us(last_c)},
        which cuts the gap to about {F['gap_now']:.0f} if demand held at September's level. Credit is catching up; demand has not slowed.
        Between the two kinds of borrower it is the opposite: that spread is widening (Chart 4).</p></div>
      <div class="q"><div class="ask">Are rates driving the stress?</div><div class="ans">For the giants, yes. For CoreWeave, no.</div>
        <p>Since the IPO the investment-grade borrowing rate rose {igI['total']:.2f} points, and all of it came from Treasury yields:
        their credit spread actually fell. The junk rate rose {ccI['total']:.2f} points, {pct(ccI['spread'], ccI['total'])}% of it credit spread.
        Since 9/30 the 10-year yield <i>fell</i> ({F['y10_930']:.2f}% → {F['y10_last']:.2f}% on {d_us(F['y10_lastd'])}) while junk spreads widened by {round((F['ccc_last']-F['ccc_930'])*100)}bp.</p></div>
    </div>
  </section>

  <section class="card">
    <h2>Chart 1 · the shape Jake asked for</h2>
    <h3>Demand vs credit stress, both indexed to March 2025 = 100</h3>
    <div class="legend"><span><i style="background:var(--s1)"></i>Chip demand: TSMC revenue, 3-month average</span>
      <span><i style="background:var(--s2)"></i>Debt-funded borrowers: junk (CCC) bond spread</span>
      <span><i style="background:var(--s3)"></i>Cash-flow borrowers: investment-grade bond spread</span></div>
    <div class="chart" id="c1"></div>
    <p class="note">Up is more demand on the blue line and more stress on the other two. The investment-grade line is
    below where it started: the giants borrow at a tighter spread over Treasuries than when CoreWeave listed. The junk line
    spiked in April 2025 (the tariff shock), drifted for a year, climbed from June to September 2026, then jumped in October.
    That October jump is what closes the gap.
    Tap or hover for values.</p>
    <details><summary>Table view</summary><div class="tw"><table>
      <thead><tr><th>Month</th><th>TSMC NT$B</th><th>Demand idx</th><th>CCC bp</th><th>CCC idx</th><th>IG bp</th><th>IG idx</th></tr></thead>
      <tbody>{table_rows()}</tbody></table></div>
      <p class="note">Demand idx = 3-month average revenue ÷ the Jan–Mar 2025 average. Spread idx = monthly average ÷ March 2025 average
      (CCC {base_c*100:.0f}bp, IG {base_i*100:.0f}bp).</p></details>
  </section>

  <section class="card">
    <h2>Chart 2 · chip demand, month by month</h2>
    <h3>TSMC monthly revenue, NT$ billions</h3>
    <div class="chart" id="c2"></div>
    <p class="note">TSMC makes the chips for Nvidia, AMD, Broadcom and Apple, and reports revenue monthly, so it is the
    fastest public read on AI chip orders. The labels under the bars are each 2026 quarter against the same quarter of 2025.
    September's {F['sep_mm']:+.1f}% versus August is the first down month since April (−1.1%).
    Revenue is not units, and some of the growth is price.</p>
  </section>

  <section class="card">
    <h2>Chart 3 · are rates doing it?</h2>
    <h3>What raised each tier's borrowing rate</h3>
    <div class="legend"><span><i class="pale" style="background:var(--ink-3)"></i>Treasury part (pale)</span>
      <span><i class="solid" style="background:var(--ink-3)"></i>Credit-spread part (solid)</span></div>
    <div class="dc" id="c3"></div>
    <p class="note">Each bar is the change in the index's all-in yield, split into the Treasury part (yield minus spread)
    and the credit-spread part. The split uses each index's own yield and spread, so it is matched to the index's maturity
    rather than to the 10-year. Day to day, junk spreads and the 10-year have not moved together: the correlation of daily changes
    is {F['rc_ipo']:+.2f} since the IPO (n={F['n_ipo']} days; weakly opposite, so spreads tended to widen on days yields fell) and
    {F['rc_aug']:+.2f} since August 1 (n={F['n_aug']}; no relationship).</p>
  </section>

  <section class="card">
    <h2>Chart 4 · the two borrowers, on their own credit</h2>
    <h3>Five-year credit default swaps since {d_us(d0)}, indexed to {d_us(d0)} = 100</h3>
    <div class="legend"><span><i style="background:var(--s2)"></i>CoreWeave</span>
      <span><i style="background:var(--s3)"></i>Cash-flow four: Alphabet, Amazon, Microsoft, Meta (average)</span>
      <span><i style="background:var(--s4)"></i>Oracle</span></div>
    <div class="chart" id="c4"></div>
    <p class="note">A credit default swap (CDS) is insurance against a borrower defaulting; its price in basis points (bp) is the market's
    fear gauge for that one company. Since {d_us(d0)}: CoreWeave {F['crwv0']:,.0f} → {F['crwv1']:,.0f}bp ({sgn(F['crwv1']-F['crwv0'])}),
    Oracle {F['orcl0']:.0f} → {F['orcl1']:.0f}bp ({sgn(F['orcl1']-F['orcl0'])}), the cash-flow four {F['cf0']:.1f} → {F['cf1']:.1f}bp
    ({sgn(F['cf1']-F['cf0'],1)}). CoreWeave's premium over the four went from {F['gap0']:,.0f} to {F['gap1']:,.0f}bp.
    <b>Between the two borrower types the spread is widening, not flattening.</b></p>
    <details><summary>Table view (bp)</summary><div class="tw"><table>
      <thead><tr><th>Date</th><th>CRWV</th><th>ORCL</th><th>GOOGL</th><th>AMZN</th><th>MSFT</th><th>META</th><th>CF avg</th></tr></thead>
      <tbody>{cds_rows()}</tbody></table></div></details>
  </section>

  <section class="card">
    <h2>So where does the money go</h2>
    <ul class="money">
      <li><b>Cash-flow giants<br>GOOGL · AMZN · MSFT · META</b><span>Their higher borrowing cost is a rates story, and their own
        credit barely moved (+{F['cf1']-F['cf0']:.1f}bp in CDS while CoreWeave's rose {F['crwv1']-F['crwv0']:.0f}bp). A bond rally helps them directly.
        This is the case for holding GOOGL through the chip sell-off.</span></li>
      <li><b>Debt-funded borrowers<br>CRWV · ORCL</b><span>Theirs is a credit story, and lower Treasury yields do not reach
        them: since 9/30 the 10-year fell while their spreads blew out. That is the CRWV short.</span></li>
      <li><b>The suppliers<br>TSM · the chip names</b><span>Orders were still accelerating through September. The risk is
        whether the debt-funded buyers can keep paying, not end demand. TSM fell on a record quarter, so the market is
        pricing the financing, not the orders.</span></li>
    </ul>
  </section>

  <section class="card">
    <h2>What this cannot see</h2>
    <ul class="cav">
      <li>Charts 1 and 3 use bond indexes (ICE BofA CCC and investment-grade) as stand-ins, not each company's own bonds.
        CoreWeave's 2032 notes yield about 16.1% to worst (reported 10/15), a little below the CCC index's {cccey[max(cccey)]:.1f}%
        and far above the investment-grade index's {igey[max(igey)]:.1f}%, so the market prices CoreWeave close to the CCC tier.</li>
      <li>Company CDS only starts 8/21/2026, with a gap from 8/24 to 9/28 and a contract roll on 9/20. Only the current
        (Dec-2031) contract is plotted. The bp figures are model conversions of upfront prices: read the changes, not the levels.</li>
      <li>The "gap" in Chart 1 is a picture, not a measured quantity: revenue and spreads are different units, put on one scale by indexing.
        October has no TSMC month yet (due ~11/10).</li>
      <li>TSMC revenue is in Taiwan dollars and includes price increases and non-AI chips.</li>
      <li>The 10-year is FRED's daily close through {F['y10_lastd']}.</li>
    </ul>
  </section>

  <p class="src">Sources: TSMC monthly revenue reports (SEC Form 6-K) · ICE BofA US Corporate and CCC &amp; Lower option-adjusted
  spreads and effective yields via FRED (BAMLC0A0CM, BAMLH0A3HYC, BAMLC0A0CMEY, BAMLH0A3HYCEY) · 10-year Treasury, FRED DGS10 ·
  ICE Clear Credit end-of-day CDS settlement prices (<span class="mono">data/fragility/cds_panel.csv</span>). Built by
  <span class="mono">tools/chips_credit_html.py</span>; a static snapshot that does not refresh itself.</p>
</div>
<script type="application/json" id="d">{json.dumps(DATA, separators=(',', ':'))}</script>
<script>{JS}</script>
"""

out = P("docs", "chips-credit.html")
with open(out, "w") as f:
    f.write(html)
print(f"wrote {out} ({len(html)//1024} KB)")
for k in ("q1", "q2", "q3", "sep_mm", "dem_last", "ccc_sep", "ccc_now", "gap_sep", "gap_now", "ccc_930", "ccc_last",
          "y10_930", "y10_last", "y10_lastd", "crwv0", "crwv1", "orcl0", "orcl1", "cf0", "cf1", "gap0", "gap1",
          "rc_ipo", "rc_aug", "ri_ipo", "n_ipo", "n_aug", "d0", "d1"):
    print(k, F[k])
for r in decomp:
    print(r)
