# BidDeed.AI Conversational Intelligence

An AI-powered conversational interface for foreclosure investment analysis in Brevard County, Florida.

**Architecture inspired by [OpenManus](https://github.com/FoundationAgents/OpenManus)** - The open-source AI agent framework.

## 🏗️ Architecture

```
BidDeed Conversational AI
├── src/
│   ├── agents/
│   │   ├── base.py         # BaseAgent, ReActAgent (OpenManus pattern)
│   │   └── biddeed_agent.py # Main BidDeed Agent
│   ├── tools/
│   │   └── foreclosure_tools.py # Domain-specific tools
│   ├── flows/              # LangGraph workflows
│   ├── llm/                # LLM integrations
│   ├── memory/             # Conversation memory
│   └── prompts/            # Agent prompts
├── components/             # React UI components
├── config/                 # Configuration
└── public/                 # Static frontend
    └── index.html          # Split-screen chat UI
```

## 🔧 Tools (Following OpenManus BaseTool Pattern)

| Tool | Description |
|------|-------------|
| `property_search` | Search foreclosure properties by address, city, ZIP, or case number |
| `bcpao_lookup` | Get property details from Brevard County Property Appraiser |
| `lien_discovery` | Discover liens and encumbrances via AcclaimWeb |
| `max_bid_calculator` | Calculate max bid using formula: (ARV×70%)-Repairs-$10K-MIN($25K,15%ARV) |
| `auction_calendar` | Get upcoming auction dates and locations |

## 🤖 Agent Hierarchy

```
BaseAgent (abstract)
    ↓
ReActAgent (Think-Act-Observe loop)
    ↓
ToolCallAgent (Tool execution)
    ↓
BidDeedAgent (Foreclosure domain expert)
```

## ✨ Features

### Split-Screen UI
- **Left Panel**: Conversational chat interface
- **Right Panel**: Agent workspace with activity log, property cards, map

### Voice Input
- Speech-to-text for hands-free queries
- Works on mobile and desktop

### Real-Time Agent Activity
- Tool execution logs
- Property search results
- Calculation breakdowns

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/breverdbidder/biddeed-conversational-ai
cd biddeed-conversational-ai

# Run locally
python -m http.server 8080 --directory public

# Open http://localhost:8080
```

## 🔗 Live URLs

- **Chat**: https://biddeed-conversational-ai.pages.dev
- **Map**: https://brevard-bidder-landing.pages.dev/map

## 📊 Data Sources

- **Supabase**: `auction_results` table with 22 real foreclosures
- **BCPAO GIS API**: Property details, assessments, photos
- **AcclaimWeb**: Lien and mortgage records (production)
- **RealForeclose**: Auction schedules (production)

## 🧠 Inspired By

- [OpenManus](https://github.com/FoundationAgents/OpenManus) - Multi-agent AI framework
- [MetaGPT](https://github.com/geekan/MetaGPT) - Agent orchestration
- [LangGraph](https://github.com/langchain-ai/langgraph) - Workflow graphs

## 📜 License

MIT - Everest Capital USA

---

**BidDeed.AI** - Agentic AI for Foreclosure Investment  
Built by the team at Everest Capital USA
