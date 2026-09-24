# 🍔 Online Food Delivery — Dataset Analysis

> **Data Analytics Project** · Python · Pandas · Plotly · Streamlit

An end-to-end data analytics project that loads, cleans, analyses, and visualises a real-world online food delivery customer survey dataset from Bangalore, India. A fully interactive **Streamlit dashboard** presents all findings across 7 dedicated tabs.

---

## 📁 Project Structure

```
food_delivery_analysis/
├── app.py                              ← Streamlit dashboard (7 tabs, 30+ charts)
├── data_loader.py                      ← Data loading, cleaning & helper functions
├── requirements.txt                    ← Python dependencies
└── README.md                           ← This file

online food delivery dataset.csv        ← Raw dataset (place in project root)
```

---

## 📊 Dataset

| Property | Value |
|---|---|
| **Source** | Online food delivery customer survey — Bangalore, India |
| **Raw rows** | 388 records |
| **Clean rows** | 285 (after removing 103 exact duplicates) |
| **Columns** | 13 meaningful features |

### Column Reference

| Column | Type | Description |
|---|---|---|
| `Age` | Numeric | Customer age in years |
| `Gender` | Categorical | Male / Female |
| `Marital Status` | Categorical | Single / Married / Prefer not to say |
| `Occupation` | Categorical | Student / Employee / Self Employed / House wife |
| `Monthly Income` | Ordered categorical | No Income → Below Rs.10,000 → 10,001–25,000 → 25,001–50,000 → More than 50,000 |
| `Educational Qualifications` | Ordered categorical | Uneducated → School → Graduate → Post Graduate → Ph.D |
| `Family size` | Numeric | Number of household members |
| `Customer Type` | Categorical | New / Regular / Frequent |
| `latitude` / `longitude` | Numeric | GPS coordinates |
| `Pin code` | String | Postal zone |
| `Output` | Binary | Did the customer order online? (Yes / No) |
| `Feedback` | Binary | Customer sentiment (Positive / Negative) |

---

## 🧹 Data Cleaning Steps

1. **Drop unnamed columns** — Removed trailing empty column caused by CSV trailing-comma artefact.
2. **Strip whitespace** — All string columns trimmed; `"Negative "` normalised to `"Negative"`.
3. **Remove duplicates** — 103 exact duplicate rows removed (388 → 285 records).
4. **Fix typos** — `"Self Employeed"` corrected to `"Self Employed"` across 38 rows.
5. **Enforce ordered categoricals** — `Monthly Income` and `Educational Qualifications` set as ordered categoricals for correct chart sorting.
6. **Derive new columns**:
   - `Age Group` — binned: `≤20 / 21–25 / 26–30 / 31–40 / 40+`
   - `Orders Online` — binary `0/1` from `Output`
   - `Positive Feedback` — binary `0/1` from `Feedback`

**Final state: 285 rows × 16 columns — zero missing values — zero errors.**

---

## 🚀 Getting Started

### 1 · Prerequisites

- Python **3.9+**
- pip

### 2 · Install dependencies

```bash
pip install -r food_delivery_analysis/requirements.txt
```

### 3 · Run the dashboard

```bash
streamlit run food_delivery_analysis/app.py
```

The app opens at `http://localhost:8501` in your browser.

> **Dataset location** — The app automatically searches for `online food delivery dataset.csv` in the project root (one level above `food_delivery_analysis/`). If it is not found, a file-uploader widget appears in the browser so you can upload it manually.

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `streamlit` | Interactive web dashboard |
| `pandas` | Data loading, cleaning, aggregation |
| `numpy` | Numerical operations |
| `plotly` | Interactive charts (30+ visualisations) |
| `matplotlib` / `seaborn` | Supporting chart utilities |
| `scipy` | Statistical helpers |

---

## 🖥️ Dashboard Tabs

The Streamlit app is organised into **7 tabs**, all responsive to the **sidebar filters** (Gender, Occupation, Monthly Income, Marital Status, Age Range).

### Tab 1 — 📊 Overview
- 5 KPI metric cards: Total Customers, Order Online %, Positive Feedback %, Average Age, Average Family Size
- Online ordering rate donut chart
- Feedback distribution donut chart
- Collapsible **Data Quality Report** (raw vs clean row counts, missing value check)
- Collapsible **clean dataset preview**

### Tab 2 — 👥 Demographics
- Gender bar chart with percentages
- Marital status pie chart
- Age histogram (continuous distribution)
- Age group bar chart
- Occupation horizontal bar chart
- Education level bar chart
- Monthly income funnel chart
- Family size bar chart
- Full demographic summary table

### Tab 3 — 🛒 Ordering Behaviour
- Customer type pie chart
- Ordering rate by gender (stacked bar)
- Ordering rate by occupation (horizontal bar)
- Ordering rate by income bracket (line chart)
- Customer type by age group (100% stacked bar)
- Ordering rate by education (bar)
- **Heatmap**: Income × Marital Status ordering rate

### Tab 4 — 💬 Feedback Analysis
- Feedback by gender (grouped bar)
- Positive feedback rate by occupation (horizontal bar)
- Feedback vs online ordering decision (stacked bar)
- Positive feedback rate by income (line chart)
- Feedback by age group (grouped bar)
- Feedback by marital status (grouped bar)
- **Heatmap**: Feedback distribution by education level

### Tab 5 — 💰 Income & Family Insights
- Income by gender (stacked bar)
- Occupation × income count heatmap
- Family size vs ordering rate (bubble/scatter)
- Family size by marital status (box plot with jitter)
- Income distribution across education levels (100% stacked bar)

### Tab 6 — 🔀 Comparative Analysis
- **Radar chart**: demographic profile of orderers vs non-orderers (5 normalised dimensions)
- Age distribution overlay (orderers vs non-orderers)
- Customer type × feedback (grouped bar)
- **Sunburst**: Occupation → Income → Ordering Decision drill-down

### Tab 7 — 💡 Business Insights & Recommendations
- 8 insight cards with backing statistics and concrete action items
- Full segment summary table (by occupation): count, %, avg age, ordering rate, feedback rate, family size

---

## 📈 Key Findings

| Metric | Value |
|---|---|
| Overall online ordering rate | **76.1%** |
| Overall positive feedback rate | **81.1%** |
| Average customer age | **24.7 years** |
| Dominant occupation | **Student (50.5%)** |
| Dominant education | **Post Graduate (63.5%)** |
| Dominant income bracket | **No Income (38.6%)** |
| Most common customer type | **Frequent (49.8%)** |
| Feedback → ordering correlation | Positive: **88.3%** order online vs Negative: **50.0%** |

---

## 💡 Business Recommendations

1. **High digital adoption** — Focus on retention and loyalty, not acquisition.
2. **Target students** — Combo deals, referral programmes, campus tie-ups.
3. **Strong sentiment** — Leverage positive reviews in marketing; audit negative feedback sources.
4. **Price-sensitive market** — Micro-bundles, free delivery thresholds, UPI/wallet offers.
5. **Family meal opportunity** — Group order discounts for 3–5 member households.
6. **Gamify frequent customers** — Tiered loyalty with streaks, badges, and exclusive deals.
7. **Feedback drives orders** — Positive feedback customers are 2× more likely to order; prioritise service quality.
8. **Geographic expansion** — Dataset is Bangalore-centric; expand to Tier-2 cities for growth.

---

## 🗂️ Module Reference

### `data_loader.py`

| Symbol | Description |
|---|---|
| `load_data(filepath)` | Load CSV, apply all 6 cleaning steps, return enriched DataFrame |
| `summary_stats(df)` | Return dict of 8 high-level KPI values |
| `pct_series(series)` | Return count + percentage DataFrame for a column |
| `crosstab_pct(df, row, col)` | Return raw crosstab + row-normalised % crosstab |
| `INCOME_ORDER` | Ordered list of 5 income bracket labels |
| `EDU_ORDER` | Ordered list of 5 education level labels |

### `app.py`

| Function | Description |
|---|---|
| `get_data(filepath)` | Cached wrapper around `load_data` |
| `render_sidebar(df)` | Renders sidebar filters; returns filtered DataFrame |
| `tab_overview(df, raw_df)` | Renders Tab 1 |
| `tab_demographics(df)` | Renders Tab 2 |
| `tab_ordering(df)` | Renders Tab 3 |
| `tab_feedback(df)` | Renders Tab 4 |
| `tab_income_family(df)` | Renders Tab 5 |
| `tab_comparative(df)` | Renders Tab 6 |
| `tab_insights(df)` | Renders Tab 7 |

---

## 📸 Screenshots

> Run `streamlit run food_delivery_analysis/app.py` to see the live dashboard.

---

## 📝 License

This project was created as part of an **IBM Bob Internship** data analytics exercise.  
Dataset is a public survey dataset for educational use.

---

*Built with Python · Pandas · Plotly · Streamlit*
