# INMA — Session Handoff

**Last updated:** mid-session, field-estimator rewrite in progress
**Repo:** `smsyt4sjvc-crypto/INMA-`
**Live site:** `https://inmagent.com` (GitHub Pages serves `main`)
**Work branch:** `claude/replace-company-names-rSYNT` (merged to `main` via no-ff merges after each change)

---

## 1. Recap — what shipped today

All of these are live on `main` and `inmagent.com`.

### Field Estimator (`field-estimate.html`)
- Full rewrite from flat form to 6-step stepper PWA (photos stored as data URLs, window.open outputs called synchronously for iOS Safari).
- Removed "Lap Siding (Gables)" line item — all field siding now rolls into Primed Hardie or ColorPlus.
- Converted Siding / Windows / Trim from predefined items to **free-form add-line lists** (each line: description + qty + $/unit + remove).
- Added "← Back to Estimator" button on both the Customer Estimate and Contractor Pack popup windows. Falls back to navigating to `/field-estimate.html` if `window.close()` is refused (PWA/iOS edge case).
- **Removed the "Analyze with AI" feature entirely** (Jake decided it wasn't useful).

### New DIY Assistance landing page (`diy.html`)
- Dedicated page intended as QR target for a parking-lot flyer across from Home Depot.
- Hero, 7 benefit cards, 3-step "How it works", comparison table (DIY alone vs DIY with INMA vs Full contractor), FAQ, Call/Text CTA, footer.
- Pricing: **$250** initial house visit · **$250/week** unlimited support · **$75/visit** additional house calls.
- Sticky top nav with "← Back to INMA" link (fixes mobile-trap issue where PWA/in-app browsers hide browser back button).
- DIY card on `index.html` now has a "Learn more →" button linking to `/diy.html`.

### Index page (`index.html`)
- Floating bottom banner swapped from "Upload your quote" to **Spring Tune-Up · $750 · Play the game** (greener styling, links to `/game.html`).
- New **"Upload it. I'll walk you through it."** CTA section inserted directly after the National Company vs. INMA comparison table (while the 30-40% markup data is fresh).
- Softened "beat by 20% guaranteed" → "I can very often reduce these by around 20%."
- Footer: relabeled "WA LLC" to **"WA UBI #606 027 063"** with Verify → link to WA state lookup.
- Added new "Hide what I charge." bullet in the "What I Will Never Do" section — discloses the 10% fee + FMV transparency.
- Added "💾 Save my contact" button under the main CTA block + in the footer.

### Game (`game.html`)
- Added 80s chiptune audio engine (Web Audio API, no external files):
  - Looping bassline + melody (A-minor pentatonic, 140 BPM)
  - SFX: shoot, hit, hurt, win, lose
  - ♪/🔇 mute toggle top-right of canvas, persisted via localStorage
- Fixed iPad touch controls (swapped `max-width:600px` for `(hover:none) and (pointer:coarse)`).
- **Removed FIRE button — auto-fire always.**
- Difficulty retuned: spawn 62→40, min 20→12, asteroid vy 1.4-3.4 → 2.4-5.0, shootCooldown 14→24, GAME_TIME 60→45.
- Once-per-day limit **disabled** (Jake can still reach out to re-enable when marketing goes live — look for `canPlay()` in the file, it currently returns `true`).
- "Save Jake's Contact" link added to the Win overlay.

### Save-contact (vCard) site-wide
- New file: `/jake.vcf` with `FN: Jake Bishop`, `ORG: INMA — Inland Northwest Marketing Affiliates`, title, phone, email, URL, note.
- "💾 Save my contact" button added on: `index.html` (CTA + footer), `diy.html` (under bottom CTA), `upload.html` (on success screen — peak receptivity), `Review.html` (footer), `contractor.html` (after CTAs), `game.html` (win overlay).
- Not added on `consult.html` (internal tool) or `market-report.html` (low traffic).

### Name correction
- Fixed **Jake Paulson → Jake Bishop** across `index.html` (JSON-LD schema), `diy.html` (title + footer), `consult.html` (signature line).

### Upload page (`upload.html`)
- Hero headline softened from "We'll Beat Any National Firm Quote by 20%" → **"Upload Your Quote. I'll Walk You Through It."**

---

## 2. In-progress task — Field Estimator v2 redesign (NOT BUILT YET)

Jake wants a major rework of `field-estimate.html`. **The half-finished HTML changes were reverted at end of session — the current field-estimate.html on `main` is the working 6-step manual version.** Pick up from clean state.

### Target architecture

**4-step flow:**

1. **Step 1 — Job Info** (existing fields + one change)
   - Homeowner Name, Property Address, Date, Estimate #
   - **NEW: Estimate # auto-fills from the leading digits in the address.** E.g. typing "1234 Main St, Spokane WA" sets Estimate # = `INMA-1234` (editable; Jake can type his own). Implementation: regex `^(\d+)` on the address input, fire on `input` event, only auto-fill if Jake hasn't manually edited the estimate #.

2. **Step 2 — General Job Scope** (NEW)
   - Single textarea. Placeholder: *"E.g. Full tearoff. Hardie ColorPlus board-and-batten on all four sides. Replace 12 windows — mix of sizes. Paint new trim."*
   - One-line overview Jake dictates before walking. Gives AI global context.
   - Hint below: "Tap the mic on your keyboard to dictate."

3. **Step 3 — Walk the Job** (rebuilt)
   - Per-wall entry card: one photo + one textarea for notes, **"✓ Save Wall & Add Another"** button.
   - Cancel button on the in-progress card to discard it.
   - Saved walls render above as small cards (thumbnail + truncated notes + tap-to-edit + delete buttons).
   - "+ Add Wall / Area" button always visible when no card is being edited.
   - **Up to 12 walls.** (Old limit was 8 photos total — raise to 12.)
   - Hint: "When you're done, hit Next below to generate the estimate." Nav's Next button advances to Step 4.

4. **Step 4 — Generate & Edit** (NEW, replaces the old Review step)
   - Big **"✨ Generate Estimate with AI"** button at top.
   - Button calls the Vercel endpoint with { jobInfo, generalScope, walls }, shows a spinner for 15–30s.
   - On success: reveals the preview area containing:
     - **Customer-Facing Scope** textarea (editable prose, plain-English, no internal pricing)
     - **Contractor Scope** textarea (editable prose, technical, measurements, access/staging, punch list)
     - **Line Items** list — editable rows (description + qty + unit + rate + remove), with "+ Add Line" button
     - **Totals block** — Job Subtotal, −INMA Fee 10%, Contractor Subtotal, Sales Tax % (input), Job Total, Jake Keeps
     - **"📄 Customer Estimate"** + **"📋 Contractor Pack"** buttons (open print windows)
     - **"⟳ Regenerate from walls (overwrites edits)"** button at bottom
   - Every field is editable. Print windows are frozen snapshots of whatever state is in the preview when Jake hits print.

### What to delete
- The old Siding / Windows / Trim steps (steps 3, 4, 5 in the current version).
- `state.siding`, `state.windows`, `state.trim` arrays.
- `renderGroup`, `bindAddButtons`, `addLine`, `GROUP_HOST` constants.
- `collectLineItems` gets rewritten to just iterate `state.previewLines`.

### What to keep
- `fileToDataURL` helper, photo handling (just per-wall instead of global).
- Output templates (`buildCustomerHTML`, `buildContractorHTML`) — rewire to pull from `state.previewLines`, `state.customerScope`, `state.contractorScope`.
- Nav system (`bindNav`, `updateStepUI`, dots) — just change `TOTAL_STEPS = 4`.
- Back button on output windows.
- Auto-estimate # from date (keep as a fallback if address is empty).

### New state shape
```js
const state = {
  step: 1,
  generalScope: '',
  walls: [],          // [{ id, dataUrl, mediaType, notes }]
  currentWall: null,  // { dataUrl?, mediaType?, notes } while editing a new card
  customerScope: '',
  contractorScope: '',
  previewLines: [],   // [{ id, desc, qty, unit, rate }]
  taxPct: '',
  generated: false,
};
```

### Vercel endpoint changes (`api/generate-estimate.js`)
- Endpoint: `https://inma-five.vercel.app/api/generate-estimate` (same URL).
- New request body: `{ jobInfo: {owner, address, date, num}, generalScope, walls: [{image: {mediaType, base64}, notes}] }`.
- Send all wall photos to Claude in a single multi-image message. Include `generalScope` and each wall's notes as labeled text blocks.
- New prompt:
  - Give Claude the FMV rate card (already in the current file — keep it).
  - Tell it to produce TWO prose blocks (customer-facing and contractor-facing, distinct tones — see below) AND a `line_items` array.
  - Customer prose: plain English, no internal markup, no measurements jargon, verbose professional descriptions.
  - Contractor prose: technical, per-area notes, punch list, access/staging callouts, measurements if mentioned.
  - Line items: each has `{ desc_customer, desc_contractor, qty, unit, rate }` anchored to FMV.
- New response shape:
  ```json
  {
    "customer_scope": "string",
    "contractor_scope": "string",
    "line_items": [{"desc_customer":"","desc_contractor":"","qty":0,"unit":"SF","rate":0}]
  }
  ```
- Keep the existing CORS / Anthropic SDK wiring. Model: keep `claude-haiku-4-5-20251001`.

### Output templates — what changes
- Customer Estimate: before the line items table, insert an **intro paragraph** = `state.customerScope`.
- Contractor Pack: replace the existing "Scope Notes (Jake)" + "AI Observations" blocks with a single **"Scope"** block = `state.contractorScope`. Keep the photo grid (now pulls from `state.walls.map(w => w.dataUrl)`).
- Line items table in both: iterate `state.previewLines`. Customer uses `desc_customer`; contractor uses `desc_contractor`.

### Dictation notes
- **Don't build custom speech recognition.** Just use regular `<textarea>` elements. iOS keyboard has a built-in mic button — Jake taps the textarea, taps the mic, dictates, hits Done. Zero new code.

---

## 3. How to kick off in the new chat

Copy-paste this as the first message in the new chat:

> I'm continuing work from a previous session. See `HANDOFF.md` on the `claude/replace-company-names-rSYNT` branch of `smsyt4sjvc-crypto/INMA-` (also on main). We're picking up mid-task on the Field Estimator v2 redesign — 4-step flow, per-wall photo + dictation, AI-generated editable estimate. The current `field-estimate.html` on main is the **last working manual 6-step version**; the v2 rewrite has not been started in code yet. Please read `HANDOFF.md` and then tell me what questions you have before you start coding.

The new chat should:
1. `git checkout claude/replace-company-names-rSYNT` (create from origin if needed)
2. Read `HANDOFF.md` in full
3. Read `field-estimate.html` and `api/generate-estimate.js` to see current state
4. Confirm scope with you before coding the rewrite
5. Build in small chunks (Write→Edit→Edit) to avoid the streaming-timeout issue we hit this session

---

## 4. Gotchas & operational notes

- **GitHub Pages serves `main`.** Any change needs to be merged to main to go live on `inmagent.com`. Feature branch also gets Vercel auto-deploy previews.
- **Do not commit to main directly** — some commits during this session slipped to main; feature branch has been force-synced to match. Working pattern: edit on feature branch, commit, push, `git checkout main`, `git merge <feature-branch> --no-ff`, push main.
- **`window.open()` on iOS Safari** must be called synchronously inside the click handler (not after an `await`). The Customer Estimate / Contractor Pack buttons do this correctly — don't refactor to async or popups will be blocked.
- **Photos must be data URLs, not blob URLs.** Blob URLs don't survive `window.open()` → `document.write()`.
- **Vercel endpoint CORS** only allows `https://inmagent.com` as origin. Local testing against the real endpoint will fail; test on the deployed preview URL.
- **No email / Formspree on the field estimator** — Jake said no. Print-to-PDF only.

---

## 5. Quick reference

### URL map (all live on inmagent.com)
- `/` — main site
- `/diy.html` — DIY Assistance landing (QR target)
- `/field-estimate.html` — field tool (Jake's internal)
- `/consult.html` — tablet consultation tool
- `/upload.html` — contract upload
- `/Review.html` — review collection
- `/market-report.html` — FMV data page
- `/contractor.html` — contractor recruitment
- `/intel.html` — online identity services
- `/game.html` — Spring Tune-Up engagement game
- `/jake.vcf` — save-contact vCard

### Key files
- `index.html` — main landing
- `api/generate-estimate.js` — Vercel serverless function (will need rewriting)
- `api/analyze-quote.js` — old upload-quote analyzer (unused, leave in place)
- `package.json`, `vercel.json` — Vercel config

### Key numbers
- Phone: (509) 251-7792
- Email: jake@inmagent.com
- UBI: 606 027 063
- INMA advocacy fee: 10% of FMV
- Home Tune-Up: $750
- DIY initial visit: $250 · $250/week support · $75/visit add-ons
