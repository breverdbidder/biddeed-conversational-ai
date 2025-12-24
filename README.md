# BidDeed.AI Conversational Agent

Autonomous foreclosure research platform for Brevard County, Florida investors.

## 🚀 Live V16.5.0

| Interface | URL |
|-----------|-----|
| 🤖 Agent | https://brevard-bidder-landing.pages.dev/agent |
| 🗺️ Map | https://brevard-bidder-landing.pages.dev/map |
| 💬 Chat | https://brevard-bidder-landing.pages.dev/chat |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  BidDeed.AI V16.5.0                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  /agent                /map                  /chat          │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐│
│  │ Split-Screen │     │ Leaflet Map  │     │ Standalone   ││
│  │ Agent + Chat │     │ All Brevard  │     │ Chat Only    ││
│  │ Workspace    │     │ Foreclosures │     │              ││
│  └──────────────┘     └──────────────┘     └──────────────┘│
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │        Cloudflare Pages Functions (/api/chat)           ││
│  │                       ↓                                 ││
│  │  Smart Router V5 → Gemini 2.5 Flash (FREE default)      ││
│  │                  → Claude Sonnet 4.5 (complex queries)  ││
│  └─────────────────────────────────────────────────────────┘│
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │              LangGraph Agent Pipeline                   ││
│  │  query_parser → property_search → investment_analysis   ││
│  │                                  ↓                      ││
│  │                         response_generator              ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

## Features

### Agent UI (`/agent`)
- Split-screen: Chat panel + Agent workspace
- Voice input via Web Speech API
- Activity log with real-time actions
- Property results grid
- Terminal view for debugging

### Map (`/map`)
- Leaflet dark-mode map of Brevard County
- Color-coded markers: BID (green), REVIEW (yellow), SKIP (red)
- Filter controls by recommendation type
- Property popups with key metrics
- Stats panel: total judgment, counts by category

### Chat (`/chat`)
- Standalone conversational interface
- Suggested prompts for quick starts
- Markdown rendering in responses
- Mobile-optimized layout

## Stack

| Component | Technology |
|-----------|------------|
| Frontend | Vanilla JS + CSS (no frameworks) |
| Maps | Leaflet + CartoDB Dark tiles |
| Agent | LangGraph (Python) |
| Database | Supabase (PostgreSQL + pgvector) |
| Hosting | Cloudflare Pages |
| Functions | Cloudflare Workers |
| CI/CD | GitHub Actions |
| LLM Router | Smart Router V5 (Gemini FREE default) |

## Environment Variables

For Cloudflare Pages Functions:

```bash
ANTHROPIC_API_KEY=sk-ant-...  # Claude API
GOOGLE_API_KEY=...            # Gemini 2.5 Flash (FREE tier)
SUPABASE_URL=https://...supabase.co
SUPABASE_KEY=eyJ...
```

## Project Structure

```
biddeed-conversational-ai/
├── public/
│   ├── index.html          # Root landing
│   ├── agent.html          # Agent UI
│   ├── map.html            # Leaflet map
│   ├── chat.html           # Chat interface
│   └── _redirects          # Clean URL routing
├── functions/
│   └── api/
│       └── chat.js         # Cloudflare Worker
├── src/
│   └── agents/
│       └── foreclosure_agent.py
├── agents/                 # LangGraph nodes
├── sql/
│   └── pgvector_migration.sql
├── .github/
│   └── workflows/
│       └── agent_pipeline.yml
└── README.md
```

## Query Examples

| Query | Response |
|-------|----------|
| "What auctions are coming up?" | Next auction dates and property counts |
| "Show BID recommendations" | List of BID-rated properties |
| "Analyze 923 Slocum St" | Full property analysis with max bid |
| "Market trends in Satellite Beach" | Local market insights |
| "Calculate max bid for $200K judgment" | Formula breakdown |

## API Usage

### Chat Endpoint
```javascript
const response = await fetch('https://brevard-bidder-landing.pages.dev/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    messages: [{ role: 'user', content: 'Show BID recommendations' }]
  })
});
const data = await response.json();
console.log(data.response);
```

### GitHub Actions Trigger
```bash
gh workflow run agent_pipeline.yml -f query="Analyze upcoming auctions"
```

## Key Formulas

```
Max Bid = (ARV × 70%) - Repairs - $10K - MIN($25K, 15% × ARV)

Recommendation:
  Bid/Judgment ≥ 75% → BID
  Bid/Judgment 60-74% → REVIEW
  Bid/Judgment < 60% → SKIP
```

## Data Sources

- **RealForeclose** - Auction listings, case numbers
- **BCPAO** - Property data, photos, tax values
- **AcclaimWeb** - Lien searches, mortgage records
- **Census API** - Demographics, income levels

## Development

```bash
# Local development (static files only)
npx serve public

# Deploy to Cloudflare Pages
git push origin main  # Auto-deploys via GitHub integration
```

---

**Everest Capital USA** | BidDeed.AI V16.5.0 | Dec 24, 2025
