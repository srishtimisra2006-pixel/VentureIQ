from pathlib import Path
import pandas as pd
import yaml


def load_scoring_config(config_path="config/scoring.yaml"):
    """Load VentureIQ scoring configuration."""

    config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(
            f"Scoring configuration not found: {config_path}"
        )

    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def calculate_metric_score(value, poor, ok, strong):
    """
    Convert a metric value into a 0-100 score
    using piecewise linear interpolation.

    Supports both:
    - higher-is-better metrics
    - lower-is-better metrics
    """

    if pd.isna(value):
        return None

    try:
        value = float(value)
        poor = float(poor)
        ok = float(ok)
        strong = float(strong)
    except (TypeError, ValueError):
        return None

    # Higher is better
    if poor < strong:

        if value <= poor:
            return 0.0

        if value >= strong:
            return 100.0

        if value <= ok:
            denominator = ok - poor

            if denominator == 0:
                return 50.0

            return (
                (value - poor) / denominator
            ) * 50

        denominator = strong - ok

        if denominator == 0:
            return 100.0

        return 50 + (
            (value - ok) / denominator
        ) * 50

    # Lower is better
    if poor > strong:

        if value >= poor:
            return 0.0

        if value <= strong:
            return 100.0

        if value >= ok:
            denominator = poor - ok

            if denominator == 0:
                return 50.0

            return (
                (poor - value) / denominator
            ) * 50

        denominator = ok - strong

        if denominator == 0:
            return 100.0

        return 50 + (
            (ok - value) / denominator
        ) * 50

    return None


def score_metrics(df, config):
    """Calculate individual metric scores."""

    anchors = config["scoring"]["anchors"]

    rows = []

    for index, row in df.iterrows():

        startup_name = row.get(
            "Startup_Name",
            f"Startup_{index}"
        )

        for metric, anchor in anchors.items():

            if metric not in df.columns:
                continue

            value = row.get(metric)

            score = calculate_metric_score(
                value=value,
                poor=anchor["poor"],
                ok=anchor["ok"],
                strong=anchor["strong"]
            )

            if score is None:
                continue

            rows.append({
                "Row_ID": index,
                "Startup_Name": startup_name,
                "Metric": metric,
                "Raw_Value": value,
                "Metric_Score": round(score, 2)
            })

    return pd.DataFrame(
        rows,
        columns=[
            "Row_ID",
            "Startup_Name",
            "Metric",
            "Raw_Value",
            "Metric_Score"
        ]
    )


def calculate_category_scores(
    df,
    metric_scores,
    config
):
    """Calculate category-level scores."""

    categories = config["scoring"]["categories"]

    rows = []

    for index, row in df.iterrows():

        startup_name = row.get(
            "Startup_Name",
            f"Startup_{index}"
        )

        startup_metric_scores = metric_scores[
            metric_scores["Row_ID"] == index
        ]

        for category, settings in categories.items():

            category_metrics = settings.get(
                "metrics",
                []
            )

            available = startup_metric_scores[
                startup_metric_scores[
                    "Metric"
                ].isin(category_metrics)
            ]

            if available.empty:
                continue

            category_score = available[
                "Metric_Score"
            ].mean()

            rows.append({
                "Row_ID": index,
                "Startup_Name": startup_name,
                "Category": category,
                "Category_Score": round(
                    category_score,
                    2
                ),
                "Weight": settings["weight"],
                "Scored_Metrics": len(available)
            })

    return pd.DataFrame(
        rows,
        columns=[
            "Row_ID",
            "Startup_Name",
            "Category",
            "Category_Score",
            "Weight",
            "Scored_Metrics"
        ]
    )


def calculate_overall_scores(
    df,
    metric_scores,
    category_scores,
    config
):
    """
    Calculate investment attractiveness,
    completeness and scoring coverage.
    """

    scoring = config["scoring"]

    minimum_metrics = scoring[
        "minimum_gate"
    ]["minimum_scorable_metrics"]

    minimum_categories = scoring[
        "minimum_gate"
    ]["minimum_categories"]

    minimum_weight_coverage = scoring[
        "minimum_overall_weight_coverage"
    ]

    anchors = scoring["anchors"]
    categories = scoring["categories"]

    total_anchor_metrics = len(anchors)

    total_possible_weight = sum(
        category["weight"]
        for category in categories.values()
    )

    rows = []

    for index, row in df.iterrows():

        startup_name = row.get(
            "Startup_Name",
            f"Startup_{index}"
        )

        startup_metrics = metric_scores[
            metric_scores["Row_ID"] == index
        ]

        startup_categories = category_scores[
            category_scores["Row_ID"] == index
        ]

        metric_count = len(
            startup_metrics["Metric"].unique()
        )

        category_count = len(
            startup_categories["Category"].unique()
        )

        scored_weight = startup_categories[
            "Weight"
        ].sum()

        weight_coverage = (
            scored_weight
            / total_possible_weight
            * 100
            if total_possible_weight
            else 0
        )

        completeness = (
            metric_count
            / total_anchor_metrics
            * 100
            if total_anchor_metrics
            else 0
        )

        overall_score = pd.NA

        if (
            metric_count >= minimum_metrics
            and category_count >= minimum_categories
            and weight_coverage
            >= minimum_weight_coverage
            and scored_weight > 0
        ):

            weighted_total = (
                startup_categories[
                    "Category_Score"
                ]
                * startup_categories["Weight"]
            ).sum()

            overall_score = round(
                weighted_total / scored_weight,
                2
            )

        rows.append({
            "Row_ID": index,
            "Startup_Name": startup_name,
            "Attractiveness_Score": overall_score,
            "Scorable_Metrics": metric_count,
            "Scored_Categories": category_count,
            "Weight_Coverage": round(
                weight_coverage,
                2
            ),
            "Completeness": round(
                completeness,
                2
            )
        })

    return pd.DataFrame(rows)


def save_outputs(
    scored_df,
    metric_scores,
    category_scores,
    overall_scores,
    output_dir="output"
):
    """Save VentureIQ scoring outputs."""

    output_dir = Path(output_dir)

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    scored_path = (
        output_dir /
        "scored_startup_data.csv"
    )

    metric_path = (
        output_dir /
        "metric_scores.csv"
    )

    category_path = (
        output_dir /
        "category_scores.csv"
    )

    coverage_path = (
        output_dir /
        "metric_coverage.csv"
    )

    scored_df.to_csv(
        scored_path,
        index=False
    )

    metric_scores.to_csv(
        metric_path,
        index=False
    )

    category_scores.to_csv(
        category_path,
        index=False
    )

    overall_scores[
        [
            "Startup_Name",
            "Scorable_Metrics",
            "Scored_Categories",
            "Weight_Coverage",
            "Completeness"
        ]
    ].to_csv(
        coverage_path,
        index=False
    )

    return {
        "scored": scored_path,
        "metrics": metric_path,
        "categories": category_path,
        "coverage": coverage_path
    }


def run_scoring(
    input_path="output/derived_startup_data.csv",
    config_path="config/scoring.yaml"
):
    """Run the complete VentureIQ scoring engine."""

    input_path = Path(input_path)

    if not input_path.exists():
        raise FileNotFoundError(
            f"Input file not found: {input_path}. "
            "Run derive.py first."
        )

    df = pd.read_csv(input_path)

    config = load_scoring_config(
        config_path
    )

    metric_scores = score_metrics(
        df,
        config
    )

    category_scores = calculate_category_scores(
        df,
        metric_scores,
        config
    )

    overall_scores = calculate_overall_scores(
        df,
        metric_scores,
        category_scores,
        config
    )

    scored_df = df.copy()

    scored_df = scored_df.merge(
        overall_scores[
            [
                "Row_ID",
                "Attractiveness_Score",
                "Scorable_Metrics",
                "Scored_Categories",
                "Weight_Coverage",
                "Completeness"
            ]
        ],
        left_index=True,
        right_on="Row_ID",
        how="left"
    )

    scored_df = scored_df.drop(
        columns=["Row_ID"]
    )

    outputs = save_outputs(
        scored_df,
        metric_scores,
        category_scores,
        overall_scores
    )

    return {
        "data": scored_df,
        "metric_scores": metric_scores,
        "category_scores": category_scores,
        "overall_scores": overall_scores,
        "outputs": outputs
    }


if __name__ == "__main__":

    print(
        "VentureIQ Investment Scoring Engine"
    )
    print(
        "-----------------------------------"
    )

    try:

        result = run_scoring()

        print(
            f"Startups processed: "
            f"{len(result['data'])}"
        )

        print(
            f"Metric scores generated: "
            f"{len(result['metric_scores'])}"
        )

        print(
            f"Category scores generated: "
            f"{len(result['category_scores'])}"
        )

        scored_count = int(
            result["data"][
                "Attractiveness_Score"
            ].notna().sum()
        )

        print(
            f"Startups receiving overall score: "
            f"{scored_count}"
        )

        print()
        print(
            "Scoring completed successfully."
        )

        print()
        print("Generated files:")

        for name, path in (
            result["outputs"].items()
        ):
            print(
                f"- {name}: {path}"
            )

    except Exception as error:

        print()
        print(
            f"ERROR: {error}"
        )

        raise