#!/usr/bin/env python3
"""
BidDeed.AI Foreclosure Research Agent
LangGraph-based autonomous agent following OpenManus ReAct pattern
"""
import os, json, asyncio
from datetime import datetime
from typing import TypedDict, List

try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver
    HAS_LANGGRAPH = True
except ImportError:
    HAS_LANGGRAPH = False

import httpx

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://mocerqjnksmhcjzxrewo.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
USER_QUERY = os.environ.get("USER_QUERY", "Show BID recommendations")
SESSION_ID = os.environ.get("SESSION_ID", "default")

class AgentState(TypedDict):
    query: str
    session_id: str
    intent: dict
    properties: List[dict]
    analysis: dict
    response: str
    activities: List[dict]
    completed: bool

FORECLOSURES = [
    {"c":"05-2024-CA-029012","a":"2450 PALM BAY RD NE, PALM BAY","j":185000,"m":147000,"r":"BID","s":0.99,"d":"2025-12-03","p":"Freedom Mortgage"},
    {"c":"05-2024-CA-014947","a":"808 EMERSON DR, PALM BAY","j":219655,"m":175724,"r":"BID","s":0.81,"d":"2025-12-17","p":"LAKEVIEW LOAN"},
    {"c":"05-2024-CA-048653","a":"775 JACARANDA ST, MERRITT ISLAND","j":110864,"m":88691,"r":"BID","s":0.78,"d":"2025-12-17","p":"DATA MORTGAGE"},
    {"c":"05-2025-CA-013384","a":"2551 STRATFORD DR, COCOA","j":166431,"m":133145,"r":"BID","s":0.82,"d":"2025-12-17","p":"HUNTINGTON"},
    {"c":"05-2025-CA-022257","a":"923 SLOCUM ST, PALM BAY","j":143880,"m":115104,"r":"BID","s":0.79,"d":"2025-12-17","p":"US BANK"},
    {"c":"05-2025-CA-026675","a":"4461 LONGBOW DR, TITUSVILLE","j":224779,"m":179823,"r":"BID","s":0.83,"d":"2025-12-17","p":"NEWREZ"},
    {"c":"05-2025-CA-034578","a":"520 HOLMES AVE, PALM BAY","j":268305,"m":214644,"r":"BID","s":0.76,"d":"2025-12-17","p":"UNITED WHOLESALE"},
    {"c":"05-2024-CA-045234","a":"925 ATLANTUS TER, SATELLITE BEACH","j":425000,"m":340000,"r":"BID","s":0.85,"d":"2025-01-07","p":"NATIONSTAR"},
    {"c":"05-2024-CA-045567","a":"4521 N ATLANTIC AVE, COCOA BEACH","j":520000,"m":416000,"r":"BID","s":0.82,"d":"2025-01-07","p":"JPMORGAN CHASE"},
    {"c":"05-2024-CA-045789","a":"987 VIERA BLVD, VIERA","j":485000,"m":388000,"r":"BID","s":0.85,"d":"2025-01-07","p":"LOANCARE LLC"},
    {"c":"05-2022-CA-035649","a":"5600 GRAHAM ST, COCOA","j":279230,"m":161612,"r":"REVIEW","s":0.45,"d":"2025-12-03","p":"US Bank NA"},
    {"c":"05-2024-CA-018884","a":"906 SHAW CIR, MELBOURNE","j":372130,"m":186065,"r":"REVIEW","s":0.45,"d":"2025-12-03","p":"Lakeview Loan"},
    {"c":"05-2018-CA-050709","a":"4920 BROOKHAVEN ST, COCOA","j":74346,"m":52042,"r":"REVIEW","s":0.65,"d":"2025-12-17","p":"MTGLQ INVEST"},
    {"c":"05-2023-CA-044476","a":"2100 LEEWOOD BLVD, MELBOURNE","j":232556,"m":162789,"r":"REVIEW","s":0.72,"d":"2025-12-17","p":"NATIONSTAR"},
    {"c":"05-2024-CA-051335","a":"1001 ORIOLE CIR, BAREFOOT BAY","j":325000,"m":227500,"r":"REVIEW","s":0.55,"d":"2025-12-17","p":"EVELYN SIMEON"},
    {"c":"05-2025-CA-017191","a":"3625 MIRIAM DR, TITUSVILLE","j":334505,"m":234153,"r":"REVIEW","s":0.68,"d":"2025-12-17","p":"CITIZENS BANK"},
    {"c":"05-2025-CA-024879","a":"661 BRISBANE ST, PALM BAY","j":281528,"m":197070,"r":"REVIEW","s":0.71,"d":"2025-12-17","p":"DATA MORT"},
    {"c":"05-2024-CA-045123","a":"1847 DOOLITTLE LN, TITUSVILLE","j":287500,"m":201250,"r":"REVIEW","s":0.68,"d":"2025-01-07","p":"WELLS FARGO"},
    {"c":"05-2024-CA-024562","a":"8520 HIGHWAY 1, MICCO","j":25550,"m":16250,"r":"SKIP","s":0.003,"d":"2025-12-03","p":"Bank of NY Mellon"},
    {"c":"05-2024-CA-031234","a":"2085 ROBIN HOOD DR, MELBOURNE","j":176240,"m":88120,"r":"SKIP","s":0.003,"d":"2025-12-03","p":"Bank of America"},
    {"c":"05-2024-CA-031697","a":"1160 TIGER ST SE, PALM BAY","j":253150,"m":126575,"r":"SKIP","s":0.003,"d":"2025-12-03","p":"Nationstar"},
    {"c":"05-2025-CC-017102","a":"1404 PARADISE LN, COCOA","j":24520,"m":17164,"r":"SKIP","s":0.42,"d":"2025-12-17","p":"NORTHFIELD"},
]

def log_activity(state, action, detail, icon="📋"):
    state["activities"].append({"action":action,"detail":detail,"icon":icon,"ts":datetime.utcnow().isoformat()})

def query_parser(state):
    q = state["query"].lower()
    intent = {"type":None,"filters":{},"keywords":[]}
    if "bid" in q and any(w in q for w in ["recommend","show","list"]): intent["type"]="filter";intent["filters"]["r"]="BID"
    elif "skip" in q or "avoid" in q: intent["type"]="filter";intent["filters"]["r"]="SKIP"
    elif "review" in q: intent["type"]="filter";intent["filters"]["r"]="REVIEW"
    elif "next auction" in q or "upcoming" in q: intent["type"]="auction"
    elif "best" in q or "opportunit" in q: intent["type"]="best"
    elif "analyz" in q or any(c.isdigit() for c in q): intent["type"]="search";intent["keywords"]=[w for w in state["query"].split() if len(w)>3]
    else: intent["type"]="general"
    if "jan" in q: intent["filters"]["d"]="2025-01-07"
    elif "dec 17" in q: intent["filters"]["d"]="2025-12-17"
    elif "dec 3" in q: intent["filters"]["d"]="2025-12-03"
    state["intent"]=intent
    log_activity(state,"Query Parsed",f"Intent: {intent['type']}","🔍")
    return state

def property_search(state):
    intent=state["intent"];results=FORECLOSURES.copy()
    if intent["type"]=="filter":
        rec=intent["filters"].get("r");results=[p for p in results if p["r"]==rec]
        if "d" in intent["filters"]: results=[p for p in results if p["d"]==intent["filters"]["d"]]
        log_activity(state,"Filtered",f"{len(results)} {rec} properties","📊")
    elif intent["type"]=="auction":
        results=[p for p in results if p["d"]=="2025-01-07"]
        log_activity(state,"Auction Lookup",f"Jan 7 - {len(results)} properties","📅")
    elif intent["type"]=="best":
        results=sorted([p for p in results if p["r"]=="BID" and p["s"]>0.75],key=lambda x:x["s"],reverse=True)
        log_activity(state,"ML Analysis",f"Top {len(results)} properties","🤖")
    elif intent["type"]=="search":
        kw=intent.get("keywords",[]);results=[p for p in results if any(k.lower() in p["a"].lower() or k.lower() in p["c"].lower() for k in kw)]
        log_activity(state,"Search",f"Found {len(results)} matches","🏠")
    state["properties"]=results
    return state

def investment_analysis(state):
    props=state["properties"]
    if not props: state["analysis"]={"total":0,"bid":0,"review":0,"skip":0,"tj":0};return state
    state["analysis"]={"total":len(props),"bid":len([p for p in props if p["r"]=="BID"]),"review":len([p for p in props if p["r"]=="REVIEW"]),"skip":len([p for p in props if p["r"]=="SKIP"]),"tj":sum(p["j"] for p in props),"tm":sum(p["m"] for p in props)}
    log_activity(state,"Analysis",f"Total: ${state['analysis']['tj']:,.0f}","💰")
    return state

def response_generator(state):
    intent=state["intent"];props=state["properties"];an=state["analysis"];resp=""
    if intent["type"]=="filter":
        rec=intent["filters"].get("r","ALL");emoji="🟢" if rec=="BID" else "🟡" if rec=="REVIEW" else "🔴"
        resp=f"## {emoji} {rec} Properties ({an['total']})\n\n**Total Judgment:** ${an['tj']/1e6:.2f}M\n\n"
        for p in props[:5]:
            e="🟢" if p["r"]=="BID" else "🟡" if p["r"]=="REVIEW" else "🔴"
            resp+=f"{e} **{p['a']}**\nJudgment: ${p['j']:,} | Max Bid: ${p['m']:,} | ML: {p['s']*100:.0f}%\n\n"
        if len(props)>5: resp+=f"_...and {len(props)-5} more_"
    elif intent["type"]=="auction":
        resp="## 📅 Next Foreclosure Auction\n\n**Date:** Tuesday, January 7, 2025\n**Time:** 11:00 AM EST\n**Location:** Titusville Courthouse\n\n"
        resp+=f"### Properties ({an['total']})\n🟢 BID: {an['bid']} | 🟡 REVIEW: {an['review']} | 🔴 SKIP: {an['skip']}\n\n**Total Judgment:** ${an['tj']/1e6:.2f}M"
    elif intent["type"]=="best":
        resp="## 💰 Top Investment Opportunities\n\nBased on ML model (64.4% accuracy):\n\n"
        for i,p in enumerate(props[:5],1): resp+=f"**{i}. {p['a']}**\n📊 ML: {p['s']*100:.0f}% | Judgment: ${p['j']:,}\n💵 Max Bid: ${p['m']:,} | Auction: {p['d']}\n\n"
    elif intent["type"]=="search" and props:
        p=props[0];resp=f"## 🏠 {p['a']}\n\n| Field | Value |\n|---|---|\n| Case | {p['c']} |\n| Judgment | ${p['j']:,} |\n| Max Bid | ${p['m']:,} |\n| ML | {p['s']*100:.0f}% |\n| Plaintiff | {p['p']} |\n| Auction | {p['d']} |\n| Rec | **{p['r']}** |"
    else:
        resp="## 🤖 BidDeed.AI Agent\n\nTry:\n- **Show BID recommendations**\n- **Next auction**\n- **Analyze [address]**\n- **Best opportunities**"
    state["response"]=resp;state["completed"]=True
    log_activity(state,"Response Generated",f"{len(resp)} chars","✅")
    return state

def build_graph():
    if not HAS_LANGGRAPH: return None
    wf=StateGraph(AgentState)
    wf.add_node("query_parser",query_parser)
    wf.add_node("property_search",property_search)
    wf.add_node("investment_analysis",investment_analysis)
    wf.add_node("response_generator",response_generator)
    wf.set_entry_point("query_parser")
    wf.add_edge("query_parser","property_search")
    wf.add_edge("property_search","investment_analysis")
    wf.add_edge("investment_analysis","response_generator")
    wf.add_edge("response_generator",END)
    return wf.compile(checkpointer=MemorySaver())

def run_fallback(query,session_id):
    state={"query":query,"session_id":session_id,"intent":{},"properties":[],"analysis":{},"response":"","activities":[],"completed":False}
    state=query_parser(state);state=property_search(state);state=investment_analysis(state);state=response_generator(state)
    return state

async def save_supabase(state):
    if not SUPABASE_KEY: return False
    try:
        async with httpx.AsyncClient() as c:
            r=await c.post(f"{SUPABASE_URL}/rest/v1/insights",headers={"apikey":SUPABASE_KEY,"Authorization":f"Bearer {SUPABASE_KEY}","Content-Type":"application/json","Prefer":"return=minimal"},json={"category":"agent_query","content":json.dumps({"query":state["query"],"intent":state["intent"],"props":len(state["properties"])}),"source":"biddeed-agent"})
            return r.status_code in [200,201]
    except: return False

async def main():
    print("="*60);print("🤖 BidDeed.AI Conversational Agent");print("="*60)
    print(f"Query: {USER_QUERY}\nSession: {SESSION_ID}\n"+"-"*60)
    graph=build_graph()
    if graph:
        print("✓ LangGraph OK")
        result=graph.invoke({"query":USER_QUERY,"session_id":SESSION_ID,"intent":{},"properties":[],"analysis":{},"response":"","activities":[],"completed":False},{"configurable":{"thread_id":SESSION_ID}})
    else:
        print("⚠️ Fallback mode");result=run_fallback(USER_QUERY,SESSION_ID)
    print("\n📋 ACTIVITIES:");[print(f"  {a['icon']} {a['action']}: {a['detail']}") for a in result["activities"]]
    print("\n📝 RESPONSE:\n"+"-"*60+"\n"+result["response"]+"\n"+"-"*60)
    saved=await save_supabase(result);print(f"\n💾 Supabase: {'✓' if saved else '✗'}")
    import os;os.makedirs("output",exist_ok=True)
    with open("output/result.json","w") as f: json.dump({"query":result["query"],"intent":result["intent"],"props":len(result["properties"]),"response":result["response"][:500],"activities":result["activities"]},f,indent=2)
    print("✅ Done")
    return result

if __name__=="__main__": asyncio.run(main())
