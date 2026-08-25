import csv, collections, random, statistics as st
OUT='/home/user/INMA-/research-vault/backtest/out/'
tr=list(csv.DictReader(open(OUT+'oracle_features.csv')))
pn=list(csv.DictReader(open(OUT+'daily_panel.csv')))
F=lambda x: float(x) if x not in ('','None') else None
# panel indexed by (sym,date)
pidx={(r['sym'],r['date']):r for r in pn}
bysm=collections.defaultdict(list)
for r in pn: bysm[(r['sym'],r['date'][:7])].append(r)
for k in bysm: bysm[k].sort(key=lambda r:r['date'])

print("=== days_to_opex range in panel ===")
d=[F(r['days_to_opex']) for r in pn]
print("min",min(d),"max",max(d), "uniq sample", sorted(set(d))[:8], sorted(set(d))[-5:])
print("=== dow codes ===", sorted(collections.Counter(r['dow'] for r in pn).items()))
print("=== tday_in_month panel ===", sorted(collections.Counter(int(F(r['tday_in_month'])) for r in pn).items()))
print("=== tdays_in_month ===", sorted(collections.Counter(int(F(r['tdays_in_month'])) for r in pn).items()))
print("=== turn_of_month base ===", collections.Counter(r['is_turn_of_month'] for r in pn))
print("=== opex_week base ===", collections.Counter(r['is_opex_week'] for r in pn))
print("=== qtr_end_month base ===", collections.Counter(r['is_quarter_end_month'] for r in pn))
