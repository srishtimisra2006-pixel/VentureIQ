from pathlib import Path
import pandas as pd


def build_startup_dimension(df):
    """Create the master startup table."""

    identity_columns = [
        "Startup_ID",
        "Startup_Name",
        "Industry",
        "Business_Model",
        "Founded_Year",
        "Location",
        "Funding_Stage"
    ]

    available = [
        column
        for column in identity_columns
        if column in df.columns
    ]

    return df[available].drop_duplicates(
        subset=["Startup_Name"]
        if "Startup_Name" in available
        else None
    )


def build_financials(df):
    """Create the financial analysis table."""

    columns = [
        "Startup_Name",
        "Revenue",
        "Revenue_Growth",
        "Gross_Margin",
        "Net_Margin",
        "EBITDA",
        "Burn_Rate",
        "Cash_Balance",
        "Cash_Runway",
        "Funding_Raised",
        "Valuation",
        "Debt",
        "Funding_Required",
        "Equity_Offered",
        "Ask_Valuation"
    ]

    available = [
        column
        for column in columns
        if column in df.columns
    ]

    return df[available].copy()


def build_scores(df):
    """Create the investment scoring table."""

    columns = [
        "Startup_Name",
        "Attractiveness_Score",
        "Scorable_Metrics",
        "Scored_Categories",
        "Weight_Coverage",
        "Completeness"
    ]

    available = [
        column
        for column in columns
        if column in df.columns
    ]

    return df[available].copy()


def build_risk_table(df):
    """Create the risk analysis table."""

    columns = [
        "Startup_Name",
        "Risk_Score",
        "Risk_Level",
        "High_Flags",
        "Medium_Flags",
        "Low_Flags",
        "Total_Flags",
        "Investment_Category"
    ]

    available = [
        column
        for column in columns
        if column in df.columns
    ]

    return df[available].copy()


def build_derived_metrics(df):
    """Create the derived metrics table."""

    derived_columns = [
        "Startup_Name",
        "Revenue_Per_Founder",
        "Monthly_Sales_Revenue_Ratio",
        "EBITDA_Margin_Calculated",
        "Deal_Amount_to_Valuation",
        "Funding_to_Revenue",
        "Implied_Ask_Valuation",
        "Valuation_to_Revenue",
        "Ask_to_Revenue",
        "Net_Burn_Ratio",
        "Funded_Runway_Proxy"
    ]

    available = [
        column
        for column in derived_columns
        if column in df.columns
    ]

    return df[available].copy()


def publish_outputs(
    input_path="output/investment_decisions.csv",
    output_dir="output/published"
):
    """
    Build the final VentureIQ analytical data package.
    """

    input_path = Path(input_path)
    output_dir = Path(output_dir)

    if not input_path.exists():
        raise FileNotFoundError(
            f"Input file not found: {input_path}"
        )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    df = pd.read_csv(input_path)

    tables = {
        "Dim_Startup": build_startup_dimension(df),
        "Fact_Financials": build_financials(df),
        "Fact_Scores": build_scores(df),
        "Fact_Risk": build_risk_table(df),
        "Fact_DerivedMetrics": build_derived_metrics(df)
    }

    outputs = {}

    for table_name, table_df in tables.items():

        output_path = (
            output_dir /
            f"{table_name}.csv"
        )

        table_df.to_csv(
            output_path,
            index=False
        )

        outputs[table_name] = output_path

    # Also save the complete analytical dataset.
    full_path = (
        output_dir /
        "VentureIQ_Final_Analysis.csv"
    )

    df.to_csv(
        full_path,
        index=False
    )

    outputs["Final_Analysis"] = full_path

    return outputs


if __name__ == "__main__":

    print("VentureIQ Publish Engine")
    print("------------------------")

    try:

        outputs = publish_outputs()

        print()
        print(
            "Publishing completed successfully."
        )

        print()
        print("Generated analytical tables:")

        for name, path in outputs.items():
            print(
                f"- {name}: {path}"
            )

        print()
        print(
            "VentureIQ analytical package ready."
        )

    except Exception as error:

        print()
        print(
            f"ERROR: {error}"
        )

        raise