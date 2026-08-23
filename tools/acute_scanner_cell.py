
# ============================================================================
#  ACUTE SCANNER — 10-hour window, vault keywords / threads, source-tiered
#  Prints: (1) INDEX prices  (2) MAG 7 alone  (3) MEMORY alone
#          (4) keyword HITS ONLY, financial outlets first, buzz last
#          (5) PRIORITY FOLLOW-UP QUEUE — hits grouped by the OPEN VAULT FLAG they
#              could close, paywalled primary wires marked [GET], with full links.
#  Two gates: keywords say ON-TOPIC; the flag registry says WORTH READING.
#  Prints NOTHING for a tier with no hits. No padding. Token-free.
# ============================================================================
import subprocess, sys, re, io, time, textwrap, urllib.request
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
try:
    import yfinance as yf
except Exception:
    subprocess.run([sys.executable,'-m','pip','install','-q','yfinance']); import yfinance as yf

HOURS  = 10                       # <-- the DISPLAY window for the hit tiers
# The FLAG window is deliberately WIDER than the display window. An open question does not
# age out because the news cycle did: on run 3 the two PRI-1 flags (F1 MSFT leases, F2 the
# Goldman/Blue Owl deals) showed "no candidate" purely because their evidence had scrolled
# past 10h. The highest-priority questions were the ones the window hid. Feeds using
# Google's when:1d cap out around 24h regardless; this takes whatever the others still hold.
FLAG_HOURS = 30
PER_TIER_CAP = 40                 # safety cap so a bad feed can't wall you
UA = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
NOW = datetime.now(timezone.utc)
CUT = NOW - timedelta(hours=HOURS)
FCUT= NOW - timedelta(hours=FLAG_HOURS)

# ---------------------------------------------------------------- PRICES
INDEX = [('^GSPC','S&P 500'), ('^NDX','Nasdaq 100'), ('^RUT','Russell 2000'),
         ('SOXX','SOXX semis'), ('SMH','SMH semis'), ('^VIX','VIX'),
         ('^TNX','US 10Y'), ('^TYX','US 30Y'), ('DX-Y.NYB','DXY'),
         ('CL=F','WTI'), ('BZ=F','Brent'), ('GC=F','Gold'), ('TLT','TLT 20y+')]
MAG7  = [('AAPL','Apple'), ('MSFT','Microsoft'), ('GOOGL','Alphabet'), ('AMZN','Amazon'),
         ('META','Meta'), ('NVDA','Nvidia'), ('TSLA','Tesla')]
MEM   = [('MU','Micron'), ('SNDK','SanDisk'), ('STX','Seagate'), ('WDC','WestDigital'),
         ('005930.KS','Samsung Elec'), ('000660.KS','SK hynix'), ('TSM','TSMC'), ('AVGO','Broadcom')]


# ── EVENT CLUSTERING — added 8/2 after Jake caught me presenting a ZeroHedge re-report of a
#    Truth Social post HE HAD ALREADY PASTED as fresh corroboration. The run printed 95 HITS;
#    it carried ~15-18 DISTINCT EVENTS. The Hormuz block alone was ~50 headlines over ~9 things.
#    ⛔ THE DEFECT: the scanner counted SYNDICATION as SIGNAL. Forty outlets reprinting one
#    statement is one datum, not forty — and a big hit-count READS as high signal, which is the
#    opposite of true. war-board.md L572 already registered the rule: "if this is the same story
#    resurfacing it is NOT NEW INFORMATION." The scanner had no way to apply it.
STOP = set("""the a an of of to in on for and or at by from with as is are was be been says say said
after over amid new more than that this it its us u.s. reuters bloomberg report reports news will would
could may might near into out up down but not no yes he she they his her their who what when where why
live day update breaking exclusive""".split())
def _stem(w):
    for suf in ("'s", "ies", "ing", "ed", "es", "s"):
        if w.endswith(suf) and len(w) - len(suf) >= 4: return w[:-len(suf)]
    return w
def _toks(t):
    import re as _re
    return {_stem(x) for x in _re.findall(r"[a-z0-9']+", t.lower())
            if x not in STOP and len(x) > 2}
def cluster_hits(hits, thresh=0.60, minshare=3):
    """Group same-EVENT headlines. CONTAINMENT (inter / smaller set), not Jaccard --
       headlines vary wildly in length and Jaccard punishes long-vs-short pairs, which is
       exactly the wire-vs-aggregator case we need to catch."""
    out = []
    for h in hits:
        tk = _toks(h[3]); placed = False
        for rep, dupes, rtk in out:
            inter = len(tk & rtk)
            if inter >= minshare and inter / max(1, min(len(tk), len(rtk))) >= thresh:
                dupes.append(h); rtk |= tk          # widen the cluster as members join
                placed = True; break
        if not placed:
            out.append((h, [], set(tk)))
    return [(r, d) for r, d, _ in out]

def px_block(title, rows):
    print(f'\n### {title}')
    print(f'  {"":13}{"last":>12}{"chg%":>9}{"BASE":>12}   as of')
    tick = [t for t,_ in rows]; moves = []
    try:
        df = yf.download(tick, period='5d', progress=False, auto_adjust=True, threads=True)['Close']
    except Exception as e:
        print(f'  !! price fetch failed: {e}'); return
    if hasattr(df,'to_frame') and not hasattr(df,'columns'): df = df.to_frame(tick[0])
    for t, lab in rows:
        try:
            s = df[t].dropna()
            if len(s) < 2: print(f'  {lab:13}   -- n/a'); continue
            last, base = float(s.iloc[-1]), float(s.iloc[-2])
            ch = (last/base-1)*100; moves.append((lab, ch))
            print(f'  {lab:13}{last:>12,.2f}{ch:>+9.2f}{base:>12,.2f}   {s.index[-1].date()}')
        except Exception:
            print(f'  {lab:13}   -- n/a')
    print('  (chg% is vs the BASE column = prior session close. Compare PRICES across runs.)')
    _price_alarms(title, moves)

# ── PRICE ALARMS — added 8/1 after the scanner printed SK hynix +29.95% (0.05pp off the
#    KRX daily limit) next to Micron -5.90% and raised NOTHING. Every alarm below is
#    PRICE-ONLY. The keyword tier could not have caught it: the KOREA thread's words are
#    kospi/circuit breaker/de-gross/margin call, and the wire said "SK Hynix Surged 30% in
#    South Korea." A limit-up is not a vocabulary event.
#    ⇒ THE GAP WAS STRUCTURAL: the scanner held prices and headlines in the same run and
#      NEVER CROSSED THEM. A move can be the story even when no headline says so.
LIMIT_UP = {'Samsung Elec': 30.0, 'SK hynix': 30.0}      # KRX daily price limit, +/-30%
def _price_alarms(title, moves):
    if not moves: return
    out = []
    for lab, ch in moves:
        lim = LIMIT_UP.get(lab)
        if lim and abs(ch) >= lim - 0.5:
            out.append(f'!! {lab} {ch:+.2f}% — WITHIN 0.5pp OF THE {lim:.0f}% DAILY LIMIT. '
                       f'A limit move is a FLOW event until proven fundamental. Check the ADR: '
                       f'if it disagrees, the local move is positioning, not news.')
        elif abs(ch) >= 10:
            out.append(f'!! {lab} {ch:+.2f}% — DOUBLE-DIGIT SINGLE SESSION on a mega-cap. '
                       f'Confirm it is not a split/dividend/currency artifact BEFORE reading it.')
    hi, lo = max(moves, key=lambda x: x[1]), min(moves, key=lambda x: x[1])
    spread = hi[1] - lo[1]
    if spread >= 15:
        out.append(f'!! DISPERSION {spread:.1f}pp INSIDE ONE BLOCK — {hi[0]} {hi[1]:+.2f}% vs '
                   f'{lo[0]} {lo[1]:+.2f}%. Same industry moving opposite is a SORT, not a drift: '
                   f'name the axis it sorted on before reading any single name.')
    if out:
        print(f'  {"-"*72}')
        for o in out: print(f'  {o}')

# ---------------------------------------------------------------- FRONT END
# Yahoo has no clean 2Y ticker (^FVX=5Y, ^IRX=13wk), so the 2Y comes from FRED.
# THIS IS NOT DECORATION: the 2Y is the registered KILL SWITCH on the Fed-hike
# call (predictions/2026-07-30-fed-hike-before-december.md). The scanner ran a
# full window on 7/31 WITHOUT it, which is the one number the call turns on.
#   2Y RISING while the 30Y stalls  = BEAR FLATTENING = the market pricing hikes
#   2Y FALLING while the 30Y rises  = inflation-TOLERANCE steepening (the 7/29 read)
def front_end_block():
    import urllib.request, io as _io
    print('\n### FRONT END / CURVE  (FRED — the Fed-call kill switch)')
    out = {}
    for sid in ('DGS2', 'DGS10', 'DGS30'):
        try:
            raw = urllib.request.urlopen(
                f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}', timeout=25).read().decode()
            d = pd.read_csv(_io.StringIO(raw)); d.columns = ['date', sid]
            d[sid] = pd.to_numeric(d[sid], errors='coerce')
            d = d.dropna()
            out[sid] = (float(d[sid].iloc[-1]), float(d[sid].iloc[-2]), d['date'].iloc[-1])
        except Exception as e:
            print(f'  {sid:13}   -- FRED fetch failed ({type(e).__name__})')
    if not out:
        print('  !! front end unavailable — the Fed kill switch CANNOT be read this run'); return
    print(f'  {"":13}{"last":>12}{"chg bp":>9}{"BASE":>12}   as of')
    for sid, lab in (('DGS2','US 2Y'), ('DGS10','US 10Y (FRED)'), ('DGS30','US 30Y (FRED)')):
        if sid in out:
            l, b, dt = out[sid]
            print(f'  {lab:13}{l:>12.2f}{(l-b)*100:>+9.0f}{b:>12.2f}   {dt}')
    if 'DGS2' in out and 'DGS30' in out:
        l2, b2, _ = out['DGS2']; l30, b30, _ = out['DGS30']
        sp, spb = l30 - l2, b30 - b2
        print(f'  {"2s30s":13}{sp:>+12.2f}{(sp-spb)*100:>+9.0f}{spb:>+12.2f}')
        d2, d30 = (l2-b2)*100, (l30-b30)*100
        if   d2 > 0 and d30 <= d2: verdict = 'BEAR FLATTENING — front end leading = market pricing HIKES'
        elif d2 < 0 and d30 > 0:   verdict = 'inflation-TOLERANCE steepening — 2Y down, long end up'
        elif d2 > 0 and d30 > d2:  verdict = 'bear steepening — long end leading'
        else:                      verdict = 'no clean signal this session'
        print(f'  -> {verdict}')
    print('  (FRED lags ~1 session vs the Yahoo quotes above. Compare LEVELS, not timestamps.)')

# ---------------------------------------------------------------- KEYWORDS
# ~45 terms, thread-tagged. \b-anchored so short acronyms don't false-match
# (SPR must not hit "spread", CDS must not hit "CDSL", etc).
# ═══════════════ THREAD MAP BEGIN — single source of truth ═══════════════
# The router EXECS this block as real Python (sentinel-delimited), so comments and
# apostrophes are safe — the 8/8 regex-parser bug class is structurally dead.
# DESIGN (rebuilt 2026-08-08 after FIVE gaps in one day, #13-#17):
#   Every thread carries THREE vocabulary layers, because each missed for a different reason:
#   1. CONCEPTS  — what the thread is about        (the original map had only these)
#   2. ENTITIES  — proper nouns: tickers, companies, people, places, models, agencies
#                  (gaps #13/#14/#15/#16: materials, robotics policy, model names, alliances)
#   3. MEASURES  — the data vocabulary that REPORTS on the thread: series names, assessors,
#                  ratio/flow words (gap #17: flows/positioning; gap #12: earnings quality)
#   Layers are merged per-list (the matcher is flat); the discipline is in AUTHORING:
#   when adding a thread, fill all three layers or say why one is empty.
#   Duplicates ACROSS threads are fine — a hit can legitimately tag two threads.
#   Gap history stays here as comments; it is the map's calibration record.
THREADS = {
 # ── MEMORY ──
 'MEMORY':    ['dram','hbm','nand','memory price','memory chip','chip shortage',
               'cxmt','micron','hynix','sk hynix','samsung','sandisk','sndk','kioxia',
               'western digital','wdc',
               'contract price','spot price','bit growth','wafer input'],
 # ── SEMIS ──
 # gap #26 (2026-08-18, Jake): ETCHED had ZERO vault coverage despite a $5B->$21B ladder in 8 months,
 # SK Hynix on the cap table and a named production customer. Inference-ASIC challengers had no thread.
 'INF-ASIC':  ['etched','sohu','inference asic','inference chip','rack-scale','rack scale',
               'low voltage inference','cluster scale memory','mlperf','mlcommons',
               'groq','cerebras','sambanova','tenstorrent','furiosa','rebellions','d-matrix',
               'tokens per watt','tokens per dollar','tokens-per-watt','decode phase','prefill',
               'serdes','retimer','optical dsp','co-packaged optics','cpo','substrate','interposer'],
 'SEMIS':     ['wafer','foundr','lithograph','advanced packaging','chip capex',
               'tsmc','asml','nvidia','nvda','amd','broadcom','avgo','intel','qualcomm',
               'rubin','blackwell','h100','h200','gb200','cowos'],
 # gap #13 (2026-08-08): rare-earth/magnet/humanoid had NO thread; duplicate note filed.
 # gap #14 (2026-08-08): robotics POLICY vocabulary (fcc, import ban, producer names).
 'MATERIALS': ['rare earth','rare-earth','magnet','ndfeb','ndpr','neodymium','dysprosium',
               'terbium','praseodymium','critical mineral','permanent magnet','mgoe',
               'humanoid','actuator','reducer','robotics','physical ai','motion control',
               'robot dog','quadruped','embodied',
               'harmonic drive','nabtesco','mp materials','lynas','vulcan elements',
               'reelement','niron','tuopu','sanhua','inovance','unitree','agibot','ubtech',
               'figure ai','optimus','noveon','vacuumschmelze','energy fuels','ucore',
               'arafura','niocorp','serra verde','torngat','pensana','traxys','nidec',
               'solvay','shanghai metals','smm',
               'fcc','import ban','import control','entity list','section 232',
               'price floor','offtake','fob china','book-to-bill','order intake'],
 # gap #11 (8/5): filer names. gap #12 (8/8): earnings-quality measures.
 'CAPEX':     ['capex','capital expenditure','data center','data centre','hyperscaler',
               'off-balance','uncommenced','not commenced','depreciation','useful life',
               'useful-life','finance lease','self-funding',
               'spacex','spcx','starlink','microsoft','msft','alphabet','googl','google',
               'amazon','amzn','meta','oracle','orcl','openai','anthropic','stargate','xai',
               'unrealized','unrealised','mark-to-market','marked up','equity investment',
               'equity securities','earnings quality','net margin','earnings beat',
               'operating cash flow','free cash flow','net income'],
 'SHEETS':    ['balance sheet','net cash','gross debt','total debt','commercial paper',
               'purchase commitment','purchase obligation','operating lease','finance lease',
               'stockholders equity','cash pile','stake book','non-marketable','sheets board',
               'sheets ledger','net debt','buyback capacity'],
 'FINANCING': ['credit default','cds','private credit','bdc','spv','neocloud','coreweave',
               'nebius','bond sale','off balance sheet','vendor financing',
               'lockup','lock-up','tender offer','share unlock','secondary sale','follow-on',
               'blue owl','apollo','blackstone','ares','oaktree','diameter','valor','obdc',
               'ig spread','high yield','spread widen','non-accrual','downgrade','issuance',
               'trs','total return swap','13f','situational awareness','aschenbrenner',
               'acie','nscale','neocloud spv','dwarkesh','venture capital','venture debt','vc fund','venture round',
               'dsx','residual value','gpu-hour','investable asset',
               'coatue','citadel','prime brokerage','prime book','swap position',
               # gap #21, 8/12: a paste of CRWV MANAGEMENT'S OWN REALISED A100/H100 PRICING —
               # the exact transacted datum this thread had registered THREE TIMES — matched
               # FINANCING(1)* on the single word "coreweave" and nothing else. The whole
               # SILICON-GENERATION + RATE vocabulary was absent from all three layers, so the
               # depreciation/collateral thread could not see its own subject matter.
               # ENTITIES — the generations ARE the proper nouns of this thread:
               'a100','h100','h200','b200','gb200','ampere','hopper','blackwell','vera rubin',
               'grace hopper','p4d','p4de','silicon data','sda100rt','lambda labs','crusoe',
               # CONCEPTS — the depreciation/underwriting argument:
               'depreciation','useful life','economic life','warranty','rate card','recontract',
               'sold out','prior-generation','prior generation','older generation','obsolescence',
               'residual','rvg','fleet life','refresh cycle','scrap',
               # MEASURES — how the rate is REPORTED:
               'rental rate','realised pricing','realized pricing','per gpu-hour','$/gpu-hr',
               'gpu hour','rate curve','active mw','contracted power','utilisation','utilization',
               'backlog','implied rate','asp','average selling price',
               # gap #25b (8/13): same inbound, same failure on the CREDIT axis. The thread held
               # 'residual value','rvg','vendor financing','obsolescence' — the credit-desk terms —
               # and could not see "duration of the loan", "retain values", "hamster wheel". The
               # phrase "for the duration of the loan" is a DIRECT hit on this note's own
               # registered test #1 (`:4138` the paper's TENOR vs the collateral's generation
               # clock) and the router handed back silence.
               'hamster wheel','treadmill','circular','circular financing','duration of the loan',
               'loan duration','loan tenor','life of the loan','maturity wall','maturity ladder',
               'weighted average maturity','retain value','retain values','collateral value',
               'resale','secondary market','marginal buyer','refinanc','roll the debt'],
 # gap #22, 8/12: "VIX is like 14, feels coiled" matched NOTHING — no thread at all — while the
 # vault holds a BACKTESTED result on exactly that question (where-the-edge-is:73, "filtering on
 # VIX LEVEL fails"), a VIX history across four notes, and an options thread. The map could not
 # see the single most common way a market question gets asked. CONCEPTS/ENTITIES/MEASURES:
 'VOL':       ['vix','vvix','move index','volatility index','implied vol','realised vol',
               'realized vol','iv/rv','iv rank','iv percentile','variance risk premium','vrp',
               'skew','term structure','contango','backwardation','vol of vol',
               'dispersion','correlation','implied correlation','cboe','0dte','gamma',
               'coiled','complacen','quiet market','low vol','vol crush','vol spike',
               'covered call','vol target','vol selling','put/call','straddle','strangle',
               '200-day','200 day','drawdown','tail hedge','convexity'],
 # gap #24 (2026-08-18): a UBS note on GERMAN GAS STORAGE + the RHINE matched WAR/OIL and CONSUMER only.
 # war-board:531 had ALREADY registered the gap in words -- "no European gas instrument at all" -- and it
 # sat open. Thread + wiki/europe-energy-crunch.md created together.
 'EUROGAS':   ['ttf','jkm','european gas','eu gas','dutch ttf','mwh','€/mwh','eur/mwh',
               'gas storage','storage level','storage target','injection season','withdrawal season',
               'regasification','regasif','fsru','lng terminal','lng cargo','lng import',
               'trading hub europe','gasunie','uniper','sefe','nord stream','norwegian maintenance',
               'troll','groningen','rhine','kaub','barge','low water','navigable',
               'gas-to-oil','gas to oil','fuel switching','switching','gasoil','heating season',
               'bundesnetzagentur','ehb','aggregate eu storage'],
 'POWER':     ['pjm','curtail','grid emergency','turbine','interconnection','smr',
               'behind-the-meter','ofgem','grid access','connection queue','commitment fee',
               'wolfspeed','silicon carbide','empower semiconductor','ionic digital',
               'grid operator','transmission','substation','ratepayer','moratorium',
               'nuclear','reactor','criticality','part 57','nrc',
               'avista','spokane','oklo','westinghouse','vistra','constellation','nextera',
               'ge vernova','ercot','caiso','datacenter power','megawatt','gigawatt',
               # gap #19 (2026-08-23): THE FUEL-SOURCE POLITICS LAYER. A daily scan carried
               # "~200 MAHA-aligned activists urged the administration not to use AI/data-centre
               # growth to justify expanded COAL generation" and the map returned NOTHING --
               # `grep -rn coal wiki/` hits only the word "coalition". The vault's power thesis
               # has priced gas, nuclear, renewables and the interconnection queue and has NEVER
               # priced the COAL option, in either direction: as competing supply that would
               # relieve the scarcity the thesis trades, or as the political fight over it.
               'coal','lignite','retirement deferral','coal plant','fuel source',
               'maha','clean air','emissions rule','epa','sierra club','air permit'],
 # gap #18 (2026-08-09): Western-hemisphere replacement-barrel vocabulary — a Venezuela-imports
 # paste weak-matched ALLIANCE(1)* while demand-destruction held the +1.6M b/d offset line and the
 # China-routing prior. The oil map covered the DISRUPTED side, never the REPLACEMENT side.
 'WAR/OIL':   ['hormuz','qeshm','tanker','houthi','irgc','abqaiq','jazan','transit fee',
               'war risk','crack spread','refiner','lng',
               'iran','oman','majlis','fars','aramco','opec','brent','wti','kharg',
               'corridor','flag state','insurance premium',
               'venezuela','pdvsa','chevron','merey','heavy sour','heavy crude','guyana',
               'gulf coast','official selling price','crude import','import license'],
 'BLACK SEA': ['cpc','caspian pipeline','novorossiysk','tengiz','kashagan','karachaganak',
               'kazakh','kazakhstan','black sea','primorsk','ust-luga','druzhba','ceyhan'],
 'INVENTORY': ['spr','cushing','strategic petroleum','crude draw','crude build','tank bottoms',
               'eia','api inventory','days of supply'],
 # GAP #10 (8/5): the call's own subject. Entities + auction/liquidity measures added 8/8.
 # gap #23, 8/13: a PPI PRINT matched NO THREAD AT ALL. FED carried 'core cpi' and nothing else
 # from the inflation-release vocabulary — so the vault's own macro spine (new-economy-regime) and
 # its REGISTERED HIKE CALL were unreachable by the single most routine macro inbound there is.
 # ENTITIES = the releases and agencies; MEASURES = how a print is reported.
 # gap #22 (2026-08-17, Jake): "we've tracked corporate / 2 / 10 / 30y treasury bond spreads
 # closely" -- and there was NO thread for it. FED is policy; FINANCING is AI paper. The 8/17
 # brief's "10Y at 4.71%" matched FED(4) and landed nowhere. 187 curve mentions were buried in
 # new-economy-regime.md. Thread + wiki/rates-board.md created together.
 # gap #25 (2026-08-18, Jake): "Treasuries -> hyperscaler CDS/bond spreads -> bank/private-credit
 # appetite -> hyperscaler capex commitments -> AI supplier orders. Hierarchy." The vault had all five
 # subjects and no CAUSAL ORDER, so a propagation question had no address. -> wiki/transmission-chain.md
 # + wiki/hyperscaler-credit.md (stage 2, which had no note at all) + wiki/_timelines/_chain.md.
 'CHAIN':     ['transmission','propagation','pass-through','passthrough','feeds through','knock-on',
               'second-order','downstream','upstream','cost of capital','discount rate',
               'financial conditions','fci','conditions index','credit channel','funding channel',
               'lead-lag','lead lag','causal chain','hierarchy','the chain'],
 'HYPCREDIT': ['cds','credit default swap','5y cds','basis points of protection','spread over',
               'new-issue concession','new issue concession','issue concession','oas',
               'nvda cds','msft cds','googl cds','meta cds','orcl cds','crwv cds',
               'ig spread','investment grade spread','secondary spread','bond spread'],
 'RATES':     ['term premium','yield curve','curve steepen','curve flatten','bear steepen',
               'bull steepen','inversion','inverted curve','2s10s','5s30s','10s30s',
               'long end','long-end','front end','duration','convexity','real yield',
               'breakeven','tips','10-year yield','10y yield','30-year yield','30y yield',
               'treasury yield','treasury yields','coupon supply','refunding','auction',
               'auction stop','tail','bid-to-cover','bid to cover','indirect bidding',
               'direct bidding','dealer takedown','bid dispersion','allotted at the stop',
               'primary dealer','qra','quarterly refunding','debt ceiling','issuance mix',
               'bills vs coupons','acm','adrian crump','moench',
               'ig spread','ig oas','high-yield spread','hy oas','credit spread','oas',
               'investment grade','high yield','spread widening','spread tightening',
               'corporate spread','cds spread','swap spread','sofr','move index',
               'jgb','gilt','bund','oat','btp','boj','yield curve control','ycc'],
 'FED':       ['ppi','producer price','cpi','pce','core pce','deflator','headline cpi',
               'bls','bea','import price','ism prices','prices paid','unit labor cost',
               'month-over-month','year-over-year','mom','yoy','annualised','annualized',
               'trade services','ex-food and energy','core inflation','disinflation',
               'sticky','supercore','breakeven','tips','2y','2-year','two-year','front end',
               'dot plot','sep','fomc','dissent','hike','cut','target range','r-star',
               'warsh','term premium','forward guidance','steepen','core cpi','supply shock',
               'dissent','rate hike','rate cut','rate pause','rate decision','fomc','fed funds','raise rate','cut rate','the fed',
               'fedwatch','hike odds','basis point','powell','hawkish','dovish','fed meeting',
               'rate expectations',
               'hammack','kashkari','waller','bostic','goolsbee','jefferson','bowman','daly',
               'treasury auction','30y auction','auction tail','bid-to-cover','indirect',
               'reserve balances','reverse repo','rrp','qt','tic data','dot plot','sep',
               # gap #19 (8/11): the RATES-VOL SURFACE was entirely absent. A ZH post on 3y10y
               # swaption payer skew + vol-of-vol returned only single-keyword matches, and the
               # vault holds just two lines on repo/SRF. The malign box (yields up + stocks down)
               # is priced HERE, and the map could not see the instrument that prices it.
               'swaption','payer','receiver','vol of vol','skew','3y10y','payer skew',
               'rate vol','rates vol','move index','repo market','standing repo facility','srf',
               'not qe','bessent','refunding','coupon auction','duration supply','term premium'],
 # gap #17 (8/8): measurement vocabulary — flows/positioning. NOT the proper-noun defect.
 'FLOWS':     ['fund flow','inflow','outflow','epfr','allocation','net buying','net selling',
               'retail flow','institutional flow','positioning','percentile','exposure',
               'de-gross','cta','systematic','risk parity','buyback','short interest',
               'put/call','skew','sentiment','aaii','bull-bear','cash levels',
               'fund manager survey','bofa','hartnett','record inflow','annualized'],
 # gap #15 (8/8): model NAMES + usage-share measures.
 'MODEL-ECON':['open-weight','open weight','routing layer','per-token','inference cost','agentic',
               'deepseek','qwen','kimi','glm','minimax','tencent','hunyuan','xiaomi','mimo',
               'llama','mistral','nemotron','gpt-5','gpt5','gemini','claude','grok','astra',
               'openrouter','leaderboard','token usage','token share','token volume',
               'market share','usage share','model ranking','trillion tokens',
               # gap #18 (8/11): Zuckerberg manifesto matched POWER/CAPEX but NOT model-econ —
               # 'open source' (vs 'open-weight'), distillation and checkpoint vocabulary missing.
               'open source','open-source','distillation','distill','training checkpoint',
               'intermediate checkpoint','personal superintelligence','superintelligence',
               'recursive self-improvement','rsi','frontier lab','model release',
               # gap #25a (8/13): Jake's recursive-self-improvement argument scored NO MATCH on the
               # router AND zero on the full-text sweep — while THIS THREAD ALREADY HELD
               # 'recursive self-improvement' and 'superintelligence'. The map had the LAB JARGON
               # and none of the PLAIN ENGLISH. He wrote "learning from its own research and
               # failures" and "the learning curve … goes vertical"; the map could only see the
               # paper-title form of the same idea. THE CLASS: the map is keyed to how SOURCES
               # write, not how JAKE writes — and his own theses are this vault's highest-value
               # inbound. Fix the register, not just the words.
               'learning curve','goes vertical','self-improving','self improvement',
               'improve itself','improves itself','its own research','ai research',
               'automate research','automating research','research loop','flywheel',
               'takeoff','scaling law','scaling laws','capability curve','own failures'],
 # gap #26 (8/14): JULY RETAIL SALES + UMICH SENTIMENT + BUSINESS INVENTORIES scored FED(3) on
 # inflation vocabulary alone and NOTHING on the consumer. THE MAP HAD ZERO CONSUMER-DEMAND
 # VOCABULARY -- no 'retail sales', no 'control group', no 'michigan', no 'consumer sentiment',
 # no 'nonstore'. THE LARGEST COMPONENT OF GDP WAS INVISIBLE TO THE ROUTER, and the vault's own
 # PRE-REGISTERED call on this exact print (market-fragility:2625, GS -0.1% vs consensus +0.1%,
 # "Prime-Day timing payback -0.2pp on core") was reachable only through a full-text sweep.
 # 'INVENTORY' already existed but means SPR/crude -- a homonym, not a consumer thread.
 'CONSUMER':  [# CONCEPTS
               'retail sales','control group','consumer spending','consumer sentiment',
               'consumer confidence','personal consumption','discretionary','staples',
               'trade-down','trade down','pull-forward','pull forward','back-to-school',
               'holiday spend','same-store','comparable sales','foot traffic','wallet share',
               'delinquenc','subprime auto','buy now pay later','bnpl','revolving credit',
               'savings rate','excess savings','real income','disposable income',
               # ENTITIES
               'michigan','umich','conference board','census bureau','advance retail',
               'redbook','prime day','black friday','walmart','target','costco','amazon',
               'dollar general','dollar tree','tjx','ross stores','burlington',
               # MEASURES
               'nonstore','ex-autos','ex autos','ex-auto','food services','restaurants and bars',
               'general merchandise','business inventories','inventory/sales','inventories-to-sales',
               'retail-only','one-year inflation expectations','five-year inflation expectations',
               'inflation expectations','sentiment index','expectations index','current conditions'],
 'FX/CARRY':  ['yen','jpy','usd/jpy','usdjpy','boj','bank of japan','carry trade','repatriation',
               'currency intervention','fx intervention','fx reserves','ministry of finance',
               'dxy','dollar index','ueda','mof','kanda','jgb','japan sold','tic shows'],
 'AI-POLICY': [
               # gap #24, 8/13: "regulatory depreciation / MW-per-token efficiency standards" matched
               # SEMIS(2) and nothing on the POLICY axis, while the vault had ZERO coverage of
               # best-available-technology regulation -- a third depreciation channel it had never
               # considered. CONCEPTS/ENTITIES/MEASURES for efficiency-standard regulation:
               'best available technology','bact','mact','laer','ecodesign','energy efficiency directive',
               'efficiency standard','efficiency mandate','cafe standard','emissions standard',
               'pue','power usage effectiveness','perf per watt','performance per watt','watts per token',
               'mw per token','mlperf','benchmark standard','regulatory obsolescence','regulatory depreciation',
               'data centre moratorium','data center moratorium','ratepayer','interconnection queue reform',
               'export control','entity list','blacklist','huawei','huang','jensen',
               'chip ban','chip export','tech transfer','sovereign ai','ai regulation',
               'ai policy','diffusion rule','deregulat','preempt','smic','state ai law',
               'executive order','white house','ai framework','voluntary framework',
               'model evaluation','capabilities testing','pre-release','frontier model',
               'ai safety','ai executive','classified threshold','trusted partner',
               'ai act','model access','safety institute','nist ai','red team'],
 'KOREA':     ['kospi','kosdaq','circuit breaker','de-gross','degross','leveraged etf',
               'margin call','south korea','limit up','limit-up','daily limit','krx','korea'],
 'LABOR':     ['payroll','jolts','job openings','unemployment','jobless','nonfarm',
               'hires','quits rate','layoffs','labor market','labour market','wage growth',
               'initial claims','continuing claims','adp employment',
               'bls','household survey','participation rate','multiple jobholders',
               'full-time','part-time','productivity','unit labor cost'],
 'MUNITIONS': ['atacms','tomahawk','munition','stockpile','prsm','precision strike',
               'defense production act','missile inventory','replenish','ordnance',
               'supplemental appropriation','arms sale','patriot','interceptor','thaad'],
 # gap #16 (8/8): alliances had no vocabulary — war was reachable only via weapons/oil/theatres.
 'ALLIANCE':  ['defense pact','defence pact','mutual defense','mutual defence','collective defense',
               'collective defence','article 5','joint defence','joint defense','security guarantee',
               'saudi','pakistan','turkey','turkiye','erdogan','bin salman','sharif','mecca',
               'riyadh','islamabad','ankara','nato','treaty','accession','mjda'],
 'LEVANT':    ['lebanon','hezbollah','israel','litani','leviathan','karish','rome talks',
               'framework agreement','ceasefire','idf','beirut','northern front'],
 'TOKEN-ECON':['token cost','token price','per token','tokens per','inference cost',
               'api pricing','price per million','intelligence per watt','tokens per watt',
               'token expenditure','compute cost','gpu rental','jevons','price war',
               'inference revenue','cost per task',
               'custom chip','in-house chip','custom silicon','asic','tpu','trainium',
               'co-design','custom accelerator',
               'silicon data','sdllmtk','cheaperinference',
               # gap #18 (8/11): an explicit AUCTION-PRICED inference mechanism was announced by a
               # principal and TOKEN-ECON could not see it. Pricing MECHANISM vocabulary was absent.
               'auction','dynamic auction','lowest price','compute auction','spot price',
               'marginal cost of intelligence','per gigawatt','intelligence per gigawatt'],
 # gap #20 (2026-08-12): a Goldman TMT note on "Google Zero" / crawler unbundling matched CAPEX(2)
 # only — the vault had ZERO mentions of crawler, Google Zero, search traffic or content licensing.
 # CONTENT is the one AI input the map could not see: compute, power, memory and capital all had
 # threads; the TRAINING CORPUS did not.
 'CONTENT-TOLL':['google zero','zero click','zero-click','ai overview','ai overviews',
                 'crawler','crawlers','googlebot','robots.txt','scraping','scraper',
                 'search referral','referral traffic','search traffic','organic traffic',
                 'publisher','publishers','content licensing','licensing deal','pay per crawl',
                 'training data','data licensing','corpus','opt out','opt-out',
                 'cloudflare','semrush','nieman','digiday'],

 # MAP GAP #27 (2026-08-16). The vault runs SCREENS and BACKTESTS -- quiet-health-screen,
 # sp500_health_screen.py, durable_value_screen.py, the 52-week scans, bandwidth_parity_cell --
 # and the map had ZERO vocabulary for the METHOD. A paste describing a point-in-time EDGAR
 # backtest returned NO THREAD MATCHED while the sweep found six notes.
 # ⇒ SAME CLASS AS #25/#26: the map was keyed to what the vault CONCLUDES, never to how it
 #   MEASURES. Screens are a recurring artifact type here; they needed a thread of their own.
 # MAP GAP #28 (2026-08-19). MODERNA GAPPED +125% ON A PHASE 3 CANCER-VACCINE READOUT, MERCK
 # +10.6% WITH IT, IBB +4.8% -- and the map had ZERO clinical/biotech vocabulary. The sweep
 # could only reach quiet-health-screen, and only because the word "health" is in the filename.
 # => Same class as #25/#26/#27: the vault had a HEALTH SCREEN but no thread for the EVENTS
 #   that reprice health. A binary readout is the single largest one-day repricing mechanism
 #   in the market and the gate could not see one arrive.
 'BIOTECH':['phase 1','phase 2','phase 2b','phase 3','phase iii','readout','topline','top-line',
            'clinical trial','trial results','primary endpoint','endpoint met','overall survival',
            'progression-free','recurrence-free','hazard ratio','fda','pdufa','breakthrough therapy',
            'accelerated approval','biologics license','bla','nda',
            'approval','label expansion','oncology','immunotherapy','checkpoint','neoantigen',
            'cancer vaccine','personalized vaccine','individualised','individualized','mrna',
            'moderna','merck','pfizer','biontech','regeneron','gilead','vertex','lilly',
            'novo nordisk','keytruda','biotech','biotechnology','xbi','ibb','pipeline',
            'orphan drug','patent cliff','loss of exclusivity'],

 # MAP GAP #29 (2026-08-19). Trump's "ECONOMIC D-DAY" post -- an explicit SECONDARY-SANCTIONS threat
 # naming oil smuggling, swap lines, cash transfers, exchange houses, ship registries and front
 # companies -- routed as POWER(1)*, WAR/OIL(1)*, NUCLEAR(1)*, all single-keyword. The map had
 # vocabulary for WAR and for OIL but none for the ENFORCEMENT MACHINERY that connects them.
 # => Sanctions are how this conflict is actually being fought; the gate could not see the weapon.
 'SANCTIONS':['secondary sanctions','sanctions evasion','ofac','sdn list','designation','designated',
              'export control','entity list','correspondent bank','correspondent banking','swift',
              'de-risking','exchange house','hawala','front company','front companies','shell company',
              'ship registry','ship registries','flag state','flag of convenience','deflag','reflag',
              'shadow fleet','dark fleet','ais spoofing','ship-to-ship','sts transfer','p&i club',
              'price cap','embargo','blockade','asset freeze','licence','license','waiver','carve-out',
              'snapback','executive order','federal register','treasury department','economic warfare'],

 # MAP GAP #30 (2026-08-20, Jake's spec). The vault tracks financing stress across FIVE notes
 # (ai-financing-fragility, hyperscaler-credit, rates-board, transmission-chain, balance-sheet-board)
 # and had no single STATE reading. Jake: "a running macro read on the financing of all of this...
 # every upload creates a shift to more, less or neutral on fragility."
 'FRAGILITY':['fragility','financing','refinanc','rollover','maturity wall','new-issue concession',
              'concession','order book','oversubscribed','undersubscribed','pulled deal','postponed',
              'break issue','syndicate','underwriter','private credit','bdc','business development',
              'redemption','gated','nav','mark to market','leverage ratio','covenant','downgrade',
              'outlook change','fallen angel','ig index','mandate','forced selling','spv','abs',
              'securitis','securitiz','residual value','rvg','guarantee','first loss','offtake',
              'vendor financing','circular','dilution','equity offering','shelf','atm offering'],

 'SCREEN-METHOD':['backtest','back-test','point-in-time','point in time','look-ahead',
                  'lookahead','look ahead bias','survivorship','survivorship bias',
                  'formation date','holding period','control group','universe',
                  'edgar','xbrl','companyfacts','10-k','10-q','filed date','as-reported',
                  'restatement','restated','split-adjusted','split adjusted',
                  'trailing twelve','ttm','year-to-date','ytd','discrete quarter',
                  'p/e','pe ratio','earnings yield','trailing e','forward multiple',
                  'peak earnings','peak-cycle earnings','normalised earnings','normalized earnings',
                  'median earnings','durability','screen','screener','pass rate',
                  'sector-neutral','beat-rate','spread vs benchmark'],
}

# THREAD -> ORIGINATING VAULT NOTE. Every hit routes BACK to the note it came from.
ROUTE = {
 'VOL':       'where-the-edge-is (the VRP/200-day studies) / market-fragility / options-reference-natenberg / portfolio-state',
 'MEMORY':    'memory-regime-question / compression-thesis',
 'SEMIS':     'ai-infra-allocation-map / buildout-bottleneck-map',
 'MATERIALS': 'buildout-bottleneck-map (the magnet chokepoint, 8/4 + 8/8) / physical-ai-hardware-stack (actuators/reducers) / war-board',
 'CAPEX':     'ai-capex-cycle / cepi / balance-sheet-board',
 'SHEETS': 'balance-sheet-board / ai-financing-fragility',
 'FINANCING': 'ai-financing-fragility / balance-sheet-board',
 'POWER':     'buildout-bottleneck-map / power-not-petroleum / nuclear',
 'WAR/OIL':   'demand-destruction / war-board / oil-value-chain',
 'BLACK SEA': 'demand-destruction (CPC/Kazakh outage) / oil-value-chain',
 'INVENTORY': 'demand-destruction (SPR clock)',
 'CHAIN':      'transmission-chain (THE SPINE -- read the stage order first) / _timelines/_chain.md (merged running log, all 5 stages)',
 'HYPCREDIT':  'hyperscaler-credit (stage 2: CDS/spreads for the AI complex) / ai-financing-fragility / rates-board',
 'RATES':     'rates-board (THE curve/spread board: level, auction internals, the 4-route long-end conclusion) / new-economy-regime (the argument in full) / market-fragility',
 'EUROGAS':    'europe-energy-crunch (THE European gas/Rhine instrument) / war-board / oil-value-chain',
 'FED':       'new-economy-regime / market-fragility / predictions (the registered hike call)',
 'CONSUMER':  'consumption-vs-investment-crux (THE spine question) / new-economy-regime / market-fragility (the weekly data calendar + GS pre-print forecasts) / glp1-wardrobe-cycle (the apparel line) / trade-down-landing-pads / demand-destruction',
 'FLOWS':     'market-fragility (the 7/22 gearing frame + 8/8 record tech inflows) / detachment-bid / portfolio-state',
 'MODEL-ECON':'metered-compute / compression-thesis',
 'FX/CARRY':  'ai-financing-fragility (yen-carry corners the Fed, L491) / market-fragility / new-economy-regime',
 'AI-POLICY': 'ai-financing-fragility (blacklist timeline, F17 risk stack) / metered-compute (the NVDA letter, the council) / ai-capex-cycle (advisory council) / compression-thesis (two-bloc)',
 'KOREA':     'market-fragility (leverage cascade)',
 'LABOR':     'predictions/2026-07-30-fed-hike (the registered Friday trigger) / new-economy-regime',
 'MUNITIONS': 'war/war-board (escalation ceiling, the A-vs-C fork) / ai-capex-cycle (defense-AI crowding)',
 'ALLIANCE':  'war/war-board (MJDA 8/8 — verified; Article 5 language vs Article 5 capability) / demand-destruction / oil-value-chain',
 'LEVANT':    'war/war-board (talks-while-shooting; MoU Article 1 broke via Lebanon -- portfolio-state L143)',
 'TOKEN-ECON':'metered-compute (the Jevons/elasticity-1 test) / compression-thesis / cepi',
 'CONTENT-TOLL':'content-toll / metered-compute (same metering architecture, different input) / compression-thesis',
 'BIOTECH':   'quiet-health-screen (the value x health x NO-STORY screen -- a catalyst name is what it EXCLUDES by construction) / rotation-stickiness / dip-buying-base-rates (MRNA is the canonical single-catalyst runner in that note) / structural-pull-log',
 'SANCTIONS':  'war/war-rhetoric (threats and un-executed declarations -- the artifact test lives here) / war/war-board / war/war-confirmed / oil-value-chain / demand-destruction',
 'FRAGILITY':  'financing-fragility-gauge (THE STATE DIAL -- read this first, it is the one-page reading) / ai-financing-fragility (the detail) / hyperscaler-credit / rates-board / transmission-chain / balance-sheet-board',
 'SCREEN-METHOD':'quiet-health-screen (the 2026-07-05 snapshot screen + its peak-cycle-earnings caveat) / durable-value-backtest (the point-in-time test of that caveat) / colab-archive-audit (which tools exist and which are trustworthy) / runner-anatomy / market-fragility',
}
# ═══════════════ THREAD MAP END ═══════════════

# TWO KEYWORD CLASSES — this distinction is the whole gate and it was WRONG on first build.
# STRICT: short acronyms where a suffix creates a false positive. \bKWs?\b only.
#   spr must NOT match "spread"; cds must NOT match "CDSL"; dram must NOT match "drama".
# STEM: everything else gets up to 3 trailing chars, because headlines use plurals and
#   verb forms far more than base forms. (3 of 14 offline unit-test cases failed before this fix.)
STRICT = {'spr','cds','bdc','spv','hbm','pjm','smr','irgc','dram','nand','lng','cpc','smic',
          'yen','jpy','boj','dxy','ueda','mof','qt','sep','bls','nrc','smm','eia','rrp','mjda',
          'wti','glm','tpu','fcc','krx','idf','trs','13f','rvg'}
def _pat(k):
    return re.compile(r'\b'+re.escape(k)+(r's?\b' if k in STRICT else r'\w{0,3}\b'), re.I)
PATS = {th: [_pat(k) for k in ks] for th, ks in THREADS.items()}
NKEY = sum(len(v) for v in THREADS.values())

def tags(text):
    return [th for th, ps in PATS.items() if any(p.search(text) for p in ps)]

# ═══════════════════════════════════════════════════════════════════════════════
# OPEN FLAGS REGISTRY — the second gate, and the more important one.
#
# The keyword gate answers "is this ON-TOPIC". That is not the same question as
# "is this WORTH READING". A headline earns a follow-up only if it can CLOSE
# something the vault has registered as UNRESOLVED (⚠️) or LOGGED AS WRONG (⛔).
#
# Every entry below is a real, dated, open item from a vault note. `q` states what
# would actually resolve it — not the topic, the MISSING FACT. `pat` detects a
# candidate resolver. Retire an entry the moment it closes; a stale registry
# manufactures false urgency.
# ═══════════════════════════════════════════════════════════════════════════════
WATCH = [
 dict(id='F1', pri=1, note='ai-capex-cycle',        since='07-29',
      q='Is MSFT $130B new leases a SUBSET of the $329.1B uncommenced total, or ADDITIVE? '
        'A quarter that created a third of the off-balance-sheet obligation is a rate, not a stock.',
      pat=r'(lease|uncommenced|off.balance|329|130 ?b|\$130)'),
 dict(id='F2', pri=1, note='ai-financing-fragility', since='07-29',
      q='SPREAD, TENOR and TAKE-UP on the Goldman $5.4B MSFT-tied and Blue Owl $5.9B deals. '
        'Size alone supports neither containment nor cascade. Primary prices MARGINAL risk.',
      pat=r'(goldman|blue owl|data cent\w* (debt|loan|financ)|private credit|syndicat|spv)'),
 dict(id='F3', pri=1, note='memory-regime-question', since='07-28',
      q='The CXMT fork: glut vs politically walled out. Is the Senate action a LETTER or a BILL? '
        'A letter is noise; an enforcement mechanism is the wall. Second, COMMERCIAL evidence on '
        'the same fork: buyers signing multi-year supply deals are pre-committing AGAINST Chinese '
        'supply filling the gap — money at stake rather than votes.',
      pat=r'(cxmt|chinese memory|apple.*(memory|chip)|senator|export control|entity list|'
            r'long.?term supply|supply (deal|agreement)|multi.?year (supply|contract))'),
 dict(id='F4', pri=1, note='demand-destruction',     since='07-30',
      q='CPC/Kazakh loading status AFTER the 7/30 re-attack. Force majeure? August loading program? '
        'THE VAULT MISSED THIS THEATRE FOR ELEVEN DAYS — treat every CPC item as priority until caught up.',
      pat=r'(cpc|caspian|novorossiysk|tengiz|kashagan|kazakh|force majeure)'),
 dict(id='F5', pri=2, note='demand-destruction',     since='07-30',
      q='Are QatarEnergy\'s 33 US cargoes SPOT or TERM? Spot bridges weeks; term prices permanence. '
        'This is the cleanest available test of the structural-vs-episodic branch.',
      pat=r'(qatarenergy|qatar.*(lng|cargo)|33 cargo|term contract|spot cargo)'),
 dict(id='F6', pri=2, note='new-economy-regime',     since='07-30',
      q='The actual dissent COUNT and the 1970 comparison set. I retracted a 56-year record because '
        'it was engineered — intent revises meaning, not magnitude.',
      pat=r'(dissent|1970|fomc vote|voted against)'),
 dict(id='F7', pri=2, note='buildout-bottleneck-map', since='07-29',
      q='Ofgem commitment fee LEVEL, and is it REFUNDABLE on commencement? A refundable deposit is '
        'anti-squatting; a non-refundable fee is a real price on the optionality MSFT was rewarded for.',
      pat=r'(ofgem|commitment fee|connection queue|grid access|interconnect)'),
 dict(id='F8', pri=2, note='ai-financing-fragility',  since='07-29',
      q='The neocloud NAMED CASUALTY. Five sessions of double-digit drawdown, still nobody named. '
        'Absence is the strongest datum in the containment case — until it is not.',
      pat=r'(coreweave|nebius|neocloud|crusoe|lambda|default|covenant|going concern|missed payment)'),
 dict(id='F9', pri=3, note='memory-regime-question', since='07-30',
      q='SK hynix Q2 miss MAGNITUDE, and Micron CEO sale size + 10b5-1 status. A CEO sale without '
        'size, plan status and prior cadence is not evidence.',
      pat=r'(hynix.{0,40}(miss|consensus|target|guidance|shortfall)|10b5|mehrotra|(insider|ceo).{0,20}(sold|sale|selling))'),
 # F11 CLOSED 07-30: cap SPX -2.32% MTD vs EW SPX +1.39% -- inversion confirmed, and the
 # EW-vs-cap test returned the OPPOSITE sign from my prediction (damage is in the mega-caps,
 # not the crowded tail). Replaced by the live containment trigger, which is now a PRICE.
 dict(id='F11',pri=1, note='market-fragility',       since='07-30',
      q='CONTAINMENT KILL SWITCH: does RSP close below 212.77 (the 2026-06-30 close, -2.3% from '
        'the 07-28 ATH) while NDX keeps falling? That is the average S&P stock giving back all of '
        'July -- rotation has become a broad de-rate. Currently 215.73, -1.37% away.',
      pat=r'(equal.?weight|equal.?weighted|breadth|rotation|rotat\w+ out|average stock|rsp\b|advance.decline)'),
 dict(id='F13',pri=1, note='demand-destruction',      since='07-30',
      q='THE CRUX: is China\'s 40%%+ import cut (~4.4 mb/d, larger than every supply loss combined) a\n        SUSPENSION or a STRUCTURAL SHIFT? Reversible = reserve draws, coal switching, deferred buying.\n        Irreversible = EV substitution. Nobody has published the split. Watch the July/August import\n        bounce, Chinese gasoline demand vs EV penetration, and reserve levels.',
      pat=r'(china.{0,30}(import|crude|demand|purchas|refin|reserve|stockpil)|chinese (crude|oil|buyer|demand)|teapot|kpler|vortexa|sinopec|unipec|spr refill)'),
 dict(id='F12',pri=1, note='demand-destruction',      since='07-30',
      q='Saudi Q2 GDP: is GASTAT\'s oil -24.7%% y/y or q/q SA? And does Saudi ABANDON its ~1 mb/d\n        cut to defend volume? An oil economy down ~25%% with non-oil at +0.9%% is fiscal pressure to\n        stop cutting -- the crude BEAR case, and the vault runs only the war-premium side.',
      pat=r'(saudi|gastat|aramco|opec|quota|production cut|market share|yanbu|east.?west pipeline)'),
 dict(id='F10',pri=3, note='ai-capex-cycle',         since='07-30',
      q='Zhongji InnoLight break SIZE and terms, and whether other AI-supply-chain deals are pulled. '
        'One broken debut is a datum; a second is a primary-market regime.',
      pat=r'(innolight|zhongji|(ipo|debut|listing|offering).{0,40}(tumbl|slump|break|below|flop|pull|postpon|withdraw|price[ds] at))'),
]
WPATS = [(w, re.compile(w['pat'], re.I)) for w in WATCH]

# Brands Jake can open behind a paywall — these get marked [GET] in the follow-up queue,
# because a fetchable primary source outranks a free paraphrase of it. (The Axios/Pacing
# error was built entirely on a one-sentence paraphrase of a document I could have read.)
GETTABLE = ('reuters', 'wsj', 'wall street journal', 'bloomberg', 'ft', 'financial times')

def flags(text):
    return [w for w, p in WPATS if p.search(text)]

def brand(title, src):
    if src: return src
    m = re.search(r' [-–] ([^-–]{2,40})$', title)
    return m.group(1).strip() if m else ''

# ---------------------------------------------------------------- FEEDS BY TIER
# CNBC: the search.cnbc.com/combinedcms endpoint returns a 682-byte error page with ZERO items.
# Verified working format is /id/<ID>/device/rss/rss.html (30 items each, fresh dates).
CNBC = 'https://www.cnbc.com/id/{}/device/rss/rss.html'
GN   = 'https://news.google.com/rss/search?q={}&hl=en-US&gl=US&ceid=US:en'
YF   = 'https://feeds.finance.yahoo.com/rss/2.0/headline?s={}&region=US&lang=en-US'

TIERS = [
 ('T1  FINANCIAL WIRE  (least partisan — read these first)', [
   ('MW-top',    'https://feeds.content.dowjones.io/public/rss/mw_topstories'),
   ('MW-bulletins','https://feeds.content.dowjones.io/public/rss/mw_bulletins'),
   # MW-marketpulse DROPPED: live-tested 30 items whose newest pubDate was Jul-2025.
   # Dead/static feed, not a parser bug — the dates really are a year old.
   ('CNBC-mkts', CNBC.format('20910258')),
   ('CNBC-fin',  CNBC.format('10000664')),
   ('SeekAlpha', 'https://seekingalpha.com/market_currents.xml'),
   ('Reuters-biz',GN.format('site:reuters.com+when:1d')),
   ('Bloomberg', GN.format('site:bloomberg.com+when:1d')),
   ('WSJ',       GN.format('site:wsj.com+when:1d')),
   ('FT',        GN.format('site:ft.com+when:1d')),
   ('YF:MU',     YF.format('MU')),
   ('YF:NVDA',   YF.format('NVDA')),
   ('YF:MSFT',   YF.format('MSFT')),
   ('YF:META',   YF.format('META')),
 ]),
 ('T2  NETWORKS + GOOGLE  (broad, mixed reliability)', [
   ('CNBC-top',  CNBC.format('100003114')),
   ('ABC-money', 'https://abcnews.go.com/abcnews/moneyheadlines'),
   ('ABC-intl',  'https://abcnews.go.com/abcnews/internationalheadlines'),
   ('GN-business','https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-US&gl=US&ceid=US:en'),
   ('GN-world',  'https://news.google.com/rss/headlines/section/topic/WORLD?hl=en-US&gl=US&ceid=US:en'),
   ('GN-hormuz', GN.format('Hormuz+OR+Qeshm+OR+tanker+when:1d')),
  # Second theatre. Do NOT fold this into GN-hormuz: a Hormuz-scoped query ranks Hormuz
  # results and buried an 1.8 mb/d Black Sea outage for eleven days. One feed per theatre.
  ('GN-blacksea', GN.format('CPC+OR+Novorossiysk+OR+Tengiz+OR+Kazakh+oil+export+when:1d')),
   ('GN-memory', GN.format('DRAM+OR+HBM+OR+CXMT+OR+memory+chip+when:1d')),
   ('GN-capex',  GN.format('hyperscaler+capex+OR+data+center+capex+when:1d')),
   ('GN-grid',   GN.format('PJM+OR+grid+curtail+data+center+when:1d')),
 ]),
 ('T3  FAST / OPINIONATED  (speed over neutrality — verify before weighting)', [
   ('ZeroHedge', 'https://cms.zerohedge.com/fullrss2.xml'),
   ('Fox-biz',   'https://moxie.foxbusiness.com/google-publisher/markets.xml'),
 ]),
]

# FEED HEALTH, live-tested from this container 2026-07-29 ~10:50pm PT (fresh = within 10h):
#   T1  MW-top 10/10 · MW-bulletins 10/9 · SeekAlpha 7/7 (newest 2m) · Reuters 100/41 ·
#       Bloomberg 100/38 · WSJ 100/39 · FT 100/31 · YF:MU 20/11 · YF:NVDA 20/20 · CNBC 30 each
#   T2  ABC-money 25/7 · ABC-intl 25/4 · GN-business 26/17 · GN-world 34/13 ·
#       GN-hormuz 100/47 (newest 12m) · GN-memory 100/10
#   T3  ZeroHedge 25/20 · Fox-biz 25/1 (low yield, kept for coverage)
# The Google-News site: queries for Reuters/Bloomberg/WSJ/FT are the T1 backbone — 31-41 fresh
# items each — because those outlets' own RSS is discontinued or paywalled.

def parse(name, url):
    try:
        raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20).read()
    except Exception as e:
        return None, f'{name}: fetch failed ({type(e).__name__})'
    txt = raw.decode('utf-8', 'replace')
    out = []
    for m in re.finditer(r'<item[ >](.*?)</item>', txt, re.S|re.I):
        blk = m.group(1)
        def grab(tag):
            g = re.search(rf'<{tag}[^>]*>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</{tag}>', blk, re.S|re.I)
            return re.sub(r'<[^>]+>','', g.group(1)).strip() if g else ''
        title = grab('title')
        if not title: continue
        dt = None
        for tag in ('pubDate','updated','published','dc:date'):
            d = grab(tag)
            if d:
                try: dt = parsedate_to_datetime(d)
                except Exception:
                    try: dt = datetime.fromisoformat(d.replace('Z','+00:00'))
                    except Exception: dt = None
                if dt: break
        if dt is None: continue
        if dt.tzinfo is None: dt = dt.replace(tzinfo=timezone.utc)
        out.append((dt, title, grab('description')[:200], grab('link'), grab('source')))
    return out, None

print('='*74)
print(f'  ACUTE SCANNER — last {HOURS}h  |  {NKEY} keywords / {len(THREADS)} threads')
print(f'  run {NOW:%Y-%m-%d %H:%M} UTC   cutoff {CUT:%Y-%m-%d %H:%M} UTC')
print('='*74)

px_block('INDEX / MACRO', INDEX)
front_end_block()
px_block('MAG 7 (independent)', MAG7)
px_block('MEMORY COMPLEX (independent)', MEM)

print('\n'+'='*74); print(f'  KEYWORD HITS ONLY — last {HOURS}h, financial tier first'); print('='*74)

seen, problems, grand, QUEUE = set(), [], 0, []
distinct = 0
for tier_idx, (tier_name, feeds) in enumerate(TIERS):
    hits = []
    for name, url in feeds:
        items, err = parse(name, url)
        if err: problems.append(err); continue
        for dt, title, desc, link, src in items:
            if dt < FCUT: continue       # widest window anything is considered in
            k = re.sub(r'[^a-z0-9]','', title.lower())[:60]
            if k in seen: continue
            th = tags(title+' '+desc)
            if not th: continue          # <-- the gate: direct keyword hit or it does not print
            seen.add(k)
            fl = flags(title+' '+desc)   # <-- the SECOND gate: does it close an open flag?
            if dt >= CUT: hits.append((dt, name, th, title, link, fl))
            # A flagged item enters the QUEUE on the WIDE window even when it is too old to
            # print in the tiers above -- the question is what is open, not what is fresh.
            if fl: QUEUE.append((dt, name, th, title, link, fl,
                                 brand(title, src), tier_idx))
    print(f'\n{"="*74}\n{tier_name}\n{"="*74}')
    if not hits:
        print('  no keyword hits in this tier.')
        continue
    hits.sort(key=lambda x: x[0], reverse=True)
    clustered = cluster_hits(hits)
    dup_tot = sum(len(d) for _, d in clustered)
    if dup_tot:
        print(f'  [{len(hits)} headlines -> {len(clustered)} DISTINCT EVENTS. '
              f'{dup_tot} are syndication of an event already shown below.]')
    for (dt, name, th, title, link, fl), dupes in clustered[:PER_TIER_CAP]:
        age = (NOW-dt).total_seconds()/60
        agestr = f'{age:.0f}m' if age < 90 else f'{age/60:.1f}h'
        star = ' ***OPEN FLAG '+','.join(w['id'] for w in fl) if fl else ''
        print(f'\n[{agestr:>5}] {name:<12} {"|".join(th)}{star}')
        print(f'        {title[:150]}')
        print(f'        -> {" ; ".join(ROUTE.get(t,"?") for t in th)}')
        if link: print(f'        {link[:110]}')
        if dupes:
            srcs = ', '.join(sorted({d[1] for d in dupes}))[:90]
            print(f'        (+{len(dupes)} same-event reprints: {srcs})')
    grand += len(hits); distinct += len(clustered)
    if len(clustered) > PER_TIER_CAP:
        print(f'\n  ...{len(clustered)-PER_TIER_CAP} more DISTINCT events in this tier (capped at {PER_TIER_CAP}).')

print('\n'+'='*74)
print(f'  TOTAL KEYWORD HITS: {grand}   ->   DISTINCT EVENTS: {distinct}'
      f'   ({grand-distinct} syndicated reprints, {(grand-distinct)/max(grand,1)*100:.0f}%)')
print('  ** READ THE DISTINCT COUNT, NOT THE HIT COUNT. Forty outlets reprinting one statement is')
print('     ONE datum. A big hit-count reads as high signal and is usually the opposite. **')
print('  Every hit carries a "->" line naming the vault note it belongs to. Read it into that')
print('  note, or explicitly decide it is noise. An unrouted hit is a skipped relevance check.')
if problems:
    print('  feed problems (missing coverage, not errors in the hits above):')
    for p in problems: print(f'    - {p}')

# ═══════════════════════════════════════════════════════════════════════════════
# PRIORITY FOLLOW-UP QUEUE — the fetch list.
# Grouped by OPEN FLAG, not by feed, because the unit of work is the QUESTION, not
# the headline. Within a flag: paywalled primary wires first (they are gettable and
# they outrank paraphrase), then by tier, then by recency.
# ═══════════════════════════════════════════════════════════════════════════════
print('\n'+'='*74)
print(f'  PRIORITY FOLLOW-UP QUEUE — fetch these, in this order  (flag window {FLAG_HOURS}h)')
print('='*74)
if not QUEUE:
    print('\n  Nothing in this window touches an open flag. That is a RESULT, not a gap:')
    print('  it means the news moved and the registered questions did not.')
else:
    by_flag = {}
    for row in QUEUE:
        for w in row[5]: by_flag.setdefault(w['id'], (w, []))[1].append(row)
    def rank(r):
        return (0 if any(g in (r[6] or '').lower() for g in GETTABLE) else 1, r[7], -r[0].timestamp())
    for fid in sorted(by_flag, key=lambda i: (by_flag[i][0]['pri'], i)):
        w, rows = by_flag[fid]
        rows.sort(key=rank)
        print(f"\n─── {fid}  [pri {w['pri']}]  {w['note']}   (open since {w['since']})")
        for i, ln in enumerate(textwrap.wrap(w['q'], 84)):
            print(('    Q: ' if i == 0 else '       ') + ln)
        print()
        for dt, name, th, title, link, fl, br, ti in rows[:4]:
            age = (NOW-dt).total_seconds()/60
            agestr = f'{age:.0f}m' if age < 90 else f'{age/60:.1f}h'
            get = '[GET]' if any(g in (br or '').lower() for g in GETTABLE) else '     '
            print(f'    {get} [{agestr:>5}] {br or name}')
            print(f'           {title[:120]}')
            if link: print(f'           {link}')
        if len(rows) > 4: print(f'    ...{len(rows)-4} more touching {fid}')
    open_ids = {w['id'] for w in WATCH} - set(by_flag)
    if open_ids:
        print(f"\n  OPEN FLAGS WITH NO CANDIDATE THIS WINDOW: {', '.join(sorted(open_ids))}")
        print('  Still unresolved. Silence is not closure — these stay on the registry.')
print('='*74)
