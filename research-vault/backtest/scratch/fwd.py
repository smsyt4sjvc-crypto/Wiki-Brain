import csv, statistics as st, random
from collections import defaultdict
OUT='/home/user/INMA-/research-vault/backtest/out/'
panel=list(csv.DictReader(open(OUT+'daily_panel.csv')))
bys=defaultdict(list)
for r in panel: bys[r['sym']].append(r)
for s in bys: bys[s].sort(key=lambda r:r['date'])

def fwd(rows,h):
    for i,r in enumerate(rows):
        r['fwd%d'%h] = 100*(float(rows[i+h]['close'])/float(r['close'])-1) if i+h<len(rows) else None
for s in bys:
    for h in (5,10,21,42): fwd(bys[s],h)
rows=[r for s in bys for r in bys[s]]

def stat(sel,h,label):
    v=[r['fwd%d'%h] for r in sel if r['fwd%d'%h] is not None]
    dropped=len(sel)-len(v)
    if not v: return None
    return (label,h,len(v),dropped,st.mean(v),st.median(v),100*sum(1 for x in v if x>0)/len(v))

rsi70=[r for r in rows if float(r['rsi14'])>70]
rsi75=[r for r in rows if float(r['rsi14'])>75]
rsi80=[r for r in rows if float(r['rsi14'])>80]
h20=[r for r in rows if float(r['is_20d_high'])==1]
rsi30=[r for r in rows if float(r['rsi14'])<30]
l20=[r for r in rows if float(r['is_20d_low'])==1]
print("counts: rsi>70",len(rsi70),"rsi>75",len(rsi75),"rsi>80",len(rsi80),"is20dhigh",len(h20),"rsi<30",len(rsi30),"is20dlow",len(l20))
print(f"{'set':14s}{'h':>4s}{'n':>6s}{'drop':>6s}{'mean%':>9s}{'med%':>8s}{'%pos':>7s}")
for lab,sel in [("ALL",rows),("rsi>70",rsi70),("rsi>75",rsi75),("rsi>80",rsi80),("is_20d_high",h20),("rsi<30",rsi30),("is_20d_low",l20)]:
    for h in (5,10,21,42):
        s=stat(sel,h,lab)
        if s: print(f"{s[0]:14s}{s[1]:4d}{s[2]:6d}{s[3]:6d}{s[4]:9.3f}{s[5]:8.3f}{s[6]:7.1f}")
    print()

# ---- power: how big is the noise on the rsi>70 10d mean? ----
for h in (10,21):
    v=[r['fwd%d'%h] for r in rsi70 if r['fwd%d'%h] is not None]
    a=[r['fwd%d'%h] for r in rows if r['fwd%d'%h] is not None]
    sd=st.pstdev(v)
    naive_se=sd/len(v)**0.5
    eff=len(v)/h                       # overlap-corrected effective n
    adj_se=sd/eff**0.5
    print(f"h={h}: rsi>70 mean={st.mean(v):.3f}% sd={sd:.3f} n={len(v)} naiveSE={naive_se:.3f} overlap-adj n_eff={eff:.0f} SE={adj_se:.3f}  ALLmean={st.mean(a):.3f}%  diff={st.mean(v)-st.mean(a):+.3f}%")
    lo,hi=st.mean(v)-1.96*adj_se, st.mean(v)+1.96*adj_se
    print(f"      95%% CI on rsi>70 {h}d mean: [{lo:.2f}%, {hi:.2f}%]  -> cannot exclude reversion down to {lo:.2f}%")

# ---- non-overlapping sample ----
for h in (10,21):
    v=[]
    for s in bys:
        rr=bys[s]; i=0
        while i<len(rr):
            if float(rr[i]['rsi14'])>70 and rr[i]['fwd%d'%h] is not None:
                v.append(rr[i]['fwd%d'%h]); i+=h
            else: i+=1
    print(f"NON-OVERLAPPING rsi>70 h={h}: n={len(v)} mean={st.mean(v):.3f}% %pos={100*sum(1 for x in v if x>0)/len(v):.1f}%")

# ---- per-year stability of the rsi>70 10d edge ----
print("\nrsi>70 fwd10 by year:")
byyr=defaultdict(list)
for r in rsi70:
    if r['fwd10'] is not None: byyr[r['date'][:4]].append(r['fwd10'])
allyr=defaultdict(list)
for r in rows:
    if r['fwd10'] is not None: allyr[r['date'][:4]].append(r['fwd10'])
for y in sorted(byyr):
    print(f"  {y}: n={len(byyr[y]):4d} rsi>70 mean={st.mean(byyr[y]):+7.3f}%   ALL mean={st.mean(allyr[y]):+7.3f}%   diff={st.mean(byyr[y])-st.mean(allyr[y]):+.3f}")

# ---- prevalence ceiling on lift ----
print("\nLIFT CEILING (max lift = 1/prevalence):")
for lab,sel,tgtn in [("is_20d_high",h20,173),("is_20d_low",l20,167)]:
    prev=len(sel)/len(rows)
    print(f"  {lab}: prevalence={100*prev:.2f}%  max possible lift={1/prev:.2f}x")
