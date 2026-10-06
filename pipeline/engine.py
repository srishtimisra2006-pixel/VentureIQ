from pathlib import Path
import subprocess
import sys

from pipeline.process import run_pipeline


def run_ventureiq(file_path):
    """
    Run the complete VentureIQ analytics engine.

    Pipeline:
    1. Ingestion
    2. Column mapping
    3. Cleaning and validation
    4. Derived metrics
    5. Investment scoring
    6. Risk and red flags
    7. Publishing
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {file_path}"
        )

    print("=" * 60)
    print("VENTUREIQ COMPLETE ANALYTICS ENGINE")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. INGEST + MAPPING + CLEANING + VALIDATION
    # ---------------------------------------------------------

    print("\n[1/5] Running data processing pipeline...")

    processing_result = run_pipeline(
        input_path=str(file_path),
        schema_path="config/schema.yaml",
        output_dir="output"
    )

    print("\nData processing completed.")

    # ---------------------------------------------------------
    # 2. DERIVED METRICS
    # ---------------------------------------------------------

    print("\n[2/5] Running derived metrics engine...")

    subprocess.run(
        [
            sys.executable,
            "-m",
            "pipeline.derive"
        ],
        check=True
    )

    # ---------------------------------------------------------
    # 3. INVESTMENT SCORING
    # ---------------------------------------------------------

    print("\n[3/5] Running investment scoring engine...")

    subprocess.run(
        [
            sys.executable,
            "-m",
            "pipeline.score"
        ],
        check=True
    )

    # ---------------------------------------------------------
    # 4. RISK + RED FLAGS
    # ---------------------------------------------------------

    print("\n[4/5] Running risk and red-flag engine...")

    subprocess.run(
        [
            sys.executable,
            "-m",
            "pipeline.flags"
        ],
        check=True
    )

    # ---------------------------------------------------------
    # 5. PUBLISH
    # ---------------------------------------------------------

    print("\n[5/5] Publishing final VentureIQ outputs...")

    subprocess.run(
        [
            sys.executable,
            "-m",
            "pipeline.publish"
        ],
        check=True
    )

    # ---------------------------------------------------------
    # FINAL RESULT
    # ---------------------------------------------------------

    final_path = Path(
        "output/published/VentureIQ_Final_Analysis.csv"
    )

    if not final_path.exists():
        raise FileNotFoundError(
            "Final VentureIQ analysis file was not generated."
        )

    print("\n" + "=" * 60)
    print("VENTUREIQ ENGINE COMPLETED SUCCESSFULLY")
    print("=" * 60)

    print(f"\nFinal analysis:")
    print(final_path)

    return {
        "status": "success",
        "input_file": str(file_path),
        "rows_analyzed": processing_result["data"].shape[0],
        "columns_analyzed": processing_result["data"].shape[1],
        "final_output": str(final_path),
        "published_outputs": {
            "startup": "output/published/Dim_Startup.csv",
            "financials": "output/published/Fact_Financials.csv",
            "scores": "output/published/Fact_Scores.csv",
            "risk": "output/published/Fact_Risk.csv",
            "derived_metrics": "output/published/Fact_DerivedMetrics.csv",
            "final_analysis": "output/published/VentureIQ_Final_Analysis.csv"
        }
    }


if __name__ == "__main__":

    dataset = "data/sharktank.csv"

    result = run_ventureiq(dataset)

    print()
    print("Rows analyzed:", result["rows_analyzed"])
    print("Columns analyzed:", result["columns_analyzed"])
    print("Final output:", result["final_output"])