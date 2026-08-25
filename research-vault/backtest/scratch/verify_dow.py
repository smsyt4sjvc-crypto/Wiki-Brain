import csv, datetime, math
from collections import Counter, defaultdict

OUT='/home/user/INMA-/research-vault/backtest/out/'
panel=list(csv.DictReader(open(OUT+'daily_panel.csv')))
tr=list(csv.DictReader(open(OUT+'oracle_features.csv')))
print("panel rows",len(panel),"trades",len(tr))

names=['Mon','Tue','Wed','Thu','Fri']
# sanity: dow encoding
for r in panel[:3]:
    d=datetime.date.fromisoformat(r['date'])
    print(r['date'], 'dow_col',r['dow'],'python_wd',d.weekday())

# 1. panel weekday shares
pw=Counter(int(r['dow']) for r in panel)
print("\n--- PANEL weekday counts (all rows, both syms) ---")
for k in sorted(pw): print(names[k] if k<5 else k, pw[k], round(100*pw[k]/len(panel),3))

# panel per-sym check
for s in set(r['sym'] for r in panel):
    sub=[r for r in panel if r['sym']==s]
    c=Counter(int(r['dow']) for r in sub)
    print(s,len(sub),{names[k]:c[k] for k in sorted(c)})

# turn of month distinct values
print("\nis_turn_of_month values:",Counter(r['is_turn_of_month'] for r in panel))

ntom=[r for r in panel if r['is_turn_of_month'] in ('0','0.0','False')]
print("panel ex-TOM rows",len(ntom))
pw2=Counter(int(r['dow']) for r in ntom)
for k in sorted(pw2): print(" ex-TOM",names[k],pw2[k],round(100*pw2[k]/len(ntom),3))

# 2. trade weekday counts
bw=Counter(int(r['B_dow']) for r in tr)
sw=Counter(int(r['S_dow']) for r in tr)
print("\n--- TRADES ---")
n=len(tr)
for k in range(5):
    exp=pw[k]/len(panel)*n
    sd=math.sqrt(n*(pw[k]/len(panel))*(1-pw[k]/len(panel)))
    print(f"BUY {names[k]}: {bw[k]:3d} ({100*bw[k]/n:5.2f}%) base {100*pw[k]/len(panel):5.2f}% lift {bw[k]/exp:.3f} exp {exp:.1f} sd {sd:.2f} z {(bw[k]-exp)/sd:+.2f}")
for k in range(5):
    exp=pw[k]/len(panel)*n
    sd=math.sqrt(n*(pw[k]/len(panel))*(1-pw[k]/len(panel)))
    print(f"SELL {names[k]}: {sw[k]:3d} ({100*sw[k]/n:5.2f}%) base {100*pw[k]/len(panel):5.2f}% lift {sw[k]/exp:.3f} exp {exp:.1f} sd {sd:.2f} z {(sw[k]-exp)/sd:+.2f}")
print("net buys-minus-sells:",{names[k]:bw[k]-sw[k] for k in range(5)})

# 3. ex-TOM
btr=[r for r in tr if r['B_is_turn_of_month'] in ('0','0.0','False')]
str_=[r for r in tr if r['S_is_turn_of_month'] in ('0','0.0','False')]
print("\n--- EX TURN OF MONTH ---")
print("buy trades ex-TOM",len(btr),"sell trades ex-TOM",len(str_))
bw2=Counter(int(r['B_dow']) for r in btr); sw2=Counter(int(r['S_dow']) for r in str_)
for k in range(5):
    p=pw2[k]/len(ntom)
    exp=p*len(btr); sd=math.sqrt(len(btr)*p*(1-p))
    print(f"BUY {names[k]}: {bw2[k]:3d}/{len(btr)} base {100*p:5.2f}% lift {bw2[k]/exp:.3f} z {(bw2[k]-exp)/sd:+.2f}")
for k in range(5):
    p=pw2[k]/len(ntom)
    exp=p*len(str_); sd=math.sqrt(len(str_)*p*(1-p))
    print(f"SELL {names[k]}: {sw2[k]:3d}/{len(str_)} base {100*p:5.2f}% lift {sw2[k]/exp:.3f} z {(sw2[k]-exp)/sd:+.2f}")

# 4. year-by-year sell Thu/Fri
print("\n--- SELL Thu|Fri by year ---")
by=defaultdict(list)
for r in tr: by[r['S_year']].append(int(r['S_dow']))
pbase=(pw[3]+pw[4])/len(panel)
for y in sorted(by):
    v=by[y]; c=sum(1 for x in v if x in (3,4))
    # panel base for that year
    py=[r for r in panel if r['year']==y]
    pc=sum(1 for r in py if int(r['dow']) in (3,4))
    print(f"{y}: {c}/{len(v)} = {100*c/len(v):5.1f}%  panel-that-year {100*pc/len(py):5.1f}% (n_panel {len(py)})")
print("panel overall Thu+Fri",round(100*pbase,2))

print("\n--- BUY Mon by year ---")
byb=defaultdict(list)
for r in tr: byb[r['B_year']].append(int(r['B_dow']))
for y in sorted(byb):
    v=byb[y]; c=sum(1 for x in v if x==0)
    py=[r for r in panel if r['year']==y]
    pc=sum(1 for r in py if int(r['dow'])==0)
    print(f"{y}: {c}/{len(v)} = {100*c/len(v):5.1f}%  panel {100*pc/len(py):5.1f}%")
