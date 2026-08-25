# CRUDE CURVE / CALENDAR SPREADS — the physical-shortage arbiter (token-free)
# Flat price can lie (positioning, headline hype). The CURVE cannot:
#   backwardation (front > deferred) = barrels needed NOW  = real physical tightness
#   contango      (front < deferred) = barrels not needed  = NO physical shortage
import subprocess, sys
from datetime import date
try:
    import yfinance as yf
except Exception:
    subprocess.run([sys.executable,'-m','pip','install','-q','yfinance']); import yfinance as yf

MC = {1:'F',2:'G',3:'H',4:'J',5:'K',6:'M',7:'N',8:'Q',9:'U',10:'V',11:'X',12:'Z'}

def chain(root, n=9):
    """Generate the next n contract symbols from today (Yahoo NYMEX format)."""
    d = date.today(); out=[]
    for i in range(n):
        mm = d.month + i; yy = d.year + (mm-1)//12; mm = (mm-1)%12 + 1
        out.append((f"{root}{MC[mm]}{str(yy)[-2:]}.NYM", f"{yy}-{mm:02d}"))
    return out

def last_close(sym):
    try:
        h = yf.download(sym, period='7d', progress=False, auto_adjust=False)['Close'].dropna()
        if hasattr(h,'columns'): h = h.iloc[:,0]
        return float(h.iloc[-1]) if len(h) else None
    except Exception:
        return None

def curve(root, label):
    print('\n' + '='*62); print(f'  {label} FORWARD CURVE'); print('='*62)
    pts=[]
    for sym, tag in chain(root):
        px = last_close(sym)
        if px: pts.append((tag, sym, px))
    if len(pts) < 2:
        print('  insufficient contract data (symbols may have rolled) — try CL=F/BZ=F flat price only')
        return
    print(f'  {"MONTH":9}{"SYMBOL":14}{"PRICE":>9}{"vs prev":>10}{"vs front":>10}')
    front = pts[0][2]
    for i,(tag,sym,px) in enumerate(pts):
        prev = f'{px-pts[i-1][2]:+.2f}' if i else '   —'
        print(f'  {tag:9}{sym:14}{px:>9.2f}{prev:>10}{px-front:>+10.2f}')
    m1m2 = front - pts[1][2]
    span = len(pts)-1
    m1mN = front - pts[-1][2]
    per_month = m1m2
    print(f'\n  M1-M2 spread : {m1m2:+.2f}/bbl   ({per_month:+.2f} per month)')
    print(f'  M1-M{span+1} spread : {m1mN:+.2f}/bbl  across {span} months')
    if m1m2 > 1.50:   verdict = 'STEEP BACKWARDATION -> severe physical tightness (shortage is REAL)'
    elif m1m2 > 0.30: verdict = 'backwardation -> tight, but within normal-market range'
    elif m1m2 > -0.10:verdict = 'FLAT -> balanced; no physical shortage being priced'
    else:             verdict = 'CONTANGO -> surplus/ample supply; the market sees NO shortage'
    print(f'  VERDICT      : {verdict}')

for root,label in [('CL','WTI'),('BZ','BRENT')]:
    curve(root,label)

print('\n' + '='*62)
print('  READ: a closed Hormuz with a FLAT/CONTANGO curve means barrels are')
print('  still reaching buyers (dark fleet / toll-gated transit / bypass).')
print('  Steep backwardation = the closure is real and the tape is wrong.')
print('='*62)
