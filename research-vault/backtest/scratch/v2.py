import csv, statistics as st
from collections import defaultdict
O='/home/user/INMA-/research-vault/backtest/out/oracle_features.csv'
D='/home/user/INMA-/research-vault/backtest/out/daily_panel.csv'
tr=list(csv.DictReader(open(O))); pan=list(csv.DictReader(open(D)))
def f(x): return float(x)
# hold buckets
def bucket(h):
    if h==0: return '0'
    if h<=3: return '1-3'
    if h<=7: return '4-7'
    if h<=14: return '8-14'
    return '15+'
B=defaultdict(list)
for t in tr: B[bucket(int(f(t['hold_days'])))].append(f(t['ret_pct']))
tot=sum(f(t['ret_pct']) for t in tr)
for k in ['0','1-3','4-7','8-14','15+']:
    v=B[k]; print("h=%-5s n=%-3d mean %.3f  sum %.1f  share_ret %.1f%%  share_legs %.1f%%"%(k,len(v),st.mean(v),sum(v),100*sum(v)/tot,100*len(v)/176))
hs=[int(f(t['hold_days'])) for t in tr]
print("hold median",st.median(hs),"mean %.3f"%st.mean(hs),"max",max(hs))
# per-h counts
cnt=defaultdict(int)
for h in hs: cnt[h]+=1
print("per-h n:",dict(sorted(cnt.items())))

# build panel series per sym
S=defaultdict(list)
for p in pan: S[p['sym']].append(p)
for k in S: S[k].sort(key=lambda r:r['date'])
# base rate: (high[t+h]-low[t])/low[t], same calendar month
def base(h,mode='signed'):
    out=[]
    for k,rows in S.items():
        for i in range(len(rows)-h):
            a,b=rows[i],rows[i+h]
            if a['date'][:7]!=b['date'][:7]: continue
            if mode=='signed':
                out.append(100*(f(b['high'])-f(a['low']))/f(a['low']))
            else: # max range over window
                hi=max(f(r['high']) for r in rows[i:i+h+1]); lo=min(f(r['low']) for r in rows[i:i+h+1])
                out.append(100*(hi-lo)/lo)
    return out
print("\n h |  n   | signed mean | maxrange mean | oracle n | oracle mean | lift_signed")
oh=defaultdict(list)
for t in tr: oh[int(f(t['hold_days']))].append(f(t['ret_pct']))
for h in [0,1,2,3,4,5,6,7,8,10,12,14,17,21]:
    bs=base(h); bm=base(h,'max')
    om=st.mean(oh[h]) if oh[h] else float('nan')
    print("%3d| %5d| %11.4f | %13.4f | %8d | %11.4f | %6.2f"%(h,len(bs),st.mean(bs),st.mean(bm),len(oh[h]),om,om/st.mean(bs)))
