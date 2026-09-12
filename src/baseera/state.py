import operator
from typing import TypedDict, Annotated, List, Dict, Any, Literal
from pydantic import BaseModel, Field

class Claim(TypedDict):
    claim_id: str
    claim: str
    evidence: str
    source: str

class VerifiedClaim(TypedDict):
    domain: str 
    claim_data: Claim
    verification_status: Literal["Verified", "Unverified", "Contradicted"]
    reasoning: str 

class ResearchState(TypedDict):
    topic: str
    search_queries: List[str]
    raw_docs: Annotated[List[Dict[str, Any]], operator.add] 
    extracted_claims: Annotated[List[Claim], operator.add] 
    domain_verified_claims: Annotated[List[VerifiedClaim], operator.add]

class BaseeraState(TypedDict):
    company_name: str
    research_goal: str
    consulting_framework: str 
    research_plan: Dict[str, List[str]] 
    plan_feedback: str 
    all_verified_claims: Annotated[List[VerifiedClaim], operator.add]
    cross_domain_analysis: str
    final_report: str