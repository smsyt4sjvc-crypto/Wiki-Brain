# ZH RTs on Firmus — AFR "forced share buyback" excerpts + @kakashiii111 "idle GB300s" thread (Jake paste ~12:50pm PDT 10/12)

## Verification notes (Claude, 2026-10-12 ~12:55pm PDT)
- **AFR article exists** (Google News: AFR "Firmus faces forced share buyback if it can't resurrect IPO plans", Kanika Sood, Street Talk, stamped 23:11 GMT 10/11 = Mon 10/12 AEDT). Paywalled; only the excerpts in the paste were read. REPORTED (one outlet, citing July shareholder agreements).
- **@kakashiii111's "18.5K GB300s idle since March" is CONTRADICTED on the main point:**
  - Firmus release 9/29 + Reuters 9/28-29 (via CNA/MarketScreener/The Star): "Meta is already using NVIDIA GB300 NVL72 systems at Firmus' Melbourne AI factory, the largest deployment of NVIDIA Blackwell Ultra systems in the Southern Hemisphere"; new Meta agreements for Southeast Asia capacity (terms undisclosed).
  - SemiAnalysis ClusterMAX 3.0 (9/23, newsletter + podcast via BigGo): tested a Firmus GB300 cluster; a network misconfiguration gave 1,455 tokens/s/GPU vs ~3,500 elsewhere, fixed with SemiAnalysis's help; Firmus kept its Silver rating; "a company that has stood up thousands of GB300s with happy customers."
  - The website screenshot lists H200/H100/A100/L40S with "GB300 … coming online soon" — that is the public on-demand menu; the Melbourne GB300s are contracted to Meta. ⬜ whether the March shipment and the Melbourne deployment are the same chips; ⬜ the shipment figure itself (source not given).
- **Arithmetic (rule 21b, vault `chips-mw-framework:L31`: GB300 NVL72 135–142 kW ≈ 507–533 GPUs per MW of IT load):** 18,500 GPUs ≈ 257 racks ≈ **35–36 MW IT**, ≈ 42–51 MW of facility power at PUE 1.2–1.4. "More than 40 MW" holds only on facility power.
- **Vault prior state:** 46 MW built of a 912 MW pipeline (Bloomberg, 10/8); IPO withdrawn 10/8 (company statement), "consider other funding options such as private credit," a private round with existing investors (`ai-financing-fragility:L8894`). kakashiii111 = anonymous independent bear Substack (`ai-financing-fragility:L4059`).
- **Tape:** Maas Group (MGH.AX, a Firmus backer) Fri 10/9 close 4.63 → Mon 10/12 close 3.93 (−15.1%, 12.4M shares vs 7.2M), 7.01 on 10/5 (−44% in a week). IREN 41.28 (10/6) → 35.01 · NBIS 249.87 → 208.11 · CRWV 91.72 → 80.35 (Yahoo, ~12:55pm PT).
- Oliver Curtis: ABC 10/2 headline "owner tries to shed jailbird image" (prior insider-trading conviction in Australia; details not re-checked).

---

**ZeroHedge post (RT of @MarkDiStef):**  
The AI circular financing diddle is brutal.

**Text from the screenshots (Australian Financial Review article by Kanika Sood, Street Talk, Oct 12, 2026 – 5.00am):**

**Headline:** Firmus faces forced share buyback if it can’t resurrect IPO plans

Firmus Technologies could be forced to buy back shares from Nvidia and Blackstone if it fails to resurrect a public listing under a set of confidential agreements which put the artificial intelligence infrastructure play on a collision course with the very investors it is relying on for financing.

The same agreements suggest that a select group of shareholders including the microchip manufacturer and asset management giant will be in line for free securities if the company does not manage a 25 per cent return on investment guaranteed within three months of the failed float.

Co-founder and co-CEO Oliver Curtis is now focusing on the Nasdaq after pulling plans to list on the ASX, but his right to enter the US may be an obstacle.

Documents outlining the terms of investment with major investors signed in July point to the challenge for the company should an IPO not eventuate within five years. The shareholder agreement notes that this will give Blackstone and Nvidia “a qualified ‘put’ right to require the company to either seek to buy back its shares … or procure a third-party purchaser.”

Nvidia owns a 7.2 per cent Firmus stake while Blackstone has a 6.7 per cent holding. The asset management giant has separately bankrolled the company’s Australian data centre pipeline with a $US5 billion ($7.2 billion) loan that can be extended to $US10 billion. However, that loan locks in the founders, forcing them to retain at least half their shares even if Firmus goes public until they have fully repaid the facility, which is not due until 2031.

The shareholder agreements also detail a so-called top-up entitlement, particularly if the company is acquired before it floats. If the price is below a return target, Firmus will have to issue new shares or, if it is unable to, instead pay the investor the equivalent amount.

(Note: The full AFR article appears paywalled beyond these excerpts.)

//

**ZeroHedge post (ID 2109728931616043390):**  
RT @kakashiii111: As with every fraud, you have to connect the dots and collect the pieces of the puzzle in order to get as full a picture…

**Quoted post by @kakashiii111 (ID 2108163825547559040):**  
According to public data, Firmus currently has only 42 to 46 megawatts (MW) actively operating across two data centers in Melbourne and Singapore, while claiming a “pipeline of 900 MW.”

These deployments range from VMs to H200s.

In March, there was an unusual shipment of GB300s to Australia, from Nvidia to Firmus. It included 18.5K GB300s, or more than 40 MW if all of them were connected and operating.

So what happened to these GB300s since March? they collecting dust for more than six months, and counting.

It is a pattern we already know across neoclouds and hyperscalers.

If Firmus ever wants to get them plugged in, it needs this IPO. If Firmus wants to get any close its 900 MW fantasy, it needs this IPO.

While Jensen has dozens of neoclouds in his army, one soldier having trouble completing its training before the IPO may also affect the other soldiers.

Immediate impact? Probably not. Later impact? Well…

**Text extracted from the attached image (Firmus GPU Cloud specs screenshot):**  
■ GPU SPECS

From containerized workloads to VMs and dedicated bare metal, Firmus GPU Cloud delivers the right GPU performance model for your scale - with NVIDIA GB300 and Vera Rubin NVL72 coming online soon.

H200  
H100  
A100  
L40S  
BM  
VM

H200  
Train faster. Scale smarter.

Built for advanced AI and HPC workloads, H200 instances deliver next-generation performance and scalability with liquid-cooled efficiency and full support for distributed training.

GPU  
8x NVIDIA H200 Tensor Core GPUs (Hopper architecture, HBM3e)

GPU MEMORY  
8x 141 GB HBM3e (= 1.13 TB total)

INTERCONNECT  
NVLink 4.0 + NVSwitch 3.0 (900 GB/s bi-directional per GPU)

CPU  
2x Intel Xeon Platinum 8462Y+

SYSTEM MEMORY  
2 TB DDR5 5600 MT/s ECC

NETWORK  
Dual 200–800 Gb/s InfiniBand or 400 Gb/s Ethernet  
(RDMA / RoCE v2 support)

Start training, testing, or deploying today with Firmus GPU Cloud  
[ENQUIRE →]
