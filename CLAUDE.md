# CLAUDE.md - BidDeed.AI Conversational Agent

## Project Context
BidDeed.AI V16.5.0 - Agentic AI foreclosure research platform for Brevard County, Florida.

## URLs
- Agent: https://brevard-bidder-landing.pages.dev/agent
- Map: https://brevard-bidder-landing.pages.dev/map
- Chat: https://brevard-bidder-landing.pages.dev/chat
- Repo: https://github.com/breverdbidder/biddeed-conversational-ai

## Stack
- Frontend: Vanilla JS + CSS (no React/Vue)
- Maps: Leaflet 1.9.4 + CartoDB Dark tiles
- Backend: Cloudflare Pages Functions
- Database: Supabase (PostgreSQL)
- LLM: Smart Router V5 (Gemini 2.5 Flash FREE default)

## Key Files
```
public/
├── agent.html    # Main agent UI (split-screen)
├── map.html      # Leaflet foreclosure map
├── chat.html     # Standalone chat
├── _redirects    # URL routing
functions/api/
└── chat.js       # Cloudflare Worker for LLM calls
```

## Deployment
Auto-deploys to Cloudflare Pages on `git push origin main`.

## Environment Variables (Cloudflare Pages)
```
ANTHROPIC_API_KEY
GOOGLE_API_KEY
SUPABASE_URL
SUPABASE_KEY
```

## Coding Standards
- Single-file HTML with inline CSS/JS (no build step)
- CSS variables for theming
- Mobile-first responsive design
- Dark mode default
- No external dependencies except CDN libraries

## Design System
```css
:root {
  --bg: #0a0a0f;
  --bg2: #12121a;
  --bg3: #1a1a24;
  --border: #2a2a3a;
  --text: #f0f0f5;
  --text2: #8888a0;
  --accent: #38bdf8;
  --purple: #a78bfa;
  --success: #22c55e;
  --warn: #eab308;
  --error: #ef4444;
}
```

## Commands

### Test locally
```bash
npx serve public
```

### Deploy
```bash
git add -A && git commit -m "Update" && git push
```

### Check status
```bash
curl -s -o /dev/null -w "%{http_code}" https://brevard-bidder-landing.pages.dev/agent
```

## Agentic Execution Rules
1. NEVER ask permission - execute and report
2. Update this file when architecture changes
3. Test all endpoints after deployment
4. Push directly to main branch
5. Use GitHub API for file updates (no git clone)

## Related Repos
- `breverdbidder/brevard-bidder-scraper` - Original scraper + pipelines
- `breverdbidder/life-os` - Personal Life OS system

## Owner
Ariel Shapira - Solo Founder, Everest Capital USA
