"""
Quick Start: Integrated Lien Discovery
Usage example for foreclosure investors
"""

from integrated_lien_discovery import IntegratedLienDiscovery

# Your Firecrawl API key
FIRECRAWL_API_KEY = "fc-985293d88ddf4d6595e041936ec2cb00"

# Initialize once
lien_discovery = IntegratedLienDiscovery(firecrawl_api_key=FIRECRAWL_API_KEY)

# Discover liens for a property (just the parcel ID!)
result = lien_discovery.discover_liens(parcel_id="2517790")

# Check the recommendation
if result['success']:
    recommendation = result['investment_analysis']['recommendation']
    reason = result['investment_analysis']['reason']
    
    print(f"Recommendation: {recommendation}")
    print(f"Reason: {reason}")
    
    # Check for HOA liens (CRITICAL!)
    hoa_count = result['lien_analysis']['hoa_liens']
    if hoa_count > 0:
        print(f"\n⚠️ WARNING: {hoa_count} HOA lien(s) detected!")
        print("HOA foreclosure may extinguish senior mortgages in Florida!")
else:
    print(f"Error: {result['error']}")
