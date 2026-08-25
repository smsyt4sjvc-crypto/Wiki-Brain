# S&P 500: What time of day is the intraday low on RED days?
# Paste into a Google Colab cell and run.
#
# Idea: On days the S&P 500 closes lower, when (morning / midday / afternoon)
# did the index most often hit its lowest price of the day?
#
# Notes / caveats:
#  - Yahoo only serves intraday history for a limited window. 60-minute bars
#    reach back ~2 years, so we use 60m bars (enough to tell morning from
#    afternoon). Finer bars (5m/15m) only go back ~60 days.
#  - "Red day" here = regular-session close below the prior day's close.

!pip -q install yfinance --upgrade

import yfinance as yf
import pandas as pd

TICKER     = "^GSPC"        # S&P 500 index. Use "SPY" if you prefer the ETF.
START      = "2025-10-01"   # "since October"
INTERVAL   = "60m"          # 60m reaches back far enough; 5m/15m only ~60 days
TZ         = "America/New_York"

# ---------------------------------------------------------------------------
# 1) Pull intraday (hourly) bars
# ---------------------------------------------------------------------------
intraday = yf.download(
    TICKER, start=START, interval=INTERVAL,
    auto_adjust=False, prepost=False, progress=False,
)
# Flatten yfinance's occasional MultiIndex columns
if isinstance(intraday.columns, pd.MultiIndex):
    intraday.columns = intraday.columns.get_level_values(0)

# Make sure timestamps are in market (Eastern) time
idx = intraday.index
intraday.index = idx.tz_convert(TZ) if idx.tz is not None else idx.tz_localize("UTC").tz_convert(TZ)

# Keep only the regular session 09:30–16:00
intraday = intraday.between_time("09:30", "16:00")
intraday["date"] = intraday.index.date

# ---------------------------------------------------------------------------
# 2) Pull daily bars to label red vs green days
# ---------------------------------------------------------------------------
daily = yf.download(TICKER, start=START, interval="1d",
                    auto_adjust=False, progress=False)
if isinstance(daily.columns, pd.MultiIndex):
    daily.columns = daily.columns.get_level_values(0)

daily["prev_close"] = daily["Close"].shift(1)
daily["red"] = daily["Close"] < daily["prev_close"]
red_dates = set(d.date() for d in daily.index[daily["red"].fillna(False)])

print(f"Days in sample: {len(daily)}   Red days: {len(red_dates)}")

# ---------------------------------------------------------------------------
# 3) For each red day, find the bar holding the day's lowest LOW
# ---------------------------------------------------------------------------
def bucket(ts):
    h, m = ts.hour, ts.minute
    t = h + m / 60.0
    if t < 11.5:   return "Morning (9:30-11:30)"
    if t < 14.0:   return "Midday (11:30-2:00)"
    return "Afternoon (2:00-4:00)"

rows = []
for day, grp in intraday.groupby("date"):
    if day not in red_dates:
        continue
    low_bar = grp.loc[grp["Low"].idxmin()]      # the bar that made the low
    ts = grp["Low"].idxmin()
    rows.append({
        "date": day,
        "low_time": ts.strftime("%H:%M"),
        "hour": ts.strftime("%H:00"),
        "bucket": bucket(ts),
        "low": round(float(low_bar["Low"]), 2),
    })

res = pd.DataFrame(rows).sort_values("date")
print(f"\nRed days with intraday data: {len(res)}\n")

# ---------------------------------------------------------------------------
# 4) Summaries
# ---------------------------------------------------------------------------
print("=== Intraday low by 3 buckets (red days) ===")
order = ["Morning (9:30-11:30)", "Midday (11:30-2:00)", "Afternoon (2:00-4:00)"]
counts = res["bucket"].value_counts().reindex(order).fillna(0).astype(int)
pct = (counts / counts.sum() * 100).round(1)
print(pd.DataFrame({"days": counts, "pct": pct}).to_string())

print("\n=== Intraday low by hour bar (red days) ===")
by_hour = res["hour"].value_counts().sort_index()
print(by_hour.to_string())

print("\n=== Per-day detail ===")
print(res.to_string(index=False))

# ---------------------------------------------------------------------------
# 5) Simple chart
# ---------------------------------------------------------------------------
import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(12, 4))
counts.plot(kind="bar", ax=ax[0], color="#c0392b")
ax[0].set_title("Intraday low timing on red days"); ax[0].set_ylabel("# of red days")
ax[0].tick_params(axis="x", rotation=20)
by_hour.plot(kind="bar", ax=ax[1], color="#34495e")
ax[1].set_title("Intraday low by hour"); ax[1].set_ylabel("# of red days")
plt.tight_layout(); plt.show()
