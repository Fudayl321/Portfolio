# Heart Disease Risk Analysis

**Industry:** Healthcare  
**Tools:** Python, SQL (SQLite), scikit-learn, Power BI  
**Dataset:** UCI Heart Disease — Cleveland Clinic Foundation  
**Source:** https://archive.ics.uci.edu/dataset/45/heart+disease  
**Kaggle mirror:** https://www.kaggle.com/datasets/ronitf/heart-disease-uci

---

## Why this dataset

I picked the UCI Heart Disease dataset because it's a real clinical dataset that's been used in actual research, not something scraped together for teaching purposes. It has 1,025 patient records with 13 clinical features — things like age, blood pressure, cholesterol, chest pain type, and max heart rate — and a binary target telling you whether the patient has heart disease or not.

It also has some real messiness to it which made the cleaning part actually worth doing.

---

## What I found when I loaded the data

Before doing anything, I just profiled the raw file to understand what I was working with.

**Missing values:**
- `trestbps` (blood pressure) — 13 nulls, about 1.3% of rows
- `chol` (cholesterol) — 15 nulls, about 1.5%
- `thalach` (max heart rate) — 12 nulls, about 1.2%

**Invalid values:**
- 8 rows where `age` was 999 — clearly a data entry error, not a real age
- 5 rows where `chol` was -1 — cholesterol can't be negative, so these are wrong

Not a disaster, but enough that you can't just throw it into a model and hope for the best.

---

## Cleaning decisions and why

**Rows with impossible age (> 120)** — dropped. 8 rows out of 1,025 is less than 1%, and there's no sensible way to guess what someone's actual age was supposed to be.

**Rows with negative cholesterol** — dropped for the same reason. -1 is not a valid cholesterol reading.

**Missing blood pressure and cholesterol** — imputed with median instead of mean. I checked the distribution first and both are right-skewed, which means the mean gets pulled up by high outliers. Median is a safer middle ground for skewed data.

**Missing max heart rate** — also median imputed. Less than 1.2% missing and it's a continuous variable with no obvious grouping I could use to get smarter about it.

After cleaning: **1,012 rows, 18 columns** (the extra 4 are label columns I added for readability — `sex_label`, `cp_label`, `target_label`, `age_group`).

---

## SQL queries

Once the data was clean, I loaded it into SQLite and ran a few queries before touching any Python visualisation. This is just how I like to work — SQL first for the aggregations, then Python for the charts.

Key queries I ran:

**Risk profile by age group and gender** — grouped by `age_group` and `sex_label`, computed disease rate, average cholesterol, and average max heart rate per group.

**Chest pain type analysis** — this one surprised me. Asymptomatic chest pain (cp=0) has the highest disease rate. Intuitively you'd expect typical angina to be the worst, but the data says otherwise. Turns out this is consistent with published clinical research — asymptomatic presentation is actually a red flag.

**Feature summary for modelling** — average ST depression, vessel count, and disease rate by exercise-induced angina group.


---

## Machine learning

I used a Random Forest classifier — 200 trees, max depth 8, trained on 80% of the data with a stratified split so both classes are represented properly in train and test.

5-fold cross-validation to check the model generalises and isn't just memorising the training set.

**Results:**
- Test AUC: 0.89+
- CV mean AUC: consistent across folds, no big variance
- Top features by importance: `ca` (number of vessels coloured), `oldpeak` (ST depression), `thal`, `cp`

The feature importance result is clinically interesting — the imaging-based features (`ca`) and exercise stress indicators (`oldpeak`, `exang`) matter more than basic demographics like age or gender, at least in this dataset.

---

## Power BI dashboard

Rather than include a `.pbix` file that won't open without the original data source path, I've written a full step-by-step guide covering every part of the build — data loading, Power Query types, all 7 DAX measures, the RiskScore calculated column, and the full report layout with visual types, field assignments, and colour codes.

**→ [Power BI Setup Guide](./05_output/PowerBI_Setup_Guide.md)**

If you follow it in Power BI Desktop it takes about 15 minutes to build.

---

## Files in this folder

```
01_data/
    heart_disease_raw.csv              raw dataset — nulls and invalid values intact

02_cleaning/
    01_clean_data.py                   full cleaning script — run this first
    heart_disease_clean.csv            clean output
    eda_overview.png                   EDA plots generated during cleaning


04_analysis/
    build_dashboard.py                 Python analysis, SQL queries, and charts

05_output/
    PowerBI_Setup_Guide.md             step-by-step Power BI build instructions
```

---

## How to run

```bash
cd 01_Heart_Disease_Risk_Analysis
python3 02_cleaning/01_clean_data.py
python3 04_analysis/build_dashboard.py
```

Then follow `05_output/PowerBI_Setup_Guide.md` in Power BI Desktop.
