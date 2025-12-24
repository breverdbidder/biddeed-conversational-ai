# BidDeed.AI Conversational Agent

Manus-style autonomous foreclosure research agent for Brevard County, Florida.

## 🚀 Live Demo

**https://brevard-bidder-landing.pages.dev/agent**

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  BidDeed Conversational Agent               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐     ┌────────────────────────────────┐│
│  │   CHAT PANEL    │     │      AGENT WORKSPACE           ││
│  │                 │     │                                ││
│  │  💬 Messages    │     │  📊 Activity Log               ││
│  │  🎤 Voice Input │     │  🏠 Property Results Grid      ││
│  │  ⚡ Quick Actions│     │  💻 Terminal View              ││
│  └─────────────────┘     └────────────────────────────────┘│
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │              LangGraph Agent Pipeline                   ││
│  │                                                         ││
│  │  query_parser → property_search → investment_analysis   ││
│  │                                  ↓                      ││
│  │                         response_generator              ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

## Features

- **Split-screen UI** - Chat + Agent Workspace
- **Voice Input** - Web Speech API integration
- **LangGraph Pipeline** - ReAct pattern agent
- **Real Data** - 22 Brevard County foreclosures
- **ML Scores** - 64.4% accuracy predictions

## Stack

| Component | Technology |
|-----------|------------|
| Frontend | Vanilla JS + CSS |
| Agent | LangGraph (Python) |
| Database | Supabase + pgvector |
| Hosting | Cloudflare Pages |
| CI/CD | GitHub Actions |

## Files

```
biddeed-conversational-ai/
├── src/
│   └── agents/
│       └── foreclosure_agent.py    # LangGraph agent
├── sql/
│   └── pgvector_migration.sql      # Vector search setup
├── .github/
│   └── workflows/
│       └── agent_pipeline.yml      # Autonomous execution
└── README.md
```

## Usage

### Web Interface
Visit https://brevard-bidder-landing.pages.dev/agent

### GitHub Actions
```bash
# Trigger agent via workflow dispatch
gh workflow run agent_pipeline.yml -f query="Show BID recommendations"
```

### API (Future)
```javascript
// Repository dispatch
await fetch('https://api.github.com/repos/breverdbidder/biddeed-conversational-ai/dispatches', {
  method: 'POST',
  headers: { Authorization: 'token YOUR_TOKEN' },
  body: JSON.stringify({
    event_type: 'agent-query',
    client_payload: { query: 'Analyze 923 Slocum St' }
  })
});
```

## Query Examples

| Query | Response |
|-------|----------|
| "Show BID recommendations" | List of BID-rated properties |
| "Next auction date" | Jan 7, 2025 details |
| "Analyze 923 Slocum St" | Full property analysis |
| "Best opportunities" | Top ML-scored investments |
| "Properties to skip" | SKIP list with reasons |

## Inspired By

- [OpenManus](https://github.com/FoundationAgents/OpenManus) - Open-source AI agent framework
- [LangGraph](https://github.com/langchain-ai/langgraph) - Agent orchestration

---

**Everest Capital USA** | BidDeed.AI V16.5.0
