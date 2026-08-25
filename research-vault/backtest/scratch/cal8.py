import csv, collections, statistics as st, pickle
OUT='/home/user/INMA-/research-vault/backtest/out/'
tr=list(csv.DictReader(open(OUT+'oracle_features.csv')))
pn=list(csv.DictReader(open(OUT+'daily_panel.csv')))
F=lambda x: float(x) if x not in('','None') else None
PN=len(pn)
pdow=collections.Counter(r['dow'] for r in pn)
def corr(a,b):
    ma,mb=st.mean(a),st.mean(b)
    num=sum((x-ma)*(y-mb) for x,y in zip(a,b))
    return num/((sum((x-ma)**2 for x in a)*sum((y-mb)**2 for y in b))**.5)

# oracle opportunity stability
bysym=collections.defaultdict(list)
for r in pn: bysym[r['sym']].append(r)
for k in bysym: bysym[k].sort(key=lambda r:r['date'])
info={}
for s,rows in bysym.items():
    mm=collections.OrderedDict()
    for r in rows: mm.setdefault(r['date'][:7],[]).append(r)
    for m,w in mm.items():
        info[(s,m)]=(100*(F(w[-1]['close'])/F(w[0]['close'])-1), st.mean([F(r['realvol20_ann_pct']) for r in w]), st.mean([F(r['atr14_pct']) for r in w]), len(w))
seen=set(); O=[];B=[];V=[];A=[]
for r in tr:
    k=(r['sym'],r['month'])
    if k in seen: continue
    seen.add(k); O.append(F(r['month_total_pct'])); B.append(info[k][0]); V.append(info[k][1]); A.append(info[k][2])
print(f"n sym-months={len(O)}")
print(f"oracle month_total: mean={st.mean(O):.2f} sd={st.pstdev(O):.2f} min={min(O):.2f} max={max(O):.2f} CV={st.pstdev(O)/st.mean(O):.2f}")
print(f"buy&hold month:     mean={st.mean(B):.2f} sd={st.pstdev(B):.2f} min={min(B):.2f} max={max(B):.2f}")
print(f"corr(oracle_total, bh_month_ret)={corr(O,B):+.3f}")
print(f"corr(oracle_total, mean realvol20)={corr(O,V):+.3f}   corr(oracle_total, mean atr14%)={corr(O,A):+.3f}")

# DOW excluding turn-of-month days (control for month-edge effect)
pn_ntom=[r for r in pn if r['is_turn_of_month']=='0']
pdow2=collections.Counter(r['dow'] for r in pn_ntom); P2=len(pn_ntom)
print(f"\n=== DOW, EXCLUDING turn-of-month days (panel n={P2}) ===")
for side,pre in (('BUY','B_'),('SELL','S_')):
    rows=[r for r in tr if r[pre+'is_turn_of_month']=='0']; n=len(rows)
    c=collections.Counter(r[pre+'dow'] for r in rows)
    print(f"{side} n={n}: " + " ".join(f"{d}:{c.get(d,0):3d} {100*c.get(d,0)/n:5.1f}% base {100*pdow2[d]/P2:5.1f}% lift {(c.get(d,0)/n)/(pdow2[d]/P2):4.2f}" for d in '01234'))

# DOW by year (stability)
print("\n=== BUY-Mon / SELL-Thu+Fri by year ===")
for yr in ('2023','2024','2025','2026'):
    rows=[r for r in tr if r['buy_date'][:4]==yr]; n=len(rows)
    bm=sum(r['B_dow']=='0' for r in rows); stf=sum(r['S_dow'] in '34' for r in rows)
    print(f"{yr} n={n:3d} buyMon {bm:3d} ({100*bm/n:5.1f}% vs 18.8%)  sellThuFri {stf:3d} ({100*stf/n:5.1f}% vs 39.9%)")

# composite: net buy-minus-sell count by dow
print("\n=== net (buys - sells) by dow ===")
cb=collections.Counter(r['B_dow'] for r in tr); cs=collections.Counter(r['S_dow'] for r in tr)
for d in '01234': print(f" dow {d}: buys {cb[d]:3d} sells {cs[d]:3d} net {cb[d]-cs[d]:+4d}  (expected 0)")

# pct_through_month
N=pickle.load(open('/home/user/INMA-/research-vault/backtest/scratch/null.pkl','rb'))
print("\n=== pct_through_month deciles ===")
def dec(v): return min(9,int(F(v)*10))
pp=collections.Counter(dec(r['pct_through_month']) for r in pn)
for side,pre,nk in (('BUY','B_','nullB'),('SELL','S_','nullS')):
    c=collections.Counter(dec(r[pre+'pct_through_month']) for r in tr)
    nn=collections.Counter()
    for k,v in N[nk]['pct_through_month'].items(): nn[dec(k)]+=v
    tn=sum(nn.values())
    print(side+": "+" ".join(f"d{d}:{c.get(d,0)}({(c.get(d,0)/176)/(pp[d]/PN):.2f}|n{(c.get(d,0)/176)/(nn[d]/tn):.2f})" for d in range(10)))

# turn of month: BUY at first2 by sym and by year
print("\n=== buy in first 2 tdays of month (base rate 9.69%) ===")
for lbl,rows in (('all',tr),('spx',[r for r in tr if r['sym']=='spx']),('ndx',[r for r in tr if r['sym']=='ndx']),
                 ('2023',[r for r in tr if r['buy_date'][:4]=='2023']),('2024',[r for r in tr if r['buy_date'][:4]=='2024']),
                 ('2025',[r for r in tr if r['buy_date'][:4]=='2025']),('2026',[r for r in tr if r['buy_date'][:4]=='2026'])):
    n=len(rows); c=sum(int(F(r['B_tday_in_month']))<=2 for r in rows)
    print(f" {lbl:5} n={n:3d} {c:3d} ({100*c/n:5.1f}%) lift {(c/n)/0.0969:.2f}")
