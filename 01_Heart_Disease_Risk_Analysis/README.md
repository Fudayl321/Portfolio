# Heart Disease Risk Analysis

**Industry:** Healthcare  
**Tools:** Python, pandas, scikit-learn, Power BI  
**Dataset:** UCI Heart Disease — Cleveland Clinic Foundation  
**Source:** https://archive.ics.uci.edu/dataset/45/heart+disease  
**Kaggle mirror:** https://www.kaggle.com/datasets/ronitf/heart-disease-uci

---

## Workflow

```
01_data/heart_disease_raw.csv
  → 02_cleaning/01_clean_data.py        (Python — fix nulls, drop invalid rows, add labels)
  → 02_cleaning/heart_disease_clean.csv
  → 04_analysis/build_dashboard.py      (Python — aggregations, ML, EDA charts)
  → 05_output/PowerBI_Setup_Guide.md    (load clean CSV into Power BI and build dashboard)
```

---

## Why this dataset

The UCI Heart Disease dataset has 1,025 patient records with 13 clinical features — age, blood pressure, cholesterol, chest pain type, max heart rate, and others — and a binary target for whether the patient has heart disease. It's been used in published research, which means the findings are verifiable, not just interesting-looking numbers.

It also has real data quality issues which made the cleaning step worth doing properly.

---

## What I found in the raw data

**Missing values:**
- `trestbps` (resting blood pressure) — 13 nulls
- `chol` (cholesterol) — 15 nulls
- `thalach` (max heart rate) — 12 nulls

**Invalid values:**
- 8 rows where `age` = 999 — data entry error
- 5 rows where `chol` = -1 — physically impossible

---

## Cleaning decisions

**Invalid age and cholesterol rows** — dropped. Both are physically impossible values and there's no way to guess what they should be. Together they're less than 1.3% of the dataset so the loss is acceptable.

**Missing blood pressure and cholesterol** — imputed with the median per column. I checked both distributions first — they're right-skewed, which means the mean gets pulled upward by high values. Median is a better central estimate for skewed data.

**Missing max heart rate** — global median. Less than 1.2% missing and no meaningful subgroup to impute by.

After cleaning: **1,012 rows, 18 columns.** The extra columns beyond the original 14 are readable label versions of the coded fields (`sex_label`, `cp_label`, `target_label`) and an `age_group` bin column.

---

## Analysis

Once the data was clean the Python script does three things:

**Aggregations** — groupby summaries by age group and gender, by chest pain type, and by exercise angina group. These feed directly into the Power BI visuals.

**Machine learning** — Random Forest classifier (200 trees, max depth 8, stratified 80/20 split, 5-fold cross-validation). The model is used to extract feature importance, which tells you which clinical indicators actually drive the prediction rather than just showing which ones correlate.

**Results:**
- Test AUC: 0.89+
- CV mean AUC: stable across all 5 folds
- Top features: `ca` (vessels coloured by fluoroscopy), `oldpeak` (ST depression), `thal`, `cp`

One finding worth noting: asymptomatic chest pain (`cp=0`) has the highest disease rate, which is counterintuitive but consistent with published clinical literature. Asymptomatic presentation is a known red flag, not a sign of lower risk.

---

## Power BI dashboard

The clean CSV loads directly into Power BI Desktop — no database step in between. The setup guide covers everything: Power Query column types, all 7 DAX measures, a calculated RiskScore column, and the full report layout.

**→ [Power BI Setup Guide](./05_output/PowerBI_Setup_Guide.md)**

DAX measures included:
- Total Patients, Disease Cases, Disease Rate %
- Avg Cholesterol, Avg Max HR, Avg Age
- High Risk Patients (RiskScore ≥ 5)

---

## Files

```
01_data/
    heart_disease_raw.csv          raw dataset — nulls and invalid values intact

02_cleaning/
    01_clean_data.py               cleaning script — run this first
    heart_disease_clean.csv        clean output — load this into Power BI
    eda_overview.png               EDA plots generated during cleaning

04_analysis/
    build_dashboard.py             aggregations, ML, and chart generation

05_output/
    PowerBI_Setup_Guide.md         full Power BI build instructions
```

---

## How to run

```bash
cd 01_Heart_Disease_Risk_Analysis
python3 02_cleaning/01_clean_data.py
python3 04_analysis/build_dashboard.py
```

Then open Power BI Desktop and follow `05_output/PowerBI_Setup_Guide.md`.
