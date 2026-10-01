from pathlib import Path
import re
import pandas as pd


NULL_MARKERS = {
    "",
    "-",
    "na",
    "n/a",
    "nan",
    "none",
    "null",
    "not available",
    "not applicable"
}


PERCENTAGE_FIELDS = {
    "Revenue_Growth",
    "Gross_Margin",
    "Net_Margin",
    "Customer_Growth",
    "Retention",
    "Market_Growth",
    "Equity_Offered",
    "Deal_Equity"
}


MONEY_FIELDS = {
    "Revenue",
    "EBITDA",
    "Burn_Rate",
    "Cash_Balance",
    "Funding_Raised",
    "Valuation",
    "Debt",
    "TAM",
    "SAM",
    "SOM",
    "Monthly_Sales",
    "Funding_Required",
    "Ask_Valuation",
    "Deal_Amount",
    "Deal_Valuation"
}


NON_NEGATIVE_FIELDS = {
    "Revenue",
    "Funding_Required",
    "Funding_Raised",
    "Valuation",
    "Debt",
    "Cash_Balance",
    "Burn_Rate",
    "Customers",
    "Customer_Growth",
    "Monthly_Sales",
    "Retention",
    "SKUs",
    "TAM",
    "SAM",
    "SOM",
    "Team_Size",
    "Founder_Count",
    "Founder_Experience",
    "Technology_Readiness",
    "Deal_Amount",
    "Deal_Valuation"
}


def normalize_nulls(df):
    """
    Convert common missing-value markers into pandas NA.
    """

    cleaned = df.copy()

    for column in cleaned.columns:

        if cleaned[column].dtype == "object":

            cleaned[column] = cleaned[column].apply(
                lambda value:
                pd.NA
                if str(value).strip().lower() in NULL_MARKERS
                else value
            )

    return cleaned


def clean_text(value):
    """
    Standardize text values.
    """

    if pd.isna(value):
        return pd.NA

    value = str(value).strip()

    if value.lower() in NULL_MARKERS:
        return pd.NA

    value = re.sub(r"\s+", " ", value)

    return value


def parse_numeric(value):
    """
    Convert common financial/text representations into numbers.

    Handles:
    ₹, $, €, £
    commas
    percentages
    crore
    lakh
    million
    billion
    """

    if pd.isna(value):
        return pd.NA

    if isinstance(value, (int, float)):
        return value

    text = str(value).strip().lower()

    if text in NULL_MARKERS:
        return pd.NA

    multiplier = 1

    if "billion" in text:
        multiplier = 1_000_000_000
    elif "million" in text:
        multiplier = 1_000_000
    elif "crore" in text:
        multiplier = 10_000_000
    elif "lakh" in text:
        multiplier = 100_000

    text = (
        text.replace("₹", "")
        .replace("$", "")
        .replace("€", "")
        .replace("£", "")
        .replace(",", "")
        .replace("%", "")
        .replace("billion", "")
        .replace("million", "")
        .replace("crore", "")
        .replace("lakh", "")
        .strip()
    )

    try:
        return float(text) * multiplier

    except (ValueError, TypeError):
        return pd.NA


def normalize_percentages(df):
    """
    Convert ratio-style percentages such as 0.25 into 25.

    Only applies to known percentage fields.
    """

    cleaned = df.copy()

    for column in PERCENTAGE_FIELDS:

        if column not in cleaned.columns:
            continue

        numeric = pd.to_numeric(
            cleaned[column],
            errors="coerce"
        )

        valid_values = numeric.dropna()

        if len(valid_values) == 0:
            continue

        if valid_values.max() <= 1.5:
            cleaned[column] = numeric * 100
        else:
            cleaned[column] = numeric

    return cleaned


def clean_dataset(df):
    """
    Main cleaning function.
    """

    cleaned = df.copy()

    # Step 1: missing values
    cleaned = normalize_nulls(cleaned)

    # Step 2: clean text
    for column in cleaned.columns:

        if cleaned[column].dtype == "object":
            cleaned[column] = cleaned[column].apply(clean_text)

    # Step 3: convert known numeric fields
    for column in MONEY_FIELDS:

        if column in cleaned.columns:

            cleaned[column] = cleaned[column].apply(
                parse_numeric
            )

    # Step 4: convert other known numeric fields
    numeric_fields = (
        NON_NEGATIVE_FIELDS
        | PERCENTAGE_FIELDS
        | {"Founded_Year"}
    )

    for column in numeric_fields:

        if column not in cleaned.columns:
            continue

        if column in MONEY_FIELDS:
            continue

        cleaned[column] = pd.to_numeric(
            cleaned[column],
            errors="coerce"
        )

    # Step 5: percentage normalization
    cleaned = normalize_percentages(cleaned)

    return cleaned


def validate_dataset(df):
    """
    Validate cleaned data.

    Invalid values are converted to missing values.
    No imputation is performed.
    """

    validated = df.copy()

    flags = []

    for column in validated.columns:

        if column not in NON_NEGATIVE_FIELDS:
            continue

        numeric = pd.to_numeric(
            validated[column],
            errors="coerce"
        )

        invalid_mask = numeric < 0

        for index in validated.index[invalid_mask]:

            flags.append({
                "Row": index,
                "Column": column,
                "Issue": "Negative value not allowed",
                "Original_Value": validated.loc[index, column]
            })

            validated.loc[index, column] = pd.NA

    # Equity must be between 0 and 100
    for column in ["Equity_Offered", "Deal_Equity"]:

        if column not in validated.columns:
            continue

        numeric = pd.to_numeric(
            validated[column],
            errors="coerce"
        )

        invalid_mask = (numeric < 0) | (numeric > 100)

        for index in validated.index[invalid_mask]:

            flags.append({
                "Row": index,
                "Column": column,
                "Issue": "Percentage must be between 0 and 100",
                "Original_Value": validated.loc[index, column]
            })

            validated.loc[index, column] = pd.NA

    # Revenue cannot be negative
    if "Revenue" in validated.columns:

        numeric = pd.to_numeric(
            validated["Revenue"],
            errors="coerce"
        )

        invalid_mask = numeric < 0

        for index in validated.index[invalid_mask]:

            flags.append({
                "Row": index,
                "Column": "Revenue",
                "Issue": "Revenue cannot be negative",
                "Original_Value": validated.loc[index, "Revenue"]
            })

            validated.loc[index, "Revenue"] = pd.NA

    # Founder count must be non-negative
    if "Founder_Count" in validated.columns:

        numeric = pd.to_numeric(
            validated["Founder_Count"],
            errors="coerce"
        )

        invalid_mask = numeric < 0

        for index in validated.index[invalid_mask]:

            flags.append({
                "Row": index,
                "Column": "Founder_Count",
                "Issue": "Founder count cannot be negative",
                "Original_Value": validated.loc[index, "Founder_Count"]
            })

            validated.loc[index, "Founder_Count"] = pd.NA

    validation_df = pd.DataFrame(flags)

    if validation_df.empty:
        validation_df = pd.DataFrame(
            columns=[
                "Row",
                "Column",
                "Issue",
                "Original_Value"
            ]
        )

    return validated, validation_df


def create_quality_summary(df):
    """
    Create a column-level data quality summary.
    """

    summary = []

    total_rows = len(df)

    for column in df.columns:

        missing = int(df[column].isna().sum())

        summary.append({
            "Column": column,
            "Data_Type": str(df[column].dtype),
            "Total_Rows": total_rows,
            "Missing_Values": missing,
            "Missing_Percentage": round(
                (missing / total_rows) * 100,
                2
            ) if total_rows else 0,
            "Unique_Values": int(
                df[column].nunique(dropna=True)
            )
        })

    return pd.DataFrame(summary)


def save_cleaning_outputs(
    cleaned_df,
    validation_df,
    quality_df,
    output_dir="output"
):
    """
    Save all cleaning outputs.
    """

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    cleaned_path = (
        output_dir / "cleaned_startup_data.csv"
    )

    validation_path = (
        output_dir / "validation_flags.csv"
    )

    quality_path = (
        output_dir / "data_quality_summary.csv"
    )

    cleaned_df.to_csv(
        cleaned_path,
        index=False
    )

    validation_df.to_csv(
        validation_path,
        index=False
    )

    quality_df.to_csv(
        quality_path,
        index=False
    )

    return {
        "cleaned": cleaned_path,
        "validation": validation_path,
        "quality": quality_path
    }


if __name__ == "__main__":

    print("VentureIQ Cleaning Engine")
    print("-------------------------")
    print("Module loaded successfully.")
    print()
    print("Cleaning rules available:")
    print("- Null normalization")
    print("- Text cleaning")
    print("- Financial value parsing")
    print("- Percentage normalization")
    print("- Negative value validation")
    print("- Equity range validation")
    print("- Data quality summary")
    print()
    print("No data was modified.")