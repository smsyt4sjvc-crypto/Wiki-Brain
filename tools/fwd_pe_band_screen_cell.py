# fwd_pe_band_screen_cell.py — S&P 500 FORWARD P/E BAND SCREEN (Colab cell; Jake-side, yfinance 429s from the container)
# Jake's ask 2026-09-06: "determine the historical optimal forward P/E where stocks show the greatest
# individual returns and see which stocks are sitting there now."
#
# WHAT THIS CELL DOES AND DOES NOT DO — READ BEFORE RUNNING
#   (A) CURRENT CROSS-SECTION: forward P/E for every S&P 500 constituent (yfinance .info), deciles, sector medians.
#   (B) THE BAND: lists names whose forward P/E sits inside [BAND_LO, BAND_HI). The band is set from the
#       INDEX-LEVEL 150-year Shiller study run in the vault (tools output → rates/market-fragility note), NOT
#       from a stock-level backtest.
#   (C) THE TRAP CHECK (from durable_value_screen.py): a low forward P/E has two causes — a depressed price on
#       normal earnings (cheap) or a normal price on PEAK/INFLATED estimates (not cheap; refiners at 4-9x fwd
#       on record cracks are the vault's live example, portfolio-state 9/1). Flags: fwdEPS vs trailEPS ratio,
#       1y price return, and whether the name is at its 52w high (cheap-because-earnings-outran-price ≠ cheap).
#   ⛔ NOT DONE: a STOCK-LEVEL historical "optimal forward P/E → forward return" backtest. That needs
#       point-in-time consensus estimates (IBES/FactSet) for hundreds of names over decades. yfinance only
#       exposes CURRENT forward EPS. Any stock-level "history" built from current forwardPE is look-ahead
#       contaminated and survivorship-biased (current constituents only). Refusing to fake it.
#   ⚠️ METHOD WARNING (top10_band_test / physical-to-silicon control-test discipline): picking "the bucket with
#       the best historical return" is in-sample fitting. The vault's index study reports a CONTROL row and
#       era splits for exactly this reason — read the band as "consistent with," never "predicted by."
#
# RUN: paste into Colab. ~3-6 min for 500 .info calls. Paste the printed output back into chat for the read.

import subprocess, sys, io, urllib.request, time, math
try:
    import yfinance as yf; import pandas as pd
except Exception:
    subprocess.run([sys.executable,'-m','pip','install','-q','yfinance','pandas','lxml'])
    import yfinance as yf; import pandas as pd

# ---- PARAMETERS (edit here only) ----
# BANDS SET FROM THE VAULT'S SHILLER STUDY (raw/2026-09-06-shiller-pe-band-study-output.txt), TRAILING→FORWARD
# translated at ~8-10% growth (forward ≈ trailing ÷ (1+g)):
#   BAND_A = the 150-year optimum: trailing 10-14x → fwd ~9-13x. Mean fwd-12m real TR +10.9..+15.7% vs control +8.6%.
#            ⚠️ ZERO post-1990 months in the 10-12 bucket, 3 in 12-14: the modern market does not trade there.
#            Names printing here today are mostly cyclical-peak or troubled — the TRAP flags exist for this band.
#   BAND_B = the post-1990 best-populated: trailing 14-20x → fwd ~13-18x. Post-1990 mean +11.8..+17.2% (n=34-60).
BANDS = [('A: 150yr optimum', 9.0, 13.0), ('B: post-1990 populated', 13.0, 18.0)]
TRAP_EPS_GROWTH_MAX = 1.35        # fwdEPS/trailEPS above this = estimates far above trailing = peak/inflation risk
TRAP_1Y_RETURN_MIN  = 0.60        # 1y return above this AND low fwd P/E = "earnings outran price" (refiner pattern)
MIN_MCAP            = 2e9

UA = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
def get_constituents():
    try:
        req = urllib.request.Request('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies', headers=UA)
        t = pd.read_html(io.BytesIO(urllib.request.urlopen(req, timeout=25).read()))[0]
        return dict(zip(t['Symbol'].str.replace('.','-',regex=False), t['GICS Sector'])), 'wikipedia'
    except Exception as e:
        print('wiki failed (', e, ') -> github fallback')
    req = urllib.request.Request('https://raw.githubusercontent.com/datasets/s-and-p-500-companies/main/data/constituents.csv', headers=UA)
    t = pd.read_csv(io.BytesIO(urllib.request.urlopen(req, timeout=25).read()))
    return dict(zip(t['Symbol'].str.replace('.','-',regex=False), t['GICS Sector'])), 'github-csv'

sectors, src = get_constituents()
tickers = list(sectors.keys())
print(f'{len(tickers)} constituents loaded ({src})')

# 1y price return + 52w position from one batched download (cheap)
px = yf.download(tickers, period='1y', interval='1d', auto_adjust=True, progress=False, threads=True)['Close'].dropna(axis=1, how='all')
ret1y = (px.iloc[-1]/px.iloc[0]-1)
pos52 = (px.iloc[-1]-px.min())/(px.max()-px.min())

rows=[]; t0=time.time()
for i,t in enumerate(tickers,1):
    try:
        inf = yf.Ticker(t).info
        fpe = inf.get('forwardPE'); tpe = inf.get('trailingPE')
        feps= inf.get('forwardEps'); teps= inf.get('trailingEps')
        prc = inf.get('currentPrice') or inf.get('regularMarketPrice')
        mc  = inf.get('marketCap')
        fpe_calc = (prc/feps) if (prc and feps and feps>0) else None
        rows.append(dict(t=t, sector=sectors.get(t,'?'), price=prc, mcap=mc, fwdPE=fpe, trailPE=tpe,
                         fwdEPS=feps, trailEPS=teps, fwdPE_calc=fpe_calc,
                         ret1y=float(ret1y.get(t, float('nan'))), pos52=float(pos52.get(t, float('nan')))))
    except Exception as e:
        rows.append(dict(t=t, sector=sectors.get(t,'?'), err=str(e)[:40]))
    if i%50==0: print(f'  {i}/{len(tickers)}  {time.time()-t0:.0f}s')
df = pd.DataFrame(rows)
ok = df[df['fwdPE'].notna() & (df['fwdPE']>0) & (df['mcap']>=MIN_MCAP)].copy()
print(f'\n{len(ok)} names with a positive forward P/E (of {len(df)}); {int(df["fwdPE"].isna().sum())} missing, {int((df["fwdPE"]<=0).sum())} negative/zero')

# ---- (A) CROSS-SECTION ----
q = ok['fwdPE'].quantile([.1,.25,.5,.75,.9])
print('\nFORWARD P/E DECILES (S&P 500, today):  p10 %.1f | p25 %.1f | MEDIAN %.1f | p75 %.1f | p90 %.1f' % tuple(q))
print('Cap-weighted fwd P/E: %.1f   (equal-weight median above)' % ((ok['fwdPE']*ok['mcap']).sum()/ok['mcap'].sum()))
print('\nSECTOR MEDIAN fwd P/E:')
for s,v in ok.groupby('sector')['fwdPE'].median().sort_values().items():
    print(f'  {v:5.1f}  {s}  (n={int((ok["sector"]==s).sum())})')

# ---- (C) TRAP FLAGS ----
def trap(r):
    fl=[]
    if r['trailEPS'] and r['fwdEPS'] and r['trailEPS']>0 and r['fwdEPS']/r['trailEPS']>TRAP_EPS_GROWTH_MAX: fl.append('EPS-JUMP')   # fwd far above trailing
    if r['trailEPS'] is not None and r['trailEPS']<=0: fl.append('TRAIL<=0')                                                          # fwd P/E on a loss base
    if not math.isnan(r['ret1y']) and r['ret1y']>TRAP_1Y_RETURN_MIN: fl.append('RAN+%d%%'%int(r['ret1y']*100))                     # earnings outran price
    if not math.isnan(r['pos52']) and r['pos52']>0.9: fl.append('@52wHI')
    return ','.join(fl)
ok['trap']=ok.apply(trap,axis=1)

# ---- (B) THE BAND ----
for label, BAND_LO, BAND_HI in BANDS:
    band = ok[(ok['fwdPE']>=BAND_LO)&(ok['fwdPE']<BAND_HI)].sort_values('fwdPE')
    print(f'\n{"="*110}\nBAND {label}: FORWARD P/E IN [{BAND_LO:g}, {BAND_HI:g})  —  {len(band)} of {len(ok)}  (sorted low→high)\n{"="*110}')
    print(f'{"TICKER":7}{"fwdPE":>7}{"trlPE":>7}{"f/tEPS":>8}{"1yRet":>8}{"52w":>5}{"mcap$B":>8}  {"SECTOR":22} TRAP-FLAGS')
    for _,r in band.iterrows():
        ft = (r['fwdEPS']/r['trailEPS']) if (r['trailEPS'] and r['trailEPS']>0 and r['fwdEPS']) else float('nan')
        print(f'{r["t"]:7}{r["fwdPE"]:>7.1f}{(r["trailPE"] or float("nan")):>7.1f}{ft:>8.2f}{r["ret1y"]*100:>+7.0f}%{r["pos52"]:>5.2f}{r["mcap"]/1e9:>8.0f}  {r["sector"][:22]:22} {r["trap"]}')
    clean = band[band['trap']=='']
    print(f'\nCLEAN (no trap flags) in band {label[:1]}: {len(clean)} names → {", ".join(clean["t"].tolist())}')
print('\nREAD THE FLAGS: EPS-JUMP = forward estimate >35% above trailing (the multiple is low because the ESTIMATE is high);')
print('  RAN+ = 1y return >60% (low multiple because earnings outran price — the refiner pattern, portfolio-state 9/1);')
print('  @52wHI = at the high (not a depressed price). A low fwd P/E carrying any flag is NOT the "cheap" the band study rewards.')
ok.to_csv('sp500_fwd_pe_cross_section.csv', index=False); print('\nsaved sp500_fwd_pe_cross_section.csv')
