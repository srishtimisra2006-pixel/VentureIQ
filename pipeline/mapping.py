from pathlib import Path
import re
import pandas as pd
import yaml
from rapidfuzz import fuzz


AUTO_MATCH_THRESHOLD = 88
SUGGESTION_THRESHOLD = 70


def normalize_name(value):
    """
    Convert a column name into a comparable normalized form.
    """
    value = str(value).strip().lower()
    value = value.replace("&", " and ")
    value = re.sub(r"[_\-\/]+", " ", value)
    value = re.sub(r"[^a-z0-9\s]", "", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def load_schema(schema_path="config/schema.yaml"):
    """
    Load the VentureIQ master schema.
    """
    schema_path = Path(schema_path)

    if not schema_path.exists():
        raise FileNotFoundError(
            f"Schema file not found: {schema_path}"
        )

    with open(schema_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def build_synonym_registry(schema):
    """
    Build a lookup table containing:
    normalized synonym -> master field
    """
    registry = {}

    for field_name, field_config in schema.get("fields", {}).items():
        synonyms = field_config.get("synonyms", [])

        # Always include the official field name.
        all_names = [field_name] + synonyms

        for name in all_names:
            normalized = normalize_name(name)

            if normalized:
                registry[normalized] = field_name

    return registry


def exact_match(column_name, registry):
    """
    Find an exact synonym match.
    """
    normalized_column = normalize_name(column_name)

    return registry.get(normalized_column)


def fuzzy_match(column_name, registry):
    """
    Find the closest synonym using fuzzy matching.
    """
    normalized_column = normalize_name(column_name)

    if not normalized_column:
        return None, 0

    best_field = None
    best_score = 0

    for synonym, field_name in registry.items():
        score = fuzz.ratio(normalized_column, synonym)

        if score > best_score:
            best_score = score
            best_field = field_name

    return best_field, best_score


def is_unsafe_mapping(source_column, target_field, schema):
    """
    Prevent mappings that could create misleading interpretations.
    """
    excluded_columns = {
        normalize_name(column)
        for column in schema.get("excluded_auto_mapping", [])
    }

    normalized_source = normalize_name(source_column)

    if normalized_source in excluded_columns:
        return True

    # Never automatically treat generic IDs as Startup_ID.
    if target_field == "Startup_ID":
        if normalized_source in {
            "id",
            "company id",
            "companyid"
        }:
            return True

    return False


def map_columns(df, schema_path="config/schema.yaml"):
    """
    Map dataset columns to VentureIQ master fields.

    Returns a DataFrame containing:
    - source column
    - mapped VentureIQ field
    - match method
    - confidence
    - status
    """

    schema = load_schema(schema_path)
    registry = build_synonym_registry(schema)

    results = []

    for column in df.columns:

        # 1. Exact match
        exact_field = exact_match(column, registry)

        if exact_field:
            if is_unsafe_mapping(column, exact_field, schema):
                results.append({
                    "Source_Column": column,
                    "VentureIQ_Field": "",
                    "Match_Method": "EXCLUDED",
                    "Confidence": 0,
                    "Status": "UNMAPPED"
                })
            else:
                results.append({
                    "Source_Column": column,
                    "VentureIQ_Field": exact_field,
                    "Match_Method": "EXACT",
                    "Confidence": 100,
                    "Status": "AUTO"
                })

            continue

        # 2. Fuzzy match
        best_field, score = fuzzy_match(column, registry)

        if best_field and score >= AUTO_MATCH_THRESHOLD:

            if is_unsafe_mapping(column, best_field, schema):
                results.append({
                    "Source_Column": column,
                    "VentureIQ_Field": "",
                    "Match_Method": "FUZZY_EXCLUDED",
                    "Confidence": round(score, 2),
                    "Status": "UNMAPPED"
                })
            else:
                results.append({
                    "Source_Column": column,
                    "VentureIQ_Field": best_field,
                    "Match_Method": "FUZZY",
                    "Confidence": round(score, 2),
                    "Status": "AUTO"
                })

        elif best_field and score >= SUGGESTION_THRESHOLD:

            results.append({
                "Source_Column": column,
                "VentureIQ_Field": best_field,
                "Match_Method": "FUZZY",
                "Confidence": round(score, 2),
                "Status": "REVIEW"
            })

        else:

            results.append({
                "Source_Column": column,
                "VentureIQ_Field": "",
                "Match_Method": "NONE",
                "Confidence": round(score, 2),
                "Status": "UNMAPPED"
            })

    return pd.DataFrame(results)


def save_mapping(mapping_df, output_path="output/column_mapping.csv"):
    """
    Save mapping results for inspection and auditing.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    mapping_df.to_csv(output_path, index=False)

    return output_path


if __name__ == "__main__":

    print("VentureIQ Column Mapping Engine")
    print("--------------------------------")

    schema = load_schema()

    print(
        f"Master fields loaded: "
        f"{len(schema.get('fields', {}))}"
    )

    print(
        f"Auto-match threshold: "
        f"{AUTO_MATCH_THRESHOLD}"
    )

    print(
        f"Review threshold: "
        f"{SUGGESTION_THRESHOLD}"
    )

    print()
    print("Mapping module loaded successfully.")
    