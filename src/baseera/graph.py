from langgraph.graph import StateGraph, START, END
from langgraph.constants import Send
from langgraph.checkpoint.memory import MemorySaver

from src.baseera.state import BaseeraState, ResearchState
from src.baseera.nodes import (
    planner_node, researcher_node, domain_fact_checker_node,
    cross_domain_synthesizer_node, plan_review_node, report_writer_node
)

# 1. Build Subgraph
subgraph_builder = StateGraph(ResearchState)
subgraph_builder.add_node("research_extraction", researcher_node)
subgraph_builder.add_node("fact_checking", domain_fact_checker_node)
subgraph_builder.add_edge(START, "research_extraction")
subgraph_builder.add_edge("research_extraction", "fact_checking")
subgraph_builder.add_edge("fact_checking", END)
domain_subgraph = subgraph_builder.compile()

# 2. Wrapper & Router
def domain_wrapper_node(state: dict):
    result = domain_subgraph.invoke(state)
    return {"all_verified_claims": result.get("domain_verified_claims", [])}

def route_to_subgraphs(state: BaseeraState):
    plan = state.get("research_plan", {})
    return [
        Send("domain_wrapper_node", {
            "topic": domain, 
            "search_queries": queries,
            "raw_docs": [],
            "extracted_claims": [],
            "domain_verified_claims": []
        })
        for domain, queries in plan.items()
    ]

# 3. Build Global Graph
memory = MemorySaver()
builder = StateGraph(BaseeraState)

builder.add_node("planner_node", planner_node)
builder.add_node("plan_review_node", plan_review_node)
builder.add_node("domain_wrapper_node", domain_wrapper_node)
builder.add_node("synthesizer_node", cross_domain_synthesizer_node)
builder.add_node("report_writer_node", report_writer_node)

builder.add_edge(START, "planner_node")
builder.add_edge("planner_node", "plan_review_node")
builder.add_conditional_edges("plan_review_node", route_to_subgraphs, ["domain_wrapper_node"])
builder.add_edge("domain_wrapper_node", "synthesizer_node")
builder.add_edge("synthesizer_node", "report_writer_node")
builder.add_edge("report_writer_node", END)

baseera_app = builder.compile(checkpointer=memory)