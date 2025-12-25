---
name: github-repo-hunter
description: Automatically discovers, evaluates, and integrates relevant GitHub repositories into BidDeed.AI and Life OS projects. Use when (1) User requests to find GitHub projects related to specific technologies or domains, (2) Seeking automation tools, libraries, or open-source solutions that could enhance existing workflows, (3) Researching best practices from successful open-source projects, (4) Building comprehensive tool/API libraries. The skill hunts repositories, analyzes relevance, generates integration summaries, and alerts Ariel with actionable recommendations.
---

# GitHub Repository Hunter

Automatically discover, evaluate, and integrate relevant GitHub repositories into your projects.

## Workflow

### Step 1: Define Search Criteria

Based on user request, identify:
- **Domain/Technology** (e.g., "foreclosure data scrapers", "real-time collaboration", "Markdown parsers")
- **Target Project** (BidDeed.AI, Life OS, or both)
- **Integration Context** (API enhancement, workflow automation, developer tools, etc.)

### Step 2: Execute Multi-Query Search

Use `web_search` tool with GitHub-specific strategies:

**Search Pattern:**
```
site:github.com [domain keywords] stars:>100 pushed:>2024-01-01
```

**Multi-angle search strategy:**
1. **Primary keywords** - Direct domain terms
2. **Technology stack** - Specific frameworks ("LangGraph", "FastAPI", "Supabase")
3. **Problem statement** - What the tool solves ("email parsing automation", "job tracking")
4. **Alternative phrasing** - Synonyms and related concepts

**Example searches:**
- `site:github.com foreclosure auction scraper Python stars:>50`
- `site:github.com ADHD productivity task management stars:>100`
- `site:github.com email parser IMAP automation language:Python`

### Step 3: Repository Evaluation

For each discovered repository, analyze using `web_fetch` to load README:

**Relevance Scoring (0-100):**
- **Domain alignment** (0-30 pts): How well it matches the search intent
- **Code quality** (0-20 pts): Stars (>1000=20, >500=15, >100=10, <100=5)
- **Documentation** (0-15 pts): README quality, examples, API docs
- **License compatibility** (0-10 pts): MIT/Apache=10, GPLv3=8, Other=5
- **Maintenance** (0-15 pts): Last commit within 6 months=15, 1 year=10, older=5
- **Community** (0-10 pts): Forks, contributors, issue resolution

**Threshold:** Repositories scoring ≥60 proceed to integration analysis.

### Step 4: Generate Integration Summary

Create structured analysis for qualifying repositories:

```markdown
## [Repository Name]
**GitHub:** [URL]  
**Stars:** ⭐ [count] | **Language:** [primary] | **License:** [type]  
**Relevance Score:** [0-100]/100 | **Target:** [BidDeed.AI/Life OS/Both]

### What It Does
[2-3 sentence summary from README]

### Key Features
- [Feature 1]
- [Feature 2]
- [Feature 3]

### Integration Opportunity
**Problem Solved:** [Specific pain point it addresses]  
**Implementation Path:** [API call / library import / workflow pattern / fork & customize]  
**Estimated Effort:** [Low (< 1 hour) / Medium (1-4 hours) / High (1+ day)]  
**Dependencies:** [Required packages, services, or configurations]

### Quick Start Example
```[language]
[Minimal working example - 5-10 lines showing key functionality]
```

### Considerations
- [Potential concern 1 - e.g., "Requires Redis server"]
- [Potential concern 2 - e.g., "Last updated 8 months ago"]
- [Benefit/Trade-off - e.g., "Mature codebase, well-tested"]
```

### Step 5: Archive to Supabase

Use GitHub Actions workflow to insert findings. See `references/supabase_integration.md` for complete workflow dispatch examples.

**Supabase Schema (insights table):**
```json
{
  "category": "github_discovery",
  "subcategory": "biddeed" | "life_os" | "both",
  "title": "RepoName - Value Proposition",
  "content": {
    "repo_url": "https://github.com/...",
    "stars": 1234,
    "language": "Python",
    "license": "MIT",
    "relevance_score": 85,
    "target_project": "BidDeed.AI",
    "summary": "...",
    "features": [...],
    "integration": {
      "problem_solved": "...",
      "implementation": "...",
      "effort": "Low|Medium|High",
      "dependencies": [...]
    },
    "quick_start": "...",
    "considerations": [...]
  }
}
```

### Step 6: Alert Ariel

Present discovery summary directly in chat:

```
🎯 **GitHub Discovery Complete**

Found **[N] relevant repositories** for **[Project Name]**

**🏆 Top Pick: [Repo Name]** (⭐ [stars], Score: [XX]/100)
[One-line description]

**💡 Integration Opportunity:**
[Quick summary of how it helps]

**⚡ Quick Start:**
```[language]
[2-3 line code snippet]
```

**🔗 Repository:** [GitHub URL]

---

**📦 Other High-Scoring Repos:**
• **[Repo 2]** (⭐ [stars], Score: [XX]/100) - [Value prop]
• **[Repo 3]** (⭐ [stars], Score: [XX]/100) - [Value prop]

**💾 Archived:** All discoveries saved to Supabase `insights` table
```

## Search Strategies by Domain

See `references/search_strategies.md` for comprehensive keyword lists and examples for BidDeed.AI and Life OS domains.

## Execution Pattern

**When triggered by user request:**

1. **Parse intent** - Extract domain, technology, target project
2. **Generate 3-5 search queries** - Multiple angles on the topic
3. **Execute searches** - Use `web_search` with GitHub site filter
4. **Fetch top 5-10 repos** - Use `web_fetch` on promising results
5. **Score each repo** - Apply relevance algorithm
6. **Filter by threshold** - Keep score ≥ 60
7. **Generate summaries** - Structured analysis for each
8. **Archive to Supabase** - Via GitHub Actions workflow
9. **Present to Ariel** - Formatted discovery report

**Time estimate:** 2-5 minutes for typical discovery session

## Advanced Techniques

### Smart Filtering

**Exclude noise:**
- Skip forks unless more popular than original
- Filter out archived repositories
- Ignore repos with no commits in 18+ months (unless highly starred)
- Avoid tutorial/learning repos (unless specifically requested)

**Quality signals:**
- Has CI/CD badges (GitHub Actions, Travis, CircleCI)
- Comprehensive README with examples
- Active issues/PRs (shows community engagement)
- Tests directory exists
- Clear installation/setup instructions

### Cross-Reference Existing Stack

Before recommending, check if functionality already exists:
- **BidDeed.AI:** Review existing integrations, avoid duplication
- **Life OS:** Check current workflows, installed packages
- **Note alternatives** when new repo would replace/enhance existing tool

### Batch Discovery Mode

Process multiple discovery requests sequentially when user provides list of topics.

## Best Practices

1. **Quality over quantity** - Better to find 3 excellent repos than 20 mediocre ones
2. **Test before recommending** - Actually visit the repo, read README, check examples
3. **Consider maintenance** - Active repos > abandoned high-star repos
4. **License awareness** - Verify compatibility before suggesting integration
5. **Document reasoning** - Explain WHY a repo scores high/low
6. **Cross-reference** - Check if similar functionality already exists in stack
7. **Realistic effort estimates** - Don't underestimate integration complexity

## Troubleshooting

**GitHub rate limits:**
- Use `web_search` instead of direct GitHub API calls
- Space out `web_fetch` requests (2-3 seconds between)
- Cache results to avoid re-fetching

**Low-quality results:**
- Refine search keywords (be more specific)
- Add date filters: `pushed:>2024-01-01`
- Increase star threshold: `stars:>500`
- Filter by language: `language:Python`

**Irrelevant matches:**
- Use exclusion: `-tutorial -example -learning -course`
- Add domain-specific keywords
- Check "awesome lists" for curated options