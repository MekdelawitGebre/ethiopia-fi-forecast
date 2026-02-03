#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import pandas as pd
import numpy as np

# -----------------------------
# Paths
# -----------------------------
RAW = Path("data/raw")
PROCESSED = Path("data/processed")
PROCESSED.mkdir(parents=True, exist_ok=True)  # create folder if missing
LOG_FILE = Path("data_enrichment_log.md")

# -----------------------------
# Load CSVs
# -----------------------------
df_data = pd.read_csv(RAW / "ethiopia_fi_unified_data.csv", dtype=str)
df_ref  = pd.read_csv(RAW / "reference_codes.csv", dtype=str)
df_link = pd.read_csv(RAW / "impact_links.csv", dtype=str)

print("✅ Data loaded successfully")
print(df_data.head())

# -----------------------------
# Convert numeric columns
# -----------------------------
numeric_cols = ["value_numeric", "lag_months"]
for col in numeric_cols:
    if col in df_data.columns:
        df_data[col] = pd.to_numeric(df_data[col], errors="coerce")
    if col in df_link.columns:
        df_link[col] = pd.to_numeric(df_link[col], errors="coerce")

# -----------------------------
# Convert date columns
# -----------------------------
date_cols = ["observation_date", "period_start", "period_end", "collection_date"]
for col in date_cols:
    if col in df_data.columns:
        df_data[col] = pd.to_datetime(df_data[col], errors="coerce")
    if col in df_link.columns:
        df_link[col] = pd.to_datetime(df_link[col], errors="coerce")

# -----------------------------
# Validation / Integrity Checks
# -----------------------------
errors = {}
errors["duplicate_ids"] = df_data["record_id"].duplicated().sum()
errors["obs_missing_date"] = df_data.loc[df_data["record_type"]=="observation", "observation_date"].isna().sum()
errors["event_has_pillar"] = df_data.loc[df_data["record_type"]=="event", "pillar"].notna().sum()
unmatched_links = ~df_link["parent_id"].isin(df_data.loc[df_data["record_type"]=="event", "record_id"])
errors["impactlinks_bad_parent"] = unmatched_links.sum()

print("\n=== Validation Results ===")
for k,v in errors.items():
    print(f"{k}: {v}")

# -----------------------------
# Summary Statistics
# -----------------------------
print("\n=== Record Type Counts ===")
print(df_data["record_type"].value_counts(dropna=False))

print("\n=== Pillar Counts ===")
print(df_data["pillar"].value_counts(dropna=False))

print("\n=== Confidence Distribution ===")
print(df_data["confidence"].value_counts(dropna=False))

print("\n=== Observation Date Range ===")
obs_dates = df_data.loc[df_data["record_type"]=="observation", "observation_date"]
print(f"{obs_dates.min()} → {obs_dates.max()}")

print("\n=== Indicator Coverage ===")
ind_stats = df_data.loc[df_data["record_type"]=="observation"].groupby("indicator_code")["observation_date"].agg(['min','max','count'])
print(ind_stats)

print("\n=== Events List ===")
events = df_data.loc[df_data["record_type"]=="event", ["record_id","category","indicator","observation_date"]]
print(events)

print("\n=== Sample Impact Links ===")
print(df_link.head())

# -----------------------------
# Example: Add new Observation
# -----------------------------
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

# -----------------------------
# Example: Add new Event
# -----------------------------
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

# -----------------------------
# Example: Add new Impact Link
# -----------------------------
new_link = {
    "record_id": "IMP_0015",
    "parent_id": "EVT_0011",
    "record_type": "impact_link",
    "category": np.nan,
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

# -----------------------------
# Save enriched datasets
# -----------------------------
df_data.to_csv(PROCESSED / "ethiopia_fi_enriched.csv", index=False)
df_link.to_csv(PROCESSED / "impact_links_enriched.csv", index=False)

# -----------------------------
# Append enrichment log
# -----------------------------
with open(LOG_FILE, "a") as f:
    f.write("## New Data Added on 2026-02-03\n")
    f.write("### New Observation\n")
    f.write(str(new_obs) + "\n\n")
    
    f.write("### New Event\n")
    f.write(str(new_event) + "\n\n")
    
    f.write("### New Impact Link\n")
    f.write(str(new_link) + "\n\n")
    
    f.write("---\n\n")

print("\n✅ Task 1 dataset enrichment complete. Files saved to 'data/processed/' and log updated.")
