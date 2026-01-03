import shutil
import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from backend.graph import app as workflow_app
from backend.state import GraphState

# Initialize FastAPI
app = FastAPI(title="FinDoc AI API", version="1.0")

@app.get("/")
def home():
    return {"message": "FinDoc AI Risk Engine is Running 🚀"}

@app.post("/analyze")
async def analyze_document(file: UploadFile = File(...)):
    """
    Endpoint to upload a PDF and get a Risk Analysis.
    """
    # 1. Save the uploaded file temporarily
    temp_filename = f"temp_{file.filename}"
    try:
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        print(f"📥 Received file: {temp_filename}")

        # 2. Run the LangGraph Workflow
        # We pass the file path to the graph
        final_state = workflow_app.invoke({"file_path": temp_filename})

        # 3. Clean up (Delete temp file)
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

        # 4. Return Structured JSON
        return {
            "applicant_name": final_state["metrics"].applicant_name if final_state.get("metrics") else None,
            "risk_score": final_state.get("risk_score"),
            "approval_status": final_state.get("approval_status"),
            "monthly_salary": final_state["metrics"].monthly_salary if final_state.get("metrics") else 0,
            "total_emis": final_state["metrics"].total_emis if final_state.get("metrics") else 0,
            "reasoning": final_state.get("reasoning", [])
        }

    except Exception as e:
        # Cleanup on error
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)