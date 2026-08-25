import csv, statistics as st
from collections import defaultdict
OUT="/home/user/INMA-/research-vault/backtest/out/"
def load(p):
    with open(p) as f: return list(csv.DictReader(f))
dp=load(OUT+"daily_panel.csv"); tr=load(OUT+"oracle_features.csv")
def f(r,k):
    v=r.get(k,'')
    try: return float(v)
    except: return None
by=defaultdict(list)
for r in dp: by[r['sym']].append(r)
for s in by: by[s].sort(key=lambda r:r['date'])
# forward measures per row
H=5
for s,rows in by.items():
    for i,r in enumerate(rows):
        fut=rows[i+1:i+1+H]
        r['_fwd5_close']= (f(fut[-1],'close')/f(r,'close')-1)*100 if len(fut)==H else None
        # oracle-lite: buy at today's LOW, sell at max HIGH over next H days (incl today)
        win=rows[i:i+1+H]
        if len(win)==H+1:
            r['_fwd5_maxup']=(max(f(x,'high') for x in win)/f(r,'low')-1)*100
            r['_fwd5_maxdn']=(min(f(x,'low') for x in win)/f(r,'low')-1)*100
        else: r['_fwd5_maxup']=None; r['_fwd5_maxdn']=None
rows=[r for r in dp if r.get('_fwd5_close') is not None]
print("forward-return panel rows: %d of %d (dropped %d: last %d bars of each symbol have no 5d forward window)"%(len(rows),len(dp),len(dp)-len(rows),H))

def seg(name,pred):
    sub=[r for r in rows if pred(r)]
    if len(sub)<15: print("%-26s n=%3d  (too few)"%(name,len(sub))); return
    fc=[r['_fwd5_close'] for r in sub]; mu=[r['_fwd5_maxup'] for r in sub]
    allfc=[r['_fwd5_close'] for r in rows]; allmu=[r['_fwd5_maxup'] for r in rows]
    print("%-26s n=%4d  fwd5_close mean %+6.2f%% (all %+.2f%%, lift %+.2fpp)  P(up) %5.1f%% (all %.1f%%)  low->max5d %6.2f%% (all %.2f%%, x%.2f)"%(
      name,len(sub),st.mean(fc),st.mean(allfc),st.mean(fc)-st.mean(allfc),
      100*sum(1 for x in fc if x>0)/len(fc), 100*sum(1 for x in allfc if x>0)/len(allfc),
      st.mean(mu),st.mean(allmu),st.mean(mu)/st.mean(allmu)))
print("\n=== TRUE FORWARD BASE RATES (all days, no selection) ===")
seg("ALL DAYS",lambda r: True)
for t in [1,2,3,5]: seg("vix_chg5d > +%d"%t, lambda r,t=t: f(r,'vix_chg5d')>t)
for t in [0,-2]: seg("vix_chg5d < %d"%t, lambda r,t=t: f(r,'vix_chg5d')<t)
for t in [18,20,25]: seg("vix > %d"%t, lambda r,t=t: f(r,'vix')>t)
for t in [80,90]: seg("vix_pctile > %d"%t, lambda r,t=t: f(r,'vix_pctile_252d')>t)
seg("vix_pctile < 20", lambda r: f(r,'vix_pctile_252d')<20)
for t in [1.5,2.0]: seg("atr14_pct > %.1f"%t, lambda r,t=t: f(r,'atr14_pct')>t)
seg("realvol20 > 18", lambda r: f(r,'realvol20_ann_pct')>18)
seg("vol_vs_20d > 1.1", lambda r: (f(r,'vol_vs_20d') or 0)>1.1)
print("\n--- joint: VIX shock AND price down ---")
seg("ret5d<0 (alone)", lambda r: f(r,'ret_5d_pct')<0)
seg("ret5d<0 & chg5d>+3", lambda r: f(r,'ret_5d_pct')<0 and f(r,'vix_chg5d')>3)
seg("ret5d<0 & chg5d<=+3", lambda r: f(r,'ret_5d_pct')<0 and f(r,'vix_chg5d')<=3)
seg("ret5d<-2 (alone)", lambda r: f(r,'ret_5d_pct')<-2)
seg("ret5d<-2 & chg5d>+3", lambda r: f(r,'ret_5d_pct')<-2 and f(r,'vix_chg5d')>3)
seg("ret5d<-2 & chg5d<=+3", lambda r: f(r,'ret_5d_pct')<-2 and f(r,'vix_chg5d')<=3)

print("\n=== VIX minus realised vol (variance-risk-premium proxy) ===")
for r in dp: r['_vrp']=f(r,'vix')-f(r,'realvol20_ann_pct')
dv=[r['_vrp'] for r in dp]
bv=[f(t,'B_vix')-f(t,'B_realvol20_ann_pct') for t in tr]
sv=[f(t,'S_vix')-f(t,'S_realvol20_ann_pct') for t in tr]
print("daily mean %.2f med %.2f | BUY mean %.2f med %.2f | SELL mean %.2f med %.2f"%(st.mean(dv),st.median(dv),st.mean(bv),st.median(bv),st.mean(sv),st.median(sv)))
for t in [0,2,4,6]:
    b=sum(1 for x in dv if x>t)/len(dv); bb=sum(1 for x in bv if x>t)/len(bv); ss=sum(1 for x in sv if x>t)/len(sv)
    print("  vrp>%d : base %5.1f%%  BUY %5.1f%% (lift %.2f)  SELL %5.1f%% (lift %.2f)"%(t,100*b,100*bb,bb/b,100*ss,ss/b))
