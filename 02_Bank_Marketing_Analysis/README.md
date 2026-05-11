# Bank Marketing Campaign Analysis

**Industry:** Finance / Banking  
**Tools:** Python, pandas, Excel (openpyxl)  
**Dataset:** UCI Bank Marketing — Portuguese bank telemarketing campaign  
**Source:** https://archive.ics.uci.edu/dataset/222/bank+marketing  
**Kaggle mirror:** https://www.kaggle.com/datasets/henriqueyamahata/bank-marketing

---

## Workflow

```
01_data/bank_marketing_raw.csv
  → 02_cleaning/build_all.py           (Python — clean, aggregate with pandas, build Excel)
  → 02_cleaning/bank_marketing_clean.csv
  → 05_output/bank_marketing_dashboard.xlsx    (open in Excel or Google Sheets)
```

The same script handles cleaning, aggregation, and Excel generation in one run. The clean CSV is also saved separately in case you want to load it into Power BI or do further analysis.

---

## Why this dataset

This covers a real telemarketing campaign run by a Portuguese bank between 2008 and 2010. The target is whether a client subscribed to a term deposit — and the subscription rate is low, around 16-17%, which is realistic. Most campaigns don't convert well, so the analysis is more useful than a dataset where the outcome is 50/50.

The dataset also has an economic context built in — Euribor rates, employment variation, consumer confidence — which means you can look at whether macro conditions affected conversion alongside client-level factors.

---

## What I found in the raw data

**Duplicates:** 25 exact duplicate rows — removed completely.

**Nulls:**
- `age` — 60 nulls
- `duration` — 30 nulls

**Categorical issues:**
- `job` had 65 entries coded as `'unknown'`

**Data leakage flag:** the `duration` column (call length in seconds) is leakage — you only know how long the call was after it ends, which means after you already know the outcome. It's kept for EDA but flagged clearly and excluded from any modelling.

---

## Cleaning decisions

**Duplicates** — dropped. No reason to keep exact copies.

**Age nulls** — imputed with median per job group. A student and a manager have very different age distributions. Using the job group median keeps that signal intact rather than pulling everyone toward the same number.

**Duration nulls** — global median. Less than 1% missing and excluded from modelling anyway, so precision here doesn't matter.

**Unknown job** — recoded to the most common job within each education level. Not a perfect fix, but better than leaving it as 'unknown' which would pollute job-level analysis.

After cleaning: **4,119 rows, 27 columns** — the extra columns are engineered features added after cleaning.

---

## Feature engineering

New columns added to the clean dataset:

- `age_group` — binned into `<25`, `25-34`, `35-44`, `45-54`, `55-64`, `65+`
- `contacted_before` — 1 if `pdays` ≠ 999 (999 means never contacted in a previous campaign)
- `duration_min` — call duration converted from seconds to minutes
- `high_euribor` — 1 if Euribor 3-month rate > 3
- `subscribed` — binary version of the `y` target column (1 = yes, 0 = no)

---

## Aggregations

All aggregations are done with pandas `groupby` — no database needed. The clean CSV loads directly into whatever tool you want to use next.

Breakdowns computed:
- Subscription rate by job type
- Monthly contact volume and conversion rate
- Conversion by age group
- Impact of previous campaign outcome
- Conversion by education level

---

## Excel dashboard

The `.xlsx` file has five sheets and all formulas are live — nothing is hardcoded.

**Raw Data** — all 4,119 clean rows with auto-filter. Every formula on the other sheets pulls from this.

**Lookup Tables** — `COUNTIFS` and `AVERAGEIFS` formulas that aggregate the raw data by job, month, age group, and previous outcome. This is the calculation layer.

**Executive Dashboard** — KPI cards using `COUNTA`, `COUNTIF`, `IFERROR`. Summary tables reference Lookup Tables via cross-sheet formulas. Includes a `RANK` column showing each job's position in the conversion league table. Charts built on Lookup Tables data ranges.

**Segment Analysis** — age group, previous outcome, and education breakdowns. Directly references Lookup Tables. Includes a "vs overall average" column using cross-sheet subtraction.

**Formula Guide** — documents every formula type used in the workbook with plain English explanations and examples. Useful if you want to extend the analysis or understand how something works.

---

## Key findings

- Previous successful campaign contact is the strongest conversion signal — those clients convert at 4-5x the baseline rate
- May has the highest contact volume but not the best conversion rate. March, September, and December outperform on rate
- Students and retirees convert well above their contact share
- Call duration correlates strongly with subscription — but it's leakage, so this can't be used predictively

---

## Files

```
01_data/
    bank_marketing_raw.csv          raw dataset — nulls, duplicates, unknown values intact

02_cleaning/
    build_all.py                    cleaning + aggregation + Excel builder in one script
    rebuild_excel.py                standalone Excel rebuild script (formula-based version)
    bank_marketing_clean.csv        clean output — load into Power BI or any other tool

05_output/
    bank_marketing_dashboard.xlsx   Excel workbook with live formulas across 5 sheets
```

---

## How to run

```bash
cd 02_Bank_Marketing_Analysis
python3 02_cleaning/build_all.py
```

Then open `05_output/bank_marketing_dashboard.xlsx` in Excel or Google Sheets.
