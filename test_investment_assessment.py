from pipeline.pitch_analyzer import analyze_pitch_deck
from pipeline.consistency import (
    check_consistency,
    summarize_consistency,
)
from pipeline.investment_assessment import (
    generate_investment_assessment,
)


# Analyze pitch deck
pitch_result = analyze_pitch_deck(
    "data/VentureIQ_Test_Pitch_Deck.pdf"
)


# Load startup dataset
import pandas as pd

dataset = pd.read_csv(
    "data/test_startup.csv"
)

startup = dataset.iloc[0]


# Check deck vs dataset
comparisons = check_consistency(
    pitch_result,
    startup,
)

consistency_summary = summarize_consistency(
    comparisons
)


# Generate investment assessment
assessment = generate_investment_assessment(
    pitch_result=pitch_result,
    consistency_summary=consistency_summary,
    risk_score=25,
    completeness=85,
)


print("=" * 60)
print("VENTUREIQ INVESTMENT ASSESSMENT TEST")
print("=" * 60)

print(
    "Pitch Score:",
    assessment["pitch_score"]
)

print(
    "Consistency Score:",
    assessment["consistency_score"]
)

print(
    "Risk Score:",
    assessment["risk_score"]
)

print(
    "Completeness:",
    assessment["completeness"]
)

print(
    "Investment Score:",
    assessment["investment_score"]
)

print(
    "Investment Category:",
    assessment["investment_category"]
)

print("\nStrengths:")
for item in assessment["strengths"]:
    print("-", item)

print("\nRisks:")
for item in assessment["risks"]:
    print("-", item)

print("\nDue Diligence Actions:")
for item in assessment["due_diligence_actions"]:
    print("-", item)

print("\nInvestment assessment completed successfully.")