from pathlib import Path

import pandas as pd

from pipeline.pitch_analyzer import analyze_pitch_deck
from pipeline.consistency import (
    check_consistency,
    summarize_consistency,
)
from pipeline.investment_assessment import (
    generate_investment_assessment,
)
from pipeline.pitch_output import (
    build_pitch_intelligence_output,
    validate_pitch_intelligence_output,
)


def run_pitch_intelligence(
    pitch_file,
    dataset_file=None,
    startup_index=0,
    risk_score=None,
    completeness=None,
):
    """
    Run the complete VentureIQ Pitch Intelligence pipeline.

    Supports:
        1. Pitch deck only
        2. Pitch deck + startup dataset
    """

    pitch_path = Path(pitch_file)

    if not pitch_path.exists():
        raise FileNotFoundError(
            f"Pitch deck not found: {pitch_file}"
        )

    # --------------------------------------------------
    # STEP 1: Analyze pitch deck
    # --------------------------------------------------

    pitch_result = analyze_pitch_deck(
        pitch_path
    )

    # --------------------------------------------------
    # STEP 2: Optional dataset analysis
    # --------------------------------------------------

    consistency_summary = {
        "consistency_score": None,
        "match_count": 0,
        "mismatch_count": 0,
        "not_available_count": 0,
        "total_fields_checked": 0,
    }

    consistency_comparisons = []

    if dataset_file:

        dataset_path = Path(dataset_file)

        if not dataset_path.exists():
            raise FileNotFoundError(
                f"Dataset not found: {dataset_file}"
            )

        suffix = dataset_path.suffix.lower()

        if suffix == ".csv":

            dataset = pd.read_csv(
                dataset_path
            )

        elif suffix in {".xlsx", ".xls"}:

            dataset = pd.read_excel(
                dataset_path
            )

        else:
            raise ValueError(
                "Unsupported dataset format. "
                "Use CSV, XLSX or XLS."
            )

        if dataset.empty:
            raise ValueError(
                "The uploaded dataset is empty."
            )

        if startup_index < 0:
            raise ValueError(
                "startup_index cannot be negative."
            )

        if startup_index >= len(dataset):
            raise IndexError(
                f"startup_index {startup_index} is outside "
                f"the dataset range."
            )

        startup = dataset.iloc[
            startup_index
        ]

        consistency_comparisons = check_consistency(
            pitch_result,
            startup,
        )

        consistency_summary = summarize_consistency(
            consistency_comparisons
        )

    # --------------------------------------------------
    # STEP 3: Generate investment assessment
    # --------------------------------------------------

    investment_assessment = (
        generate_investment_assessment(
            pitch_result=pitch_result,
            consistency_summary=consistency_summary,
            risk_score=risk_score,
            completeness=completeness,
        )
    )

    # --------------------------------------------------
    # STEP 4: Build final output
    # --------------------------------------------------

    final_output = (
        build_pitch_intelligence_output(
            pitch_result=pitch_result,
            consistency_summary=consistency_summary,
            investment_assessment=investment_assessment,
        )
    )

    # --------------------------------------------------
    # STEP 5: Add detailed comparisons
    # --------------------------------------------------

    final_output[
        "deck_data_consistency"
    ][
        "comparisons"
    ] = consistency_comparisons

    # --------------------------------------------------
    # STEP 6: Validate final structure
    # --------------------------------------------------

    validate_pitch_intelligence_output(
        final_output
    )

    return final_output