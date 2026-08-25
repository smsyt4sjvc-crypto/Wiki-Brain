# sp500_health_screen.py — S&P 500 quiet-health screen: quality-adjusted cheapness, no story.
# Run in Colab (~15-25 min for Cell 1; yfinance walled off the agent container).
# Design: raw lowest-P/E sort = value-trap list (peak-cycle E, ice cubes). This screens for
# VALUE (earnings yield + FCF yield) x HEALTH (ROE, low debt, OCF>NI accruals check) x
# NON-CATALYST (beta<=1.1, |52w move| modest, revenue not shrinking), ranked SECTOR-NEUTRAL
# (else the list is all banks+energy). Cell 2 verifies top 20 against ACTUAL SEC filings
# (EDGAR XBRL companyfacts): NI+ streak, OCF>=NI, revenue up, SHARE COUNT SHRINKING (quiet
# buybacks). Yahoo-passes-but-EDGAR-fails = throw out; the gap is the signal.
# ⚠️ Caveats: info fields often None (names drop out); trailing PE lags filings ~a quarter;
# no screen fixes cyclical peak-earnings (cheap E at the top of a cycle is expensive in drag).
# See chat 2026-07-05 for the full read; results CSV -> sp500_quiet_health.csv.

# ============ CELL 1 — screen ============
"""
!pip -q install yfinance --upgrade
import yfinance as yf, pandas as pd, numpy as np, time, requests
from io import StringIO
# NB: bare pd.read_html(wikipedia_url) 403s (default python UA blocked) — fetch w/ browser UA first
html = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies',
                    headers={'User-Agent': 'Mozilla/5.0 (research script)'}).text
sp = pd.read_html(StringIO(html))[0]
# fallback if Wikipedia still blocks:
# sp = pd.read_csv('https://raw.githubusercontent.com/datasets/s-and-p-500-companies/main/data/constituents.csv')
# sp = sp.rename(columns={'Sector': 'GICS Sector'})
sp['Symbol'] = sp['Symbol'].str.replace('.', '-', regex=False)
sectors = dict(zip(sp['Symbol'], sp['GICS Sector']))
tickers = sp['Symbol'].tolist()
rows, failed = [], []
for i, t in enumerate(tickers):
    try:
        f = yf.Ticker(t).info
        mc, fcf, ocf, ni = f.get('marketCap'), f.get('freeCashflow'), f.get('operatingCashflow'), f.get('netIncomeToCommon')
        rows.append({'tkr': t, 'sector': sectors.get(t, ''), 'px': f.get('currentPrice'), 'mktcap': mc,
            'trailPE': f.get('trailingPE'), 'fwdPE': f.get('forwardPE'),
            'ey%': round(100/f['trailingPE'], 2) if f.get('trailingPE') else None,
            'fcfy%': round(fcf/mc*100, 2) if (fcf and mc) else None,
            'roe%': round(f['returnOnEquity']*100, 1) if f.get('returnOnEquity') else None,
            'd/e': f.get('debtToEquity'),
            'opm%': round(f['operatingMargins']*100, 1) if f.get('operatingMargins') else None,
            'revG%': round(f['revenueGrowth']*100, 1) if f.get('revenueGrowth') else None,
            'ocf>ni': (ocf > ni) if (ocf and ni) else None, 'beta': f.get('beta'),
            'chg52w%': round(f['52WeekChange']*100, 1) if f.get('52WeekChange') else None,
            'divY%': round(f['dividendYield'], 2) if f.get('dividendYield') else None})  # yf returns % already
    except Exception: failed.append(t)
    if (i+1) % 50 == 0:
        pd.DataFrame(rows).to_csv('sp500_raw.csv', index=False); print(f"{i+1}/{len(tickers)}")
    time.sleep(0.05)
df = pd.DataFrame(rows); df.to_csv('sp500_raw.csv', index=False)
h = df.copy()
h = h[(h['trailPE'] > 0) & (h['fwdPE'] > 0)]
h = h[h['fwdPE'] <= h['trailPE'] * 1.15]          # earnings not collapsing
h = h[h['roe%'] >= 10]
h = h[(h['d/e'].isna()) | (h['d/e'] < 150)]
h = h[h['fcfy%'] >= 3]
h = h[h['ocf>ni'] == True]                        # accruals check
h = h[(h['beta'].isna()) | (h['beta'] <= 1.1)]    # non-catalyst
h = h[h['chg52w%'].between(-20, 45)]              # no story either direction
h = h[h['revG%'] > -2]
def sect_rank(s, asc): return h.groupby('sector')[s].rank(pct=True, ascending=asc)
h['score'] = (sect_rank('ey%', True) + sect_rank('fcfy%', True) + sect_rank('roe%', True)
    + sect_rank('opm%', True) - 0.5*sect_rank('d/e', True).fillna(0.5)
    - 0.5*sect_rank('beta', True).fillna(0.5)).round(2)
out = h.sort_values('score', ascending=False)
cols = ['tkr','sector','px','trailPE','fwdPE','ey%','fcfy%','roe%','d/e','opm%','revG%','beta','chg52w%','divY%','score']
print(out[cols].head(30).to_string(index=False))
print(out.nsmallest(15, 'trailPE')[cols].to_string(index=False))
out.to_csv('sp500_quiet_health.csv', index=False)
"""

# ============ CELL 2 — EDGAR filings verification (top 20) ============
"""
import requests, pandas as pd, time
HDR = {'User-Agent': 'Jake Bishop research jake@example.com'}   # SEC requires a real UA/email
cik_map = requests.get('https://www.sec.gov/files/company_tickers.json', headers=HDR).json()
cik = {v['ticker']: str(v['cik_str']).zfill(10) for v in cik_map.values()}
def facts(tkr):
    r = requests.get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik[tkr]}.json", headers=HDR)
    return r.json()['facts'] if r.ok else None
def annual(fx, tag, unit='USD', n=4):
    try:
        vals = [v for v in fx['us-gaap'][tag]['units'][unit] if v.get('form') == '10-K' and v.get('fp') == 'FY']
        seen = {}
        for v in vals: seen[v['fy']] = v['val']
        return dict(sorted(seen.items())[-n:])
    except Exception: return {}
top = pd.read_csv('sp500_quiet_health.csv').head(20)['tkr'].tolist()
for t in top:
    fx = facts(t)
    if not fx: print(f"{t}: EDGAR miss"); continue
    rev = annual(fx, 'Revenues') or annual(fx, 'RevenueFromContractWithCustomerExcludingAssessedTax')
    ni  = annual(fx, 'NetIncomeLoss')
    ocf = annual(fx, 'NetCashProvidedByUsedInOperatingActivities')
    shs = annual(fx, 'CommonStockSharesOutstanding', unit='shares')
    yrs = sorted(ni.keys())
    ni_pos    = all(ni[y] > 0 for y in yrs) if yrs else False
    cash_conv = all(ocf.get(y, 0) >= ni[y] for y in yrs if y in ocf) if yrs else False
    shrink    = (list(shs.values())[-1] < list(shs.values())[0]) if len(shs) >= 2 else None
    grew      = (list(rev.values())[-1] > list(rev.values())[0]) if len(rev) >= 2 else None
    print(f"{t:6s} | NI+ {len(yrs)}yr: {ni_pos} | OCF>=NI: {cash_conv} | revenue up: {grew} | shares shrinking: {shrink}")
    time.sleep(0.3)
"""
