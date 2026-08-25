#!/usr/bin/env python3
"""
CROSSCHECK — the gate on MY OWN OUTPUT, not on Jake's inbound.

Jake, 2026-08-11: "The vault is supposed to remember things better than I can."
It does. Four times today it held the answer and I did not consult it:
   1. Hormuz vessel     — war-confirmed had the blockade record since 7/26
   2. FRED probe        — canonical IDs failing meant transport, not naming
   3. F19               — shell-vs-fit-out run on data centres, never on fabs
   4. META FCF          — vault said "~ZERO" on 7/30; my fresh pull said +13.2B

THE DIAGNOSIS: librarian.py gates the DOOR (what Jake pastes in). Nothing gated the
WINDOW (numbers I generate myself). Every one of the four was my own work product
contradicting something already on disk.

USAGE — pipe a data pull straight in, or pass a claim:
    python3 tools/edgar_batch_cell.py | python3 tools/crosscheck.py
    python3 tools/crosscheck.py --claim "META FCF +13.2B"
    python3 tools/crosscheck.py --claim "fab construction -58%"

It extracts (TICKER-or-TERM, number) pairs, finds vault lines mentioning the same
subject with a DIFFERENT number, and prints them newest-first. It does not decide —
it surfaces the disagreement. A disagreement is the cheapest bug detector available.
"""
import re, sys, subprocess, argparse, pathlib

WIKI = pathlib.Path(__file__).resolve().parent.parent / "wiki"

# Tickers and multi-word subjects worth cross-checking. Extend freely.
TICKERS = set("""MSFT GOOGL AMZN META NVDA AAPL TSLA ORCL AVGO TSM MU AMD INTC DELL KLAC
LRCX AMAT MRVL TXN ADI NXPI MPWR QCOM TER ALAB MCHP CRDO ASML ASX MTSI CRWV NBIS IREN
APLD WULF CORZ SPCX COHR LITE MP SWKS ARM GFS QRVO RNW RIVN EWY SPY QQQ IWM SOXX SMH""".split())
SUBJECTS = ["fab construction", "data centre", "data center", "brent", "wti", "gold",
            # gap found 8/11: the tool could not check its own headline index. Subjects must
            # cover the vault's named INSTRUMENTS, not just tickers.
            "sdllmtk", "sdllmcs", "sdllmos", "token price", "tokens", "openrouter",
            "gpu rental", "swaption", "payer skew", "repo",
            "hormuz", "payroll", "cpi", "vix", "electric", "office",
            # gap #3, found 8/12 on the Drive-folder ingest: the tool had NO vocabulary for
            # the macro spine or for any calendar/seasonality claim, so two headline findings
            # scanned as "nothing to check". Absence of vocabulary is not absence of prior.
            "balance sheet", "walcl", "m2", "money supply", "liquidity", "reserves",
            "s&p", "spx", "nasdaq", "ndx", "soxx", "index",
            "day-1", "day 1", "first of month", "seasonal", "turn of the month",
            "straddle", "breakeven", "win rate", "drawdown", "52-week high", "52w high",
            "layoff", "mean reversion", "half-life", "hurst", "autocorr",
            "bollinger", "compression", "squeeze", "kre", "regional bank",
            # gap #4, 8/12: the pre-earnings study had no vocabulary either.
            "earnings", "pre-earnings", "alpha", "drift", "suppress", "sma", "20-sma",
            "base rate", "t-stat", "significance", "iv", "implied vol", "realised vol",
            # gap #5, 8/12: the CONTENT-TOLL inbound had no vocabulary either — the whole
            # crawler/publisher/search-traffic axis was invisible to the self-check.
            "google zero", "zero click", "ai overview", "crawler", "googlebot", "publisher",
            "search traffic", "referral", "content licensing", "training data", "cloudflare",
            "net", "pay per crawl"]

NUM = re.compile(r"[-+]?\$?\d[\d,]*\.?\d*\s*(?:%|B\b|bn\b|billion|M\b|bp\b)?")
# Dates masquerade as numbers: "2026-08-11" and "Jun-26" both scan as values and the first
# test surfaced a vault value of "2026" for every dated entry. Strip them before scanning.
DATEISH = re.compile(r"\b(19|20)\d{2}[-/]\d{1,2}([-/]\d{1,2})?\b|"
                     r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[-\s]?\d{2,4}\b|"
                     r"\b(19|20)\d{2}\b|\bL\d{2,5}\b|\b\d{1,2}/\d{1,2}\b", re.I)
def strip_dates(t):
    return DATEISH.sub(" ", t)

def to_float(tok):
    t = tok.strip().lstrip("$").replace(",", "")
    mult = 1.0
    if re.search(r"(B\b|bn\b|billion)", t, re.I): mult = 1.0
    m = re.match(r"([-+]?\d*\.?\d+)", t)
    return float(m.group(1)) * mult if m else None

def extract(text):
    """(subject, value, context) triples from arbitrary text."""
    out = []
    for line in text.splitlines():
        subs = [t for t in TICKERS if re.search(rf"\b{re.escape(t)}\b", line)]
        subs += [s for s in SUBJECTS if s.lower() in line.lower()]
        if not subs:
            continue
        for m in NUM.finditer(strip_dates(line)):
            v = to_float(m.group())
            if v is None or abs(v) < 0.01 or abs(v) > 1e7:
                continue
            for s in subs:
                out.append((s, v, line.strip()[:110]))
    return out

# v2: matching on ENTITY ALONE produced pure noise on the first real test — it surfaced
# RVOL readings and unrelated percentages for META and MISSED the one line that mattered
# ("META'S FCF IS ~ZERO"). A number near a ticker is not a claim about the same thing.
# The metric must gate the search.
METRIC_SYNONYMS = {
    "fcf":          ["fcf", "free cash flow", "operating cash flow", "ocf", "cash flow"],
    "capex":        ["capex", "capital expenditure", "capital spending", "ocf"],
    "revenue":      ["revenue", "sales", "topline", "top line"],
    "construction": ["construction", "put in place", "saar"],
    "cds":          ["cds", "spread", "basis point", "bp"],
    "yield":        ["yield", "auction", "bid to cover", "tail"],
    "price":        ["close", "closed", "settled", "spot", "print"],
    "margin":       ["margin", "gross margin", "operating margin"],
    "employment":   ["payroll", "employment", "jobs", "revision"],
}
def metric_terms(text):
    """Metric vocabulary implied by the claim. Empty ⇒ caller falls back to entity-only."""
    low = text.lower()
    terms = []
    for key, syns in METRIC_SYNONYMS.items():
        if key in low or any(s in low for s in syns):
            terms += syns
    return sorted(set(terms))

def vault_lines(subject, metrics):
    """Vault lines mentioning BOTH the subject and a metric term. Metric gating is the
    difference between a read list and noise."""
    try:
        r = subprocess.run(["grep", "-rn", "--include=*.md", "-i", subject, str(WIKI)],
                           capture_output=True, text=True, timeout=60)
    except Exception:
        return []
    out = []
    for l in r.stdout.splitlines():
        body = l.split(":", 2)[-1].lower()
        if not NUM.search(body):
            continue
        if metrics and not any(m in body for m in metrics):
            continue
        out.append(l)
    return out

DATE_IN_LINE = re.compile(r"\b(20\d{2})-(\d{2})-(\d{2})\b")
def _recency(line):
    """Sort key: newest DATED entry first. Ranking by size-of-difference (v2) buried the
    line that mattered under extreme unrelated values — a read list wants recency, and
    curated markers (star / stop) outrank plain mentions at the same date."""
    m = DATE_IN_LINE.search(line)
    d = int(m.group(1) + m.group(2) + m.group(3)) if m else 0
    curated = 1 if ("\u2605" in line or "\u26d4" in line) else 0
    return (d, curated)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--claim", help="a single claim to check, e.g. 'META FCF +13.2B'")
    ap.add_argument("--tol", type=float, default=0.15,
                    help="relative difference that counts as a conflict (default 0.15)")
    ap.add_argument("--max", type=int, default=5, help="vault lines shown per conflict")
    a = ap.parse_args()

    text = a.claim if a.claim else sys.stdin.read()
    METRICS = metric_terms(text)
    claims = extract(text)
    if not claims:
        # ⛔ 8/12: "nothing to check" was rendering TWO OPPOSITE conditions identically —
        # exactly the failure that made the FRED probe show 404 and timeout as the same ✗.
        # A claim with numbers but no SUBJECT vocabulary is a GAP IN THIS FILE, not a clean pass.
        has_num = bool(NUM.search(strip_dates(text)))
        if has_num:
            print("  ⛔ crosscheck: THE TEXT HAS NUMBERS BUT NO SUBJECT THIS FILE KNOWS.")
            print("     That is a VOCABULARY GAP in crosscheck.py, NOT a clean bill of health —")
            print("     the vault was never searched. Add the subject to TICKERS/SUBJECTS above and")
            print("     re-run, or check by hand:  python3 tools/vault_find.py \"<subject>\"")
        else:
            print("  crosscheck: no numbers in the text — nothing to check.")
        return

    seen, conflicts = set(), 0
    print("=" * 92)
    print("  CROSSCHECK — my numbers vs what the vault already says")
    print(f"  metric gate: {', '.join(METRICS[:8]) if METRICS else 'NONE (entity-only — expect noise)'}")
    print("=" * 92)
    for subj, val, ctx in claims:
        key = (subj, round(val, 2))
        if key in seen:
            continue
        seen.add(key)
        hits = vault_lines(subj, METRICS)
        clash = []
        for h in hits:
            for m in NUM.finditer(strip_dates(h.split(":", 2)[-1])):
                v2 = to_float(m.group())
                if v2 is None or abs(v2) < 0.01:
                    continue
                denom = max(abs(val), abs(v2))
                if denom and abs(val - v2) / denom > a.tol and abs(val - v2) / denom < 50:
                    clash.append((_recency(h), v2, h))
                    break
        if not clash:
            continue
        clash.sort(key=lambda x: x[0], reverse=True)
        conflicts += 1
        print(f"\n  ⚠️  {subj}  — my value {val:g}")
        print(f"      from: {ctx}")
        for _, v2, h in clash[:a.max]:
            f, ln, body = h.split(":", 2)
            print(f"      vault {v2:>10g}  {pathlib.Path(f).name}:{ln}")
            print(f"                    {body.strip()[:96]}")
    print("\n" + "=" * 92)
    if conflicts:
        print(f"  {conflicts} subject(s) where the vault holds a materially different number.")
        print("  THIS IS NOT AN ERROR LIST — it is a READ LIST. Open the entries. A disagreement is")
        print("  usually a different period, a different definition, or a stale line — and sometimes")
        print("  it is your fresh pull being wrong, which is what happened to META on 8/11.")
    else:
        print("  No material conflicts found. That is weak evidence, not a clean bill:")
        print("  the vault may simply have no prior number for these subjects.")
    print("=" * 92)

if __name__ == "__main__":
    main()
