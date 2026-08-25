import csv, math, statistics as st, random
from collections import defaultdict
O='/home/user/INMA-/research-vault/backtest/out/'
panel=list(csv.DictReader(open(O+'daily_panel.csv')))
tr=list(csv.DictReader(open(O+'oracle_features.csv')))
def f(v):
    try: return float(v)
    except: return None
# --- finer conditioning: quintiles and deciles of own ret_5d_pct, trade level
qs=sorted(f(r['ret_5d_pct']) for r in panel if f(r['ret_5d_pct']) is not None)
for K in [3,5,10]:
    cuts=[qs[int(i/K*(len(qs)-1))] for i in range(1,K)]
    def bk(x):
        i=0
        while i<len(cuts) and x>=cuts[i]: i+=1
        return i
    pb=defaultdict(list); bb=defaultdict(list)
    for r in panel:
        x=f(r['ret_5d_pct'])
        if x is None: continue
        pb[bk(x)].append(f(r['hyg_chg5d'])<0)
    for t in tr:
        bb[bk(f(t['B_ret_5d_pct']))].append(f(t['B_hyg_chg5d'])<0)
    exp=0; var=0; obs=0; N=0
    for k in bb:
        p=sum(pb[k])/len(pb[k]); nk=len(bb[k])
        exp+=nk*p; var+=nk*p*(1-p); obs+=sum(bb[k]); N+=nk
    print("K=%2d buckets: obs %d/%d = %.1f%%  matched-exp %.1f = %.1f%%  lift %.2f  naive z=%.2f"%(
        K,obs,N,100*obs/N,exp,100*exp/N,(obs/N)/(exp/N),(obs-exp)/math.sqrt(var)))
# unique-date version (spx sym only, dedupe by date using spx panel row) to kill sym double-count
spxrow={r['date']:r for r in panel if r['sym']=='spx'}
bd={}
for t in tr: bd.setdefault(t['buy_date'],t)
K=5; cuts=[qs[int(i/K*(len(qs)-1))] for i in range(1,K)]
def bk(x):
    i=0
    while i<len(cuts) and x>=cuts[i]: i+=1
    return i
pb=defaultdict(list); bb=defaultdict(list)
for d,r in spxrow.items(): pb[bk(f(r['ret_5d_pct']))].append(f(r['hyg_chg5d'])<0)
for d in bd:
    r=spxrow.get(d)
    if r is None: continue
    bb[bk(f(r['ret_5d_pct']))].append(f(r['hyg_chg5d'])<0)
exp=sum(len(bb[k])*sum(pb[k])/len(pb[k]) for k in bb); var=sum(len(bb[k])*(sum(pb[k])/len(pb[k]))*(1-sum(pb[k])/len(pb[k])) for k in bb)
obs=sum(sum(bb[k]) for k in bb); N=sum(len(bb[k]) for k in bb)
print("UNIQUE-DATE spx-conditioned K=5: obs %d/%d=%.1f%% exp %.1f=%.1f%% lift %.2f z=%.2f"%(obs,N,100*obs/N,exp,100*exp/N,(obs/N)/(exp/N),(obs-exp)/math.sqrt(var)))

# --- is hyg the LARGEST raw effect in the macro lens? scan macro cols, threshold <0
macro=['dxy_chg5d','gold_chg5d','hyg_chg5d','tlt_chg5d','vix_chg5d','ust_y2_chg5d','ust_y10_chg5d','ust_y30_chg5d','curve_2s10s','curve_2s30s']
cols=[c for c in panel[0] if c.endswith('chg5d') or c.startswith('curve')]
print("\nmacro cols scanned:",cols)
res=[]
for c in cols:
    pv=[f(r[c]) for r in panel if f(r[c]) is not None]
    p=sum(1 for v in pv if v<0)/len(pv)
    bv=[f(t['B_'+c]) for t in tr if f(t['B_'+c]) is not None]
    b=sum(1 for v in bv if v<0)/len(bv)
    res.append((abs(math.log((b+1e-9)/p)),c,b,p,len(bv),(b/p)))
res.sort(reverse=True)
for _,c,b,p,n,l in res: print("  %-16s buy %.1f%% (n=%d) panel %.1f%% lift %.2f"%(c,100*b,n,100*p,l))
# also non-macro binary-ish for context
print("\nfor scale, some equity-own features (lift of buy vs panel):")
for c,thr,lab in [('rsi14',35,'<35'),('is_20d_low',0.5,'==1'),('bb_pctB',0.2,'<0.2'),('dist_sma20_pct',0,'<0'),('ret_5d_pct',0,'<0'),('dd_from_20d_high_pct',-3,'<-3')]:
    pv=[f(r[c]) for r in panel if f(r[c]) is not None]
    bv=[f(t['B_'+c]) for t in tr if f(t['B_'+c]) is not None]
    if lab=='==1': p=sum(1 for v in pv if v>0.5)/len(pv); b=sum(1 for v in bv if v>0.5)/len(bv)
    else: p=sum(1 for v in pv if v<thr)/len(pv); b=sum(1 for v in bv if v<thr)/len(bv)
    print("  %-22s buy %.1f%% panel %.1f%% lift %.2f"%(c+lab,100*b,100*p,b/p))
