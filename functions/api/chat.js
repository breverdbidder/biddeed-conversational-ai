/**
 * BidDeed.AI — Cloudflare Pages Function
 * Route: /api/chat  (POST)
 * V4 — Live Supabase + Anthropic · March 5, 2026
 * 
 * Queries multi_county_auctions (245K+ rows) for real auction data
 * Injects live context into Claude system prompt
 */

const SUPABASE_URL = "https://mocerqjnksmhcjzxrewo.supabase.co";
const ANTHROPIC_URL = "https://api.anthropic.com/v1/messages";
const ANTHROPIC_MODEL = "claude-sonnet-4-5-20250929";
const LITELLM_URL = "https://biddeed-litellm.onrender.com/chat/completions";

// ── Supabase REST helper ──
async function querySupabase(table, params, env) {
  const key = env.SUPABASE_SERVICE_KEY || env.SUPABASE_SERVICE_ROLE_KEY || env.SUPABASE_ANON_KEY;
  if (!key) return null;
  
  const url = `${SUPABASE_URL}/rest/v1/${table}?${params}`;
  try {
    const resp = await fetch(url, {
      headers: {
        "apikey": key,
        "Authorization": `Bearer ${key}`,
        "Content-Type": "application/json",
        "Prefer": "count=exact"
      }
    });
    if (!resp.ok) return null;
    const count = resp.headers.get("content-range")?.split("/")?.[1] || null;
    const data = await resp.json();
    return { data, count };
  } catch { return null; }
}

// ── Build live auction context from Supabase ──
async function buildLiveContext(env) {
  // Get upcoming/active auctions (next 30 days)
  const upcoming = await querySupabase(
    "multi_county_auctions",
    "select=county,case_number,address,city,zip,judgment_amount,market_value,auction_date,status,plaintiff,opening_bid,po_sold_amount&order=auction_date.asc&limit=25&auction_date=gte." + new Date().toISOString().split("T")[0],
    env
  );

  // Get total counts
  const totals = await querySupabase(
    "multi_county_auctions",
    "select=id&limit=1",
    env
  );

  // Get county breakdown
  const counties = await querySupabase(
    "multi_county_auctions",
    "select=county&limit=1000&auction_date=gte." + new Date().toISOString().split("T")[0],
    env
  );

  let context = "";
  
  if (totals?.count) {
    context += `\nDATABASE: ${parseInt(totals.count).toLocaleString()} total auction records in Supabase.\n`;
  }

  if (counties?.data) {
    const countByCounty = {};
    counties.data.forEach(r => { countByCounty[r.county] = (countByCounty[r.county] || 0) + 1; });
    const countyList = Object.entries(countByCounty)
      .sort((a, b) => b[1] - a[1])
      .map(([c, n]) => `${c}: ${n}`)
      .join(", ");
    context += `UPCOMING AUCTIONS BY COUNTY: ${countyList}\n`;
  }

  if (upcoming?.data?.length) {
    context += `\nLIVE AUCTION DATA — ${upcoming.data.length} upcoming properties:\n\n`;
    upcoming.data.forEach((p, i) => {
      const jdg = p.judgment_amount ? `$${Number(p.judgment_amount).toLocaleString()}` : "MISSING";
      const mkt = p.market_value ? `$${Number(p.market_value).toLocaleString()}` : "N/A";
      const open = p.opening_bid ? `$${Number(p.opening_bid).toLocaleString()}` : "N/A";
      const ratio = (p.judgment_amount && p.market_value) 
        ? ((p.market_value / p.judgment_amount) * 100).toFixed(1) + "%"
        : "N/A";
      
      // Calculate max bid: (Market × 70%) − $10K − MIN($25K, 15% × Market)
      let maxBid = "N/A";
      let recommendation = "REVIEW";
      if (p.market_value) {
        const arv = Number(p.market_value);
        const mb = (arv * 0.70) - 10000 - Math.min(25000, arv * 0.15);
        maxBid = `$${Math.round(mb).toLocaleString()}`;
        
        if (p.judgment_amount) {
          const bjr = mb / Number(p.judgment_amount);
          if (bjr >= 0.75) recommendation = "BID";
          else if (bjr >= 0.60) recommendation = "REVIEW";
          else recommendation = "SKIP";
        }
      }

      context += `PROPERTY ${i + 1} — ${p.address || "Unknown"}, ${p.city || ""} ${p.zip || ""}\n`;
      context += `County: ${p.county || "?"} | Case: ${p.case_number || "?"} | Auction: ${p.auction_date || "?"}\n`;
      context += `Judgment: ${jdg} | Market: ${mkt} | Opening: ${open} | Max Bid: ${maxBid}\n`;
      context += `Plaintiff: ${p.plaintiff || "Unknown"} | Recommendation: ${recommendation}\n`;
      if (p.po_sold_amount) context += `Sold: $${Number(p.po_sold_amount).toLocaleString()}\n`;
      context += `\n`;
    });
  } else {
    context += "\nNOTE: No upcoming auction data retrieved from Supabase. Database may need refresh.\n";
  }

  return context;
}

// ── System prompt builder ──
function buildSystemPrompt(liveContext) {
  return `You are BidDeed.AI — an agentic foreclosure auction intelligence system covering 46 Florida counties. You orchestrate the 12-stage Everest Ascent™ pipeline through Wise-branded modules:

1. DiscoverWise — Find upcoming auctions
2. GatherWise — Pull all property data  
3. TitleWise — Verify title chain
4. LienWise — Analyze lien stack
5. TaxWise — Tax certificates
6. NeighborWise — Neighborhood intelligence
7. ScoreWise — AI bid probability score
8. BidWise — Max bid calculation (THE HERO)
9. CallWise — BID / REVIEW / SKIP decision
10. InsightWise — Full intelligence report
11. TrackWise — Disposition tracking
12. VaultWise — Archive everything

${liveContext}

Max Bid Formula: (ARV × 70%) − Repairs − $10,000 − MIN($25,000, 15% × ARV)
Bid/Judgment Ratio: ≥75% = BID, 60-74% = REVIEW, <60% = SKIP

VOICE: You speak as a wise partner who's "in the zone" working on the user's deal. Use the 5 ZoneWise voice layers:
- Layer 1 (Zoning/Domain): Show deep county-level expertise
- Layer 2 (In the Zone): Tell users you're actively working their query
- Layer 3 (Focus): Filter noise, surface what matters
- Layer 4 (Their Territory): Personalize to their county/strategy
- Layer 5 (Wise Guidance): Give judgment, not just data

Rules:
- Be direct. Lead with numbers. No preamble.
- Flag missing data immediately (especially missing judgments).
- Reference specific Wise modules when explaining your analysis.
- BidWise is the hero — every answer should get them to their number.
- SKIP properties are hard stops. Never recommend further analysis on SKIPs.
- Always recommend TitleWise + LienWise verification before bidding on REVIEW properties.
- When asked about a county, filter to that county's data.
- You are NOT generic AI. You have REAL auction data. Use it.`;
}

// ── LLM calls ──
async function callAnthropic(messages, systemPrompt, apiKey) {
  const resp = await fetch(ANTHROPIC_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": apiKey,
      "anthropic-version": "2023-06-01"
    },
    body: JSON.stringify({
      model: ANTHROPIC_MODEL,
      max_tokens: 1500,
      system: systemPrompt,
      messages
    })
  });
  const data = await resp.json();
  if (!resp.ok) throw new Error(data.error?.message || `Anthropic ${resp.status}`);
  return data.content?.[0]?.text || "";
}

async function callLiteLLM(messages, systemPrompt, apiKey) {
  const fullMessages = [{ role: "system", content: systemPrompt }, ...messages];
  const resp = await fetch(LITELLM_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${apiKey}`
    },
    body: JSON.stringify({ model: "PREMIUM", max_tokens: 1500, messages: fullMessages })
  });
  const data = await resp.json();
  if (!resp.ok || data.error) throw new Error(data.error?.message || `LiteLLM ${resp.status}`);
  return data.choices?.[0]?.message?.content || "";
}

// ── API endpoint for property list (used by chat.html sidebar) ──
async function handlePropertiesRequest(env) {
  const result = await querySupabase(
    "multi_county_auctions",
    "select=county,case_number,address,city,zip,judgment_amount,market_value,auction_date,status,plaintiff,opening_bid&order=auction_date.asc&limit=50&auction_date=gte." + new Date().toISOString().split("T")[0],
    env
  );
  
  return new Response(JSON.stringify({
    success: true,
    total: result?.count || 0,
    properties: result?.data || [],
    source: "supabase-live"
  }), {
    headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
  });
}

// ── Main handler ──
export async function onRequestPost(context) {
  const { request, env } = context;
  try {
    const body = await request.json();
    
    // If requesting property list for sidebar
    if (body.action === "list_properties") {
      return handlePropertiesRequest(env);
    }

    const messages = body.messages || [];
    
    // Build live context from Supabase
    const liveContext = await buildLiveContext(env);
    const systemPrompt = buildSystemPrompt(liveContext);
    
    let text = "";
    let source = "litellm";

    // Try LiteLLM first, fallback to Anthropic direct
    try {
      text = await callLiteLLM(messages, systemPrompt, env.LITELLM_MASTER_KEY || env.ANTHROPIC_API_KEY);
    } catch (litellmErr) {
      source = "anthropic-direct";
      text = await callAnthropic(messages, systemPrompt, env.ANTHROPIC_API_KEY);
    }

    return new Response(JSON.stringify({
      success: true,
      response: text,
      source,
      data_source: liveContext.includes("LIVE AUCTION DATA") ? "supabase-live" : "no-data",
      properties_in_context: (liveContext.match(/PROPERTY \d+/g) || []).length
    }), {
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
