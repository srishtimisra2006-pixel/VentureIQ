from pipeline.pitch_analyzer import analyze_pitch_deck


deck_path = "data/VentureIQ_Test_Pitch_Deck.pdf"

result = analyze_pitch_deck(deck_path)

print("=" * 50)
print("VENTUREIQ PITCH DECK ANALYSIS")
print("=" * 50)

print("Pitch Score:", result["pitch_score"])
print("Evidence Confidence:", result["evidence_confidence"])
print("Criteria Analyzed:", len(result["criteria"]))
print("Strengths:", len(result["strengths"]))
print("Risks:", len(result["risks"]))

print("\nCRITERIA SCORES")
print("-" * 50)

for criterion, data in result["criteria"].items():
    print(
        f"{criterion}: "
        f"{data['score']} "
        f"| Confidence: {data['confidence']} "
        f"| Status: {data['evidence_status']}"
    )

print("\nAnalysis completed successfully.")