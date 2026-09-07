# mega_cap_pe_before_rips_cell.py — v3 (ran clean in Jake's Colab 2026-09-06 11:38pm) — WHERE WERE THE MEGA-CAPS' P/Es BEFORE THEIR BEST RUNS, AND WHERE ARE THEY NOW?
# Jake's ask 2026-09-06 (10:24pm): "I wanted individual stocks. What's Google's, MSFT, Nvidia, Tesla etc historical
# best P/E before their best quarters? Where do these stocks tend to be before they rip and where are they now."
#
# METHOD (per name, ~2008 → today, POINT-IN-TIME):
#   EPS   = GAAP DILUTED EPS by calendar quarter from SEC EDGAR companyconcept (free, no key). For each quarter the
#           EARLIEST-FILED value is kept = the original as-reported figure. Trailing-4Q EPS is built from those, then
#           SPLIT-ADJUSTED to today's share basis using yfinance's split history (EDGAR EPS is pre-split; yfinance
#           prices are split-adjusted — without this step every pre-split P/E is wrong by the split factor).
#   AVAIL = a quarter's EPS is usable at month m only if its 10-Q/10-K was FILED on or before m. No look-ahead.
#   P/E   = month-end close ÷ trailing-4Q EPS available at that month.   n/m when trailing EPS ≤ 0.
#   RIP   = forward 12-month PRICE return from month m (dividends omitted; immaterial for these names).
#   DECOMP= (1+ret) = (P/E_end / P/E_start) × (EPS_end / EPS_start)  → how much of each rip was MULTIPLE vs EARNINGS.
#   HINDSIGHT FWD P/E = price(m) ÷ trailing EPS twelve months LATER = "what you were paying for what it was about to
#           earn". Not what the market saw; it is how the index study's 30-40x-trailing bucket turned out +9%.
# OUTPUT per name:
#   • P/E at the start of the TOP-DECILE 12m windows vs BOTTOM-DECILE vs ALL (median, IQR)  ← "where do they tend to be"
#   • the top 3 NON-OVERLAPPING 12m rips: start date, P/E then, hindsight-fwd P/E, return, EPS growth, multiple change
#   • NOW: current trailing P/E, its percentile in the name's own history, and the current EPS trend (last 4Q vs prior 4Q)
# CAVEATS THAT TRAVEL WITH THE NUMBERS:
#   • n ≈ 150-220 months per name with OVERLAPPING 12m windows → ~12-18 independent years. Thin.
#   • These eight are the WINNERS — chosen because they ripped. The study DESCRIBES their pattern; it does not
#     predict. (Survivorship is built into the question, not an accident of the data.)
#   • GAAP diluted EPS, not "street/adjusted": ≈ same for NVDA/META/GOOGL/MSFT/AAPL; materially different for
#     TSLA (credits, SBC) and AMZN (AWS-era GAAP). Read those two P/Es as GAAP P/Es.
#   • Expect the earnings-trough pattern: several rips START at a HIGH trailing P/E because EPS had just collapsed
#     (NVDA/META/AMZN 2022→23). "Low P/E before the rip" is one regime; "high P/E on trough earnings" is another,
#     and the DECOMP column is what tells them apart.
# RUN: paste into Colab. ~1-2 min. Paste the printed output back into chat for the read.

import subprocess, sys, json, re, time, urllib.request, math
try:
    import yfinance as yf; import pandas as pd; import numpy as np
except Exception:
    subprocess.run([sys.executable,'-m','pip','install','-q','yfinance','pandas','numpy'])
    import yfinance as yf; import pandas as pd; import numpy as np

# ---- PARAMETERS (edit here only) ----
NAMES = ['GOOGL','MSFT','NVDA','TSLA','AAPL','AMZN','META','AVGO']
START = '2008-01-01'
TOPN_WINDOWS = 3
EDGAR_UA = {'User-Agent': 'INMA research vault jake@inmagent.com'}   # SEC requires a contact UA

# ---- 1. CIKs (predecessor CIKs concatenated where the registrant changed) ----
tk = json.load(urllib.request.urlopen(urllib.request.Request('https://www.sec.gov/files/company_tickers.json', headers=EDGAR_UA), timeout=30))
CIK = {v['ticker']: [str(v['cik_str']).zfill(10)] for v in tk.values() if v['ticker'] in NAMES}
CIK.setdefault('GOOGL', []).append('0001288776')   # Google Inc. (pre-2015 holding-company reorg) — adds 2008-2015
missing = [n for n in NAMES if n not in CIK]
if missing: print('⚠️ no CIK for', missing)

# ---- 1b. split history FIRST — every EDGAR period is put on today's share basis BEFORE any arithmetic ----
#   ⛔ BUG CAUGHT 2026-09-06 in the container run: deriving fiscal Q4 = FY − (Q1+Q2+Q3) with the FY on a POST-split
#   basis and Q1 on a PRE-split basis produced NVDA Q4-FY25 = −4.49 and a negative prior-year TTM (NVDA 10:1 Jun-2024,
#   AVGO 10:1 Jul-2024). The same mixing produced false LUMPY flags on GOOGL's 2023 quarters (20:1 Jul-2022). Fix:
#   adjust each period by the cumulative splits AFTER its end date, then derive Q4, then flag lumpy.
splits = {n: yf.Ticker(n).splits for n in NAMES}
def split_factor_after(n, date):
    """cumulative split ratio for splits that occurred AFTER `date` → divide as-reported EPS by this."""
    s = splits.get(n)
    if s is None or len(s) == 0: return 1.0
    idx = s.index.tz_localize(None) if s.index.tz is not None else s.index
    sel = s[idx > pd.Timestamp(date)]
    return float(np.prod(sel.values)) if len(sel) else 1.0

# ---- 2. EDGAR quarterly diluted EPS — VALIDATED 2026-09-06 against META/GOOGL raw entries ----
#   • classify by PERIOD DURATION (start→end), not by EDGAR's `frame` (frames mis-assign YTD figures);
#   • 3-month periods = quarters; 350-380 day periods = fiscal years;
#   • earliest-filed value per period end = the ORIGINAL as-reported figure (later 10-Qs re-report prior-year comparatives);
#   • fiscal Q4 is usually NOT reported as a 3-month period → derive Q4 = FY − (Q1+Q2+Q3) inside that fiscal window;
#   • LUMPY flag: a quarter outside 0.3×..3.0× the median of the prior 8 quarters (META Q3-25 $1.05 / Q1-26 $10.44 and
#     GOOGL Q1-26 $5.11 / Q2-26 $9.11 are GENUINE GAAP prints that reconcile to YTD — one-offs, not errors — and they
#     make trailing P/E collapse for a year. Read those P/Es with the flag.)
def edgar_eps(n, ciks):
    ents = []
    for cik in ciks:
        url = f'https://data.sec.gov/api/xbrl/companyconcept/CIK{cik}/us-gaap/EarningsPerShareDiluted.json'
        try: ents += json.load(urllib.request.urlopen(urllib.request.Request(url, headers=EDGAR_UA), timeout=30))['units']['USD/shares']
        except Exception as e: print(f'  ⚠️ EDGAR {cik}: {e}')
        time.sleep(0.15)
    q, fy = {}, {}
    for x in ents:
        if 'start' not in x: continue
        s, e = pd.Timestamp(x['start']), pd.Timestamp(x['end']); dur = (e - s).days
        f = pd.Timestamp(x['filed'])
        rec = dict(start=s, end=e, filed=f, val=float(x['val']) / split_factor_after(n, f))   # keyed on FILING date (v3 fix)
        if 60 <= dur <= 100:
            if e not in q or rec['filed'] < q[e]['filed']: q[e] = rec
        elif 350 <= dur <= 380:
            if e not in fy or rec['filed'] < fy[e]['filed']: fy[e] = rec
    for fe, f in fy.items():                                   # derive missing fiscal Q4
        if fe in q: continue
        inside = [v for e, v in q.items() if f['start'] <= e < fe]
        if len(inside) == 3:
            q[fe] = dict(start=max(v['end'] for v in inside), end=fe, filed=f['filed'], val=f['val'] - sum(v['val'] for v in inside), derived=True)
    df = pd.DataFrame(q).T.sort_values('end').reset_index(drop=True)
    df['val'] = df['val'].astype(float)
    for c in ('start', 'end', 'filed'): df[c] = pd.to_datetime(df[c])
    df = df.sort_values('end').reset_index(drop=True)
    df['derived'] = df['derived'].eq(True) if 'derived' in df else False
    vals = df['val'].values; lumpy = []                       # v3: two-sided test — a monotone ramp is not lumpy
    for i in range(len(vals)):
        nb = np.abs(np.concatenate([vals[max(0, i-4):i], vals[i+1:i+5]]))
        med = np.median(nb) if len(nb) >= 3 else np.nan
        r = abs(vals[i]) / med if (med and med >= 0.10) else np.nan
        lumpy.append(bool(r > 3.0 or r < 0.3) if not np.isnan(r) else False)
    df['lumpy'] = lumpy
    return df

eps = {n: edgar_eps(n, CIK[n]) for n in NAMES if n in CIK}
print('EDGAR quarters:', {n: len(v) for n, v in eps.items()})
print('LUMPY quarters:', {n: [f"{r.end.date()}={r.val:.2f}" for r in v.itertuples() if r.lumpy] for n, v in eps.items()})

# ---- 3. prices (split-adjusted) + split history ----
px = yf.download(NAMES, start=START, interval='1d', auto_adjust=True, progress=False, threads=True)['Close']
mpx = px.resample('ME').last()

# ---- 4. build monthly point-in-time trailing P/E per name ----
def build(n):
    e = eps[n].copy()
    e['adj'] = e['val']   # already on today's share basis (adjusted at ingest)
    span_ok = (e['end'] - e['end'].shift(3)).dt.days.between(250, 300)   # 4 consecutive quarter-ENDS span ~273 days (v3 fix)
    e['ttm'] = e['adj'].rolling(4).sum().where(span_ok)
    e['ttm_smooth'] = (e['adj'].rolling(4).median() * 4).where(span_ok)   # neutralises ONE lumpy quarter
    e['lumpy_ttm'] = e['lumpy'].rolling(4).max().fillna(0).astype(bool)   # any lumpy quarter inside the TTM
    e = e.dropna(subset=['ttm'])
    rows = []
    for m, p in mpx[n].dropna().items():
        avail = e[e['filed'] <= m]
        if avail.empty or math.isnan(p): continue
        last = avail.iloc[-1]
        ttm = last['ttm']
        sm = last['ttm_smooth']
        rows.append(dict(m=m, px=float(p), ttm=float(ttm), pe=(float(p)/ttm if ttm > 0 else np.nan),
                         pe_smooth=(float(p)/sm if sm > 0 else np.nan), lumpy=bool(last['lumpy_ttm']), q=avail.index[-1]))
    if not rows:
        print(f'⚠️ {n}: no usable months'); return None
    d = pd.DataFrame(rows).set_index('m')
    d['fwd12'] = d['px'].shift(-12) / d['px'] - 1
    d['pe12'] = d['pe'].shift(-12)
    d['ttm12'] = d['ttm'].shift(-12)
    d['hind_fpe'] = d['px'] / d['ttm12'].where(d['ttm12'] > 0)          # hindsight-forward P/E
    d['eps_g'] = d['ttm12'] / d['ttm'] - 1                                # EPS growth over the window
    d['mult_g'] = d['pe12'] / d['pe'] - 1                                 # multiple change over the window
    return d

def pct_rank(series, v):
    s = series.dropna()
    return 100 * (s < v).mean() if len(s) else np.nan

def fmt_pe(v): return 'n/m' if (v is None or (isinstance(v, float) and (math.isnan(v) or v <= 0)) or v > 999) else f'{v:.0f}x'

print('\n' + '=' * 118)
print('WHERE WERE THEY BEFORE THEY RIPPED — trailing P/E at the START of forward-12m windows, by return decile')
print('=' * 118)
print(f'{"NAME":6}{"months":>7}{"TOP-DECILE start P/E":>26}{"BOTTOM-DECILE start P/E":>27}{"ALL months P/E":>18}{"top-dec ret":>12}{"bot-dec ret":>12}')
summary = {}
for n in NAMES:
    if n not in eps: continue
    d = build(n)
    if d is None: continue
    summary[n] = d
    v = d.dropna(subset=['fwd12'])
    top = v[v['fwd12'] >= v['fwd12'].quantile(.9)]; bot = v[v['fwd12'] <= v['fwd12'].quantile(.1)]
    def iqr(s):
        s = s.dropna(); s = s[s > 0]
        return f'{s.median():.0f}x [{s.quantile(.25):.0f}-{s.quantile(.75):.0f}]' if len(s) else 'n/m'
    print(f'{n:6}{len(v):>7}{iqr(top["pe"]):>26}{iqr(bot["pe"]):>27}{iqr(v["pe"]):>18}{top["fwd12"].median()*100:>+11.0f}%{bot["fwd12"].median()*100:>+11.0f}%')
print('\n  Read: if the TOP-DECILE column is LOWER than ALL → the name tends to rip from a cheaper-than-usual multiple.')
print('        if it is HIGHER → the rips start from a trough-earnings high multiple (the DECOMP below will show EPS did the work).')

print('\n' + '=' * 118)
print(f'THE TOP {TOPN_WINDOWS} NON-OVERLAPPING 12-MONTH RIPS PER NAME — and what you were paying at the start')
print('=' * 118)
print(f'{"NAME":6}{"start":>9}{"P/E@start":>11}{"hind-fwdP/E":>12}{"12m ret":>9}{"EPS growth":>12}{"multiple Δ":>12}   read')
for n, d in summary.items():
    v = d.dropna(subset=['fwd12']).copy()
    picks = []
    while len(picks) < TOPN_WINDOWS and not v.empty:
        i = v['fwd12'].idxmax(); r = v.loc[i]; picks.append((i, r))
        v = v[(v.index < i - pd.DateOffset(months=12)) | (v.index > i + pd.DateOffset(months=12))]
    for i, r in picks:
        eg, mg = r['eps_g'], r['mult_g']
        driver = ('EARNINGS' if (not math.isnan(eg) and not math.isnan(mg) and eg > mg) else 'MULTIPLE') if not (math.isnan(eg) or math.isnan(mg)) else '?'
        print(f'{n:6}{i.strftime("%Y-%m"):>9}{fmt_pe(r["pe"]):>11}{fmt_pe(r["hind_fpe"]):>12}{r["fwd12"]*100:>+8.0f}%{(eg*100 if not math.isnan(eg) else float("nan")):>+11.0f}%{(mg*100 if not math.isnan(mg) else float("nan")):>+11.0f}%   {driver}-driven')
print('\n  EPS growth = trailing-4Q EPS 12m later ÷ at start − 1.  multiple Δ = P/E 12m later ÷ P/E at start − 1.  (1+ret)=(1+EPSg)(1+multΔ).')

print('\n' + '=' * 118)
print('WHERE THEY ARE NOW — current trailing P/E vs the name\'s own history')
print('=' * 118)
print(f'{"NAME":6}{"price":>9}{"TTM EPS":>9}{"P/E now":>9}{"pctile":>8}{"median P/E":>11}{"TOP-DEC median":>15}{"EPS trend 4Q/prior4Q":>22}   last EPS quarter filed')
for n, d in summary.items():
    last = d.iloc[-1]; e = eps[n]
    ttm_now = last['ttm']; prior = e['val'].rolling(4).sum().iloc[-5] if len(e) >= 8 else np.nan
    v = d.dropna(subset=['fwd12']); top = v[v['fwd12'] >= v['fwd12'].quantile(.9)]
    trend = (ttm_now / prior - 1) if (prior and prior > 0) else np.nan
    lum = ' ⚠LUMPY' if last['lumpy'] else ''
    print(f'{n:6}{last["px"]:>9.2f}{ttm_now:>9.2f}{fmt_pe(last["pe"]):>9}{pct_rank(d["pe"], last["pe"]):>7.0f}%{fmt_pe(d["pe"].median()):>11}{fmt_pe(top["pe"].median()):>15}{(trend*100 if not math.isnan(trend) else float("nan")):>+21.0f}%   {e["end"].iloc[-1].date()} (filed {e["filed"].iloc[-1].date()})  smoothed P/E {fmt_pe(last["pe_smooth"])}{lum}')
print('\n  ⚠LUMPY = a one-off quarter sits inside the trailing 4Q (GAAP). Use the SMOOTHED P/E (4× median quarter) for those names.')
print('  pctile = where today\'s P/E sits in the name\'s own 2008→ history (100 = most expensive it has ever been on trailing GAAP).')
print('  Compare "P/E now" to "TOP-DEC median": the multiple this name has historically ripped FROM. Then check EPS trend —')
print('  a P/E far above its rip-median with EPS trend NEGATIVE is the trough pattern (multiple high because E fell);')
print('  a P/E far above its rip-median with EPS trend POSITIVE is simply expensive on rising earnings.')
for n, d in summary.items(): d.to_csv(f'{n}_pe_history.csv')
print('\nsaved <NAME>_pe_history.csv per name')
