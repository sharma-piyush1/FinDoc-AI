import os
from backend.graph import app
from backend.state import ApprovalStatus

# 1. Setup the file path (ensure this matches the dummy PDF you just created)
pdf_path = "sample_bank_statement.pdf"

if not os.path.exists(pdf_path):
    print(f"Error: File '{pdf_path}' not found. Run generate_dummy_pdf.py first!")
    exit()

print(f"🚀 Starting FinDoc AI Pipeline for: {pdf_path}...")

try:
    # 2. Invoke the Graph
    # The dictionary key "file_path" matches the GraphState schema input
    final_state = app.invoke({"file_path": pdf_path})

    # 3. Print the Final Report
    print("\n" + "="*40)
    print("      📊 FINDOC AI RISK REPORT      ")
    print("="*40)
    
    # Extract details safely
    metrics = final_state.get("metrics")
    
    print(f"📝 Applicant:    {metrics.applicant_name if metrics else 'Unknown'}")
    print(f"💰 Monthly Salary: Rs. {metrics.monthly_salary:,.2f}" if metrics else "💰 Monthly Salary: N/A")
    print(f"📉 Total EMIs:     Rs. {metrics.total_emis:,.2f}" if metrics else "📉 Total EMIs:     N/A")
    print("-" * 40)
    print(f"🎯 Risk Score:     {final_state.get('risk_score')}/100")
    print(f"✅ Verdict:        {final_state.get('approval_status')}")
    print("-" * 40)
    
    print("🔍 Analysis Reasons:")
    for reason in final_state.get("reasoning", []):
        print(f" - {reason}")

except Exception as e:
    print(f"\nGraph Execution Failed: {e}")