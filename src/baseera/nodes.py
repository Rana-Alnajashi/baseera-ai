import json
from typing import Dict, List, Literal
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from langgraph.types import interrupt

from src.baseera.state import BaseeraState, ResearchState
from src.baseera.tools import baseera_tools, tavily_search

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
llm_with_tools = llm.bind_tools(baseera_tools)


# --- Pydantic Schemas ---
class ResearchDomain(BaseModel):
    domain: str
    queries: List[str]

class ResearchPlan(BaseModel):
     framework_used: str
     plan: List[ResearchDomain]

class ClaimExtraction(BaseModel):
    claim_id: str
    claim: str
    evidence: str
    source: str

class ExtractedClaimsList(BaseModel):
    claims: List[ClaimExtraction]

class VerifiedClaimOutput(BaseModel):
    claim_id: str
    verification_status: Literal["Verified", "Unverified", "Contradicted"]
    reasoning: str

class VerificationBatch(BaseModel):
    verifications: List[VerifiedClaimOutput]

class ExecutiveSynthesis(BaseModel):
    synthesis: str

# --- Nodes ---
def planner_node(state: BaseeraState) -> Dict:
    company = state.get("company_name", "")
    goal = state.get("research_goal", "")
    prompt = (
        f"Client: {company}. Goal: {goal}. Act as a Bain & Company Engagement Manager. "
        "Select the most relevant foundational logic (e.g., Profitability Framework, Market Entry, Profit from the Core, Elements of Value). "
        "Use hypothesis-driven problem solving to build a custom, MECE-compliant issue tree. "
        "Break this problem into 3-4 distinct research domains, and write 2-3 targeted OSINT search queries per domain."
    )
    result = llm.with_structured_output(ResearchPlan).invoke(prompt)
    return {
        "consulting_framework": result.framework_used,
        "research_plan": {item.domain: item.queries for item in result.plan}
    }


def plan_review_node(state: BaseeraState) -> Dict:
    # Pauses the graph and sends the payload to the frontend
    feedback = interrupt({
        "framework": state.get("consulting_framework"),
        "plan": state.get("research_plan")
    })

    if isinstance(feedback, dict) and "edited_plan" in feedback:
        return {"research_plan": feedback["edited_plan"], "plan_feedback": "Plan approved and edited by analyst."}
    return {"plan_feedback": "Plan approved without edits."}


def researcher_node(state: ResearchState) -> Dict:
    topic = state.get("topic", "")
    queries = state.get("search_queries", [])
    
    raw_data_compiled = []
    for q in queries:
        tool_result = tavily_search.invoke({"query": q})
        raw_data_compiled.append({"query": q, "content": tool_result})
        
    context_str = "\n".join([f"Query: {r['query']}\nResult: {r['content'][:1500]}" for r in raw_data_compiled])
    prompt = f"Domain: '{topic}'. Extract 2 to 4 major factual claims from this data:\n{context_str}"
    
    result = llm.with_structured_output(ExtractedClaimsList).invoke(prompt)
    formatted_claims = [{"claim_id": c.claim_id, "claim": c.claim, "evidence": c.evidence, "source": c.source} for c in result.claims]
    
    return {"raw_docs": raw_data_compiled, "extracted_claims": formatted_claims}

def domain_fact_checker_node(state: ResearchState) -> Dict:
    topic = state.get("topic", "")
    claims = state.get("extracted_claims", [])
    
    prompt = f"Domain: '{topic}'. Verify claims based on evidence. Mark tool errors as Unverified.\n{json.dumps(claims, indent=2)}"
    result = llm.with_structured_output(VerificationBatch).invoke(prompt)
    
    claims_by_id = {c["claim_id"]: c for c in claims}
    verified_records = []
    for v in result.verifications:
        if v.claim_id in claims_by_id:
            verified_records.append({
                "domain": topic,
                "claim_data": claims_by_id[v.claim_id],
                "verification_status": v.verification_status,
                "reasoning": v.reasoning
            })
            
    return {"domain_verified_claims": verified_records}

def cross_domain_synthesizer_node(state: BaseeraState) -> Dict:
    valid_claims = [c for c in state.get("all_verified_claims", []) if c["verification_status"] == "Verified"]
    if not valid_claims:
        return {"cross_domain_analysis": "No verified claims were found to synthesize."}
        
    prompt = f"Goal: {state.get('research_goal')}. Write a strategic executive synthesis based on these facts:\n{json.dumps(valid_claims, indent=2)}"
    result = llm.with_structured_output(ExecutiveSynthesis).invoke(prompt)
    return {"cross_domain_analysis": result.synthesis}


def report_writer_node(state: BaseeraState) -> dict:
    prompt = (
        f"Company: {state.get('company_name')}\n"
        f"Synthesis: {state.get('cross_domain_analysis')}\n"
        "Write a highly professional Final Due Diligence Report. "
        "You MUST include one relevant, quantitative bar chart to visualize key financial or market data from the synthesis. "
        "Use the QuickChart API to generate the chart by embedding a Markdown image link. "
        "CRITICAL URL RULES: The QuickChart URL MUST NOT contain any spaces, line breaks, double quotes, or parentheses (). "
        "You MUST use underscores instead of spaces for dataset labels, and abbreviate without parentheses (e.g., use 'Market_Size_Billion_USD' instead of 'Market Size (Billion USD)'). "
        "Example EXACT format: ![Chart Title](https://quickchart.io/chart?c={type:'bar',data:{labels:['2023','2024'],datasets:[{label:'Market_Size_USD',data:[10,20]}]}}&w=600&h=350&bkg=white) "
        "Structure the rest of the report with standard consulting headers: Executive Summary, Market Trends, Competitive Landscape, and Strategic Recommendations. "
        "Do NOT use the RAPID framework and do NOT use Mermaid.js."
    )
    result = llm.invoke(prompt)
    return {"final_report": result.content}