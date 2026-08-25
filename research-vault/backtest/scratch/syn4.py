import csv, math
from collections import defaultdict
P='/home/user/INMA-/research-vault/backtest/out/'
panel=list(csv.DictReader(open(P+'daily_panel.csv')))
tr=list(csv.DictReader(open(P+'oracle_features.csv')))
def f(v):
    try: return float(v)
    except: return None
buys={(t['sym'],t['buy_date']) for t in tr}
for r in panel: r['_b']=1 if (r['sym'],r['date']) in buys else 0
strat=[r for r in panel if f(r['is_20d_low'])==1]
print('--- 20d-low stratum by YEAR: n, buys, rate')
by=defaultdict(lambda:[0,0])
for r in strat:
    y=r['date'][:4]; by[y][0]+=1; by[y][1]+=r['_b']
for y in sorted(by): print(y, 'n=%3d buys=%2d rate=%.3f'%(by[y][0],by[y][1],by[y][1]/by[y][0]))
print()
print('--- 20d-low stratum, WITHIN-YEAR stratified AUC (Mantel-Haenszel style pooled z) for top candidates')
def pooled_z(rows,col,strat_key):
    g=defaultdict(list)
    for r in rows:
        v=f(r[col])
        if v is None: continue
        g[strat_key(r)].append((v,r['_b']))
    S=0.0; V=0.0
    for k,d in g.items():
        pos=[x for x,y in d if y]; neg=[x for x,y in d if not y]
        if not pos or not neg: continue
        # Mann-Whitney U stat
        d2=sorted(d,key=lambda t:t[0]); n=len(d2); rk=[0]*n; i=0
        while i<n:
            j=i
            while j+1<n and d2[j+1][0]==d2[i][0]: j+=1
            avg=(i+j)/2+1
            for q in range(i,j+1): rk[q]=avg
            i=j+1
        sp=sum(rk[q] for q in range(n) if d2[q][1])
        n1,n0=len(pos),len(neg)
        U=sp-n1*(n1+1)/2
        S+=U-n1*n0/2.0; V+=n1*n0*(n+1)/12.0
    return S/math.sqrt(V) if V>0 else None
for c in ['ust_y2','curve_2s10s','wti','hyg','tlt_chg5d','vix_chg5d','dow','rsi14','dd_from_20d_high_pct','consec_down_days','vol_vs_20d','atr14_pct','tday_in_month']:
    z1=pooled_z(strat,c,lambda r:r['date'][:4])
    z2=pooled_z(strat,c,lambda r:(r['sym'],r['date'][:7]))
    print('%-22s  within-YEAR z=%+5.2f   within-SYM-MONTH z=%s'%(c,z1,('%+5.2f'%z2) if z2 else 'n/a'))
