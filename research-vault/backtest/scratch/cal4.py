import csv, collections, pickle, statistics as st
OUT='/home/user/INMA-/research-vault/backtest/out/'
tr=list(csv.DictReader(open(OUT+'oracle_features.csv')))
pn=list(csv.DictReader(open(OUT+'daily_panel.csv')))
N=pickle.load(open('/home/user/INMA-/research-vault/backtest/scratch/null.pkl','rb'))
F=lambda x: float(x) if x not in ('','None') else None

def dist(vals):
    c=collections.Counter(vals); n=sum(c.values())
    return {k:v/n for k,v in c.items()}, c, n
def pdist(d):
    n=sum(d.values()); return {k:v/n for k,v in d.items()}

def report(name, obs_vals, panel_col, nullkey, feat, order=None):
    od,oc,on=dist(obs_vals)
    pd_,pc,pnn=dist([r[panel_col] for r in pn])
    nd=pdist(N[nullkey][feat])
    ks=order or sorted(set(list(od)+list(pd_)), key=lambda x: (F(x) if x.replace('-','').replace('.','').isdigit() else 0))
    print(f"\n--- {name} (n={on}) ---")
    print(f"{'val':>8} {'oracle%':>8} {'cnt':>5} {'panel%':>8} {'lift':>6} {'ordnull%':>9} {'lift_v_null':>11}")
    for k in ks:
        o=od.get(k,0)*100; p=pd_.get(k,0)*100; nu=nd.get(k,0)*100
        print(f"{k:>8} {o:8.2f} {oc.get(k,0):5d} {p:8.2f} {o/p if p else float('nan'):6.2f} {nu:9.2f} {o/nu if nu else float('nan'):11.2f}")

buys=tr; sells=tr
print("="*70); print("ALL BUYS vs panel vs order-stat null")
report("BUY dow", [r['B_dow'] for r in tr], 'dow','nullB','dow', order=['0','1','2','3','4'])
report("SELL dow", [r['S_dow'] for r in tr], 'dow','nullS','dow', order=['0','1','2','3','4'])
report("BUY turn_of_month", [r['B_is_turn_of_month'] for r in tr],'is_turn_of_month','nullB','is_turn_of_month',order=['0','1'])
report("SELL turn_of_month", [r['S_is_turn_of_month'] for r in tr],'is_turn_of_month','nullS','is_turn_of_month',order=['0','1'])
report("BUY opex_week", [r['B_is_opex_week'] for r in tr],'is_opex_week','nullB','is_opex_week',order=['0','1'])
report("SELL opex_week", [r['S_is_opex_week'] for r in tr],'is_opex_week','nullS','is_opex_week',order=['0','1'])
report("BUY tday_in_month", [r['B_tday_in_month'] for r in tr],'tday_in_month','nullB','tday_in_month')
report("SELL tday_in_month", [r['S_tday_in_month'] for r in tr],'tday_in_month','nullS','tday_in_month')
