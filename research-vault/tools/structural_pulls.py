# WEEKLY STRUCTURAL PULL — positioning + filings watchlist sweep (manual Colab run, ~5 min)
# Built 2026-07-11. Jake's directive: structural reports/filings > news and shock events.
# NO automation/cron per standing spending rule — run by hand, weekly.
# Cell A: CFTC COT leveraged-fund net positioning (free prime-book proxy; futures, not sectors)
# Cell B: Form 4 tripwire sweep over vault watchlists (3+ filings in 14d -> run form4 detail parser)
# Cell C: short interest snapshot | Cell D: 13F freshness check on tracked managers
import pandas as pd, requests, time
import xml.etree.ElementTree as ET
from datetime import date, timedelta

# ---------------- CELL A (v4: params-encoded — fixes S&P ampersand URL split) ----------------
def cot(dataset, mkt, prefix, label):
    r = requests.get(f"https://publicreporting.cftc.gov/resource/{dataset}.json",
                     params={"$where": f"contract_market_name='{mkt}'",
                             "$order": "report_date_as_yyyy_mm_dd DESC", "$limit": 8}, timeout=30)
    rows = r.json()
    if not rows: print(f"{label}: no rows"); return
    d = pd.DataFrame(rows)
    lc = [c for c in d.columns if prefix in c and "long" in c and not any(x in c for x in ("spread","change","pct"))]
    sc = [c for c in d.columns if prefix in c and "short" in c and not any(x in c for x in ("spread","change","pct"))]
    if not (lc and sc): print(f"{label}: no {prefix} cols"); return
    d["net"] = d[lc[0]].astype(float) - d[sc[0]].astype(float)
    cur, prior = d.net.iloc[0], d.net.iloc[min(4, len(d)-1)]
    print(f"{label} [{mkt}] {d.report_date_as_yyyy_mm_dd.iloc[0][:10]}: net {cur:+,.0f} | 4wk {prior:+,.0f} | delta {cur-prior:+,.0f}")

cot("gpe5-46if", "E-MINI S&P 500", "lev_money", "ES levfunds")
cot("gpe5-46if", "S&P 500 Consolidated", "lev_money", "SPX consol levfunds")
cot("gpe5-46if", "NASDAQ MINI", "lev_money", "NQ levfunds")
cot("72hh-3qpy", "CRUDE OIL, LIGHT SWEET-WTI", "m_money", "CL mgd-money")
cot("72hh-3qpy", "GOLD", "m_money", "GC mgd-money")
# Sector texture (thin volume, read direction only): E-MINI S&P TECHNOLOGY/ENERGY/FINANCIAL/HEALTH CARE INDEX

# ---------------- CELL B ----------------
EMAIL = "your_email@example.com"
H = {"User-Agent": f"Jake research {EMAIL}"}
WATCH = {
 "semi_grid": ["MU","LRCX","AMAT","NVDA","AMD","AVGO","KLAC","TER","ON","MRVL","MPWR","SMCI","WDC","STX","SNDK"],
 "quiet_health": ["PG","GILD","CME","GD","HIG","EA","FFIV","ULTA","GEHC","CBOE","UHS","WRB","CB","HII","CI"],
 "mold_12": ["VRRM","GTM","DUOL","INSP","EPAM","FRPT","BLKB","AMPH","GPK","ADMA","UPWK","WEN"],
 "bottleneck": ["CLF","VICR","VSH","ENS","VECO","AXTI","POWL","STRL","FIX","TTMI"],
}
cm = requests.get("https://www.sec.gov/files/company_tickers.json", headers=H, timeout=30).json()
cik = {v["ticker"]: str(v["cik_str"]).zfill(10) for v in cm.values()}
SINCE = (date.today() - timedelta(days=14)).isoformat()

def sweep(t):
    c = cik.get(t)
    if not c: return None
    sub = requests.get(f"https://data.sec.gov/submissions/CIK{c}.json", headers=H, timeout=30).json()
    r = sub["filings"]["recent"]; time.sleep(0.12)
    return sum(1 for i in range(len(r["form"])) if r["form"][i] == "4" and r["filingDate"][i] >= SINCE)

for group, names in WATCH.items():
    hits = {t: sweep(t) for t in names}
    flagged = {t: n for t, n in hits.items() if n}
    print(f"{group}: {flagged if flagged else 'no Form 4s in 14d'}")

# ---------------- CELL C ----------------
import yfinance as yf
for t in ["MU","NVDA","GPK","FRPT","DUOL","UPWK","VECO","AXTI","ORCL"]:
    i = yf.Ticker(t).info
    spf = i.get("shortPercentOfFloat"); ss, ssp = i.get("sharesShort"), i.get("sharesShortPriorMonth")
    d = f"{(ss/ssp-1)*100:+.0f}% MoM" if ss and ssp else "n/a"
    print(f"{t}: short {spf*100:.1f}% of float | {d}" if spf else f"{t}: n/a")

# ---------------- CELL D ----------------
MANAGERS = {"Scion (Burry)": "0001649339", "Berkshire": "0001067983", "Appaloosa": "0001656456"}
for name, c in MANAGERS.items():
    sub = requests.get(f"https://data.sec.gov/submissions/CIK{c.zfill(10)}.json", headers=H, timeout=30).json()
    r = sub["filings"]["recent"]; time.sleep(0.12)
    f13 = [(r["filingDate"][i], r["accessionNumber"][i]) for i in range(len(r["form"])) if "13F" in r["form"][i]]
    if f13:
        print(f"{name}: latest 13F {f13[0][0]} https://www.sec.gov/Archives/edgar/data/{int(c)}/{f13[0][1].replace('-','')}")
    else:
        print(f"{name}: none")
