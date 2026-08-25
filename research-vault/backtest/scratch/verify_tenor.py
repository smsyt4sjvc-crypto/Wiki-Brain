import csv, statistics as st
from collections import defaultdict
OUT="/home/user/INMA-/research-vault/backtest/out/"
panel=list(csv.DictReader(open(OUT+"daily_panel.csv")))
feat=list(csv.DictReader(open(OUT+"oracle_features.csv")))
print("panel rows",len(panel),"feat rows",len(feat))
cols=["ust_y2_chg5d","ust_y10_chg5d","ust_y30_chg5d"]

# 1. is treasury data identical across syms on same date?
bysym=defaultdict(dict)
for r in panel: bysym[r["sym"]][r["date"]]=r
syms=sorted(bysym); print("syms",[(s,len(bysym[s])) for s in syms])
common=set(bysym[syms[0]])&set(bysym[syms[1]])
diff=0
for d in common:
    for c in cols:
        if bysym[syms[0]][d][c]!=bysym[syms[1]][d][c]: diff+=1
print("date overlap",len(common),"tenor-value mismatches across syms:",diff)

# missingness
for c in cols:
    miss=sum(1 for r in panel if r[c] in ("","nan","NaN","None"))
    print("panel missing",c,miss)
    missf=sum(1 for r in feat if r["B_"+c] in ("","nan","NaN","None"))
    print("feat missing B_"+c,missf)

# unique-date panel
udates=sorted(set(r["date"] for r in panel))
panel_u={d:bysym[syms[0]].get(d) or bysym[syms[1]].get(d) for d in udates}
print("unique panel dates",len(udates))

buydates=sorted(set(r["buy_date"] for r in feat))
print("unique buy dates",len(buydates),"of",len(feat),"trades")
# also buy dates per sym pair
print("unique (sym,buy_date)",len(set((r["sym"],r["buy_date"]) for r in feat)))

def rate(rows,c,thr=15.0):
    v=[abs(float(r[c])) for r in rows if r[c] not in ("","nan")]
    return sum(1 for x in v if x>=thr), len(v)

print("\n--- THRESHOLD 15bp, |5d chg| ---")
for c in cols:
    pk,pn=rate([panel_u[d] for d in udates],c)
    bk,bn=rate([panel_u[d] for d in buydates if d in panel_u],c)
    print(c,pk,pn,bk,bn)

print("\n--- signed means ---")
for c in cols:
    pv=[float(panel_u[d][c]) for d in udates if panel_u[d][c] not in ("","nan")]
    bv=[float(panel_u[d][c]) for d in buydates if d in panel_u and panel_u[d][c] not in ("","nan")]
    print(f"{c}: panel mean {st.mean(pv):+.2f} buys mean {st.mean(bv):+.2f}")

# ALL-TRADE weighting (176 rows) instead of unique dates
print("\n--- all 176 trade rows (not dedup) ---")
for c in cols:
    pk,pn=rate([panel_u[d] for d in udates],c)
    v=[abs(float(r["B_"+c])) for r in feat if r["B_"+c] not in ("","nan")]
    bk,bn=sum(1 for x in v if x>=15),len(v)
    print(f"{c}: buys {bk}/{bn}={100*bk/bn:.1f}% lift {(bk/bn)/(pk/pn):.2f}")
