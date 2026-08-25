import csv, statistics as st
O='/home/user/INMA-/research-vault/backtest/out/'
panel=list(csv.DictReader(open(O+'daily_panel.csv')))
def f(v):
    try: return float(v)
    except: return None
spx=sorted([r for r in panel if r['sym']=='spx'],key=lambda r:r['date'])
# recompute hyg 5-trading-day pct change from hyg column
pts=[]
for i in range(5,len(spx)):
    h0=f(spx[i-5]['hyg']); h1=f(spx[i]['hyg']); x=f(spx[i]['ret_5d_pct'])
    if None in (h0,h1,x): continue
    pts.append((x,100*(h1/h0-1)))
mx=st.mean(p[0] for p in pts); my=st.mean(p[1] for p in pts)
b=sum((x-mx)*(y-my) for x,y in pts)/sum((x-mx)**2 for x,_ in pts)
print("recomputed-hyg beta=%.3f alpha=%.3f n=%d"%(b,my-b*mx,len(pts)))
# corr of column vs recomputed
a=[f(spx[i]['hyg_chg5d']) for i in range(5,len(spx))]
c=[100*(f(spx[i]['hyg'])/f(spx[i-5]['hyg'])-1) for i in range(5,len(spx))]
print("corr(col, recomputed)=%.4f  mean diff %.4f"%(st.correlation(a,c),st.mean(x-y for x,y in zip(a,c))))
print("sign agreement %.1f%%"%(100*sum(1 for x,y in zip(a,c) if (x<0)==(y<0))/len(a)))
