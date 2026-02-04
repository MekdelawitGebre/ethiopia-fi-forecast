"""
Task 3: Event Impact Modeling (Robust Version)
- Handles missing columns in impact_links
- Builds Event-Indicator matrix with default values if needed
- Saves CSV and Heatmap
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

# -------------------------------
# Paths
# -------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"
PLOTS_DIR = BASE_DIR / "plots"
PLOTS_DIR.mkdir(exist_ok=True)

ENRICHED_DATA_FILE = DATA_DIR / "ethiopia_fi_enriched.csv"
IMPACT_LINKS_FILE = DATA_DIR / "impact_links_enriched.csv"
OUTPUT_MATRIX_FILE = DATA_DIR / "event_indicator_matrix.csv"
OUTPUT_HEATMAP_FILE = PLOTS_DIR / "event_indicator_matrix_heatmap.png"

# -------------------------------
# Load Data
# -------------------------------
df_data = pd.read_csv(ENRICHED_DATA_FILE)
df_impact = pd.read_csv(IMPACT_LINKS_FILE)
print("✅ Data loaded successfully")

# -------------------------------
# Ensure essential columns exist
# -------------------------------
if 'parent_id' not in df_impact.columns:
    raise KeyError("❌ impact_links CSV must have 'parent_id' column")
if 'record_type' not in df_impact.columns:
    df_impact['record_type'] = 'impact_link'

# Add missing columns with defaults
for col in ['indicator', 'magnitude', 'direction', 'lag']:
    if col not in df_impact.columns:
        df_impact[col] = 0
        print(f"⚠️ Column '{col}' not found in impact links, filling with 0")

# Ensure numeric
df_impact['magnitude'] = pd.to_numeric(df_impact['magnitude'], errors='coerce').fillna(0)

# -------------------------------
# Map indicators from events if missing
# -------------------------------
events = df_data[df_data['record_type'] == 'event'][['record_id', 'indicator']]
events.rename(columns={'record_id': 'parent_id'}, inplace=True)

if df_impact['indicator'].eq(0).all():
    df_impact = df_impact.merge(events, on='parent_id', how='left', suffixes=('', '_from_event'))
    df_impact['indicator'] = df_impact['indicator'].where(df_impact['indicator'] != 0, df_impact['indicator_from_event'])
    df_impact.drop(columns=['indicator_from_event'], inplace=True)

# -------------------------------
# Build Event-Indicator Matrix
# -------------------------------
matrix = pd.pivot_table(
    df_impact,
    index='parent_id',
    columns='indicator',
    values='magnitude',
    aggfunc='sum',
    fill_value=0
)

matrix.to_csv(OUTPUT_MATRIX_FILE)
print(f"✅ Event-Indicator matrix saved to {OUTPUT_MATRIX_FILE}\n")

# Preview
print("=== Event-Indicator Matrix Preview ===")
print(matrix.head())

print("\n=== Summary Stats ===")
print(f"Number of events: {matrix.shape[0]}")
print(f"Number of indicators: {matrix.shape[1]}")
print(f"Max impact value: {matrix.max().max()}")
print(f"Min impact value: {matrix.min().min()}")

# -------------------------------
# Heatmap
# -------------------------------
plt.figure(figsize=(14, 8))
sns.heatmap(matrix, annot=True, fmt=".1f", cmap="coolwarm", cbar_kws={'label': 'Impact Magnitude'})
plt.title("Event-Indicator Impact Matrix")
plt.ylabel("Event ID")
plt.xlabel("Indicator")
plt.tight_layout()
plt.savefig(OUTPUT_HEATMAP_FILE)
plt.close()
print(f"📈 Heatmap saved: {OUTPUT_HEATMAP_FILE}")
