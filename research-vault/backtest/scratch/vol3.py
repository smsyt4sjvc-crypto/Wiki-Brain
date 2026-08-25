import csv, statistics as st
OUT="/home/user/INMA-/research-vault/backtest/out/"
def load(p):
    with open(p) as f: return list(csv.DictReader(f))
tr=load(OUT+"oracle_features.csv"); dp=load(OUT+"daily_panel.csv")
def f(r,k):
    v=r.get(k,'')
    try: return float(v)
    except: return None

# --- correlation vix_chg5d vs ret_5d_pct on daily panel
def corr(xs,ys):
    n=len(xs); mx=st.mean(xs); my=st.mean(ys)
    num=sum((a-mx)*(b-my) for a,b in zip(xs,ys))
    den=(sum((a-mx)**2 for a in xs)*sum((b-my)**2 for b in ys))**.5
    return num/den, num/sum((a-mx)**2 for a in xs), my, mx   # r, slope, meany, meanx
d=[(f(r,'ret_5d_pct'),f(r,'vix_chg5d')) for r in dp]
d=[(a,b) for a,b in d if a is not None and b is not None]
r,slope,my,mx=corr([a for a,b in d],[b for a,b in d])
print("daily corr(ret_5d_pct, vix_chg5d) = %.3f  slope=%.3f VIXpts per 1%% ret  n=%d"%(r,slope,len(d)))
inter=my-slope*mx
def resid(ret,vc): return vc-(inter+slope*ret)
dres=[resid(a,b) for a,b in d]
print("daily residual vix_chg5d: mean %.3f sd %.3f"%(st.mean(dres),st.pstdev(dres)))
bres=[resid(f(t,'B_ret_5d_pct'),f(t,'B_vix_chg5d')) for t in tr if f(t,'B_ret_5d_pct') is not None]
sres=[resid(f(t,'S_ret_5d_pct'),f(t,'S_vix_chg5d')) for t in tr if f(t,'S_ret_5d_pct') is not None]
print("BUY  residual: n=%d mean %.3f (%.2f sd) median %.3f"%(len(bres),st.mean(bres),st.mean(bres)/st.pstdev(dres),st.median(bres)))
print("SELL residual: n=%d mean %.3f (%.2f sd) median %.3f"%(len(sres),st.mean(sres),st.mean(sres)/st.pstdev(dres),st.median(sres)))
# raw comparison
print("raw B_vix_chg5d mean %.3f vs daily %.3f | B_ret_5d mean %.3f vs daily %.3f"%(
  st.mean([f(t,'B_vix_chg5d') for t in tr]), st.mean([b for a,b in d]),
  st.mean([f(t,'B_ret_5d_pct') for t in tr]), st.mean([a for a,b in d])))

# --- stratified: within ret_5d_pct deciles, rate of vix_chg5d>+3 daily vs at buys
print("\n=== STRATIFIED BY ret_5d_pct DECILE: P(vix_chg5d > +3) ===")
rets=sorted(a for a,b in d)
cuts=[rets[int(len(rets)*i/10)] for i in range(1,10)]
def dec(x):
    for i,c in enumerate(cuts):
        if x<c: return i
    return 9
print("%-6s %-16s %8s %8s %8s %8s %6s"%("dec","ret_5d range","n_daily","base%","n_buy","buy%","lift"))
tot_exp=0; tot_obs=0
for i in range(10):
    ddec=[(a,b) for a,b in d if dec(a)==i]
    bdec=[t for t in tr if f(t,'B_ret_5d_pct') is not None and dec(f(t,'B_ret_5d_pct'))==i]
    if not ddec: continue
    base=sum(1 for a,b in ddec if b>3)/len(ddec)
    nb=len(bdec); ob=sum(1 for t in bdec if f(t,'B_vix_chg5d')>3)
    tot_exp+=base*nb; tot_obs+=ob
    print("%-6d %-16s %8d %7.1f%% %8d %7.1f%% %6s"%(i,"%.2f..%.2f"%(min(a for a,b in ddec),max(a for a,b in ddec)),
      len(ddec),100*base,nb,100*ob/nb if nb else 0,"%.2f"%((ob/nb)/base) if nb and base else "-"))
print("TOTAL stratified: observed %d buys with vix_chg5d>+3, expected %.1f if VIX-shock added nothing beyond 5d return -> lift %.2fx (unstratified lift 2.70x)"%(tot_obs,tot_exp,tot_obs/tot_exp))

# same for vix level >20 and pctile>80
for name,col,thr in [("vix>20",'vix',20),("vix_pctile>80",'vix_pctile_252d',80),("vix_chg5d>+2",'vix_chg5d',2),("atr14>1.5",'atr14_pct',1.5)]:
    tot_exp=0;tot_obs=0;nn=0
    for i in range(10):
        ddec=[r_ for r_ in dp if f(r_,'ret_5d_pct') is not None and dec(f(r_,'ret_5d_pct'))==i]
        bdec=[t for t in tr if f(t,'B_ret_5d_pct') is not None and dec(f(t,'B_ret_5d_pct'))==i]
        if not ddec or not bdec: continue
        base=sum(1 for r_ in ddec if f(r_,col)>thr)/len(ddec)
        ob=sum(1 for t in bdec if f(t,'B_'+col)>thr)
        tot_exp+=base*len(bdec); tot_obs+=ob; nn+=len(bdec)
    print("STRATIFIED %-16s obs=%3d exp=%6.1f  within-stratum lift=%.2fx (n=%d)"%(name,tot_obs,tot_exp,tot_obs/tot_exp if tot_exp else 0,nn))
