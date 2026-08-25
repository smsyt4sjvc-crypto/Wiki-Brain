#!/usr/bin/env python3
"""Treasury par yield curve, daily, 2023-2026, from Treasury.gov primary."""
import urllib.request, csv, os, io, time
ROOT=os.path.dirname(os.path.abspath(__file__))
UA={'User-Agent':'Mozilla/5.0'}
out={}
for yr in (2023,2024,2025,2026):
    u=(f'https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/{yr}/all'
       f'?type=daily_treasury_yield_curve&field_tdr_date_value={yr}&page&_format=csv')
    txt=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=90).read().decode()
    rd=csv.DictReader(io.StringIO(txt)); n=0
    for r in rd:
        m,d,y=r['Date'].split('/'); iso=f'{y}-{int(m):02d}-{int(d):02d}'
        out[iso]={k:r.get(k,'') for k in ('2 Yr','5 Yr','10 Yr','20 Yr','30 Yr','3 Mo','1 Yr')}
        n+=1
    print(yr,n,'rows'); time.sleep(0.5)
p=os.path.join(ROOT,'data','treasury_curve.csv')
with open(p,'w',newline='') as f:
    w=csv.writer(f); w.writerow(['date','m3','y1','y2','y5','y10','y20','y30'])
    for d in sorted(out):
        r=out[d]; w.writerow([d,r['3 Mo'],r['1 Yr'],r['2 Yr'],r['5 Yr'],r['10 Yr'],r['20 Yr'],r['30 Yr']])
print('total',len(out),'->',p)
