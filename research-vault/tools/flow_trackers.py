# flow_trackers.py — free MOSO-equivalent + RVOL tracker for the book's universe.
# Run in Colab (Yahoo/yfinance is walled off the agent container; works in Jake's Colab).
# Two independent cells below — copy the one you want. See wiki/live-flow-trackers.md for the read.
#
# UNIVERSE is the book + watchlist. Edit TICKERS to taste.
# Yahoo data is ~15-min delayed and share counts are STALE (quarterly filings) — read the wiki caveats.

# =============================================================================
# CELL 1 — MOSO (most-traded options): most-active, unusual, call/put skew
# =============================================================================
"""
!pip -q install yfinance --upgrade
import yfinance as yf, pandas as pd
TICKERS = ['SPY','QQQ','MU','NVDA','AMD','TSM','MRVL','AVGO','SMCI','PLTR',
           'NBIS','CRWV','META','GEV','VST','OKLO','SMR']
N_EXP = 4
rows = []
for t in TICKERS:
    try:
        tk = yf.Ticker(t)
        for e in tk.options[:N_EXP]:
            try:
                ch = tk.option_chain(e)
                for typ, df in [('CALL', ch.calls), ('PUT', ch.puts)]:
                    d = df[['strike','lastPrice','volume','openInterest','impliedVolatility']].copy()
                    d['tkr'], d['type'], d['exp'] = t, typ, e
                    rows.append(d)
            except Exception: pass
    except Exception as ex:
        print(f"{t}: fail {ex}")
opt = pd.concat(rows, ignore_index=True)
opt['volume'] = pd.to_numeric(opt['volume'], errors='coerce').fillna(0)
opt['openInterest'] = pd.to_numeric(opt['openInterest'], errors='coerce').fillna(0)
opt['vol/OI'] = (opt['volume'] / opt['openInterest'].replace(0, pd.NA)).round(1)
opt['IV%'] = (opt['impliedVolatility']*100).round(0)
show = ['tkr','type','exp','strike','lastPrice','volume','openInterest','vol/OI','IV%']
print("== MOST ACTIVE (raw volume; 0DTE index = noise) =="); print(opt.sort_values('volume', ascending=False).head(25)[show].to_string(index=False))
print("\n== UNUSUAL (vol>500 & vol/OI>3 = fresh positioning; ignore OI=1) =="); print(opt[(opt['volume']>500)&(opt['vol/OI']>3)&(opt['openInterest']>50)].sort_values('vol/OI', ascending=False).head(25)[show].to_string(index=False))
skew = opt.groupby(['tkr','type'])['volume'].sum().unstack(fill_value=0)
skew['P/C'] = (skew['PUT']/skew['CALL'].replace(0,pd.NA)).round(2)
print("\n== CALL/PUT SKEW (P/C>1 = put-heavy/hedged/bearish) =="); print(skew.sort_values('P/C', ascending=False).to_string())
"""

# =============================================================================
# CELL 2 — RVOL (relative volume) live participation tracker
# RVOL = today's cumulative vol / avg vol at the SAME point in the day, prior sessions.
# 1.0 = on pace, >2 = twice normal (attention arriving), <0.7 = dead.
# Uses 5-min bars -> ~30-day baseline (Yahoo allows 5m ~60d back; 1m capped at 8d).
# =============================================================================
"""
!pip -q install yfinance --upgrade
import yfinance as yf, pandas as pd, numpy as np
TICKERS = ['SPY','QQQ','MU','NVDA','AMD','TSM','MRVL','AVGO','SMCI','PLTR',
           'NBIS','CRWV','META','GEV','VST','OKLO','SMR']
rows = []
for t in TICKERS:
    try:
        tk = yf.Ticker(t)
        h = tk.history(period='30d', interval='5m')   # 5m -> real month baseline
        if h.empty:
            print(f"{t}: no data"); continue
        h['d'] = h.index.date
        days = sorted(h['d'].unique())
        today, prior = days[-1], days[:-1]
        td = h[h['d']==today]
        bars = len(td)
        vol_today = int(td['Volume'].sum())
        last_px = float(td['Close'].iloc[-1])
        same_time = [h[h['d']==d]['Volume'].iloc[:bars].sum()
                     for d in prior if len(h[h['d']==d]) >= bars]
        base = np.mean(same_time) if same_time else np.nan
        rvol = vol_today/base if base and base==base else np.nan
        fi = tk.fast_info
        shares = getattr(fi,'shares',None)
        pct = (vol_today/shares*100) if shares else np.nan
        rows.append({'tkr':t,'px':round(last_px,2),'min':bars*5,'ndays':len(same_time),
                     'vol':vol_today,'avg@time':int(base) if base==base else 0,
                     'RVOL':round(rvol,2) if rvol==rvol else np.nan,
                     '%shs':round(pct,2) if pct==pct else np.nan})
    except Exception as ex:
        print(f"{t}: {ex}")
df = pd.DataFrame(rows).sort_values('RVOL', ascending=False, na_position='last')
print("RVOL = today's vol / avg at this point in day (~30 sess). 1.0=normal, >2=hot. %shs = turnover (STALE denom).\n")
print(df.to_string(index=False))
"""
