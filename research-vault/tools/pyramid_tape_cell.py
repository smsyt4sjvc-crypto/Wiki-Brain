
# PYRAMID TAPE — price every layer of the server/electrical cascade in one shot (token-free)
import subprocess, sys
try:
    import yfinance as yf
except Exception:
    subprocess.run([sys.executable,'-m','pip','install','-q','yfinance']); import yfinance as yf

LAYERS = {
 'L1 memory':        ['MU','SNDK','STX','WDC'],
 'L2 passives/MLCC': ['VSH','APH','TEL','LFUS'],                   # US-listed (KYCCF dropped: thin OTC)
 'L2 foreign (MLCC)':['2327.TW','6981.T','6762.T','009150.KS'],   # Yageo, Murata, TDK, Samsung Electro-Mech
 'L3 substrate/PCB': ['TTMI','ROG','4062.T','3037.TW','8046.TW'], # +Ibiden, Unimicron, Nan Ya PCB (6967.T dead)
 'L4 base materials':['FCX','MTRN','3110.T'],                     # +Nittobo (glass cloth)
 'Electrical stack': ['VICR','ENS','CLF','ETN','POWL','GEV'],
 'Reference':        ['SOXX','^GSPC'],
}

def q(t):
    try:
        fi = yf.Ticker(t).fast_info
        px = fi['last_price']; pc = fi['previous_close']
        return float(px), (float(px)/float(pc)-1)*100
    except Exception:
        try:
            h = yf.download(t, period='5d', progress=False, auto_adjust=True)['Close'].dropna()
            if hasattr(h,'columns'): h = h.iloc[:,0]
            return float(h.iloc[-1]), (float(h.iloc[-1])/float(h.iloc[-2])-1)*100
        except Exception: return None, None

print('='*58); print('  PYRAMID TAPE — is capital rotating DOWN the layers, or OUT?'); print('='*58)
for layer, tks in LAYERS.items():
    print(f'\n### {layer}')
    vals=[]
    for t in tks:
        px, ch = q(t)
        if px is None: print(f'  {t:10} — n/a'); continue
        vals.append(ch)
        print(f'  {t:10}{px:>11,.2f}  {ch:>+7.2f}%')
    if vals: print(f'  {"LAYER AVG":10}{"":>11}  {sum(vals)/len(vals):>+7.2f}%')
print('\nRead: layers GREEN while L1 red = rotation DOWN the pyramid (the thesis).')
print('      All layers red together     = one position, not four (the deleveraging state).')
