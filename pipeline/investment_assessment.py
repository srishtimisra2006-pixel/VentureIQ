from typing import Optional


def _safe_number(value, default=0):
    """
    Safely convert a value to a number.
    """

    try:
        if value is None:
            return default

        return float(value)

    except (TypeError, ValueError):
        return default


def calculate_investment_score(
    pitch_score: Optional[float],
    consistency_score: Optional[float],
    risk_score: Optional[float],
):
    """
    Calculate the combined VentureIQ Investment Score.

    Weighting:
        Pitch Attractiveness = 50%
        Deck–Data Consistency = 25%
        Risk Adjustment = 25%
    """

    available_scores = []
    available_weights = []

    if pitch_score is not None:
        available_scores.append(
            _safe_number(pitch_score)
        )
        available_weights.append(50)

    if consistency_score is not None:
        available_scores.append(
            _safe_number(consistency_score)
        )
        available_weights.append(25)

    if risk_score is not None:
        risk_adjusted_score = max(
            0,
            100 - _safe_number(risk_score)
        )

        available_scores.append(
            risk_adjusted_score
        )
        available_weights.append(25)

    if not available_scores:
        return None

    weighted_total = sum(
        score * weight
        for score, weight in zip(
            available_scores,
            available_weights,
        )
    )

    total_weight = sum(
        available_weights
    )

    return round(
        weighted_total / total_weight,
        2,
    )


def classify_investment(
    investment_score,
    risk_score=None,
    completeness=None,
):
    """
    Assign the final VentureIQ investment category.
    """

    if investment_score is None:
        return "Further Due Diligence"

    investment_score = _safe_number(
        investment_score
    )

    risk_score = (
        None
        if risk_score is None
        else _safe_number(risk_score)
    )

    completeness = (
        None
        if completeness is None
        else _safe_number(completeness)
    )

    # High Risk takes priority.
    if risk_score is not None and risk_score >= 60:
        return "High Risk"

    # Strong opportunity with acceptable risk.
    if (
        investment_score >= 70
        and (
            risk_score is None
            or risk_score < 35
        )
        and (
            completeness is None
            or completeness >= 60
        )
    ):
        return "High Priority"

    # Strong enough to investigate further.
    if investment_score >= 60:
        return "Further Due Diligence"

    return "Watchlist"


def generate_investment_assessment(
    pitch_result,
    consistency_summary=None,
    risk_score=None,
    completeness=None,
):
    """
    Generate the final investor-facing VentureIQ
    investment assessment.
    """

    pitch_score = pitch_result.get(
        "pitch_score"
    )

    consistency_score = None

    if consistency_summary:
        consistency_score = consistency_summary.get(
            "consistency_score"
        )

    investment_score = calculate_investment_score(
        pitch_score=pitch_score,
        consistency_score=consistency_score,
        risk_score=risk_score,
    )

    category = classify_investment(
        investment_score=investment_score,
        risk_score=risk_score,
        completeness=completeness,
    )

    strengths = list(
        pitch_result.get(
            "strengths",
            []
        )
    )

    risks = list(
        pitch_result.get(
            "risks",
            []
        )
    )

    due_diligence_actions = list(
        pitch_result.get(
            "due_diligence_actions",
            []
        )
    )

    # Add consistency-related risks.
    if consistency_summary:

        mismatch_count = consistency_summary.get(
            "mismatch_count",
            0,
        )

        if mismatch_count > 0:
            risks.append(
                f"{mismatch_count} pitch-to-dataset "
                "claim(s) show material mismatch."
            )

            due_diligence_actions.append(
                "Verify the mismatched financial and "
                "operational claims against source records."
            )

    # Add general risk-related due diligence.
    if risk_score is not None and risk_score >= 60:

        due_diligence_actions.append(
            "Conduct detailed risk and financial due diligence "
            "before considering investment."
        )

    if completeness is not None and completeness < 60:

        due_diligence_actions.append(
            "Request additional startup information "
            "to improve data completeness."
        )

    # Remove duplicates.
    strengths = list(
        dict.fromkeys(strengths)
    )

    risks = list(
        dict.fromkeys(risks)
    )

    due_diligence_actions = list(
        dict.fromkeys(
            due_diligence_actions
        )
    )

    return {
        "investment_score": investment_score,
        "investment_category": category,
        "pitch_score": pitch_score,
        "consistency_score": consistency_score,
        "risk_score": risk_score,
        "completeness": completeness,
        "strengths": strengths,
        "risks": risks,
        "due_diligence_actions": due_diligence_actions,
    }