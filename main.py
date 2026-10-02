import os
from typing import TypedDict, Annotated
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from tools import retail_analyzer

load_dotenv()

# --- STEP 1: Define the shared State ---
class AgentState(TypedDict):
    analysis_data: dict
    report: str
    sentence_count: int
    iterations: int  # Add this

# Initialize LLM
llm = ChatGroq(temperature=0, model_name="llama-3.3-70b-versatile")

# --- STEP 2: Define the Nodes ---
def analyze_data_node(state: AgentState):
    print("--- NODE: ANALYZING DATA ---")
    data = retail_analyzer("test_data.csv")
    return {"analysis_data": data}

def write_report_node(state: AgentState):
    print(f"--- NODE: WRITING REPORT (Attempt {state.get('iterations', 0) + 1}) ---")
    data = state['analysis_data']
    prompt = f"Format this data into Q1-Q5. Q5 MUST be exactly 3 sentences. No extra text: {data}"
    response = llm.invoke(prompt)
    return {"report": response.content, "iterations": state.get('iterations', 0) + 1}

def validate_node(state: AgentState):
    print("--- NODE: VALIDATING ---")
    # Count sentences in Q5 (basic logic for example)
    q5_part = state['report'].split("Q5:")[-1]
    count = q5_part.count(".") 
    return {"sentence_count": count}

# --- STEP 3: Define Conditional Logic ---
def should_continue(state: AgentState):
    if state['sentence_count'] == 3 or state.get('iterations', 0) >= 3:
        return "perfect"
    else:
        return "retry"

# --- STEP 4: Build the Graph ---
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("analyzer", analyze_data_node)
workflow.add_node("writer", write_report_node)
workflow.add_node("validator", validate_node)

# Set Flow
workflow.set_entry_point("analyzer")
workflow.add_edge("analyzer", "writer")
workflow.add_edge("writer", "validator")

# Add Conditional Edge (Reflection Loop)
workflow.add_conditional_edges(
    "validator",
    should_continue,
    {
        "perfect": END,
        "retry": "writer"
    }
)

# Compile
app = workflow.compile()

# --- STEP 5: Run ---
if __name__ == "__main__":
    final_state = app.invoke({"analysis_data": {}, "report": "", "sentence_count": 0})
    with open("Agent47.txt", "w") as f:
        f.write(final_state['report'])
    print("\n--- MISSION ACCOMPLISHED ---")