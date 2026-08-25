import csv, collections, statistics as st, pickle
OUT='/home/user/INMA-/research-vault/backtest/out/'
tr=list(csv.DictReader(open(OUT+'oracle_features.csv')))
pn=list(csv.DictReader(open(OUT+'daily_panel.csv')))
N=pickle.load(open('/home/user/INMA-/research-vault/backtest/scratch/null.pkl','rb'))
F=lambda x: float(x) if x not in('','None') else None

# --- SPX/NDX co-timing (effective n) ---
d=collections.defaultdict(dict)
for r in tr: d[(r['month'],r['leg'])][r['sym']]=r
same_b=same_s=0; n=0; w1b=w1s=0
for k,v in d.items():
    if len(v)<2: continue
    n+=1
    a,b=v['spx'],v['ndx']
    same_b+= a['buy_date']==b['buy_date']; same_s+= a['sell_date']==b['sell_date']
    import datetime as dt
    f=lambda s: dt.date.fromisoformat(s)
    w1b += abs((f(a['buy_date'])-f(b['buy_date'])).days)<=1
    w1s += abs((f(a['sell_date'])-f(b['sell_date'])).days)<=1
print(f"SPX/NDX same buy_date {same_b}/{n} ({100*same_b/n:.0f}%); same sell_date {same_s}/{n} ({100*same_s/n:.0f}%); within1cal buy {w1b} sell {w1s}")

# --- calendar month of year: counts are FIXED by construction; test RETURNS ---
print("\n=== month-of-year: oracle month_total_pct vs buy&hold month return ===")
bysym=collections.defaultdict(list)
for r in pn: bysym[r['sym']].append(r)
for k in bysym: bysym[k].sort(key=lambda r:r['date'])
bh={}
for s,rows in bysym.items():
    mm=collections.OrderedDict()
    for r in rows: mm.setdefault(r['date'][:7],[]).append(r)
    for m,w in mm.items(): bh[(s,m)]=100*(F(w[-1]['close'])/F(w[0]['close'])-1)
seen=set(); rows=[]
for r in tr:
    k=(r['sym'],r['month'])
    if k in seen: continue
    seen.add(k); rows.append((k,F(r['month_total_pct']),bh[k],int(r['month'][5:7]),int(r['month'][:4]),int(r['B_is_quarter_end_month'])))
print(f"n sym-months={len(rows)}")
bym=collections.defaultdict(list)
for k,tot,b,mo,yr,qe in rows: bym[mo].append((tot,b))
print(f"{'mo':>3} {'n':>3} {'oracle_med':>10} {'oracle_mean':>11} {'bh_mean':>8} {'ratio':>6}")
for mo in sorted(bym):
    v=bym[mo]; o=[x[0] for x in v]; b=[x[1] for x in v]
    print(f"{mo:3d} {len(v):3d} {st.median(o):10.2f} {st.mean(o):11.2f} {st.mean(b):8.2f} {st.mean(o)/abs(st.mean(b)) if st.mean(b) else float('nan'):6.2f}")
allo=[x[1] for x in rows]; allb=[x[2] for x in rows]
print(f"ALL n={len(rows)} oracle_mean={st.mean(allo):.2f} median={st.median(allo):.2f} bh_mean={st.mean(allb):.2f}")
byy=collections.defaultdict(list)
for k,tot,b,mo,yr,qe in rows: byy[yr].append((tot,b))
print("\n=== year ===")
for yr in sorted(byy):
    v=byy[yr]; o=[x[0] for x in v]; b=[x[1] for x in v]
    print(f"{yr} n={len(v):3d} oracle_mean={st.mean(o):6.2f} median={st.median(o):6.2f} bh_mean={st.mean(b):6.2f}")
qe=[x[1] for x in rows if x[5]==1]; nqe=[x[1] for x in rows if x[5]==0]
qeb=[x[2] for x in rows if x[5]==1]; nqeb=[x[2] for x in rows if x[5]==0]
print(f"\nquarter-end months n={len(qe)} oracle_mean={st.mean(qe):.2f} med={st.median(qe):.2f} bh={st.mean(qeb):.2f}")
print(f"other months      n={len(nqe)} oracle_mean={st.mean(nqe):.2f} med={st.median(nqe):.2f} bh={st.mean(nqeb):.2f}")

# --- per-trade ret by buy dow / buy TOM ---
print("\n=== per-trade ret_pct by BUY dow ===")
byd=collections.defaultdict(list)
for r in tr: byd[r['B_dow']].append(F(r['ret_pct']))
for k in sorted(byd): print(f" dow {k} n={len(byd[k]):3d} mean={st.mean(byd[k]):5.2f} med={st.median(byd[k]):5.2f}")
print("all trades mean ret", round(st.mean([F(r['ret_pct']) for r in tr]),2))

# --- same-day trades ---
sd=[r for r in tr if int(F(r['hold_days']))==0]
print(f"\n=== same-day trades n={len(sd)} ===")
print(" dow:", sorted(collections.Counter(r['B_dow'] for r in sd).items()))
print(" TOM:", collections.Counter(r['B_is_turn_of_month'] for r in sd))
print(" opexwk:", collections.Counter(r['B_is_opex_week'] for r in sd))
print(" leg:", collections.Counter(r['leg'] for r in sd), " sym:",collections.Counter(r['sym'] for r in sd))
print(" tday:", sorted(collections.Counter(int(F(r['B_tday_in_month'])) for r in sd).items()))

# --- days_to_opex fine ---
print("\n=== days_to_opex ===")
pdo=collections.Counter(int(F(r['days_to_opex'])) for r in pn); PN=len(pn)
bdo=collections.Counter(int(F(r['B_days_to_opex'])) for r in tr); sdo=collections.Counter(int(F(r['S_days_to_opex'])) for r in tr)
nb=pdist=None
nbd={int(F(k)):v for k,v in N['nullB']['days_to_opex'].items()}; tb=sum(nbd.values())
nsd={int(F(k)):v for k,v in N['nullS']['days_to_opex'].items()}; ts=sum(nsd.values())
print(f"{'dto':>4} {'panel%':>7} {'buy':>4} {'buy%':>6} {'lift':>5} {'null%':>6} | {'sell':>4} {'sell%':>6} {'lift':>5} {'null%':>6}")
for k in sorted(pdo):
    p=100*pdo[k]/PN
    print(f"{k:4d} {p:7.2f} {bdo.get(k,0):4d} {100*bdo.get(k,0)/176:6.2f} {(bdo.get(k,0)/176)/(pdo[k]/PN):5.2f} {100*nbd.get(k,0)/tb:6.2f} | {sdo.get(k,0):4d} {100*sdo.get(k,0)/176:6.2f} {(sdo.get(k,0)/176)/(pdo[k]/PN):5.2f} {100*nsd.get(k,0)/ts:6.2f}")
