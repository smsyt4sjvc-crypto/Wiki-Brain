# jevons_beta_decay_cell.py — DOES JAKE'S THESIS PRINT? (Colab cell, complete; Jake-side — yfinance 429s from the container)
# THESIS (Jake, 2026-09-08 3:35pm): "Realized MW volume as efficiency and Jevons outruns token economics.
#   Software that earns revenue in COMPUTE instead of TOKEN economics benefits from Jevons. All summer Nasdaq
#   sold off hard when Iran/oil escalated because everything had insane valuations and there were a lot of
#   unknowns that are now known. The numbers are rolling in. Software and compute volume is carrying."
#
# THREE TESTS, EACH FALSIFIABLE:
#   T1 BETA DECAY  — rolling beta of each basket to (a) the 10Y REAL yield and (b) Brent. If the thesis is right,
#                    beta to BOTH shrinks from CHOP (Jun-Aug) to NOW (Sep). If beta is unchanged, the thesis fails.
#   T2 EVENT STUDY — on OIL-SHOCK and REAL-RATE-SHOCK days only, what did each basket do, by period?
#                    This is the direct form of "all summer Nasdaq sold off hard when oil escalated."
#   T3 EPS vs MULTIPLE — decompose each name's return as (1+ret) = (1+EPS growth)(1+multiple change) using
#                    point-in-time EDGAR TTM EPS. "The numbers are rolling in" predicts EPS-DRIVEN, not multiple-driven.
#
# ⚠️ WHAT THIS CANNOT TEST: the token-denominated seller. OpenAI and Anthropic are private, so there is no public
#    pure-play whose revenue IS tokens. The COMPUTE-SELLERS basket is the testable half of Jake's split; the
#    token-seller half has no listed expression and the cell says so rather than faking a proxy.
# ⚠️ n IS SMALL. Sep-2026 has ~6 trading days at time of writing. Treat NOW as a reading, not a result, until n>20.
#
# RUN: paste into Colab. ~1-2 min. Paste the printed output back into chat.

import subprocess, sys, io, urllib.request, json, time, warnings
warnings.filterwarnings('ignore')
try:
    import yfinance as yf, pandas as pd, numpy as np
except Exception:
    subprocess.run([sys.executable,'-m','pip','install','-q','yfinance','pandas','numpy'])
    import yfinance as yf, pandas as pd, numpy as np

START = '2024-01-01'
PERIODS = [('PRE  Jan-May 26','2026-01-01','2026-05-31'),
           ('CHOP Jun-Aug 26','2026-06-01','2026-08-31'),
           ('NOW  Sep 26'    ,'2026-09-01','2026-12-31')]
ROLL = 45                      # trading days in the rolling beta
OIL_SHOCK  = 0.02              # Brent daily >= +2%
REAL_SHOCK = 5.0               # 10Y real yield daily >= +5bp

BASKETS = {
 'SEMIS'          : ['NVDA','AVGO','MU','TSM','AMAT','LRCX','KLAC'],
 'COMPUTE-SELLERS': ['ORCL','CRWV','IREN','NBIS'],          # revenue denominated in COMPUTE (Jake's category)
 'SOFTWARE'       : ['MSFT','NOW','CRM','PLTR','ADBE'],     # revenue in seats/outcomes, COGS falls as tokens cheapen
 'MEGACAP'        : ['AAPL','GOOGL','META','AMZN'],
 'OLD-ECON'       : ['CAT','DE','UPS','FDX','DAL','WMT'],   # oil is a COST here — the control for T2
}
INDICES = ['QQQ','SPY','DIA','IGV','SOXX','XLE','XLI']
ALL_TK  = sorted(set(sum(BASKETS.values(), []) + INDICES))

# ---------------- FRED ----------------
def fred(ids):
    out = {}
    for sid in ids:
        try:
            u = f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}'
            raw = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent':'Mozilla/5.0'}), timeout=30).read()
            d = pd.read_csv(io.BytesIO(raw))
            d.columns = ['DATE','V']
            d['DATE'] = pd.to_datetime(d['DATE'])
            d['V'] = pd.to_numeric(d['V'], errors='coerce')
            out[sid] = d.dropna().set_index('DATE')['V']
            print(f'  FRED {sid}: {len(out[sid])} obs, last {out[sid].index[-1].date()} = {out[sid].iloc[-1]}')
        except Exception as e:
            print(f'  ⚠️ FRED {sid} failed: {str(e)[:60]}')
    return out

print('Fetching FRED…')
F = fred(['DFII10','DFII30','DGS10','T10YIE','DCOILBRENTEU'])
real10 = F.get('DFII10'); brent = F.get('DCOILBRENTEU')
if real10 is None: raise SystemExit('DFII10 unavailable — cannot run T1/T2.')

print('\nFetching prices…')
px = yf.download(ALL_TK, start=START, auto_adjust=True, progress=False, threads=True)['Close']
px = px.dropna(axis=1, how='all')
missing = [t for t in ALL_TK if t not in px.columns]
if missing: print('  ⚠️ no price data:', ', '.join(missing))
px.index = pd.to_datetime(px.index).tz_localize(None)
ret = px.pct_change()

# basket = equal-weight mean of available members
bask = pd.DataFrame(index=ret.index)
for name, mem in BASKETS.items():
    have = [t for t in mem if t in ret.columns]
    if have: bask[name] = ret[have].mean(axis=1)
for t in INDICES:
    if t in ret.columns: bask[t] = ret[t]

# factors, aligned to trading days
d_real = real10.reindex(bask.index, method='ffill').diff() * 100.0        # bp/day
d_oil  = brent.reindex(bask.index, method='ffill').pct_change() if brent is not None else pd.Series(index=bask.index, dtype=float)
X = pd.DataFrame({'dreal_bp': d_real, 'doil': d_oil}).reindex(bask.index)

def slice_(df, a, b): return df.loc[(df.index >= a) & (df.index <= b)]

# ---------------- T1 — BETA BY PERIOD ----------------
print('\n' + '='*104)
print('T1  BETA TO THE FACTORS, BY PERIOD   (regression of daily basket return on the daily factor change)')
print('    beta_real = % move per +1bp in the 10Y REAL yield   |   beta_oil = % move per +1% in Brent')
print("    JAKE'S PREDICTION: both betas shrink toward zero from CHOP to NOW.")
print('='*104)
hdr = f'{"BASKET":18}'
for lbl,_,_ in PERIODS: hdr += f'{lbl:>26}'
print(hdr); print(f'{"":18}' + ''.join(f'{"beta_real  beta_oil   n":>26}' for _ in PERIODS))
def beta(y, x):
    d = pd.concat([y, x], axis=1).dropna()
    if len(d) < 8: return np.nan, len(d)
    yy, xx = d.iloc[:,0].values, d.iloc[:,1].values
    if np.std(xx) == 0: return np.nan, len(d)
    return float(np.polyfit(xx, yy, 1)[0]), len(d)
for col in list(BASKETS.keys()) + INDICES:
    if col not in bask.columns: continue
    line = f'{col:18}'
    for lbl, a, b in PERIODS:
        y = slice_(bask[col], a, b); xr = slice_(X['dreal_bp'], a, b); xo = slice_(X['doil'], a, b)
        br, n1 = beta(y, xr); bo, _ = beta(y, xo)
        line += f'{(br*100 if br==br else float("nan")):>9.3f}{(bo*100 if bo==bo else float("nan")):>10.2f}{n1:>7}'
    print(line)
print('  (beta_real in %-move per bp ×100 = basis points of equity move per bp of real yield; beta_oil in % per %.)')

# ---------------- T2 — EVENT STUDY ----------------
print('\n' + '='*104)
print(f'T2  SHOCK-DAY EVENT STUDY   (OIL shock = Brent >= +{OIL_SHOCK*100:.0f}% ; REAL shock = 10Y real >= +{REAL_SHOCK:.0f}bp)')
print("    JAKE'S CLAIM: 'all summer Nasdaq sold off hard when Iran/oil escalated' — and it has stopped.")
print('='*104)
for shock_name, mask_all in [('OIL SHOCK', X['doil'] >= OIL_SHOCK), ('REAL-RATE SHOCK', X['dreal_bp'] >= REAL_SHOCK)]:
    print(f'\n{shock_name} DAYS — mean basket return on those days (%)')
    hdr = f'{"BASKET":18}'
    for lbl,_,_ in PERIODS: hdr += f'{lbl:>18}'
    print(hdr)
    counts = []
    for lbl, a, b in PERIODS:
        m = mask_all & (X.index >= a) & (X.index <= b)
        counts.append(int(m.sum()))
    print(f'{"  (n shock days)":18}' + ''.join(f'{c:>18}' for c in counts))
    for col in list(BASKETS.keys()) + INDICES:
        if col not in bask.columns: continue
        line = f'{col:18}'
        for lbl, a, b in PERIODS:
            m = mask_all & (X.index >= a) & (X.index <= b)
            v = bask.loc[m, col].mean() * 100 if m.sum() else float('nan')
            line += f'{v:>+18.2f}'
        print(line)
    print(f'{"SPREAD QQQ-DIA":18}' + ''.join(
        f'{((bask.loc[(mask_all)&(bask.index>=a)&(bask.index<=b),"QQQ"].mean() - bask.loc[(mask_all)&(bask.index>=a)&(bask.index<=b),"DIA"].mean())*100 if ((mask_all)&(bask.index>=a)&(bask.index<=b)).sum() else float("nan")):>+18.2f}'
        for _, a, b in PERIODS) + '   <-- positive = Nasdaq OUTPERFORMS on shock days')

# ---------------- T1b — ROLLING BETA PATH ----------------
print('\n' + '='*104)
print(f'T1b ROLLING {ROLL}-DAY BETA TO THE 10Y REAL YIELD — month-end readings (bp of equity move per bp of real)')
print('='*104)
roll_cols = [c for c in ['QQQ','IGV','SOXX','SEMIS','SOFTWARE','COMPUTE-SELLERS','DIA','OLD-ECON'] if c in bask.columns]
rb = {}
for c in roll_cols:
    cov = bask[c].rolling(ROLL).cov(X['dreal_bp']); var = X['dreal_bp'].rolling(ROLL).var()
    rb[c] = (cov/var) * 100
rbdf = pd.DataFrame(rb).dropna(how='all')
me = rbdf.loc[rbdf.index >= '2025-09-01'].resample('M').last()
print(f'{"MONTH":10}' + ''.join(f'{c:>17}' for c in roll_cols))
for dt, row in me.iterrows():
    print(f'{dt.strftime("%Y-%m"):10}' + ''.join(f'{row[c]:>17.3f}' if row[c]==row[c] else f'{"":>17}' for c in roll_cols))

# ---------------- T3 — EPS vs MULTIPLE ----------------
print('\n' + '='*104)
print('T3  RETURN DECOMPOSED:  (1+ret) = (1+EPS growth) x (1+multiple change)   — point-in-time EDGAR TTM EPS')
print("    JAKE'S CLAIM: 'the numbers are rolling in' => recent returns should be EPS-DRIVEN, not multiple-driven.")
print('='*104)
CIK = {'NVDA':'0001045810','AVGO':'0001730168','MU':'0000723125','ORCL':'0001341439','MSFT':'0000789019',
       'GOOGL':'0001652044','META':'0001326801','AMZN':'0001018724','AAPL':'0000320193','AMAT':'0000006951',
       'LRCX':'0000707549','KLAC':'0000319201','ADBE':'0000796343','CRM':'0001108524','NOW':'0001373715'}
UA = {'User-Agent':'research-vault contact@example.com'}
def split_adj(tk):
    try:
        s = yf.Ticker(tk).splits
        if s is None or len(s)==0: return pd.Series(dtype=float)
        idx = s.index.tz_localize(None) if s.index.tz is not None else s.index
        return pd.Series(s.values, index=idx)
    except Exception:
        return pd.Series(dtype=float)
def ttm_eps_series(tk, cik):
    try:
        u = f'https://data.sec.gov/api/xbrl/companyconcept/CIK{cik}/us-gaap/EarningsPerShareDiluted.json'
        ents = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30))['units']['USD/shares']
    except Exception as e:
        print(f'  ⚠️ EDGAR {tk}: {str(e)[:50]}'); return None
    sp = split_adj(tk)
    def factor_after(d):
        if len(sp)==0: return 1.0
        sel = sp[sp.index > pd.Timestamp(d)]
        return float(np.prod(sel.values)) if len(sel) else 1.0
    q, fy = {}, {}
    for x in ents:
        if 'start' not in x: continue
        s_, e_, f_ = pd.Timestamp(x['start']), pd.Timestamp(x['end']), pd.Timestamp(x['filed'])
        dur = (e_-s_).days
        rec = dict(start=s_, end=e_, filed=f_, val=float(x['val'])/factor_after(f_))
        if 60 <= dur <= 100:
            if e_ not in q or f_ < q[e_]['filed']: q[e_] = rec
        elif 350 <= dur <= 380:
            if e_ not in fy or f_ < fy[e_]['filed']: fy[e_] = rec
    for fe, fv in fy.items():                       # derive fiscal Q4 = FY - (Q1+Q2+Q3)
        if fe in q: continue
        inside = [v for e_, v in q.items() if fv['start'] <= e_ < fe]
        if len(inside) == 3:
            q[fe] = dict(start=max(v['end'] for v in inside), end=fe, filed=fv['filed'],
                         val=fv['val'] - sum(v['val'] for v in inside))
    if len(q) < 5: return None
    df = pd.DataFrame(q).T.reset_index(drop=True)
    for c in ('start','end','filed'): df[c] = pd.to_datetime(df[c])
    df['val'] = df['val'].astype(float)
    df = df.sort_values('end').reset_index(drop=True)
    span_ok = (df['end'] - df['end'].shift(3)).dt.days.between(250, 300)
    df['ttm'] = df['val'].rolling(4).sum().where(span_ok)
    df = df.dropna(subset=['ttm']).sort_values('filed')
    return df[['filed','ttm']].drop_duplicates('filed', keep='last').set_index('filed')['ttm']

def eps_at(s, d):                                    # last TTM KNOWN as of date d (no look-ahead)
    if s is None: return np.nan
    v = s[s.index <= pd.Timestamp(d)]
    return float(v.iloc[-1]) if len(v) else np.nan
def px_at(tk, d):
    if tk not in px.columns: return np.nan
    v = px[tk][px.index <= pd.Timestamp(d)].dropna()
    return float(v.iloc[-1]) if len(v) else np.nan

names = [t for t in ['NVDA','AVGO','MU','ORCL','MSFT','GOOGL','META','AMZN','AAPL','AMAT','LRCX','KLAC','ADBE','CRM','NOW'] if t in px.columns]
eps_cache = {}
for t in names:
    eps_cache[t] = ttm_eps_series(t, CIK[t]); time.sleep(0.2)
for lbl, a, b in PERIODS:
    b_eff = min(pd.Timestamp(b), px.index[-1])
    print(f'\n{lbl}   ({a} -> {b_eff.date()})')
    print(f'{"NAME":7}{"RET%":>9}{"EPSg%":>9}{"MULTd%":>9}{"P/E0":>8}{"P/E1":>8}   DRIVER')
    rows = []
    for t in names:
        p0, p1 = px_at(t, a), px_at(t, b_eff)
        e0, e1 = eps_at(eps_cache.get(t), a), eps_at(eps_cache.get(t), b_eff)
        if not all(x == x for x in (p0,p1,e0,e1)) or e0 <= 0 or e1 <= 0: 
            print(f'{t:7}{"— insufficient EDGAR/price data —":>50}'); continue
        r = p1/p0 - 1; g = e1/e0 - 1; m = (1+r)/(1+g) - 1
        drv = 'EPS' if abs(g) > abs(m) else 'MULTIPLE'
        rows.append((t, r, g, m))
        print(f'{t:7}{r*100:>+9.1f}{g*100:>+9.1f}{m*100:>+9.1f}{p0/e0:>8.1f}{p1/e1:>8.1f}   {drv}')
    if rows:
        neps = sum(1 for _,_,g,m in rows if abs(g) > abs(m))
        print(f'  => {neps} of {len(rows)} names EPS-DRIVEN | mean EPSg {np.mean([g for _,_,g,_ in rows])*100:+.1f}%  mean MULTd {np.mean([m for _,_,_,m in rows])*100:+.1f}%')

print('\n' + '='*104)
print('HOW TO READ IT')
print("  T1/T1b: if beta_real and beta_oil FALL from CHOP to NOW for QQQ/SOFTWARE/COMPUTE-SELLERS, Jake's")
print('          uncertainty-decay mechanism has evidence. If they are flat, the Dow/Nasdaq split was sector mix.')
print('  T2:     the QQQ-DIA spread on shock days is the direct test. Negative in CHOP and positive in NOW = thesis.')
print('  T3:     EPS-DRIVEN in NOW and MULTIPLE-DRIVEN in CHOP = "the numbers are rolling in", measured.')
print('  ⚠️ n for NOW is tiny. A sign is a reading; a result needs n>20 shock days or another month.')
print('='*104)
