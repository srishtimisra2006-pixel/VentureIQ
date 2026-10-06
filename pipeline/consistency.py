import re
import math
import pandas as pd


CONSISTENCY_FIELDS = {
    "Revenue": {
        "dataset_columns": [
            "Revenue",
            "Monthly_Sales",
        ],
        "keywords": [
            "revenue",
            "sales",
            "turnover",
        ],
    },
    "Customers": {
        "dataset_columns": [
            "Customers",
        ],
        "keywords": [
            "customers",
            "customer",
            "users",
            "users",
        ],
    },
    "Revenue_Growth": {
        "dataset_columns": [
            "Revenue_Growth",
        ],
        "keywords": [
            "revenue growth",
            "growth",
            "grew",
            "grew by",
        ],
    },
    "Funding_Raised": {
        "dataset_columns": [
            "Funding_Raised",
        ],
        "keywords": [
            "funding raised",
            "raised",
            "funding",
            "capital raised",
        ],
    },
    "Valuation": {
        "dataset_columns": [
            "Valuation",
            "Ask_Valuation",
        ],
        "keywords": [
            "valuation",
            "valued at",
            "company valuation",
        ],
    },
    "Funding_Required": {
        "dataset_columns": [
            "Funding_Required",
        ],
        "keywords": [
            "funding required",
            "funding ask",
            "investment required",
            "raising",
            "raise",
            "ask",
        ],
    },
    "Equity_Offered": {
        "dataset_columns": [
            "Equity_Offered",
        ],
        "keywords": [
            "equity",
            "equity offered",
            "stake",
        ],
    },
}


def _to_number(value):
    """
    Convert common financial/numeric text into a number.
    """

    if value is None:
        return None

    if isinstance(value, bool):
        return None

    if isinstance(value, (int, float)):
        if isinstance(value, float) and math.isnan(value):
            return None
        return float(value)

    text = str(value).strip().lower()

    if not text or text in {
        "nan",
        "none",
        "na",
        "n/a",
        "-",
    }:
        return None

    text = text.replace(",", "")
    text = text.replace("₹", "")
    text = text.replace("$", "")
    text = text.replace("€", "")
    text = text.replace("£", "")

    multiplier = 1

    if "crore" in text or "cr" in text:
        multiplier = 10_000_000

    elif "lakh" in text or "lac" in text:
        multiplier = 100_000

    elif "million" in text:
        multiplier = 1_000_000

    elif "billion" in text:
        multiplier = 1_000_000_000

    elif "thousand" in text:
        multiplier = 1_000

    percent = "%" in text

    match = re.search(
        r"-?\d+(?:\.\d+)?",
        text,
    )

    if not match:
        return None

    number = float(match.group())

    if percent:
        return number

    return number * multiplier


def _extract_pitch_numbers(evidence):
    """
    Extract numeric claims from pitch evidence.
    """

    claims = []

    for sentence in evidence:

        matches = re.finditer(
            r"(?i)"
            r"(?:₹|\$|€|£)?\s*"
            r"\d+(?:,\d+)*(?:\.\d+)?"
            r"\s*"
            r"(?:crore|cr|lakh|lac|million|billion|thousand|%)?",
            sentence,
        )

        for match in matches:

            raw_value = match.group().strip()
            numeric_value = _to_number(raw_value)

            if numeric_value is not None:
                claims.append(
                    {
                        "raw_value": raw_value,
                        "value": numeric_value,
                        "evidence": sentence,
                    }
                )

    return claims


def _find_dataset_value(dataset_row, field):
    """
    Find the first usable dataset value for a consistency field.
    """

    config = CONSISTENCY_FIELDS[field]

    for column in config["dataset_columns"]:

        if column not in dataset_row.index:
            continue

        value = _to_number(
            dataset_row[column]
        )

        if value is not None:
            return value, column

    return None, None


def _field_mentioned(sentence, field):
    """
    Check whether a sentence is relevant to a field.
    """

    keywords = CONSISTENCY_FIELDS[field]["keywords"]

    sentence_lower = sentence.lower()

    return any(
        keyword.lower() in sentence_lower
        for keyword in keywords
    )


def _compare_values(
    pitch_value,
    dataset_value,
    tolerance=0.15,
):
    """
    Compare pitch and dataset values.

    Values within the tolerance range are treated as MATCH.
    """

    if pitch_value is None or dataset_value is None:
        return "NOT_AVAILABLE"

    if dataset_value == 0:

        if pitch_value == 0:
            return "MATCH"

        return "MISMATCH"

    difference = abs(
        pitch_value - dataset_value
    ) / abs(dataset_value)

    if difference <= tolerance:
        return "MATCH"

    return "MISMATCH"


def check_consistency(
    pitch_result,
    dataset_row,
    tolerance=0.15,
):
    """
    Compare pitch-deck claims against one startup's
    structured dataset row.
    """

    if not isinstance(dataset_row, pd.Series):
        dataset_row = pd.Series(dataset_row)

    comparisons = []

    for field in CONSISTENCY_FIELDS:

        dataset_value, dataset_column = (
            _find_dataset_value(
                dataset_row,
                field,
            )
        )

        criterion = pitch_result.get(
            "criteria",
            {},
        ).get(field)

        evidence = []

        if criterion:
            evidence = criterion.get(
                "evidence",
                [],
            )

        relevant_evidence = [
            sentence
            for sentence in evidence
            if _field_mentioned(
                sentence,
                field,
            )
        ]

        pitch_claims = _extract_pitch_numbers(
            relevant_evidence
        )

        if dataset_value is None:

            comparisons.append(
                {
                    "field": field,
                    "status": "NOT_AVAILABLE",
                    "pitch_value": (
                        pitch_claims[0]["raw_value"]
                        if pitch_claims
                        else None
                    ),
                    "dataset_value": None,
                    "dataset_column": dataset_column,
                    "difference_percent": None,
                    "evidence": (
                        pitch_claims[0]["evidence"]
                        if pitch_claims
                        else None
                    ),
                    "reason": (
                        "Dataset value is not available."
                    ),
                }
            )

            continue

        if not pitch_claims:

            comparisons.append(
                {
                    "field": field,
                    "status": "NOT_AVAILABLE",
                    "pitch_value": None,
                    "dataset_value": dataset_value,
                    "dataset_column": dataset_column,
                    "difference_percent": None,
                    "evidence": None,
                    "reason": (
                        "No numeric claim was found "
                        "in the pitch evidence."
                    ),
                }
            )

            continue

        claim = pitch_claims[0]

        status = _compare_values(
            claim["value"],
            dataset_value,
            tolerance=tolerance,
        )

        if dataset_value != 0:

            difference_percent = round(
                (
                    abs(
                        claim["value"]
                        - dataset_value
                    )
                    / abs(dataset_value)
                )
                * 100,
                2,
            )

        else:
            difference_percent = (
                0.0
                if claim["value"] == 0
                else None
            )

        comparisons.append(
            {
                "field": field,
                "status": status,
                "pitch_value": claim["raw_value"],
                "dataset_value": dataset_value,
                "dataset_column": dataset_column,
                "difference_percent": difference_percent,
                "evidence": claim["evidence"],
                "reason": (
                    "Pitch claim and dataset value "
                    "are within the accepted tolerance."
                    if status == "MATCH"
                    else
                    "Pitch claim differs materially "
                    "from the dataset value."
                    if status == "MISMATCH"
                    else
                    "Insufficient evidence for comparison."
                ),
            }
        )

    return comparisons


def calculate_consistency_score(comparisons):
    """
    Calculate a 0-100 Deck–Data Consistency Score.

    Only MATCH and MISMATCH comparisons are scored.
    NOT_AVAILABLE does not reduce the score.
    """

    scored = [
        item
        for item in comparisons
        if item["status"] in {
            "MATCH",
            "MISMATCH",
        }
    ]

    if not scored:
        return None

    matches = sum(
        1
        for item in scored
        if item["status"] == "MATCH"
    )

    return round(
        (matches / len(scored)) * 100,
        2,
    )


def summarize_consistency(comparisons):
    """
    Create a compact summary for the frontend.
    """

    match_count = sum(
        1
        for item in comparisons
        if item["status"] == "MATCH"
    )

    mismatch_count = sum(
        1
        for item in comparisons
        if item["status"] == "MISMATCH"
    )

    unavailable_count = sum(
        1
        for item in comparisons
        if item["status"] == "NOT_AVAILABLE"
    )

    score = calculate_consistency_score(
        comparisons
    )

    return {
        "consistency_score": score,
        "match_count": match_count,
        "mismatch_count": mismatch_count,
        "not_available_count": unavailable_count,
        "total_fields_checked": len(comparisons),
    }