import csv, collections, pickle
OUT='/home/user/INMA-/research-vault/backtest/out/'
tr=list(csv.DictReader(open(OUT+'oracle_features.csv')))
pn=list(csv.DictReader(open(OUT+'daily_panel.csv')))
F=lambda x: float(x) if x not in ('','None') else None
print("TOM flag by tday_in_month (panel):")
c=collections.defaultdict(collections.Counter)
for r in pn: c[int(F(r['tday_in_month']))][r['is_turn_of_month']]+=1
for k in sorted(c): print(" tday",k,dict(c[k]))
print("\nTOM flag by tdays_to_month_end:")
c2=collections.defaultdict(collections.Counter)
for r in pn: c2[int(F(r['tdays_to_month_end']))][r['is_turn_of_month']]+=1
for k in sorted(c2)[:8]: print(" tte",k,dict(c2[k]))
print("\nopex_week by days_to_opex:")
c3=collections.defaultdict(collections.Counter)
for r in pn: c3[int(F(r['days_to_opex']))][r['is_opex_week']]+=1
for k in sorted(c3): print(" dto",k,dict(c3[k]))
