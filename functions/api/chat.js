/**
 * BidDeed.AI — Cloudflare Pages Function
 * Route: /api/chat  (POST)
 * LLM: LiteLLM Smart Router → https://biddeed-litellm.onrender.com
 * Models: FREE (Gemini 2.5 Flash) | ULTRA_CHEAP (DeepSeek V3.2) | PREMIUM (Claude Sonnet 4.5)
 * Updated: 2026-03-05 · V3 House Brand
 */

const LITELLM_URL   = "https://biddeed-litellm.onrender.com/chat/completions";
const DEFAULT_MODEL = "PREMIUM"; // Claude Sonnet 4.5 for auction decisions

const SYSTEM_PROMPT = `You are BidDeed.AI — an autonomous foreclosure auction intelligence system for Brevard County, Florida. You orchestrate four AI capabilities: Perceptive (data scraping), Semantic (lien interpretation), Analytical (XGBoost + max bid formula), and Agentic (12-stage Everest Ascent pipeline).

LIVE AUCTION DATA — Brevard County · March 4, 2026:

PROPERTY 1 — 1737 Guldahl Dr, Titusville 32780
Decision: REVIEW | Max Bid: $143,393 | Market: $223,380 | AVM: $299,133 | Judgment: MISSING
3bd/2ba · 1,683 sqft · Single Family · Built 1966 | Case: PO-419795 | Last Sale: $308,300
Note: AVM $75K above market — strong equity gap. Judgment missing = AcclaimWeb pull required.

PROPERTY 2 — 310 Crestview St NE, Palm Bay 32907
Decision: REVIEW | Max Bid: $112,937 | Market: $239,910 | Judgment: $219,709 | Ratio: 91.6%
3bd/2ba · 1,714 sqft · Single Family | Case: PO-419045
Note: Viable spread at 91.6% bid ratio. Lien stack unverified — title pull before auction.

PROPERTY 3 — 915 Jamestown Ave #99, Indian Harbour Beach 32937
Decision: SKIP | Max Bid: $94,490 | Market: $151,250 | Opening Bid: $219,675 | Ratio: 145.2%
2bd/1.5ba · 1,088 sqft · Condominium · Built 1964 | Case: PO-419203
Note: Opening bid $68K above market. No equity for third-party bidder.

PROPERTY 4 — 3206 Galleon Ave NE, Palm Bay 32905
Decision: SKIP | Max Bid: $95,145 | Market: $207,350 | Judgment: $344,626 | Ratio: 166.2%
3bd/2ba · 1,166 sqft · Single Family · Built 1973 | Case: PO-419045
Note: Judgment $137K over market. Hard skip.

PROPERTY 5 — 1784 Middlebury Dr SE, Palm Bay 32909
Decision: SKIP | Max Bid: $154,710 | Market: $327,860 | Judgment: $494,190 | Ratio: 150.7%
2,023 sqft · New Construction 2022 | Case: PO-419852 | Last Sale: $396,000
Note: Opening bid $166K above market. Skip.

AUCTION SUMMARY: 5 properties · 0 BID · 2 REVIEW · 3 SKIP
Top pick: Guldahl Dr (strongest AVM gap). Second: Crestview St (needs lien verify).
Priority zips: 32937 Indian Harbour Beach · 32940 Melbourne/Viera

Max Bid Formula: (ARV × 70%) − Repairs − $10,000 − MIN($25,000, 15% × ARV)

Rules:
- Be direct. Lead with numbers.
- Flag missing data immediately (judgment, AVM, taxes).
- Never say "AI-powered" — say the specific capability: Perceptive / Semantic / Analytical / Agentic.
- SKIP properties are hard stops. Do not suggest bidding on them.`;

export async function onRequestPost(context) {
  const { request, env } = context;

  try {
    const body = await request.json();
    const messages = body.messages || [];
    const model    = body.model || DEFAULT_MODEL;

    // LiteLLM uses OpenAI-compatible format
    const llmResponse = await fetch(LITELLM_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${env.LITELLM_API_KEY || env.ANTHROPIC_API_KEY}`
      },
      body: JSON.stringify({
        model,
        max_tokens: 1024,
        messages: [
          { role: "system", content: SYSTEM_PROMPT },
          ...messages
        ]
      })
    });

    const data = await llmResponse.json();

    // LiteLLM returns OpenAI-format: choices[0].message.content
    const text = data.choices?.[0]?.message?.content
      || data.content?.[0]?.text  // fallback: Anthropic direct format
      || "No response generated";

    return new Response(JSON.stringify({
      success: true,
      response: text,
      model: data.model || model,
      usage: data.usage
    }), {
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
      }
    });

  } catch (error) {
    return new Response(JSON.stringify({
      success: false,
      error: error.message
    }), {
      status: 500,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
      }
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
