# MONDAY FLOWS — where money went last week (manual pre-open Monday run; pairs with
# structural_pulls.py: run this -> COT cell -> Form 4 tripwire. ~20 min total.)
# Built 2026-07-11. No cron per standing spending rule.
import yfinance as yf, pandas as pd, numpy as np

SECTORS = {"XLK":"tech","SMH":"semis","XLE":"energy","XLV":"health","XLF":"fins","XLI":"indus",
           "XLP":"staples","XLY":"discret","XLU":"utes","XLB":"materials","XLRE":"REITs",
           "XLC":"comms","GLD":"gold","USO":"crude","TLT":"20y bond","UUP":"dollar","IBIT":"btc"}
rows = []
for t, name in SECTORS.items():
    h = yf.Ticker(t).history(period="4mo")
    if h.empty: continue
    dv = h.Close * h.Volume
    rows.append({"etf": t, "sector": name,
        "1w%": round((h.Close.iloc[-1]/h.Close.iloc[-6]-1)*100, 1),
        "1m%": round((h.Close.iloc[-1]/h.Close.iloc[-22]-1)*100, 1),
        "$vol_1w_vs_3m": round(dv.iloc[-5:].mean()/dv.iloc[-65:-5].mean(), 2)})
d = pd.DataFrame(rows).sort_values("1w%", ascending=False)
print(d.to_string(index=False))
print("\nREAD: 1w% = direction | $vol ratio = conviction (>1.3 = money moving).")

import requests
from io import StringIO
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
html = requests.get("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies", headers=UA, timeout=30).text
tickers = [str(t).replace(".", "-") for t in pd.read_html(StringIO(html))[0]["Symbol"]]
px = yf.download(tickers, period="4mo", auto_adjust=True, progress=False)
close, vol = px["Close"], px["Volume"]
dv = close * vol
ret1w = (close.iloc[-1]/close.iloc[-6]-1)*100
flow = (dv.iloc[-5:].mean()/dv.iloc[-65:-5].mean()).replace([np.inf], np.nan)
f = pd.DataFrame({"1w%": ret1w.round(1), "flow_x": flow.round(2)}).dropna()
hot = f[f.flow_x > 1.5].copy()
hot["signed"] = hot.flow_x * np.sign(hot["1w%"])
ins, outs = hot[hot["1w%"] > 0], hot[hot["1w%"] < 0]
print(f"MONEY IN (abnormal volume, up) — {len(ins)} names:")
print(ins.nlargest(12, "flow_x").to_string() if len(ins) else "  NONE — no abnormal-volume accumulation this week (itself a signal: drift, not buying)")
print(f"\nMONEY OUT (abnormal volume, down) — {len(outs)} names:")
print(outs.nlargest(12, "flow_x").to_string() if len(outs) else "  NONE")
