/**
 * BidDeed.AI - Claude API Worker Function
 * Handles chat requests via Anthropic API
 */

export async function onRequestPost(context) {
  const { request, env } = context;
  
  try {
    const { messages, query } = await request.json();
    
    // System prompt for foreclosure assistant
    const systemPrompt = `You are BidDeed.AI, an expert foreclosure research assistant for Brevard County, Florida. You help real estate investors analyze foreclosure auctions.

Your capabilities:
- Search and filter foreclosure properties by recommendation (BID/REVIEW/SKIP), date, and city
- Analyze specific properties including judgment amount, max bid calculation, ML scores
- Explain lien priority and title issues
- Provide plaintiff pattern analysis
- Run the Everest Ascent 12-stage pipeline

Key formulas you use:
- Max Bid = (ARV × 70%) - Repairs - $10K - MIN($25K, 15% of ARV)
- Bid/Judgment Ratio: ≥75% = BID, 60-74% = REVIEW, <60% = SKIP

Current auctions in database:
- Dec 3, 2025: 6 properties (completed)
- Dec 17, 2025: 12 properties (completed)
- Jan 7, 2025: 4 properties (upcoming at Titusville Courthouse, 11 AM)

Be concise, professional, and action-oriented. Use markdown formatting for readability.`;

    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': env.ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 1024,
        system: systemPrompt,
        messages: messages || [{ role: 'user', content: query }]
      })
    });

    const data = await response.json();
    
    return new Response(JSON.stringify({
      success: true,
      response: data.content?.[0]?.text || 'No response generated',
      usage: data.usage
    }), {
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      }
    });
    
  } catch (error) {
    return new Response(JSON.stringify({
      success: false,
      error: error.message
    }), {
      status: 500,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      }
    });
  }
}

export async function onRequestOptions() {
  return new Response(null, {
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    }
  });
}
