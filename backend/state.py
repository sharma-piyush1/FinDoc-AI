from typing import List, Optional, TypedDict
from pydantic import BaseModel, Field
from enum import Enum

# --- 1. Enums for Strict Classification ---
class DocumentType(str, Enum):
    BANK_STATEMENT = "bank_statement"
    ITR = "itr"
    SALARY_SLIP = "salary_slip"
    UNKNOWN = "unknown"

class ApprovalStatus(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    PENDING = "PENDING"

# --- 2. The Data Payload (What we extract) ---
class FinancialMetrics(BaseModel):
    monthly_salary: float = Field(
        ..., 
        description="The detected monthly income extracted from credit transactions."
    )
    total_emis: float = Field(
        0.0, 
        description="Sum of all detected loan EMI debits."
    )
    closing_balance: float = Field(
        ..., 
        description="The final closing balance detected in the statement."
    )
    applicant_name: Optional[str] = Field(
        None, 
        description="Name of the account holder."
    )

# --- 3. The Graph State (Passed between Nodes) ---
class GraphState(BaseModel):
    """
    Represents the memory of the entire workflow.
    LangGraph nodes will read from and write to this object.
    """
    # Inputs
    file_path: str
    document_text: Optional[str] = None
    
    # Classification & Extraction
    document_type: DocumentType = DocumentType.UNKNOWN
    metrics: Optional[FinancialMetrics] = None
    
    # Audit & Control
    confidence_score: float = Field(0.0, ge=0.0, le=1.0, description="Confidence score 0-1")
    extraction_errors: List[str] = Field(default_factory=list)
    
    # Decision Engine Output
    risk_score: int = Field(0, ge=0, le=100, description="Calculated Risk Score 0-100")
    approval_status: ApprovalStatus = ApprovalStatus.PENDING
    reasoning: List[str] = Field(default_factory=list, description="List of reasons for the decision")