# src/utils.py
from pathlib import Path
import pandas as pd
import numpy as np

def load_data(processed_path: Path):
    """Load enriched CSVs from processed folder"""
    df_data_file = processed_path / "ethiopia_fi_enriched.csv"
    df_link_file = processed_path / "impact_links_enriched.csv"

    if not df_data_file.exists() or not df_link_file.exists():
        raise FileNotFoundError(f"Enriched CSVs not found in {processed_path}")

    df_data = pd.read_csv(df_data_file)
    df_link = pd.read_csv(df_link_file)

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

    return df_data, df_link

def save_outputs(df_data: pd.DataFrame, df_link: pd.DataFrame, processed_path: Path):
    """Save enriched datasets"""
    processed_path.mkdir(parents=True, exist_ok=True)
    df_data.to_csv(processed_path / "ethiopia_fi_enriched.csv", index=False)
    df_link.to_csv(processed_path / "impact_links_enriched.csv", index=False)
