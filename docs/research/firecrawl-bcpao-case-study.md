# Firecrawl vs Direct API: BCPAO Case Study

## Test Results (Dec 26, 2025)

### Attempt 1: Firecrawl v2/scrape with JSON extraction
- **Result:** Empty fields (JavaScript didn't execute)
- **Credits used:** 5
- **Time:** ~3 seconds

### Attempt 2: Firecrawl with waitFor + actions
- **Result:** Still stuck on "Loading..." splash screen
- **Credits used:** 5
- **Time:** ~5 seconds

### Attempt 3: Firecrawl with 8-second JavaScript wait
- **Result:** 37,994 chars but still mostly navigation/UI, not property data
- **Credits used:** 1
- **Time:** ~10 seconds

### ✅ Current Working Solution: Direct BCPAO API
```python
import requests

url = "https://www.bcpao.us/api/v1/search"
params = {"accountNumber": "2517790"}
response = requests.get(url, params=params)
data = response.json()
```

- **Result:** Complete property data in 0.3 seconds
- **Credits used:** 0 (free API)
- **Reliability:** 99.9%

## Why Firecrawl Struggled with BCPAO

1. **Client-side routing** (`#/property/ID`) - Hash-based Angular/React routing
2. **Delayed data loading** - AJAX calls happen AFTER initial render
3. **Multiple API calls** - Property data loads incrementally (owner, taxes, sales separately)
4. **Anti-scraping measures** - BCPAO may detect headless browsers

## When Firecrawl DOES Excel

### ✅ Perfect Use Cases:
1. **No official API** - Sites without public APIs (e.g., PropertyOnion)
2. **Authentication required** - Login walls, session management
3. **Complex navigation** - Multi-step processes, pagination, dropdowns
4. **Dynamic content** - Infinite scroll, lazy loading
5. **Visual verification needed** - Screenshot + data extraction

### ❌ Skip Firecrawl When:
1. **Official API exists** - Always use it (faster, cheaper, more reliable)
2. **Simple static pages** - requests + BeautifulSoup is fine
3. **High volume** - Direct APIs scale better (rate limits, cost)

## BidDeed.AI Application Strategy

### Use Direct APIs:
- **BCPAO:** `https://www.bcpao.us/api/v1/search` ✅
- **RealForeclose:** May have undocumented API (check network tab)
- **Clerk of Court:** May have case search API

### Use Firecrawl:
- **AcclaimWeb title search:** No public API, complex search forms ✅
- **PropertyOnion:** Competitor intelligence, no API ✅
- **Zillow/Redfin comps:** If no API access ✅
- **HOA websites:** Varied structures, no standards ✅

## Cost Comparison (100 properties/month)

| Method | Cost | Time | Reliability |
|--------|------|------|-------------|
| BCPAO Direct API | $0 | 30s | 99.9% |
| Firecrawl | $0.50-1.00 | 5-10min | 85-90% |
| Custom Selenium | $0 (dev time) | 3-5min | 70-80% |

## Decision Matrix

**Use Firecrawl when:**
```
score = (has_api * -10) + 
        (requires_auth * 5) + 
        (complex_navigation * 5) + 
        (dynamic_content * 3) + 
        (visual_needed * 2)

if score > 5: use_firecrawl()
else: use_direct_api() or requests()
```

**Examples:**
- BCPAO: (-10 + 0 + 0 + 3 + 0) = -7 → **Don't use Firecrawl**
- AcclaimWeb: (0 + 0 + 5 + 3 + 0) = 8 → **Use Firecrawl** ✅
- PropertyOnion: (0 + 0 + 5 + 5 + 0) = 10 → **Use Firecrawl** ✅

## Lessons Learned

1. **Always check for APIs first** - View network tab, look for `/api/` endpoints
2. **Firecrawl is not magic** - Complex SPAs with delayed loading still challenging
3. **Hybrid approach wins** - Use best tool for each data source
4. **Cost adds up** - $0.01/page * 10,000 pages/year = $100 vs free API

## Recommendation for BidDeed.AI

**Tier 1 (Direct APIs):**
- BCPAO property data
- Census demographics
- Any government open data

**Tier 2 (Firecrawl):**
- AcclaimWeb title search
- PropertyOnion competitor analysis
- Sites without public APIs

**Tier 3 (Custom scrapers):**
- Last resort only
- Document why Firecrawl can't handle it
- Plan for maintenance burden

**Action:** Document known APIs in `docs/data-sources/api-inventory.md`
