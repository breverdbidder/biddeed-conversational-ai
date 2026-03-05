/**
 * BidDeed.AI — Cloudflare Pages Function
 * Route: /api/chat  (POST)
 * Primary: LiteLLM Smart Router (biddeed-litellm.onrender.com)
 * Fallback: Anthropic API direct (claude-sonnet-4-20250514)
 * Updated: 2026-03-05 · V16.5 House Brand
 */

const LITELLM_URL   = "https://biddeed-litellm.onrender.com/chat/completions";
const ANTHROPIC_URL = "https://api.anthropic.com/v1/messages";
const ANTHROPIC_MODEL = "claude-sonnet-4-5-20250929";

const SYSTEM_PROMPT = `You are BidDeed.AI — an autonomous foreclosure auction intelligence system for Brevard County, Florida. You orchestrate four AI capabilities: Perceptive (data scraping), Semantic (lien interpretation), Analytical (XGBoost + max bid formula), and Agentic (12-stage Everest Ascent pipeline).

LIVE AUCTION DATA — Brevard County · March 5, 2026:

PROPERTY 1 — 1737 Guldahl Dr, Titusville 32780
Decision: REVIEW | Max Bid: $143,393 | Market: $223,380 | AVM: $299,133 | Judgment: MISSING
3bd/2ba · 1,683 sqft · Single Family · Built 1966 | Case: PO-419795 | Last Sale: $308,300
Note: AVM $75K above market — strong equity gap. Judgment missing = AcclaimWeb pull required before bidding.

PROPERTY 2 — 310 Crestview St NE, Palm Bay 32907
Decision: REVIEW | Max Bid: $112,937 | Market: $239,910 | Judgment: $219,709 | Ratio: 91.6%
3bd/2ba · 1,714 sqft · Single Family | Case: PO-419045
Note: Viable spread at 91.6% bid ratio. Lien stack unverified — title pull required before auction.

PROPERTY 3 — 915 Jamestown Ave #99, Indian Harbour Beach 32937
Decision: SKIP | Max Bid: $94,490 | Market: $151,250 | Opening Bid: $219,675 | Ratio: 145.2%
2bd/1.5ba · 1,088 sqft · Condominium · Built 1964 | Case: PO-419203
Note: Opening bid $68K above market. No equity. Hard skip.

PROPERTY 4 — 3206 Galleon Ave NE, Palm Bay 32905
Decision: SKIP | Max Bid: $95,145 | Market: $207,350 | Judgment: $344,626 | Ratio: 166.2%
3bd/2ba · 1,166 sqft · Single Family · Built 1973 | Case: PO-419045
Note: Judgment $137K over market. Hard skip.

PROPERTY 5 — 1784 Middlebury Dr SE, Palm Bay 32909
Decision: SKIP | Max Bid: $154,710 | Market: $327,860 | Judgment: $494,190 | Ratio: 150.7%
2,023 sqft · New Construction 2022 | Case: PO-419852 | Last Sale: $396,000
Note: Opening bid $166K above market. Hard skip.

AUCTION SUMMARY: 5 properties · 0 BID · 2 REVIEW · 3 SKIP
Top pick: 1737 Guldahl Dr (strongest AVM gap — verify judgment via AcclaimWeb).
Second: 310 Crestview St (91.6% ratio, viable if lien stack is clean).
Priority zips: 32937 Indian Harbour Beach · 32940 Melbourne/Viera

Max Bid Formula: (ARV × 70%) − Repairs − $10,000 − MIN($25,000, 15% × ARV)

Rules:
- Be direct. Lead with numbers. No preamble.
- Flag missing data immediately.
- Never say "AI-powered" — say the specific capability: Perceptive / Semantic / Analytical / Agentic.
- SKIP properties are hard stops.
- Always recommend AcclaimWeb verification before bidding on REVIEW properties.`;

async function callLiteLLM(messages, model, apiKey) {
  const resp = await fetch(LITELLM_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${apiKey}`
    },
    body: JSON.stringify({ model: model || "PREMIUM", max_tokens: 1024, messages })
  });
  const data = await resp.json();
  if (!resp.ok || data.error) throw new Error(data.error?.message || `LiteLLM ${resp.status}`);
  return data.choices?.[0]?.message?.content || "";
}

async function callAnthropic(messages, apiKey) {
  const resp = await fetch(ANTHROPIC_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": apiKey,
      "anthropic-version": "2023-06-01"
    },
    body: JSON.stringify({
      model: ANTHROPIC_MODEL,
      max_tokens: 1024,
      system: SYSTEM_PROMPT,
      messages
    })
  });
  const data = await resp.json();
  if (!resp.ok) throw new Error(data.error?.message || `Anthropic ${resp.status}`);
  return data.content?.[0]?.text || "";
}

export async function onRequestPost(context) {
  const { request, env } = context;
  try {
    const body = await request.json();
    const messages = body.messages || [];
    const fullMessages = [{ role: "system", content: SYSTEM_PROMPT }, ...messages];
    
    let text = "";
    let source = "litellm";

    // Try LiteLLM first, fallback to Anthropic direct
    try {
      text = await callLiteLLM(fullMessages, body.model, env.LITELLM_MASTER_KEY || env.ANTHROPIC_API_KEY);
    } catch (litellmErr) {
      source = "anthropic-direct";
      text = await callAnthropic(messages, env.ANTHROPIC_API_KEY);
    }

    return new Response(JSON.stringify({ success: true, response: text, source }), {
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });

  } catch (error) {
    return new Response(JSON.stringify({ success: false, error: error.message }), {
      status: 500,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
    });
  }
}

export async function onRequestOptions() {
  return new Response(null, {
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization"
    }
  });
}
