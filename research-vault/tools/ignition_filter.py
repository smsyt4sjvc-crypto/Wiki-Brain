# IGNITION FILTER — "intact wreckage" (strict mold from runner_anatomy, 2026-07-10)
# Gates: dd<=-50% vs 2y high | mcap $0.2-10B | 0<PE<15 | FCF+ | revenue growing
# Necessary-profile, NOT sufficient: the study conditioned on winners; value traps
# pass too. Name-level "is the business intact" work required per survivor.
# Re-run DURING panic windows — that's when the list gets long and the study says
# runners are born. Tiebreaker: insider cluster buys (OpenInsider cell).
import pandas as pd, requests, yfinance as yf
from io import StringIO

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
tk = []
for u in ["List_of_S%26P_500_companies", "List_of_S%26P_400_companies", "List_of_S%26P_600_companies"]:
    html = requests.get(f"https://en.wikipedia.org/wiki/{u}", headers=UA, timeout=30).text
    tk += [str(t).replace(".", "-").strip() for t in pd.read_html(StringIO(html))[0]["Symbol"]]
tk = sorted(set(tk))

px = yf.download(tk, period="2y", auto_adjust=True, progress=False)["Close"].dropna(axis=1, how="all")
dd = px.iloc[-1] / px.max() - 1
crushed = dd[dd <= -0.50].sort_values()            # GATE 1 — the one that matters most
print(f"{len(crushed)} names >=50% below 2y high\n")

rows = []
for t in crushed.index:                             # .info only for the crushed few
    try:
        i = yf.Ticker(t).info
    except Exception:
        continue
    mc, fcf = i.get("marketCap"), i.get("freeCashflow")
    rows.append({"ticker": t, "dd%": round(crushed[t] * 100),
                 "mcap_B": round((mc or 0) / 1e9, 1),
                 "PE": i.get("trailingPE"),
                 "FCFy%": round(fcf / mc * 100, 1) if (fcf and mc) else None,
                 "revG%": round(i["revenueGrowth"] * 100, 1) if i.get("revenueGrowth") is not None else None,
                 "sector": i.get("sector")})
df = pd.DataFrame(rows)

mold = df[df["mcap_B"].between(0.2, 10) & df["PE"].between(0, 15)
          & (df["FCFy%"] > 0) & (df["revG%"] > 0)]
print("=== STRICT MOLD (all 5 gates) ===")
print(mold.sort_values("dd%").to_string(index=False))
print("\n=== NEAR MISSES (crushed + profitable, failed one gate) ===")
near = df[df["mcap_B"].between(0.2, 10) & df["PE"].between(0, 20)].drop(mold.index, errors="ignore")
print(near.sort_values("dd%").to_string(index=False))
