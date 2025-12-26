# BidDeed.AI Data Sources API Inventory

**Last Updated:** December 26, 2025  
**Purpose:** Document all data sources with API availability and integration strategy

---

## Summary

| Source | Has API | Integration Method | Status | Priority |
|--------|---------|-------------------|--------|----------|
| BCPAO | ✅ Yes | Direct REST API | ACTIVE | P0 |
| RealForeclose | ❓ Unknown | Web scraping | NEEDS INVESTIGATION | P1 |
| AcclaimWeb | ❌ No | Firecrawl | PLANNED | P1 |
| RealTDM | ❓ Unknown | Web scraping | NEEDS INVESTIGATION | P2 |
| Census Bureau | ✅ Yes | Direct REST API | ACTIVE | P2 |
| PropertyOnion | ❌ No | Firecrawl | COMPETITIVE INTEL | P3 |

---

## Tier 1: Direct APIs (FREE, Fast, Reliable)

### BCPAO (Brevard County Property Appraiser)

**API Endpoint:** `https://www.bcpao.us/api/v1/search`

**Authentication:** None required

**Rate Limits:** Unknown (appears unlimited for reasonable use)

**Example Request:**
```python
import requests

url = "https://www.bcpao.us/api/v1/search"
params = {"accountNumber": "2517790"}
response = requests.get(url, params=params)
data = response.json()
```

**Response Fields:**
- `accountNumber` - Parcel ID
- `propertyAddress` - Full address
- `ownerName` - Current owner
- `livingArea` - Square footage
- `yearBuilt` - Construction year
- `bedrooms` - Number of bedrooms
- `bathrooms` - Number of bathrooms  
- `assessedValue` - Total assessed value
- `landValue` - Land value
- `buildingValue` - Improvement value
- `annualTax` - Tax amount
- `saleHistory` - Array of sales

**Performance:**
- Response time: 200-500ms
- Reliability: 99.9%
- Cost: $0

**Integration Status:** ✅ ACTIVE in BidDeed.AI V16.5.0

**Notes:**
- Most reliable data source
- Updated daily (4:19 AM EST)
- Includes photo URLs: `https://www.bcpao.us/photos/{prefix}/{account}011.jpg`
- GIS endpoint: `https://gis.brevardfl.gov/gissrv/rest/services/Base_Map/Parcel_New_WKID2881/MapServer/5`

---

### Census Bureau API

**API Endpoint:** `https://api.census.gov/data`

**Authentication:** API key required (free)

**Rate Limits:** 500 requests/IP/day (uncredentialed), 5,000/day (with key)

**Example Request:**
```python
import requests

url = "https://api.census.gov/data/2021/acs/acs5"
params = {
    "get": "B01001_001E,B19013_001E,B25077_001E",  # Population, Income, Home Value
    "for": "zip code tabulation area:32937",
    "key": CENSUS_API_KEY
}
response = requests.get(url, params=params)
data = response.json()
```

**Use Cases:**
- Demographic analysis by ZIP code
- Median income levels
- Home value trends
- Population density

**Integration Status:** ✅ ACTIVE in market intelligence module

**Documentation:** https://www.census.gov/data/developers/guidance/api-user-guide.html

---

## Tier 2: Needs Investigation (Potential APIs)

### RealForeclose (Brevard County Foreclosure Auctions)

**URL:** https://brevard.realforeclose.com

**Current Method:** Web scraping

**Investigation Needed:**
1. Check network tab for `/api/` endpoints
2. Look for GraphQL endpoints
3. Test CORS restrictions
4. Document rate limiting

**Hypothesis:** Likely has undocumented API (modern React site suggests backend API)

**Action Items:**
- [ ] Inspect network requests during auction listing load
- [ ] Test discovered endpoints with curl
- [ ] Document request/response schemas
- [ ] Compare API vs web scraping cost/reliability

**Priority:** P1 (Jan 7 auction approaching)

---

### RealTDM (Tax Deed/Certificate Search)

**URL:** https://www.realtaxdeed.com/

**Current Method:** Custom scraper (realtdm_scraper.py)

**Investigation Needed:**
- Check for official API
- Test current scraper reliability
- Consider Firecrawl if no API

**Priority:** P2 (less frequent data needs)

---

## Tier 3: No API - Use Firecrawl

### AcclaimWeb (Brevard County Clerk Official Records)

**URL:** https://or.brevardclerk.us/AcclaimWeb/

**Why No Direct API:**
- Complex ASP.NET WebForms application
- JavaScript-heavy search interface
- Session-based navigation

**Firecrawl Integration Strategy:**
```python
from firecrawl import Firecrawl

firecrawl = Firecrawl(api_key=FIRECRAWL_API_KEY)

result = firecrawl.scrape(
    url="https://or.brevardclerk.us/AcclaimWeb/search/SearchTypeName?SearchType=Image",
    formats=["markdown"],
    actions=[
        {"type": "wait", "milliseconds": 3000},
        {"type": "click", "selector": "input[value='MTG']"},  # Mortgage checkbox
        {"type": "click", "selector": "input[value='LIEN']"},  # Lien checkbox
        {"type": "write", "selector": "input[name='NameSearchModel.SearchCriteria']", "text": address},
        {"type": "click", "selector": "button[type='submit']"},
        {"type": "wait", "milliseconds": 5000}
    ]
)
```

**Use Cases:**
- Lien discovery (mortgages, judgments, HOA liens)
- Title search automation
- Recorded document retrieval

**Cost Estimate:**
- ~5-10 credits per search
- ~100 searches/month = 500-1,000 credits
- Starter plan (500K credits) = ~$0.04/search

**Integration Status:** PLANNED for V17.0

**Priority:** P1 (core lien discovery feature)

---

### PropertyOnion (Competitor Intelligence)

**URL:** https://propertyonion.com

**Why Scrape:**
- Competitive analysis
- No public API
- Validate our ML predictions

**Firecrawl Integration:**
```python
result = firecrawl.scrape(
    url="https://propertyonion.com/property_search/Brevard-County?listing_type=foreclosure",
    formats=["markdown", {"type": "json", "prompt": "Extract property list with addresses, judgments, and sale dates"}]
)
```

**Use Cases:**
- Compare PropertyOnion recommendations vs BidDeed.AI
- Validate ML model accuracy
- Market research

**Frequency:** Weekly (not real-time)

**Cost:** ~20 credits/week = 80/month

**Priority:** P3 (nice-to-have, not critical path)

---

## Tier 4: Custom Scrapers (Last Resort)

### When to Build Custom Scraper:

**Decision Matrix:**
```python
def should_use_custom_scraper(data_source):
    if data_source.has_public_api:
        return False  # Use API!
    
    if data_source.firecrawl_score > 5:
        return False  # Use Firecrawl!
    
    if data_source.update_frequency == "real-time":
        return True  # Need reliable automation
    
    if data_source.complexity == "simple":
        return True  # requests + BeautifulSoup is fine
    
    return False  # Default to Firecrawl
```

**Current Custom Scrapers:**
- `bcpao_scraper.py` - ⚠️ DEPRECATED (use API instead)
- `realtdm_scraper.py` - Under review (check for API)
- `census_api.py` - ✅ Using official API

**Maintenance Burden:**
- Each custom scraper = ~4 hours/quarter maintenance
- Breaking changes when sites update
- Rate limiting issues
- IP blocking risks

**Strategy:** Minimize custom scrapers, prefer APIs > Firecrawl > Custom

---

## Integration Decision Flowchart

```
┌─────────────────────┐
│  New Data Source    │
└──────────┬──────────┘
           │
           ▼
    ┌──────────────┐
    │ Has Public   │──YES──► Use Direct API
    │ API?         │         (Tier 1)
    └──────┬───────┘
           │ NO
           ▼
    ┌──────────────┐
    │ Complex      │──YES──► Use Firecrawl
    │ Navigation?  │         (Tier 3)
    └──────┬───────┘
           │ NO
           ▼
    ┌──────────────┐
    │ Simple HTML? │──YES──► requests +
    │              │         BeautifulSoup
    └──────┬───────┘
           │ NO
           ▼
    ┌──────────────┐
    │ Try Firecrawl│
    │ Anyway       │
    └──────────────┘
```

---

## Cost Analysis (Monthly)

**Current Approach (V16.5.0):**
- BCPAO API: $0
- Census API: $0
- Custom scrapers: $0 (but 12 hours/quarter maintenance)
- **Total:** $0/month + developer time

**With Firecrawl (V17.0):**
- BCPAO API: $0
- Census API: $0
- Firecrawl (AcclaimWeb + PropertyOnion): ~$20/month
- **Total:** $20/month, saves 10 hours/quarter

**ROI:** $20/month vs 10 hours/quarter maintenance = **15x ROI**

---

## Action Items

### Immediate (Before Jan 7 Auction):
- [ ] Verify BCPAO API reliability under load
- [ ] Investigate RealForeclose for API endpoints
- [ ] Test current scrapers on production data

### Short-term (Q1 2026):
- [ ] Implement Firecrawl for AcclaimWeb lien discovery
- [ ] Document all discovered APIs
- [ ] Deprecate bcpao_scraper.py (use API)
- [ ] Build API monitoring alerts

### Long-term (Q2 2026):
- [ ] Evaluate Zillow/Redfin APIs for comparable sales
- [ ] Consider HUD/GSE APIs for REO properties
- [ ] Build unified data source abstraction layer

---

## Monitoring & Alerts

**API Health Checks:**
- BCPAO API: Daily ping, alert if >5s response time
- Census API: Weekly validation
- Firecrawl: Credit usage tracking, alert at 80% consumed

**Scraper Health:**
- Weekly validation runs
- Schema change detection
- Error rate monitoring (alert if >5%)

---

## Documentation Standards

**For Each New Data Source:**
1. Document in this file (API Inventory)
2. Create `/docs/data-sources/{source_name}.md` with details
3. Add integration code to `/src/integrations/{source_name}_client.py`
4. Write tests in `/tests/integrations/test_{source_name}.py`
5. Update PROJECT_STATE.json with data source metadata

---

## Related Documentation

- [Firecrawl Integration Pattern](../patterns/firecrawl-integration.md)
- [BCPAO API Documentation](bcpao-api.md)
- [Census API Guide](census-api.md)
- [Web Scraping Best Practices](../patterns/web-scraping-best-practices.md)
