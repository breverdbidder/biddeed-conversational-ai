"""
Integrated Lien Discovery Workflow
Combines BCPAO API (owner lookup) + Firecrawl AcclaimWeb (lien search)

This is the CORRECT way to use both systems together.
"""

import requests
import json
from typing import Dict, List, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntegratedLienDiscovery:
    """
    Two-step lien discovery process:
    1. Get owner name from BCPAO API
    2. Search AcclaimWeb by owner name using Firecrawl
    """
    
    def __init__(self, firecrawl_api_key: str):
        self.firecrawl_api_key = firecrawl_api_key
        self.bcpao_base_url = "https://www.bcpao.us/api/v1/search"
        self.firecrawl_base_url = "https://api.firecrawl.dev/v2"
    
    def discover_liens(
        self,
        parcel_id: str,
        include_mortgages: bool = True,
        include_liens: bool = True,
        include_judgments: bool = True
    ) -> Dict:
        """
        Complete lien discovery workflow
        
        Args:
            parcel_id: BCPAO parcel/account number (e.g., "2517790")
            include_mortgages: Search for mortgages (MTG)
            include_liens: Search for liens (LIEN)
            include_judgments: Search for judgments (JUDG)
            
        Returns:
            Complete lien discovery results with property data + liens
        """
        logger.info(f"Starting lien discovery for parcel {parcel_id}")
        
        # Step 1: Get owner name from BCPAO
        bcpao_data = self._get_owner_from_bcpao(parcel_id)
        
        if not bcpao_data['success']:
            return {
                "success": False,
                "error": "Failed to get property owner from BCPAO",
                "details": bcpao_data['error']
            }
        
        owner_name = bcpao_data['owner_name']
        address = bcpao_data['address']
        
        logger.info(f"Property: {address}")
        logger.info(f"Owner: {owner_name}")
        
        # Step 2: Search AcclaimWeb by owner name
        acclaimweb_result = self._search_acclaimweb(
            owner_name=owner_name,
            address=address,
            include_mortgages=include_mortgages,
            include_liens=include_liens,
            include_judgments=include_judgments
        )
        
        # Step 3: Combine results
        return self._combine_results(bcpao_data, acclaimweb_result)
    
    def _get_owner_from_bcpao(self, parcel_id: str) -> Dict:
        """
        Step 1: Get property owner from BCPAO API
        
        This is FREE and instant - always use the API!
        """
        logger.info(f"BCPAO API: Looking up parcel {parcel_id}")
        
        try:
            response = requests.get(
                self.bcpao_base_url,
                params={"accountNumber": parcel_id},
                timeout=10
            )
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"BCPAO API returned status {response.status_code}"
                }
            
            data = response.json()
            
            # Extract relevant fields
            owner_name = data.get('ownerName', '').strip()
            address = data.get('propertyAddress', '').strip()
            
            if not owner_name:
                return {
                    "success": False,
                    "error": "Owner name not found in BCPAO data"
                }
            
            return {
                "success": True,
                "parcel_id": parcel_id,
                "owner_name": owner_name,
                "address": address,
                "assessed_value": data.get('assessedValue', 0),
                "just_value": data.get('justValue', 0),
                "living_area": data.get('livingArea', 0),
                "year_built": data.get('yearBuilt', 0),
                "raw_data": data
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"BCPAO API error: {str(e)}")
            return {
                "success": False,
                "error": f"BCPAO API request failed: {str(e)}"
            }
    
    def _search_acclaimweb(
        self,
        owner_name: str,
        address: str,
        include_mortgages: bool,
        include_liens: bool,
        include_judgments: bool
    ) -> Dict:
        """
        Step 2: Search AcclaimWeb using Firecrawl Agent
        
        This requires Firecrawl because AcclaimWeb has no API
        """
        logger.info(f"AcclaimWeb: Searching for liens on {owner_name}")
        
        # Build document types list
        doc_types = []
        if include_mortgages:
            doc_types.append("MTG (Mortgage)")
        if include_liens:
            doc_types.append("LIEN (Lien)")
        if include_judgments:
            doc_types.append("JUDG (Judgment)")
        
        doc_types_str = ", ".join(doc_types)
        
        # Build Firecrawl Agent prompt
        prompt = f"""
Task: Extract recorded liens and mortgages from Brevard County Clerk AcclaimWeb

Property Information:
- Address: {address}
- Owner Name: {owner_name}
- Search By: OWNER NAME (grantee)

URL: https://or.brevardclerk.us/AcclaimWeb/search/SearchTypeName?SearchType=Image

CRITICAL: AcclaimWeb searches by PERSON NAME, not address!

STEP-BY-STEP NAVIGATION:

1. Navigate to https://or.brevardclerk.us/AcclaimWeb/search/SearchTypeName?SearchType=Image
2. Wait 3 seconds for page to fully load
3. Look for "Official Records Image Search" interface
4. Find the "Document Types" section (may be collapsed)
5. If "Document Types" is collapsed, click to expand it
6. Select these document type checkboxes: {doc_types_str}
7. Wait 1 second between each checkbox selection
8. Locate the search field (labeled "Name", "Grantee", or "Search Criteria")
9. Clear any existing text in the field
10. Enter EXACTLY: {owner_name}
11. Wait 1 second after typing
12. Click the Search button
13. Wait 10 seconds for results to load
14. Look for results table with columns: Type, Instrument #, Book/Page, Grantor, Grantee, Date, Amount
15. Extract ALL rows from the results

DATA EXTRACTION:

For EACH document/lien in the results table, extract:

{{
  "document_type": "MTG or LIEN or JUDG",
  "instrument_number": "the CFN or instrument number",
  "book": "book number",
  "page": "page number",
  "grantor": "WHO holds the lien (creditor - bank, HOA, IRS, etc.)",
  "grantee": "WHO owes the debt (should be {owner_name})",
  "recorded_date": "MM/DD/YYYY format",
  "amount": "dollar amount as number (no $ symbol)"
}}

CRITICAL - HOA LIEN DETECTION:

For each lien, examine the GRANTOR name for these keywords:
- HOMEOWNER
- HOMEOWNERS
- HOA
- ASSOCIATION
- CONDO
- CONDOMINIUM
- COMMUNITY

If ANY keyword found in grantor name:
- Add field: "hoa_lien": true
- Add field: "warning": "HOA lien detected - may extinguish senior mortgages in Florida foreclosure!"

If no keywords found:
- Add field: "hoa_lien": false

PAGINATION:

If you see "Page 1 of 3" or similar pagination:
- Extract from current page
- Click "Next" or page 2
- Extract those results
- Continue until all pages processed

VALIDATION:

- Verify grantee name matches or contains: {owner_name}
- Confirm recorded dates are in the past (not future)
- Check amounts are reasonable ($1,000 - $5,000,000 range)
- If grantee doesn't match owner, note as "possible_name_variant"

RETURN FORMAT:

Return a valid JSON object with this exact structure:

{{
  "success": true,
  "property_address": "{address}",
  "owner_name": "{owner_name}",
  "search_timestamp": "current ISO datetime",
  "total_documents": <count>,
  "documents": [
    {{
      "document_type": "MTG",
      "instrument_number": "2023000123",
      "book": "1234",
      "page": "567",
      "grantor": "WELLS FARGO BANK NA",
      "grantee": "{owner_name}",
      "recorded_date": "01/15/2023",
      "amount": 250000,
      "hoa_lien": false
    }},
    {{
      "document_type": "LIEN",
      "instrument_number": "2023000456",
      "book": "1235",
      "page": "890",
      "grantor": "SUNSET HOMEOWNERS ASSOCIATION INC",
      "grantee": "{owner_name}",
      "recorded_date": "03/20/2023",
      "amount": 5000,
      "hoa_lien": true,
      "warning": "HOA lien detected - may extinguish senior mortgages in Florida foreclosure!"
    }}
  ],
  "hoa_liens_detected": <true if any HOA liens found>,
  "total_hoa_liens": <count of HOA liens>
}}

ERROR HANDLING:

If no results found:
{{
  "success": true,
  "documents": [],
  "total_documents": 0,
  "message": "No liens found for owner: {owner_name}"
}}

If page fails to load:
{{
  "success": false,
  "error": "description of error",
  "stage": "navigation|search|extraction",
  "screenshot_url": "if available"
}}

IMPORTANT:
- Return ONLY valid JSON (no markdown, no code blocks, no extra text)
- All string values in double quotes
- All numeric values as numbers (not strings)
- Boolean values as true/false (not "true"/"false")
"""
        
        # Call Firecrawl Agent endpoint
        try:
            logger.info("Calling Firecrawl Agent...")
            
            response = requests.post(
                f"{self.firecrawl_base_url}/agent",
                headers={
                    "Authorization": f"Bearer {self.firecrawl_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "prompt": prompt,
                    "max_steps": 20,  # Allow enough steps for navigation
                    "output_format": "json"
                },
                timeout=120  # Allow up to 2 minutes for Agent to complete
            )
            
            if response.status_code != 200:
                logger.error(f"Firecrawl Agent failed: {response.status_code}")
                return {
                    "success": False,
                    "error": f"Firecrawl Agent returned status {response.status_code}",
                    "response": response.text
                }
            
            result = response.json()
            
            # Extract the Agent's output
            agent_output = result.get('data', {}).get('output', {})
            
            # Log credits used
            credits_used = result.get('data', {}).get('metadata', {}).get('creditsUsed', 'unknown')
            logger.info(f"Firecrawl credits used: {credits_used}")
            
            return {
                "success": True,
                "agent_result": agent_output,
                "credits_used": credits_used,
                "raw_response": result
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Firecrawl Agent request error: {str(e)}")
            return {
                "success": False,
                "error": f"Firecrawl Agent request failed: {str(e)}"
            }
    
    def _combine_results(self, bcpao_data: Dict, acclaimweb_result: Dict) -> Dict:
        """
        Step 3: Combine BCPAO property data with AcclaimWeb lien data
        """
        if not acclaimweb_result['success']:
            return {
                "success": False,
                "error": "AcclaimWeb search failed",
                "bcpao_data": bcpao_data,
                "acclaimweb_error": acclaimweb_result.get('error')
            }
        
        agent_output = acclaimweb_result.get('agent_result', {})
        
        # Parse liens from agent output
        liens = agent_output.get('documents', [])
        total_liens = len(liens)
        hoa_liens = [lien for lien in liens if lien.get('hoa_lien', False)]
        
        # Calculate total encumbrance
        total_encumbrance = sum(lien.get('amount', 0) for lien in liens)
        
        # Analyze lien priority
        mortgages = [lien for lien in liens if lien['document_type'] == 'MTG']
        other_liens = [lien for lien in liens if lien['document_type'] == 'LIEN']
        judgments = [lien for lien in liens if lien['document_type'] == 'JUDG']
        
        first_position = mortgages[0] if mortgages else None
        
        # Calculate net equity
        assessed_value = bcpao_data.get('assessed_value', 0)
        just_value = bcpao_data.get('just_value', 0)
        arv = max(assessed_value, just_value)  # Use higher value
        max_bid_equity = (arv * 0.70) - total_encumbrance - 10000  # 70% ARV - liens - closing
        
        # Build warnings
        warnings = []
        
        if hoa_liens:
            warnings.append({
                "type": "HOA_FORECLOSURE_RISK",
                "severity": "CRITICAL",
                "message": f"{len(hoa_liens)} HOA lien(s) detected - may extinguish senior mortgages in Florida!",
                "hoa_liens": hoa_liens
            })
        
        if len(mortgages) > 2:
            warnings.append({
                "type": "COMPLEX_TITLE",
                "severity": "MEDIUM",
                "message": f"{len(mortgages)} mortgages detected - complex title structure"
            })
        
        if max_bid_equity < 10000:
            warnings.append({
                "type": "INSUFFICIENT_EQUITY",
                "severity": "HIGH",
                "message": f"Insufficient equity after liens: ${max_bid_equity:,.2f}"
            })
        
        # Investment recommendation
        if hoa_liens:
            recommendation = "SKIP"
            reason = "HOA foreclosure risk - may wipe senior mortgages"
        elif max_bid_equity < 10000:
            recommendation = "SKIP"
            reason = "Insufficient equity after liens"
        elif len(mortgages) > 2:
            recommendation = "REVIEW"
            reason = "Complex title - verify lien priority with attorney"
        else:
            recommendation = "BID"
            reason = "Acceptable lien structure and equity position"
        
        return {
            "success": True,
            "timestamp": datetime.utcnow().isoformat(),
            
            # Property Data (from BCPAO)
            "property": {
                "parcel_id": bcpao_data['parcel_id'],
                "address": bcpao_data['address'],
                "owner_name": bcpao_data['owner_name'],
                "assessed_value": assessed_value,
                "just_value": just_value,
                "living_area": bcpao_data.get('living_area', 0),
                "year_built": bcpao_data.get('year_built', 0)
            },
            
            # Lien Analysis (from AcclaimWeb)
            "lien_analysis": {
                "total_liens": total_liens,
                "total_encumbrance": total_encumbrance,
                "mortgages": len(mortgages),
                "other_liens": len(other_liens),
                "judgments": len(judgments),
                "hoa_liens": len(hoa_liens),
                "first_position": first_position
            },
            
            # All Liens
            "liens": liens,
            
            # Investment Analysis
            "investment_analysis": {
                "arv": arv,
                "max_bid_equity_70pct": max_bid_equity,
                "recommendation": recommendation,
                "reason": reason,
                "warnings": warnings
            },
            
            # Metadata
            "metadata": {
                "bcpao_source": "Direct API (FREE)",
                "acclaimweb_source": "Firecrawl Agent",
                "credits_used": acclaimweb_result.get('credits_used', 'unknown')
            }
        }


def main():
    """Example usage"""
    
    # Configuration
    FIRECRAWL_API_KEY = "fc-985293d88ddf4d6595e041936ec2cb00"
    TEST_PARCEL = "2517790"  # 4127 Arlington Ave
    
    # Initialize workflow
    discovery = IntegratedLienDiscovery(firecrawl_api_key=FIRECRAWL_API_KEY)
    
    # Run complete lien discovery
    print("=" * 80)
    print("INTEGRATED LIEN DISCOVERY WORKFLOW")
    print("=" * 80)
    print(f"\nProperty: Parcel {TEST_PARCEL}")
    print(f"\nStep 1: Getting owner from BCPAO API...")
    print(f"Step 2: Searching AcclaimWeb for liens...")
    print(f"\nPlease wait 30-60 seconds for Firecrawl Agent...\n")
    
    result = discovery.discover_liens(
        parcel_id=TEST_PARCEL,
        include_mortgages=True,
        include_liens=True,
        include_judgments=True
    )
    
    # Display results
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)
    
    if result['success']:
        # Property Info
        prop = result['property']
        print(f"\n📍 PROPERTY:")
        print(f"   Address: {prop['address']}")
        print(f"   Owner: {prop['owner_name']}")
        print(f"   Assessed Value: ${prop['assessed_value']:,}")
        
        # Lien Analysis
        analysis = result['lien_analysis']
        print(f"\n🔍 LIEN ANALYSIS:")
        print(f"   Total Liens: {analysis['total_liens']}")
        print(f"   Total Encumbrance: ${analysis['total_encumbrance']:,}")
        print(f"   - Mortgages: {analysis['mortgages']}")
        print(f"   - Other Liens: {analysis['other_liens']}")
        print(f"   - Judgments: {analysis['judgments']}")
        print(f"   - HOA Liens: {analysis['hoa_liens']} {'⚠️ CRITICAL!' if analysis['hoa_liens'] > 0 else ''}")
        
        # First Position
        if analysis['first_position']:
            fp = analysis['first_position']
            print(f"\n   First Position:")
            print(f"   - Grantor: {fp['grantor']}")
            print(f"   - Amount: ${fp.get('amount', 0):,}")
            print(f"   - Date: {fp.get('recorded_date', 'N/A')}")
        
        # Investment Recommendation
        inv = result['investment_analysis']
        print(f"\n💰 INVESTMENT ANALYSIS:")
        print(f"   ARV: ${inv['arv']:,}")
        print(f"   Max Bid Equity (70% - liens): ${inv['max_bid_equity_70pct']:,}")
        print(f"   Recommendation: {inv['recommendation']}")
        print(f"   Reason: {inv['reason']}")
        
        # Warnings
        if inv['warnings']:
            print(f"\n⚠️  WARNINGS:")
            for warning in inv['warnings']:
                print(f"   [{warning['severity']}] {warning['message']}")
        
        # Detailed Liens
        if result['liens']:
            print(f"\n📋 DETAILED LIENS:")
            for idx, lien in enumerate(result['liens'], 1):
                print(f"\n   Lien #{idx}:")
                print(f"   Type: {lien['document_type']}")
                print(f"   Grantor: {lien['grantor']}")
                print(f"   Amount: ${lien.get('amount', 0):,}")
                print(f"   Date: {lien.get('recorded_date', 'N/A')}")
                if lien.get('hoa_lien'):
                    print(f"   ⚠️  HOA LIEN - HIGH RISK!")
        
        # Metadata
        meta = result['metadata']
        print(f"\n📊 METADATA:")
        print(f"   BCPAO Source: {meta['bcpao_source']}")
        print(f"   AcclaimWeb Source: {meta['acclaimweb_source']}")
        print(f"   Credits Used: {meta['credits_used']}")
        
        # Save to file
        output_file = f"lien_discovery_{TEST_PARCEL}.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n💾 Full results saved to: {output_file}")
        
    else:
        print(f"\n❌ ERROR: {result.get('error')}")
        print(f"Details: {json.dumps(result, indent=2)}")


if __name__ == "__main__":
    main()
