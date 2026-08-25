import csv, statistics as st
from collections import defaultdict
D='/home/user/INMA-/research-vault/backtest/out/'
panel=list(csv.DictReader(open(D+'daily_panel.csv')))
bysym=defaultdict(list)
for r in panel: bysym[r['sym']].append(r)
for s in bysym: bysym[s].sort(key=lambda x:x['date'])
for s,rows in bysym.items():
    c=[float(x['close']) for x in rows]
    for h in (5,21):
        for i,x in enumerate(rows): x['f%d'%h]=(c[i+h]/c[i]-1)*100 if i+h<len(c) else None
A=[x for s in bysym for x in bysym[s]]
b5=[x['f5'] for x in A if x['f5'] is not None]; b21=[x['f21'] for x in A if x['f21'] is not None]
print('BASE n=%d 5d mean %+.2f med %+.2f pos %.0f%% | 21d mean %+.2f med %+.2f'%(len(b5),st.mean(b5),st.median(b5),100*sum(1 for v in b5 if v>0)/len(b5),st.mean(b21),st.median(b21)))
conds={'is_20d_low':lambda x:x['is_20d_low']=='1','is_63d_low':lambda x:x['is_63d_low']=='1',
 'rsi14<30':lambda x:float(x['rsi14'])<30,'rsi14<35':lambda x:float(x['rsi14'])<35,'rsi14<25':lambda x:float(x['rsi14'])<25,
 'bb_pctB<0.05':lambda x:float(x['bb_pctB'])<0.05,'bb_pctB<0.02':lambda x:float(x['bb_pctB'])<0.02,
 'dd63>5%':lambda x:float(x['dd_from_63d_high_pct'])<=-5,'dd63>8%':lambda x:float(x['dd_from_63d_high_pct'])<=-8,
 'dd252>10%':lambda x:float(x['dd_from_252d_high_pct'])<=-10,'consec_down>=3':lambda x:float(x['consec_down_days'])>=3,
 'dist_sma50<-5%':lambda x:float(x['dist_sma50_pct'])<=-5,'ret_5d<-4%':lambda x:float(x['ret_5d_pct'])<=-4}
print('\n%-18s %4s %8s %8s %6s %8s %8s'%('cond','n','5dmean','5dmed','pos%','21dmean','21dmed'))
for k,f in sorted(conds.items()):
    S=[x for x in A if f(x)]
    v5=[x['f5'] for x in S if x['f5'] is not None]; v21=[x['f21'] for x in S if x['f21'] is not None]
    if len(v5)<20: print('%-18s n=%d SKIP'%(k,len(v5))); continue
    print('%-18s %4d %+8.2f %+8.2f %5.0f%% %+8.2f %+8.2f'%(k,len(v5),st.mean(v5),st.median(v5),100*sum(1 for v in v5 if v>0)/len(v5),st.mean(v21),st.median(v21)))
# symbol overlap in 63d lows
L=[x for x in A if x['is_63d_low']=='1']
d=defaultdict(list)
for x in L: d[x['date']].append(x['sym'])
print('\n63d_low: %d rows, %d unique dates, %d dates present in BOTH symbols'%(len(L),len(d),sum(1 for v in d.values() if len(v)==2)))
