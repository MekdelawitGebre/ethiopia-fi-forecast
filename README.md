
# Ethiopia Financial Inclusion Project

## Overview
This project analyzes financial inclusion in Ethiopia, focusing on access, usage, affordability, and gender gaps. It utilizes structured datasets collected from surveys, operators, regulators, and other official sources to identify trends and support future impact modeling.

The workflow is divided into two primary phases:
* **Task 1:** Data Exploration & Enrichment
* **Task 2:** Exploratory Data Analysis (EDA)

---

## File Structure

```text
ethiopia-fi-forecast/
│
├─ data/
│  ├─ raw/                      # Original raw datasets
│  └─ processed/                # Cleaned & enriched datasets
│
├─ plots/                       # All plots generated in Task 2 EDA
│  ├─ temporal_coverage.png
│  ├─ confidence_distribution.png
│  ├─ access_trends.png
│  ├─ gender_gap.png
│  ├─ usage_trends.png
│  ├─ infrastructure_trends.png
│  ├─ event_timeline.png
│  ├─ access_with_events.png
│  └─ indicator_correlation.png
│
├─ src/
│  ├─ task1_explore_and_enrich.py # Task 1: Data exploration and enrichment
│  └─ task2_eda.py                # Task 2: EDA and visualization logic
│
├─ requirements.txt
├─ .gitignore
└─ README.md

```

---

## Setup Instructions

1. **Clone the repository:**
```bash
git clone [https://github.com/MekdelawitGebre/ethiopia-fi-forecast.git](https://github.com/MekdelawitGebre/ethiopia-fi-forecast.git)
cd ethiopia-fi-forecast

```


2. **Create and activate a virtual environment:**
```bash
python3 -m venv .venv
source .venv/bin/activate

```


3. **Install dependencies:**
```bash
pip install -r requirements.txt

```


4. **Run Task 1 (Data Exploration & Enrichment):**
```bash
python3 src/task1_explore_and_enrich.py

```


* Cleans and enriches raw data.
* Validates schema and data quality.
* Saves enriched data to `data/processed/`.


5. **Run Task 2 (Exploratory Data Analysis):**
```bash
python3 src/task2_eda.py

```


* Generates visualizations for access, usage, infrastructure, and events.
* Saves all plots to the `plots/` folder.



---

## Task 1 – Data Exploration & Enrichment

This phase focuses on converting raw information into a machine-readable format while maintaining strict schema validation.

**Features:**

* Date conversion and standardization.
* **Validation Checks:**
* Duplicate ID identification.
* Date presence for all observations.
* Pillar and impact link consistency.


* Dataset summarization by `record_type`, `pillar`, and `source_type`.

**Validation Sample Output:**

```text
duplicate_ids: 0
obs_missing_date: 0
event_has_pillar: 0
impactlinks_bad_parent: 0

Record Type Counts:
observation    30
event          10
target          3

```

---

## Task 2 – Exploratory Data Analysis (EDA)

This phase visualizes the state of financial inclusion to uncover underlying patterns.

### Key Analysis Areas:

* **Temporal Coverage:** Heatmaps showing the density of indicator observations over time.
* **Access Analysis:** Account ownership trends (2011–2024), growth rates, and gender gap disparities.
* **Usage Analysis:** Digital payment trends (Mobile Money) and the gap between registered vs. active accounts.
* **Infrastructure:** Correlation between 4G coverage, mobile penetration, and financial access.
* **Event Overlay:** Mapping key milestones (Telebirr, Safaricom, M-Pesa) against ownership trends.

### Key Insights:

* **Access Growth:** Steady increase from 2014–2024, with a slight plateauing effect after 2021.
* **Gender Gap:** Persistent disparities remain, specifically within rural demographics.
* **Digital Adoption:** Mobile money is surging, but a significant "active usage" gap exists.
* **Market Impact:** Major launches (Telebirr 2021, M-Pesa 2023) show immediate correlation with usage spikes.

---

## Data Limitations

* **Sparsity:** Several indicators (e.g., `ACC_4G_COV`) have  records, making them difficult to forecast.
* **Confidence Levels:** Data quality varies between high and medium confidence levels.
* **Structural Bias:** Differences between survey-based data and operator-reported metrics.

