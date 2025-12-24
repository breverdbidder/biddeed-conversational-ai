# BidDeed.AI Conversational Foreclosure Agent

🤖 **Manus-inspired autonomous AI agent for Brevard County foreclosure research**

## Live Demo

🌐 **https://biddeed-conversational-ai.pages.dev**

## Features

### 💬 Split-Screen Interface
- **Chat Panel**: Natural language conversation with Claude AI
- **Agent Workspace**: Live activity feed, property results, pipeline progress
- **Quick Actions**: One-click common queries

### 🎙️ Voice Activation
- Web Speech API integration
- Click microphone to speak queries
- Automatic speech-to-text conversion

### 🤖 Autonomous Agent
- **NLP Query Parser**: Understands foreclosure-specific intents
- **Multi-Node Workflow**: LangGraph orchestrator with 8 processing nodes
- **Context Engineering**: Manus-inspired architecture for complex tasks

### 📊 Foreclosure Intelligence
- 22 real Brevard County properties
- ML-powered recommendations (BID/REVIEW/SKIP)
- Max bid calculations using BidDeed formula
- Plaintiff pattern analysis
- Lien priority detection

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                BidDeed.AI Conversational Agent              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐         ┌─────────────────┐           │
│  │   Chat Panel    │         │  Agent Workspace │           │
│  │                 │         │                  │           │
│  │ • Voice input   │◀───────▶│ • Activity feed  │           │
│  │ • Quick actions │         │ • Results tab    │           │
│  │ • Messages      │         │ • Pipeline view  │           │
│  └─────────────────┘         └─────────────────┘           │
│           │                           │                     │
│           ▼                           ▼                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              LangGraph Orchestrator                  │   │
│  │                                                      │   │
│  │  Node 1: Parse Query      Node 5: Max Bid Calc      │   │
│  │  Node 2: Fetch Properties Node 6: ML Scoring        │   │
│  │  Node 3: Enrich (BCPAO)   Node 7: Generate Report   │   │
│  │  Node 4: Lien Analysis    Node 8: Save Results      │   │
│  └─────────────────────────────────────────────────────┘   │
│           │                           │                     │
│           ▼                           ▼                     │
│  ┌─────────────┐           ┌─────────────────┐             │
│  │  Supabase   │           │  Claude API     │             │
│  │  Database   │           │  (Sonnet 4)     │             │
│  └─────────────┘           └─────────────────┘             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Query Examples

```
"Show me BID properties for Jan 7"
"Analyze 923 Slocum St Palm Bay"
"Which plaintiffs have highest third-party rates?"
"Explain lien priority in foreclosures"
"Run full pipeline on next auction"
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | HTML/CSS/JS (Single-page) |
| Chat UI | Split-screen responsive |
| Voice | Web Speech API |
| Backend | Cloudflare Workers |
| AI | Claude Sonnet 4 (Anthropic API) |
| Orchestration | LangGraph (Python) |
| Database | Supabase |
| Hosting | Cloudflare Pages |

## Deployment

Automatically deploys to Cloudflare Pages on push to `main`:

```yaml
# .github/workflows/deploy.yml
wrangler pages deploy public --project-name=biddeed-conversational-ai
```

## Environment Variables

```
ANTHROPIC_API_KEY=your_api_key
SUPABASE_URL=https://mocerqjnksmhcjzxrewo.supabase.co
SUPABASE_KEY=your_service_role_key
```

## Related Projects

- [brevard-bidder-scraper](https://github.com/breverdbidder/brevard-bidder-scraper) - Main pipeline
- [brevard-bidder-landing](https://github.com/breverdbidder/brevard-bidder-landing) - Landing page
- [Foreclosure Map](https://brevard-bidder-landing.pages.dev/map) - Interactive map

## License

Proprietary - Everest Capital USA

---

**Built with BidDeed.AI V16.4.0** | Manus-inspired architecture
