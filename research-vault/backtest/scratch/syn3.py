import csv, math, random
P='/home/user/INMA-/research-vault/backtest/out/'
panel=list(csv.DictReader(open(P+'daily_panel.csv')))
tr=list(csv.DictReader(open(P+'oracle_features.csv')))
def f(v):
    try: return float(v)
    except: return None
buys={(t['sym'],t['buy_date']) for t in tr}
for r in panel: r['_b']=1 if (r['sym'],r['date']) in buys else 0
cols=[c for c in panel[0] if c not in ('sym','date','month','_b')]
def auc(rows,col):
    d=[(f(r[col]),r['_b']) for r in rows if f(r[col]) is not None]
    pos=[x for x,y in d if y]; neg=[x for x,y in d if not y]
    if not pos or not neg: return None,0,0
    d.sort(key=lambda t:t[0])
    # rank-based AUC with ties
    ranks={}; i=0; n=len(d)
    rk=[0]*n
    while i<n:
        j=i
        while j+1<n and d[j+1][0]==d[i][0]: j+=1
        avg=(i+j)/2+1
        for k in range(i,j+1): rk[k]=avg
        i=j+1
    sp=sum(rk[k] for k in range(n) if d[k][1])
    np_,nn=len(pos),len(neg)
    a=(sp-np_*(np_+1)/2)/(np_*nn)
    return a,np_,nn
def z_of_auc(a,np_,nn):
    return (a-0.5)/math.sqrt((np_+nn+1)/(12.0*np_*nn))
print('=== ALL-PANEL: AUC for predicting oracle BUY, all %d features, sorted by |AUC-0.5|'%len(cols))
res=[]
for c in cols:
    a,p,n=auc(panel,c)
    if a is None: continue
    res.append((abs(a-0.5),a,c,p,n,z_of_auc(a,p,n)))
res.sort(reverse=True)
for d,a,c,p,n,z in res[:14]: print('%-24s AUC=%.3f  z=%+5.2f'%(c,a,z))
print('... (%d features tested; |z|>2 count = %d, expected under null ~%.1f)'%(len(res),sum(1 for x in res if abs(x[5])>2),0.0455*len(res)))
print()
strat=[r for r in panel if f(r['is_20d_low'])==1]
print('=== WITHIN 20d-LOW STRATUM (n=%d, buys=%d): AUC, all features'%(len(strat),sum(r['_b'] for r in strat)))
res2=[]
for c in cols:
    a,p,n=auc(strat,c)
    if a is None: continue
    res2.append((abs(a-0.5),a,c,p,n,z_of_auc(a,p,n)))
res2.sort(reverse=True)
for d,a,c,p,n,z in res2[:12]: print('%-24s AUC=%.3f  z=%+5.2f'%(c,a,z))
print('... %d features tested; |z|>2 count = %d, expected ~%.1f under pure null'%(len(res2),sum(1 for x in res2 if abs(x[5])>2),0.0455*len(res2)))
