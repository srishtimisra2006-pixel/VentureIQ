from pathlib import Path
import pandas as pd
import yaml


def load_risk_config(config_path="config/scoring.yaml"):
    """Load VentureIQ risk configuration."""

    config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration not found: {config_path}"
        )

    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def add_flag(
    flags,
    row_id,
    startup_name,
    flag_type,
    severity,
    reason,
    metric=None,
    value=None
):
    """Add one risk flag."""

    flags.append({
        "Row_ID": row_id,
        "Startup_Name": startup_name,
        "Flag_Type": flag_type,
        "Severity": severity,
        "Reason": reason,
        "Metric": metric,
        "Value": value
    })


def detect_flags(df):
    """
    Detect VentureIQ investment risk signals.
    """

    flags = []

    for index, row in df.iterrows():

        startup_name = row.get(
            "Startup_Name",
            f"Startup_{index}"
        )

        # -----------------------------------------
        # 1. LOW CASH RUNWAY
        # -----------------------------------------

        if "Cash_Runway" in df.columns:

            runway = pd.to_numeric(
                row.get("Cash_Runway"),
                errors="coerce"
            )

            if pd.notna(runway):

                if runway < 6:

                    add_flag(
                        flags,
                        index,
                        startup_name,
                        "Low_Runway",
                        "High",
                        "Cash runway is below 6 months.",
                        "Cash_Runway",
                        runway
                    )

                elif runway < 12:

                    add_flag(
                        flags,
                        index,
                        startup_name,
                        "Low_Runway",
                        "Medium",
                        "Cash runway is below 12 months.",
                        "Cash_Runway",
                        runway
                    )

        # -----------------------------------------
        # 2. HIGH BURN RATE
        # -----------------------------------------

        if "Burn_Rate" in df.columns:

            burn = pd.to_numeric(
                row.get("Burn_Rate"),
                errors="coerce"
            )

            if pd.notna(burn) and burn > 0:

                add_flag(
                    flags,
                    index,
                    startup_name,
                    "Positive_Burn",
                    "Medium",
                    "Startup has a positive cash burn rate.",
                    "Burn_Rate",
                    burn
                )

        # -----------------------------------------
        # 3. WEAK / NEGATIVE REVENUE GROWTH
        # -----------------------------------------

        if "Revenue_Growth" in df.columns:

            growth = pd.to_numeric(
                row.get("Revenue_Growth"),
                errors="coerce"
            )

            if pd.notna(growth):

                if growth < 0:

                    add_flag(
                        flags,
                        index,
                        startup_name,
                        "Negative_Growth",
                        "High",
                        "Revenue growth is negative.",
                        "Revenue_Growth",
                        growth
                    )

                elif growth < 10:

                    add_flag(
                        flags,
                        index,
                        startup_name,
                        "Weak_Growth",
                        "Medium",
                        "Revenue growth is below 10%.",
                        "Revenue_Growth",
                        growth
                    )

        # -----------------------------------------
        # 4. HIGH DEBT
        # -----------------------------------------

        if "Debt" in df.columns:

            debt = pd.to_numeric(
                row.get("Debt"),
                errors="coerce"
            )

            if pd.notna(debt) and debt > 0:

                add_flag(
                    flags,
                    index,
                    startup_name,
                    "Debt_Exposure",
                    "Medium",
                    "Startup has reported debt exposure.",
                    "Debt",
                    debt
                )

        # -----------------------------------------
        # 5. LOW GROSS MARGIN
        # -----------------------------------------

        if "Gross_Margin" in df.columns:

            margin = pd.to_numeric(
                row.get("Gross_Margin"),
                errors="coerce"
            )

            if pd.notna(margin):

                if margin < 30:

                    add_flag(
                        flags,
                        index,
                        startup_name,
                        "Low_Gross_Margin",
                        "High",
                        "Gross margin is below 30%.",
                        "Gross_Margin",
                        margin
                    )

                elif margin < 50:

                    add_flag(
                        flags,
                        index,
                        startup_name,
                        "Low_Gross_Margin",
                        "Medium",
                        "Gross margin is below 50%.",
                        "Gross_Margin",
                        margin
                    )

        # -----------------------------------------
        # 6. NEGATIVE NET MARGIN
        # -----------------------------------------

        if "Net_Margin" in df.columns:

            net_margin = pd.to_numeric(
                row.get("Net_Margin"),
                errors="coerce"
            )

            if pd.notna(net_margin) and net_margin < 0:

                add_flag(
                    flags,
                    index,
                    startup_name,
                    "Negative_Profitability",
                    "High",
                    "Net margin is negative.",
                    "Net_Margin",
                    net_margin
                )

        # -----------------------------------------
        # 7. NEGATIVE EBITDA
        # -----------------------------------------

        if "EBITDA" in df.columns:

            ebitda = pd.to_numeric(
                row.get("EBITDA"),
                errors="coerce"
            )

            if pd.notna(ebitda) and ebitda < 0:

                add_flag(
                    flags,
                    index,
                    startup_name,
                    "Negative_EBITDA",
                    "Medium",
                    "EBITDA is negative.",
                    "EBITDA",
                    ebitda
                )

        # -----------------------------------------
        # 8. HIGH FUNDING ASK RELATIVE TO REVENUE
        # -----------------------------------------

        if "Funding_to_Revenue" in df.columns:

            funding_ratio = pd.to_numeric(
                row.get("Funding_to_Revenue"),
                errors="coerce"
            )

            if pd.notna(funding_ratio):

                if funding_ratio > 2:

                    add_flag(
                        flags,
                        index,
                        startup_name,
                        "High_Funding_Ask",
                        "Medium",
                        "Funding required exceeds twice reported revenue.",
                        "Funding_to_Revenue",
                        funding_ratio
                    )

        # -----------------------------------------
        # 9. LOW DATA COMPLETENESS
        # -----------------------------------------

        if "Completeness" in df.columns:

            completeness = pd.to_numeric(
                row.get("Completeness"),
                errors="coerce"
            )

            if pd.notna(completeness):

                if completeness < 40:

                    add_flag(
                        flags,
                        index,
                        startup_name,
                        "Low_Data_Completeness",
                        "High",
                        "Less than 40% of scorable metrics are available.",
                        "Completeness",
                        completeness
                    )

                elif completeness < 60:

                    add_flag(
                        flags,
                        index,
                        startup_name,
                        "Low_Data_Completeness",
                        "Medium",
                        "Data completeness is below 60%.",
                        "Completeness",
                        completeness
                    )

        # -----------------------------------------
        # 10. PRE-REVENUE WITH LARGE FUNDING ASK
        # -----------------------------------------

        if {
            "Revenue",
            "Funding_Required"
        }.issubset(df.columns):

            revenue = pd.to_numeric(
                row.get("Revenue"),
                errors="coerce"
            )

            funding = pd.to_numeric(
                row.get("Funding_Required"),
                errors="coerce"
            )

            if (
                pd.notna(revenue)
                and pd.notna(funding)
                and revenue == 0
                and funding > 0
            ):

                add_flag(
                    flags,
                    index,
                    startup_name,
                    "Pre_Revenue_Ask",
                    "Low",
                    "Startup reports zero revenue while requesting funding.",
                    "Funding_Required",
                    funding
                )

    return pd.DataFrame(
        flags,
        columns=[
            "Row_ID",
            "Startup_Name",
            "Flag_Type",
            "Severity",
            "Reason",
            "Metric",
            "Value"
        ]
    )


def calculate_risk_scores(
    df,
    flags,
    config
):
    """
    Calculate 0-100 risk score.

    Higher score = higher investment risk.
    """

    risk_config = config["risk"]

    high_weight = risk_config[
        "weights"
    ]["High_Flag"]

    medium_weight = risk_config[
        "weights"
    ]["Medium_Flag"]

    low_weight = risk_config[
        "weights"
    ]["Low_Flag"]

    completeness_multiplier = risk_config[
        "completeness_penalty"
    ]["multiplier"]

    maximum_score = risk_config[
        "maximum_score"
    ]

    rows = []

    for index, row in df.iterrows():

        startup_name = row.get(
            "Startup_Name",
            f"Startup_{index}"
        )

        startup_flags = flags[
            flags["Row_ID"] == index
        ]

        high_count = int(
            (
                startup_flags["Severity"]
                == "High"
            ).sum()
        )

        medium_count = int(
            (
                startup_flags["Severity"]
                == "Medium"
            ).sum()
        )

        low_count = int(
            (
                startup_flags["Severity"]
                == "Low"
            ).sum()
        )

        base_risk = (
            high_count * high_weight
            + medium_count * medium_weight
            + low_count * low_weight
        )

        completeness = pd.to_numeric(
            row.get("Completeness"),
            errors="coerce"
        )

        if pd.notna(completeness):

            completeness_penalty = (
                (100 - completeness)
                * completeness_multiplier
            )

        else:

            completeness_penalty = 20

        risk_score = min(
            base_risk + completeness_penalty,
            maximum_score
        )

        if risk_score >= 60:

            risk_level = "High Risk"

        elif risk_score >= 35:

            risk_level = "Medium Risk"

        else:

            risk_level = "Low Risk"

        rows.append({
            "Row_ID": index,
            "Startup_Name": startup_name,
            "Risk_Score": round(
                risk_score,
                2
            ),
            "Risk_Level": risk_level,
            "High_Flags": high_count,
            "Medium_Flags": medium_count,
            "Low_Flags": low_count,
            "Total_Flags": (
                high_count
                + medium_count
                + low_count
            )
        })

    return pd.DataFrame(rows)


def assign_investment_category(
    scores_df
):
    """
    Assign an investment decision-support category.

    This is not an investment recommendation.
    """

    result = scores_df.copy()

    categories = []

    for _, row in result.iterrows():

        attractiveness = pd.to_numeric(
            row.get("Attractiveness_Score"),
            errors="coerce"
        )

        risk = pd.to_numeric(
            row.get("Risk_Score"),
            errors="coerce"
        )

        completeness = pd.to_numeric(
            row.get("Completeness"),
            errors="coerce"
        )

        high_flags = row.get(
            "High_Flags",
            0
        )

        if (
            pd.notna(risk)
            and (
                risk >= 60
                or high_flags >= 2
            )
        ):

            category = "High Risk"

        elif (
            pd.notna(completeness)
            and completeness < 50
        ):

            category = "Further Due Diligence"

        elif (
            pd.notna(attractiveness)
            and pd.notna(risk)
            and attractiveness >= 65
            and 35 <= risk < 60
        ):

            category = "Further Due Diligence"

        elif (
            pd.notna(attractiveness)
            and pd.notna(risk)
            and pd.notna(completeness)
            and attractiveness >= 70
            and risk < 35
            and completeness >= 60
        ):

            category = "High Priority"

        else:

            category = "Watchlist"

        categories.append(category)

    result["Investment_Category"] = categories

    return result


def save_risk_outputs(
    scored_df,
    flags,
    output_dir="output"
):
    """Save risk and flag outputs."""

    output_dir = Path(output_dir)

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    risk_path = (
        output_dir /
        "risk_scores.csv"
    )

    flags_path = (
        output_dir /
        "red_flags.csv"
    )

    scored_path = (
        output_dir /
        "investment_decisions.csv"
    )

    scored_df.to_csv(
        scored_path,
        index=False
    )

    flags.to_csv(
        flags_path,
        index=False
    )

    risk_only = scored_df[
        [
            "Startup_Name",
            "Risk_Score",
            "Risk_Level",
            "High_Flags",
            "Medium_Flags",
            "Low_Flags",
            "Total_Flags"
        ]
    ]

    risk_only.to_csv(
        risk_path,
        index=False
    )

    return {
        "decisions": scored_path,
        "risk_scores": risk_path,
        "red_flags": flags_path
    }


if __name__ == "__main__":

    print("VentureIQ Risk & Red-Flag Engine")
    print("--------------------------------")

    input_path = Path(
        "output/scored_startup_data.csv"
    )

    if not input_path.exists():

        print(
            f"Input file not found: {input_path}"
        )

        print(
            "Run score.py first."
        )

        raise SystemExit(1)

    df = pd.read_csv(input_path)

    config = load_risk_config()

    print(
        f"Loaded dataset: "
        f"{df.shape[0]} rows × "
        f"{df.shape[1]} columns"
    )

    # Detect red flags
    flags = detect_flags(df)

    print(
        f"Risk flags generated: "
        f"{len(flags)}"
    )

    # Calculate risk scores
    risk_scores = calculate_risk_scores(
        df,
        flags,
        config
    )

    # Merge risk scores
    result = df.merge(
        risk_scores[
            [
                "Row_ID",
                "Risk_Score",
                "Risk_Level",
                "High_Flags",
                "Medium_Flags",
                "Low_Flags",
                "Total_Flags"
            ]
        ],
        left_index=True,
        right_on="Row_ID",
        how="left"
    )

    result = result.drop(
        columns=["Row_ID"]
    )

    # Investment decision-support category
    result = assign_investment_category(
        result
    )

    outputs = save_risk_outputs(
        result,
        flags
    )

    print()
    print(
        "Risk analysis completed successfully."
    )

    print()
    print("Generated files:")

    for name, path in outputs.items():
        print(
            f"- {name}: {path}"
        )

    print()
    print(
        "VentureIQ risk engine ready."
    )
    