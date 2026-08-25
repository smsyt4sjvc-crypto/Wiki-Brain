import csv, collections, pickle, math
OUT='/home/user/INMA-/research-vault/backtest/out/'
tr=list(csv.DictReader(open(OUT+'oracle_features.csv')))
pn=list(csv.DictReader(open(OUT+'daily_panel.csv')))
N=pickle.load(open('/home/user/INMA-/research-vault/backtest/scratch/null.pkl','rb'))
F=lambda x: float(x) if x not in ('','None') else None
def pdist(d):
    n=sum(d.values()); return {k:v/n for k,v in d.items()}

# ---- TOM decomposition: start-TOM (tday<=2) vs end-TOM (tte<=1) ----
def tomclass(tday,tte):
    if tday<=2: return 'start'
    if tte<=1: return 'end'
    return 'mid'
pc=collections.Counter(tomclass(int(F(r['tday_in_month'])),int(F(r['tdays_to_month_end']))) for r in pn)
pn_n=len(pn)
print("panel TOM class:", {k:(v,round(100*v/pn_n,2)) for k,v in pc.items()})
for side,pre in (('BUY','B_'),('SELL','S_')):
    for sub,rows in (('all',tr),('leg1',[r for r in tr if r['leg']=='1']),('leg2',[r for r in tr if r['leg']=='2']),
                     ('spx',[r for r in tr if r['sym']=='spx']),('ndx',[r for r in tr if r['sym']=='ndx'])):
        c=collections.Counter(tomclass(int(F(r[pre+'tday_in_month'])),int(F(r[pre+'tdays_to_month_end']))) for r in rows)
        n=len(rows)
        print(f"{side:4} {sub:5} n={n:3}", {k:f"{c.get(k,0)}({100*c.get(k,0)/n:.1f}%,lift{(c.get(k,0)/n)/(pc[k]/pn_n):.2f})" for k in ('start','mid','end')})

print("\n==== leg1 vs leg2 tday medians ====")
import statistics as st
for pre,lbl in (('B_','buy'),('S_','sell')):
    for leg in ('1','2'):
        v=[F(r[pre+'tday_in_month']) for r in tr if r['leg']==leg]
        p=[F(r[pre+'pct_through_month']) for r in tr if r['leg']==leg]
        print(f"{lbl} leg{leg}: median tday={st.median(v):.1f} mean={st.mean(v):.1f} | median pct_through={st.median(p):.3f}")
pp=[F(r['pct_through_month']) for r in pn]
print("panel median pct_through_month",st.median(pp), "mean",round(st.mean(pp),3))

print("\n==== OPEX week: buy/sell/hold coverage ====")
# build date index per sym to compute holding days
bysym=collections.defaultdict(list)
for r in pn: bysym[r['sym']].append(r)
for k in bysym: bysym[k].sort(key=lambda r:r['date'])
pos={s:{r['date']:i for i,r in enumerate(v)} for s,v in bysym.items()}
hold_ow=0; hold_tot=0; hold_tom=0
for r in tr:
    s=r['sym']; a=pos[s][r['buy_date']]; b=pos[s][r['sell_date']]
    for i in range(a,b+1):
        row=bysym[s][i]; hold_tot+=1
        hold_ow+= int(row['is_opex_week']); hold_tom+=int(row['is_turn_of_month'])
print(f"held days n={hold_tot}: opex_week {hold_ow} ({100*hold_ow/hold_tot:.1f}%) vs panel 31.98% lift {(hold_ow/hold_tot)/0.3198:.2f}")
print(f"held days: TOM {hold_tom} ({100*hold_tom/hold_tot:.1f}%) vs panel 19.37% lift {(hold_tom/hold_tot)/0.1937:.2f}")

print("\n==== opex week by leg / sym (buys) ====")
for sub,rows in (('leg1',[r for r in tr if r['leg']=='1']),('leg2',[r for r in tr if r['leg']=='2']),
                 ('spx',[r for r in tr if r['sym']=='spx']),('ndx',[r for r in tr if r['sym']=='ndx'])):
    n=len(rows)
    bo=sum(int(r['B_is_opex_week']) for r in rows); so=sum(int(r['S_is_opex_week']) for r in rows)
    print(f"{sub:5} n={n} buy_opexwk {bo} ({100*bo/n:.1f}%, lift {(bo/n)/0.3198:.2f})  sell_opexwk {so} ({100*so/n:.1f}%, lift {(so/n)/0.3198:.2f})")

print("\n==== DOW by leg/sym ====")
pdow=collections.Counter(r['dow'] for r in pn); pn_n=len(pn)
for side,pre in (('BUY','B_'),('SELL','S_')):
    for sub,rows in (('all',tr),('leg1',[r for r in tr if r['leg']=='1']),('leg2',[r for r in tr if r['leg']=='2']),
                     ('spx',[r for r in tr if r['sym']=='spx']),('ndx',[r for r in tr if r['sym']=='ndx'])):
        c=collections.Counter(r[pre+'dow'] for r in rows); n=len(rows)
        print(f"{side:4} {sub:5} n={n:3} " + " ".join(f"{d}:{c.get(d,0):3d}({(c.get(d,0)/n)/(pdow[d]/pn_n):.2f})" for d in '01234'))
