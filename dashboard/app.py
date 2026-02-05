# dashboard/app.py


from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- Paths (adjust if you moved processed data) ---
BASE = Path(__file__).resolve().parent.parent
DATA_DIR = BASE / "data" / "processed"
PLOTS_DIR = BASE / "plots"

# Files (expected from Tasks 1-4)
ENRICHED_CSV = DATA_DIR / "ethiopia_fi_enriched.csv"
IMPACT_LINKS_CSV = DATA_DIR / "impact_links_enriched.csv"
EVENT_IND_MATRIX_CSV = DATA_DIR / "event_indicator_matrix.csv"
FORECAST_ACC_CSV = DATA_DIR / "forecast_ACC_OWNERSHIP.csv"
FORECAST_USG_CSV = DATA_DIR / "forecast_USG_DIGITAL_PAYMENT.csv"

# --- Helpers ---
@st.cache_data(ttl=600)
def load_csv(path: Path):
    if not path.exists():
        return None
    return pd.read_csv(path)

def safe_date(col):
    try:
        return pd.to_datetime(col, errors="coerce")
    except Exception:
        return col

# Load data
df = load_csv(ENRICHED_CSV)
df_links = load_csv(IMPACT_LINKS_CSV)
df_matrix = load_csv(EVENT_IND_MATRIX_CSV)
df_f_acc = load_csv(FORECAST_ACC_CSV)
df_f_usg = load_csv(FORECAST_USG_CSV)

# App layout
st.set_page_config(page_title="Ethiopia Financial Inclusion Dashboard", layout="wide", initial_sidebar_state="expanded")
st.title("🇪🇹 Ethiopia Financial Inclusion — Dashboard")
st.markdown("Interactive dashboard: trends, event impacts, and forecasts (2025–2027).")

# Sidebar
st.sidebar.header("Controls")
indicator_choice = st.sidebar.selectbox("Select indicator / view", ["Account Ownership (ACCESS)", "Digital Payment Usage (USAGE)", "Event-impact matrix", "All data / downloads"])
year_range = st.sidebar.slider("Year range (for plots)", 2011, 2027, (2014, 2027))
show_events = st.sidebar.checkbox("Overlay events on time series", value=True)
scenario_choice = st.sidebar.selectbox("Forecast scenario (if available)", ["Base", "Optimistic (+50%)", "Pessimistic (-50%)"])

st.sidebar.markdown("---")
st.sidebar.markdown("Data source: enriched CSVs (data/processed) and impact links.")
st.sidebar.markdown("Run: `streamlit run dashboard/app.py`")

# Overview KPIs
if indicator_choice in ["Account Ownership (ACCESS)", "Digital Payment Usage (USAGE)"]:
    col1, col2, col3, col4 = st.columns(4)
    # Current / most recent values
    if df is not None:
        # pick most recent observation per indicator
        recent = df.dropna(subset=["observation_date"])
        recent["observation_date"] = safe_date(recent["observation_date"])
        recent["year"] = recent["observation_date"].dt.year
        # ACCESS
        acc = recent[recent["indicator_code"] == "ACC_OWNERSHIP"]
        usg = recent[recent["indicator_code"].str.contains("USG") | (recent["pillar"]=="USAGE")]
        acc_val = acc.sort_values("observation_date").tail(1)["value_numeric"].values
        usg_val = usg.sort_values("observation_date").tail(1)["value_numeric"].values
        acc_text = f"{acc_val[0]:.1f}%" if len(acc_val) else "n/a"
        usg_text = f"{usg_val[0]:.1f}%" if len(usg_val) else "n/a"
    else:
        acc_text = usg_text = "n/a"

    col1.metric("Latest Account Ownership", acc_text)
    col2.metric("Latest Digital Payment Usage", usg_text)
    # P2P/ATM crossover if available
    crossover = df[df["indicator_code"]=="USG_CROSSOVER"]
    if not crossover.empty:
        cross_val = crossover.sort_values("observation_date").tail(1)["value_numeric"].values[0]
        col3.metric("P2P/ATM Crossover", f"{cross_val:.1f}")
    else:
        col3.metric("P2P/ATM Crossover", "n/a")
    # Growth highlight (last survey jump)
    if len(acc) >= 2:
        last_two = acc.sort_values("observation_date").tail(2)["value_numeric"].values
        growth = last_two[-1] - last_two[-2]
        col4.metric("Recent growth (pp)", f"{growth:.1f}%")
    else:
        col4.metric("Recent growth (pp)", "n/a")

# Content area
if indicator_choice == "Account Ownership (ACCESS)":
    st.header("Account Ownership — Historical and Forecast (ACCESS)")
    # Time series historical
    if df is None:
        st.warning("Enriched data not found at: " + str(ENRICHED_CSV))
    else:
        hist = df[df["record_type"]=="observation"]
        hist["observation_date"] = safe_date(hist["observation_date"])
        hist["year"] = hist["observation_date"].dt.year
        acc = hist[hist["indicator_code"]=="ACC_OWNERSHIP"].copy()
        acc = acc.dropna(subset=["value_numeric"])
        if acc.empty:
            st.info("No account ownership observations available.")
        else:
            acc_plot = acc[(acc["year"]>=year_range[0]) & (acc["year"]<=year_range[1])]
            fig = px.line(acc_plot, x="year", y="value_numeric", markers=True, title="Account Ownership (survey points)")
            fig.update_yaxes(title="Account Ownership (%)")
            st.plotly_chart(fig, use_container_width=True)

            # overlay events
            if show_events and df_links is not None:
                events = df[df["record_type"]=="event"].copy()
                events["observation_date"] = safe_date(events["observation_date"])
                events["year"] = events["observation_date"].dt.year
                events_plot = events[(events["year"]>=year_range[0]) & (events["year"]<=year_range[1])]
                if not events_plot.empty:
                    for _, r in events_plot.iterrows():
                        st.markdown(f"**Event** {r.get('record_id','')}: {r.get('indicator','')} — {r.get('category','')}, {r.get('observation_date','')}")
                    # show timeline
                    ev_fig = px.scatter(events_plot, x="year", y=[0]*len(events_plot), text="indicator", title="Event Timeline (years)")
                    st.plotly_chart(ev_fig, use_container_width=True)

            # Forecast panel
            if df_f_acc is not None:
                st.subheader("Forecast (2025–2027)")
                f = df_f_acc.copy()
                if "year" in f.columns:
                    figf = go.Figure()
                    figf.add_trace(go.Scatter(x=f["year"], y=f["forecast"], mode="lines+markers", name="Forecast"))
                    figf.update_layout(title="Account Ownership Forecast (2025–2027)", xaxis_title="Year", yaxis_title="%")
                    st.plotly_chart(figf, use_container_width=True)
                else:
                    st.info("Forecast file found but unexpected format.")

elif indicator_choice == "Digital Payment Usage (USAGE)":
    st.header("Digital Payment Usage — Historical and Forecast (USAGE)")
    if df is None:
        st.warning("Enriched data not found at: " + str(ENRICHED_CSV))
    else:
        hist = df[df["record_type"]=="observation"]
        hist["observation_date"] = safe_date(hist["observation_date"])
        hist["year"] = hist["observation_date"].dt.year
        usage = hist[hist["pillar"]=="USAGE"].copy()
        usage = usage.dropna(subset=["value_numeric"])
        if usage.empty:
            st.info("No usage observations available.")
        else:
            usage_plot = usage[(usage["year"]>=year_range[0]) & (usage["year"]<=year_range[1])]
            fig = px.line(usage_plot, x="year", y="value_numeric", color="indicator_code", markers=True, title="Digital Payment Usage Trends")
            fig.update_yaxes(title="Value")
            st.plotly_chart(fig, use_container_width=True)

            # Forecast
            if df_f_usg is not None:
                st.subheader("Forecast (2025–2027)")
                f = df_f_usg.copy()
                if "year" in f.columns:
                    figf = go.Figure()
                    figf.add_trace(go.Scatter(x=f["year"], y=f["forecast"], mode="lines+markers", name="Forecast"))
                    figf.update_layout(title="Digital Payment Usage Forecast (2025–2027)", xaxis_title="Year", yaxis_title="%")
                    st.plotly_chart(figf, use_container_width=True)

elif indicator_choice == "Event-impact matrix":
    st.header("Event → Indicator Impact Matrix")
    if df_matrix is None:
        st.warning("Event-Indicator matrix not found: " + str(EVENT_IND_MATRIX_CSV))
    else:
        # show heatmap with plotly
        mat = df_matrix.fillna(0)
        # ensure numeric where possible
        mat_numeric = mat.select_dtypes(include=[np.number])
        if mat_numeric.shape[0] == 0:
            # fallback: show raw table
            st.dataframe(mat)
        else:
            fig = px.imshow(mat_numeric.values,
                            x=mat_numeric.columns,
                            y=mat_numeric.index,
                            color_continuous_scale="RdBu",
                            labels=dict(x="Indicator", y="Event", color="Impact"))
            fig.update_layout(height=700, width=1000, title="Event-Indicator Impact Matrix")
            st.plotly_chart(fig, use_container_width=True)

elif indicator_choice == "All data / downloads":
    st.header("Raw and Processed Data — Download")
    st.markdown("Download the enriched CSVs and forecasts used in the analysis.")
    if ENRICHED_CSV.exists():
        st.download_button("Download enriched dataset (ethiopia_fi_enriched.csv)", data=ENRICHED_CSV.read_bytes(), file_name="ethiopia_fi_enriched.csv")
    if IMPACT_LINKS_CSV.exists():
        st.download_button("Download impact links (impact_links_enriched.csv)", data=IMPACT_LINKS_CSV.read_bytes(), file_name="impact_links_enriched.csv")
    if EVENT_IND_MATRIX_CSV.exists():
        st.download_button("Download event-indicator matrix (event_indicator_matrix.csv)", data=EVENT_IND_MATRIX_CSV.read_bytes(), file_name="event_indicator_matrix.csv")
    if FORECAST_ACC_CSV.exists():
        st.download_button("Download account forecast", data=FORECAST_ACC_CSV.read_bytes(), file_name="forecast_ACC_OWNERSHIP.csv")
    if FORECAST_USG_CSV.exists():
        st.download_button("Download usage forecast", data=FORECAST_USG_CSV.read_bytes(), file_name="forecast_USG_DIGITAL_PAYMENT.csv")

st.markdown("---")
st.caption("Dashboard built from project artifacts (data/processed/). Customize the code in dashboard/app.py to add more charts or change layout.")
