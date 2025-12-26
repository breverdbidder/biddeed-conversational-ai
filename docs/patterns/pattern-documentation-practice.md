# BidDeed.AI Pattern Documentation Practice

## Purpose
Document working patterns IMMEDIATELY after success, not after 3 failed versions. Compound knowledge through skills, not repeated debugging.

## When to Document

### ✅ ALWAYS Document After:
1. **First successful implementation** - Capture what worked while fresh
2. **Bug fix that took >30 minutes** - Prevent recurrence
3. **API integration success** - Schema, auth, rate limits
4. **Performance optimization** - Before/after metrics
5. **User-reported accuracy improvement** - Real-world validation

### ❌ NEVER Wait Until:
1. "After we refactor" - Refactors forget context
2. "When we have time" - Time never comes
3. "After 3 versions" - Pattern already forgotten
4. "End of sprint" - Details lost
5. "When it's perfect" - Perfect is enemy of documented

## Documentation Template

### Pattern Name
**One-line description**

### Context
- What problem does this solve?
- When should you use this pattern?
- When should you NOT use this pattern?

### Implementation
```language
# Working code example
# With comments explaining WHY, not just WHAT
```

### Anti-Patterns
- ❌ What doesn't work (with examples)
- Why it fails
- How to recognize you're doing it wrong

### Edge Cases
- Scenario 1: [description] → Solution: [approach]
- Scenario 2: [description] → Solution: [approach]

### Metrics
- Performance: [before] → [after]
- Accuracy: [baseline] → [improved]
- Time saved: [manual] vs [automated]

### Related Patterns
- Links to other documented patterns
- When to combine patterns
- Dependency chain

### Version History
- v1.0: Initial implementation
- v1.1: Added edge case handling for X
- v2.0: Refactored to support Y

## BidDeed.AI Specific Patterns

### Pattern: Apify YouTube Transcript Extraction

**One-line:** Extract YouTube video transcripts using Apify actor with token auth.

**Context:**
- **Use when:** Need transcripts for property walkthroughs, coaching videos, market analysis
- **Don't use when:** Video is private/unlisted, or has no captions

**Implementation:**
```python
import requests
import time

APIFY_TOKEN = "APIFY_TOKEN_FROM_ENV"
ACTOR = "starvibe~youtube-video-transcript"  # Note: ~ separator, not /

def get_transcript(video_url: str) -> str:
    # Start run
    run_response = requests.post(
        f"https://api.apify.com/v2/acts/{ACTOR}/runs?token={APIFY_TOKEN}",
        json={"youtube_url": video_url},  # Note: youtube_url not videoUrl
        headers={"Content-Type": "application/json"}
    )
    
    if run_response.status_code != 201:
        raise Exception(f"Failed to start: {run_response.text}")
    
    run_data = run_response.json()
    run_id = run_data['data']['id']
    dataset_id = run_data['data']['defaultDatasetId']
    
    # Poll for completion (max 3 minutes)
    status_url = f"https://api.apify.com/v2/acts/{ACTOR}/runs/{run_id}?token={APIFY_TOKEN}"
    
    for i in range(60):
        time.sleep(3)
        status_response = requests.get(status_url)
        
        if status_response.status_code == 200:
            status = status_response.json()['data']['status']
            
            if status == 'SUCCEEDED':
                # Get results
                results = requests.get(
                    f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_TOKEN}"
                ).json()
                
                if results:
                    result = results[0]
                    transcript = result.get('transcript', result.get('text', ''))
                    
                    if isinstance(transcript, list):
                        transcript = ' '.join([str(s.get('text', s)) for s in transcript])
                    
                    return str(transcript)
            
            elif status in ['FAILED', 'ABORTED', 'TIMED-OUT']:
                raise Exception(f"Run {status}")
    
    raise Exception("Timeout after 3 minutes")
```

**Anti-Patterns:**
- ❌ Using `/` separator: `streamers/youtube-transcript-scraper` (404 error)
- ❌ Input format `videoUrl` or `url` (400 invalid-input error)
- ❌ Assuming actor names from web search (actors get renamed/deprecated)
- ❌ Not polling for completion (run is async, immediate response is empty)
- ❌ Guessing input schema instead of querying `/input-schema` endpoint

**Edge Cases:**
- **Video has no captions:** Actor returns empty transcript, check `result.get('transcript')` for None
- **Very long video (>2 hours):** May timeout, increase max_wait to 300 seconds
- **Rate limit hit:** Wait 60 seconds, retry with exponential backoff
- **Actor deprecated:** Search Apify store: `curl -s "https://api.apify.com/v2/store?search=youtube+transcript"`

**Metrics:**
- **Time:** ~30 seconds for 10-minute video
- **Cost:** FREE tier (no monthly subscription needed)
- **Accuracy:** Depends on YouTube's auto-generated captions (~95% for clear audio)

**Related Patterns:**
- `conversation_search` - Find Apify token from previous chats
- `google_drive_search` - Locate "genspark method" documentation

**Version History:**
- v1.0 (Dec 26, 2025): Initial documentation after 90-minute debugging session
- Lesson: Should have searched past chats first (18x time savings)

---

### Pattern: Search Past Chats Before Innovating

**One-line:** Always search conversation history when user references "previous work" or "our method".

**Context:**
- **Use when:** User says "check our previous chats", "follow the X method", "we solved this before"
- **Don't use when:** Completely new problem with no prior context

**Implementation:**
```python
# When user says: "Check our previous chats for the Apify key"

# Step 1: conversation_search for key terms
conversation_search(query="Apify token key API")

# Step 2: If found, use exact pattern from previous success
# Step 3: If not found, google_drive_search for documentation
# Step 4: Only innovate if both searches return nothing

# Time to value: 5 minutes (search) vs 90 minutes (reinvent)
```

**Anti-Patterns:**
- ❌ Assuming past solutions are outdated (they're usually still valid)
- ❌ Trying "better" approaches before trying known solutions
- ❌ Skipping search because "I know what to do" (you don't have full context)
- ❌ Not documenting WHY something worked (future you won't remember)

**Edge Cases:**
- **Past solution genuinely blocked:** Document blocking error, then innovate
- **Multiple past solutions:** Test most recent first
- **Conflicting information:** Ask user for clarification

**Metrics:**
- **Time saved:** 18x (proven Dec 26, 2025: 5 min vs 90 min)
- **Success rate:** ~95% (past solutions still work for our use cases)

**Related Patterns:**
- `google_drive_search` - For documented SOPs
- `recent_chats` - For temporal context (last week, yesterday)

**Version History:**
- v1.0 (Dec 26, 2025): Created after ignoring "check previous chats" instruction
- Painful lesson: User references to past work = INSTRUCTIONS not suggestions

---

### Pattern: Theme-Switching for Reports

**One-line:** Single-prompt transformation of report presentation for different audiences.

**Context:**
- **Use when:** Same data, different audience (investor/lender/contractor)
- **Don't use when:** Audiences need fundamentally different data (not just framing)

**Implementation:**
```python
# Prompt pattern for theme switching:

"""
Convert this [CURRENT_THEME] report to [NEW_THEME] theme.

Emphasis changes:
- FROM: [current focus]
- TO: [new focus]

Color changes:
- Accent: [current color] → [new color]

Section reordering:
1. [new priority section]
2. [second priority]
...

Terminology updates:
- Replace "[old term]" with "[new term]"
- Example: "equity" → "collateral cushion"

Use the biddeed-frontend-design skill for all visual changes.
"""

# Example: Investor → Lender
"""
Convert this investor report to lender theme.

Emphasis changes:
- FROM: Profit potential, ROI
- TO: Security, collateral, risk mitigation

Color changes:
- Accent: #2E7D32 (green) → #1E3A5F (blue)

Section reordering:
1. Collateral Valuation (LTV ratios)
2. Lien Priority Analysis
3. Title Risk Assessment
4. Market Stability Metrics

Terminology updates:
- Replace "equity" with "collateral cushion"
- Replace "profit" with "recovery value"
- Replace "exit strategy" with "recovery scenario"

Use the biddeed-frontend-design skill for all visual changes.
"""
```

**Anti-Patterns:**
- ❌ Creating separate codebases for each theme (maintenance nightmare)
- ❌ Hard-coding theme logic in components (inflexible)
- ❌ Not documenting theme requirements upfront (causes inconsistency)

**Edge Cases:**
- **Hybrid audiences:** Create "lender-investor" theme with both metrics
- **White-label needs:** Theme includes logo/branding replacement
- **Print vs digital:** Adjust for grayscale, page breaks

**Metrics:**
- **Development time:** 5 min (theme switch) vs 4 hours (new codebase)
- **Maintenance:** 1 source of truth vs 3 diverging codebases

**Related Patterns:**
- `biddeed-frontend-design` skill - Visual consistency rules
- Component composition - Build for theme flexibility from day 1

**Version History:**
- v1.0 (Dec 26, 2025): Learned from "Nano Banana" video tutorial

---

## Process: Immediate Documentation Workflow

### After Any Success (5 minutes):

1. **Open /docs/patterns/[pattern-name].md**
2. **Fill template:**
   - One-line description
   - Working code example
   - Anti-patterns encountered
   - Edge cases hit
3. **Commit with message:** `docs: add [pattern-name] pattern from [context]`
4. **Link in related skills:** Update cross-references

### Weekly Review (30 minutes):

1. **Scan commits for undocumented patterns**
2. **Interview yourself:** "What worked this week that I'd forget next week?"
3. **Update version history** on existing patterns
4. **Flag patterns for skill promotion** (if used 3+ times, elevate to skill)

### Monthly Audit (60 minutes):

1. **Review pattern usage metrics**
2. **Deprecate outdated patterns** (mark with ⚠️ and replacement link)
3. **Consolidate similar patterns** into unified approach
4. **Create meta-patterns** from recurring combinations

## Metrics to Track

### Documentation Health:
- **Patterns documented:** [current count]
- **Patterns used 3+ times:** [count] (candidates for skills)
- **Undocumented successes:** [count] (technical debt)
- **Deprecated patterns:** [count] (evolution rate)

### Time ROI:
- **Time to document:** ~5 min per pattern
- **Time saved on reuse:** 60-90 min average
- **ROI multiplier:** 12-18x

### Knowledge Compounding:
- **Patterns → Skills:** [count]
- **Skills → Meta-skills:** [count]
- **Cross-references:** [count] (network density)

## Anti-Patterns in Documentation

### ❌ "We'll document later"
**Impact:** Context lost, pattern forgotten, bug reintroduced
**Fix:** 5-minute rule - document immediately after success

### ❌ "This is too simple to document"
**Impact:** Spend 30 min debugging "simple" thing 6 months later
**Fix:** Simple patterns are MOST valuable (used frequently)

### ❌ "I'll remember this"
**Impact:** You won't. Future you has different context.
**Fix:** Assume future you is a different person who needs onboarding

### ❌ Over-engineering documentation
**Impact:** Nobody reads 50-page docs, patterns unused
**Fix:** Template-driven, scannable, example-heavy

### ❌ No version history
**Impact:** Can't track evolution, don't know why changes happened
**Fix:** Every update adds version entry with reason

## Success Criteria

**Good pattern documentation:**
- Can be implemented by future you in < 10 minutes
- Has working code example (copy-paste ready)
- Lists anti-patterns (what NOT to do)
- Shows edge cases with solutions
- Links to related patterns

**Great pattern documentation:**
- Includes metrics (before/after)
- Has version history with lessons learned
- Connected to skills (bidirectional references)
- Used 3+ times without modification

**Excellent pattern documentation:**
- Promoted to skill (used 10+ times)
- Referenced by other teams/projects
- Generates meta-patterns (combinations with other patterns)
- Measurable ROI (time saved, bugs prevented)

## BidDeed.AI Commitment

**From today forward (Dec 26, 2025):**

1. ✅ Document every successful pattern within 24 hours
2. ✅ Update existing patterns when improved
3. ✅ Link patterns → skills when usage hits 3x
4. ✅ Monthly audit for consolidation/deprecation
5. ✅ Measure ROI: time to document vs time saved on reuse

**Goal:** 3-5x faster iteration through compounding knowledge, not repeated debugging.

**Mantra:** "Search first, innovate second, document always."
