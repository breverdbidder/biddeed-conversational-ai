"""
BidDeed.AI LangGraph Orchestrator
Autonomous foreclosure research agent with multi-node workflow.

Architecture inspired by Manus AI:
- CodeAct pattern (Python execution vs JSON tool calls)
- Multi-agent coordination
- Context engineering for long tasks
- Error recovery in context
"""

import os
import json
import asyncio
from datetime import datetime
from typing import TypedDict, Annotated, List, Optional
from dataclasses import dataclass

# LangGraph imports (install: pip install langgraph langchain-anthropic)
try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    print("LangGraph not installed. Run: pip install langgraph")

import httpx

# Configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://mocerqjnksmhcjzxrewo.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")


@dataclass
class ForeclosureProperty:
    """Property data structure."""
    case_number: str
    address: str
    city: str
    zipcode: str
    judgment_amount: float
    plaintiff: str
    auction_date: str
    
    # Enrichment fields
    bcpao_account: Optional[str] = None
    assessed_value: Optional[float] = None
    year_built: Optional[int] = None
    sqft: Optional[int] = None
    photo_url: Optional[str] = None
    
    # Analysis fields
    max_bid: Optional[float] = None
    ml_score: Optional[float] = None
    recommendation: Optional[str] = None
    
    # Lien analysis
    has_senior_mortgage: bool = False
    lien_notes: Optional[str] = None


class AgentState(TypedDict):
    """State passed between nodes in the workflow."""
    query: str
    intent: dict
    properties: List[dict]
    current_property: Optional[dict]
    analysis_results: List[dict]
    errors: List[str]
    messages: List[dict]
    stage: int
    status: str


# ============== AGENT NODES ==============

async def parse_query_node(state: AgentState) -> AgentState:
    """Node 1: Parse natural language query into structured intent."""
    query = state["query"].lower()
    
    intent = {
        "type": "general",
        "filters": {},
        "entities": [],
        "action": None
    }
    
    # Detect intent type
    if any(w in query for w in ["show", "find", "list", "get"]):
        intent["type"] = "search"
        if "bid" in query and "skip" not in query:
            intent["filters"]["recommendation"] = "BID"
        elif "review" in query:
            intent["filters"]["recommendation"] = "REVIEW"
        elif "skip" in query:
            intent["filters"]["recommendation"] = "SKIP"
    
    elif any(w in query for w in ["analyze", "analysis", "research"]):
        intent["type"] = "analyze"
        intent["action"] = "full_analysis"
    
    elif any(w in query for w in ["pipeline", "run", "execute"]):
        intent["type"] = "pipeline"
        intent["action"] = "run_pipeline"
    
    elif any(w in query for w in ["lien", "title", "mortgage"]):
        intent["type"] = "lien_analysis"
    
    elif any(w in query for w in ["plaintiff", "bank", "servicer"]):
        intent["type"] = "plaintiff_analysis"
    
    # Extract date filters
    date_patterns = {
        "jan 7": "2025-01-07", "january 7": "2025-01-07",
        "dec 17": "2025-12-17", "december 17": "2025-12-17",
        "dec 3": "2025-12-03", "december 3": "2025-12-03",
    }
    for pattern, date in date_patterns.items():
        if pattern in query:
            intent["filters"]["auction_date"] = date
            break
    
    # Extract city
    cities = ["palm bay", "melbourne", "cocoa", "titusville", "satellite beach", "merritt island", "viera"]
    for city in cities:
        if city in query:
            intent["filters"]["city"] = city.upper()
            break
    
    state["intent"] = intent
    state["stage"] = 1
    state["status"] = "query_parsed"
    state["messages"].append({
        "role": "system",
        "content": f"Parsed query intent: {intent['type']}",
        "timestamp": datetime.utcnow().isoformat()
    })
    
    return state


async def fetch_properties_node(state: AgentState) -> AgentState:
    """Node 2: Fetch properties from Supabase based on intent."""
    intent = state["intent"]
    
    if not SUPABASE_KEY:
        state["errors"].append("SUPABASE_KEY not configured")
        state["status"] = "error"
        return state
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }
    
    # Build query
    url = f"{SUPABASE_URL}/rest/v1/auction_results?select=*"
    
    filters = intent.get("filters", {})
    if filters.get("recommendation"):
        url += f"&recommendation=eq.{filters['recommendation']}"
    if filters.get("auction_date"):
        url += f"&auction_date=eq.{filters['auction_date']}"
    if filters.get("city"):
        url += f"&city=ilike.%{filters['city']}%"
    
    url += "&order=auction_date.asc&limit=50"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                state["properties"] = response.json()
                state["status"] = "properties_fetched"
                state["messages"].append({
                    "role": "system",
                    "content": f"Fetched {len(state['properties'])} properties",
                    "timestamp": datetime.utcnow().isoformat()
                })
            else:
                state["errors"].append(f"Supabase error: {response.status_code}")
    except Exception as e:
        state["errors"].append(f"Fetch error: {str(e)}")
    
    state["stage"] = 2
    return state


async def enrich_property_node(state: AgentState) -> AgentState:
    """Node 3: Enrich current property with BCPAO data."""
    prop = state.get("current_property")
    if not prop:
        return state
    
    # BCPAO API endpoint
    bcpao_url = "https://gis.brevardfl.gov/gissrv/rest/services/Base_Map/Parcel_New_WKID2881/MapServer/5/query"
    
    # Search by address
    address = prop.get("property_address", "")
    params = {
        "where": f"UPPER(SITUS_ADDR) LIKE '%{address.split(',')[0].upper()}%'",
        "outFields": "*",
        "f": "json"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(bcpao_url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                features = data.get("features", [])
                if features:
                    attrs = features[0].get("attributes", {})
                    prop["bcpao_account"] = attrs.get("ACCT")
                    prop["assessed_value"] = attrs.get("JV")
                    prop["sqft"] = attrs.get("LIV_AREA")
                    prop["year_built"] = attrs.get("YR_BLT")
                    
                    state["messages"].append({
                        "role": "system",
                        "content": f"Enriched property with BCPAO data: {prop.get('bcpao_account')}",
                        "timestamp": datetime.utcnow().isoformat()
                    })
    except Exception as e:
        state["errors"].append(f"BCPAO enrichment error: {str(e)}")
    
    state["current_property"] = prop
    state["stage"] = 3
    return state


async def lien_analysis_node(state: AgentState) -> AgentState:
    """Node 4: Analyze lien priority for current property."""
    prop = state.get("current_property")
    if not prop:
        return state
    
    plaintiff = prop.get("plaintiff", "").upper()
    
    # HOA detection patterns
    hoa_keywords = ["HOA", "HOMEOWNERS", "CONDOMINIUM", "ASSOCIATION", "COA", "POA"]
    is_hoa = any(kw in plaintiff for kw in hoa_keywords)
    
    if is_hoa:
        prop["has_senior_mortgage"] = True
        prop["lien_notes"] = "HOA foreclosure - senior mortgage likely survives"
        prop["recommendation"] = "SKIP"
        
        state["messages"].append({
            "role": "warning",
            "content": f"HOA foreclosure detected: {plaintiff}. Senior mortgage survives.",
            "timestamp": datetime.utcnow().isoformat()
        })
    else:
        prop["has_senior_mortgage"] = False
        prop["lien_notes"] = "Mortgage foreclosure - standard lien priority"
    
    state["current_property"] = prop
    state["stage"] = 4
    return state


async def calculate_max_bid_node(state: AgentState) -> AgentState:
    """Node 5: Calculate max bid using BidDeed formula."""
    prop = state.get("current_property")
    if not prop:
        return state
    
    # Get ARV (After Repair Value) - use assessed value or judgment as proxy
    arv = prop.get("assessed_value") or prop.get("judgment_amount", 0) * 1.2
    
    # Estimate repairs (20% of ARV for conservative estimate)
    repairs = arv * 0.20
    
    # BidDeed Max Bid Formula:
    # (ARV × 70%) - Repairs - $10K - MIN($25K, 15% of ARV)
    margin = min(25000, arv * 0.15)
    max_bid = (arv * 0.70) - repairs - 10000 - margin
    
    prop["max_bid"] = max(0, max_bid)
    
    # Calculate bid/judgment ratio
    judgment = prop.get("judgment_amount", 1)
    ratio = (prop["max_bid"] / judgment) * 100 if judgment > 0 else 0
    
    # Set recommendation based on ratio
    if prop.get("recommendation") != "SKIP":  # Don't override HOA skip
        if ratio >= 75:
            prop["recommendation"] = "BID"
        elif ratio >= 60:
            prop["recommendation"] = "REVIEW"
        else:
            prop["recommendation"] = "SKIP"
    
    state["messages"].append({
        "role": "system",
        "content": f"Max bid calculated: ${prop['max_bid']:,.0f} ({ratio:.0f}% of judgment) → {prop['recommendation']}",
        "timestamp": datetime.utcnow().isoformat()
    })
    
    state["current_property"] = prop
    state["stage"] = 5
    return state


async def ml_scoring_node(state: AgentState) -> AgentState:
    """Node 6: Apply ML model for third-party probability."""
    prop = state.get("current_property")
    if not prop:
        return state
    
    # Simplified ML scoring based on plaintiff patterns
    plaintiff = prop.get("plaintiff", "").upper()
    
    # High third-party probability plaintiffs (from historical data)
    high_tp_plaintiffs = ["FREEDOM", "LAKEVIEW", "NATIONSTAR", "MR COOPER", "NEWREZ"]
    low_tp_plaintiffs = ["HOA", "ASSOCIATION", "TAX", "LIEN"]
    
    base_score = 0.5
    
    if any(p in plaintiff for p in high_tp_plaintiffs):
        base_score = 0.75
    elif any(p in plaintiff for p in low_tp_plaintiffs):
        base_score = 0.15
    
    # Adjust based on judgment amount
    judgment = prop.get("judgment_amount", 0)
    if judgment < 100000:
        base_score *= 0.8  # Lower value = less third-party interest
    elif judgment > 300000:
        base_score *= 1.1  # Higher value = more interest
    
    prop["ml_score"] = min(0.99, max(0.01, base_score))
    
    state["messages"].append({
        "role": "system",
        "content": f"ML score: {prop['ml_score']:.0%} third-party probability",
        "timestamp": datetime.utcnow().isoformat()
    })
    
    state["current_property"] = prop
    state["stage"] = 6
    return state


async def generate_report_node(state: AgentState) -> AgentState:
    """Node 7: Generate analysis report."""
    prop = state.get("current_property")
    if not prop:
        return state
    
    report = {
        "case_number": prop.get("case_number"),
        "address": prop.get("property_address"),
        "judgment_amount": prop.get("judgment_amount"),
        "max_bid": prop.get("max_bid"),
        "ml_score": prop.get("ml_score"),
        "recommendation": prop.get("recommendation"),
        "lien_notes": prop.get("lien_notes"),
        "auction_date": prop.get("auction_date"),
        "generated_at": datetime.utcnow().isoformat()
    }
    
    state["analysis_results"].append(report)
    state["stage"] = 7
    state["status"] = "analysis_complete"
    
    return state


async def save_results_node(state: AgentState) -> AgentState:
    """Node 8: Save results to Supabase."""
    if not state["analysis_results"] or not SUPABASE_KEY:
        return state
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }
    
    for result in state["analysis_results"]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{SUPABASE_URL}/rest/v1/auction_results",
                    headers=headers,
                    json=result
                )
                if response.status_code in [200, 201]:
                    state["messages"].append({
                        "role": "system",
                        "content": f"Saved analysis for {result.get('case_number')}",
                        "timestamp": datetime.utcnow().isoformat()
                    })
        except Exception as e:
            state["errors"].append(f"Save error: {str(e)}")
    
    state["stage"] = 8
    state["status"] = "complete"
    return state


# ============== WORKFLOW BUILDER ==============

def should_continue(state: AgentState) -> str:
    """Router function to determine next step."""
    if state["errors"]:
        return "handle_error"
    if state["status"] == "complete":
        return END
    
    intent_type = state["intent"].get("type", "general")
    
    if intent_type == "search" and state["stage"] >= 2:
        return END
    elif intent_type == "analyze" and state["stage"] >= 7:
        return "save_results"
    elif intent_type == "pipeline" and state["stage"] >= 8:
        return END
    
    return "continue"


def build_workflow():
    """Build the LangGraph workflow."""
    if not LANGGRAPH_AVAILABLE:
        return None
    
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("parse_query", parse_query_node)
    workflow.add_node("fetch_properties", fetch_properties_node)
    workflow.add_node("enrich_property", enrich_property_node)
    workflow.add_node("lien_analysis", lien_analysis_node)
    workflow.add_node("calculate_max_bid", calculate_max_bid_node)
    workflow.add_node("ml_scoring", ml_scoring_node)
    workflow.add_node("generate_report", generate_report_node)
    workflow.add_node("save_results", save_results_node)
    
    # Set entry point
    workflow.set_entry_point("parse_query")
    
    # Add edges
    workflow.add_edge("parse_query", "fetch_properties")
    workflow.add_conditional_edges(
        "fetch_properties",
        lambda s: "enrich_property" if s["intent"]["type"] in ["analyze", "pipeline"] else END
    )
    workflow.add_edge("enrich_property", "lien_analysis")
    workflow.add_edge("lien_analysis", "calculate_max_bid")
    workflow.add_edge("calculate_max_bid", "ml_scoring")
    workflow.add_edge("ml_scoring", "generate_report")
    workflow.add_edge("generate_report", "save_results")
    workflow.add_edge("save_results", END)
    
    return workflow.compile(checkpointer=MemorySaver())


# ============== MAIN EXECUTION ==============

async def run_agent(query: str) -> dict:
    """Run the agent with a natural language query."""
    initial_state: AgentState = {
        "query": query,
        "intent": {},
        "properties": [],
        "current_property": None,
        "analysis_results": [],
        "errors": [],
        "messages": [],
        "stage": 0,
        "status": "initialized"
    }
    
    if LANGGRAPH_AVAILABLE:
        workflow = build_workflow()
        if workflow:
            config = {"configurable": {"thread_id": "biddeed-agent-1"}}
            result = await workflow.ainvoke(initial_state, config)
            return result
    
    # Fallback: run nodes sequentially
    state = initial_state
    state = await parse_query_node(state)
    state = await fetch_properties_node(state)
    
    if state["intent"]["type"] in ["analyze", "pipeline"] and state["properties"]:
        state["current_property"] = state["properties"][0]
        state = await enrich_property_node(state)
        state = await lien_analysis_node(state)
        state = await calculate_max_bid_node(state)
        state = await ml_scoring_node(state)
        state = await generate_report_node(state)
        state = await save_results_node(state)
    
    return state


if __name__ == "__main__":
    # Test the agent
    async def main():
        print("🚀 BidDeed.AI LangGraph Agent")
        print("=" * 50)
        
        queries = [
            "Show me BID properties for Jan 7",
            "Analyze 923 Slocum St Palm Bay",
            "Run pipeline on next auction"
        ]
        
        for query in queries:
            print(f"\n📝 Query: {query}")
            result = await run_agent(query)
            print(f"   Status: {result['status']}")
            print(f"   Properties: {len(result['properties'])}")
            print(f"   Messages: {len(result['messages'])}")
            if result['errors']:
                print(f"   Errors: {result['errors']}")
    
    asyncio.run(main())
