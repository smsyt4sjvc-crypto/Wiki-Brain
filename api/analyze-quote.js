import Anthropic from '@anthropic-ai/sdk';

const ALLOWED_ORIGIN = 'https://inmagent.com';

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', ALLOWED_ORIGIN);
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const { imageBase64, mediaType } = req.body || {};
  if (!imageBase64) return res.status(400).json({ error: 'No image provided' });

  const client = new Anthropic();

  const message = await client.messages.create({
    model: 'claude-haiku-4-5-20251001',
    max_tokens: 1500,
    messages: [
      {
        role: 'user',
        content: [
          {
            type: 'image',
            source: {
              type: 'base64',
              media_type: mediaType || 'image/jpeg',
              data: imageBase64,
            },
          },
          {
            type: 'text',
            text: `You are helping Jake at INMA (Inland Northwest Marketing Affiliates) analyze a competitor quote. Extract and summarize every piece of information visible in this quote image.

Return your analysis in this exact format:

CONTRACTOR: [company name]
QUOTE DATE: [date if visible, otherwise "not shown"]
HOMEOWNER: [name if visible]
PROJECT ADDRESS: [address if visible]

LINE ITEMS:
- [item]: $[amount]
- [item]: $[amount]
(list every line item)

SUBTOTAL: $[amount]
TAX: $[amount if shown]
TOTAL: $[amount]

MATERIALS SPECIFIED: [list any specific brands, models, or product lines mentioned]
WARRANTY: [any warranty terms mentioned]
FINANCING: [any financing terms if shown]

RED FLAGS: [anything that looks unusual, vague, or missing that a homeowner should know about]

NOTES: [anything else visible that Jake should know before calling this homeowner back]

If any section is not visible in the image, write "not shown". Be thorough — Jake uses this to prepare before his follow-up call.`,
          },
        ],
      },
    ],
  });

  return res.status(200).json({ analysis: message.content[0].text });
}
