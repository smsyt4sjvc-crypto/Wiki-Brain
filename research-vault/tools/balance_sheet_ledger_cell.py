#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════════════════════════════
#  THE SHEETS LEDGER — Jake's spec 2026-08-10: "an explicit mag7 + Oracle, SpaceX,
#  Broadcom and hyperscaler financial branch. We need to know exactly what their sheets
#  are, how they're evolving… Start in 2023."
#
#  Pulls SEC EDGAR XBRL companyfacts (free, no key) for the 10-name AI-complex universe
#  and prints each company's BALANCE-SHEET evolution, quarterly, 2023 → latest filed:
#     cash & equivalents · short-term investments · long-term marketable securities ·
#     total debt (LT + current + CP + ST borrowings) · NET (narrow & broad) ·
#     operating-lease liability · finance-lease liability · stockholders' equity
#  plus Δ-since-2023 per name and a latest-quarter complex aggregate.
#
#  SCOPE, deliberate: INSTANT (point-in-time) concepts only — robust across filers.
#  FLOWS (OCF, capex, the self-funding ratios) live in cepi_tracker_cell.py. OFF-SHEET
#  items that only exist in text notes (purchase commitments, SPVs, RVGs) and MARKET
#  items (CDS, bond spreads) are CURATED on wiki/balance-sheet-board.md — this cell
#  prints the XBRL purchase-obligation tags where a filer provides them, and says so
#  when it doesn't. COMPLETE CELL — paste whole into Colab and run.
# ═══════════════════════════════════════════════════════════════════════════════════════
import json, time, urllib.request

UA = {"User-Agent": "Jake Research vault@example.com"}
NAMES = ["MSFT", "GOOGL", "AMZN", "META", "NVDA", "AAPL", "TSLA", "ORCL", "AVGO", "SPCX"]
SINCE = "2022-12-01"          # first 2023-adjacent quarter-end kept

CONCEPTS = {                   # concept -> candidate us-gaap tags, first with data wins per date
 "cash":  ["CashAndCashEquivalentsAtCarryingValue"],
 "sti":   ["ShortTermInvestments", "MarketableSecuritiesCurrent",
           "AvailableForSaleSecuritiesDebtSecuritiesCurrent", "MarketableSecurities",
           "DebtSecuritiesAvailableForSaleCurrent",
           "DebtSecuritiesAvailableForSaleExcludingAccruedInterestCurrent",
           "DebtSecuritiesCurrent"],
 "lti":   ["MarketableSecuritiesNoncurrent", "AvailableForSaleSecuritiesDebtSecuritiesNoncurrent",
           "LongTermInvestments"],
 "ltd_nc":["LongTermDebtNoncurrent", "NotesPayableNoncurrent", "LongTermNotesPayable",
           "SeniorLongTermNotes", "LongTermDebtAndCapitalLeaseObligations"],
 "ltd_c": ["LongTermDebtCurrent", "NotesPayableCurrent", "LongTermDebtAndCapitalLeaseObligationsCurrent"],
 "ltd":   ["LongTermDebt"],
 "cp":    ["CommercialPaper"],
 "stb":   ["ShortTermBorrowings", "OtherShortTermBorrowings"],
 "oplease":["OperatingLeaseLiability"],
 "oplease_c":["OperatingLeaseLiabilityCurrent"], "oplease_nc":["OperatingLeaseLiabilityNoncurrent"],
 "finlease":["FinanceLeaseLiability"],
 "finlease_c":["FinanceLeaseLiabilityCurrent"], "finlease_nc":["FinanceLeaseLiabilityNoncurrent"],
 "equity":["StockholdersEquity",
           "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"],
 "purch": ["UnrecordedUnconditionalPurchaseObligationBalanceSheetAmount",
           "UnconditionalPurchaseObligation"],
 "stakes":["EquitySecuritiesWithoutReadilyDeterminableFairValueAmount"],
 "stakes2":["EquitySecuritiesFvNi"],
}

def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    return json.loads(urllib.request.urlopen(req, timeout=60).read())

def series(facts, tags):
    """{end_date: value} from 10-Q/10-K instant facts, latest-filed wins."""
    out = {}
    for tag in tags:
        node = facts.get(tag)
        if not node: continue
        for unit, pts in node.get("units", {}).items():
            if unit != "USD": continue
            for p in pts:
                end, val, form = p.get("end"), p.get("val"), p.get("form", "")
                if not end or val is None or end < SINCE: continue
                if form not in ("10-Q", "10-K", "10-Q/A", "10-K/A", "20-F"): continue
                key = (end, tag)
                prev = out.get(key)
                if prev is None or p.get("filed", "") >= prev[1]:
                    out[key] = (val, p.get("filed", ""))
    # merge candidates per END DATE, earlier-listed tag wins where both have the date
    # (v1.1 fix: first-tag-wins broke NVDA/ORCL/AVGO when filers switched tags mid-series)
    merged = {}
    for tag in tags:
        for (end, t), (val, _) in out.items():
            if t == tag and end not in merged:
                merged[end] = val
    return merged

print("═" * 100)
print("  THE SHEETS LEDGER — AI-complex balance sheets, quarterly, 2023 → latest filed (EDGAR XBRL)")
print("  All figures $B. NET(narrow)=cash+STI−debt · NET(broad)=+LT marketable securities.")
print("═" * 100)

tickmap = {}
try:
    tk = fetch("https://www.sec.gov/files/company_tickers.json")
    for _, row in tk.items():
        tickmap[row["ticker"].upper()] = f'{row["cik_str"]:010d}'
except Exception as e:
    print(f"  !! ticker map failed: {e}")

agg, agg_asof = {}, {}
for name in NAMES:
    cik = tickmap.get(name)
    print(f'\n── {name} ' + '─' * (96 - len(name)))
    if not cik:
        print(f"   NOT FOUND in EDGAR ticker file — no filings under this ticker yet. "
              f"(SPCX: if newly listed, facts may lag; check again after its first 10-Q.)")
        continue
    try:
        d = fetch(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json")
    except Exception as e:
        print(f"   !! fetch failed: {e}"); continue
    facts = d.get("facts", {}).get("us-gaap", {})
    if not facts:
        print("   no us-gaap facts (foreign/newly-listed filer)."); continue
    S = {c: series(facts, tags) for c, tags in CONCEPTS.items()}
    if not S["oplease"]:
        S["oplease"] = {e: S["oplease_c"].get(e, 0) + S["oplease_nc"].get(e, 0)
                        for e in set(S["oplease_c"]) | set(S["oplease_nc"])}
    if not S["finlease"]:
        S["finlease"] = {e: S["finlease_c"].get(e, 0) + S["finlease_nc"].get(e, 0)
                        for e in set(S["finlease_c"]) | set(S["finlease_nc"])}
    ends = sorted(set(S["cash"]) | set(S["ltd"]) | set(S["ltd_nc"]) | set(S["equity"]))
    if not ends:
        print("   no instant balance-sheet facts ≥ 2023."); continue
    print(f'   {"end":<12}{"cash":>8}{"+STI":>8}{"+LTI":>8}{"debt":>8}{"NETnar":>9}{"NETbrd":>9}'
          f'{"opLease":>9}{"finLease":>9}{"equity":>9}')
    B = 1e9; rows = {}
    for e in ends:
        cash = S["cash"].get(e); sti = S["sti"].get(e, 0); lti = S["lti"].get(e, 0)
        if S["ltd_nc"].get(e) is not None or S["ltd_c"].get(e) is not None:
            debt = S["ltd_nc"].get(e, 0) + S["ltd_c"].get(e, 0)
        else:
            debt = S["ltd"].get(e, 0)
        debt += S["cp"].get(e, 0) + S["stb"].get(e, 0)
        if cash is None and debt == 0: continue
        cash = cash or 0
        nn = cash + sti - debt; nb = nn + lti
        rows[e] = (cash, sti, lti, debt, nn, nb)
        print(f'   {e:<12}{cash/B:>8.1f}{sti/B:>8.1f}{lti/B:>8.1f}{debt/B:>8.1f}{nn/B:>+9.1f}'
              f'{nb/B:>+9.1f}{S["oplease"].get(e,0)/B:>9.1f}{S["finlease"].get(e,0)/B:>9.1f}'
              f'{S["equity"].get(e,0)/B:>9.1f}')
    if rows:
        first, last = min(rows), max(rows)
        f0, f1 = rows[first], rows[last]
        print(f'   Δ {first} → {last}:  cash+STI {(f0[0]+f0[1])/B:,.0f} → {(f1[0]+f1[1])/B:,.0f}  ·  '
              f'debt {f0[3]/B:,.0f} → {f1[3]/B:,.0f}  ·  NET(narrow) {f0[4]/B:+,.0f} → {f1[4]/B:+,.0f}  ·  '
              f'opLease {S["oplease"].get(first,0)/B:,.0f} → {S["oplease"].get(last,0)/B:,.0f}  ·  '
              f'finLease {S["finlease"].get(first,0)/B:,.0f} → {S["finlease"].get(last,0)/B:,.0f}')
        agg[name] = f1; agg_asof[name] = last
    stk = {e: S["stakes"].get(e, 0) + S["stakes2"].get(e, 0)
           for e in set(S["stakes"]) | set(S["stakes2"])}
    if stk:
        s_last = max(stk)
        print(f'   EQUITY-STAKE BOOK (non-marketable + FVNI equity securities): {stk[s_last]/1e9:,.1f}B @ {s_last}'
              f'   <- the vendor-equity leg; NOT in NET above')
    if S["purch"]:
        p_last = max(S["purch"]); print(f'   XBRL purchase-obligation tag: {S["purch"][p_last]/B:,.1f}B @ {p_last}')
    else:
        print("   purchase commitments: NOT in XBRL for this filer — text-note item, curated on the board.")
    time.sleep(0.3)                        # EDGAR rate courtesy

print("\n" + "═" * 100)
print("  COMPLEX AGGREGATE — latest filed quarter per name (⚠️ MIXED fiscal ends; as-of dates differ):")
B = 1e9
for k in agg: print(f'    {k:<6} as of {agg_asof[k]}   NET(narrow) {agg[k][4]/B:>+9.1f}B   debt {agg[k][3]/B:>8.1f}B')
if agg:
    tn = sum(v[4] for v in agg.values()); td = sum(v[3] for v in agg.values())
    print(f'    {"SUM":<6} {"(mixed dates)":<19} NET(narrow) {tn/B:>+9.1f}B   debt {td/B:>8.1f}B')
print("─" * 100)
print("  CAVEATS: instant concepts only (flows/self-funding = cepi_tracker_cell.py). Fiscal ends differ")
print("  (AAPL Sep · MSFT Jun · NVDA Jan · AVGO Oct/Nov · ORCL May — never compare rows across names by")
print("  date without checking). NET excludes equity stakes (GOOGL's Anthropic mark etc. are NOT cash).")
print("  Off-sheet purchase commitments, SPVs, RVGs, CDS and bond spreads: wiki/balance-sheet-board.md.")
print("═" * 100)
