from pipeline.engine import run_ventureiq


result = run_ventureiq(
    file_path="data/test_startup.csv",
    pitch_file="data/VentureIQ_Test_Pitch_Deck.pdf",
    startup_index=0,
)

print("\n" + "=" * 60)
print("PITCH INTEGRATION TEST")
print("=" * 60)

print(
    "Status:",
    result["status"]
)

print(
    "Rows analyzed:",
    result["rows_analyzed"]
)

print(
    "Columns analyzed:",
    result["columns_analyzed"]
)

pitch = result["pitch_intelligence"]

if pitch:

    print(
        "Pitch Score:",
        pitch["pitch_analysis"]["pitch_score"]
    )

    print(
        "Consistency Score:",
        pitch["deck_data_consistency"][
            "consistency_score"
        ]
    )

    print(
        "Investment Score:",
        pitch["investment_assessment"][
            "investment_score"
        ]
    )

    print(
        "Investment Category:",
        pitch["investment_assessment"][
            "investment_category"
        ]
    )

print("\nPitch integration test completed.")