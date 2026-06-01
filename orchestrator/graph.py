from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Any
from agents.inspector import inspector_node
from agents.test_engineer import test_engineer_node
from agents.debugger import debugger_node
from agents.reviewer import reviewer_node

class CrewState(TypedDict):
    project_root: str
    user_query: str
    findings: List[Dict]
    confirmed_findings: List[Dict]
    test_outputs: List[Dict]
    patches: List[Dict]
    final_report: str

def build_graph(enable_fixer: bool = False):
    builder = StateGraph(CrewState)
    builder.add_node("inspector", inspector_node)
    builder.add_node("test_engineer", test_engineer_node)
    
    builder.set_entry_point("inspector")
    builder.add_edge("inspector", "test_engineer")
    
    if enable_fixer:
        builder.add_node("debugger", debugger_node)
        builder.add_node("reviewer", reviewer_node)
        builder.add_edge("test_engineer", "debugger")
        builder.add_edge("debugger", "reviewer")
        builder.add_edge("reviewer", END)
    else:
        builder.add_edge("test_engineer", END)
    
    return builder.compile()

def run_crewcode(project_root: str = ".", user_query: str = "", enable_fixer: bool = False):
    graph = build_graph(enable_fixer=enable_fixer)
    initial = {
        "project_root": project_root,
        "user_query": user_query,
        "findings": [],
        "confirmed_findings": [],
        "test_outputs": [],
        "patches": [],
        "final_report": ""
    }
    final = graph.invoke(initial)
    return final