exec(open('/home/user/INMA-/research-vault/backtest/scratch/setup.py').read())
MACRO=['ust_y2','ust_y5','ust_y10','ust_y30','curve_2s10s','curve_2s30s',
       'ust_y2_chg5d','ust_y10_chg5d','ust_y30_chg5d',
       'dxy','dxy_chg5d','tlt','tlt_chg5d','hyg','hyg_chg5d','gold','gold_chg5d','wti','wti_chg5d']
# dedupe buy dates and sell dates (macro identical across sym)
buy_dates=sorted(set(t['buy_date'] for t in trades))
sell_dates=sorted(set(t['sell_date'] for t in trades))
pby={r['date']:r for r in mpanel}
def sub(dates): return [pby[d] for d in dates if d in pby]
B=sub(buy_dates); S=sub(sell_dates)
def stats(rows,c):
    v=[f(r,c) for r in rows]; v=[x for x in v if x is not None]
    if not v: return None
    return len(v), st.median(v), sum(v)/len(v)
print(f"{'col':<16} {'panel_n':>7} {'p_med':>8} {'buy_n':>5} {'b_med':>8} {'sell_n':>6} {'s_med':>8}  fracNEG panel/buy/sell")
for c in MACRO:
    ps=stats(mpanel,c); bs=stats(B,c); ss=stats(S,c)
    def fneg(rows):
        v=[f(r,c) for r in rows]; v=[x for x in v if x is not None]
        return sum(1 for x in v if x<0)/len(v) if v else float('nan')
    print(f"{c:<16} {ps[0]:>7} {ps[1]:>8.3f} {bs[0]:>5} {bs[1]:>8.3f} {ss[0]:>6} {ss[1]:>8.3f}   {fneg(mpanel):.3f}/{fneg(B):.3f}/{fneg(S):.3f}")
