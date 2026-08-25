#!/usr/bin/env python3
# =============================================================================
#  FEATURE TABLE — every oracle buy/sell date tagged with everything computable
#  from primary series. NO event calendar here (FOMC/CPI) -- that is a known gap,
#  registered rather than guessed at.
# =============================================================================
import csv, os, json, math, datetime
ROOT = os.path.dirname(os.path.abspath(__file__))

def load(name, cols=('open','high','low','close','volume')):
    d = {}
    p = os.path.join(ROOT,'data',name+'.csv')
    if not os.path.exists(p): return d
    with open(p) as f:
        for r in csv.DictReader(f):
            try: d[r['date']] = {c: (float(r[c]) if r.get(c) not in ('','None',None) else None) for c in cols if c in r}
            except (ValueError,TypeError): pass
    return d

def series(d, key='close'):
    ks = sorted(d); return ks, [d[k].get(key) for k in ks]

def sma(v,i,n):
    if i+1<n: return None
    w=[x for x in v[i-n+1:i+1] if x is not None]
    return sum(w)/len(w) if len(w)==n else None

def rsi(v,i,n=14):
    if i<n: return None
    g=l=0.0
    for j in range(i-n+1,i+1):
        if v[j] is None or v[j-1] is None: return None
        ch=v[j]-v[j-1]
        g+=max(ch,0); l+=max(-ch,0)
    if l==0: return 100.0
    rs=(g/n)/(l/n); return 100-100/(1+rs)

def stdev(v,i,n):
    if i+1<n: return None
    w=[x for x in v[i-n+1:i+1] if x is not None]
    if len(w)<n: return None
    m=sum(w)/n; return math.sqrt(sum((x-m)**2 for x in w)/n)

def pct_rank(v,i,n):
    if i+1<n or v[i] is None: return None
    w=[x for x in v[i-n+1:i+1] if x is not None]
    if len(w)<n*0.8: return None
    return round(100.0*sum(1 for x in w if x<=v[i])/len(w),1)

MACRO = {k: load(k, ('close',)) for k in ('vix','dxy','wti','gold','hyg','tlt')}
TSY = {}
p=os.path.join(ROOT,'data','treasury_curve.csv')
with open(p) as f:
    for r in csv.DictReader(f):
        try: TSY[r['date']] = {k: (float(r[k]) if r[k] not in ('','None') else None) for k in ('m3','y1','y2','y5','y10','y20','y30')}
        except (ValueError,TypeError): pass

def last_on_or_before(d, day, maxback=7):
    dt=datetime.date.fromisoformat(day)
    for k in range(maxback+1):
        s=(dt-datetime.timedelta(days=k)).isoformat()
        if s in d: return d[s], s
    return None, None

def chg(d, day, back, key='close'):
    cur,_=last_on_or_before(d,day)
    dt=datetime.date.fromisoformat(day)-datetime.timedelta(days=back*1.45 if False else back)
    prev,_=last_on_or_before(d,(datetime.date.fromisoformat(day)-datetime.timedelta(days=int(back*1.45)+2)).isoformat())
    if not cur or not prev: return None
    a,b=cur.get(key),prev.get(key)
    return None if a is None or b is None else round(a-b,4)

def third_friday(y,m):
    d=datetime.date(y,m,1); f=[]
    while d.month==m:
        if d.weekday()==4: f.append(d)
        d+=datetime.timedelta(days=1)
    return f[2]

def build(sym):
    px=load(sym)
    dates=sorted(px); idx={d:i for i,d in enumerate(dates)}
    c=[px[d]['close'] for d in dates]; h=[px[d]['high'] for d in dates]
    lo=[px[d]['low'] for d in dates]; vol=[px[d]['volume'] for d in dates]
    tr=[None]+[max(h[i]-lo[i],abs(h[i]-c[i-1]),abs(lo[i]-c[i-1])) for i in range(1,len(dates))]
    feats={}
    for i,d in enumerate(dates):
        if d<'2022-12-01': continue
        F={}
        F['close']=c[i]; F['high']=h[i]; F['low']=lo[i]
        for n in (20,50,200):
            m=sma(c,i,n); F[f'dist_sma{n}_pct']=round((c[i]/m-1)*100,3) if m else None
        F['rsi14']=round(rsi(c,i,14),2) if rsi(c,i,14) else None
        sd=stdev(c,i,20); m20=sma(c,i,20)
        F['bb_pctB']=round((c[i]-(m20-2*sd))/(4*sd),3) if (sd and m20 and sd>0) else None
        atr=None
        if i>=14 and all(x is not None for x in tr[i-13:i+1]): atr=sum(tr[i-13:i+1])/14
        F['atr14_pct']=round(atr/c[i]*100,3) if atr else None
        for n in (1,3,5,10,20):
            F[f'ret_{n}d_pct']=round((c[i]/c[i-n]-1)*100,3) if i>=n else None
        for n in (20,63,252):
            if i+1>=n:
                w=c[i-n+1:i+1]
                F[f'dd_from_{n}d_high_pct']=round((c[i]/max(w)-1)*100,3)
                F[f'up_from_{n}d_low_pct']=round((c[i]/min(w)-1)*100,3)
        F['is_20d_low']=int(i>=19 and lo[i]==min(lo[i-19:i+1]))
        F['is_20d_high']=int(i>=19 and h[i]==max(h[i-19:i+1]))
        F['is_63d_low']=int(i>=62 and lo[i]==min(lo[i-62:i+1]))
        F['is_63d_high']=int(i>=62 and h[i]==max(h[i-62:i+1]))
        av=sma(vol,i,20); F['vol_vs_20d']=round(vol[i]/av,3) if (av and av>0 and vol[i]) else None
        F['realvol20_ann_pct']=round(stdev([ (c[j]/c[j-1]-1) if j>0 else 0 for j in range(len(c))],i,20)*math.sqrt(252)*100,2) if i>=20 else None
        dn=0
        j=i
        while j>0 and c[j]<c[j-1]: dn+=1; j-=1
        up=0; j=i
        while j>0 and c[j]>c[j-1]: up+=1; j-=1
        F['consec_down_days']=dn; F['consec_up_days']=up
        dt=datetime.date.fromisoformat(d)
        F['dow']=dt.weekday(); F['dom']=dt.day; F['month']=dt.month; F['year']=dt.year
        mdays=[x for x in dates if x[:7]==d[:7]]
        F['tday_in_month']=mdays.index(d)+1; F['tdays_in_month']=len(mdays)
        F['tdays_to_month_end']=len(mdays)-F['tday_in_month']
        F['pct_through_month']=round(F['tday_in_month']/len(mdays),3)
        tf=third_friday(dt.year,dt.month)
        F['days_to_opex']=(tf-dt).days
        F['is_opex_week']=int(abs((tf-dt).days)<=4)
        F['is_quarter_end_month']=int(dt.month in (3,6,9,12))
        F['is_turn_of_month']=int(F['tday_in_month']<=2 or F['tdays_to_month_end']<=1)
        for nm,dd in MACRO.items():
            cur,_=last_on_or_before(dd,d)
            F[nm]=cur['close'] if cur else None
            F[nm+'_chg5d']=chg(dd,d,5)
        t,_=last_on_or_before(TSY,d)
        if t:
            for k,v in t.items(): F['ust_'+k]=v
            if t.get('y10') and t.get('y2'): F['curve_2s10s']=round(t['y10']-t['y2'],3)
            if t.get('y30') and t.get('y2'): F['curve_2s30s']=round(t['y30']-t['y2'],3)
        t5,_=last_on_or_before(TSY,(dt-datetime.timedelta(days=8)).isoformat())
        if t and t5:
            for k in ('y2','y10','y30'):
                if t.get(k) and t5.get(k): F[f'ust_{k}_chg5d']=round(t[k]-t5[k],3)
        vser={k:MACRO['vix'][k]['close'] for k in MACRO['vix']}
        vk=sorted(vser); vv=[vser[k] for k in vk]
        if d in vser:
            F['vix_pctile_252d']=pct_rank(vv,vk.index(d),252)
        feats[d]=F
    return feats

if __name__=='__main__':
    trades=json.load(open(os.path.join(ROOT,'out','oracle_trades.json')))
    FE={s:build(s) for s in ('spx','ndx')}
    rows=[]
    for t in trades:
        fb=FE[t['sym']].get(t['buy_date'],{}); fs=FE[t['sym']].get(t['sell_date'],{})
        r=dict(t)
        for k,v in fb.items(): r['B_'+k]=v
        for k,v in fs.items(): r['S_'+k]=v
        rows.append(r)
    keys=sorted({k for r in rows for k in r})
    lead=['sym','month','leg','buy_date','sell_date','ret_pct','hold_days']
    keys=lead+[k for k in keys if k not in lead]
    out=os.path.join(ROOT,'out','oracle_features.csv')
    with open(out,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys); w.writeheader(); w.writerows(rows)
    print(f'{len(rows)} trades x {len(keys)} columns -> {out}')
    # also dump the full daily feature panel for base-rate comparison
    allrows=[]
    for s in ('spx','ndx'):
        for d,F in FE[s].items():
            if d>='2023-01-01': allrows.append(dict(sym=s,date=d,**F))
    k2=sorted({k for r in allrows for k in r}); k2=['sym','date']+[k for k in k2 if k not in ('sym','date')]
    out2=os.path.join(ROOT,'out','daily_panel.csv')
    with open(out2,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=k2); w.writeheader(); w.writerows(allrows)
    print(f'{len(allrows)} daily rows x {len(k2)} columns -> {out2}')
