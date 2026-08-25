
# ============================================================================
#  ASIA STRESS — is the Korea crash TRANSMITTING, or is it contained?
#  Equity beta has already been tested 3 sessions and failed. This cell reads
#  the channels that could still transmit: FX/funding, carry, gold, US futures.
#  Run it while Asia is open. Token-free.
# ============================================================================
import subprocess, sys, time
try:
    import yfinance as yf
except Exception:
    subprocess.run([sys.executable,'-m','pip','install','-q','yfinance']); import yfinance as yf
import numpy as np, pandas as pd

GROUPS = {
 'ASIA EQUITY (the event)': [('^KS11','KOSPI'), ('^KQ11','KOSDAQ'), ('^N225','Nikkei'),
                             ('^TWII','Taiwan'), ('^HSI','HangSeng'), ('000001.SS','Shanghai')],
 '★ FX / FUNDING (channel a)': [('KRW=X','USD/KRW'), ('JPY=X','USD/JPY'), ('TWD=X','USD/TWD'),
                                ('CNY=X','USD/CNY'), ('DX-Y.NYB','DXY')],
 '★ US FUTURES (the gauge)': [('NQ=F','Nasdaq fut'), ('ES=F','S&P fut'), ('YM=F','Dow fut'),
                              ('RTY=F','R2K fut')],
 '★ REFEREE (channel d)': [('GC=F','Gold'), ('SI=F','Silver'), ('^TNX','US 10Y'), ('CL=F','WTI')],
 'THE NAMES': [('005930.KS','Samsung Elec'), ('000660.KS','SK hynix'),
               ('2330.TW','TSMC'), ('MU','Micron')],
}
ALL = [t for g in GROUPS.values() for t,_ in g]

def fetch(tickers, period='3mo', tries=3):
    last, best = None, {}
    for i in range(tries):
        try:
            df = yf.download(tickers, period=period, progress=False,
                             auto_adjust=True, threads=True)['Close']
            if isinstance(df, pd.Series): df = df.to_frame(tickers[0])
            out = {c: df[c].dropna() for c in df.columns if df[c].dropna().size > 2}
            if len(out) > len(best): best = out
            if len(out) >= len(tickers) - 2: return out
            last = f'{len(out)}/{len(tickers)} returned'
        except Exception as e:
            last = e
        if i < tries-1:
            print(f'  ...attempt {i+1}: {last}; retry in {2**i}s'); time.sleep(2**i)
    if best:
        print(f'  !! PARTIAL ({len(best)}/{len(tickers)}). Missing lines say NOT AVAILABLE.')
        return best
    print(f'  !! ALL FETCHES FAILED: {last}'); return {}

print('='*68); print('  ASIA STRESS — transmitting, or contained?'); print('='*68)
D = fetch(ALL)
if not D:
    print('\n  NO DATA. Re-run in 60s or use a fresh Colab runtime.'); raise SystemExit

def stats(t):
    s = D.get(t)
    if s is None or len(s) < 2: return None
    px = float(s.iloc[-1]); d1 = (px/float(s.iloc[-2])-1)*100
    # ARTIFACT GUARD: a halted market's yfinance daily series can DROP a bar, turning a
    # 2-day move into a fake 1-day print. Flag anything implausible for a cash index.
    gap = (s.index[-1] - s.index[-2]).days
    n20 = min(21, len(s)); m = (px/float(s.iloc[-n20])-1)*100
    dd = (px/float(s.max())-1)*100
    base = float(s.iloc[-2])   # the prior-session reference the 1d% is measured against
    flag = ' <-- CHECK: bar gap %dd, 1d%% may be MULTI-DAY' % gap if (gap > 3 or abs(d1) > 12) else ''
    return px, d1, m, dd, s.index[-1].date(), flag, base

for g, items in GROUPS.items():
    print(f'\n### {g}')
    print(f'  {"":14}{"last":>12}{"1d%":>9}{"~1mo%":>9}{"vs 3mo hi":>11}{"BASE":>12}   as of')
    for t, lab in items:
        r = stats(t)
        if r is None: print(f'  {lab:14}   -- NOT AVAILABLE'); continue
        px, d1, m, dd, dt, flag, base = r
        print(f'  {lab:14}{px:>12,.2f}{d1:>+9.2f}{m:>+9.1f}{dd:>+11.1f}{base:>12,.2f}   {dt}{flag}')

# ---------------- the reads ----------------
print('\n' + '='*68); print('  THE CHANNELS'); print('='*68)
print('\n  !! READ THE **BASE** COLUMN BEFORE COMPARING TWO RUNS OF THIS CELL.')
print('     The 1d%% is measured against that base. When a session rolls, the BASE changes and')
print('     every 1d%% re-prices WITHOUT THE MARKET MOVING. Two runs 15 minutes apart produced a')
print('     1.85pt "spread compression" here on 2026-07-28 that was ENTIRELY a base change')
print('     (Dow futures base +562 pts, Mon settle -> Tue settle) while real price action was')
print('     NQ -0.26%% / YM -0.09%%. Compare PRICES across runs. Compare %% only at equal base.')

def val(t, i=1):
    r = stats(t); return r[i] if r else None

k1, k20 = val('^KS11'), val('^KS11', 2)
if k20 is not None:
    print(f'\n[event] KOSPI {k1:+.2f}% today, {k20:+.1f}% over ~1 month.')

krw, jpy = val('KRW=X'), val('JPY=X')
print('\n[a] FX / FUNDING — the channel that reaches the S&P without touching Korean beta')
if krw is None: print('    USD/KRW NOT AVAILABLE — channel (a) unreadable.')
else:
    print(f'    USD/KRW {krw:+.2f}% today ({val("KRW=X",2):+.1f}% ~1mo)   USD/JPY {jpy:+.2f}%'
          if jpy is not None else f'    USD/KRW {krw:+.2f}% today')
    m_krw = val('KRW=X', 2)
    print('    NOTE ON DIRECTION: USD/KRW UP = won WEAK = FOREIGNERS FLEEING Korea.')
    print('                       USD/KRW DOWN = won STRONG = Korean money coming HOME')
    print('                       (selling FOREIGN assets to fund domestic margin) OR export-earnings')
    print('                       conversion. A strong won in a crash is REPATRIATION, not calm.')
    if krw > 0.7:
        print('    -> WON WEAKENING HARD: foreign capital flight. Channel (a) LIVE (outflow form).')
    elif m_krw is not None and m_krw < -3:
        print(f'    -> WON STRENGTHENING {abs(m_krw):.1f}% over ~1mo DURING an equity crash. Two readings,')
        print('       and they point opposite ways: (i) REPATRIATION - domestic institutions selling')
        print('       FOREIGN assets to fund margin at home. That is channel (a) firing, and it reaches')
        print('       the S&P without touching Korean beta. (ii) EXPORT EARNINGS - record dollar revenue')
        print('       (hynix tripled) converted to won. Fundamentals up, multiple down.')
        print('       DISCRIMINATOR: (i) shows up as foreign net-selling of US equities; (ii) does not.')
    else:
        print('    -> won roughly stable. No clear FX-channel signal either way.')

print('\n[c] CARRY — the Aug-2024 replay mechanism')
if jpy is None: print('    USD/JPY NOT AVAILABLE.')
else:
    print('    ' + (f'-> YEN STRENGTHENING ({jpy:+.2f}%): carry unwind pressure. This is how Asia stress'
                    '\n       reached US megacaps in Aug-2024.' if jpy < -0.5 else
                    f'-> yen {jpy:+.2f}%: no carry-unwind signal.'))

print('\n[d] REFEREE — do the METALS sell WITH equities?')
g1, s1 = val('GC=F'), val('SI=F')
if g1 is None: print('    Gold NOT AVAILABLE.')
else:
    print(f'    Gold {g1:+.2f}%' + (f'   Silver {s1:+.2f}%' if s1 is not None else ''))
    if s1 is not None and g1 < -0.8 and s1 < -0.8:
        print('    -> BOTH METALS DOWN HARD WITH equities = LIQUIDATION (calls sell what is liquid).')
    elif s1 is not None and (s1 > 0 or g1 > -0.5):
        print('    -> metals NOT being dumped. A margin cascade sells what is liquid; silver green or')
        print('       gold only marginally lower says the FORCED-SELLING channel is NOT open.')
    else:
        print('    -> mixed metals; no clean liquidation read.')

print('\n[GAUGE] US FUTURES — Jake\'s registered contagion gauge')
nq, es = val('NQ=F'), val('ES=F')
if nq is None: print('    NQ NOT AVAILABLE.')
else:
    ym = val('YM=F')
    print(f'    NQ {nq:+.2f}%   ES {es:+.2f}%   YM {ym:+.2f}%'
          if es is not None and ym is not None else f'    NQ {nq:+.2f}%')
    if ym is not None:
        spread = nq - ym
        print(f'    NQ-minus-YM spread = {spread:+.2f} pts')
        if spread < -1.0 and ym > 0:
            print('    -> DISPERSION, NOT CONTAGION. Dow futures GREEN while Nasdaq futures fall is the')
            print('       same rotation that has absorbed every Asian session so far - it is the ABSORBER')
            print('       working, not the channel opening. An absolute NQ level cannot tell these apart.')
            print('    WATCH: the spread COMPRESSING toward zero while BOTH fall = absorber exhausted =')
            print('       that is the transmission event. A wide spread = another failure to transmit.')
        elif nq < -0.05 and ym < 0:
            ratio = abs(nq)/max(abs(ym), 1e-9)
            print(f'    NQ is falling {ratio:.1f}x as hard as YM.')
            if ratio >= 2.0:
                print('    -> STILL DISPERSION. Both red does NOT mean the absorber failed - the absorber')
                print('       is measured by the RATIO, not by YM\'s sign. Dow futures down a fifth of a')
                print('       percent while Nasdaq futures fall ~1% is the rotation working, not breaking.')
                print('    THE TRANSMISSION EVENT is the RATIO collapsing toward 1.0 (everything falling')
                print('       TOGETHER), not YM merely printing negative.')
            else:
                print('    -> RATIO NEAR 1: everything falling together at similar magnitude. The absorber')
                print('       is GONE and correlation has snapped back. THIS is the transmission event.')
            print(f'    MAGNITUDE CHECK: NQ {nq:+.2f}% / YM {ym:+.2f}% - the shape can change while the')
            print('       size stays trivial. Do not call a rout off a sub-1% overnight tape.')
            print('    !! ALTERNATIVE, equal weight: OVERNIGHT sessions are structurally lower-dispersion')
            print('       than CASH sessions (single-stock rotation does not trade overnight). Compare an')
            print('       overnight spread to another OVERNIGHT spread, never to a cash-session spread.')
        else:
            print('    -> mixed; no clean read. Use the ratio and the spread, not the levels.')

print('\n' + '='*68)
print('  WHAT WOULD ACTUALLY CHANGE THE READ (none of it is a price)')
print('  1. A NAMED CASUALTY — a Korean securities house, fund gate, or structured product.')
print('     Its ABSENCE is the strongest argument for containment. Watch the wires, not the tape.')
print('  2. KRW breaking out = forced selling of FOREIGN assets to meet domestic margin.')
print('  3. Yen strengthening = carry unwind = the Aug-2024 transmission path.')
print('  4. Gold selling WITH equities = liquidation, not rotation.')
print('  COUNTER: Korea is a retail-margin market that fell 8.8% in a day in Aug-2024 and fully')
print('  recovered in weeks. Circuit breakers break price discovery - you cannot read "orderly"')
print('  or "disorderly" off a market that keeps halting.')
print('='*68)
