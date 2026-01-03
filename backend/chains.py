import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from backend.state import FinancialMetrics

load_dotenv()

# --- 1. Initialize the Model ---
# We use gemini-flash-latest as it's the best balance of speed/cost/intelligence
llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0  # Deterministic: We want facts, not creativity
)

# --- 2. Define the Extractor Chain ---
def get_extraction_chain():
    """
    Creates a specialized chain that forces Gemini to output 
    structured financial data (JSON) matching our Pydantic schema.
    """
    
    # The Prompt: strictly instructs the AI on how to handle the data
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert Financial Data Analyst. Your task is to extract specific financial metrics from raw OCR text of Bank Statements or Income Tax Returns."),
        ("human", """
        Analyze the following document text carefully. 
        
        EXTRACT THESE 3 METRICS ONLY:
        1. Monthly Salary: Look for recurring 'Credit' transactions labeled 'Salary', 'Stipend', 'NEFT', or similar corporate transfers. If multiple exist, take the average.
        2. Total EMIs: Look for recurring 'Debit' transactions labeled 'EMI', 'Loan', 'Finance', 'Bajaj', 'HDFC', etc. Sum them up to get a total monthly obligation.
        3. Closing Balance: Look for the final/latest balance mentioned at the end of the statement.

        If a value is not explicitly found, set it to 0. Do not guess.
        
        DOCUMENT TEXT:
        {text}
        """)
    ])

    # The Magic: Binding the Pydantic Schema to the Model
    # This forces the output to be a valid 'FinancialMetrics' object
    structured_llm = llm.with_structured_output(FinancialMetrics)
    
    # Create the chain: Prompt -> Model -> Structured Output
    chain = prompt | structured_llm
    
    return chain