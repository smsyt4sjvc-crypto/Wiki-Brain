import csv, statistics as st
from collections import defaultdict
B='/home/user/INMA-/research-vault/backtest/out/'
panel=list(csv.DictReader(open(B+'daily_panel.csv')))
tr=list(csv.DictReader(open(B+'oracle_features.csv')))
def f(x):
    try: return float(x)
    except: return None
bym=defaultdict(list)
for r in panel: bym[(r['sym'],r['date'][:7])].append(r)
print("=== sell percentile by leg ===")
for leg in ['1','2']:
    sub=[t for t in tr if t['leg']==leg]
    for c in ['dist_sma20_pct','dd_from_20d_high_pct']:
        ps=[]
        for t in sub:
            vals=[f(d[c]) for d in bym[(t['sym'],t['month'])]]; v=f(t['S_'+c])
            ps.append((sum(1 for x in vals if x<v)+0.5*sum(1 for x in vals if x==v))/len(vals))
        print(f"  leg{leg} S_{c:24s} meanPct {st.mean(ps):.3f} n={len(sub)}")
print("\n=== 20d low / 20d high flags ===")
for c in ['is_20d_low','is_20d_high','is_63d_low','is_63d_high']:
    b=sum(1 for t in tr if t['B_'+c]=='1')/176; s=sum(1 for t in tr if t['S_'+c]=='1')/176
    d=sum(1 for r in panel if r[c]=='1')/len(panel)
    print(f"  {c:14s} buy {b*100:5.1f}%  sell {s*100:5.1f}%  base {d*100:5.1f}%  lift_buy {b/d if d else 0:5.2f}x  lift_sell {s/d if d else 0:5.2f}x")
print("\n=== oracle month haul vs regime depth: per sym-month ===")
mo=defaultdict(list)
for t in tr: mo[(t['sym'],t['month'])].append(t)
rows=[]
for k,ts in mo.items():
    ds=bym[k]
    rows.append((min(f(d['dd_from_252d_high_pct']) for d in ds), sum(f(t['ret_pct']) for t in ts), st.median([f(d['realvol20_ann_pct']) for d in ds]), k))
rows.sort()
qs=[rows[:22],rows[22:44],rows[44:66],rows[66:]]
for i,g in enumerate(qs):
    print(f"  Q{i+1} by month-depth (deepest first): n={len(g)} medMinDd252 {st.median([r[0] for r in g]):7.2f}  medSumLegs {st.median([r[1] for r in g]):6.2f}%  medRealVol {st.median([r[2] for r in g]):5.1f}")
print("\n  deepest 6 months:", [(r[3],round(r[0],1),round(r[1],1)) for r in rows[:6]])
print("  shallowest 6:", [(r[3],round(r[0],1),round(r[1],1)) for r in rows[-6:]])
