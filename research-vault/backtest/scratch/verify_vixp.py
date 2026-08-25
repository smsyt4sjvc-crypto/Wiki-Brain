import csv, statistics as st
from collections import defaultdict
P='/home/user/INMA-/research-vault/backtest/out/'
panel=list(csv.DictReader(open(P+'daily_panel.csv')))
tr=list(csv.DictReader(open(P+'oracle_features.csv')))
print("panel rows",len(panel),"trades",len(tr))
def f(r,k):
    v=r.get(k,'')
    return None if v in ('','NA','nan',None) else float(v)
# missingness
for k in ['vix','vix_pctile_252d']:
    miss=sum(1 for r in panel if f(r,k) is None)
    print("panel missing",k,miss)
for k in ['B_vix','B_vix_pctile_252d']:
    miss=sum(1 for r in tr if f(r,k) is None)
    print("trade missing",k,miss)
vp=[f(r,'vix_pctile_252d') for r in panel]; vp=[x for x in vp if x is not None]
vv=[f(r,'vix') for r in panel]; vv=[x for x in vv if x is not None]
print("panel vix_pctile mean %.2f median %.2f"%(st.mean(vp),st.median(vp)))
print("panel vix mean %.2f median %.2f"%(st.mean(vv),st.median(vv)))
def base(vals,pred): return sum(1 for x in vals if pred(x))/len(vals)
bvp=[f(r,'B_vix_pctile_252d') for r in tr]
bvv=[f(r,'B_vix') for r in tr]
cuts=[('vix_pctile>80',vp,bvp,lambda x:x>80),('vix_pctile>90',vp,bvp,lambda x:x>90),
      ('vix_pctile>75',vp,bvp,lambda x:x>75),('vix_pctile<20',vp,bvp,lambda x:x<20),
      ('vix>20',vv,bvv,lambda x:x>20),('vix>18',vv,bvv,lambda x:x>18),('vix>22',vv,bvv,lambda x:x>22)]
for name,pool,buys,pred in cuts:
    b=base(pool,pred); h=sum(1 for x in buys if pred(x)); r=h/len(buys)
    print("%-16s base %.3f  buys %d/%d = %.3f  lift %.2fx"%(name,b,h,len(buys),r,r/b))
# unique-date base rates (VIX is macro, panel double counts dates)
udates={}
for r in panel:
    udates[r['date']]=(f(r,'vix'),f(r,'vix_pctile_252d'))
uvv=[a for a,b in udates.values() if a is not None]; uvp=[b for a,b in udates.values() if b is not None]
print("unique dates",len(udates))
for name,pool,buys,pred in cuts:
    pool2 = uvp if 'pctile' in name else uvv
    b=base(pool2,pred); h=sum(1 for x in buys if pred(x)); r=h/len(buys)
    print("UNIQ %-16s base %.3f  lift %.2fx"%(name,b,r/b))
