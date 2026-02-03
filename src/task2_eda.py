from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# -----------------------------
# Folder setup
# -----------------------------
PROCESSED = Path("data/processed")
PLOTS = Path("plots")
PLOTS.mkdir(exist_ok=True)

# -----------------------------
# Utility functions
# -----------------------------
def load_data():
    """Load enriched data from Task 1"""
    try:
        df_data = pd.read_csv(PROCESSED / "ethiopia_fi_enriched.csv", parse_dates=["observation_date", "collection_date"])
        df_link = pd.read_csv(PROCESSED / "impact_links_enriched.csv", parse_dates=["collection_date"])
        print("✅ Data loaded successfully")
        return df_data, df_link
    except FileNotFoundError as e:
        print("❌ File not found. Did you run Task 1?")
        raise e

def save_plot(fig, name):
    """Save plot to plots folder"""
    path = PLOTS / name
    fig.savefig(path, bbox_inches='tight', dpi=150)
    print(f"📈 Plot saved: {path}")

def summarize_data(df):
    """Print summary statistics"""
    print("\n=== Record Type Counts ===")
    print(df['record_type'].value_counts(dropna=False))
    print("\n=== Pillar Counts ===")
    print(df['pillar'].value_counts(dropna=False))
    print("\n=== Source Type Counts ===")
    print(df['source_type'].value_counts(dropna=False))

def temporal_coverage(df):
    """Heatmap of indicators by year"""
    df['year'] = df['observation_date'].dt.year
    indicator_year = df[df['record_type']=='observation'].groupby(['year','indicator_code']).size().unstack(fill_value=0)
    fig, ax = plt.subplots(figsize=(12,6))
    sns.heatmap(indicator_year.T, cmap="Blues", cbar=True, ax=ax)
    ax.set_title("Temporal Coverage of Indicators")
    ax.set_xlabel("Year")
    ax.set_ylabel("Indicator")
    save_plot(fig, "temporal_coverage.png")
    plt.close(fig)

def confidence_distribution(df):
    """Bar plot of confidence distribution"""
    fig, ax = plt.subplots(figsize=(8,5))
    sns.countplot(data=df, x='confidence', order=df['confidence'].value_counts().index, ax=ax)
    ax.set_title("Confidence Distribution")
    save_plot(fig, "confidence_distribution.png")
    plt.close(fig)

def sparse_indicators(df, threshold=2):
    """Identify indicators with few records"""
    obs_count = df[df['record_type']=='observation'].groupby('indicator_code')['value_numeric'].count()
    sparse = obs_count[obs_count <= threshold]
    print("\nIndicators with sparse coverage (<=2 records):")
    print(sparse)

def plot_access_trends(df):
    """Account ownership trajectory and growth"""
    access_obs = df[(df['record_type']=='observation') & (df['pillar']=='ACCESS') & (df['indicator_code']=='ACC_OWNERSHIP')]
    access_obs = access_obs.sort_values('observation_date')
    
    access_obs['growth_pp'] = access_obs['value_numeric'].diff()
    
    fig, ax = plt.subplots(figsize=(10,6))
    sns.lineplot(data=access_obs, x='observation_date', y='value_numeric', marker='o', ax=ax)
    ax.set_ylabel("Account Ownership (%)")
    ax.set_title("Ethiopia Account Ownership (2011-2024)")
    save_plot(fig, "access_trends.png")
    plt.close(fig)
    
    print("\n=== Access Growth per Year ===")
    print(access_obs[['observation_date','value_numeric','growth_pp']])

def plot_gender_gap(df):
    """Gender disaggregated account ownership"""
    gender_obs = df[(df['record_type']=='observation') & (df['pillar']=='GENDER')]
    if 'gender' in gender_obs.columns:
        fig, ax = plt.subplots(figsize=(10,6))
        sns.lineplot(data=gender_obs, x='year', y='value_numeric', hue='gender', marker='o', ax=ax)
        ax.set_title("Gender Gap in Account Ownership")
        save_plot(fig, "gender_gap.png")
        plt.close(fig)

def plot_usage_trends(df):
    """Digital payment adoption trends"""
    usage_obs = df[(df['record_type']=='observation') & (df['pillar']=='USAGE')]
    fig, ax = plt.subplots(figsize=(10,6))
    sns.lineplot(data=usage_obs, x='year', y='value_numeric', hue='indicator_code', marker='o', ax=ax)
    ax.set_title("Digital Payment Adoption Trends")
    save_plot(fig, "usage_trends.png")
    plt.close(fig)

def plot_infrastructure(df):
    """4G coverage and mobile penetration"""
    infra_obs = df[(df['record_type']=='observation') & (df['pillar']=='ACCESS') & df['indicator_code'].str.contains('4G|MOBILE')]
    if not infra_obs.empty:
        fig, ax = plt.subplots(figsize=(10,6))
        sns.lineplot(data=infra_obs, x='year', y='value_numeric', hue='indicator_code', marker='o', ax=ax)
        ax.set_title("Infrastructure Trends (4G coverage, mobile penetration)")
        save_plot(fig, "infrastructure_trends.png")
        plt.close(fig)

def plot_event_timeline(df):
    """Event timeline and overlay on account ownership"""
    events = df[df['record_type']=='event']
    fig, ax = plt.subplots(figsize=(12,2))
    sns.scatterplot(data=events, x='observation_date', y=[0]*len(events), hue='category', s=100, ax=ax)
    ax.set_yticks([])
    ax.set_title("Event Timeline")
    save_plot(fig, "event_timeline.png")
    plt.close(fig)
    
    # Overlay on access
    access_obs = df[(df['record_type']=='observation') & (df['pillar']=='ACCESS') & (df['indicator_code']=='ACC_OWNERSHIP')]
    fig, ax = plt.subplots(figsize=(12,6))
    sns.lineplot(data=access_obs, x='observation_date', y='value_numeric', marker='o', label="Account Ownership", ax=ax)
    for _, row in events.iterrows():
        ax.axvline(row['observation_date'], color='red', linestyle='--', alpha=0.5)
    ax.set_title("Account Ownership with Event Timeline")
    save_plot(fig, "access_with_events.png")
    plt.close(fig)

def correlation_analysis(df):
    """Correlation heatmap of numeric observations"""
    obs_wide = df[df['record_type']=='observation'].pivot_table(index='year', columns='indicator_code', values='value_numeric', aggfunc='mean')
    corr = obs_wide.corr()
    fig, ax = plt.subplots(figsize=(12,10))
    sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
    ax.set_title("Indicator Correlation Matrix")
    save_plot(fig, "indicator_correlation.png")
    plt.close(fig)

# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    df_data, df_link = load_data()
    summarize_data(df_data)
    temporal_coverage(df_data)
    confidence_distribution(df_data)
    sparse_indicators(df_data)
    plot_access_trends(df_data)
    plot_gender_gap(df_data)
    plot_usage_trends(df_data)
    plot_infrastructure(df_data)
    plot_event_timeline(df_data)
    correlation_analysis(df_data)
    print("\n✅ Task 2 EDA complete. All plots saved in 'plots/' folder.")
