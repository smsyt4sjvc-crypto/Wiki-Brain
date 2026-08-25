# DENSE INSIDER PULL — full Form 4 detail from EDGAR (primary source), any tickers, any window.
# Built 2026-07-11 consolidating the scattered chat cells. Per filing: owner, title, transaction
# code, $ value, and the 10b5-1 checkbox (auto-separates scheduled comp sales from discretionary).
# Cluster read: distinct discretionary buyers in window = the MTDR-signature detector.
import requests, time, re
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import date, timedelta

EMAIL = "your_email@example.com"                  # EDGAR requires real contact
H = {"User-Agent": f"Jake research {EMAIL}"}
TICKERS = ["ENS", "VICR", "TTMI", "CME", "HII", "GTM"]   # <- edit
DAYS = 30                                          # lookback window
SINCE = (date.today() - timedelta(days=DAYS)).isoformat()

CODES = {"P": "BUY (open mkt)", "S": "SELL", "A": "grant/award", "M": "option exercise",
         "F": "tax withholding", "G": "gift", "D": "disposition to issuer", "C": "conversion"}

cm = requests.get("https://www.sec.gov/files/company_tickers.json", headers=H, timeout=30).json()
cik = {v["ticker"]: str(v["cik_str"]).zfill(10) for v in cm.values()}

def txt(el, path):
    e = el.find(path)
    return e.text.strip() if e is not None and e.text else None

all_rows = []
for t in TICKERS:
    c = cik.get(t)
    if not c:
        print(f"{t}: no CIK"); continue
    sub = requests.get(f"https://data.sec.gov/submissions/CIK{c}.json", headers=H, timeout=30).json()
    time.sleep(0.12)
    rec = sub["filings"]["recent"]
    f4s = [(rec["accessionNumber"][i], rec["filingDate"][i], rec["primaryDocument"][i])
           for i in range(len(rec["form"]))
           if rec["form"][i] == "4" and rec["filingDate"][i] >= SINCE]
    for acc, fdate, pdoc in f4s:
        url = f"https://www.sec.gov/Archives/edgar/data/{int(c)}/{acc.replace('-','')}/{pdoc.split('/')[-1]}"
        try:
            x = requests.get(url, headers=H, timeout=30).text
            time.sleep(0.12)
            root = ET.fromstring(re.sub(r"<\?xml[^>]*\?>", "", x, count=1))
        except Exception as e:
            print(f"  {t} {acc}: parse fail {str(e)[:40]}"); continue
        owner = txt(root, ".//reportingOwner/reportingOwnerId/rptOwnerName") or "?"
        rel = root.find(".//reportingOwner/reportingOwnerRelationship")
        title = (txt(rel, "officerTitle") or
                 ("Director" if txt(rel, "isDirector") in ("1", "true") else "") or
                 ("10%+ owner" if txt(rel, "isTenPercentOwner") in ("1", "true") else "?"))
        plan = txt(root, ".//aff10b5One") in ("1", "true")   # 10b5-1 checkbox (2023+)
        for tr in root.findall(".//nonDerivativeTransaction"):
            code = txt(tr, "transactionCoding/transactionCode")
            sh = txt(tr, "transactionAmounts/transactionShares/value")
            pr = txt(tr, "transactionAmounts/transactionPricePerShare/value")
            ad = txt(tr, "transactionAmounts/transactionAcquiredDisposedCode/value")
            if not (code and sh):
                continue
            all_rows.append({"ticker": t, "filed": fdate, "owner": owner[:26], "title": title[:24],
                             "code": code, "what": CODES.get(code, code), "A/D": ad,
                             "shares": float(sh), "price": float(pr) if pr else None,
                             "value_$": round(float(sh) * float(pr or 0)),
                             "10b5-1": "YES" if plan else ""})
    print(f"{t}: {len(f4s)} Form 4s parsed")

df = pd.DataFrame(all_rows)
if len(df):
    print("\n=== FULL DETAIL ===")
    print(df.sort_values(["ticker", "filed"]).to_string(index=False))
    print("\n=== SUMMARY (discretionary only — 10b5-1 excluded) ===")
    disc = df[df["10b5-1"] != "YES"]
    for t in df.ticker.unique():
        d = disc[disc.ticker == t]
        buys = d[d.code == "P"]; sells = d[d.code == "S"]
        planned = df[(df.ticker == t) & (df["10b5-1"] == "YES") & (df.code == "S")]["value_$"].sum()
        b_sum, s_sum, n_buyers = buys["value_$"].sum(), sells["value_$"].sum(), buys.owner.nunique()
        cluster = " <-- CLUSTER" if n_buyers >= 3 else ""
        print(f"{t}: disc buys ${b_sum:,} ({n_buyers} distinct buyers{cluster}) | "
              f"disc sells ${s_sum:,} | scheduled 10b5-1 sells ${planned:,}")
else:
    print("no transactions in window")
