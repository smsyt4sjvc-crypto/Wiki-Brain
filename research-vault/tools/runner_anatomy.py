# =====================================================================
# RUNNER ANATOMY — every 200%+ 12-month run since 2020: what did they
# look like at IGNITION? (Colab, free: yfinance + Wikipedia + SEC EDGAR
# + OpenInsider). Built 2026-07-10 for Jake's challenge.
#
# CELL 1: find the runs (universe -> rolling 252d return >= 200% -> episodes)
# CELL 2: fundamentals AT RUN START from EDGAR filings (P/E, FCF, rev,
#         capex, buybacks, shares) + drawdown-from-prior-high
# CELL 3: insider Form-4 activity in the 6 months BEFORE each start
#         (OpenInsider; optional, slowest)
# CELL 4: commonality table
#
# ⚠️ SURVIVORSHIP: universe = CURRENT S&P 500/400/600 members. Runners
# that later collapsed/delisted (many 2021 meme names) are invisible.
# Read results as "what index-quality 3x runners looked like," not all.
# =====================================================================

# ---------------------------------------------------------------------
# CELL 1 — universe + run detection
# ---------------------------------------------------------------------
import pandas as pd, numpy as np, requests, time, json, re
from io import StringIO
import yfinance as yf

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
WIKI = {
    "sp500": "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
    "sp400": "https://en.wikipedia.org/wiki/List_of_S%26P_400_companies",
    "sp600": "https://en.wikipedia.org/wiki/List_of_S%26P_600_companies",
}
UNIVERSE = ["sp500", "sp400", "sp600"]   # trim to ["sp500"] for a fast first pass

tickers = []
for u in UNIVERSE:
    html = requests.get(WIKI[u], headers=UA, timeout=30).text
    for t in pd.read_html(StringIO(html))[0]["Symbol"]:
        tickers.append(str(t).replace(".", "-").strip())
tickers = sorted(set(tickers))
print(f"universe: {len(tickers)} tickers")

px = yf.download(tickers, start="2019-01-01", auto_adjust=True,
                 progress=True, threads=True)["Close"]
px = px.dropna(axis=1, how="all")
print(f"prices: {px.shape[1]} names, {px.index[0].date()} -> {px.index[-1].date()}")

THRESH, LOOKBACK = 2.0, 252          # 200% over 12 months
events = []
for t in px.columns:
    s = px[t].dropna()
    if len(s) < LOOKBACK + 60:
        continue
    r = s / s.shift(LOOKBACK) - 1
    sig = r[r >= THRESH]
    sig = sig[sig.index >= "2020-01-01"]
    if sig.empty:
        continue
    # split signal days into episodes (gap > 180 calendar days = new run)
    gaps = sig.index.to_series().diff().dt.days.fillna(0)
    ep_id = (gaps > 180).cumsum()
    for _, ep in sig.groupby(ep_id):
        first_cross = ep.index[0]
        pre = s.loc[:first_cross].iloc[-(LOOKBACK + 1):]
        start_date = pre.idxmin()           # run start = low before the cross
        start_px = float(s.loc[start_date])
        seg = s.loc[start_date:ep.index[-1]]
        peak_date = seg.idxmax()
        events.append({
            "ticker": t, "start": start_date.date(), "cross": first_cross.date(),
            "peak": peak_date.date(), "start_px": round(start_px, 2),
            "max_12m_ret%": round(float(r.loc[ep.index].max()) * 100, 0),
            "start_to_peak%": round((float(s.loc[peak_date]) / start_px - 1) * 100, 0),
            # cheapness-by-price: how far below prior 2y high was it at start?
            "drawdown_at_start%": round(
                (start_px / float(s.loc[:start_date].iloc[-504:].max()) - 1) * 100, 0),
        })

ev = pd.DataFrame(events).sort_values("max_12m_ret%", ascending=False).reset_index(drop=True)
print(f"\n{len(ev)} run events across {ev.ticker.nunique()} tickers")
print(ev.head(40).to_string())
ev["start_q"] = pd.PeriodIndex(pd.to_datetime(ev["start"]), freq="Q").astype(str)
print("\nWHEN runs ignited (event count by start quarter):")
print(ev["start_q"].value_counts().sort_index().to_string())

# ---------------------------------------------------------------------
# CELL 2 — fundamentals AT START from EDGAR (last fiscal year filed
# before the run began) + split-safe market cap
# ---------------------------------------------------------------------
EMAIL = "your_email@example.com"        # EDGAR requires a real contact UA
EHEAD = {"User-Agent": f"Jake research {EMAIL}"}

cikmap = {d["ticker"]: str(d["cik_str"]).zfill(10)
          for d in requests.get("https://www.sec.gov/files/company_tickers.json",
                                headers=EHEAD, timeout=30).json().values()}

TAGS = {
    "rev":  ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax",
             "SalesRevenueNet", "RevenueFromContractWithCustomerIncludingAssessedTax"],
    "ni":   ["NetIncomeLoss"],
    "ocf":  ["NetCashProvidedByUsedInOperatingActivities"],
    "capex":["PaymentsToAcquirePropertyPlantAndEquipment"],
    "bb":   ["PaymentsForRepurchaseOfCommonStock"],
}

def fy_value(facts, tags, asof, prior=False):
    """FY (10-K, ~330-380d duration) value ending on/before asof; prior= one FY earlier."""
    rows = []
    gaap = facts.get("facts", {}).get("us-gaap", {})
    for tag in tags:
        for unit in gaap.get(tag, {}).get("units", {}).values():
            for f in unit:
                if f.get("form") != "10-K" or "start" not in f or not f.get("end"):
                    continue
                d = (pd.Timestamp(f["end"]) - pd.Timestamp(f["start"])).days
                if 330 <= d <= 380 and pd.Timestamp(f["end"]) <= asof:
                    rows.append((f["end"], f["val"]))
        if rows:
            break
    if not rows:
        return None, None
    ends = sorted({e for e, _ in rows})
    pick = ends[-2] if (prior and len(ends) > 1) else ends[-1]
    return dict(rows)[pick], pick

def shares_at(facts, asof):
    out = []
    for unit in facts.get("facts", {}).get("dei", {}) \
                     .get("EntityCommonStockSharesOutstanding", {}) \
                     .get("units", {}).values():
        out += [(f["end"], f["val"]) for f in unit
                if f.get("end") and pd.Timestamp(f["end"]) <= asof + pd.Timedelta(days=45)]
    return sorted(out)[-1][1] if out else None

rows, cache = [], {}
for _, e in ev.iterrows():
    t, asof = e.ticker, pd.Timestamp(e.start)
    cik = cikmap.get(t.replace("-", ""), cikmap.get(t))
    if not cik:
        continue
    if cik not in cache:
        r = requests.get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json",
                         headers=EHEAD, timeout=30)
        cache[cik] = r.json() if r.ok else {}
        time.sleep(0.15)
    fx = cache[cik]
    if not fx:
        continue
    rev,  _ = fy_value(fx, TAGS["rev"], asof)
    rev0, _ = fy_value(fx, TAGS["rev"], asof, prior=True)
    ni,   _ = fy_value(fx, TAGS["ni"], asof)
    ocf,  _ = fy_value(fx, TAGS["ocf"], asof)
    cap,  _ = fy_value(fx, TAGS["capex"], asof)
    bb,   _ = fy_value(fx, TAGS["bb"], asof)
    sh = shares_at(fx, asof)
    # split-safe mcap: EDGAR shares (then-basis) x split factor since -> today-basis
    try:
        spl = yf.Ticker(t).splits
        factor = float(spl[spl.index > asof.tz_localize(spl.index.tz)].prod()) if len(spl) else 1.0
    except Exception:
        factor = 1.0
    factor = factor or 1.0
    mcap = e.start_px * sh * factor if sh else None
    fcf = (ocf - cap) if (ocf is not None and cap is not None) else None
    rows.append({
        "ticker": t, "start": e.start, "max_12m_ret%": e["max_12m_ret%"],
        "drawdown_at_start%": e["drawdown_at_start%"],
        "mcap_$B": round(mcap / 1e9, 2) if mcap else None,
        "trail_PE": round(mcap / ni, 1) if (mcap and ni and ni > 0) else None,
        "NI_neg": bool(ni is not None and ni <= 0),
        "P/S": round(mcap / rev, 2) if (mcap and rev) else None,
        "FCF_yield%": round(fcf / mcap * 100, 1) if (fcf is not None and mcap) else None,
        "rev_yoy%": round((rev / rev0 - 1) * 100, 1) if (rev and rev0) else None,
        "capex/rev%": round(cap / rev * 100, 1) if (cap and rev) else None,
        "buyback/mcap%": round(bb / mcap * 100, 1) if (bb and mcap) else None,
    })
    print(f"{t} {e.start} ok", end="  ")

fund = pd.DataFrame(rows)
print("\n\n", fund.to_string())

# ---------------------------------------------------------------------
# CELL 3 (optional, slow) — insider Form 4s in the 6 months BEFORE start
# OpenInsider works from Colab; sleep to be polite. Trim N_TOP if needed.
# ---------------------------------------------------------------------
N_TOP = 60
ins_rows = []
for _, e in ev.head(N_TOP).iterrows():
    t = e.ticker
    d1 = (pd.Timestamp(e.start) - pd.Timedelta(days=183)).strftime("%m/%d/%Y")
    d2 = pd.Timestamp(e.start).strftime("%m/%d/%Y")
    url = (f"http://openinsider.com/screener?s={t}&fd=-1"
           f"&fdr={d1.replace('/', '%2F')}+-+{d2.replace('/', '%2F')}&cnt=100")
    try:
        html = requests.get(url, headers=UA, timeout=30).text
        tabs = pd.read_html(StringIO(html))
        tab = next((x for x in tabs if x.shape[1] > 8), None)
        if tab is None:
            ins_rows.append({"ticker": t, "start": e.start, "buys_$": 0, "sells_$": 0, "n_buys": 0})
            continue
        tab.columns = [str(c).replace("\xa0", " ").strip() for c in tab.columns]
        tcol = next(c for c in tab.columns if "Trade Type" in c or "Type" in c)
        vcol = next(c for c in tab.columns if "Value" in c)
        val = (tab[vcol].astype(str).str.replace(r"[\$,+()]", "", regex=True)
               .replace("", "0").astype(float))
        buys = val[tab[tcol].astype(str).str.contains("P - Purchase", na=False)]
        sells = val[tab[tcol].astype(str).str.contains("S - Sale", na=False)]
        ins_rows.append({"ticker": t, "start": e.start,
                         "buys_$": int(buys.sum()), "sells_$": int(sells.sum()),
                         "n_buys": int(len(buys))})
    except Exception as ex:
        ins_rows.append({"ticker": t, "start": e.start, "buys_$": None,
                         "sells_$": None, "n_buys": None})
    time.sleep(1.5)
    print(t, end=" ")

ins = pd.DataFrame(ins_rows)
print("\n", ins.to_string())

# ---------------------------------------------------------------------
# CELL 4 — commonality summary (what do ignitions share?)
# ---------------------------------------------------------------------
df = fund.copy()
if "ins" in dir() and len(ins):
    df = df.merge(ins.drop(columns=["start"]), on="ticker", how="left")

def pct(mask):
    m = mask.dropna() if hasattr(mask, "dropna") else mask
    return f"{100 * m.mean():.0f}%" if len(m) else "n/a"

print(f"\n===== COMMONALITY — {len(df)} run events =====")
print(f"drawdown at start: median {df['drawdown_at_start%'].median():.0f}% | "
      f">30% below prior high: {pct(df['drawdown_at_start%'] <= -30)} | "
      f">50% below: {pct(df['drawdown_at_start%'] <= -50)}")
print(f"unprofitable at start (FY NI<=0): {pct(df['NI_neg'])}")
pe = df["trail_PE"].dropna()
print(f"trailing P/E (profitable only, n={len(pe)}): median {pe.median():.1f} | "
      f"<15x: {pct(pe < 15)} | >40x: {pct(pe > 40)}")
print(f"P/S: median {df['P/S'].median():.2f} | <2x: {pct(df['P/S'] < 2)}")
print(f"FCF yield: median {df['FCF_yield%'].median():.1f}% | "
      f"FCF-negative: {pct(df['FCF_yield%'] < 0)}")
print(f"revenue yoy at start: median {df['rev_yoy%'].median():.1f}% | "
      f"shrinking: {pct(df['rev_yoy%'] < 0)} | >25% growth: {pct(df['rev_yoy%'] > 25)}")
print(f"capex/revenue: median {df['capex/rev%'].median():.1f}%")
print(f"buybacks: >1% of mcap in prior FY: {pct(df['buyback/mcap%'] > 1)}")
if "buys_$" in df:
    print(f"insider buying in 6m pre-start: any: {pct(df['n_buys'] > 0)} | "
          f">$1M net: {pct((df['buys_$'] - df['sells_$']) > 1e6)}")
print(f"\nmcap at start: median ${df['mcap_$B'].median():.1f}B | "
      f"<$10B: {pct(df['mcap_$B'] < 10)}")
print("\n'CHEAP' scorecard at ignition — cheap on price (drawdown<=-30%), "
      "cheap on earnings (0<PE<15), cheap on sales (P/S<2):")
cheap_px = df["drawdown_at_start%"] <= -30
cheap_pe = df["trail_PE"].fillna(9999) < 15
cheap_ps = df["P/S"].fillna(9999) < 2
print(f"  price-cheap {pct(cheap_px)} | earnings-cheap {pct(cheap_pe)} | "
      f"sales-cheap {pct(cheap_ps)} | none-of-the-three {pct(~(cheap_px | cheap_pe | cheap_ps))}")
