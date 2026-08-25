exec(open('/home/user/INMA-/research-vault/backtest/scratch/setup.py').read())
buy_dates=sorted(set(t['buy_date'] for t in trades))
sell_dates=sorted(set(t['sell_date'] for t in trades))
pby={r['date']:r for r in mpanel}
COLS=['hyg_chg5d','tlt_chg5d','ust_10y_dummy','ust_y10_chg5d','ust_y2_chg5d','ust_y30_chg5d','dxy_chg5d','wti_chg5d','gold_chg5d','curve_2s10s','curve_2s30s','ust_y10']
def yr(d): return d[:4]
for c in ['hyg_chg5d','tlt_chg5d','ust_y10_chg5d','ust_y2_chg5d','dxy_chg5d','wti_chg5d','gold_chg5d']:
    print('==',c,'-- FRACTION NEGATIVE (5d change < 0)')
    print(f"{'yr':<6}{'panelN':>7}{'panel%':>8}{'buyN':>6}{'buy%':>8}{'lift':>7}{'sellN':>6}{'sell%':>8}")
    for y in ['2023','2024','2025','2026','ALL']:
        P=[r for r in mpanel if (y=='ALL' or yr(r['date'])==y)]
        B=[pby[d] for d in buy_dates if (y=='ALL' or yr(d)==y)]
        S=[pby[d] for d in sell_dates if (y=='ALL' or yr(d)==y)]
        def fr(rows):
            v=[f(r,c) for r in rows]; v=[x for x in v if x is not None]
            return (len(v), sum(1 for x in v if x<0)/len(v)*100 if v else float('nan'))
        pn,pp=fr(P); bn,bp=fr(B); sn,sp=fr(S)
        print(f"{y:<6}{pn:>7}{pp:>8.1f}{bn:>6}{bp:>8.1f}{bp/pp:>7.2f}{sn:>6}{sp:>8.1f}")
    print()
