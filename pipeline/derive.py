from pathlib import Path
import pandas as pd


def safe_divide(numerator, denominator):
    """
    Safely divide two values.
    Returns NA when denominator is zero or missing.
    """
    numerator = pd.to_numeric(numerator, errors="coerce")
    denominator = pd.to_numeric(denominator, errors="coerce")

    result = numerator.div(denominator)

    result = result.replace(
        [float("inf"), float("-inf")],
        pd.NA
    )

    return result


def calculate_derived_metrics(df):
    """
    Calculate VentureIQ derived metrics.

    Missing source values are not imputed.
    """

    result = df.copy()

    # -------------------------------------------------
    # 1. Revenue per Founder
    # -------------------------------------------------

    if {
        "Revenue",
        "Founder_Count"
    }.issubset(result.columns):

        result["Revenue_Per_Founder"] = safe_divide(
            result["Revenue"],
            result["Founder_Count"]
        )

    # -------------------------------------------------
    # 2. Annualized Monthly Sales / Revenue
    # -------------------------------------------------

    if {
        "Monthly_Sales",
        "Revenue"
    }.issubset(result.columns):

        annualized_sales = (
            pd.to_numeric(
                result["Monthly_Sales"],
                errors="coerce"
            ) * 12
        )

        result["Monthly_Sales_Revenue_Ratio"] = safe_divide(
            annualized_sales,
            result["Revenue"]
        )

    # -------------------------------------------------
    # 3. EBITDA Margin
    # -------------------------------------------------

    if {
        "EBITDA",
        "Revenue"
    }.issubset(result.columns):

        result["EBITDA_Margin_Calculated"] = (
            safe_divide(
                result["EBITDA"],
                result["Revenue"]
            ) * 100
        )

    # -------------------------------------------------
    # 4. Deal Amount / Deal Valuation
    # -------------------------------------------------

    if {
        "Deal_Amount",
        "Deal_Valuation"
    }.issubset(result.columns):

        result["Deal_Amount_to_Valuation"] = (
            safe_divide(
                result["Deal_Amount"],
                result["Deal_Valuation"]
            ) * 100
        )

    # -------------------------------------------------
    # 5. Funding Required / Revenue
    # -------------------------------------------------

    if {
        "Funding_Required",
        "Revenue"
    }.issubset(result.columns):

        result["Funding_to_Revenue"] = safe_divide(
            result["Funding_Required"],
            result["Revenue"]
        )

    # -------------------------------------------------
    # 6. Implied Ask Valuation
    #
    # Funding Required / Equity Offered
    # -------------------------------------------------

    if {
        "Funding_Required",
        "Equity_Offered"
    }.issubset(result.columns):

        equity_ratio = (
            pd.to_numeric(
                result["Equity_Offered"],
                errors="coerce"
            ) / 100
        )

        result["Implied_Ask_Valuation"] = safe_divide(
            result["Funding_Required"],
            equity_ratio
        )

    # -------------------------------------------------
    # 7. Valuation / Revenue
    # -------------------------------------------------

    if {
        "Valuation",
        "Revenue"
    }.issubset(result.columns):

        result["Valuation_to_Revenue"] = safe_divide(
            result["Valuation"],
            result["Revenue"]
        )

    # -------------------------------------------------
    # 8. Ask Valuation / Revenue
    # -------------------------------------------------

    if {
        "Ask_Valuation",
        "Revenue"
    }.issubset(result.columns):

        result["Ask_to_Revenue"] = safe_divide(
            result["Ask_Valuation"],
            result["Revenue"]
        )

    # -------------------------------------------------
    # 9. Net Burn Ratio
    # -------------------------------------------------

    if {
        "Burn_Rate",
        "Revenue"
    }.issubset(result.columns):

        result["Net_Burn_Ratio"] = safe_divide(
            result["Burn_Rate"],
            result["Revenue"]
        )

    # -------------------------------------------------
    # 10. Funded Runway Proxy
    #
    # Cash Balance / Burn Rate
    # -------------------------------------------------

    if {
        "Cash_Balance",
        "Burn_Rate"
    }.issubset(result.columns):

        result["Funded_Runway_Proxy"] = safe_divide(
            result["Cash_Balance"],
            result["Burn_Rate"]
        )

    return result


def save_derived_data(
    df,
    output_path="output/derived_startup_data.csv"
):
    """
    Save dataset containing derived metrics.
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

    print("VentureIQ Derived Metrics Engine")
    print("--------------------------------")

    input_path = Path(
        "output/cleaned_startup_data.csv"
    )

    if not input_path.exists():

        print(
            f"Input file not found: {input_path}"
        )

        print(
            "Run the processing pipeline first."
        )

        raise SystemExit(1)

    df = pd.read_csv(input_path)

    print(
        f"Loaded dataset: "
        f"{df.shape[0]} rows × {df.shape[1]} columns"
    )

    derived_df = calculate_derived_metrics(df)

    output_path = save_derived_data(
        derived_df
    )

    print()
    print("Derived metrics calculated successfully.")
    print(
        f"Output: {output_path}"
    )

    print()
    print("Derived columns found:")

    derived_columns = [
        column
        for column in derived_df.columns
        if column not in df.columns
    ]

    for column in derived_columns:
        print(f"- {column}")

    print()
    print(
        f"Final dataset: "
        f"{derived_df.shape[0]} rows × "
        f"{derived_df.shape[1]} columns"
    )