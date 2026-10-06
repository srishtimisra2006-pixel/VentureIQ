def build_pitch_intelligence_output(
    pitch_result,
    consistency_summary=None,
    investment_assessment=None,
):
    """
    Build the final standardized VentureIQ
    Pitch Intelligence output for the frontend/API.
    """

    if consistency_summary is None:
        consistency_summary = {}

    if investment_assessment is None:
        investment_assessment = {}

    return {
        "module": "Pitch Deck Intelligence",

        "pitch_analysis": {
            "pitch_score": pitch_result.get(
                "pitch_score"
            ),
            "evidence_confidence": pitch_result.get(
                "evidence_confidence"
            ),
            "criteria": pitch_result.get(
                "criteria",
                {}
            ),
            "strengths": pitch_result.get(
                "strengths",
                []
            ),
            "risks": pitch_result.get(
                "risks",
                []
            ),
            "due_diligence_actions": pitch_result.get(
                "due_diligence_actions",
                []
            ),
        },

        "deck_data_consistency": {
            "consistency_score": consistency_summary.get(
                "consistency_score"
            ),
            "match_count": consistency_summary.get(
                "match_count",
                0
            ),
            "mismatch_count": consistency_summary.get(
                "mismatch_count",
                0
            ),
            "not_available_count": consistency_summary.get(
                "not_available_count",
                0
            ),
            "total_fields_checked": consistency_summary.get(
                "total_fields_checked",
                0
            ),
        },

        "investment_assessment": {
            "investment_score": investment_assessment.get(
                "investment_score"
            ),
            "investment_category": investment_assessment.get(
                "investment_category"
            ),
            "pitch_score": investment_assessment.get(
                "pitch_score"
            ),
            "consistency_score": investment_assessment.get(
                "consistency_score"
            ),
            "risk_score": investment_assessment.get(
                "risk_score"
            ),
            "completeness": investment_assessment.get(
                "completeness"
            ),
            "strengths": investment_assessment.get(
                "strengths",
                []
            ),
            "risks": investment_assessment.get(
                "risks",
                []
            ),
            "due_diligence_actions": investment_assessment.get(
                "due_diligence_actions",
                []
            ),
        },
    }


def validate_pitch_intelligence_output(output):
    """
    Validate the final Pitch Intelligence structure.
    """

    required_sections = [
        "module",
        "pitch_analysis",
        "deck_data_consistency",
        "investment_assessment",
    ]

    for section in required_sections:

        if section not in output:
            raise ValueError(
                f"Missing required output section: {section}"
            )

    required_pitch_fields = [
        "pitch_score",
        "evidence_confidence",
        "criteria",
    ]

    for field in required_pitch_fields:

        if field not in output["pitch_analysis"]:
            raise ValueError(
                f"Missing pitch analysis field: {field}"
            )

    required_consistency_fields = [
        "consistency_score",
        "match_count",
        "mismatch_count",
        "not_available_count",
    ]

    for field in required_consistency_fields:

        if field not in output["deck_data_consistency"]:
            raise ValueError(
                f"Missing consistency field: {field}"
            )

    required_investment_fields = [
        "investment_score",
        "investment_category",
        "pitch_score",
        "consistency_score",
        "risk_score",
    ]

    for field in required_investment_fields:

        if field not in output["investment_assessment"]:
            raise ValueError(
                f"Missing investment assessment field: {field}"
            )

    return True