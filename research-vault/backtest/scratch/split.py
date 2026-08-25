import csv, math
OUT='/home/user/INMA-/research-vault/backtest/out/'
panel=list(csv.DictReader(open(OUT+'daily_panel.csv')))
tr=list(csv.DictReader(open(OUT+'oracle_features.csv')))
buyset=set((r['sym'],r['buy_date']) for r in tr)
edges=[0,25,30,35,40,45,50,60,70,75,101]
def table(sub,label):
    base=sum(1 for r in sub if (r['sym'],r['date']) in buyset)/len(sub)
    out=[]
    for i in range(len(edges)-1):
        s=[r for r in sub if edges[i]<=float(r['rsi14'])<edges[i+1]]
        k=sum(1 for r in s if (r['sym'],r['date']) in buyset)
        out.append(f"{(k/len(s))/base:.2f}({k}/{len(s)})" if s else "-")
    print(f"{label:<22} base={100*base:.2f}%  "+" ".join(f"{o:>11}" for o in out))
print("bins:                             "+" ".join(f"{str(edges[i])+'-'+str(edges[i+1]):>11}" for i in range(len(edges)-1)))
table(panel,"ALL")
table([r for r in panel if r['sym']=='spx'],"SPX only")
table([r for r in panel if r['sym']=='ndx'],"NDX only")
d=sorted({r['date'] for r in panel}); mid=d[len(d)//2]
table([r for r in panel if r['date']<mid],"first half (time)")
table([r for r in panel if r['date']>=mid],"second half (time)")
