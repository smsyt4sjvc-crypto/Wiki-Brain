import csv, statistics as st
from collections import defaultdict

OUT="/home/user/INMA-/research-vault/backtest/out/"
def load(p):
    with open(OUT+p) as f: return list(csv.DictReader(f))
dp=load("daily_panel.csv"); tr=load("oracle_features.csv")
print("rows daily",len(dp),"trades",len(tr))
def fl(r,k):
    v=r.get(k,"")
    try: return float(v)
    except: return None

# missingness
for k in ["vix","vix_chg5d"]:
    miss=sum(1 for r in dp if fl(r,k) is None)
    print("daily missing",k,miss)
for k in ["B_vix","B_vix_chg5d"]:
    miss=sum(1 for r in tr if fl(r,k) is None)
    print("trade missing",k,miss)

dvix=[fl(r,"vix") for r in dp if fl(r,"vix") is not None]
dchg=[fl(r,"vix_chg5d") for r in dp if fl(r,"vix_chg5d") is not None]
bvix=[fl(r,"B_vix") for r in tr if fl(r,"B_vix") is not None]
bchg=[fl(r,"B_vix_chg5d") for r in tr if fl(r,"B_vix_chg5d") is not None]
print("daily vix mean %.3f med %.3f n=%d"%(st.mean(dvix),st.median(dvix),len(dvix)))
print("daily chg mean %.3f med %.3f n=%d"%(st.mean(dchg),st.median(dchg),len(dchg)))

def rate(xs,thr): return sum(1 for x in xs if x>thr)/len(xs)
print("--- ALL-DAYS DENOMINATOR (n=%d daily rows, both syms) ---"%len(dvix))
for thr in [1,2,3,5]:
    b=rate(dchg,thr); h=rate(bchg,thr)
    print("vix_chg5d>+%d base %.1f%% buys %.1f%% lift %.2fx (k=%d/%d)"%(thr,b*100,h*100,h/b,sum(1 for x in bchg if x>thr),len(bchg)))
for thr in [18,20,22,25]:
    b=rate(dvix,thr); h=rate(bvix,thr)
    print("vix>%d base %.1f%% buys %.1f%% lift %.2fx (k=%d/%d)"%(thr,b*100,h*100,h/b,sum(1 for x in bvix if x>thr),len(bvix)))

# DEDUP: vix is market-wide, daily panel double counts SPX+NDX
uniq={}
for r in dp:
    d=r["date"]
    if d not in uniq and fl(r,"vix") is not None: uniq[d]=(fl(r,"vix"),fl(r,"vix_chg5d"))
uv=[v[0] for v in uniq.values()]; uc=[v[1] for v in uniq.values() if v[1] is not None]
print("--- UNIQUE DATES n=%d ---"%len(uniq))
for thr in [2,3,5]:
    print("chg>+%d base %.1f%%"%(thr,rate(uc,thr)*100))
for thr in [20,22,25]:
    print("vix>%d base %.1f%%"%(thr,rate(uv,thr)*100))
# unique buy dates
ub={}
for r in tr:
    ub.setdefault(r["buy_date"],(fl(r,"B_vix"),fl(r,"B_vix_chg5d")))
print("unique buy dates",len(ub))
ubv=[v[0] for v in ub.values()]; ubc=[v[1] for v in ub.values()]
for thr in [2,3,5]:
    b=rate(uc,thr);h=rate(ubc,thr);print("  chg>+%d buys %.1f%% lift %.2fx k=%d"%(thr,h*100,h/b,sum(1 for x in ubc if x>thr)))
for thr in [20,22,25]:
    b=rate(uv,thr);h=rate(ubv,thr);print("  vix>%d buys %.1f%% lift %.2fx k=%d"%(thr,h*100,h/b,sum(1 for x in ubv if x>thr)))
