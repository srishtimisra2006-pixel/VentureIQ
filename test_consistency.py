import pandas as pd

from pipeline.pitch_analyzer import analyze_pitch_deck
from pipeline.consistency import (
    check_consistency,
    summarize_consistency,
)


# 1. Analyze the pitch deck
pitch_result = analyze_pitch_deck(
    "data/VentureIQ_Test_Pitch_Deck.pdf"
)


# 2. Load the startup dataset
dataset = pd.read_csv(
    "data/test_startup.csv"
)

startup = dataset.iloc[0]


# 3. Compare pitch claims with dataset values
comparisons = check_consistency(
    pitch_result,
    startup,
)


# 4. Create summary
summary = summarize_consistency(
    comparisons
)


print("=" * 60)
print("VENTUREIQ DECK × DATASET CONSISTENCY TEST")
print("=" * 60)

print(
    "Consistency Score:",
    summary["consistency_score"]
)

print(
    "Matches:",
    summary["match_count"]
)

print(
    "Mismatches:",
    summary["mismatch_count"]
)

print(
    "Not Available:",
    summary["not_available_count"]
)

print("\nFIELD COMPARISON")
print("-" * 60)

for item in comparisons:

    print(
        f"{item['field']}: "
        f"{item['status']} | "
        f"Pitch: {item['pitch_value']} | "
        f"Dataset: {item['dataset_value']}"
    )

print("\nConsistency test completed successfully.")