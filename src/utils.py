from pathlib import Path
import pandas as pd
import numpy as np

def load_data(raw_path: Path):
    """Load CSVs from raw folder"""
    df_data = pd.read_csv(raw_path / "ethiopia_fi_unified_data.csv", dtype=str)
    df_ref = pd.read_csv(raw_path / "reference_codes.csv", dtype=str)
    df_link = pd.read_csv(raw_path / "impact_links.csv", dtype=str)
    # Convert numeric columns
    numeric_cols = ["value_numeric", "lag_months"]
    for col in numeric_cols:
        if col in df_data.columns:
            df_data[col] = pd.to_numeric(df_data[col], errors="coerce")
        if col in df_link.columns:
            df_link[col] = pd.to_numeric(df_link[col], errors="coerce")
    # Convert date columns
    date_cols = ["observation_date", "period_start", "period_end", "collection_date"]
    for col in date_cols:
        if col in df_data.columns:
            df_data[col] = pd.to_datetime(df_data[col], errors="coerce")
        if col in df_link.columns:
            df_link[col] = pd.to_datetime(df_link[col], errors="coerce")
    return df_data, df_ref, df_link

def validate_schema(df_data: pd.DataFrame, df_link: pd.DataFrame):
    """Perform integrity checks and return a dict of errors"""
    errors = {}
    errors["duplicate_ids"] = df_data["record_id"].duplicated().sum()
    errors["obs_missing_date"] = df_data.loc[df_data["record_type"]=="observation", "observation_date"].isna().sum()
    errors["event_has_pillar"] = df_data.loc[df_data["record_type"]=="event", "pillar"].notna().sum()
    unmatched_links = ~df_link["parent_id"].isin(df_data.loc[df_data["record_type"]=="event", "record_id"])
    errors["impactlinks_bad_parent"] = unmatched_links.sum()
    return errors

def enrich_data(df_data: pd.DataFrame, df_link: pd.DataFrame):
    """Add sample new observation, event, and impact link"""
    # New Observation
    new_obs = {
        "record_id": "OBS_0031",
        "record_type": "observation",
        "pillar": "ACCESS",
        "indicator": "Example Indicator",
        "indicator_code": "ACC_EXAMPLE",
        "value_numeric": 10,
        "observation_date": pd.Timestamp("2025-01-01"),
        "source_name": "Example Source",
        "source_type": "report",
        "confidence": "medium"
    }
    df_data = pd.concat([df_data, pd.DataFrame([new_obs])], ignore_index=True)

    # New Event
    new_event = {
        "record_id": "EVT_0011",
        "record_type": "event",
        "category": "policy",
        "pillar": np.nan,
        "indicator": "Example Policy Launch",
        "observation_date": pd.Timestamp("2025-06-01"),
        "source_name": "Example Source",
        "source_type": "report",
        "confidence": "high"
    }
    df_data = pd.concat([df_data, pd.DataFrame([new_event])], ignore_index=True)

    # New Impact Link
    new_link = {
        "record_id": "IMP_0015",
        "parent_id": "EVT_0011",
        "record_type": "impact_link",
        "pillar": "ACCESS",
        "related_indicator": "ACC_EXAMPLE",
        "impact_direction": "increase",
        "impact_magnitude": "medium",
        "lag_months": 6,
        "evidence_basis": "literature",
        "collected_by": "Mekdelawit",
        "collection_date": pd.Timestamp("2026-02-03"),
        "notes": "Example impact of policy"
    }
    df_link = pd.concat([df_link, pd.DataFrame([new_link])], ignore_index=True)

    return df_data, df_link

def save_outputs(df_data: pd.DataFrame, df_link: pd.DataFrame, processed_path: Path):
    """Save enriched datasets"""
    processed_path.mkdir(parents=True, exist_ok=True)
    df_data.to_csv(processed_path / "ethiopia_fi_enriched.csv", index=False)
    df_link.to_csv(processed_path / "impact_links_enriched.csv", index=False)
