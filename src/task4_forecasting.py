# src/task4_forecasting.py

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from .utils import load_data, save_outputs  # Use the Task2/Task3 utils

# -----------------------------
# Paths
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_PATH = BASE_DIR / "data" / "processed"
PLOTS_PATH = BASE_DIR / "plots"
PLOTS_PATH.mkdir(exist_ok=True)

# -----------------------------
# Forecast parameters
# -----------------------------
FORECAST_YEARS = [2025, 2026, 2027]
TARGET_INDICATORS = {
    "ACC_OWNERSHIP": "Account Ownership Rate (Access)",
    "USG_DIGITAL_PAYMENT": "Digital Payment Usage"
}

# -----------------------------
# Helper functions
# -----------------------------
def build_event_features(years, impact_links, events, indicator_code):
    """Create a feature DataFrame with event impacts for the given indicator"""
    # Filter relevant links
    df_links = impact_links[impact_links["related_indicator"] == indicator_code]
    features = pd.DataFrame(0.0, index=years, columns=df_links["parent_id"].unique())
    for _, row in df_links.iterrows():
        event_year = events.loc[events["record_id"] == row["parent_id"], "observation_date"].dt.year.values
        if len(event_year) == 0:
            continue
        event_year = event_year[0]
        for y in years:
            if y >= event_year:
                features.loc[y, row["parent_id"]] += 1  # simple +1 impact per year after event
    return features

def forecast_trend(y, X_trend, event_features=None):
    """Fit linear trend (optionally with events)"""
    if event_features is not None:
        X = pd.concat([X_trend, event_features], axis=1)
    else:
        X = X_trend
    X = sm.add_constant(X)
    model = sm.OLS(y, X).fit()
    y_pred = model.predict(X)
    return y_pred, model

# -----------------------------
# Forecasting
# -----------------------------
def run_forecast():
    print("✅ Data loading...")
    df_data, df_link = load_data(PROCESSED_PATH)

    print("✅ Data loaded successfully")

    # Ensure numeric values
    for col in ["value_numeric"]:
        df_data[col] = pd.to_numeric(df_data[col], errors="coerce")

    # Extract event info
    events = df_data[df_data["record_type"] == "event"]
    impact_links = df_link.copy()
    
    # Fill missing impact columns
    for col in ["impact_magnitude", "impact_direction", "lag_months"]:
        if col not in impact_links.columns:
            print(f"⚠️ Column '{col}' not found in impact links, filling with 0")
            impact_links[col] = 0

    forecast_results = {}

    for indicator_code, indicator_name in TARGET_INDICATORS.items():
        print(f"\n--- Forecasting {indicator_name} ({indicator_code}) ---")

        # Historical data
        df_ind = df_data[df_data["indicator_code"] == indicator_code].copy()
        df_ind = df_ind.sort_values("observation_date")
        y = df_ind.set_index(df_ind["observation_date"].dt.year)["value_numeric"]

        # Trend-only model
        years = sorted(y.index.tolist() + FORECAST_YEARS)
        X_trend = pd.DataFrame({"year": years})
        X_trend = sm.add_constant(X_trend)

        # Event features
        event_feats = build_event_features(years, impact_links, events, indicator_code)

        # Align indices
        y_full = pd.Series(index=years, dtype=float)
        for year in y.index:
            y_full[year] = y.loc[year]

        # Fill missing with simple forward fill
        y_full = y_full.fillna(method="ffill").fillna(method="bfill")

        # Forecast with trend + events
        y_pred, model = forecast_trend(y_full, X_trend, event_features=event_feats)

        # Save results
        df_forecast = pd.DataFrame({
            "year": years,
            "forecast": y_pred
        })
        forecast_results[indicator_code] = df_forecast

        # Plot
        plt.figure(figsize=(8,5))
        plt.plot(years, y_full, "o-", label="Historical")
        plt.plot(years, y_pred, "s--", label="Forecast (trend+events)")
        plt.title(f"{indicator_name} Forecast")
        plt.xlabel("Year")
        plt.ylabel(indicator_name)
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plot_file = PLOTS_PATH / f"{indicator_code}_forecast.png"
        plt.savefig(plot_file)
        plt.close()
        print(f"📈 Plot saved: {plot_file}")

        # Display
        print(df_forecast)

    # Optionally save forecast table
    for key, df in forecast_results.items():
        df.to_csv(PROCESSED_PATH / f"forecast_{key}.csv", index=False)
    print("\n✅ Forecasting complete. Forecast tables saved in processed folder.")

# -----------------------------
# Run script
# -----------------------------
if __name__ == "__main__":
    run_forecast()
