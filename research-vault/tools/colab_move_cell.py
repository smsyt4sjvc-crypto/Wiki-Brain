# =====================================================================
#  MOVE INDEX FETCHER  --  paste this whole cell into Colab and run it
# =====================================================================
#  WHY: every automated route to the MOVE index (ICE BofA Merrill Lynch
#  Option Volatility Estimate -- the Treasury market's VIX) is blocked
#  from a datacentre IP address. Yahoo returns HTTP 429 from both the
#  research container AND from GitHub Actions runners; CNBC returns 403;
#  Wall Street Journal returns 401; Nasdaq does not carry it; Stooq needs
#  JavaScript; and FRED's VXTYN substitute was discontinued in May 2020.
#
#  Colab runs on Google Cloud, which is ALSO a datacentre range -- so this
#  may well fail the same way. That is exactly what the cell is for: it
#  TESTS every route and tells you which, if any, got through.
#
#  If they all fail, the last section prints the manual fallback, which
#  works because your phone is a residential IP address and theirs is not.
# =====================================================================

import json
import urllib.request
from datetime import datetime, timezone

BROWSER_UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")


def _get(url, ua=BROWSER_UA, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": ua} if ua else {})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def try_yahoo(host):
    """Yahoo Finance chart endpoint. Needs a browser User-Agent; without one
    it returns HTTP 429 immediately."""
    url = (f"https://{host}.finance.yahoo.com/v8/finance/chart/"
           "%5EMOVE?range=5d&interval=1d")
    res = json.loads(_get(url))["chart"]["result"][0]
    stamps, closes = res["timestamp"], res["indicators"]["quote"][0]["close"]
    pairs = [(datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%d"), c)
             for t, c in zip(stamps, closes) if c is not None]
    if not pairs:
        raise ValueError("no closes returned")
    return pairs[-1]


def try_stooq():
    """Stooq daily CSV. Usually returns a JavaScript shell rather than data."""
    raw = _get("https://stooq.com/q/d/l/?s=%5Emove&i=d", ua=None).decode()
    if "<" in raw[:200]:
        raise ValueError("returned an HTML/JavaScript shell, not CSV")
    rows = [ln.split(",") for ln in raw.strip().splitlines()[1:] if ln]
    return rows[-1][0], float(rows[-1][4])


ROUTES = [
    ("Yahoo query1", lambda: try_yahoo("query1")),
    ("Yahoo query2", lambda: try_yahoo("query2")),
    ("Stooq CSV",    try_stooq),
]

print("Testing every known MOVE route from this Colab session\n" + "=" * 58)
winner = None
for name, fn in ROUTES:
    try:
        d, v = fn()
        print(f"  {name:<16} OK      {d}  MOVE = {float(v):.2f}")
        winner = winner or (d, float(v))
    except Exception as e:
        msg = str(e).split("\n")[0][:70]
        print(f"  {name:<16} FAILED  {type(e).__name__}: {msg}")

print("=" * 58)
if winner:
    d, v = winner
    print(f"\n✅ COLAB'S IP ADDRESS IS CLEAN. Paste this line back to Claude:\n")
    print(f"      MOVE {v:.2f} {d}\n")
    print("Because this worked, Colab can be the standing MOVE fetcher --")
    print("run this cell once a day and paste the line above.")
else:
    print("\n❌ EVERY ROUTE FAILED. Colab's IP address is blocked too,")
    print("   which confirms this is IP reputation and not a header problem.\n")
    print("   MANUAL FALLBACK -- takes about ten seconds on your phone:")
    print("   Open any of these and read the number, then paste it back")
    print("   to Claude in the form:   MOVE 73.40\n")
    print("     * finance.yahoo.com/quote/%5EMOVE")
    print("     * cnbc.com/quotes/.MOVE")
    print("     * investing.com  -> search 'MOVE index'\n")
    print("   Your phone is a residential IP address, which is precisely")
    print("   why it works where every datacentre route does not.")
