
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
               # gap #27, 10/14: Jake — "we should have extensive notes on insurers/ABS/PE/Apollo/MetLife".
               # The vault held 241 insurer mentions in 25 notes, Athene 47, Bermuda 60, and Burry Part III
               # (the channel's primary) — but this thread carried NONE of the insurance vocabulary, so the
               # CoreWeave "unlimited insurance tranche" paste surfaced only the 7/3 chain line.
               # ENTITIES — the holders and their sponsors:
               'insurer','insurers','life insurer','annuity','annuities','athene','metlife','prudential',
               'brighthouse','corebridge','lincoln financial','global atlantic','aquarian','delaware life',
               'nippon life','kkr','brookfield','pimco','hps','cliffwater','bxsl','bcred','bizd',
               # CONCEPTS — the channel's mechanism:
               'reinsurance','reinsurer','bermuda','captive','insurance tranche','widows and orphans',
               'bezzle','burry','heretic','asset-backed','data center abs','data-center abs','cmbs',
               'securitization','securitisation','fhlb','federal home loan','guaranty fund',
               # MEASURES — how it is reported:
               'schedule d','statutory statement','naic','risk-based capital','redemption request',
               'tender','gated','pik','payment in kind','imf gfsr','financial stability report',
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
               # gap 2026-09-30: PJM backstop procurement + large-load curtailment were unreachable
               'backstop procurement','reliability backstop','resource adequacy','base residual auction','monitoring analytics','large load','dominion',
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
               # gap 2026-09-30: Iraq exit + aviation war + UAE route-building were unreachable
               'flydubai','fz1073','inherent resolve','erbil','ain dar','north ghawar','mokhber',"l'imad",'zero hormuz',
               'war risk','crack spread','refiner','lng',
               'iran','oman','majlis','fars','aramco','opec','brent','wti','kharg',
               'corridor','flag state','insurance premium',
               'venezuela','pdvsa','chevron','merey','heavy sour','heavy crude','guyana',
               'gulf coast','official selling price','crude import','import license',
               # gap 2026-10-09 (Jake's squawk '*US GULF SHUTS IN 1.3 BCF/D OR 59% GAS PRODUCTION: MMA'):
               # NO THREAD MATCHED although oil-value-chain held three days of Isaias shut-in entries
               # (10/7 25.08%, 10/8 62.89%). The map had the war-side supply words and none of the
               # WEATHER/OFFSHORE vocabulary or the gas measures. MMA = Marine Minerals Administration
               # (BOEM+BSEE reunified 2026-07-10), the agency that publishes the shut-in table.
               'shut in','shut-in','shuts in','marine minerals','mma','bsee','hurricane','tropical storm',
               'offshore production','platforms evacuated','gulf of america','gulf of mexico',
               'bcf/d','bcfd','mmcf','henry hub','natural gas futures','storage build','feedgas',
               # gap #20 (2026-08-23): THE ADVERSARY'S DOMESTIC ECONOMY. A paste on Iran importing
               # FROZEN MEAT to cap meat prices routed WAR/OIL(1)* -- a single weak keyword -- and
               # the sweep flagged a vocabulary gap. The board has tracked 131 days of blockade from
               # the OUTSIDE (tankers, terminals, transits, strikes) and holds NOTHING on whether
               # Iran can ENDURE it: no rial, no inflation, no food prices, no subsidy, no snapback.
               # Endurance is the variable that sets the blockade's duration, and it was unmapped.
               'ghalibaf','qalibaf','pezeshkian','khamenei','rial','toman','tehran bourse',
               'subsidy','subsidies','food price','frozen meat','bread price','staple',
               'currency peg','devaluation','capital flight','domestic inflation',
               'snapback','trigger mechanism','boomerang','unsc resolution','2231'],
 'BLACK SEA': ['cpc','caspian pipeline','novorossiysk','tengiz','kashagan','karachaganak',
               'kazakh','kazakhstan','black sea','primorsk','ust-luga','druzhba','ceyhan'],
 'INVENTORY': ['spr','cushing','strategic petroleum','crude draw','crude build','tank bottoms',
               'eia','api inventory','days of supply','padd 2','midwest gasoline','gasoline stocks'],
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
               # gap 2026-09-30: nowcasts + data-vintage vocabulary
               'gdpnow','nowcast','annual revision','annual update','saving rate','savings rate','personal saving',
               'bls','bea','import price','ism prices','prices paid','unit labor cost',
               # gap #21 (2026-08-23): PRICE ADMINISTRATION AS A POLICY INSTRUMENT. Jake listed six
               # live US interventions that set or coerce a price -- beef import waiver, directed
               # drug pricing, pressure on Walmart, securities purchases to lower mortgage rates,
               # housing participation limits, a $2.50 gasoline target with a DOJ pass-through
               # probe -- and the vault held NONE of them. It tracks the Fed and tariffs as policy
               # levers and has no concept of administered prices. Worse: it knows "price cap" ONLY
               # as a sanctions tool against Russian crude. Same instrument, one direction only.
               'price cap','price ceiling','price control','administered price','windfall tax',
               'price gouging','most favored nation','drug pricing','pass-through','doj probe',
               'antitrust','jawbone','moral suasion','export restriction','margin cap',
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
               'llama','mistral','nemotron','gpt-5','gpt5','gemini','claude','grok','astra','argon','fairwind','gpt-6',
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
               # gap 2026-09-29: FICO/VantageScore + CarMax hit NO thread (open scan 9/29)
               'carmax','kmx','fico','fair isaac','vantagescore','fhfa','rocket mortgage','credit score',
               'used-car','used car','auto loan',
               # MEASURES
               'nonstore','ex-autos','ex autos','ex-auto','food services','restaurants and bars',
               'general merchandise','business inventories','inventory/sales','inventories-to-sales',
               'retail-only','one-year inflation expectations','five-year inflation expectations',
               'inflation expectations','sentiment index','expectations index','current conditions'],
 'FX/CARRY':  ['yen','jpy','usd/jpy','usdjpy','boj','bank of japan','carry trade','repatriation',
               'currency intervention','fx intervention','fx reserves','ministry of finance',
               'dxy','dollar index','ueda','mof','kanda','jgb','japan sold','tic shows',
               # gap 2026-10-09: the dollar's direction words (Saravelos: "dollar negative")
               'dollar negative','dollar-negative','dollar positive','sell america','fx hedge','hedge ratio',
               'eurusd','eur/usd','saravelos'],
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
               'ai act','model access','safety institute','nist ai','red team',
               # gap 2026-09-30: the Accord + FTC probe + China's CUDA substitute
               'ftc','civil investigative','ferguson','super intelligence','external auditor','tilelang','ascend'],
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
              'vendor financing','circular','dilution','equity offering','shelf','atm offering',
              # gap 2026-10-09 (Saravelos/DB: "biggest systemic risk... something going wrong in the AI
              # ecosystem: a safety event, a failed IPO, or disappointing revenues... concentration risk
              # is immense... dollar negative, very bond positive"): NO THREAD MATCHED although the vault
              # filed a failed IPO (Firmus) and a revenue miss (OpenAI ~$50B) the day before. The map had
              # the deal-plumbing words and none of the RISK-NARRATIVE vocabulary sell-side strategists use.
              'systemic risk','concentration risk','event risk','tail risk','failed ipo','ipo window',
              'safety event','under-priced','underpriced','disappointing revenue','ai ecosystem',
              'saravelos','deutsche bank'],

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
 # gap (2026-10-08): SpaceX's 800 MHz buy + Jake's AI-device thesis routed to CAPEX/MODEL-ECON only —
 # the vault had NO telecom thread, and missed Starlink Mobile's carrier plan from SpaceX's 8/4 Q2 call to 10/8.
 # CONCEPTS: spectrum / direct-to-device / carrier competition / the endpoint device.
 # ENTITIES: carriers, tower REITs, satellite-to-phone players, spectrum sellers, executives.
 # MEASURES: MHz, subscriber/ARPU vocabulary. (Short tickers T/VZ/AMT/CCI left out: false positives.)
 'TELECOM':['spectrum','mhz','low-band','low band','mid-band','direct to cell','direct-to-cell',
            'direct-to-device','satellite-to-phone','femtocell','small cell','wireless carrier',
            'mobile carrier','fourth carrier','starlink mobile','t-satellite','handset','smartphone',
            'agentic os','ai phone','thin client','thin-client','ai device',
            'at&t','verizon','t-mobile','tmus','asts','ast spacemobile','spacemobile','echostar',
            'grain management','american tower','crown castle','sba communications','sbac',
            'tower reit','tower compan','shotwell','stankey','spcx',
            'postpaid','phone net adds','arpu','subscriber'],
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
 'TELECOM':   'ai-capex-cycle (SpaceX/Starlink Mobile 10/8: spectrum, carriers, towers) / compression-thesis (the endpoint/agent-OS device thesis, 9/23 + 10/8) / money-board',
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
# ── 2026-10-16/17 VAULT-WIDE READ (Jake: 'Read the vault in its entirety… create keywords for your librarian') ──
# Thirty Sonnet readers digested every note + chat-log; every term below was verified to occur in wiki/ text
# (≥1 note, ≤35% of notes). THREADS_ADD extends existing threads; THREADS_NEW opens threads the map could not
# reach (this week's misses: East-West/Petroline/Yanbu/Khurais, Goldman Prime gross/net, basis trade,
# Starshield, refiner tickers, Brent levels, Anthropic IPO, momentum basket). Merged below with plain loops
# (the router execs this block with separate globals/locals — no comprehensions).
THREADS_ADD = {
 'AI-POLICY': [
               'lutnick','amodei','sacks','musk','commerce','pentagon','altman','export controls',
               'supply-chain-risk designation','pacing the frontier','bipartisan','open weights',
               'zuckerberg','hugging face','eo 14420','jensen huang',"tom's hardware",
               'carolina principles','elon musk','procurement ban','containment escape',
               'national-security probe','open-weight letter','open-weights letter',
               'ai diffusion rule replacement','anca dragan','david sacks','dawn song',
               'jakub pachocki','jared kaplan','jasjeet sekhon','john schulman','mark chen',
               'mark warner','micah carroll','pacingthefrontier.com','shantanu jain',
               'shengjia zhao','department of defense','mandatory capabilities testing',
               'matthew rahtz','pre-release government access','satya nadella','taiwan','dell',
               'senate','congress','danger-disclosure','danger-disclosure-playbook','hill','pacing',
               'kill switch','smci','deregulation','truth social','fable','quartz','a16z','github',
               'hegseth','karp','telemetry','bytedance','chapel hill','mythos','pace the frontier',
               'trump admin','accord','aug 1','autonomous weapons','brockman','cisco','culpability',
               'd.c. circuit','doordash','equity stake','fable 5','hassabis','judge lin','mofcom',
               'mythos 5','pachocki','palantir','ai-evaluation-framework','american ai leadership',
               'carr','cembalest','cisa','eo 14409','federal procurement ban','forbes','ieepa',
               'lawmakers','maria curi','palo alto','servicenow','venturebeat','ai czar',
               'ai diffusion rule','asserted-complete vs published','barr','certification branch',
               'chip controls','claude fable 5','cohere','cybergym','dario amodei',
               'department of war','emil michael','eo 14330','most under-priced','nist',
               'pacing letter','pichai','regulatory capture','regulatory moat',
               'remote-access loophole','remote-access rule','safety validation','sam altman',
               'skynet day','ustr','whoever wins ai wins','advisory council','ai safety institute',
               'alliance letter','arc turned','aug-1 framework','beat china',
               'capability-keyed certification','certification moat','china signed',
               'chinese-ai ban','chips act','clayton','clean air act','coalition of interest',
               'covered frontier model','crowdstrike','designation regime',
               'developer-elected constraint','european commission','federal judge',
               'federal preemption','first amendment retaliation','framework behind closed doors',
               'grave mistake','greer','insider-risk','irregular','judge rita lin',
               'kill switch act','kratsios','liability withholding','linux foundation',
               'looking at controls','mark zuckerberg','mass domestic surveillance','meeks',
               'model distillation','moolenaar','mozilla','murphy','ratepayer pledge','musk 15gw',
               'refusal discharges','he needs enterprise approval','culpability discharge',
               'unless open price rises',
 ],
 'ALLIANCE': [
               'qatar','saudi arabia','bahrain','mediators','macron','von der leyen',
               'g20 asheville','north atlantic council','congress','france','canada','kyiv',
               'kuwait','germany','centcom','hegseth','moscow','netanyahu','announced vs fid',
               'none new','poland','cbs news','gulf-arab coalition','italy','japan-linked vessels',
               'raf fairford','romania',"4 house r's",'60-day clock','breaking defense',
               'coalition ledger','compartmentalization','estonia','fidan','iceland','portugal',
               'saudi fighter aircraft','us treaty ally','al-ansari','al-thawadi','andy burnham',
               'atlantic council','eucom','european union','mecca joint defence agreement',
               'mohammed bin salman','moldova','nz aluminum extruders','pacom','picton',
               'raf voyager','saceur','shehbaz sharif','siluanov','southcom',
 ],
 'BIOTECH': [
               'jnj','unh','google deepmind','cvs','alhc','alphafold',
 ],
 'CAPEX': [
               'vertiv','iren','google cloud','azure','capex/ocf','census c30','capex discipline',
               'capex-gap razor','ai capex','dell','intc','razor','semianalysis','apple','lambda',
               'fluidstack','eaton','sacks','second derivative','capex/revenue','negative fcf',
               'capex intensity','meta compute','compute oversupply','gnrc','optionality razor',
               'reversibility','sieyuan','third-party capacity','bofa exhibit 6','caterpillar',
               'fcf burn','deferred depreciation','golden window','hyperscalers','mrvl','neoclouds',
               'soxx','aapl','detachment-bid','shipments','etn','pwr','take-or-pay','arm','amat',
               'hyperscaler capex','machinery','musk','tsla','ibm','lrcx','round trip','qcom',
               'powder','vrt','lly','capex guide','carrier','lutnick','wobble','hyperion',
               'lead times','louisiana','trendforce','uncommenced leases','xom','colossus','smci',
               'tesla','vercel','cvx','escape hatch','mag7','off-balance-sheet','amplitude',
               'crowd-out','open models','schneider','apld','beige book','bloom energy',
               'dallas fed','data-centre construction','fomc minutes','purchase commitments',
               'sold out through','token economics','2027 capex','bernstein','crossover',
               'electricians','gw contracted','hoarding','mediatek','poolside','ccj','seagate',
               'beat-sold','build-out','cloud growth','contracted revenue','cost curve',
               'crowd-out loop','gaap eps','it load','jensen huang','krishna','marvell',
               'morningstar','scarcity rent','air gap','capex guidance','capex solvency','fwd fcf',
               'ism manufacturing','non-cancellable','overbuild','tokens/mw','hood','nflx',
               'arms race','beat-sold razor','capacity additions','cembalest','corz',
               'expected to get worse','fink','gw under construction','hubb','mw delivered',
               'negative free cash flow','project jupiter','quanta',
               'remaining performance obligations','saar','self-build','servicenow',
               'switchgear sold out','three-leg squeeze','transportation equipment',
               'adjusted ebitda','atlanta fed','bloomberg consensus','capital intensity',
               'colossus ii','compute glut','construction spending','core scientific',
               'demand exceeds supply','depreciation schedules','digital drive','double-ordering',
               'epoch ai','forcing function','housing starts','hut 8','lip-bu tan',
               'china has extraordinary timing','market ear','cepi','ocf/c','da/c','slinky',
               'price-insensitive borrowers','buy corporates','tug-of-war','1.4 gw',
               'model economics','fourth denomination','orchestrator',
               "isn't it literally contracted",'debt-financed ai spending','you just glossed it',
               'layer 4','little or no value','ai node','spv parade','capital web','who owes whom',
 ],
 'CHAIN': [
               'transmission chain','transmission-chain','propagated or died','fast channel',
               'hyperscaler-credit','stage 3','stage 1','stage 5','supplier orders','williams',
               'co-signed raise test','dallas fed','fomc minutes','hyperscaler cds',
               'reaction function','rule 18d','9 hike dots','cost-shifting family','doom loop',
               'revenue per gpu-hour','counterparty map','hyperscaler spreads','nvda 5y cds',
               'ai supplier orders','ig-ai cohort','n/n lit','transmission stage','volta book',
 ],
 'CONSUMER': [
               'apple','pump price','retail diesel','beige book','hollow bottom','pump prices',
               'gas prices','rost','burl','eia retail','k-shaped','precedent bid','gasbuddy',
               'net charge-offs','washington','soxx','aapl','diesel','detachment-bid','jpm',
               'freight','texas','dell','90 days','745 put','capitulation','dip-buying',
               'compression thesis','dino','gasoline','gs prime','mining','new york','len','glp-1',
               'louisiana','52-week high','chicago','census','citi','rail','reflex','core goods',
               'dallas fed','delinquency','unverifiable','goods inflation','ism services',
               'price hikes','record diesel','buy the dip','delaware','margin squeeze','marvell',
               'samsung electronics','shelter','vance','wday','atlanta','biggo','cisco','cleveland',
               'consumer credit','detachment bid','fertilizer','florida','k-shape','labor day',
               'mcelligott','memory pass-through','mississippi','procyclical','risk appetite',
               'second wave','unh','wfc','diesel/gasoline ratio','dip screen','ew s&p',
               'expectations wedge','foreclosures','jones act','lennar','lulu','national average',
               'nintendo','pre-buying','richmond','st. louis','usda','west virginia','netflix',
               'xrt','alaska','food inflation','glp1','hassett','hedonics','income quintile',
               'kentucky','korea joongang daily','macbook','memory costs surge sixfold','miami',
               'new jersey','population mismatch','re-wardrobing','transaction volume',
               'umich inflation expectations','xbox','90-day grace','cacc','cvs','sofi','alabama',
               'bloomingbit','cash price','churn ledger','climate commitment act','cockroach',
               'conference board 81.9','conoco','constituent vol','core goods inflation',
               'credit bridge','cvna','diesel price','diversified exposure','dollar stores',
               'eurozone','foundayo','fourth loss channel','fox news','freight cost',
               'gasoline deflation','gsci/spx','ipad','iqvia','lenovo','lillydirect',
               'maha-aligned activists','manufactured familiarity','marshalls','mortgage rates',
               'nahb','necessities basket','newsweek','nothing to fear','nothing to lose','novo',
               'off-price','orforglipron','price census','rattner','rotation engine','santander',
               'self-pay','seller exhaustion','shrinkflation','sloos','ttan','it schedules it',
 ],
 'CONTENT-TOLL': [
               'chatgpt ads','fencing the commons','sap pay usdc','shopify checkout','trafficguard',
 ],
 'EUROGAS': [
               'qatarenergy','cheniere','gaslog shanghai','europe','qatar','ras laffan','adnoc',
               'force majeure','williams','europe-energy-crunch','helium','germany','newsquawk',
               'graham act','qatari lng','loviisa','venture global','egypt','freeport',
               'seaborne lng','24-hour blackouts','lng carriers','damietta','drone strike',
               'irina slav','lng exports','romania','112 bcm','33 us cargoes','energy transfer',
               'cove point','dhhngsp','gas-set power','golden pass','lng carrier struck',
               'neptun deep','no alternative route','rolling blackouts','spot lng','uae lng',
               'petrobras','qatar lng','waha','al rekayyat','ambrey','energos winter',
               'gaslog salem','lng enugu','maran gas mystras','marshall islands','stonex',
               'us-managed',
 ],
 'FED': [
               'fed trap','williams','reaction function','fiscal dominance','september hike','iorb',
               'hassett','hike before december','fomc minutes','fed voter','one-and-done',
               'fomc week','jackson hole','look-through','musalem','sintra','fed put','hawk bloc',
               'hike probability','schmid','ai-related price pressures','cme fedwatch',
               'fed independence','federal reserve','on rrp','walcl','ample reserves',
               'cleveland fed','forward guidance deleted','desk','tariff','coin flip',
               'implementation','ny fed','participants','polymarket','blackout','kill switch',
               'beige book','araghchi','consumer price','core goods','dallas fed','maintain',
               'passenger','fully priced','july minutes','10y 4.64','25bp','hike case','hot cpi',
               'look through','policy path','tchir','collins','funds rate','ppi diesel',
               'reinvestment','sept 16','soma','supervision','9 hike dots','capture test',
               'cpi morning','federalreserve.gov','hike dots','import prices',
               'lender of last resort','presser','september hike odds','eci','q2 gdp advance',
               'barr','debasement bid','dgs2','family fight','fdic','fed hike odds','gdp advance',
               'greenspan','kevin warsh','not a pause','policy error','run hot','second hike',
               'several participants','taper','unanchoring','work to do',"can't cut",'cnbc 6/30',
               'core goods inflation','cpi consensus','credibility hike','dxy 101.06','fed hold',
               'fed oig','fisher','fomc july','good family fight','hawkish branch','hike odds low',
               'kalshi','m2 yoy','newyorkfed.org','no fed put','no need for urgency','not-qe',
               'october hold','only oil argues hawkish','overtightening','pce 3.7',
               'prediction markets','reuters poll','second hike branch','sofr futures',
               'soma holdings','stein','three hike dissents','trump truth social','volcker',
               'andreessen','bank of canada','barkin','blanche','bloomberg wirp',
               'board of governors','boskin commission','charles jones','chetty','dynan',
               'eccles building','fed desk','fed swaps','genius act','he lifeng','mankiw',
               'mcmillon','minneapolis fed','miskin','neel kashkari','ny fed desk','panic of 1907',
               'pappalardo','paulson','rajan','regional reserve banks','sargent','senate testimony',
               'sept 15-16','timiraos','william white','stale-but-ok jobs','no comment on jobs',
               'rate hike odds','debasement next',
 ],
 'FINANCING': [
               'iren','blackrock','softbank','firmus','junkbondinvestor','residual value guarantee',
               'take-or-pay','gs prime','lambda','sb energy','pitchbook','blackrock jv',
               'takeout cliff','claim queue','meta/blackrock jv','price-insensitive bid',
               'means of financing','neoclouds','backstop','detachment-bid','artifact test','intc',
               'circularity','pipe','watchlist','fidelity','circle','concessions','gating',
               'ig issuance','uncommenced leases','williams','capex/ocf','debt issuance',
               'off-balance-sheet','volta','wulf','crowd-out','vice','125bp wide of guidance',
               'apld','bloom energy','fluidstack','dallas fed','dowd','terawulf','ai issuance',
               'customer concentration','industrial policy','payment terms','airtrunk',
               'dated ledger','baa2','cifr','crowd-out loop','duration mismatch','holtec',
               'ig spreads','ports-pike','psky','residual-value guarantees','stateline',
               'alphaville','anthropic ipo','cdx ig','collar','hlne','mcelligott','meta compute',
               'named casualty','vendor-financed','x402','archegos','corz','anchor customer',
               'applied digital','capital raise','crowding out','dc abs','equity raise',
               'financing tape','fink','funding squeeze','funding window','g-spread',
               'hyperscaler bond issuance','jane street','remaining performance obligations',
               'spacex ipo','spacexai','situational awareness lp','citadel securities',
               'contract duration','core scientific','counterparty credit','cover ratio',
               'credit derivatives','digital drive','evergreen','financing demand',
               'financing pulled back','ft alphaville','funding chain','funding gap',
               'goldman ig desk','gs ficc','gundlach','hurdle rate','hut 8',
               'hyperscaler debt binge','kevin warsh','monoline','offtake quality','openai ipo',
               'openai ohio','papai','pentagon loan','refinancing wall','sofr+300','solaris',
               'vanguard','archegos 2.0','credit suisse','dbs','nomura','ai-debt pipe',
               'airtrunk reit','aixtron','banks hitting sector limits','chris wood','cockroaches',
               'compute as collateral','contract counterparty','convertible issuance',
               'customer-supplied hardware','dealer writedown','distribution to retail',
               'fixed claims','galaxy digital','google backstop','gpu spv','gpu-backed abs',
               'gpu-backed spv term loan','gulf bond boom','healthy reset','hy project bonds',
               'hyperscaler cds basket','ig window','interest expense compounding','ipo deferred',
               'jpmam','lease obligations','lockbox','mag7 workbook','marginal borrower',
               'negative carry','neocloud facility','neocloud financing','neocloud loans','crwv',
               'nbis','ccc spread','bbb spread','hy spread','dso','roic','reit','dlr',
               'digital realty','dbrg','digitalbridge','eqix','equinix','vie','bhf','akamai','gfc',
               'smccf','tmt','doj','tlb','term loan b','mufg','ifr','hpc','arr','wbd','pldt','pgim',
               'green chile','new mexico','srt','significant risk transfer','smbc','sifma','nbfi',
               'mou','icc','ice clear credit','dscr','aep','sftby','cusip','cdx','cdx hy','big sky',
               'bnp','asx','round-trip','gpu-backed','gpu collateral','delayed draw','ddtl',
               'payment-in-kind','db research','leopold','spvs','off-b/s','treadmill test',
               'four roles','sbe','coverage audit','development partner','swks','qrvo','hung loan',
               'fulcrum','asset on sale','re-concentration',"let's send the gopher",
               'co-signed raise','rvgs','rvg chain','cds going points up',
               'financing backed by chips','equity exit',
 ],
 'FLOWS': [
               'gs prime','soxx','two clocks','archegos','short covering','de-grossed but unhedged',
               'factor unwind','breadth','iren','nasdaq','s&p 500','fidelity','bloom','commodities',
               'ny fed','price-insensitive','polymarket','roberts','washout','deleveraging','rvol',
               'bloom energy','dallas fed','open interest','hedge funds','nasdaq-100',
               'precedent-bid','de-grossing','forced seller','gross exposure','prediction market',
               'fms','consensus-bear','dispersion regime','distribution chain','equity supply',
               'fundamental clock','leveraged etfs','passive bid','positioning clock',
               'reinvestment','sidelines','soma','applied digital','asset managers','basis trade',
               'cftc cot','cramer','dispersion trade','jane street','nbim','net long','pain trade',
               'pitchbook','poland','re-gross','short squeeze','swap spreads','trend-following',
               '424b4','situational awareness lp','automatic bid','calibration note',
               'citadel securities','cleanspark','core scientific','cta trigger','degrossing',
               'dv01','fast money','forced liquidation','foreign buyers','fund flows','gs ficc',
               'gs prime book','leveraged funds','liability-driven','macro products',
               'mechanical flows','median stock','meta 0.60x','momentum basket',
               'money keeps moving','net leverage','nvda 13f','paul tudor jones','put buying',
               'retroactive','skhy adr','supply calendar','v-bounce','vanguard','credit suisse',
               'etf flows','gsprhimo','goldman cta','nomura','bilateral block sale','bofa fms',
               'clear street','consensus bear','de-dollarization','depth of the bid',
               'distribution texture','el-erian','evergreen redemptions','everpure','forced buying',
               'foreign bid fading','goldman desk','goldman prime','googl 0.69x','gpif','gross mv',
               'gs prime brokerage','illumina','indirect fade','issuance flood','jpm am',
               'lance roberts','leopold','momentum factor','momentum unwind','natixis',
               'newyorkfed.org','poor liquidity','positioning flush','record soxx inflows',
               'second rank','sell-triggers','seller exhaustion','slickcharts','synthetic duration',
               'unspent bid','vol-control','vol-scaled','weakening traditional buyer base',
               'bca research','balchunas','gs derivatives desk','goldman sachs prime','hwang',
               'prime insights & analytics','vinnie lin','dram-themed etf','eisman','elebank',
               'form pf','goldman cta model','goldman momo basket','goldman prime book',
               'goldman sachs prime book','gs delta-one','irs notice 2026-62','ken griffin',
               'msci korea','norges bank investment management','realinvestmentadvice',
 ],
 'FRAGILITY': [
               'warning vs trigger','roberts','debasement','kill switch','flip test',
               'fragility ladder','gate 1','top forming','iren','transmission-chain',
               'detachment-bid','stage 2','watchlist','bull-bear-ledger','absorber','odds-shader',
               'regime change','forest.md','two clocks','transmission chain','spy put','air pocket',
               'ccc oas','spy 745 put','fragility.py','ice bofa','mcelligott',
               'confirmation sequence','correlation snap','duration thesis',"he'll inflate anyhow",
               'ice clear credit','multiple compression','two-speed market','druckenmiller',
               'archegos','coiled setup','false positive','move 113.65','bailey',
               'citadel securities','dimon','anchors and balloons','bbb oas','calm-stage flip',
               'central contradiction','containment case','four calm stages','lagging half',
               'melt-up cracked','move 106.6','stage 1.5','200-dma',
               'bofa global investment strategy','rsi-14','spy/rsp ratio','aa 61','beat and sold',
               'cheap hedge','citigroup','dealer writedown','denominator trap','divergence trigger',
               'event-risk reduction','f8 dealer leg','funding-migration ladder','healthy reset',
               'ig pinned','lamont','n/n lit','narrow-market state','pace tell',
               'positioning is a state','state not a trigger','trs funding','bca research','ms now',
               'wilshire 5000','first brands','golub','point bonita','western alliance',
               'goldman prime','gs prime','gross leverage','net leverage','gross exposure',
               'net exposure','hedge fund leverage','basis trade','cash-futures basis',
               'relative value','dallas fed','deleveraging','mean reversion','sign-flip test',
               'gw-destruction ledger','agentic peak',
 ],
 'FX/CARRY': [
               'carry unwind','boj hike','yen carry','yen intervention','katayama','japan',
               'correlation snap','nbim','takaichi','hedged pickup','usdkrw','usd/twd','bonbast',
               'gold','intervention','fed trap','escalation ladder','tether','open interest',
               'us treasury','anadolu','haven bid','hawkish fed','short covering','squeeze setup',
               '40-year low','citadel securities','dec spy puts','hurdle rate','pboc',
               'state street','yen defence','aug-2024 replay','avalanche','bank channel',
               'bessent-boj','carry corners the fed','de-dollarisation','disorderly unwind',
               'dollar bid','fima','gpif','gs gir','hedge cost','japan selling treasuries',
               'japanese accelerant','joint action','positioning reset','soros','stronger yen',
               'surprise hike','thorne','weak yen','yen through 160','japan pm','usd/krw',
               'ankur banerjee','camp david notepad','chinese banks','exchange stabilization fund',
               'frankfurter','japan mof','jason douglas','koeda','masahiko loo','piepenburg',
               'setser','takata','tyler durden','vongreyerz','wellington altus','silver week',
               'sharpest catch',
 ],
 'HYPCREDIT': [
               'blackrock','iren','softbank','lambda','avgo cds','record wides','single-name cds',
               'counterparty credit quality','cds bp','neoclouds','apple','stage 2','force majeure',
               'hyperion','volta','crowd-out','fomc minutes','hyperscaler cds','ccc oas',
               'counterparty risk','customer concentration','hyperscaler issuance','jumbo',
               'new-issue concessions','127bp','226bp','abilene','cds record','ice bofa',
               'indigestion','40yr','52-week low','avgo 127','cds panel','cdx ig',
               'confirmation sequence','goog','ice clear credit','issuers asked to wait',
               'quality ladder','record cds','weak links','197bp','g-spread','carr','ccc index',
               'cembalest','chip financing','coreweave cds','ficc','re-widening','vantage',
               '2.5-year maturity','googl 75.6','hy 315','ai-related bond issuance','bbb oas',
               'cash bond','cds 198','citadel securities','funding ladder','hedge lock',
               'hyperscaler spreads','ig dam','monoline','orcl 226','15y+ ig yield','25bp vs 6bp',
               '300bp on identical collateral','30y spread','5-year cds','amzn 76.5','bbb 104',
               'cds record wides','meta 106.1','msft 53.5','nvda cds 77.6','ai bonds',
               'ai debt spree','ai-capex financing benchmark','ai-credit basis','cds dispersion',
               'credit nexus','crwv 701','el-erian','fifth-largest issuer','floating rungs',
               'floors are credit risk','galaxy digital','gpu ladder','ig effective yield',
               'investor demand cools','jpmam','jupiter 89-91','n/n lit','ten-year equivalents',
               'two waves','weary rotation','weighted-average maturity by leg','widen-trigger',
               'widest on record','amd 103.1','avgo 143.9','nvda 92.1','orcl 299.2','amanda cooper',
               'beignet investor llc','bofa global research','goldman credit desk',
               'goldman delta-1','mackenzie bc','nohshad shah','oracle cds','orcl cds 228',
               'remember hyperscaler cds spreads','s&p global-markit','softbank paper',
               'sopaipilla investor llc','spacex bonds','spacex cds','borrower tiers',
 ],
 'INF-ASIC': [
               'google tpu','marvell','mrvl','semianalysis','mediatek','b300','mtia',
               'vera rubin nvl72','ironwood','sglang','vllm','nvidia tax','apple','xpv',
               'ai revenue','alab','gb300','rubin ultra','bernstein','customer concentration',
               'share loss','blackwell ultra','nvl72','replacement cycle','tokens/mw',
               'vertical integration','grace blackwell','hock tan','1m tpus','customer financing',
               'inferencex','kimi k3','next web','td cowen','3.5gw','maia 300','agentx',
               'ai semi revenue','decart','humain','jevons at the socket','nvlink fusion','red hat',
               'sandbagging','scale-out','six xpu customers','superpod','tok/s/mw','tok/s/user',
               'tokens per mw','tpu spv','tpuv7','trainium2','1.6t optics','graviton',
               'ascend 950dt','atlas 950 superpod','atlas 960 superpod','aws trainium',
               'china mobile ucm','deepep-ascend','deepgemm-ascend','enfabrica','evercore',
               'glm 5.3','inferact','jalapeno','lee jae myung','maia 200','nvidia gb300',
               'nvidia rubin','radixark','rubin cpx','scott guthrie',
               'terawulf/cipher/hut 8 site spvs','tomahawk 6','torchax','torchtpu','tpu v7',
               'tpu v8i','tpuv8i','tsmc n3p','vr200',
 ],
 'INVENTORY': [
               'wdistus1','strategic petroleum reserve','absorber','distillate stocks',
               'days of cover','five-year range','refill bid','ir.eia.gov',
               'product exports 8.07 mb/d','wcsstus1','depletion clock',
               'weekly petroleum status report','buffer','singapore','europe-energy-crunch',
               'dallas fed','shock absorber','4-week average','kb/d','oecd','spr exchange',
               'five-year average','opec+','table 1','40-year low','722k bpd','commercial crude',
               'countdown','distillate exports','distillate inventories','floating storage',
               'lowest since 1982','refinery distillate yield','spr clock','spr draw',
               'stock vs flow','tank-bottoms','year-over-year same-week','17 weeks','284.6m',
               '298.7m','eia wpsr','already paid for','build rate','crude inventories',
               'distillate production','dnav','fuse length','hfi research','highlights pdf',
               'largest since jan-2023','mbbl','nasser','operationally zero','padd 3',
               'product supplied','refinery utilisation','refinery utilization','seasonal draw',
               'spr 3.05mm','spr 3.05mm barrels','stock draw','strategic reserve',
               'thousand barrels','wdiexus2','akazawa','amrita sen','amsterdam-rotterdam-antwerp',
               'big hill','bryan mound','joliet','kharg waiting area','padd 1',
               'petroleum status report','petroleum supply monthly','table 9','wdiupus2',
 ],
 'KOREA': [
               'margin cascade','ewy','lutnick','seoul','plunge protectors','usdkrw',
               'short-selling ban','taiwan','dell','intc','softbank','escalation ladder',
               'tradingview','skhy','samsung electronics','ewy 6','leveraged etfs',
               'national assembly','none new','bok','skhy adr','basel','bolsonaro','chosunbiz',
               'forced liquidation','hyundai','korea joongang daily','samsung c&t',
               'seoul economic daily','hang seng','nps','tokyo electron','blue house',
               'concrete preparations','contained by construction','eight reactors','encinal',
               'kwak','leverage flush','national assembly consent','no named casualty',
               'p-8 poseidon','retail puking','semi tariff rule text','seohak ants','sidecar',
               'sidecars','stabilization fund','advantest','hangul day','lasertec',
               'samsung electro-mechanics','alaska lng','dpm lee hyoung-il','grid x technology',
               'gs caltex','gwangju','honam','ked global','kim yong-beom','koo yun-cheol',
               'korea times','korean oil tanker','lee jae myung','lee jae-myung','ls electric',
               'marandi','pohang','s-oil','studsvik','yongin',
 ],
 'LABOR': [
               'displacement','challenger','electricians','fink','table b-1','adp +38k',
               'claude corps','frozen labor','payroll revisions','ny fed','churn','wages','census',
               'zuckerberg','beige book','attrition','hollow bottom','tokenmaxxing','goodhart',
               'qcew','quits','uber','bifurcating','forbes','indexbox','jobless claims',
               'broadly stable','h-1b','local-government education','openings','stock vs flow',
               'unemployment rate','world cup','calendar reversal','composition effect',
               'cyclical core','discouraged workers','empsit','ets survey',
               'ism services employment 47.8','jolts 7.10m','kiyosaki','labor hoarding',
               'layoffmaxxing','machinists','nfib','ny fed liberty street','pipefitters',
               'seat count','skilled workers','specialty trade','ssdi','stall speed',
               'three-month average','transfer rolls','vacancies','weak jobs',
               'bls employment situation','covid winter wave','fred payems','harvey/irma',
               'pfnyc/lightcast','aarp','atlanta fed wage tracker','bayway','bloomberg econgecc',
               'bls commissioner fired','july employment situation','kevin gordon','khosrowshahi',
               'lightcast','schwab','stanford 2025 ai index','stephen juneau',
               'stock-fueled retirement party','teamsters local 877','upwork',
 ],
 'LEVANT': [
               'houthis','jordan','netanyahu','syria','aqaba','red sea','united states','kuwait',
               'centcom','yemen','red line','riyadh airport','second front','bab al-mandab',
               'rabigh','aramco hq','completing the mission','jazan refinery','muwaffaq salti',
               'muwaffaq salti air base','rezaei','73 wounded',"sana'a",'tanajib','ali al-taher',
               'azraq','baniyas','barak ravid','dammam','dhubab','jeddah','al azraq','al-otaibah',
               'al-tanf garrison','ali taher tunnels','amman','camp titin','damascus','daraa',
               'deir ali','gaza','hamas','idf general staff forum','prince hassan','rosh hashanah',
               'rukban','south lebanon','southern jordan','state department','tishreen plant',
 ],
 'MATERIALS': [
               'critical minerals','almonty','machinery','cohr','copper','helium','ras laffan',
               'schneider','usar','magnets','rare earths','uuuu','qatarenergy','aloy','exxonmobil',
               'mofcom','vertiv','freeport','howden','transportation equipment','aluminum',
               'atlanta fed','department of war','rare-earth refining','reinhausen','sieyuan','abf',
               'copx','centinela strike','teck','administered price floor','anfgf','antofagasta',
               'centinela','crml','electrician shortage','ex-china ndpr','first quantum','fqvlf',
               'germanium','helium juniors','ionic clay','ism respondents','kronos',
               'lead-time extensions','mtrn','prices paid 71.1','rare earth war','ring of fire',
               'samr','scco','state-equity taxonomy','stillwater','stockpiling','tungsten',
               'tungsten scrap export ban','usa rare earth','comex hg','project vault',
               'air liquide','anglo american','bradesco','capesize','chemical products',
               'cleveland fed','cobre panama','doe grant','fabricated metal products',
               'greenland mines','kazr','lundin','mesabi metallics','mulino','oklo aurora',
               'paper products','peabody','simandou','us army',
 ],
 'MEMORY': [
               'digikey','trendforce','apple','dell','advantech','intc','second leg',
               'memory shortage','hbm shortage','hbm sold out','wccftech','nintendo','kv cache',
               'kwak','memory cost-push','dram contract price','lta floor','memory canary',
               'memory-regime-question','iren','aapl','glut','take-or-pay','diffusion',
               'prepayments','plateau','two clocks','citi','crowd-out','crucial','gehc',
               'long-term contracts','bloom energy','memory prices','skhy','bernstein',
               'insider selling','ism services','seagate','gartner',"tom's hardware",'blow-off',
               'cisco','ism manufacturing','memory crowd-out','memory pass-through',"fq4'26",
               'deferred revenue','dram spot','ericsson','informational edge','mehrotra',
               'memory cycle','prices paid 72.6','supercycle','26 scas','toshiba','cxmt fork',
               'dated runway','infineon','nokia','qimonda','rdimm','shortage to 2030',
               'spot vs contract','stop 995','wafer starts','xbox','ymtc','20 weeks vs 8',
               'dram bits','dram spot vs contract','nittobo','sandisk sndk','bit shipments',
               'bonded dram','cash deposits','component inflation','destocking','glut clock',
               'gpt-5.6 nerf','hbm transition','hbm wafer starts','hdd 50 vs 16','hynix adr',
               'inventory split','ism respondents','lenovo','memory content per accelerator',
               'memory input costs','memory tariff','memory-price derivatives','rolling roster',
               'server ddr5','shawn kim','sicarrier','strategic customer agreements',
               'temporary constrained supply','terminal-value short','trump truth social',
               'two-tier market','udimm','v900','seagate stx','taoyuan strike','tim cook',
               'amp parts','cantor','changxin memory','dramexchange','elpida','futurum','gwangju',
               'hetzner','honam','indiana packaging','intuitive machines','iridium','kearney',
               'matterfact','mt62f2g64d8cz-023','mtc40f2046s1rc80bh1','mtc40f4087s1hc1axb1',
               'oge 278-t','pengxinwei','pengxinxu','skhyv','steve liu','swaysure','yongin',
               'digikey tracker','late 2028',
 ],
 'MODEL-ECON': [
               'capability convergence','compression thesis','commoditization','karp',
               'reflection ai','jensen huang','fable 5','opus 5','commoditize your complement',
               'epoch ai','sam altman','thinking machines','capability plateau','delong',
               'gpt-5.6 sol','kedrosky','mark zuckerberg','spread halved','satya nadella',
               'treadmill tax','debasement','altman','cursor','roberts','open weights',
               'segmentation','claude code','copilot','dowd','unit economics','model layer',
               'muse spark','seller-denomination axis','buy the dip','coinbase','detachment bid',
               'goodhart','gopher digest','gpt-6 astra','harness','margin compression','mythos 5',
               'opendesign','palantir','sign flip','artificial analysis','bedrock',
               'indemnification','release cadence','servicenow','telecom analogy','wound','z.ai',
               'gemini 4 argon','azure ai foundry','cost wall','dario amodei','decisions api',
               'front-loading','frontier cadence','frontier premium','google deepmind',
               'huggingface','lip-bu tan','near-frontier','roberts scorecard','run-hot','snowflake',
               'window discipline','fable 5.1','opus 5.5','qwen3.5','sonnet 5.5','agent swarms',
               'arcee','arena.ai','automationbench','cadence stretching','capability margin',
               'capability margins','capital iq','certification moat','composer 2',
               'convergence chart','core pce 3.4','david sacks','deepswe','denominator trap',
               'epoch eci','frontier-bench','frontier-cadence trigger','gemini 3.8 flash',
               'gpt-5.6 luna','gpt-5.6 terra','gpt-6 luna','gpt-6.1 sol','grok 4.6',
               'hidden reasoning','highest since oct 2022','ignoring harnesses',
               'industrial-scale distillation','institutional memory','interchangeable models',
               'marco argenti','meta superintelligence labs','mini-cycle','mit nanda','opus 4.8',
               'oracle oci','ppi 4.7','prudence','re-divergence','richland parish','shield regime',
               'sonnet 5','terminal-bench','terminal-bench science','unit labor costs',
               'willing axis','haiku 5.5','acemoglu','aldasoro','bis bulletin 130',
               'black forest labs','brian armstrong','briggs','chatgpt pro','claude max',
               'composer 2.5','farbast','fireworks ai','fred ophnfb','future is for everyone',
               'gambacorta','gemini 3.6 flash','genai divide','goldman sachs cio','gpt-5.5 pro',
               'gvr chart','kharroubi','kodnani','llama strategy','meta llama','microsoft mdash',
               'minisqlite','nano banana','nvidia nemotron 3 ultra','onramp','openai cfo',
               'openai devday','openai help center','opus 4.5','osworld 2.0','qwen3.5-9b','replit',
               'rottner','samsara','sargent','sqlite in rust','sqllogictest','winbuzzer',
               'wsj tokenunmaxxing','zscaler','perplexity','suspicious timing',
               'handheld agentic module','nothing local',"that's brian armstrong",'ahead of him',
 ],
 'MUNITIONS': [
               'pac-3','interceptor depletion','avav','ktos','onds','ondas','caine','neros',
               'pickaxe mountain','dpa priority','hellfire','one-way attack drones','pltr','musk',
               'centcom','hegseth','attrition','triage','vance','starshield','cooper','magazine',
               'palantir','sm-6','us navy','rcat','appropriation','gbu-43','telegraph',
               'third carrier','air defense','anonymous officials','department of war',
               'drone dominance','emil michael','leverage-poor','munitions leak','northrop',
               'project meridian','raf fairford','replacement demand','replenishment',
               'supplemental','anduril','lmt/noc/gd','patriot batteries','abraham lincoln',
               'air-defense munitions depleting','ammunition rapidly','anti-ship missiles',
               'autowarcom','gauntlet ii','general atomics','instrumentalism','jassm','manpads',
               'moab','mq-9','non-concur','patriots-for-pause','praying mantis',
               'precision strike missiles expended','shahed-136','spr 3.05mm','theodore roosevelt',
               'umac','waltz','nmesis','aptim','b-1b','b-52','beidou','caudle','diego garcia',
               'drnl','drnz','dzyne','earnest will','ellsworth','essm','eucom','fmu-139',
               'george h.w. bush','george washington','gingrich','greek-run patriot','iskander',
               'jedi','keen sword','kh-101','luckey','makin island arg','mh-60','mk 41 vls',
               'mq-9 reaper','nasr 2','ocean trader','pacom','parnell',
               'prioritised ukraine requirements list','quanta government solutions','shld',
               'sm-series','southcom','space force lane 1','stark aerospace','whiteman','yonaguni',
 ],
 'POWER': [
               'bring your own power','interconnection queue','transgrid','power-not-petroleum',
               'semianalysis','transformers','turbines','fuel cells','bloom energy','eo 14420',
               'sb energy','entergy','power bottleneck','gartner','ratepayer protection','exelon',
               'large-load tariff','talen','vertiv','heatmap','on-site generation','electric bill',
               'bring your own generation','33 gw shortfall','bridge power','data centres','texas',
               'transformer','ports','doe','lutnick','mw-dollar','switchgear','blackout','ferc',
               'hyperion','trendforce','chips-mw-framework','ppas','schneider','nrg','tceq',
               'electrons','ratepayers','relief valve','eaton','uprates','300 mw','abbott',
               'energized mw','ghost-mw purge','krishna','adnoc','bess','bipartisan ratchet',
               'energized capacity','loviisa','rate base','ratepayer protection pledge','thailand',
               'bwxt','batch zero','calvert cliffs','nne','voltagrid','aep ohio','capacity factor',
               'census c30','commitment fees','data-center load','de-risked gw',
               'electric construction','gas turbines','iras','kw/gpu','pike county',
               'project jupiter','slot reservations','switchgear sold out','time-to-power',
               'utility dive','virginia gs-5','warren','4.2 gw','puct','active power','aema',
               'behind-the-meter gas','core scientific','desalination','doe spark',
               'electricity forwards','fervo','finland halt','firm power','grid queue',
               'landlocked finding','lng exports','merchant nuclear','mw do not add','nrsc',
               'nuclear ppa','phantom pipeline','pjm 7gw short','pressure campaign','san francisco',
               'sieyuan','speed-to-power','termination charges','0.72 gw','1.6 gw',
               '116 telecom towers','250mw','5 gigawatts','800mw by 2028','possum point','baird',
               'binding offtake','blumenthal','census construction','civilian utilities',
               'coal-for-ai','compute-per-mw test','contested from inside','contracted load',
               'curtailment tariff','data center watch','data-center share of electricity',
               'discount-rate channel','el paso electric','emergency order','forced dispatch',
               'gas-set power','georgia power','grid constraint','grid interconnection','hochul',
               'interconnection criteria','interim resource adequacy service','load forecasts',
               'maha-aligned activists','mgrid','microgrid','nerc','net power shortfall',
               'oct-5 cme curve','power caveat','power eases','power gap','ratepayer act','s.4214',
               'sempra','softbank energy','stranded compute','swett','utility bills','van hollen',
               'watts-for-silicon','williams power jvs','ferc iras','aemo',
               'al-subiya power station','bowring','capito','crea','doe 17-state order',
               'duke energy','duke energy carolinas','pay your way',
               'efficiency substitutes for megawatts','horrendous job','ghost-mw','announced gw',
               'hwm','gev','underwater car','btm over','foot the bill',
 ],
 'RATES': [
               'treasury','t10yie','dgs10','dgs2','bear steepening','dgs30','2s30s','t5yie',
               'bull steepener','higher for longer','indirects','dallas fed','fiscal dominance',
               'dfii30','highest since 2007','treasurydirect','bear flattening','dfii10','20s30s',
               'el-erian','highest since 2001','jpmam','bear flattener','bear steepener','tlt',
               'dealers','directs','roberts','belly','10y real','ice bofa','tchir','us treasury',
               '10y breakeven','fiscal supply','haven bid','when-issued','30y real','cembalest',
               'crowding out','decomposition first','druckenmiller','nbim','real cost of money',
               'stopped through','5y5y','dgs20','safe-haven inversion','30y 5.19',
               'acm 10y term premium','financial repression','hedged pickup','level vs change',
               "long end won't cooperate",'mortgage rates','real-led','summers','t5yifr',
               'tips liquidity squeeze','yield-targeters','academy securities','administered 30y',
               'de vere','duration collision','effr','quarterly anchors','ramaswamy',
               'real vs breakeven','searls','base rate','gold','war-board','tools/tape.py',
               'priced in','round trip','ny fed','credibility','resistance','new high','round-trip',
               'breakout','payrolls','citi','real yields','stagflation','steepening','apparatus',
               'takedown','tradingview','btc','already in the price','basis points','dowd',
               'seasonality','bond yields','give-back','ism services','slok','10y 4.64',
               '10y auction','crowd-out loop','dec-745 put','disconfirmer fired',
               'division of labor','policy path','red line','24-year high','buyer base',
               'confirmation sequence','inflation prints','ltcm','one-and-done','treasury buyback',
               'war window','10y real yield','20y auction','3y auction','5y +3bp','tnx',
               'auction internals','bear-steepening','bonds bid','borrowing costs',
               'expectations wedge','iorb','july cpi',"long end won't rally",'musalem','real wages',
               'steepener','stepped back','supply and demand','10y 5.10','19-year high','30y 5.26',
               '30y reopening','5y auction','60/40','99.95th percentile','tyx','absorption problem',
               'barchart','bond rout','breakevens anchored','citadel securities',
               'convenience yield','debasement trade','durables','duration bid','dv01',
               'effective n','basis trade','20y reopening','10y reopening','5y tips','stop-through',
               '8/13 auction','back-to-school hiring','bind','collision thesis','separation shape',
               'fragility scan','there are buyers','hike is bullish','abundant and expensive',
               'discount-rate grind','h.15','pro-hikes',
 ],
 'SANCTIONS': [
               'graham act','india','lutnick','rubio','alibaba','bytedance','designations','mofcom',
               'economic outcast','demarche','economic fury','shadow banking','washington',
               'sanctions','taiwan','senate','russia','apple','commerce','pentagon',
               'export controls','graham','smci','atlantic','gb300','heating oil','helium','quartz',
               'tether','export-quota','hong kong','distillate stocks','malaysia','murban','taipei',
               'us treasury','vance','collins','gl 135','legal clock','loophole','smuggling',
               'urals','basrah','catl','diesel licence','on/off switch',
               'operation economic outcast','witkoff','z.ai','ofac gl 135','domestic duv',
               'economic isolation','kimi k3','macau','sanctions relief','shadow-fleet easing',
               'shadow-fleet sanctions','sieyuan','super micro','uk sanctions','ymtc','28nm',
               'al-monitor','almonty','commerce rule','congress.gov','curtis','customs circular',
               'eight shadow tankers','european commission','germanium','i am the house',
               'kyiv post',"lloyd's market association",'maximum pressure','meeks','moonshot ai',
               'nitc','ofac sdn','parallel market','re-export','sb0507','scrap export ban',
               'seizure authority','self-enforcing embargo','shandong','sicarrier','tungsten',
               'zombie vlccs','36 entities','eo 14066','uani','afra al hameli','albatron',
               'arab medium','b300 indictment','bank melli','business upturn','chinese banks',
               'chinese embassy','comac','g20 asheville','govinfo','guo jiakun','he lifeng',
               'hengli petrochemical','house select committee','ikco','iran railway co',
               'irgc firms','islamabad agreement','itar','julianne mcshane',
               'keelung district prosecutors','mahan air','manus','moea','murkowski',
               'persian gulf strait authority','raja passenger trains','reagan act',
               'responsible business alliance','responsible minerals initiative','s.5025','saipa',
               'senate foreign relations','shaheen','shandong teapots','sullivan & cromwell',
               'swaysure','teapot refiners','three banks sanctioned','tillis','uae mofa','uae nsa',
               'us energy chief','wally liaw','whitaker','jan 2028','questionable legal grounds',
 ],
 'SCREEN-METHOD': [
               'artifact test','instrument mismatch','rule 21b','rule 21','tape.py',
               'evidence ladder','anti-double-count','error class 8','rule 21c','yfinance',
               'vendor conflict maximal','acute scanner','warning vs trigger','over-correction',
               '47/46 baseline','mainstreaming discount','multiple testing',
               'quote-header reconciliation','rule 22c','class 8','flag-board','transmission-chain',
               'tools/tape.py','promoted','assumption-filters','rule 10','rule 9','runner-anatomy',
               'danger-disclosure-playbook','denominators','dip-buying-base-rates','retail-edge',
               'falsifiers','adsk','category error','librarian','chips-mw-framework','digikey',
               'rule 20','two clocks','bloomberg chart','buying-at-highs','google news rss',
               'hindsight','power-to-silicon-thesis','tradingview','error class 4','gehc',
               'grades.md','headline only','rule 8','who gains if believed','yahoo 1-minute',
               'confound','demoted','edgar xbrl','error class 2','lagged echo',
               'numbers and perimeters only','persona','pypl','funnel','independence score',
               '20-sma','4-week average','chartpreviousclose','psky','stale reference',
               'two-population','200-sma','collector csv','deep-value-reclaim','hlne','paypal',
               'powl','sharpe','surprise rule','upwk','vicr','9 hike dots','amph','bond-like',
               'crosscheck.py','ctsh','e-path','gnrc','header test','magnitude collision',
               'marks.csv','numerator and denominator','rung upgrade','adma','base/reference error',
               'bottleneck layer','calendar gate','celh','close array','confidence interval',
               'decompose before reading','denominator artefact','effective n','fisv',
               'leave-one-out','menu.py','numbers vs adverbs','p-value','quiet-health screen',
               'quote header','railroad layer','republish trap','sensitivity table',
               'stale denominator','stale reference value','strl','tautology','20-day reclaim',
               'soxx-minus-spy','amrz','aroc','blkb','chokepoint measures the chokepoint',
               'composition effect','e broken','fcf gate','header reconciliation','magnitude check',
               'meta-lesson','momentum-cohort signature','net vs gross','perimeter clash',
               'previous close','reported vs measured','run event','stale bar',
               'start-date artifact','value-cohort ignition tell','verification layer','vrrm',
               'adnt','archrock','avnt','caly','celsius','docu','exls','fidelity trader+','gntx',
               'goldman communacopia','hamilton lane','mim.py','newegg','prdo','qnst',
               'treasurydirect api','usac','worthington steel','wsj graphic','yelp',
               'power-to-silicon',
 ],
 'SEMIS': [
               'intc','mrvl','soxx','dell','amat','klac','lrcx','crdo','cohr','smci','anet',
               'lutnick','marvell','lumentum','qcom','trendforce','alab','substrates','ttmi','cien',
               'hock tan','corning','credo','tsm','aapl','semianalysis','tsla','commerce',
               'gross margin','optical','bloom','stx','smh','washout','ddr5','gb300','citi',
               'semicap','sox','memory complex','rubin ultra','mediatek','h100 rental',
               'installed base','one trade','air-pocket','anss','bottom decile','buy the dip',
               'custom-asic','ewy 6','mpwr','seagate','worst case','concentration flag',
               'crowded longs','crwd','mtsi','privorotsky','revenue per wafer',
               'taiwan concentration','vertiv','zero buys','2330.tw','terafab','axti',
               'capex unchanged','chip rout','cuda','memory rout','mitsui','anchors and balloons',
               'beat and raise','besi','cdns','demand exceeds fy27 outlook','exemption list',
               'mi355x','mlcc','nvts','relative volume','semiconductor tariff','semis ladder',
               'snps','synopsys','tsmc monthly revenue','wafer starts','soxx-minus-spy spread',
               'abf substrates','ai semi revenue','aixtron','apex name','applied materials',
               'chips act','ciena','copper foil','custom-silicon test','ebrard','full-index sweep',
               'globalfoundries','ibiden','jean hu','jim schneider','jpm am','lam research',
               'laser-making machines','mi400','mi450','momentum factor','mtrn','nittobo',
               'passives','prepaid capacity','priced for perfection','reference architecture',
               'rogers','second demand wave','semiconductor tariffs','sglang','staples +3.52',
               'strength zone','sumitomo','ticking time bomb','units vs price','veco','vllm',
               '3110.t','5016.t','6967.t','ai enterprise','aixny','amg.as','ansys',
               'apriel-nemotron','astera labs','dupont','elite material','eneos','eoptolink','epyc',
               'g10-asp','gary dickerson','goldman 1-delta desk','google earnings','hurlston',
               'intel ohio','kakashiii','kyccf','lfus','materion','mocvd','murata','netapp','ntap',
               'qcom dragonwing iq-2390','rich privorotsky','sammy fans',
               'samsung electro-mechanics','semco','semi silicon area','shinko','sk nexilis',
               'spector','taniobis','teradyne','tsmc arizona','unimicron','ustr greer','veeco',
               'yageo',
 ],
 'SHEETS': [
               'balance-sheet-board','blackrock','cursor','uncommenced leases','capex/ocf',
               'off-balance-sheet','lessor guarantee','purchase commitments','finance leases',
               'purchase obligations','spacexai','artificial earnings','primary beneficiary',
               'fcf proxy','iren','backstop','soxx','leases','amat','apple','tsla','circularity',
               'rpo','ai-infra-allocation-map','stakes','hyperion','tesla','wulf','apld',
               'connectivity','receivables','terawulf','crcl','negative fcf','sale-leaseback',
               'stateline','compute sellers','do-not-add rule','el paso','off-sheet','spacex mark',
               'adj ebitda','anthropic facility','contingent liability','corz','customer equity',
               'deferred revenue','lease backstop','lease guarantees','musk complex','nflx',
               'op income','capital intensity','cipher','consolidated vie','equity-securities gain',
               'hut 8','item 8.01','level 2','ports guarantee','segment revenue','solaris',
               'unrealized gains','ai segment','ai-cloud agreements','annualized burn','atm equity',
               'contracted commitments','conversion rate','leases not yet commenced',
               'meta louisiana','non-operating mark','noncancelable commitments',
               'off-balance-sheet thesis','orcl 10-q','residual guarantee',
               'residual value guarantee','segment table','starbase','vendor-bank','10-q footnote',
               'affordable care','airtable','apr energy','bending spoons','confluent',
               'first brands','hashicorp','medallia','microsoft 10-q','point bonita',
               'private capital field report','proofpoint','sara eisen','stateline spv',
               'tsla megapack','western alliance',
 ],
 'TELECOM': [
               'lucent','nortel','telecom analogy','clecs','musk','carriers','gehc',
               'long-term contracts','receivables','billing','cisco','starshield','uber','charter',
               'ericsson','restoration','worldcom','amt','cci','fierce','global crossing','juniper',
               'netflix','nokia','peak/off-peak','scotiabank','100 mph','amazon leo','fcc approval',
               'femtocells','fierce network','switchboard','whatsapp','beskrestnov','cricket',
               'dish','ekholm','electronics360','iridium','mobile world live','mvno',
               'wireless estimator',
 ],
 'TOKEN-ECON': [
               'tokenmaxxing','token deflation','tokens per task','pltr','compression thesis',
               'artificial analysis','deepseek v4 flash','frontier premium','kimi k3',
               'token price war','jevons paradox','barbell','vercel','token index','gpt-5.6','karp',
               'token-denominated','ornn','compute-denominated','fable 5','palantir',
               'price per token','volume leg','cost per token','gpt-5.5','opus 5','price umbrella',
               'ramp ai index','revenue per gpu-hour','commoditize your complement','epoch ai',
               'free tokens','reasoning tokens','revenue per token','tokenunmaxxing',
               'usage-weighted index','deepseek v4 pro','gpt-5.6 sol','gpt-5.6 terra',
               'metered compute','moonshot ai','opus 4.8','race to zero','token revolt',
               'vercel ai gateway','break-even volume','quality-adjusted price','qwen 3.8 max',
               'token efficiency','volume outruns price','iren','routing','semianalysis','musk',
               'polymarket','altman','scarcity premium','commoditization','fable','marginal cost',
               'own the toll','segmentation','45 days','a16z','claude code','copilot','air pocket',
               'bain','price cut','scarcity pricing','seller-denomination axis','snow',
               'token demand','alibaba','coinbase','ddog','duration mismatch','infant market',
               'jensen huang','list price','mythos','clustermax','commoditisation','commodity tier',
               'compute futures','gpt-6 astra','jevons spread','mythos 5','no listed expression',
               'price hike','revenue jevons','routers','x402','datadog','bedrock','broad index',
               'cheap tier','flat-rate','free tier','jevons volume','mix shift','muse spark 1.1',
               'opus 4','seat-denominated','spacexai','tiering','vintage split','z.ai',
               'azure ai foundry','cast ai','consumer surplus','deepseek v4.1 flash',
               'efficiency shock','financialization','gemini 4 argon','glm-5.3','glm-5.3-flash',
               'h100 rental index','litellm','llm token expenditure index','muse wonder',
               'outcome/seat-denominated','paid tokens','per 1m tokens','per-token price',
               'premium pricing is vulnerable','price leg','price of intelligence',
               'reference price','shopify','spend limits','token expenditure index',
               'token price index','2.05 peak','arena.ai','braggawatts','cached input',
               'cheap chinese compute','cogs cut','composer','cost per accepted result',
               'culpability premium','deepswe','fable 5.1','frontier-bench','gemini 3.8 flash',
               'glm 5.2','glm-5.2','gpt-4','gpt-5.6 luna','gpt-6 luna','gpt-6.1 sol','grok 4.6',
               'half price','half the price','hyperscaler index','inference arr',
               'input/output asymmetry','jevons dashboard','kimi k2.5','layoffmaxxing',
               'mag7 workbook','measurement blindness','metered rail','model arbitrage',
               'realized mw','denomination axis','commoditization layer',
               'software integration layer',
 ],
 'VOL': [
               'cor1m','implied move','vol-divergence','correlation snap','vix9d','dealer gamma',
               'garrett','short gamma','vix asleep','gold','where-the-edge-is','yfinance','whipsaw',
               'earnings-implied-moves','sensor','iv30','dec-745 put','iv crush','cdx ig',
               'dec-18 745 put','bimodal','calm stages','mcelligott','options-reference-natenberg',
               'squeeze fuel','two-speed market','vol gap','745 put strike','dispersion arithmetic',
               'dispersion trade','record-low correlation','thin liquidity','vol clustering',
               'wilson','atm straddle','dec-745 puts','spy straddle','anchors and balloons',
               'call volume','cboe delayed quotes','cor3m','dec spy puts','decide zone','long vol',
               'median index correlation +0.10','nasdaq 100','straddle breakeven','vix pop',
               '724 put','garch','iv vs rv','vix3m','cheap index put','correlation discount',
               'gate 2','gs semiconductor long vol','implied vs realized','insurance cost',
               'long rate vol','louis miller','mag7 long vol','move/vix 7.3','nomura',
               'semiconductor long vol','single-name dispersion','sts vol desk','var shock',
               'vix 15.28','vol compression','cboe iv30','dspx','s&p single-stock volatility index',
               'skew index','vix call skew','vix futures','vix6m','cullen morgan','dec-18 745p',
               'goldman derivs','heisenberg report','meta options','pasquariello','rubner','savone',
               'tuteja','what window','theta','gap is the trade','move/vix',
 ],
 'WAR/OIL': [
               'war premium','trump','polymarket','houthis','kuwait','centcom','jask','yanbu',
               'iraq','bahrain','saudi arabia','adnoc','kharg island','naval blockade','qatar',
               'fujairah','araghchi','rubio','jmic','vance','war-risk insurance','brent-wti spread',
               'netanyahu','ras tanura','administered strait','basra','mojtaba khamenei','gold',
               'war-board','diesel','kill switch','ultimatum','escalation ladder','ras laffan',
               'strait of hormuz','jordan','murban','3-2-1 crack','all or nothing',
               'discretionary permission regime','irgc navy','irib','sirik','south pars',
               'war-risk premium','chris wright','instrumentalism','larak island','qeshm island',
               'fuse','parr','india','tripwire','mb/d','red sea','united states','diesel crack',
               'heating oil','newsquawk','bab el-mandeb','off-ramp','petroline','tehran','yemen',
               'qatarenergy','anadolu','east-west pipeline','permission regime','sumed',
               'attribution doctrine','baghaei','bandar abbas','basrah','dark tankers',
               'hormuz closure','night 13','ratcliffe','war powers','witkoff','ali al salem',
               'asaluyeh','blockade of iranian ports','caine','chabahar','day 145',
               'gated-transit regime','grigsby','hassett','hormozgan','kavomaleas','konarak',
               'muwaffaq salti air base','physical gap','pickaxe mountain','strike-then-deal',
               'struyven','toll regime','war-premium unwind','bilateral punitive interdiction',
               'dark transits','disabling fire','energy independence','fig leaf','kushner','natanz',
               'nsa bahrain','rezaee','zolfaghari','administered chokepoint','blockade runner',
               'electoral clock','escalation rung','goreh-jask','gps jamming','khatam al-anbiya',
               'leverage-poor pause','mohsen rezaei','operation epic fury','pgsa',
               'reported vs physical','snsc','supreme national security council','toll gate',
               'oil-value-chain','fork','vlo','artifact test','freight','mpc','chokepoint','razor',
               'dht','cracks','risk premium','russia','capitulation','coalition','midterms','psx',
               'congress','de-escalation','priced in','pentagon','dino','pbf','xle','bno',
               'force majeure','khurais','starshield','pac-3','sm-3','brent dec','brent front',
               'brent spread','oil spike','oil shock','gulf exports','saudi exports','alert',
               'russian refineries hammered','wrong body of water','mining the strait',
               'predicate read','anti-mining','retaliation','declare it over',"isn't a war",
               'exit architecture','gfs',"russia's decree",'missile constraint',
               'signaling a shortage','instrumentalism thesis','holding their breath','oman talks',
               'transit windows','bab-el-mandeb','i offered them nothing',
               'dated third-country meeting','loud attack distraction','yanbu day','tolls',
               'detention','two-track','freight shopping tickets','sheesh','simply false',
 ],
}
THREADS_NEW = {
 'REFINING': [
               'diesel crack','3-2-1 crack','parr','dino','hf sinclair','gasoline crack',
               'par pacific','valero','volgograd','heating oil crack','marathon petroleum',
               'phillips 66','refiners','kill-switch','demand destruction','conversion capacity',
               'dubai','murban','us refiners','wright','exit bell','orsk','refiner summit','ryazan',
               'zawiya','100m bbl','birol','dangote','macron','refining margin','ruwais',
               'deferred crack','dyed diesel','capture rate','ice gasoil','pbf energy','rbob crack',
               'run-rate headroom','small refinery exemptions','steep backwardation',
               'straight-run diesel','swing refiner','ulsd crack','unplanned outage','war-board',
               'buybacks','bracket','export ban','midterms','rationing','tripwire','all-time high',
               'beijing','nov 3','price-insensitive','52-week high','four months','mexico',
               'singapore','williams','diesel export ban','heating oil','q3 earnings','windfall',
               'yanbu','differential rule','loadings','refinery basket','sep-26','crack spreads',
               'hong kong','midstream','dec-26','product exports','refiner basket','ulsd','abbott',
               'ban clock','california','duration mismatch','espo','fuel campaign','missing half',
               'norsi','padd-1','producer exemption','refinery strikes','stng','tchir','turnaround',
               'vance','campbell','crude leg','deferred strip','exxon','exxonmobil','hocl1','kb/d',
               'margin capture','novak','refinery runs','rostov','sinclair','spr exchange','urals',
               'whitehouse.gov','99.4th percentile','above target','chalmette',
               'deferred maintenance','diesel/gasoline ratio','guidance language','hawaii index',
               'lukoil','mt/yr','multi-year high','multiple expansion','port arthur','product leg',
               'refiner trade','robinhood','saratov','sres','suppression stack','trmd','usda',
               'vitol','0.66 mb/d','bzz26','coker','conversion-capacity bottleneck','dated brent',
               'dec-27','delek','denominator down','diesel release','eps revisions','eu gasoil',
               'export quota','floating storage','fy27 eps','gasoil crack','hold 9',
               'jazan refinery','mahshahr','mccormick','meduza','month mismatch','moscow times',
               'novoshakhtinsk','diesel','ho crack','2-1-1 crack','distillate','jet fuel','rbob',
               'refinery','vlo','mpc','psx','dk','cvr','pbf','diesel ban','product export',
               'aaa gas','gasbuddy','gas prices','pump price','retail gasoline','90-day plan',
               "ceasefire won't last",'paper loss',
 ],
 'MARITIME': [
               'bypass','yanbu','east-west pipeline','sumed','ras tanura','sohar','fujairah',
               'araghchi','petroline','bwet','insw','jask','jmic','qatarenergy','stng',
               'permission regime','habshan-fujairah','adcop','insights.windward.ai',
               "lloyd's market association",'iraq-syria pipeline','freight','force majeure','vlcc',
               'iraq','ras laffan','toll booth','centcom','strait of hormuz','dubai','saudi arabia',
               'data as of','hormuz bypass','seagate','us treasury','war-risk insurance',
               'yanbu loadings','adnoc','khurais','product tankers','pumping station',
               'spare capacity','tanker rates','baghaei','bandar abbas','bypass terminus',
               'discretionary permission regime','egypt','habshan','illegal route','kharg island',
               'opec+','transit count','trmd','20.7 million barrels','vlgc','bahri','basra',
               'convoy','dark vessels','floating storage','hassett','howden re','imam khomeini',
               "iran's lane",'japan-linked vessels','kavomaleas','lavan','ncc ghazal',
               'stocks clock','toll layer','toll regime','trafigura','vlsfo','waiting area',
               'war-risk cover','windward daily intelligence','10.05 mb/d ineligible',
               '60 days without fees','7 bypass projects','odfl','zim','abu dhabi ports','baniyas',
               'bypass artery','bypass eligibility','chokepoint tax','dark transits','dhahran',
               'dubai east-coast port','eo satellite','evacuation route','fee holiday',
               'fee schedule','foiz','foreign interference','freight wedge','frontline',
               'gaslog shanghai','gastat','gulf bond boom','iran foreign ministry',
               'khurais pumping station','kotc','kurdish region','laden runners',
               'launched from iraqi territory',"lloyd's clause",'management of ship traffic','mioc',
               'mt lavine','nitc','noble','ofac sdn','oman corridor','opec exit','proxy layer',
               'record freight','red sea terminus','renewal leverage','repair clock',
               'resumption vs repair','saudi aramco','saudi east-west pipeline','shadow tanker',
               'shedgum','sidi kerir','smuggling risk','southern corridor','tamura','tanajib',
               'thermal anomaly','third door','third spigot','ton-miles','tool of pressure',
               'transit fixtures','turn-backs','uae flag','umm qasr','unclos','vessel transits',
               'vlcc rates','wreck removal','zero transits','jbht','knx','panama m7.7','ain sukhna',
               'amara','ambrey','angelicoussis','east west pipeline','pump station',
               'bypass pipeline','strait transit','hormuz transit fee','transit toll','vortexa',
               'tankertrackers','ais gap','suezmax','aframax','td3c','fro','dht','tnk','asc','nat',
               'euronav','hafnia','torm','ws rate','worldscale','war-risk premium',
               'war risk insurance','p&i','cape of good hope',
 ],
 'RED-SEA': [
               'yanbu','houthis','bab el-mandeb','second chokepoint','red sea','suez','abha',
               'bab al-mandab','cape of good hope','sanaa','encelia','hodeidah','jizan','ncc masa',
               'yahya saree','near-miss','petroline','saudi arabia','east-west pipeline','sumed',
               'attribution doctrine','habshan-fujairah','houthi blockade','ras tanura',
               'suez canal','aqaba','bahri','jazan refinery','ncc ghazal','rabigh','adcop',
               'east-west pumping station','fidan','firms cluster','full-scale war',
               'gaslog shanghai','ground offensive','hisn murad','hocc','khamis mushait',
               'mb/d bypass','red sea blockade','red sea closure','three chokepoints','viirs',
               'al shuqaiq','al watan','al-assad','al-jawf','al-salif','ali al-zaidi','amzan',
               'ansarallah','asir','british maritime monitors','chrystal sky','dammam','dhubab',
               'future investment initiative','jeddah','jeddah north bulk plant',
               "jordan's only seaport",'kaifan','kamaran island','khalid bin salman',
               'king fahd airport','king khalid international airport','lesser hanish',
               'maha al saud','marib','mayun island','mecca pact','medina power station',
               'minoan pioneer','mokha','molowarmonitor','najran','navig8 messi','ncc wafa',
               'petro rabigh','presidential leadership council','rashad al-alimi','riyan star',
               'saada','saba agency','sharurah','tarifa','tihamah','turki al-maliki','ukmto 106-26',
               'world petroleum congress','yemen online','yemeni armed forces',
               'yemeni government troops',
 ],
 'RUSSIA-UA': [
               'putin','kyiv','zelensky','norsi','kremlin','novak','ratcliffe','ryazan','saratov',
               'peskov','moscow','zelenskyy','energy ceasefire','kyiv independent','lukoil',
               'meduza','novoshakhtinsk','syzran','gazprom neft','kushner','rosneft','tatneft',
               'kharkiv chp-5','refinery strike campaign','export ban','musk','payback','ukraine',
               'graham','diesel export ban','dallas fed','graham act','effective immediately',
               'iaea','physical constraint','refinery strikes','collins','diesel exports','rostov',
               'russian diesel deal','starshield','energy truce','orsk','poland','telegraph',
               'tpp-6','ukrainian drones','witkoff','macron','moscow times','nefrit','new front',
               'new leader','physical capital destruction','piers morgan','product imports',
               'romania','sanctions relief','sochi','unilateral halt','von der leyen','0.74 mb/d',
               'arms threat','betrayal','burn refineries','curtis','decree asymmetry',
               'depot strike','drone campaign','estonia','gasoline vs diesel','geiger',
               'importing refined product','kirishi','krasnodar','kyiv post','naryshkin',
               'neptun deep','netback','omsk','orenburg','patriots-for-pause','petrol queues',
               'refineries burning','refinery campaign','russian seaborne diesel/gasoil loadings',
               'ryazan 17.1 mt/yr','trilateral summit','ukhta','volgograd',
               'we will burn refineries','arkhangelsk','bashkortostan','c-17','cia director',
               'eurasia group','iskra','kaluga','kh-101','khabirov','kolyandr','kstovo',
               'kyiv tpp-6','leipzig/halle','michal','millerovo','moldova','moscow refinery',
               'murkowski','myla','north atlantic council','pantsir-s1','penza',
               'permnefteorgsintez','primorsky','serhiy beskrestnov','shaheen','smolensk',
               'sobyanin','sternenko','steve cortes','tambov','tillis','ukraine general staff',
               'ukrnafta','ulyanovsk','ushakov','voronezh','yandex data centres','yaroslavl',
               'yeysk','zaporizhzhia npp','both like huh',
 ],
 'IRAN-POL': [
               'aapl','houthis','araghchi','hong kong','reuters exclusive','succession','baghaei',
               'irib','supreme leader','manpads','mojtaba khamenei','noble',
               'shoulder-launched missile systems','22 chinese-linked vessels','ali khamenei',
               'assembly of experts','mohsen rezaee','salimi','snsc','wbur',
 ],
 'CHINA': [
               'apple','canada','brazil','malaysia','catl','csis','domestic duv','kimi k3',
               'shandong','caijing','netease','aapl','taiwan','senate','india','beijing',
               'demand destruction','trendforce','cost-push','curtailment','shanghai',
               'release valve','customs','usar','dubai','product exports','uuuu','bytedance','espo',
               'restocking',"tom's hardware",'aloy','argentina','chinese open-weight models',
               'mofcom','moonshot','urals','wccftech','ieepa','liao na','opec+','sasac','teapot',
               'z.ai','4.4 mb/d','bessent-he','department of war','djeno','export quota',
               'glm-5.3-flash','localization','nist','open-source models','price vs volume',
               'project swarm','remote-access loophole','spot return','stopped bidding',
               'trump-xi summit','ustr','v4.1 flash','wrench','100-140mb','almonty','amec',
               'bonded dram','cairo','canada investment summit','compartmentalization','congo',
               'core cpi 1.0','delivered cost','demand withdrawal','dpa priority',
               'exporting its way out','glm 5.2','glut clock','hfi research','huawei 950dt',
               'independent refiners','inner mongolia','kimi k2.5','kozmino','leverage ledger',
               'lng trucks','magnet chokepoint','monolith','moolenaar','moonshot ai','onshoring',
               'ring of fire','sangdong','section 301','supply offset','tariff-refund','teapots',
               'technode','ticking time bomb','trade deficit','trade truce','trump-xi dinner',
               'tungsten scrap export ban','usa rare earth','v4 pro','carney','china daily','crea',
               'critical metals','cyclic','deepseek v4 flash 0423','donald trump jr','e-vac',
               'futurum','general administration of customs','geomega','glm 5.3','golden dome',
               'greenland','greenland mines','guangzhou','guo jiakun','hohhot','hypromag',
               'japan offtake','jl mag','kayrros','korean metals plant','liang wenfeng','magneti',
               'mahan air','martinson','meidan','mestersvig','mi325x','narsarsuaq','naura',
               'naval war college','neorem','niron magnetics','np materials estonia','oies',
               'ox alpha','patented pharma','phoenix tailings','pituffik','pla navy',
               'power of siberia','qwen3.5-9b','ratingdog','sakhalin','sarfartoq','sartell',
               'shanghai star ipo','shanghai yuliangsheng','smee ssa800','space bunny alpha',
               'stapczynski','star group','state ai fund','stepfun','taiwan cga','tanbreez',
               'teapot refiners','tony blair institute','ubs evidence lab',
 ],
 'VENEZUELA': [
               'washington','hegseth','rubio','pre-repo','maduro','maduro captured',
               'majority us control','delcy rodriguez','extra-heavy','gulf coast refiners',
               'interim president','no chokepoint','operation southern spear','orinoco','texas a&m',
               'amuay','capital economics','columbia cgep','el palito','goldwyn','haustveit',
               'misra','puerto la cruz','sternoff',
 ],
 'FISCAL': [
               'treasury','treasurydirect','deficit','reopening','interest expense',
               'fiscal dominance','when-issued','stop-through','cash-neutral','refinancing wall',
               'reserve injection','fiscaldata','rollover risk','wam shortening',
               'liquidity support','off-the-run','primary dealers','binding constraint',
               'debasement','buybacks','congress','reserves','canada','dealers','directs','roberts',
               'monetize','citi','crowd-out','governing','indirects','real money','4-week',
               'debt service','10y auction','interest bill','norway','rubric','us treasury',
               'at cap','ice clear credit','soma','treasury buyback','wealth tax',
               'auction internals','druckenmiller','ieepa','nbim','net interest',
               'treasury auctions','yen intervention','30-year high','6-auction average','8-week',
               'announcement effect','bond buyer','buyer strike','convenience yield',
               'denominator artefact','highest auction stop since','iran mou','katayama',
               'new issue','nov 4 refunding','sept 18','six-auction average','size cut','vanguard',
               '10y tips','2y frn','administered long end','bnp paribas','buyer-base rotation',
               'dealer take','dealers left holding','doubled buybacks','dswp','duration swap',
               'exhibit 4','fed owns','fima','fiscal ledger','gpif','gross interest','h.4.1','h4.1',
               'hqla','liquidity-support','live-fire date','lyngen','marginal-pressure tool','mspd',
               'net marketable borrowing','peter tchir','prefunding','quiet easing',
               'record deficit','refinancing gap','shortening wam','ssdi','summers','tga drain',
               'tga-funded','treasury general account','treasury issuance','trs funding',
               'warehoused','weak auction','weighted-average maturity','yield-targeters',
               '31 usc 3111','8/5 refunding statement','academy securities',
               'api.fiscaldata.treasury.gov','cusip 912810ux4','cusip 91282crn3','cusip 91282crq6',
               'flanagan','france isf','frbny weekly','iowa legislature','iowa sf 2472','le pen',
               'markets.newyorkfed.org','mnuchin','percentoutstanding','refunding statement',
               's&p global ratings','sargent','takata','tobias','wisdomtree','zervos',
               'wolf richter',
 ],
 'INFLATION': [
               'shelter','margin compression','hassett','lodging away from home','umcsent',
               'unit labor costs','portfolio management fees','gold','pricing power','slowdown',
               'ny fed','gasoline','forwards','cost-push','rule 20','census','refi','stagflation',
               'beige book','core goods','dallas fed','q2 gdp','dgs30','margin squeeze',
               'chicago fed','haven bid','level shift','relief rally','sign flip','t10yie','zoning',
               'cramer','de-anchoring','decomposition first','dfii30','dgs10','existing-home sales',
               'final demand','hunterbrook','lennar','mix shift','real wages','10y 2.35',
               'anchored expectations','claims 197k','core ppi','cpi by income quintile','dfii10',
               'personal income','10y tips','30y tips','5y tips','5y5y 2.33','airline fares',
               'arm share','base effects','branch 4','core services','freddie mac','housingwire',
               'ism prices paid','millrose','mortgage rate','nahb','nber w32163',
               "owners' equivalent rent",'purchase apps','rattner','same-vintage','sofr-iorb',
               'summers','tips liquidity premium','vintage mismatch','ytd run-rate','bolhuis',
               'cleveland fed nowcast','feroli','gillingham','jpmorgan traders',
               'mortgage news daily','ny fed sce','richmond fed','schulz','treasury cmt',
               'wsj graphic',
 ],
 'BREADTH': [
               'roberts','breadth','aapl','ndx','qqq','tsla','cape','trendforce','iwm',
               'ai-money-map','rsp','scarcity rent','mcelligott','revenue per wafer',
               'druckenmiller','revenue per unit','wilson','trailing p/e','gsprhimo',
               'comfort systems','equity risk premium','forward p/e','gated demand','lumentum',
               'micron fq4','price-led growth','profit share','rsp vs spy','shiller','spy volume',
               'top-10 weight','yale','qqqe','spxew','goldman pasquariello','longtermtrends',
               'multpl','ritter','rubner','semi silicon area','sf compute','wilshire 5000',
               'momentum basket','momentum factor','momentum unwind','momentum crash',
               'factor rotation','crowded longs','crowding','most-shorted','short basket',
               'high-beta','low-vol','equal-weight','breadth thrust','advance-decline','new highs',
               'new lows','percent above 200','concentration','mag 7','magnificent seven',
               'market cap weight','optimal p/e band',
 ],
 'EARNINGS': [
               'jpm','amat','tsla','adsk','10b5-1','form 4','wfc','cluster buy',
               'open-market purchase','memory-regime-question','aapl','pltr','klac','crdo','lrcx',
               'round trip','dino','rotation-stickiness','blackrock','citi','github','shop',
               'insider selling','snow','blk','ddog','securitize','panw','adbe','anthropic s-1',
               'upwk','crwd','hlne','integration seat','mcelligott','openinsider','zero buys',
               'intu','spacex ipo','coiled setup','ficc','insider buying','mehrotra','nflx','okta',
               'robinhood','table i','flip-tell','insider sales','mu ceo','netflix','bac',
               'agentforce','bank of america','beat sold','cheaper entry','comp monetization',
               'discretionary buy','escape hatch failed','exercise-and-sell','form 144',
               'former ceo','good news sold','googl 7/22','gross proceeds','intc 7/24',
               'post-earnings window','priced for perfection','psus','record-but-insufficient',
               'washout cohort','wells fargo','gtlb','ackman','centerwell','humana','ionq',
               'jpm analyst call','malone','marino','ntap','piper','samsara','unitedhealth','wcas',
               'xlk executives','zscaler',
 ],
 'US-POLITICS': [
               'trump','midterms','musk','commerce','congress','nov 3','ohio','cursor','oversight',
               'who gains if believed','usar','november cluster','uuuu','vance','starshield',
               'palantir','state equity','vertical integration','wisconsin','terafab','adobe',
               'clarity act','ctsh','right after the midterms','warrants-for-volume','55 days',
               'capgemini','chip debt','colossus ii','eo 14330','h-1b','hamilton','hassett',
               'infosys','kansas','paid in equity','political fuse','tarp','trump oil date',
               'administered price floor','administration risk','cognizant','colossus i',
               'house flip','infy','ipo lockup','kalshi','subpoenas','wipro','cahill','cfo johnsen',
               'chips r&d','grok 5','jeffries','quantinuum','starmind ai-1','starship','tata',
 ],
 'CREDIT': [
               'softbank','sb energy','ice bofa','listing cluster','securitize','archegos','nasdaq',
               'dell','vendor conflict','musk','circle','lutnick','polymarket','blackrock','firmus',
               'kill switch','smci','tesla','tether','crowd-out','gehc','btc','ccc oas','crcl',
               'customer concentration','lucent','coinbase','holtec','psky','anthropic s-1',
               'anthropic ipo','cdx ig','cisco','crwv 5y cds','hlne','nortel',
               'residual-value guarantee','x402','announced vs fid','clarity act','crowding out',
               'ctsh','entry condition','ericsson','fink','fuel load','jane street',
               'lease backstop','record ipo','servicenow','innio','appaloosa','arvind krishna',
               'bamlc0a0cm','bbb oas','co-signing','corporate spreads','drall & granato',
               'effective yield','fdic','http 402','ice clear credit eod','infosys','long life',
               'monoline','netflix','nokia','paramount skydance','paul tudor jones',
               'revenue recognition','situational awareness lp','snowflake','tarp','wind-down',
               'maas','ambac','arena.ai','at&t wireless','bamlc0a4cbbb','bamlh0a3hyc','big short',
               'bilateral block sale','bnp paribas','capex reprioritization','cash trap',
               'clear street','cognizant','credit suisse','demand subsidy','depth of the bid',
               'dodd-frank','equity-exit ledger','fire suppression','first closed tranche',
               'first-loss equity','gary cohn','gulf bond boom','hudson pacific','ig pinned',
               'interval fund','investment-grade rating','issuance flood','mbia','minsky',
               'model act','new constructs','nomura','non-operating gains','northwestern mutual',
               'off-takers','office cmbs delinquency','pets.com','premium-tax credit',
               'project-by-project','question the roi','ratings arbitrage','rattner',
               'round-tripping','take-or-pay offtakes','tattle-teller','token revolt','ut austin',
               'wipro','yale','zhongji innolight','bermuda bma','ablin','accenture','alibaba 2014',
               'allen center','andrew granato','anther capital','arcc','ares private credit',
               'assenagon','aviva usa','bamlh0a0hym2','basel iii','bermuda monetary authority',
               'blackstone property partners','blue owl technology fund','breit','bumble','carlyle',
               'castle hook','credit agricole','cresset','dsx ai factories','dwarkesh patel',
               'fluence','fred carr','gardizy','gbdc','openai ipo','ipo pressure','clo',
               'direct lending','leveraged loan','term loan','project finance','insurance float',
               'spac','co-founder sale','form 144','insider sale',
 ],
 'NEOCLOUD': [
               'iren','lambda','datadog','servicenow','semianalysis','cursor','firmus','ddog',
               'take-rate','azure ai foundry','core scientific','governance layer','cloudzero',
               'control plane','fireworks nexus','aws p4d.24xlarge','managed inference arr',
               'microsoft mdash','nitin agrawal','routing','blackrock','google cloud',
               'natural experiment','vercel','evals','wulf','customer prepayments','ddtl',
               'hugging face','segmentation','techcrunch','apld','fluidstack','a16z','claude code',
               'open interest','stripe','terawulf','customer concentration','telemetry','cifr',
               'b300','capex/revenue','control tower','coverage ratio','krishna','lock-in','ornn',
               'panw','wday','hut','ai gateway','app layer','compute futures','harness',
               'integration seat','long tail','meta compute','multi-model','observability','paypal',
               'applied digital','bedrock','clustermax 3.0','deferred revenue','fidelity level 1',
               'jane street','lightning','okta','radiant','salesforce','spacexai','tensorwave',
               'vantage','zitron','agentic cfo','ai acv','cast ai','cipher','curve shape',
               'debt ladder','enroll-once','h100 rental index','h100e','hut 8','layer-4 thesis',
               'litellm','portability','portable computer','refinancing wall','seat erosion',
               'snowflake','spend limits','3-yr reserved','docn','adjusted operating income',
               'agent 365','ai control tower','approval pending','apriel','attach rate',
               'aws bedrock','bitdeer','circularity catch','circularity playbook','collateral mark',
               'commitments of traders','composer 2','contract roll','cost-saving','decart',
               'deep magic','default surface','depreciation cliff','dgx spark','eviction',
               'galaxy digital','genai inference','gpu rental price','gpu1','gpu2','gpuaas',
               'hermes','hkust','horizontal integration layer','jim li','kimi k2.5','langchain',
               'menlo','mlq.ai','mongodb','neutrality paradox','one-year contract midpoint',
               'openai-compatible api','orchestration layer','palo alto networks',
               'reference architecture','rental price index','routing and cost-control layer',
               'sandwich topology','sdh100rt','sglang','sharon ai','smart routing',
               'squeeze in the middle','steering channel','switching cost','take rate',
               'token arbitrage','tom brown','unobserved residual','visible alpha','vllm',
               'agentkit','aimultiple','alistair barr','arize','autogen','b200 rental index',
               'b200 rental index futures','braintrust','capitalg','cirrascale','clearport',
               'cloudflare ai gateway','context portability','usb port for llms',
 ],
 'GRID': [
               'nimby','social license','bloom','bloom energy','tceq','bipartisan ratchet',
               'caterpillar','s.4214','synthetic minor','apr energy','ge tm2500','mitsubishi ft8',
               'sanders','where not if','texas','semianalysis','musk','ohio','force majeure',
               'altman','firmus','williams','fuel cells','schneider','cement','dallas fed',
               'ratepayers','eaton','abbott','coverage ratio','ornn','permian','carry cost','eqix',
               'ercot audit','finland','jevons spread','mississippi','powl',
               'ratepayer protection pledge','revenue/mw','vertiv','vicr','wisconsin','catl',
               'enerflex','heatmap','hubb','jevons absorption','minneapolis','permit freeze',
               'project jupiter','quanta','revenue per mw','sold out through 2028',
               'switchgear sold out','texas permit freeze','time-to-power','voltagrid','cleanspark',
               'collecting dust','epoch ai','haynesville','housing starts','hyundai','infineon',
               'inio','innio','local opposition','lumber','moratorium bills','nrsc','nvts',
               'off-grid','on-site gas','operational mw','permit stay','price of intelligence',
               'public backlash','reinhausen','siemens','sieyuan','sold out through 2030',
               'td cowen','140+ local groups','17 states restricting','30.2gw it','42.6gw facility',
               'aeroderivative turbines','aggreko','aon center','baker hughes','baltimore',
               'chips per mw','circularity catch','clean air act','community acceptance',
               'data center watch','denver','efxt','enchanted rock','energy vault',
               'half collecting dust','hochul','jenbacher','jevons paradox','local veto',
               'midterm issue','moat list','powered-silicon absorption rate',
               'pre-qualified vendor list','ready-mix','reciprocating engines','recips',
               'regulatory-perimeter arbitrage','rural limits','sage road','small models',
               'southaven','stranded capacity','stranded silicon','stranded silicon gap',
               'techpowerup','tom brown','virginia digital gateway','2g energy',
               'advent international','aib data centers','ak steel butler',
               'american battlefield trust','bandi & su','barrack ai','build.inc','change research',
               'chargedup','clarke energy','clearway nv','doncasters','embold research',
               'environmental integrity project','environmental protection network','eugene ye',
               'gpugene','grand rapids mi','green chile pipeline','grid x technology','heatmap pro',
               'howmet','iesc','iija','kalina alberta','kodiak gas services','lathrop',
               'loudoun county','ls electric','mission control','missouri town',
               'mitsubishi j-class','murata','naacp','new mexico environment department',
               'new mexico supreme court','nobles county mn','oak valley hoa',
               'oracle project jupiter','ppi by industry','precision castparts',"who's voltagrid",
 ],
 'NUCLEAR': [
               'holtec','iaea','talen','bwxt','howden','aurora','bwrx-300','el26-101-000',
               'samsung c&t','tmi-1','uprate','advanced nuclear','baker hughes','bechtel','cameco',
               'first-of-a-kind','ge vernova hitachi','htgr','kronos','nano nuclear','natrium',
               'nuscale','terrapower','chart industries','eel river','enveniam',
               'janus microreactors','pabineau','prodigy','rolls-royce smr','studsvik','vattenfall',
               'world nuclear association',
 ],
 'AI-SAFETY': [
               'exploitgym','hugging face','metr','artifactory','chain-of-thought monitoring',
               'gpt-5.6 sol','transcript tampering','redwood research','dell','register','apple',
               'danger-disclosure-playbook','containment','pacing','trendforce','techcrunch',
               'euronews','class action','culpability','gpt-6 astra','injunction','mythos 5',
               'elon musk','message board','sandbox escape','activation monitoring',
               'critical cyber threshold','cybergym','daybreak','liability-withholding mechanism',
               'reward hacking','xbox','zero-day','agentic attacker','ai accelerating ai',
               'ajeya cotra','automakers','capability evaluations','closed self-improvement loop',
               'cointelegraph','covert channel','detection-to-response failure','direct purchasers',
               'exhibit b','five datasets','gpt-5.4','hjalmar wijk','instrument problem','kam1196a',
               'madge waggy','mai-cyber-1-flash','mark chen','n.d. cal','ndrc','obey collective',
               'permadeath','pre-release model','ryan greenblatt','s-curve','thenextweb',
               'uk ai security institute','uk aisi','abdulrahman alfozan','apple v openai',
               'bbs bilisim','black hat 2026','core-bench','craig missakian','fairwind program',
               'favaro','foxconn','geekwire','gpt-6.1 astra','gtg-10007','gtg-50020','gtg-50021',
               'gtg-50029','internal model 1','johannes heidecke','joshua achiam','judge noel wise',
               'lkm company','mia glaese','microsoft mdash','ns123abc','persistent-astra',
               'phaseone10841','sc media','security boulevard','tang tan','self-sacrifice',
 ],
 'AI-ADOPTION': [
               'reflection ai','hugging face','z.ai','thinking machines','android playbook',
               'mastercard','zhipu','musk','softbank','circle','google cloud','ai trade','azure',
               'open weights','vercel','amodei','bitcoin','oligopoly','pypl','stripe','visa','crcl',
               'lucent','mediatek','muse spark','poolside','sovereignty','alibaba','coinbase',
               'deepmind','jensen huang','level 3','hassabis','moonshot','nortel','oecd','paypal',
               'stablecoin','unit of account','x402','asc 606','clarity act','contra-revenue',
               'nbim','ramp ai index','terafab','usdc','worldcom','actuators',
               'commoditize your complement','decisions api','dycom','global ring','http 402',
               'kimi k3','laguna s','messenger','mstr','norges','pichai','regulatory capture',
               'self-hosted','shopify','takaichi','agentic payments','anthropic economic index',
               'antonoglou','apache 2.0','armstrong','bind goes global','burnham','carson',
               'chatgpt ads','chosun','corning','david sacks','deepep','deepgemm',
               'deliberate industrial policy','fierce network','franklin templeton',
               'frontier is the teacher','glm 5.2','gpif','grok bot','harmonic drive systems',
               'humanoid robots','industrial-scale distillation','laskin','linux foundation',
               'mechanize','meta superintelligence labs','micropayment','moonshot ai','muse charm',
               'nemotron 3 ultra','off-balance-sheet spv','sandwich topology','solana',
               'stripe sessions','torsten slok','vendor switching','whatsapp','36kr','adelphia',
               'agility','apollo daily spark','apptopia','ara kharazian','ascend 960/970/980',
               'asia optical','beite','brian wayman','bullock','dean ball','dell xps 16',
               'discovery loop','echostar spectrum','essilorluxottica','estun','everwin','flashmla',
               'fujitsu','gemma','goldman miller','goldman momo basket','gpt-oss','green harmonic',
               'hangzhou seenpin',"investors' chronicle",'jds uniphase','jeff dean',
               'jpmorgan fremont tour','kavukcuoglu','kingpin','koeda','kwhiy','le pen','lescure',
               'llama-4','meta vr glasses','metronome','mirle','munee','nemotron 3.5 lightning',
               'noetra corp','nvidia nemotron','nvidia nemotron 3 ultra','nvidia ports',
               'nvidia rubin','openai devday','openai enterprise signals',
               'openai signals individual','oracle rpo','payai','pentagon list','phonearena',
               'privy','quanta services','quoc le','qwen 3.8 max','qwen 4','ray-ban meta',
               'riksbank',
 ],
 'STORM': [
               'restart','cheniere','edouard','isaias','port arthur','landfall','golden pass',
               'sabine pass','alliance refinery','marine minerals administration','motiva',
               'pascagoula','wdsu','weather channel','wlox',
 ],
 'AIRLINES': [
               'etihad','ual','united','graham act','jet fuel','dal','gaca','rezaei',
               'ual skip rule','airline fuel','fuel cost','hijack',"sana'a airport",'ual pick',
               '27 iranian airlines','abha airport','air india','ajet','bastian','channel 12',
               'china eastern 5735','cirium','dammam','egyptair 990','emirates','flightradar24',
               'flydubai fz1073','germanwings','indigo','king fahd airport',
               'king khalid international airport','kuwait airways','mahan air','pegasus',
               'qatar airways','tabuk','terminal 3','terminal 4','turkish airlines','us mission',
 ],
 'PORTFOLIO': [
               'fidelity','lot','lot 1','lot 2','call buyback','assignment','limit order','fill',
               'filled','stop','stopped out','745 put','745p','dec-18','leaps','theta bill',
               'paper trade','actual trade','flag trade','flag_trades','shares','sh','avg cost',
               'cost basis','p&l','pnl','gross','net','open position','closed','time stop',
               'disconfirmer exit','bracket','+3%','-3%','target first','stop first','47/46',
               'baseline','spy put','kre puts','bno puts','mu puts','parr','dht','crwv','tsm',
               'stop loss','parr covered call',
 ],
 'VAULT-OPS': [
               'window error','demand-destruction','reuters','oil-value-chain','axios','zerohedge',
               'artifact test','error class 8','paywalled','map gap','windward',
               'instrument mismatch','ukmto','who gains if believed','claude code',
               'interested party','rule 19','mainstreaming','war-confirmed','fable 5',
               'sonnet subagent','zacks','crosscheck.py','deepseek v4 flash','opus 5',
               'source grade','windward daily','js-rendered','librarian.py','satire','tier-1 agent',
               't3 source','cache read','gpt-5.6 luna','opis','step zero break','token arbitrage',
               'soma holdings file','stockanalysis.com','tools/cite.py','zerohedge hormuz piece',
               'gopher','other tool','kobeissi','daily brief','daily market brief','holdings scan',
               'scan zh','flag sweep','mim','money in the morning','menu','money board',
               'flag board','librarian','thread arc','crosscheck','vault_amend','timeline',
               'chat-log','scoreboard','grades','marks','120-day','rule 16d','rule 16e','rule 16f',
               'rule 21','rule 21b','rule 21c','rule 22','rule 22c','class 8','error class',
               'step zero','republish trap','republish date','source time','paste time',
               'verified clock','quote-header','reconcile','supersede','extends','amend','firewall',
               'evidence ladder','perimeter','who gains','vendor conflict','bloomberg','cnbc',
               'politico','wsj','ft','the information','seeking alpha','stocktwits','kpler',
               'vortexa',"lloyd's list",'tankertrackers','argus','platts','rystad','energy aspects',
               'jefferies','barclays','goldman','goldman sachs','jpmorgan','morgan stanley','citi',
               'ubs','factset','lseg','refinitiv','haver','fred','stooq','google news',
               'yahoo finance','perimeters of a deal','liability angle','beta mismatch',
               'seem bananas','market intelligence',"where's the money",'usually reliable',
               'price deviations','tranche plan','opinions move stocks','us open scan',
               'top overnight news','at the open','9pm fetch','grok list','stretchy demand',
               'co-signers','rotation thesis','it was the intention',"where there's a will",
               'probably the most related',
 ],
}
ROUTE_NEW = {
 'REFINING': 'oil-value-chain / demand-destruction / war/war-board',
 'MARITIME': 'war/war-board / demand-destruction / oil-value-chain / war/war-confirmed',
 'RED-SEA': 'war/war-board / war/war-confirmed / demand-destruction',
 'RUSSIA-UA': 'war/war-board / oil-value-chain / demand-destruction',
 'IRAN-POL': 'war/war-board / war/war-rhetoric',
 'CHINA': 'compression-thesis / demand-destruction / war/war-board / buildout-bottleneck-map / new-economy-regime',
 'VENEZUELA': 'oil-value-chain',
 'FISCAL': 'rates-board / new-economy-regime',
 'INFLATION': 'rates-board / new-economy-regime / demand-destruction',
 'BREADTH': 'market-fragility / rotation-stickiness / dip-buying-base-rates / concentration / weekly-momentum',
 'EARNINGS': 'earnings-implied-cepi / compression-thesis / rotation-stickiness / memory-regime-question',
 'US-POLITICS': 'new-economy-regime / war/war-board / demand-destruction',
 'CREDIT': 'ai-financing-fragility / hyperscaler-credit / balance-sheet-board / financing-fragility-gauge / insurance-pe-channel',
 'NEOCLOUD': 'metered-compute / ai-financing-fragility / hyperscaler-credit / compression-thesis / buildout-bottleneck-map',
 'GRID': 'buildout-bottleneck-map / chips-mw-framework / power-not-petroleum / power-scarcity-equities / mw-dollar',
 'NUCLEAR': 'nuclear / buildout-bottleneck-map / power-not-petroleum',
 'AI-SAFETY': 'danger-disclosure-playbook / compression-thesis / ai-evaluation-framework',
 'AI-ADOPTION': 'compression-thesis / metered-compute / buildout-bottleneck-map / physical-ai-hardware-stack',
 'STORM': 'oil-value-chain / war/war-board / demand-destruction',
 'AIRLINES': 'war/war-board / oil-value-chain',
 'PORTFOLIO': 'portfolio-state / money-board / flag-board / _scorecard',
 'VAULT-OPS': '_calibration / data-sourcing-playbook / money-board / grades / _persona / _learning / _scorecard / _reconcile-ledger',
}
ROUTE_ADD = {
}
for _k in THREADS_ADD:
    THREADS[_k] = THREADS.get(_k, []) + THREADS_ADD[_k]
for _k in THREADS_NEW:
    THREADS[_k] = THREADS.get(_k, []) + THREADS_NEW[_k]
for _k in ROUTE_NEW:
    ROUTE[_k] = ROUTE_NEW[_k]
for _k in ROUTE_ADD:
    ROUTE[_k] = ROUTE.get(_k, '') + ' / ' + ROUTE_ADD[_k]
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
