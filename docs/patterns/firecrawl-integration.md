# Firecrawl Integration Pattern

**Created:** December 26, 2025  
**Version:** 1.0  
**Status:** Production Ready

---

## Overview

Firecrawl is a web scraping API designed for AI applications. Use it when sites have complex navigation, no public APIs, or require browser automation.

**API Key:** `fc-985293d88ddf4d6595e041936ec2cb00`  
**Plan:** Starter ($20/month, 500K credits)  
**Credits Remaining:** ~489K (11 used in testing)

---

## When to Use Firecrawl

### Decision Matrix
```python
score = (has_api * -10) + \
        (requires_auth * 5) + \
        (complex_navigation * 5) + \
        (dynamic_content * 3) + \
        (visual_needed * 2)

if score > 5:
    use_firecrawl()
else:
    use_direct_api() or requests()
```

### ✅ Perfect Use Cases
1. **No Official API** - Sites without public APIs (e.g., PropertyOnion, AcclaimWeb)
2. **Authentication Required** - Login walls, session management
3. **Complex Navigation** - Multi-step processes, pagination, dropdowns, search forms
4. **Dynamic Content** - Infinite scroll, lazy loading, JavaScript-rendered content
5. **Visual Verification** - Screenshot + data extraction in one call

### ❌ Don't Use When
1. **Official API exists** - Always use it (faster, cheaper, more reliable)
2. **Simple static pages** - `requests` + `BeautifulSoup` is fine
3. **High volume scraping** - Direct APIs scale better
4. **Client-side routing only** - Sites with `#/route` may not load data properly

---

## BidDeed.AI Applications

### HIGH VALUE (Use Firecrawl)

**1. AcclaimWeb Title Search**
- **URL:** https://or.brevardclerk.us/AcclaimWeb/
- **Complexity:** ASP.NET WebForms, complex search forms
- **Use Case:** Automated lien discovery (mortgages, judgments, HOA liens)
- **Estimated Cost:** ~5-10 credits/search × 100 searches/month = 500-1,000 credits/month
- **ROI:** Replaces manual title search (2 hours → 10 seconds)

**2. PropertyOnion Competitor Intelligence**
- **URL:** https://propertyonion.com
- **Complexity:** No public API, dynamic content loading
- **Use Case:** Validate BidDeed.AI predictions vs competitor
- **Frequency:** Weekly scrapes
- **Cost:** ~20 credits/week = 80 credits/month

**3. Comparable Sales (Zillow/Redfin)**
- **Complexity:** Anti-bot protection, dynamic pricing
- **Use Case:** Recent sales data for ARV calculations
- **Alternative:** Check for official APIs first

### LOW VALUE (Don't Use Firecrawl)

**1. BCPAO Property Data**
- ❌ Has direct API: `https://www.bcpao.us/api/v1/search`
- **Test Result:** 11 credits wasted trying to scrape when API exists
- **Lesson:** Always check for APIs FIRST

**2. RealForeclose Auction Listings**
- ⚠️ Investigate for API first
- Modern React site suggests backend API may exist
- Only use Firecrawl if no API found

---

## Implementation Patterns

### Pattern 1: Simple Scrape with JSON Extraction

```python
import requests

FIRECRAWL_API_KEY = "fc-985293d88ddf4d6595e041936ec2cb00"

url = "https://api.firecrawl.dev/v2/scrape"

headers = {
    "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "url": "https://example.com/property/12345",
    "formats": [
        {
            "type": "json",
            "prompt": """
            Extract property details as JSON:
            - address: full property address
            - price: listing price
            - beds: number of bedrooms
            - baths: number of bathrooms
            - sqft: square footage
            """
        }
    ]
}

response = requests.post(url, json=payload, headers=headers)
data = response.json()

if response.status_code == 200 and data['success']:
    property_data = data['data']['json']
    print(property_data)
```

**Use When:** Simple data extraction from single page

---

### Pattern 2: Form Navigation with Actions

```python
payload = {
    "url": "https://example.com/search",
    "formats": ["markdown"],
    "actions": [
        {"type": "wait", "milliseconds": 3000},
        {"type": "write", "selector": "input[name='address']", "text": "123 Main St"},
        {"type": "click", "selector": "button[type='submit']"},
        {"type": "wait", "milliseconds": 5000},
        {"type": "screenshot"}
    ]
}

response = requests.post(url, json=payload, headers=headers)
```

**Use When:** Complex forms, multi-step navigation

**Available Actions:**
- `wait` - Pause for JavaScript to load
- `click` - Click buttons, links, checkboxes
- `write` - Enter text into input fields
- `press` - Press keyboard keys (Enter, Tab, etc.)
- `scroll` - Scroll page (useful for lazy loading)
- `screenshot` - Capture visual state

---

### Pattern 3: Python SDK Usage

```python
from firecrawl import Firecrawl

firecrawl = Firecrawl(api_key="fc-985293d88ddf4d6595e041936ec2cb00")

# Simple scrape
doc = firecrawl.scrape(
    url="https://example.com",
    formats=["markdown", "html"]
)

print(doc.markdown)

# With actions
result = firecrawl.scrape(
    url="https://example.com/search",
    formats=["markdown"],
    actions=[
        {"type": "wait", "milliseconds": 2000},
        {"type": "write", "selector": "#search", "text": "foreclosure"},
        {"type": "click", "selector": "button.submit"},
        {"type": "wait", "milliseconds": 3000}
    ]
)
```

**When to use SDK vs REST API:**
- SDK: Python projects, better type hints, automatic retries
- REST: Language-agnostic, more control, debugging

---

### Pattern 4: Batch Scraping

```python
from firecrawl import Firecrawl

firecrawl = Firecrawl(api_key="fc-985293d88ddf4d6595e041936ec2cb00")

# Scrape multiple URLs at once
urls = [
    "https://example.com/property/1",
    "https://example.com/property/2",
    "https://example.com/property/3"
]

job = firecrawl.batch_scrape(
    urls=urls,
    formats=["markdown"]
)

# Results
for result in job.data:
    print(result.markdown)
```

**Use When:** Scraping 10+ properties at once

**Cost:** Same as individual scrapes (1 credit per URL)

---

## Error Handling

### Common Errors

**1. DNS Resolution Failed**
```json
{
  "success": false,
  "code": "SCRAPE_DNS_RESOLUTION_ERROR",
  "error": "DNS resolution failed for hostname: example.com"
}
```

**Solutions:**
- Check if domain is actually accessible
- Try with `www.` prefix or without
- Site may be temporarily down

**2. JavaScript Didn't Execute**
- **Symptom:** Empty fields or "Loading..." text
- **Solution:** Increase `waitFor` parameter or add wait actions

```python
payload = {
    "url": "https://example.com",
    "waitFor": 10000,  # Wait 10 seconds
    "actions": [
        {"type": "wait", "milliseconds": 5000}
    ]
}
```

**3. Insufficient Credits**
```json
{
  "success": false,
  "error": "Insufficient credits to perform this request."
}
```

**Solution:** Upgrade plan at https://firecrawl.dev/pricing

**4. Rate Limiting**
- **Symptom:** 429 status code
- **Solution:** Add delays between requests, use batch scraping

---

## Cost Optimization

### Credit Usage by Operation

| Operation | Credits | Notes |
|-----------|---------|-------|
| Simple scrape | 1 | Static HTML |
| Scrape with JSON extraction | 5 | LLM processing |
| Scrape with actions | 1-10 | Depends on action count |
| Screenshot | +1 | Added to base cost |
| Stealth proxy (auto) | +5 | Only if basic proxy fails |

### Optimization Strategies

**1. Cache Results**
```python
# Use max_age to leverage Firecrawl's cache
result = firecrawl.scrape(
    url="https://example.com",
    max_age=600000  # 10 minutes (in ms)
)
```

**2. Minimize JSON Extractions**
- Get markdown first, parse locally with regex/BeautifulSoup
- Only use JSON extraction when complex parsing needed

**3. Batch Operations**
- Scrape 100 properties in single batch vs 100 individual calls
- Same cost, less overhead

**4. Use only_main_content**
```python
result = firecrawl.scrape(
    url="https://example.com",
    only_main_content=True  # Excludes nav, footer, ads
)
```

Reduces content size = faster processing = lower costs

---

## Testing & Debugging

### Test in Playground First
1. Go to https://app.firecrawl.dev/playground
2. Test URLs and actions interactively
3. View screenshots to verify selectors
4. Copy working config to code

### Debug Failed Scrapes

**1. Check Screenshot**
```python
payload = {
    "formats": ["markdown"],
    "actions": [
        # ... your actions
        {"type": "screenshot"}  # Always add at end
    ]
}

# Get screenshot URL from response
screenshot_url = data['data']['actions']['screenshots'][0]
print(f"Screenshot: {screenshot_url}")
```

**2. View Raw HTML**
```python
payload = {
    "formats": ["rawHtml"]  # See exactly what Firecrawl sees
}
```

**3. Inspect Selectors**
- Use browser DevTools to find correct CSS selectors
- Test selectors in console: `document.querySelector("your-selector")`

---

## Integration with BidDeed.AI

### Stage in Data Pipeline

```
┌──────────────┐
│ Discovery    │ RealForeclose scraper finds auction properties
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Enrichment   │ BCPAO API gets property details
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Lien Search  │ ⭐ FIRECRAWL AcclaimWeb title search
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Analysis     │ ForecastEngine™ calculates max bid
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Reporting    │ Generate investment reports
└──────────────┘
```

### Code Integration

```python
# src/integrations/firecrawl_client.py

from firecrawl import Firecrawl

class FirecrawlClient:
    def __init__(self, api_key: str):
        self.client = Firecrawl(api_key=api_key)
    
    def search_acclaimweb_liens(self, address: str) -> dict:
        """Search AcclaimWeb for liens on property"""
        
        result = self.client.scrape(
            url="https://or.brevardclerk.us/AcclaimWeb/search/SearchTypeName?SearchType=Image",
            formats=["markdown"],
            actions=[
                {"type": "wait", "milliseconds": 3000},
                {"type": "click", "selector": "input[value='MTG']"},
                {"type": "click", "selector": "input[value='LIEN']"},
                {"type": "write", "selector": "input[name='NameSearchModel.SearchCriteria']", "text": address},
                {"type": "click", "selector": "button[type='submit']"},
                {"type": "wait", "milliseconds": 5000}
            ]
        )
        
        # Parse liens from markdown
        liens = self._parse_liens(result.markdown)
        return liens
    
    def _parse_liens(self, markdown: str) -> list:
        """Extract lien data from AcclaimWeb results"""
        # Implementation here
        pass
```

---

## Monitoring & Alerts

### Track Credit Usage

```python
import requests

def get_credit_balance():
    response = requests.get(
        "https://api.firecrawl.dev/v2/account",
        headers={"Authorization": f"Bearer {FIRECRAWL_API_KEY}"}
    )
    
    data = response.json()
    credits_remaining = data['credits']
    
    if credits_remaining < 100000:  # Alert at 20% remaining
        send_alert(f"Firecrawl credits low: {credits_remaining:,}")
    
    return credits_remaining
```

### Log All Requests

```python
import logging

logger = logging.getLogger(__name__)

def scrape_with_logging(url: str, **kwargs):
    logger.info(f"Firecrawl request: {url}")
    
    start_time = time.time()
    response = firecrawl.scrape(url, **kwargs)
    duration = time.time() - start_time
    
    logger.info(f"Firecrawl response: {duration:.2f}s, credits: {response.metadata.creditsUsed}")
    
    return response
```

---

## Best Practices

### 1. Always Check for APIs First
- View network tab in browser DevTools
- Look for `/api/`, `/graphql`, or `/rest/` endpoints
- Test with curl before building Firecrawl integration

### 2. Start Simple, Add Complexity
- Begin with basic scrape + markdown
- Add JSON extraction only if needed
- Use actions only for complex navigation

### 3. Cache Aggressively
- Property data doesn't change minute-to-minute
- Use `max_age` parameter liberally
- Store results in Supabase to avoid re-scraping

### 4. Monitor Costs
- Set up alerts at 80% credit usage
- Review monthly spend
- Deprecate unused integrations

### 5. Document Selectors
- CSS selectors break when sites update
- Document WHY each selector is needed
- Include screenshot of target element

---

## Troubleshooting Guide

| Problem | Solution |
|---------|----------|
| Empty JSON fields | Increase waitFor, add wait actions |
| Wrong data extracted | Refine JSON extraction prompt |
| Selector not found | Update CSS selector, check screenshot |
| Timeout errors | Reduce action count, increase waitFor |
| DNS errors | Check domain accessibility |
| High credit usage | Review unnecessary JSON extractions |

---

## Related Documentation

- [API Inventory](../data-sources/api-inventory.md)
- [AcclaimWeb Integration](../data-sources/acclaimweb.md)
- [PropertyOnion Scraping](../data-sources/propertyonion.md)
- [Web Scraping Best Practices](web-scraping-best-practices.md)

---

## Version History

- **v1.0 (Dec 26, 2025):** Initial pattern documentation after testing
- Tested BCPAO (wrong use case), identified AcclaimWeb as high-value target
- Credits used in testing: 11
- Key lesson: Always check for APIs before using Firecrawl
