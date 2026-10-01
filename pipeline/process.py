from pathlib import Path
import pandas as pd

from pipeline.ingest import load_dataset
from pipeline.mapping import map_columns
from pipeline.clean import (
    clean_dataset,
    validate_dataset,
    create_quality_summary,
    save_cleaning_outputs
)


def apply_mapping(df, mapping_df):
    """
    Rename automatically mapped source columns
    to VentureIQ standard field names.

    Unmapped columns are preserved.
    """

    rename_map = {}

    used_targets = set()

    for _, row in mapping_df.iterrows():

        source = row["Source_Column"]
        target = row["VentureIQ_Field"]
        status = row["Status"]

        if (
            status == "AUTO"
            and target
            and target not in used_targets
        ):
            rename_map[source] = target
            used_targets.add(target)

    processed = df.rename(columns=rename_map)

    return processed


def run_pipeline(
    input_path,
    schema_path="config/schema.yaml",
    output_dir="output"
):
    """
    Run the VentureIQ ingestion, mapping and cleaning pipeline.
    """

    print("=" * 60)
    print("VentureIQ DATA PROCESSING PIPELINE")
    print("=" * 60)

    # -------------------------
    # 1. INGEST
    # -------------------------

    print("\n[1/5] Loading dataset...")

    df = load_dataset(input_path)

    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    # -------------------------
    # 2. MAPPING
    # -------------------------

    print("\n[2/5] Mapping columns...")

    mapping_df = map_columns(
        df,
        schema_path=schema_path
    )

    mapping_path = (
        Path(output_dir) /
        "column_mapping.csv"
    )

    mapping_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    mapping_df.to_csv(
        mapping_path,
        index=False
    )

    auto_count = int(
        (mapping_df["Status"] == "AUTO").sum()
    )

    review_count = int(
        (mapping_df["Status"] == "REVIEW").sum()
    )

    unmapped_count = int(
        (mapping_df["Status"] == "UNMAPPED").sum()
    )

    print(f"Auto mapped: {auto_count}")
    print(f"Needs review: {review_count}")
    print(f"Unmapped: {unmapped_count}")

    # -------------------------
    # 3. APPLY MAPPING
    # -------------------------

    print("\n[3/5] Applying standard schema...")

    mapped_df = apply_mapping(
        df,
        mapping_df
    )

    print(
        f"Standardized columns: "
        f"{len(mapped_df.columns)}"
    )

    # -------------------------
    # 4. CLEAN
    # -------------------------

    print("\n[4/5] Cleaning and validating...")

    cleaned_df = clean_dataset(
        mapped_df
    )

    validated_df, validation_df = validate_dataset(
        cleaned_df
    )

    quality_df = create_quality_summary(
        validated_df
    )

    # -------------------------
    # 5. SAVE
    # -------------------------

    print("\n[5/5] Saving outputs...")

    outputs = save_cleaning_outputs(
        validated_df,
        validation_df,
        quality_df,
        output_dir=output_dir
    )

    print("\nPipeline completed successfully.")

    print("\nGenerated files:")

    for name, path in outputs.items():
        print(f"- {name}: {path}")

    print(f"- mapping: {mapping_path}")

    return {
        "data": validated_df,
        "mapping": mapping_df,
        "validation": validation_df,
        "quality": quality_df,
        "outputs": outputs,
        "mapping_path": mapping_path
    }


if __name__ == "__main__":

    dataset_path = Path(
        "data/sharktank.csv"
    )

    if not dataset_path.exists():

        print(
            f"Dataset not found: {dataset_path}"
        )

        raise SystemExit(1)

    result = run_pipeline(
        input_path=dataset_path
    )

    print("\nFinal dataset shape:")
    print(result["data"].shape)

    print("\nVentureIQ processing finished.")
    