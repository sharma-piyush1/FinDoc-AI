from backend.state import GraphState, ApprovalStatus

def calculate_risk(state: GraphState) -> GraphState:
    """
    The Decision Node: Applies deterministic banking rules to the extracted metrics.
    
    Input: GraphState with 'metrics' populated.
    Output: GraphState with 'risk_score', 'approval_status', and 'reasoning' filled.
    """
    
    # 1. Safety Check: If metrics are missing, we cannot calculate risk
    if not state.metrics:
        state.extraction_errors.append("Risk Engine Failed: No metrics found.")
        state.approval_status = ApprovalStatus.HUMAN_REVIEW
        return state

    metrics = state.metrics
    reasons = []
    score = 100  # Start with a perfect score
    
    # --- RULE 1: Debt-to-Income Ratio (DTI) ---
    # Banks usually reject if EMIs are > 40-50% of salary
    dti_ratio = 0.0
    if metrics.monthly_salary > 0:
        dti_ratio = metrics.total_emis / metrics.monthly_salary
    
    if dti_ratio > 0.50:
        penalty = 40
        score -= penalty
        reasons.append(f"CRITICAL: High DTI Ratio ({dti_ratio:.1%}). EMIs exceed 50% of income.")
    elif dti_ratio > 0.30:
        penalty = 20
        score -= penalty
        reasons.append(f"WARNING: Moderate DTI Ratio ({dti_ratio:.1%}).")

    # --- RULE 2: Minimum Income Threshold ---
    # Example: Salary must be at least 25k
    if metrics.monthly_salary < 25000:
        penalty = 50 # Huge penalty
        score -= penalty
        reasons.append(f"CRITICAL: Low Income. Salary {metrics.monthly_salary} is below 25k threshold.")

    # --- RULE 3: Negative Balance Check ---
    if metrics.closing_balance < 0:
        score = 0 # Instant fail
        reasons.append("CRITICAL: Negative Closing Balance detected in statement.")

    # --- Final Score Clamping (Keep between 0-100) ---
    final_score = max(0, min(100, score))
    state.risk_score = final_score
    state.reasoning = reasons

    # --- Final Verdict Logic ---
    if final_score >= 75:
        state.approval_status = ApprovalStatus.APPROVED
    elif final_score < 50:
        state.approval_status = ApprovalStatus.REJECTED
    else:
        # Between 50-75 is a "Grey Area" requiring human eyes
        state.approval_status = ApprovalStatus.HUMAN_REVIEW
        reasons.append("Score is in the grey zone (50-75). Human review required.")

    return state