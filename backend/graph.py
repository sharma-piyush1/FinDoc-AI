from langgraph.graph import StateGraph, END
from backend.state import GraphState, ApprovalStatus
from backend.chains import get_extraction_chain
from backend.risk_engine import calculate_risk
from backend.tools import parse_pdf

# --- NODES (The Steps) ---

def ingest_node(state: GraphState):
    """Step 1: Read the PDF file."""
    print(f"--- INGEST NODE: Processing {state.file_path} ---")
    
    # Use LlamaParse to get text
    text = parse_pdf(state.file_path)
    
    if not text:
        return {
            "extraction_errors": ["OCR Failed: Could not read document."],
            "confidence_score": 0.0
        }
        
    return {"document_text": text}

def extract_node(state: GraphState):
    """Step 2: Extract structured data using Gemini."""
    print("--- EXTRACT NODE: Identifying Financial Metrics ---")
    
    chain = get_extraction_chain()
    try:
        # Invoke the LLM chain with the text from the previous step
        metrics = chain.invoke({"text": state.document_text})
        
        # Simple Confidence Logic: 
        # If salary was found, we are reasonably confident. If 0, something is wrong.
        confidence = 1.0 if metrics.monthly_salary > 0 else 0.4
        
        return {
            "metrics": metrics,
            "confidence_score": confidence
        }
    except Exception as e:
        return {
            "extraction_errors": [f"LLM Extraction Failed: {str(e)}"],
            "confidence_score": 0.0
        }

def risk_node(state: GraphState):
    """Step 3: Run the Deterministic Rules."""
    print("--- RISK NODE: Calculating Score ---")
    # This function is pure Python (from backend/risk_engine.py)
    updated_state = calculate_risk(state)
    
    # We return the updates to the state
    return {
        "risk_score": updated_state.risk_score,
        "approval_status": updated_state.approval_status,
        "reasoning": updated_state.reasoning
    }

# --- EDGES (The Logic) ---

def decide_next_step(state: GraphState):
    """Conditional Logic: Where do we go after extraction?"""
    
    # If confidence is low (e.g., No Salary Found), skip Risk Engine
    if state.confidence_score < 0.5:
        print("⚠️ Low Confidence -> Routing to HUMAN REVIEW")
        return "human_review"
    
    # Otherwise, proceed to Risk Engine
    return "risk_engine"

def human_review_node(state: GraphState):
    """Placeholder for Human Review state."""
    return {
        "approval_status": ApprovalStatus.HUMAN_REVIEW,
        "reasoning": ["Automated extraction failed or confidence low. Manual check required."]
    }

# --- GRAPH CONSTRUCTION ---

workflow = StateGraph(GraphState)

# 1. Add Nodes
workflow.add_node("ingest", ingest_node)
workflow.add_node("extract", extract_node)
workflow.add_node("risk_engine", risk_node)
workflow.add_node("human_review", human_review_node)

# 2. Set Entry Point
workflow.set_entry_point("ingest")

# 3. Add Edges
workflow.add_edge("ingest", "extract")

# 4. Conditional Edge from Extract
workflow.add_conditional_edges(
    "extract",
    decide_next_step,
    {
        "risk_engine": "risk_engine",
        "human_review": "human_review"
    }
)

# 5. End points
workflow.add_edge("risk_engine", END)
workflow.add_edge("human_review", END)

# 6. Compile
app = workflow.compile()