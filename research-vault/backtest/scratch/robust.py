import csv, statistics as st, datetime, random
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
allrows=[x for s in bysym for x in bysym[s]]
base5=[x['f5'] for x in allrows if x['f5'] is not None]
base21=[x['f21'] for x in allrows if x['f21'] is not None]
print('BASE 5d mean %+.3f med %+.3f sd %.2f pos %.1f%% | 21d mean %+.3f med %+.3f'%(
 st.mean(base5),st.median(base5),st.pstdev(base5),100*sum(1 for v in base5 if v>0)/len(base5),st.mean(base21),st.median(base21)))
L=[x for x in allrows if x['is_63d_low']=='1']
v5=[x['f5'] for x in L]; v21=[x['f21'] for x in L if x['f21'] is not None]
print('63dLOW 5d mean %+.3f med %+.3f sd %.2f pos %d/%d=%.0f%% | 21d mean %+.3f med %+.3f'%(
 st.mean(v5),st.median(v5),st.pstdev(v5),sum(1 for v in v5 if v>0),len(v5),100*sum(1 for v in v5 if v>0)/len(v5),st.mean(v21),st.median(v21)))
se=st.pstdev(v5)/len(v5)**.5
print('SE of 63dlow 5d mean = %.3f pp ; diff vs base mean = %+.3f pp -> t=%.2f'%(se,st.mean(v5)-st.mean(base5),(st.mean(v5)-st.mean(base5))/se))
# episodes
def ep(rows):
    ds=sorted(set(x['date'] for x in rows)); out=[];prev=None
    for d in ds:
        dt=datetime.date.fromisoformat(d)
        if prev is None or (dt-prev).days>7: out.append(set())
        out[-1].add(d); prev=dt
    return out
E=ep(L)
print('\nLEAVE-ONE-EPISODE-OUT (5d median, 5d %pos, 21d mean):')
for e in E:
    keep=[x for x in L if x['date'] not in e]
    k5=[x['f5'] for x in keep]; k21=[x['f21'] for x in keep if x['f21'] is not None]
    print('  drop %s (n=%d) -> n=%d med %+.3f pos %.0f%% 21dmean %+.3f'%(min(e),len(L)-len(keep),len(keep),st.median(k5),100*sum(1 for v in k5 if v>0)/len(k5),st.mean(k21)))
# block bootstrap by episode
epi=[[x for x in L if x['date'] in e] for e in E]
random.seed(0); mm=[];pp=[]
for _ in range(20000):
    s=[]; 
    for _ in range(len(epi)): s+=random.choice(epi)
    f=[x['f5'] for x in s]; mm.append(st.median(f)); pp.append(sum(1 for v in f if v>0)/len(f))
mm.sort();pp.sort()
print('\nEPISODE BLOCK BOOTSTRAP (7 blocks, 20k):')
print('  5d median 95%% CI [%+.2f, %+.2f]  (base median %+.2f) -> %.1f%% of draws have median > base'%(mm[500],mm[19500],st.median(base5),100*sum(1 for v in mm if v>st.median(base5))/len(mm)))
print('  5d %%pos   95%% CI [%.0f%%, %.0f%%] (base %.0f%%) -> %.1f%% of draws >= base'%(100*pp[500],100*pp[19500],100*sum(1 for v in base5 if v>0)/len(base5),100*sum(1 for v in pp if v>=sum(1 for z in base5 if z>0)/len(base5))/len(pp)))
# oracle-side binomial fragility
print('\nORACLE SIDE: 16/54=29.6%% vs 20d-not-63d 34/85=40.0%%. Diff 10.4pp.')
# SE of difference of proportions
p1,n1,p2,n2=16/54,54,34/85,85
sed=((p1*(1-p1)/n1)+(p2*(1-p2)/n2))**.5
print('  SE(diff)=%.3f -> z=%.2f (and the 54 rows are ~7 independent episodes, so true z is far smaller)'%(sed,(p2-p1)/sed))
# how many days must flip
print('\nFRAGILITY: 5d pos count = %d/54. Base rate 61%% would need %d positives. Gap = %d days.'%(sum(1 for v in v5 if v>0),round(0.61*54),round(0.61*54)-sum(1 for v in v5 if v>0)))
