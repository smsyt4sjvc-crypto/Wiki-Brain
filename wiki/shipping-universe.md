# Shipping universe — the US-listed tickers by segment, and what each trades on

*Reference list, built 2026-10-04 ~9:05pm PT on Jake's ask ("Shipping tickers"). One idea: WHICH ticker expresses
WHICH freight market. Tape via `tools/tape.py` (Yahoo closes Fri 2026-10-02). The freight tickets with levels are in
[[money-board]] 10/4 9:00pm; the flag is [[flag-board]] TANKERS; the war context is [[war/war-board]].*

## DATA (observed — Fri 2026-10-02 close · 5d · 20d · 60d % · 20-day realized vol · $ average daily volume, 20d)
### Crude tankers — driver: VLCC/Suezmax spot rates (BWET); Hormuz/Red Sea incidents; OPEC+ volumes
| tk | name | close | 5d | 20d | 60d | rv20 | ADV $M | vault |
|---|---|---|---|---|---|---|---|---|
| DHT | DHT Holdings (VLCC) | 23.68 | +8.7 | +17.3 | +39.9 | 36 | 95 | BULL 1, flag fired 10/4 |
| FRO | Frontline (VLCC/Suezmax/LR2) | 52.74 | +10.5 | +16.1 | +44.3 | 38 | 201 | BULL 0.5 |
| INSW | International Seaways (mixed crude + product) | 115.81 | +9.6 | +13.3 | +39.6 | 33 | 87 | mentioned |
| TNK | Teekay Tankers (Suezmax/Aframax) | 103.10 | +9.6 | +12.3 | +48.8 | 31 | 49 | mentioned |
| NAT | Nordic American (Suezmax, low $/share) | 8.42 | +9.1 | +18.6 | +42.7 | 34 | 39 | mentioned once |
| CMBT | CMB.TECH (ex-Euronav; absorbed Golden Ocean 2025) | 19.85 | +4.4 | +6.1 | +33.0 | 29 | 21 | none |

### Product tankers — driver: clean freight (LR/MR rates); Russian diesel export cuts; refinery outages; the diesel crack
| tk | name | close | 5d | 20d | 60d | rv20 | ADV $M | vault |
|---|---|---|---|---|---|---|---|---|
| STNG | Scorpio Tankers (largest product fleet) | 86.23 | +5.8 | +7.6 | +13.1 | 27 | 99 | none |
| TRMD | Torm | 40.00 | +16.6 | +17.0 | +42.6 | 46 | 76 | mentioned |
| HAFN | Hafnia | 10.25 | +14.9 | +14.8 | +46.0 | 44 | 30 | none |
| ASC | Ardmore (MR) | 19.30 | +8.1 | +7.1 | +26.0 | 26 | 11 | none |

### LNG / LPG carriers — driver: LNG shipping spot (weak: newbuild glut) · LPG: US–Asia propane arb
| tk | name | close | 5d | 20d | 60d | rv20 | ADV $M | vault |
|---|---|---|---|---|---|---|---|---|
| FLNG | Flex LNG | 31.24 | +1.2 | 0.0 | +7.1 | 17 | 12 | none |
| GLNG | Golar LNG (FLNG infrastructure, not a carrier bet) | 49.21 | −0.8 | −5.3 | −3.3 | 23 | 71 | none |
| LPG | Dorian LPG (VLGC) | 57.21 | +7.1 | +6.8 | +48.0 | 34 | 36 | mentioned |
| CLCO | Cool Company | Yahoo 404 (⬜ delisted or re-tickered) | | | | | | |
| NFE | New Fortress Energy | ⚠️ artifact: +2,189% 20d, rv 1,319 — a corporate action, not a price; do not use | | | | | | |

### Dry bulk — driver: Baltic Dry (BDRY); China steel/iron ore; grain
| tk | name | close | 5d | 20d | 60d | rv20 | ADV $M | vault |
|---|---|---|---|---|---|---|---|---|
| SBLK | Star Bulk | 30.75 | +4.1 | −3.5 | +18.8 | 32 | 61 | none |
| GNK | Genco | 27.67 | +6.1 | +1.4 | +13.8 | 33 | 17 | none |
| SB | Safe Bulkers | 8.81 | +8.2 | −2.2 | +31.5 | 45 | 16 | none (the vault's "SB" hits are Senate bills) |
| HSHP | Himalaya Shipping | 18.17 | +3.6 | +1.3 | +23.4 | 32 | 10 | none |
| GOGL | Golden Ocean | ⚠️ ADV ≈ 0 — merged into CMBT 2025; stale ticker | | | | | | |

### Containers / lessors — driver: box rates (Drewry WCI); Red Sea diversions; tariffs
| tk | name | close | 5d | 20d | 60d | rv20 | ADV $M | vault |
|---|---|---|---|---|---|---|---|---|
| ZIM | ZIM (liner, spot-heavy) | 29.63 | +1.5 | +7.4 | +22.7 | 33 | 51 | none |
| MATX | Matson (Jones Act + transpacific) | 231.11 | +2.9 | +4.0 | +12.2 | 28 | 71 | none |
| DAC | Danaos (lessor) | 165.15 | +7.1 | +7.1 | +29.7 | 25 | 22 | none |
| GSL | Global Ship Lease | 45.79 | +3.3 | +0.1 | +16.1 | 22 | 13 | none |
| CMRE | Costamare | 15.44 | +6.3 | +0.3 | +5.6 | 27 | 5 | none |
| SFL | SFL Corp (diversified lessor) | 13.45 | +5.2 | +6.6 | +24.7 | 33 | 20 | none |

### Jones Act / inland — driver: US domestic barge/tanker demand (not the war)
| tk | name | close | 5d | 20d | 60d | rv20 | ADV $M | vault |
|---|---|---|---|---|---|---|---|---|
| KEX | Kirby (inland barges) | 137.87 | +7.0 | −3.8 | −3.3 | 24 | 62 | mentioned |
| OSG | Overseas Shipholding | ⚠️ acquired by Saltchuk 2024 — stale ticker (ADV $2M) | | | | | | |

### ETFs — the drivers themselves
| tk | what it holds | close | 5d | 20d | 60d | rv20 | ADV $M |
|---|---|---|---|---|---|---|---|
| BWET | Breakwave Tanker — crude tanker freight FUTURES | 873.00 | +32.7 | +75.9 | +337.7 | 127 | 146 |
| BDRY | Breakwave Dry Bulk — Baltic freight futures | 14.20 | −7.3 | −12.0 | +9.7 | 34 | 2 |
| SEA | U.S. Global Sea to Sky Cargo — equities, all segments | 20.72 | +4.1 | +4.2 | +21.3 | 16 | 1 |
| BOAT | SonicShares Global Shipping — equities | 52.43 | +3.0 | +4.1 | +31.7 | 18 | 5 |

## THESIS (interpretation — NOT fact)
- *(analysis)* **The war is a CRUDE-TANKER story first, PRODUCT-TANKER second, and nothing else in shipping.** Crude
  tankers +33 to +49% in 60 days on freight (BWET +338%); product tankers +13 to +46% on the diesel squeeze (TRMD/HAFN
  lead, STNG lags); dry bulk flat-to-down over 20 days (BDRY −12%) and LNG carriers flat — those segments have their own
  cycles (China steel; the LNG newbuild glut) and carry no Hormuz premium. The 16d driver rule (freight, not crude)
  applies segment by segment: a dry-bulk name is not a war trade however "shipping" it sounds.
- *(analysis)* **Coverage gap, stated:** the vault holds a view on crude tankers only. Product tankers are the natural
  freight leg of the refinery thread ([[oil-value-chain]] 9/10 onward: the bottleneck is conversion, and Russian
  diesel has to move further) but no entry has been made — STNG/TRMD/HAFN get no mark until a study exists.
- *(analysis)* Three tickers in the common lists are dead or distorted (GOGL, OSG, NFE) and one is missing (CLCO). A
  list is not a universe until each line has been traded recently.

## 🌊 El Niño + the Panama Canal — which of these are ALSO exposed (added 2026-10-04 ~9:15pm PT, Jake's Q)
### DATA (observed)
- **NOAA CPC ENSO discussion, 10 Sep 2026:** status **El Niño ADVISORY**; Niño-3.4 **+1.8°C** (Aug), Niño-3 +2.5, Niño-1+2
  +3.4; **>90% chance of a VERY STRONG event in NH fall/winter 2026-27; 75% chance OND 2026 is HISTORIC (3-month RONI
  ≥ +2.5°C, exceeding every event since 1950).** Next update **Thu 2026-10-08.** (cpc.ncep.noaa.gov/…/ensodisc.shtml)
- **Panama Canal Authority, 28 Sep 2026:** maximum Neopanamax draft **14.94 m / 49.0 ft, effective immediately**; daily
  slots **33 from 15 Oct 2026** (10 Neopanamax + 23 Panamax), citing the present and projected Gatun Lake level and
  "close to average precipitation on the Canal watershed"; **"the water deficit continues."** Trade press: a scheduled
  1 Oct cut to 47.5 ft was POSTPONED; restrictions had escalated through September as El Niño built; Gatun ~84.7 ft.
  (pancanal.com announcement; FreightWaves/Sourcing Journal.)
- **The 2023-24 precedent (the last strong El Niño):** Oct 2023 the driest October since 1950 (−41% vs normal); Gatun
  just over 79 ft; draft cut to **44 ft** (from 49.5-50); transits **36 → 32 (30 Jul 2023) → 24 (7 Nov 2023)**; 160+ ships
  queued, Neopanamax waits ≥17 days (Aug 2023); **VLGC Houston–Chiba $250/t (w/e 29 Sep 2023) = record since the
  assessment began (2016)**; LNG carrier transits cut >40%. (S&P Global, Maritime Executive, EIA, TradeWinds.)
- **Canal mix, FY2025 (ACP):** 13,404 transits (+19.3% y/y), 3,342 Neopanamax; growth led by **containers and LPG**; bulk
  recovering; **LNG below expectations** (freight economics, i.e. Cape/Suez routing or US→Europe instead).
- **El Niño channels already printing (2026):** Asian hydropower −13 GW avg y/y in June (India + Vietnam >80% of the
  decline) → more coal and LNG burn (Down to Earth; Breakwave 8/18) · Brazil: El Niño extends the dry season → thermal
  output and LNG imports into 2027 (Argus 7/30) · Australian wheat 2026/27 forecast ~29 Mt (−19%), exports ~23.5 Mt
  (DCN) · UBS: a super El Niño tightens thermal coal.

### THESIS (interpretation — NOT fact)
- *(analysis)* **"Vulnerable" runs the OTHER way for most owners.** A canal restriction is a TON-MILE event: cargo that
  cannot transit sails around the Cape or waits, and the owner of the ship gets paid more. 2023 proved it — the VLGC
  record was canal-made. The charterer/liner pays; the lessor on a fixed charter is insulated. So the exposure table
  below gives a DIRECTION, not just a yes.
- *(analysis)* **Exposure by name, both channels:**
  | tk | canal | El Niño | net read |
  |---|---|---|---|
  | **LPG** (Dorian, VLGC) | HIGHEST — US Gulf→Asia propane is the canal's #1 energy user; 2023 record | mild US winter → low propane → wider arb → more exports (bull) | restriction = windfall; easing (now) removes the 2023 tailwind |
  | **FLNG** (LNG carriers) | HIGH — US→Asia via canal or Cape; 2023 transits −40% | Asian hydro deficit + Brazil thermal → more LNG cargoes (bull) | the only El Niño-demand name; carrier glut caps it |
  | **STNG · ASC · TRMD · HAFN** (MR product) | MODERATE — US Gulf→west-coast South America diesel/gasoline | Peru/Chile demand; second order | restriction lengthens voyages (bull) |
  | **ZIM** (liner) | NEGATIVE — pays slot auctions / reroutes; Asia→USEC via canal | — | the one name a restriction HURTS |
  | **DAC · GSL · CMRE · SFL** (lessors) | insulated (fixed charters) | — | none |
  | **MATX** | NONE — transpacific to Long Beach, no canal | — | none |
  | **SBLK · GNK · SB · HSHP** (dry bulk) | LOW-MODERATE — US Gulf grain→Asia | MIXED: Australian wheat −19% (bear), Asian coal imports up on hydro deficit (bull), Brazil soy weather (⬜) | El Niño matters more than the canal; direction not settled |
  | **KEX** (Mississippi barges) | none | El Niño = WETTER southern US → fewer low-water episodes (the 2022-23 low water was La Niña) | mildly positive |
  | **DHT · FRO · INSW · TNK · NAT** (crude) | NONE — VLCCs cannot transit; Suezmax/Aframax marginal | mild NH winter → less heating-oil demand, second order | the war trade is unaffected by either |
- *(analysis)* **State today: the canal is EASING INTO a historic El Niño.** The ACP has raised slots and draft on
  near-average rain through September, while NOAA puts 75% on the strongest event on record for Oct-Dec. The 2023
  failure came in OCTOBER (driest since 1950) and the restrictions bit in Nov-May. ⇒ the 120-day question is whether
  the Oct-Nov rains fail; if they do, the 15 Oct slot increase reverses and the 2023 sequence (draft cuts → slot cuts →
  auctions → VLGC/LNG spike) replays into Q1 2027. If they hold, the tailwind simply does not arrive.
- *(analysis)* **Money, today: no instrument.** LPG's +48%/60d is the propane arb and the Middle East (Gulf LPG exports
  disrupted), not the canal; the canal is currently a REMOVED tailwind. The only name with a positive El Niño DEMAND
  channel independent of the canal is FLNG (Asia/Brazil LNG burn), and it is flat on 20 days. No marks. ⚠️ Class 8: the
  "super El Niño" headlines come from weather-sellers and commodity desks; NOAA's own probability (75% historic) is the
  datum.

### 📌 REGISTERED
- 🔴 **Thu 2026-10-08 NOAA ENSO update** — does the historic-event probability hold ≥75%?
- 🔴 **15 Oct 2026** — do the 33 slots take effect, and does the ACP's next monthly notice hold 49 ft? A draft cut
  announced for Nov-Dec = the 2023 sequence starting → LPG / FLNG / MR tankers 🟢, ZIM 🔴.
- ⬜ Gatun Lake level series (ACP publishes daily) — adopt as the instrument; 2023 trough ~79 ft vs ~84.7 ft now.
- ⬜ Australian wheat export estimate (ABARES Dec) and Asian coal import prints — the dry-bulk direction.

## 📌 OPEN
- ⬜ product-tanker study (clean freight series; TRMD/HAFN/STNG vs the diesel crack) before any mark.
- ⬜ CLCO status; NFE corporate action behind the artifact.
- ⬜ an options snapshot for the product tankers (STNG iv30 37.5 on CBOE 10/2 vs rv 27 — not rich).
