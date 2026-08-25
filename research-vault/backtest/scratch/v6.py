import csv, statistics as st
F='/home/user/INMA-/research-vault/backtest/out/oracle_features.csv'
tr=list(csv.DictReader(open(F)))
def f(x):
    try: return float(x)
    except: return None
bk=[("<15",lambda v:v<15),("15-20",lambda v:15<=v<20),("20-25",lambda v:20<=v<25),(">25",lambda v:v>=25)]
print("Oracle trade return by B_vix bucket:")
for lbl,fn in bk:
    s=[f(t['ret_pct']) for t in tr if fn(f(t['B_vix']))]
    print("  %6s n=%3d mean=%.2f med=%.2f"%(lbl,len(s),st.mean(s),st.median(s)))
# hold days by bucket -> is the gradient just longer holds / bigger range?
for lbl,fn in bk:
    s=[t for t in tr if fn(f(t['B_vix']))]
    print("  %6s hold=%.1f  |ret|/hold=%.2f"%(lbl,st.mean(f(t['hold_days']) for t in s),
        st.mean(f(t['ret_pct'])/max(f(t['hold_days']),0.5) for t in s)))
# how many trades in vix>25 come from distinct months?
s=[t for t in tr if f(t['B_vix'])>=25]
print("  >25 trades: months",sorted(set(t['month'] for t in s)))
