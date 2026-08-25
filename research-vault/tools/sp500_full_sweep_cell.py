
# S&P 500 FULL SWEEP v2 — every constituent, sorted by today's % move (token-free; 403-proof)
import subprocess, sys, io, urllib.request
try:
    import yfinance as yf; import pandas as pd
except Exception:
    subprocess.run([sys.executable,'-m','pip','install','-q','yfinance','pandas','lxml'])
    import yfinance as yf; import pandas as pd

UA = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}

def get_constituents():
    # path 1: Wikipedia WITH a browser user-agent (bare pandas fetch gets 403'd)
    try:
        req = urllib.request.Request('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies', headers=UA)
        html = urllib.request.urlopen(req, timeout=25).read()
        t = pd.read_html(io.BytesIO(html))[0]
        return dict(zip(t['Symbol'].str.replace('.','-',regex=False), t['GICS Sector'])), 'wikipedia'
    except Exception as e:
        print('wiki failed (', e, ') -> github fallback')
    # path 2: maintained CSV on github raw
    req = urllib.request.Request('https://raw.githubusercontent.com/datasets/s-and-p-500-companies/main/data/constituents.csv', headers=UA)
    t = pd.read_csv(io.BytesIO(urllib.request.urlopen(req, timeout=25).read()))
    return dict(zip(t['Symbol'].str.replace('.','-',regex=False), t['GICS Sector'])), 'github-csv'

sectors, src = get_constituents()
tickers = list(sectors.keys())
print(f'{len(tickers)} constituents loaded ({src})')

px = yf.download(tickers, period='5d', interval='1d', auto_adjust=True,
                 progress=False, threads=True)['Close']
px = px.dropna(axis=1, how='all')
last, prev = px.iloc[-1], px.iloc[-2]
chg = ((last/prev - 1)*100).dropna().sort_values(ascending=False)

up, dn = int((chg>0).sum()), int((chg<0).sum())
print(f'\nBREADTH: {up} up / {dn} down / median {chg.median():+.2f}%   (~15m delayed)')
sec = pd.DataFrame({'pct':chg, 'sector':[sectors.get(t,'?') for t in chg.index]})
print('\nSECTOR AVG %:')
for s,v in sec.groupby('sector')['pct'].mean().sort_values(ascending=False).items():
    print(f'  {v:+6.2f}%  {s}')

print(f'\n{"#":>3} {"TICKER":7}{"CHG":>8}  {"PRICE":>10}  SECTOR')
for i,(t,v) in enumerate(chg.items(),1):
    print(f'{i:>3} {t:7}{v:>+7.2f}%  {last[t]:>10,.2f}  {sectors.get(t,"?")[:22]}')
