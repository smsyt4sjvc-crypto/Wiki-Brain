import Anthropic from '@anthropic-ai/sdk';

const ALLOWED_ORIGIN = 'https://inmagent.com';

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', ALLOWED_ORIGIN);
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const { jobInfo = {}, generalScope = '', walls = [] } = req.body || {};

  const client = new Anthropic();

  const content = [];

  content.push({
    type: 'text',
    text:
`You are helping Jake at INMA (Inland Northwest Marketing Affiliates, Spokane WA) build a siding / windows / trim estimate from a general scope, per-wall photos, and Jake's dictated field notes.

JOB:
- Homeowner: ${jobInfo.owner || '—'}
- Address: ${jobInfo.address || '—'}
- Date: ${jobInfo.date || '—'}
- Estimate #: ${jobInfo.num || '—'}

GENERAL SCOPE (Jake's up-front dictation):
${generalScope || '(none)'}

Below are photos and notes from each wall Jake walked. Use them together with the general scope to estimate the job.`
  });

  walls.forEach((w, idx) => {
    const label = w.label || `Wall ${idx+1}`;
    if (w.image && w.image.base64) {
      content.push({
        type: 'image',
        source: { type: 'base64', media_type: w.image.mediaType || 'image/jpeg', data: w.image.base64 }
      });
    }
    content.push({
      type: 'text',
      text: `--- ${label} ---\nField notes: ${w.notes || '(no notes)'}`
    });
  });

  content.push({
    type: 'text',
    text:
`Use this INMA fair-market-value rate card as a starting point. INMA sits at the UPPER end of FMV because we don't cut corners — pick rates accordingly.

SIDING (per SF unless noted):
- Primed Hardie B&B: $12.50
- ColorPlus Hardie: $19.00
- Aluminum Soffit: $13.00/LF
- Aluminum Fascia: $8.50/LF
- Post/Beam Wrap: $12.00/LF
- Tearoff/Dump/Cleanup: $1.50/SF

WINDOWS (per unit):
- Small (≤20 SF): $425
- Medium (21–40 SF): $900
- Large (>40 SF): $1,200

TRIM (per LF):
- Interior Trim: $4.00
- Exterior Trim / Belly Band: $5.00

OUTPUT — respond with ONE JSON object and nothing else. No prose outside the JSON. Shape:

{
  "customer_scope": "Plain-English prose for the homeowner. Detailed — explain what's happening, what product is going on, tear-off, trim style, windows, any specials. No internal pricing talk, no contractor jargon. 3-6 sentences.",
  "contractor_scope": "Technical prose for the installing contractor. Per-wall specifics where relevant, access/staging callouts, punch list, fastening/trim/flashing details, measurements if Jake mentioned them. Direct and concise.",
  "material_list": "Plain-text bulleted material list compiled from Jake's notes — counts of light blocks, gable vents, hose bib blocks, corners, window trim style, etc. One item per line with leading '· '. Leave blank if nothing called out.",
  "line_items": [
    {
      "desc": "Line description — clear, professional, works for homeowner and contractor alike",
      "qty": 0,
      "unit": "SF" ,
      "rate": 0
    }
  ]
}

Rules:
- Every line_item has qty (number), unit (SF / LF / EA), rate (number), and desc (string).
- Anchor rates to the FMV card above, upper end.
- If a quantity isn't clear from photos/notes, use your best conservative estimate and mention it in contractor_scope — Jake can adjust.
- No trailing commentary. JSON only.`
  });

  const message = await client.messages.create({
    model: 'claude-haiku-4-5-20251001',
    max_tokens: 4000,
    messages: [{ role: 'user', content }]
  });

  const text = message.content.map(b => b.type === 'text' ? b.text : '').join('');

  const parsed = safeParseJSON(text);
  if (parsed) return res.status(200).json({ estimate: parsed });
  return res.status(200).json({ estimate: null, raw: text });
}

function safeParseJSON(text){
  if (!text) return null;
  try { return JSON.parse(text); } catch(_) {}
  const m = text.match(/\{[\s\S]*\}/);
  if (m) { try { return JSON.parse(m[0]); } catch(_) {} }
  return null;
}
