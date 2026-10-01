from pathlib import Path
import pandas as pd


SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls"}


def load_dataset(file_path):
    """
    Load a CSV, XLSX, or XLS dataset.

    Parameters
    ----------
    file_path : str or Path
        Path to the uploaded dataset.

    Returns
    -------
    pandas.DataFrame
        Loaded dataset.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {file_path}"
        )

    extension = file_path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {extension}. "
            f"Supported formats: CSV, XLSX, XLS."
        )

    if extension == ".csv":
        df = pd.read_csv(file_path)

    elif extension == ".xlsx":
        df = pd.read_excel(file_path, engine="openpyxl")

    elif extension == ".xls":
        df = pd.read_excel(file_path, engine="xlrd")

    else:
        raise ValueError("Unsupported dataset format.")

    if df.empty:
        raise ValueError("The uploaded dataset is empty.")

    # Remove completely empty rows
    df = df.dropna(how="all").reset_index(drop=True)

    # Clean column names
    df.columns = [
        str(column).strip()
        for column in df.columns
    ]

    return df


def get_dataset_profile(df):
    """
    Generate basic dataset information.
    """

    profile = {
        "rows": len(df),
        "columns": len(df.columns),
        "missing_cells": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "column_names": list(df.columns)
    }

    total_cells = df.shape[0] * df.shape[1]

    if total_cells > 0:
        profile["missing_percentage"] = round(
            (profile["missing_cells"] / total_cells) * 100,
            2
        )
    else:
        profile["missing_percentage"] = 0

    return profile


def save_raw_dataset(df, output_path):
    """
    Save the uploaded dataset as a standardized raw CSV.
    """

    output_path = Path(output_path)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        output_path,
        index=False
    )

    return output_path


if __name__ == "__main__":

    print("VentureIQ Ingestion Module")
    print("--------------------------")
    print("Supported formats:")
    print("CSV")
    print("XLSX")
    print("XLS")
    print()
    print("Module loaded successfully.")