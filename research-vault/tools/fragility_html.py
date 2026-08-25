#!/usr/bin/env python3
"""
fragility_html.py -- renders data/fragility/latest.json into docs/index.html.

THE NUMBERS ARE BAKED IN AT BUILD TIME. There is no client-side fetch and that is
the whole design. A page that pulls its data with JavaScript renders EMPTY to an
agent (WebFetch converts HTML to markdown; it does not execute scripts), so a
"live" dashboard would be unreadable by the one reader who checks it daily.
Static values are readable by a person AND by Claude, diff cleanly in git, and
need no CORS, no API key and no server.

DESIGN NOTE: the semantic status ramp owns the data channel. The accent hue is
used ONLY for structure, links and focus, so nothing competes with the one thing
the page exists to communicate -- which stage is lit.
"""
import json, os
from html import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D    = json.load(open(os.path.join(ROOT, "data", "fragility", "latest.json")))

# Reserved status palette -- never reused as a series hue.
SC    = {"calm": "#0ca30c", "warning": "#fab219", "serious": "#ec835a", "critical": "#d03b3b"}
GLYPH = {"calm": "●", "warning": "▲", "serious": "▲", "critical": "■"}
ORDER = list(SC)


def spark(vals, status, w=120, h=30, pad=4):
    """One series. No legend, no axis -- the row label names it. A CALM row draws
    in neutral ink rather than the 'good' green: painting twenty quiet series
    green makes the page read as a reassurance, and the eye should go to the rows
    that are actually lit."""
    if not vals or len(vals) < 2:
        return '<span class="nodata">no history</span>'
    lo, hi = min(vals), max(vals)
    rng = (hi - lo) or 1.0
    n = len(vals)
    pts = [(pad + i * (w - 2 * pad) / (n - 1),
            h - pad - (v - lo) * (h - 2 * pad) / rng) for i, v in enumerate(vals)]
    col = "var(--ink-faint)" if status == "calm" else SC[status]
    d = "M" + " L".join("%.1f,%.1f" % p for p in pts)
    area = "%s L%.1f,%.1f L%.1f,%.1f Z" % (d, pts[-1][0], h, pts[0][0], h)
    ex, ey = pts[-1]
    uid = abs(hash((round(lo, 6), round(hi, 6), n, status))) % 1000000
    return (
        '<svg class="spark" viewBox="0 0 %d %d" width="%d" height="%d" role="img" '
        'aria-label="last %d observations, low %.4g, high %.4g">'
        '<defs><linearGradient id="g%d" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="%s" stop-opacity=".20"/>'
        '<stop offset="1" stop-color="%s" stop-opacity="0"/></linearGradient></defs>'
        '<path d="%s" fill="url(#g%d)"/>'
        '<path d="%s" fill="none" stroke="%s" stroke-width="1.75" '
        'stroke-linejoin="round" stroke-linecap="round"/>'
        '<circle cx="%.1f" cy="%.1f" r="2.8" fill="%s" stroke="var(--card)" '
        'stroke-width="1.6"/></svg>'
        % (w, h, w, h, n, lo, hi, uid, col, col, area, uid, d, col, ex, ey, col))


def typo(t):
    """ASCII arrows and dashes are correct in the terminal view and wrong in
    19px serif. latest.json stays ASCII; only the page gets the real glyphs."""
    return t.replace(" -> ", " \u2192 ").replace(" -- ", " \u2014 ")


def chip(status):
    return ('<span class="chip" style="--c:%s"><span class="g" aria-hidden="true">%s</span>%s</span>'
            % (SC[status], GLYPH[status], status))


def num(v, unit):
    if v is None:
        return "—"
    if abs(v) >= 1000:
        return "{:,.0f}".format(v)
    if abs(v) >= 100:
        return "{:,.1f}".format(v)
    return "{:,.2f}".format(v)


def dl(v, stress_up=True):
    """Coloured by whether the move is TOWARD stress, not by its sign. Rising
    deposits are not a red number just because rising dealer fails is."""
    if v is None:
        return '<span class="mut">—</span>'
    if v == 0:
        return '<span class="mut">0.00</span>'
    cls = "up" if ((v > 0) == stress_up) else "dn"
    s = "{:+,.0f}".format(v) if abs(v) >= 1000 else "{:+,.2f}".format(v)
    return '<span class="%s">%s</span>' % (cls, s)


CSS = """
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Serif:wght@400;500&display=swap');

:root{
  --ground:#f4f6f7; --card:#ffffff; --card-2:#f7f9fa;
  --line:#e2e6ea; --line-soft:#eef1f4;
  --ink:#101418; --ink-2:#4a5560; --ink-3:#6f7c88; --ink-faint:#9aa5b1;
  --accent:#2f5d8c; --accent-soft:#e8eef5;
  --pos:#0f7a3d; --neg:#b3261e;
  --shadow:0 1px 2px rgba(16,20,24,.05), 0 8px 24px -14px rgba(16,20,24,.16);
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    color-scheme:dark;
    --ground:#0e1216; --card:#161b21; --card-2:#1b2129;
    --line:#252c34; --line-soft:#1e242b;
    --ink:#eef2f5; --ink-2:#a7b3bf; --ink-3:#7d8b98; --ink-faint:#5b6873;
    --accent:#7aa8d8; --accent-soft:#1b2733;
    --pos:#5cc98a; --neg:#f2857c;
    --shadow:0 1px 2px rgba(0,0,0,.42), 0 8px 24px -14px rgba(0,0,0,.7);
  }
}
:root[data-theme="dark"]{
  color-scheme:dark;
  --ground:#0e1216; --card:#161b21; --card-2:#1b2129;
  --line:#252c34; --line-soft:#1e242b;
  --ink:#eef2f5; --ink-2:#a7b3bf; --ink-3:#7d8b98; --ink-faint:#5b6873;
  --accent:#7aa8d8; --accent-soft:#1b2733;
  --pos:#5cc98a; --neg:#f2857c;
  --shadow:0 1px 2px rgba(0,0,0,.42), 0 8px 24px -14px rgba(0,0,0,.7);
}

*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--ground);color:var(--ink);
  font-family:"IBM Plex Sans",ui-sans-serif,-apple-system,"Segoe UI",Roboto,sans-serif;
  font-size:14px;line-height:1.5}
.wrap{max-width:1060px;margin:0 auto;padding:34px 20px 72px;
  display:flex;flex-direction:column;gap:18px}

.mast{display:flex;flex-direction:column;gap:5px;margin-bottom:2px}
.eyebrow{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:10.5px;
  letter-spacing:.16em;text-transform:uppercase;color:var(--ink-3)}
h1{font-size:25px;line-height:1.15;margin:0;letter-spacing:-.018em;
  font-weight:600;text-wrap:balance}
.mast .meta{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:11.5px;
  color:var(--ink-3)}

.card{background:var(--card);border:1px solid var(--line);border-radius:12px;
  padding:20px 22px;box-shadow:var(--shadow)}
h2{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:10.5px;
  text-transform:uppercase;letter-spacing:.14em;color:var(--ink-3);
  margin:0 0 16px;font-weight:500}

.verdict{display:flex;gap:17px;align-items:stretch}
.verdict .bar{flex:none;width:3px;border-radius:2px;background:var(--vc)}
.verdict .txt{display:flex;flex-direction:column;gap:10px;min-width:0}
.lede{font-family:"IBM Plex Serif",Georgia,serif;font-size:19px;line-height:1.34;
  font-weight:500;letter-spacing:-.008em;text-wrap:balance;margin:0}
.verdict .sub2{color:var(--ink-2);font-size:12.5px;line-height:1.62;margin:0;max-width:76ch}

ol.ladder{list-style:none;margin:0;padding:0;position:relative}
ol.ladder::before{content:"";position:absolute;left:13px;top:22px;bottom:22px;
  width:1px;background:var(--line)}
ol.ladder li{position:relative;display:flex;align-items:center;gap:13px;padding:9px 0}
.sn{flex:none;width:27px;height:27px;border-radius:50%;display:grid;place-items:center;
  font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:11.5px;font-weight:500;
  background:var(--card);border:1px solid var(--line);color:var(--ink-3)}
li.lit .sn{background:var(--c);border-color:var(--c);color:#fff;font-weight:600}
li.dark .ln{color:var(--ink-3)}
.ln{flex:1;min-width:0;font-size:13.5px}
.cnt{flex:none;font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:11px;
  color:var(--ink-3);width:88px;text-align:right;font-variant-numeric:tabular-nums}

.chip{display:inline-flex;align-items:center;gap:5px;font-size:11px;font-weight:600;
  color:var(--c);white-space:nowrap}
.chip .g{font-size:8.5px;line-height:1}

.scroll{overflow-x:auto}
table{border-collapse:collapse;width:100%;min-width:800px}
th,td{text-align:right;padding:10px 9px;border-bottom:1px solid var(--line-soft)}
thead th{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:10px;
  text-transform:uppercase;letter-spacing:.11em;color:var(--ink-3);font-weight:500;
  border-bottom:1px solid var(--line)}
td.nm,th.nm,tr.grp th{text-align:left}
tbody tr:not(.grp):hover td{background:var(--card-2)}
tr.grp th{padding:22px 9px 8px;font-size:11.5px;color:var(--ink-2);font-weight:600;
  border-bottom:1px solid var(--line)}
tr.grp .sn{display:inline-grid;width:21px;height:21px;font-size:10px;margin-right:8px;
  vertical-align:middle}
td.nm{box-shadow:inset 3px 0 0 var(--rc,transparent)}
.nm b{font-weight:600;font-size:13.5px;letter-spacing:-.005em}
.sub{display:block;color:var(--ink-3);font-size:11px;margin-top:2px;line-height:1.4}
.v,.d,.p{font-family:"IBM Plex Mono",ui-monospace,monospace;font-variant-numeric:tabular-nums}
.v{font-weight:500;font-size:13.5px}
.u{color:var(--ink-faint);font-weight:400;font-size:10.5px;margin-left:4px;
  font-family:"IBM Plex Sans",sans-serif}
.d{font-size:12.5px}
.up{color:var(--neg)}.dn{color:var(--pos)}.mut{color:var(--ink-faint)}
.p{color:var(--ink-2);font-size:12px}
td.st{white-space:nowrap}
.stale{display:inline-block;font-family:"IBM Plex Mono",ui-monospace,monospace;
  font-size:9px;font-weight:600;letter-spacing:.06em;color:var(--card);
  background:var(--ink-3);border-radius:3px;padding:2px 5px;margin-left:6px}
.spark{display:block}
td.sp{width:132px;padding:5px 9px}
.nodata{color:var(--ink-faint);font-size:11px}

ul.gaps{list-style:none;margin:0;padding:0}
ul.gaps li{padding:11px 0;border-bottom:1px solid var(--line-soft)}
ul.gaps li:last-child{border-bottom:0}
.gs{display:inline-block;font-family:"IBM Plex Mono",ui-monospace,monospace;
  font-size:9.5px;font-weight:600;color:var(--ink-3);margin-left:9px;
  text-transform:uppercase;letter-spacing:.08em}
.err{color:var(--neg);font-size:12.5px;margin:15px 0 0;padding-top:14px;
  border-top:1px solid var(--line-soft)}
p.note{color:var(--ink-2);font-size:12.5px;line-height:1.65;margin:0 0 11px;max-width:76ch}
p.note:last-child{margin-bottom:0}
code{font-family:"IBM Plex Mono",ui-monospace,monospace;background:var(--accent-soft);
  color:var(--accent);border-radius:4px;padding:1.5px 5px;font-size:11.5px}
a{color:var(--accent)}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:3px}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
@media (max-width:640px){
  .wrap{padding:24px 14px 56px}
  h1{font-size:21px}
  .lede{font-size:17px}
  .cnt{width:76px}
}
"""

# ------------------------------------------------------------------ assemble
lit = [l for l in D["ladder"] if l["lit"]]
worst = max((l["status"] for l in D["ladder"]), key=ORDER.index)

rows_html, cur = [], None
for r in sorted(D["rows"], key=lambda x: (x["stage"] or 99, -ORDER.index(x["status"]))):
    if r["stage"] != cur:
        cur = r["stage"]
        nm = D["stages"].get(str(cur), D["stages"].get(cur, "Context — not a chain stage"))
        rows_html.append('<tr class="grp"><th colspan="8"><span class="sn">%s</span>%s</th></tr>'
                         % ((str(cur) if cur else "·"), escape(str(nm))))
    lvl = "—" if r["level_pct"] is None else "%.0f" % r["level_pct"]
    lvl_t = ("level percentile suppressed: this series trends structurally, so its level "
             "measures the trend rather than stress. Scored on rate of change only."
             if r["level_pct"] is None
             else "%.0fth percentile of its own trailing 3 years" % r["level_pct"])
    rate = "—" if r["rate_pct"] is None else "%.0f" % r["rate_pct"]
    stale = ('<span class="stale" title="last observation is %d days old">STALE %dd</span>'
             % (r["age_days"], r["age_days"])) if r["stale"] else ""
    stripe = "transparent" if r["status"] == "calm" else SC[r["status"]]
    sub = ("chart %d · " % r["chart"] if r["chart"] else "") + escape(r["note"])
    rows_html.append(
        '<tr>'
        '<td class="nm" style="--rc:%s"><b>%s</b><span class="sub">%s</span></td>'
        '<td class="sp">%s</td>'
        '<td class="v">%s<span class="u">%s</span></td>'
        '<td class="d">%s</td><td class="d">%s</td>'
        '<td class="p" title="%s">%s</td>'
        '<td class="p" title="percentile of the trailing 20-observation change">%s</td>'
        '<td class="st">%s%s</td></tr>'
        % (stripe, escape(r["label"]), sub, spark(r["spark"], r["status"]),
           num(r["value"], r["unit"]), escape(r["unit"]),
           dl(r["d1"], not r["inverted"]), dl(r["d20"], not r["inverted"]),
           escape(lvl_t), lvl, rate, chip(r["status"]), stale))

ladder_html = "".join(
    '<li class="%s" style="--c:%s"><span class="sn">%d</span>'
    '<span class="ln">%s</span>%s<span class="cnt">%d/%d lit%s</span></li>'
    % ("lit" if l["lit"] else "dark", SC[l["status"]], l["stage"], escape(l["name"]),
       chip(l["status"]), l["n_lit"], l["n_indep"],
       "&nbsp;✦" if l["corroborated"] else "")
    for l in D["ladder"])

gaps_html = "".join(
    '<li><b>Chart %s — %s</b><span class="gs">%s</span>'
    '<span class="sub">%s</span></li>'
    % (g["chart"], escape(g["name"]), escape(g["status"]), escape(g["why"]))
    for g in D["gaps"])

errs = D.get("feed_errors") or []
err_html = ('<p class="err">Feed errors this run: <b>%s</b> — those rows carry the last '
            'good value and are stamped STALE.</p>'
            % escape(", ".join(e["key"] for e in errs))) if errs else ""

HTML = """<title>Fragility Ladder</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>%s</style>
<div class="wrap">

<header class="mast">
<span class="eyebrow">Credit &amp; debt · %d series</span>
<h1>Fragility ladder</h1>
<span class="meta">%s · baked in at build time, no client-side fetch</span>
</header>

<div class="card verdict" style="--vc:%s">
<div class="bar"></div>
<div class="txt">
<p class="lede">%s</p>
<p class="sub2">Stress is meant to migrate <b>downward</b> through these stages. One lit stage is a
repricing; stages lighting <b>in order</b> is the chain. <b>n/N lit</b> counts the independent series
in a stage at warning or worse — a stage holding eight series has eight chances to light and one
holding a single series has one, so the count is shown rather than hidden.
<b>✦ marks corroboration</b>: two or more independent series in that stage agree.</p>
</div></div>

<div class="card"><h2>Transmission ladder</h2><ol class="ladder">%s</ol></div>

<div class="card"><h2>Indicators</h2>
<p class="note">Change columns are in <b>observations, not days</b> — a weekly series&rsquo;
&ldquo;1p&rdquo; is one week, and a change is coloured by whether it moves <b>toward stress</b>,
not by its sign. <b>lvl%%</b> is the percentile of today&rsquo;s value within its own three years,
shown as &ldquo;—&rdquo; for series that trend structurally. <b>rate%%</b> is the percentile of
the trailing 20-observation change.</p>
<div class="scroll"><table>
<thead><tr><th class="nm">Indicator</th><th>120 obs</th><th>Value</th><th>chg 1p</th>
<th>chg 20p</th><th>lvl%%</th><th>rate%%</th><th>Status</th></tr></thead>
<tbody>%s</tbody></table></div>%s</div>

<div class="card"><h2>Known gaps — not in the data above</h2>
<p class="note">Named explicitly so an absent row is never mistaken for a calm one.</p>
<ul class="gaps">%s</ul></div>

<div class="card"><h2>Method</h2>
<p class="note"><b>No absolute thresholds anywhere.</b> Every indicator is ranked against its own
trailing three years, on level and on 20-observation rate of change. Status reaches
<code>critical</code> at level ≥95th <i>and</i> rate ≥80th; <code>serious</code> at level
≥90th <i>or</i> rate ≥95th; <code>warning</code> at level ≥75th <i>or</i> rate
≥85th. Series that trend structurally are scored on rate alone. Bank loans and deposits are
inverted — for those, <b>contraction</b> is the stress.</p>
<p class="note">A series that merely restates another (the CCC-minus-HY gap is arithmetic on CCC and
HY) is shown and scored but <b>excluded from the corroboration count</b>, so CCC is not counted
twice. Cross-bank comparisons are held to like-for-like seasonal adjustment: large-bank C&amp;I is
computed as domestically-chartered minus small, both <b>not</b> seasonally adjusted, because the
seasonally-adjusted small-bank series was discontinued in 2018.</p>
<p class="note">Sources, all keyless: FRED public graph CSV · New York Fed markets API ·
TreasuryDirect auction API · Yahoo (^MOVE). Raw series live in
<code>data/fragility/series/*.csv</code>.</p></div>

</div>""" % (CSS, len(D["rows"]), escape(D["generated"][:16].replace("T", " ")),
             SC[worst], escape(typo(D["verdict"])), ladder_html,
             "".join(rows_html), err_html, gaps_html)

os.makedirs(os.path.join(ROOT, "docs"), exist_ok=True)
out = os.path.join(ROOT, "docs", "index.html")
open(out, "w").write(HTML)
print("wrote %s  (%s bytes, %d indicators, %d stage(s) lit, worst=%s)"
      % (out, format(len(HTML), ","), len(D["rows"]), len(lit), worst))
