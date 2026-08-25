import csv, collections
OUT='/home/user/INMA-/research-vault/backtest/out/'
panel=list(csv.DictReader(open(OUT+'daily_panel.csv')))
tr=list(csv.DictReader(open(OUT+'oracle_features.csv')))
buyset=set((r['sym'],r['buy_date']) for r in tr)
base=len(buyset)/len(panel)
print("unique buy days %d / %d = %.4f%%"%(len(buyset),len(panel),100*base))
edges=[0,25,30,35,40,45,50,60,70,75,101]
def b(x):
    for i in range(len(edges)-1):
        if edges[i]<=x<edges[i+1]: return i
    return None
cnt=collections.Counter(); hit=collections.Counter()
for r in panel:
    i=b(float(r['rsi14'])); cnt[i]+=1
    if (r['sym'],r['date']) in buyset: hit[i]+=1
tot=0
print(f"{'bin':<12}{'n_days':>7}{'buys':>6}{'p%':>8}{'lift':>7}")
for i in range(len(edges)-1):
    n=cnt[i]; k=hit[i]; tot+=n
    p=k/n if n else 0
    print(f"[{edges[i]},{edges[i+1]})".ljust(12)+f"{n:>7}{k:>6}{100*p:>8.2f}{p/base:>7.2f}")
print("total days binned",tot,"total buys",sum(hit.values()))
# flat middle 40-75
mid=[r for r in panel if 40<=float(r['rsi14'])<75]
midk=sum(1 for r in mid if (r['sym'],r['date']) in buyset)
print("RSI 40-75: days=%d buys=%d p=%.2f%% lift=%.3f"%(len(mid),midk,100*midk/len(mid),(midk/len(mid))/base))
