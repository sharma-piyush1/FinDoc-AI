import streamlit as st
import requests

# CONSTANTS
API_URL = "http://127.0.0.1:8000/analyze"

st.set_page_config(page_title="FinDoc AI", page_icon="🏦")

st.title("🏦 FinDoc AI: Intelligent Loan Underwriter")
st.markdown("### Architecture: Streamlit (Client) ↔ HTTP Request ↔ FastAPI (Server)")

uploaded_file = st.file_uploader("Upload Bank Statement (PDF)", type=["pdf"])

if uploaded_file:
    st.success(f"File Ready: {uploaded_file.name}")
    
    if st.button("Analyze Risk via API"):
        with st.spinner("🚀 Sending document to FastAPI Backend..."):
            try:
                # 1. Prepare the file payload for the API request
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                
                # 2. Make the POST request
                response = requests.post(API_URL, files=files)
                
                # 3. Handle Response
                if response.status_code == 200:
                    data = response.json()
                    
                    st.divider()
                    
                    # Display Metrics
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Risk Score", f"{data['risk_score']}/100")
                    col2.metric("Monthly Salary", f"₹{data['monthly_salary']:,.2f}")
                    col3.metric("Total EMIs", f"₹{data['total_emis']:,.2f}")
                    
                    # Verdict Banner
                    status = data['approval_status']
                    if status == "APPROVED":
                        st.success(f"✅ VERDICT: {status}")
                    elif status == "REJECTED":
                        st.error(f"❌ VERDICT: {status}")
                    else:
                        st.warning(f"⚠️ VERDICT: {status}")
                    
                    # Reasoning
                    st.subheader("📝 Reasoning")
                    for reason in data['reasoning']:
                        st.write(f"- {reason}")
                        
                    with st.expander("See Raw API Response"):
                        st.json(data)
                        
                else:
                    st.error(f"❌ API Error: {response.text}")
                    
            except Exception as e:
                st.error(f"❌ Connection Failed: {e}. Is the backend running?")