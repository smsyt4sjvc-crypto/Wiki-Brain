# Second-tool audit of the AI money map — Jake's paste, 2026-10-10 ~8:16pm PDT (verbatim, tables flattened)

AI money-map audit — October 10, 2026
I've found several disclosures that materially improve the circular-financing model. Two are especially important:
* Microsoft actually discloses $24.1 billion of FY2026 revenue from OpenAI-related commercial arrangements, including revenue sharing. Its cumulative OpenAI investment funding was $11.9 billion at June 30. That gives us a measurable commercial relationship rather than an assumed loop, although the revenue and investment figures cover different periods.
* NVIDIA's $36 billion cloud commitment cannot be treated as $6 billion of annual circular spending today. The filing schedules none of that particular program for the remainder of fiscal 2027, with $6 billion scheduled for FY2028. Its actual annual financial exposure is more complicated than the previous model allowed.
These findings support the circular-financing concern, but they also show why three categories must stay separate: money already paid, contractually promised future purchases, and contingent financing or guarantees.

1. What the new evidence closes
Anthropic customer channels | $2.16B, or 47% of 2025 revenue, passed through AWS and Google marketplaces | Measured, 2025
Marketplace revenue sharing | AWS and Google received about $351M in distribution fees, roughly 16% of those sales | Measured, 2025
Amazon financing the labs | $50B invested in OpenAI during 2026, plus $10B invested in Anthropic in Q2 | Filed, cash investment
Google financing Anthropic | $10B initial investment reported; $20B of contingent funding remained at June 30 | Reported + filed
Cloud dependence on labs | Jefferies estimates Q2 revenue exposure: AWS 6%, Azure 25%, Google Cloud Platform 45% | Analyst estimates
CoreWeave customer concentration | Its three largest customers contributed 36%, 26%, and 10% of Q2 revenue | Filed; customers unnamed
Oracle customer financing | $75B in prepaid or customer-supplied AI hardware reported at May 31 | Company disclosure
Sources: Reuters on Anthropic's confidential prospectus; Amazon, Alphabet and CoreWeave SEC filings; Oracle's FY2026 results; and Jefferies reporting.
The biggest methodological improvement comes from Anthropic's marketplace disclosure. Its reported 2025 revenue included approximately $2.16 billion in customer purchases routed through AWS and Google. Around $351 million returned to those platforms as distribution fees.
That $351 million is a measurable payment from Anthropic back to its cloud partners, but it was generated from customer sales. It should not automatically be classified as investor-funded circular demand.

2. NVIDIA's financing loop is substantially bigger than the original $6B estimate
Its July 26, 2026 SEC filing establishes three separate exposures:
Net equity-security purchases, first six months of FY2027 | $35.16B | Actual net investing cash outflow
Equity investments held at July 26 | ~$99B | Balance-sheet exposure, including valuation changes
Future equity-investment commitments | $25B | Potential future financing
AI-cloud purchase commitments | $36B | Future compute purchases, beginning FY2028
OpenAI/SB Energy lease guarantees | Up to $105B | Conditional credit support; generally begins as sites open from FY2029
All figures are from NVIDIA's 2026 second-quarter 10-Q. The $35.16B is derived from $42.404B of equity purchases less $7.241B of sales proceeds, not a measurement of how much ultimately returned as NVIDIA chip revenue.
That's a major distinction: NVIDIA isn't merely selling processors into a market where everyone else is raising the money. It is also deploying substantial capital into the ecosystem and underwriting some future customer obligations.
But the amount of NVIDIA's own capital that actually recycled into its reported chip revenue remains unmeasured. The SEC figures above establish financing exposure, not the traceable recycled revenue percentage.

3. Anthropic's future spending is much more measurable than the earlier map suggested
Reuters' September 29 examination of Anthropic's confidential IPO prospectus identifies approximately $518B of planned infrastructure spending with six partners, including:
Google | $111.1B | Apr 2026–Jul 2033
Amazon | $110.0B | May 2026–Apr 2036
Microsoft | $31.4B | Nov 2026–May 2033
Broadcom-related equipment leases | $161.2B | Largely noncancelable
xAI | Up to $84.5B | Largely cancelable with 90 days' notice
AMD | More than $20B of expected compute supply | Separate partnership
Source: Reuters, September 29, 2026, reporting on the confidential IPO filing. These are obligations and prospective spending, not realized revenue.
Approximately $413.7B of the first four obligations is difficult to cancel or must be paid regardless of usage. [80% hard obligations / 20% other prospective spending]
This closes much of the contractual obligation side of the map. It does not close the annual cash-flow side: we still need delivery schedules and amounts actually paid to know how much revenue was generated in a given year.
It also identifies an important credit-risk channel. The proposed $60B Broadcom/Anthropic chip-financing package would finance part of the equipment ecosystem, so it cannot simply be added to Anthropic's $161.2B lease obligations as another independent source of demand.

4. Correcting the outside-money calculation
Using Anthropic's reported 2025 figures of $4.59B revenue and $7.33B compute costs, the original scenario can be recalculated:
20% → 50.1% · 35% → 40.7% · 50% → 31.3% (assumed revenue from inside buyers → end-customer-funded share of compute)
The middle case of 41¢ was correct. But the full range, holding the 1.6× compute/revenue ratio constant, is 31–50¢, not 31–67¢. These are attribution scenarios, not observed cash flows.
There's also an important distinction between investor money and inside money. Outside shareholders financing an unprofitable lab represent a genuine new inflow of capital, but not independently generated AI customer demand. Those dollars should be retained in a separate financing category rather than silently counted as external AI sales.

5. What remains unresolved
Percentage of lab revenue from genuinely independent customers | Still unknown
Actual annual cloud revenue from each lab | Partially known, but Microsoft combines services and revenue sharing
Financing that returns to the original chip vendor | Material exposures identified; exact recycled cash not measured
Hyperscaler AI spending funded by non-AI business profits | Not separately disclosed with sufficient precision
Guarantees that could become real liabilities | Contract limits increasingly identifiable; actual losses unknown
The principal change to the risk model: Anthropic's largely noncancelable contracts mean a financing shock may not immediately stop cloud revenue recognition. Instead, the stress can migrate into overdue receivables, defaults, lenders, equipment leases, and ultimately guarantors such as Broadcom or NVIDIA.
The map should therefore retain three distinct measures for every company: realized revenue, independently funded demand, and contingent credit exposure. Adding these together would overstate the amount of money circulating.
For now, the evidence is considerably stronger on the contractual financing loops than on the exact percentage of chip revenue ultimately supported by independent AI customers. I would not publish a definitive industry-wide circular-revenue percentage until that last attribution problem is solved.
The next high-value source is Anthropic's public S-1, when available, followed by the cloud providers' next quarterly filings.
