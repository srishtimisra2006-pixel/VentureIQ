PITCH_CRITERIA = [
    "Problem",
    "Solution",
    "Market",
    "Business_Model",
    "Traction",
    "Competition",
    "Product_Technology",
    "Team",
    "Financials",
    "Fundraising",
    "Scalability",
]


def create_pitch_result():
    """
    Create the standard structure for VentureIQ
    pitch-deck analysis output.
    """

    criteria = {}

    for criterion in PITCH_CRITERIA:
        criteria[criterion] = {
            "score": None,
            "evidence": [],
            "missing_information": [],
            "risks": [],
            "confidence": None,
            "evidence_status": None,
        }

    return {
        "pitch_score": None,
        "criteria": criteria,
        "strengths": [],
        "risks": [],
        "due_diligence_actions": [],
        "evidence_confidence": None,
    }


def validate_pitch_result(result):
    """
    Validate the structure of a pitch analysis result.
    """

    required_keys = [
        "pitch_score",
        "criteria",
        "strengths",
        "risks",
        "due_diligence_actions",
        "evidence_confidence",
    ]

    for key in required_keys:
        if key not in result:
            raise ValueError(
                f"Missing required pitch result field: {key}"
            )

    for criterion in PITCH_CRITERIA:
        if criterion not in result["criteria"]:
            raise ValueError(
                f"Missing pitch criterion: {criterion}"
            )

    return True