# BidDeed.AI Conversational Agent

**Split-screen autonomous AI agent for tax deed & foreclosure investing**

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  BidDeed.AI Conversational Agent                    │
├──────────────────────┬──────────────────────────────┤
│                      │                              │
│   CONVERSATION       │    AGENT WORKSPACE           │
│   (40% width)        │    (60% width)               │
│                      │                              │
│  💬 Natural Language │  🗺️ Interactive Map          │
│     Query Interface  │  📊 Live Property Analysis   │
│                      │  🔍 Title Research           │
│  🎤 Voice Commands   │  💰 Bid Calculations         │
│                      │  📈 Market Intelligence      │
│  📝 Chat History     │                              │
│                      │  [Autonomous Agent Activity] │
│  [User Input]        │  ✓ Searching databases       │
│                      │  ✓ Analyzing comparables     │
│                      │  ✓ Checking liens            │
│                      │  ✓ Calculating ROI           │
│                      │                              │
└──────────────────────┴──────────────────────────────┘
```

## Tech Stack

- **Frontend:** React 18 + Vite + Tailwind CSS
- **AI:** Claude Sonnet 4.5 (Anthropic API)
- **Vector Search:** Supabase pgvector
- **Voice:** Web Speech API + Cloud Speech-to-Text
- **Orchestration:** LangGraph
- **Database:** Supabase (PostgreSQL)
- **Deployment:** Cloudflare Pages
- **Monitoring:** GitHub Actions

## Features

### Phase 1: Foundation ✅
- [x] Natural language query parsing
- [x] Split-screen UI
- [x] Chat interface
- [x] Agent activity display
- [x] Supabase integration

### Phase 2: Intelligence 🔄
- [ ] Vector semantic search
- [ ] Voice commands
- [ ] Mobile responsive
- [ ] Semantic caching (30-40% cost reduction)

### Phase 3: Autonomous 📅
- [ ] LangGraph orchestrator
- [ ] Automated title research
- [ ] Lien discovery
- [ ] Investment scoring
- [ ] Proactive recommendations

## Performance Targets

Based on industry benchmarks:
- Query understanding: **85-90% accuracy**
- Response time: **<500ms**
- Voice accuracy: **95%** (tax deed terminology)
- Cost per analysis: **~$2**
- Engagement lift: **20-40%**
- Time savings: **25-30%**

## Quick Start

```bash
npm install
npm run dev
```

## Environment Variables

```env
VITE_ANTHROPIC_API_KEY=sk-ant-...
VITE_SUPABASE_URL=https://...
VITE_SUPABASE_ANON_KEY=eyJ...
VITE_GOOGLE_SPEECH_API_KEY=...
```

---

Built with ❤️ by BidDeed.AI | Powered by Claude & LangGraph
