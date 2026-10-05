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

## 📌 OPEN
- ⬜ product-tanker study (clean freight series; TRMD/HAFN/STNG vs the diesel crack) before any mark.
- ⬜ CLCO status; NFE corporate action behind the artifact.
- ⬜ an options snapshot for the product tankers (STNG iv30 37.5 on CBOE 10/2 vs rv 27 — not rich).
