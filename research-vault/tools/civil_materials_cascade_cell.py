# ============================================================================
#  THE CIVIL CASCADE — is the data-centre buildout visible in BUILDING-MATERIAL
#  prices, or is that a story?    (Jake's claim, 2026-07-31)
#
#  THE CLAIM: data-centre construction is inflationary through concrete, lumber
#  and landscaping — not only through transformers and electricity.
#
#  READ THIS BEFORE THE OUTPUT — the test is a DIVERGENCE, not a level.
#
#  Everything in construction rises together in a normal cycle, so "cement is up"
#  proves nothing. The civil-cascade story makes a SHARPER prediction:
#
#     CEMENT / READY-MIX / AGGREGATE  should run HOT
#     LUMBER                          should run FLAT-to-COOL
#
#  Because ready-mix has a ~90-minute delivery radius and CANNOT be arbitraged
#  into a booming county, while lumber is a continental market priced by HOUSING
#  starts and mill capacity — and housing is not the thing booming.
#
#     both hot  -> a general construction cycle; the data-centre attribution is unearned
#     both flat -> the whole leg is a story
#     cement hot + lumber flat -> the claim survives its first real test
#
#  CONTROLS
#   [A] HOUSING STARTS — the alternative explanation for any materials move.
#       If starts explain cement, data centres are not needed as a cause.
#   [B] The ELECTRICAL stack (electrical equipment PPI) — the vault's already-
#       mapped cascade. It is the POSITIVE control: if data-centre demand moves
#       materials at all, it must show here. If electrical is flat too, the
#       buildout is not moving PPI anywhere and the whole thesis is in doubt.
#   [C] Everything indexed to a common base date so LEVELS are comparable, and
#       shown as YoY so the CYCLE is visible. No conclusions from one series.
# ============================================================================
import io, urllib.request
import pandas as pd, numpy as np

FRED = 'https://fred.stlouisfed.org/graph/fredgraph.csv?id={}'
SERIES = {
    # --- the CIVIL stack (the claim) ---
    'WPU1322':        'Concrete products PPI',
    'WPU1321':        'Cement PPI',
    'WPU1321011':     'Portland cement PPI',
    'PCU212312123':   'Crushed stone / aggregate PPI',
    'WPU081':         'Lumber PPI',
    'WPU0811':        'Softwood lumber PPI',
    # --- the ELECTRICAL stack (positive control, vault-mapped) ---
    'WPU1174':        'Electrical equipment PPI',
    'WPU10170502':    'Steel mill products PPI',
    # --- the alternative explanation ---
    'HOUST':          'Housing starts',
    'TTLCONS':        'Total construction spend',
    # --- reference ---
    'PPIACO':         'PPI all commodities',
    'CPIAUCSL':       'CPI headline',
}
BASE = '2023-01-01'

def fred(sid):
    raw = urllib.request.urlopen(FRED.format(sid), timeout=30).read().decode()
    d = pd.read_csv(io.StringIO(raw)); d.columns = ['date', sid]
    d['date'] = pd.to_datetime(d['date'])
    d[sid] = pd.to_numeric(d[sid], errors='coerce')
    return d.dropna().set_index('date')[sid]

print('pulling FRED ...')
data = {}
for sid, lab in SERIES.items():
    try:
        data[lab] = fred(sid)
    except Exception as e:
        print(f'  {lab:<32} unavailable ({type(e).__name__}) — id {sid}')
if not data:
    raise SystemExit('no series returned')
df = pd.DataFrame(data).sort_index()

print('\n' + '=' * 92)
print(f'  LEVELS, indexed to 100 at {BASE}   (last obs per series shown)')
print('=' * 92)
print(f'  {"series":<32}{"latest":>10}{"as of":>12}{"idx vs base":>13}{"YoY":>9}{"3m ann":>9}')
sub = df[df.index >= BASE]
for lab in df.columns:
    s = df[lab].dropna()
    if s.empty: continue
    b = s[s.index >= BASE]
    if b.empty: continue
    base_val = b.iloc[0]
    idx = s.iloc[-1] / base_val * 100
    yoy = (s.iloc[-1] / s[s.index <= s.index[-1] - pd.DateOffset(years=1)].iloc[-1] - 1) * 100 \
          if len(s[s.index <= s.index[-1] - pd.DateOffset(years=1)]) else np.nan
    m3 = ((s.iloc[-1] / s.iloc[-4]) ** 4 - 1) * 100 if len(s) > 4 else np.nan
    print(f'  {lab:<32}{s.iloc[-1]:>10,.1f}{str(s.index[-1].date()):>12}{idx:>13.1f}'
          f'{yoy:>+8.1f}%{m3:>+8.1f}%')

print('\n' + '=' * 92)
print('  *** THE TEST: CIVIL vs LUMBER — the divergence IS the claim ***')
print('=' * 92)
civil = [c for c in ('Concrete products PPI','Cement PPI','Portland cement PPI',
                     'Crushed stone / aggregate PPI') if c in df.columns]
lum   = [c for c in ('Lumber PPI','Softwood lumber PPI') if c in df.columns]
elec  = [c for c in ('Electrical equipment PPI','Steel mill products PPI') if c in df.columns]

def grp_yoy(cols):
    vals = []
    for c in cols:
        s = df[c].dropna()
        prior = s[s.index <= s.index[-1] - pd.DateOffset(years=1)]
        if len(prior): vals.append((s.iloc[-1] / prior.iloc[-1] - 1) * 100)
    return np.mean(vals) if vals else np.nan

cy, ly, ey = grp_yoy(civil), grp_yoy(lum), grp_yoy(elec)
ref = grp_yoy(['PPI all commodities']) if 'PPI all commodities' in df.columns else np.nan
print(f'  {"CIVIL (cement/concrete/aggregate)":<40}{cy:>+8.1f}% YoY   [{len(civil)} series]')
print(f'  {"LUMBER":<40}{ly:>+8.1f}% YoY   [{len(lum)} series]')
print(f'  {"ELECTRICAL (positive control)":<40}{ey:>+8.1f}% YoY   [{len(elec)} series]')
print(f'  {"PPI all commodities (reference)":<40}{ref:>+8.1f}% YoY')
print(f'\n  CIVIL minus LUMBER spread: {cy-ly:>+.1f}pp')
print('  VERDICT KEY:')
print('    civil hot + lumber flat  -> claim SURVIVES (captive-local-supply story holds)')
print('    both hot                 -> general construction cycle; attribution UNEARNED')
print('    both flat                -> the leg is a story')
print('    electrical flat too      -> buildout is not moving PPI anywhere; doubt the whole thesis')

print('\n' + '=' * 92)
print('  [A] CONTROL — does HOUSING explain the civil move without data centres?')
print('=' * 92)
if 'Housing starts' in df.columns:
    h = df['Housing starts'].dropna()
    prior = h[h.index <= h.index[-1] - pd.DateOffset(years=1)]
    hy = (h.iloc[-1]/prior.iloc[-1]-1)*100 if len(prior) else np.nan
    print(f'  Housing starts {h.iloc[-1]:,.0f}k  ({h.index[-1].date()})   YoY {hy:+.1f}%')
    print(f'  Civil PPI YoY {cy:+.1f}% against housing starts {hy:+.1f}%.')
    print('  ** If starts are FLAT-to-DOWN while civil PPI is UP, housing does NOT explain it,')
    print('     and a non-residential source of concrete demand is required. That is the test. **')
    for c in civil:
        s = df[c].dropna().resample('MS').last().pct_change(12).dropna()*100
        hh = h.resample('MS').last().pct_change(12).dropna()*100
        j = pd.concat([s, hh], axis=1).dropna()
        if len(j) > 24:
            print(f'    corr(YoY {c[:28]:<28}, YoY starts) over {len(j)} months = {j.corr().iloc[0,1]:+.2f}')
if 'Total construction spend' in df.columns:
    t = df['Total construction spend'].dropna()
    pr = t[t.index <= t.index[-1] - pd.DateOffset(years=1)]
    print(f'  Total construction spend YoY {(t.iloc[-1]/pr.iloc[-1]-1)*100:+.1f}%' if len(pr) else '')

print('\n' + '=' * 92)
print('  ⚠️  WHAT THIS CANNOT DO, STATED PLAINLY')
print('=' * 92)
print('  PPI is NATIONAL. The civil-cascade claim is that prices spike LOCALLY in counties')
print('  hosting builds, and that ready-mix CANNOT be arbitraged between counties. A national')
print('  index AVERAGES exactly the dispersion the claim is about, so it is a WEAK test that')
print('  can only DISCONFIRM cheaply, never confirm strongly. A hot national print is real')
print('  evidence; a flat one is consistent with a large local effect that averages away.')
print('  The right instrument would be metro-level materials series or regional Fed district')
print('  construction surveys — neither is free on FRED. Read this as a screen, not a verdict.')
print('=' * 92)
