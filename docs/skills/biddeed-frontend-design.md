# BidDeed.AI Frontend Design Skill

## Purpose
Professional UI/UX design for foreclosure investment reports and dashboards that don't look "AI-generated". Establishes trust through polish, consistency, and brand alignment.

## When to Use This Skill
- Creating investor reports (PDF, DOCX, HTML)
- Building dashboard interfaces
- Generating property comparison views
- Designing lender presentations
- Theme-switching between report types

## Core Principles

### 1. Brand Identity
**Colors:**
- Primary: `#1E3A5F` (Navy blue - trust, authority)
- Secondary: `#2E7D32` (Green - growth, profit)
- Accent: `#FF6B35` (Orange - urgency, action)
- Background: `#F5F7FA` (Light gray - professional)
- Error: `#C62828` (Red - risk, warning)

**Typography:**
- Headings: Inter Bold (modern, readable)
- Body: Inter Regular
- Numbers: JetBrains Mono (monospaced for alignment)
- Minimum font size: 11pt (accessibility)

**Logo Usage:**
- BidDeed.AI wordmark (never "BrevardBidderAI")
- ForecastEngine™ for ML predictions
- Tagline: "Intelligent Foreclosure Investment Analysis"

### 2. Report Themes

#### Investor Theme (Default)
**Focus:** ROI, equity, profit potential
**Colors:** Green accents, positive framing
**Sections:**
- Property Snapshot (photo, address, judgment amount)
- Equity Analysis (ARV, liens, net equity)
- ForecastEngine™ Predictions (bid probability, third-party risk)
- Max Bid Recommendation (formula breakdown)
- Comparable Sales (3-5 recent sales in zip)
- Exit Strategies (flip timeline, rental yield)

#### Lender Theme
**Focus:** Security, collateral, risk mitigation
**Colors:** Blue accents, conservative framing
**Sections:**
- Collateral Valuation (LTV ratios, equity cushion)
- Lien Priority Analysis (senior/junior positions)
- Title Risk Assessment (clouds, judgments, HOA)
- Market Stability Metrics (days on market, price trends)
- Borrower Credit Profile (if available)
- Recovery Scenarios (foreclosure timeline, costs)

#### Contractor Theme
**Focus:** Rehab scope, materials, labor
**Colors:** Orange accents, action-oriented
**Sections:**
- Property Condition Assessment (age, square footage, beds/baths)
- Repair Estimates by Category (roof, HVAC, cosmetic)
- Comparable Rehab Projects (similar properties, actual costs)
- Timeline Projections (permit time, construction phases)
- Material Sourcing (local suppliers, bulk discounts)
- Subcontractor Recommendations (licensed, insured)

### 3. Layout Patterns

#### One-Page Summary (Standard)
```
[Header: Logo + Property Address]
[Hero Image: BCPAO photo or street view]
[Key Metrics Grid: 4 columns]
  - ARV | Judgment | Equity | Max Bid
[Decision Box: BID/REVIEW/SKIP with confidence %]
[Lien Priority Table: Plaintiff, amount, position]
[Comparable Sales: 3 properties, map]
[Footer: ForecastEngine™ disclaimer, report date]
```

#### Multi-Page Deep Dive
```
Page 1: Executive Summary (above)
Page 2: Market Analysis (demographics, trends, heat map)
Page 3: Lien Discovery Details (title search, HOA status)
Page 4: Financial Projections (IRR, cash-on-cash, exit scenarios)
Page 5: Appendix (full comps table, data sources)
```

#### Dashboard View
```
[Top Bar: Auction date, property count, filters]
[Map View: Brevard County with property pins colored by recommendation]
[List View: Sortable table with key metrics]
[Detail Panel: Slides in on property selection]
```

### 4. Data Visualization

#### Charts (Use Recharts or Chart.js)
- **Equity Waterfall:** Shows ARV → liens → net equity flow
- **Price Trends:** 12-month historical prices in zip code
- **Bid/Judgment Ratio:** Scatter plot of historical auctions
- **Lien Priority Stack:** Horizontal bar chart of lien positions

#### Maps (Use Leaflet or Mapbox)
- **Property Location:** Pin with circle radius = equity amount
- **Comparable Sales:** Color-coded by days on market
- **Heat Map:** Foreclosure density by zip code
- **Demographic Overlay:** Median income, vacancy rates

#### Tables
- Zebra striping for readability
- Sortable columns (click header)
- Highlight row on hover
- Bold totals/subtotals
- Right-align numbers, left-align text

### 5. Interactive Elements

#### Progress Indicators
- Loading states: "Analyzing liens..." with progress bar
- Success: Green checkmark + "Analysis complete"
- Warning: Orange exclamation + "Manual review needed"
- Error: Red X + specific error message

#### Buttons
- Primary: Solid color, high contrast
- Secondary: Outline only
- Disabled: 50% opacity, no hover
- Loading: Spinner inside button

#### Forms
- Labels above inputs (not placeholder text)
- Error messages below field in red
- Required fields marked with *
- Auto-save drafts every 30 seconds

### 6. Accessibility

**WCAG 2.1 AA Compliance:**
- Color contrast ratio ≥ 4.5:1 for text
- All interactive elements keyboard accessible
- Skip navigation links
- Alt text for all images
- ARIA labels for screen readers

**Print Optimization:**
- Remove navigation, interactive elements
- Convert colors to grayscale-friendly
- Page breaks before major sections
- Footer with page numbers

### 7. Responsive Design

**Breakpoints:**
- Mobile: < 640px (single column, stacked metrics)
- Tablet: 640-1024px (two columns, condensed tables)
- Desktop: > 1024px (full layout, side-by-side comps)

**Mobile-First Approach:**
- Touch targets ≥ 44px
- Swipe gestures for image gallery
- Collapsible sections for long content
- Fixed header with property address

## Anti-Patterns (What NOT to Do)

### ❌ Generic AI Aesthetics
**Bad:** Purple/blue gradients, glassmorphism, excessive shadows
**Good:** Solid colors, subtle borders, purposeful whitespace

### ❌ Overloaded Dashboards
**Bad:** 20 metrics on screen, tiny fonts, cluttered layout
**Good:** 4-6 key metrics, clear hierarchy, progressive disclosure

### ❌ Inconsistent Terminology
**Bad:** "ARV" in one report, "After Repair Value" in another
**Good:** Pick one, use everywhere, define in glossary

### ❌ Unlabeled Numbers
**Bad:** "$450,000" with no context
**Good:** "ARV: $450,000 (Forecast confidence: 87%)"

### ❌ Missing Data Sources
**Bad:** "Property value: $X" with no attribution
**Good:** "ARV: $X (Source: BCPAO + 3 comps within 0.5mi, sold last 90 days)"

### ❌ Static PDFs Only
**Bad:** Email PDF, hope they read it
**Good:** Interactive HTML dashboard + PDF export option

## Implementation Examples

### React Component Pattern
```jsx
import { BidDeedTheme } from './themes';

function PropertyReport({ property, theme = 'investor' }) {
  const colors = BidDeedTheme[theme];
  
  return (
    <div style={{ background: colors.background }}>
      <Header logo={colors.primary} />
      <DecisionBox 
        recommendation={property.recommendation}
        color={property.recommendation === 'BID' ? colors.success : colors.warning}
      />
      <MetricsGrid data={property.metrics} />
    </div>
  );
}
```

### Theme Switching (Single Prompt)
```
"Convert this investor report to lender theme. 
Emphasize security and LTV ratios. 
Use blue accent colors. 
Reframe equity as collateral cushion."
```

### DOCX Template (Python-DOCX)
```python
from docx import Document
from docx.shared import RGBColor, Pt

doc = Document()

# Header
header = doc.add_heading('BidDeed.AI Property Analysis', level=1)
header.runs[0].font.color.rgb = RGBColor(30, 58, 95)  # Navy

# Decision box
decision = doc.add_paragraph()
decision.add_run('RECOMMENDATION: BID').bold = True
decision.runs[0].font.size = Pt(16)
decision.runs[0].font.color.rgb = RGBColor(46, 125, 50)  # Green
```

## Quality Checklist

Before delivering any report/dashboard:

- [ ] Brand colors used consistently
- [ ] All numbers have labels and sources
- [ ] Typography hierarchy clear (h1 > h2 > body)
- [ ] White space prevents cramped feeling
- [ ] Charts have titles and axis labels
- [ ] Tables are sortable and scannable
- [ ] Mobile view tested (if applicable)
- [ ] Print preview looks professional
- [ ] No spelling/grammar errors
- [ ] Confidence scores shown for predictions
- [ ] Disclaimer/date in footer
- [ ] "Powered by ForecastEngine™" attribution

## Tools & Libraries

**Recommended Stack:**
- React + TailwindCSS (web dashboards)
- Recharts (charts and graphs)
- Leaflet (maps)
- python-docx (DOCX reports)
- ReportLab (PDF reports)
- Shadcn/ui (component library)

**Fonts:**
- Google Fonts: Inter, JetBrains Mono
- Fallbacks: system-ui, Arial, monospace

**Icons:**
- Lucide React (consistent, open source)
- Avoid: Emoji (unprofessional), Font Awesome (overused)

## Edge Cases

### Missing BCPAO Photo
- Use street view from Google Maps API
- Or placeholder with property type icon (house, condo, land)

### Negative Equity
- Show in red, flag as "underwater"
- Still calculate max bid (may be $0 or plaintiff only)

### Extremely Long Lien Lists (10+ liens)
- Summary view: Top 3 liens + "7 more..."
- Expandable accordion for full list
- PDF appendix with complete table

### Zero Comparable Sales
- Widen radius (0.5mi → 1mi → 2mi)
- Expand timeframe (90 days → 180 days → 1 year)
- Fallback: BCPAO assessed value with disclaimer

## Metrics to Track

**Usage Analytics:**
- Reports generated per theme (investor/lender/contractor)
- Average time on dashboard page
- Most common filter combinations
- PDF download rate vs HTML view

**Quality Metrics:**
- User-reported accuracy of predictions
- Reports flagged for manual review
- Theme switch requests (indicates report flexibility)
- Time to generate report (should be < 10 seconds)

## Version History

- **v1.0 (Dec 2025):** Initial skill based on YouTube tutorial insights
- **Source:** "Steal This Nano Banana PRO Claude Code Skill" video
- **Next:** Add white-label support for broker partnerships

## Related Skills

- `bcpao-property-scraper.md` - Data source for property info
- `foreclosure-lien-analysis.md` - Core logic for lien priority
- `max-bid-calculator.md` - Financial calculations
- `brevard-market-intelligence.md` - Demographic and trend data

## Author Notes

This skill is inspired by the frontend-design skill from Anthropic, adapted specifically for foreclosure investment reports. The goal is to make BidDeed.AI reports indistinguishable from professional analyst output, not "AI-generated slop."

**Key insight from video:** "Doesn't look AI-generated" = trust. Every gradient removed, every shadow reduced, every color chosen purposefully.
