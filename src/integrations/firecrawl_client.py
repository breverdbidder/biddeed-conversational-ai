"""
Firecrawl Client for BidDeed.AI
Handles web scraping for sites without public APIs
"""

import requests
import time
import re
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class FirecrawlClient:
    """Client for Firecrawl API v2"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.firecrawl.dev/v2"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def scrape(
        self,
        url: str,
        formats: List[str] = ["markdown"],
        actions: Optional[List[Dict]] = None,
        wait_for: int = 5000,
        max_age: int = 600000
    ) -> Dict:
        """
        Scrape a URL with Firecrawl
        
        Args:
            url: Target URL
            formats: Output formats (markdown, html, json, screenshot)
            actions: Browser actions to perform
            wait_for: Milliseconds to wait for page load
            max_age: Cache age in milliseconds
            
        Returns:
            Response data dict
        """
        payload = {
            "url": url,
            "formats": formats,
            "waitFor": wait_for,
            "maxAge": max_age
        }
        
        if actions:
            payload["actions"] = actions
        
        logger.info(f"Firecrawl scrape: {url}")
        start_time = time.time()
        
        response = requests.post(
            f"{self.base_url}/scrape",
            json=payload,
            headers=self.headers
        )
        
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            credits_used = data.get('data', {}).get('metadata', {}).get('creditsUsed', 'unknown')
            logger.info(f"Firecrawl success: {duration:.2f}s, {credits_used} credits")
            return data
        else:
            logger.error(f"Firecrawl failed: {response.status_code} - {response.text}")
            response.raise_for_status()


class AcclaimWebClient:
    """Client for Brevard County Clerk AcclaimWeb system"""
    
    def __init__(self, firecrawl_client: FirecrawlClient):
        self.firecrawl = firecrawl_client
        self.base_url = "https://or.brevardclerk.us/AcclaimWeb"
    
    def search_liens(
        self,
        address: str,
        parcel_id: Optional[str] = None,
        include_mortgages: bool = True,
        include_liens: bool = True,
        include_judgments: bool = True
    ) -> Dict:
        """
        Search AcclaimWeb for liens on a property
        
        Args:
            address: Property address to search
            parcel_id: Optional parcel ID for more precise search
            include_mortgages: Include mortgage records
            include_liens: Include lien records
            include_judgments: Include judgment records
            
        Returns:
            Dict with liens data and metadata
        """
        logger.info(f"AcclaimWeb lien search: {address}")
        
        # Build actions sequence
        actions = [
            {"type": "wait", "milliseconds": 3000},
        ]
        
        # Select document types
        if include_mortgages:
            actions.append({"type": "click", "selector": "input[value='MTG']"})
            actions.append({"type": "wait", "milliseconds": 500})
        
        if include_liens:
            actions.append({"type": "click", "selector": "input[value='LIEN']"})
            actions.append({"type": "wait", "milliseconds": 500})
        
        if include_judgments:
            actions.append({"type": "click", "selector": "input[value='JUDG']"})
            actions.append({"type": "wait", "milliseconds": 500})
        
        # Enter search criteria
        search_text = parcel_id if parcel_id else address
        actions.extend([
            {
                "type": "write",
                "selector": "input[name='NameSearchModel.SearchCriteria']",
                "text": search_text
            },
            {"type": "wait", "milliseconds": 1000},
            {"type": "click", "selector": "button[type='submit']"},
            {"type": "wait", "milliseconds": 5000},
            {"type": "screenshot"}
        ])
        
        # Scrape with Firecrawl
        try:
            result = self.firecrawl.scrape(
                url=f"{self.base_url}/search/SearchTypeName?SearchType=Image",
                formats=["markdown"],
                actions=actions
            )
            
            if result.get('success'):
                markdown = result['data']['markdown']
                screenshot = result['data'].get('actions', {}).get('screenshots', [None])[0]
                
                # Parse liens from markdown
                liens = self._parse_liens(markdown)
                
                return {
                    "success": True,
                    "address": address,
                    "parcel_id": parcel_id,
                    "liens": liens,
                    "total_liens": len(liens),
                    "screenshot": screenshot,
                    "raw_markdown": markdown,
                    "search_timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": result.get('error', 'Unknown error'),
                    "address": address
                }
                
        except Exception as e:
            logger.error(f"AcclaimWeb search failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "address": address
            }
    
    def _parse_liens(self, markdown: str) -> List[Dict]:
        """
        Parse lien information from AcclaimWeb search results
        
        Args:
            markdown: Raw markdown from Firecrawl
            
        Returns:
            List of lien dictionaries
        """
        liens = []
        
        # AcclaimWeb result patterns
        # Example: "MTG | 2023-12345 | Book 1234 Page 567 | WELLS FARGO | JOHN DOE | 01/15/2023 | $250,000"
        
        # Pattern for lien records (adjust based on actual AcclaimWeb format)
        lien_pattern = re.compile(
            r'(MTG|LIEN|JUDG)\s*\|\s*'  # Document type
            r'(\d{4}-\d+)\s*\|\s*'       # Instrument number
            r'Book\s*(\d+)\s*Page\s*(\d+)\s*\|\s*'  # Book/Page
            r'([^|]+)\|\s*'              # Grantor (creditor)
            r'([^|]+)\|\s*'              # Grantee (debtor)
            r'(\d{2}/\d{2}/\d{4})\s*\|\s*'  # Date
            r'\$?([\d,]+)'               # Amount
        )
        
        # Also look for simpler patterns
        lines = markdown.split('\n')
        
        for line in lines:
            match = lien_pattern.search(line)
            if match:
                lien = {
                    "type": match.group(1),
                    "instrument_number": match.group(2),
                    "book": match.group(3),
                    "page": match.group(4),
                    "grantor": match.group(5).strip(),
                    "grantee": match.group(6).strip(),
                    "recorded_date": match.group(7),
                    "amount": self._parse_amount(match.group(8))
                }
                liens.append(lien)
        
        # Detect HOA liens (critical for foreclosure analysis)
        for lien in liens:
            if any(keyword in lien['grantor'].upper() for keyword in [
                'HOMEOWNER', 'HOA', 'ASSOCIATION', 'CONDO', 'COMMUNITY'
            ]):
                lien['is_hoa'] = True
                lien['warning'] = "HOA lien may wipe senior mortgages if foreclosed"
            else:
                lien['is_hoa'] = False
        
        # Sort by recorded date (oldest first)
        liens.sort(key=lambda x: datetime.strptime(x['recorded_date'], '%m/%d/%Y'))
        
        return liens
    
    def _parse_amount(self, amount_str: str) -> float:
        """Parse dollar amount from string"""
        try:
            # Remove commas and dollar signs
            cleaned = amount_str.replace(',', '').replace('$', '').strip()
            return float(cleaned)
        except (ValueError, AttributeError):
            return 0.0
    
    def analyze_lien_priority(self, liens: List[Dict]) -> Dict:
        """
        Analyze lien priority and total encumbrance
        
        Args:
            liens: List of lien dictionaries from _parse_liens
            
        Returns:
            Analysis dict with priority order and warnings
        """
        analysis = {
            "total_liens": len(liens),
            "total_encumbrance": sum(lien['amount'] for lien in liens),
            "first_position": None,
            "hoa_liens": [],
            "mortgages": [],
            "judgments": [],
            "warnings": []
        }
        
        # Categorize liens
        for idx, lien in enumerate(liens):
            lien['priority_position'] = idx + 1
            
            if lien['type'] == 'MTG':
                analysis['mortgages'].append(lien)
                if idx == 0:
                    analysis['first_position'] = lien
            elif lien['type'] == 'LIEN':
                if lien.get('is_hoa'):
                    analysis['hoa_liens'].append(lien)
                    analysis['warnings'].append({
                        "type": "HOA_FORECLOSURE_RISK",
                        "message": f"HOA lien detected: {lien['grantor']} - may wipe senior mortgages",
                        "lien": lien
                    })
            elif lien['type'] == 'JUDG':
                analysis['judgments'].append(lien)
        
        # Check for title issues
        if len(analysis['mortgages']) > 2:
            analysis['warnings'].append({
                "type": "MULTIPLE_MORTGAGES",
                "message": f"{len(analysis['mortgages'])} mortgages detected - complex title",
                "count": len(analysis['mortgages'])
            })
        
        if analysis['total_encumbrance'] > 0:
            analysis['encumbrance_summary'] = {
                "total": analysis['total_encumbrance'],
                "first_mortgage": analysis['first_position']['amount'] if analysis['first_position'] else 0,
                "other_liens": analysis['total_encumbrance'] - (
                    analysis['first_position']['amount'] if analysis['first_position'] else 0
                )
            }
        
        return analysis


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize clients
    FIRECRAWL_API_KEY = "fc-985293d88ddf4d6595e041936ec2cb00"
    
    firecrawl = FirecrawlClient(api_key=FIRECRAWL_API_KEY)
    acclaimweb = AcclaimWebClient(firecrawl_client=firecrawl)
    
    # Test with property from Jan 7 auction
    result = acclaimweb.search_liens(
        address="4127 ARLINGTON AVE",
        include_mortgages=True,
        include_liens=True,
        include_judgments=True
    )
    
    print("=" * 80)
    print("ACCLAIMWEB LIEN SEARCH RESULTS")
    print("=" * 80)
    print(f"Address: {result['address']}")
    print(f"Success: {result['success']}")
    
    if result['success']:
        print(f"Total liens found: {result['total_liens']}")
        
        if result['liens']:
            print("\nLIENS DETECTED:")
            for lien in result['liens']:
                print(f"\n  {lien['type']}: {lien['instrument_number']}")
                print(f"  Creditor: {lien['grantor']}")
                print(f"  Debtor: {lien['grantee']}")
                print(f"  Amount: ${lien['amount']:,.2f}")
                print(f"  Date: {lien['recorded_date']}")
                if lien.get('is_hoa'):
                    print(f"  ⚠️ HOA LIEN - HIGH RISK")
        
        # Analyze priority
        if result['liens']:
            analysis = acclaimweb.analyze_lien_priority(result['liens'])
            
            print("\n" + "=" * 80)
            print("LIEN PRIORITY ANALYSIS")
            print("=" * 80)
            print(f"Total encumbrance: ${analysis['total_encumbrance']:,.2f}")
            
            if analysis['first_position']:
                print(f"\nFirst position: {analysis['first_position']['grantor']}")
                print(f"Amount: ${analysis['first_position']['amount']:,.2f}")
            
            if analysis['warnings']:
                print(f"\n⚠️ {len(analysis['warnings'])} WARNINGS:")
                for warning in analysis['warnings']:
                    print(f"  - {warning['type']}: {warning['message']}")
        
        if result.get('screenshot'):
            print(f"\n📸 Screenshot: {result['screenshot']}")
    else:
        print(f"Error: {result.get('error')}")
