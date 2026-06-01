import json
from config.settings import get_model_config
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from tools.test_runner import run_pytest

def generate_test(finding: dict, project_root: str) -> str:
    """Use LLM to write a pytest that reproduces the bug."""
    provider, model = get_model_config("test_engineer")
    if provider == "ollama":
        llm = ChatOllama(model=model, temperature=0.2)
    elif provider == "groq":
        llm = ChatGroq(model=model, temperature=0.2)
    else:
        llm = ChatOllama(model=model, temperature=0.2)
    
    prompt = f"""You are a test engineer. Write a pytest function that triggers the following bug.

File: {finding['file']}
Line: {finding['line']}
Type: {finding['type']}

The test should fail exactly because of this bug. Use assertions and any necessary imports.
Output ONLY the Python test code, no explanations.
"""
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content

def test_engineer_node(state: dict) -> dict:
    findings = state.get("findings", [])
    if not findings:
        return {"confirmed_findings": [], "test_outputs": []}
    
    confirmed = []
    outputs = []
    for f in findings[:3]:   # limit to 3 per run
        test_code = generate_test(f, state["project_root"])
        result = run_pytest(test_code, state["project_root"])
        outputs.append({"file": f["file"], "test_output": result["output"]})
        if not result["passed"]:   # test failed as expected -> bug confirmed
            confirmed.append(f)
    return {"confirmed_findings": confirmed, "test_outputs": outputs}