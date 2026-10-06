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


# 1. Analyze pitch deck
pitch_result = analyze_pitch_deck(
    "data/VentureIQ_Test_Pitch_Deck.pdf"
)


# 2. Load startup dataset
dataset = pd.read_csv(
    "data/test_startup.csv"
)

startup = dataset.iloc[0]


# 3. Check deck vs dataset
comparisons = check_consistency(
    pitch_result,
    startup,
)

consistency_summary = summarize_consistency(
    comparisons
)


# 4. Generate investment assessment
investment_assessment = generate_investment_assessment(
    pitch_result=pitch_result,
    consistency_summary=consistency_summary,
    risk_score=25,
    completeness=85,
)


# 5. Build final VentureIQ output
final_output = build_pitch_intelligence_output(
    pitch_result=pitch_result,
    consistency_summary=consistency_summary,
    investment_assessment=investment_assessment,
)


# 6. Validate final structure
validate_pitch_intelligence_output(
    final_output
)


print("=" * 60)
print("VENTUREIQ PITCH INTELLIGENCE")
print("=" * 60)

print(
    "Pitch Score:",
    final_output["pitch_analysis"]["pitch_score"]
)

print(
    "Evidence Confidence:",
    final_output["pitch_analysis"]["evidence_confidence"]
)

print(
    "Consistency Score:",
    final_output["deck_data_consistency"]["consistency_score"]
)

print(
    "Investment Score:",
    final_output["investment_assessment"]["investment_score"]
)

print(
    "Investment Category:",
    final_output["investment_assessment"][
        "investment_category"
    ]
)

print(
    "Matches:",
    final_output["deck_data_consistency"]["match_count"]
)

print(
    "Mismatches:",
    final_output["deck_data_consistency"]["mismatch_count"]
)

print("\nFINAL OUTPUT STRUCTURE VALIDATED")
print("Pitch Intelligence integration successful.")