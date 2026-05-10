# Dashboard 2 — Bank Marketing Campaign Analysis

**Industry:** Finance / Banking  
**Tools:** Python, SQL (SQLite), Excel (openpyxl)  
**Dataset:** UCI Bank Marketing — Portuguese bank telemarketing campaign  
**Source:** https://archive.ics.uci.edu/dataset/222/bank+marketing  
**Kaggle mirror:** https://www.kaggle.com/datasets/henriqueyamahata/bank-marketing

---

## Why this dataset

This is a real dataset from a Portuguese bank that ran a phone-based marketing campaign between May 2008 and November 2010. The goal was to get clients to subscribe to a term deposit. It has 4,100+ records and 20 features — a mix of client demographics, contact history, and macroeconomic indicators like the Euribor rate and employment variation.

What I liked about it for a portfolio project is that it's the kind of data you'd actually see in a financial services job. The conversion rate is low (around 11–17% depending on the subset), which is realistic — most campaigns don't convert well — and that makes the analysis more interesting than a dataset where half the outcomes are positive.

---

## What I found when I loaded the data

First thing I always do is check for duplicates and nulls before anything else.

**Duplicates:** 25 exact duplicate rows. Small number but worth removing — they'd skew any count-based metric.

**Nulls:**
- `age` — 60 nulls
- `duration` — 30 nulls

**Categorical issues:**
- `job` had 65 entries coded as `'unknown'` — not technically a null but not useful either

One important note I flagged early: the `duration` column (how long the call lasted) is **data leakage**. You only know the call duration after the call ends, which means after you already know the outcome. I kept it in the dataset for EDA purposes but explicitly excluded it from any modelling. This kind of thing matters and I wanted to document it clearly.

---

## Cleaning decisions and why

**Duplicates** — dropped all 25. No reason to keep exact copies.

**Age nulls** — imputed using median per job group, not global median. A 22-year-old student and a 58-year-old manager have very different typical ages. Using the job group median preserves that demographic signal better than throwing everyone together.

**Duration nulls** — global median. Less than 1% missing and since it's excluded from modelling anyway, precision here doesn't matter much.

**Unknown job** — recoded using the most common job type within each education level. Not perfect, but better than leaving it as 'unknown' since it adds noise to any job-level grouping.

After cleaning: **4,119 rows, 27 columns** (including the derived columns I added).

---

## Feature engineering

A few new columns I created that made the analysis more useful:

- `age_group` — binned into `<25`, `25-34`, `35-44`, `45-54`, `55-64`, `65+` for group-level comparisons
- `contacted_before` — binary flag, 1 if `pdays` is not 999 (999 means they were never contacted in a previous campaign)
- `duration_min` — converted call duration from seconds to minutes, easier to read
- `high_euribor` — flag for whether the Euribor 3-month rate was above 3 (a rough indicator of tighter economic conditions)

---

## SQL queries

Same approach as project 1 — load into SQLite, aggregate with SQL, then pass to Python for visualisation.

The queries I found most useful:

**Subscription rate by job** — big variation here. Students and retirees convert at significantly higher rates than blue-collar workers, even with smaller sample sizes.

**Monthly campaign performance** — May has the most contacts by far, but March, September, and December have the best conversion rates. High volume ≠ high quality.

**Impact of previous campaign outcome** — this was the clearest finding in the whole dataset. If someone subscribed in a previous campaign, they convert at 4-5x the baseline rate. If they were contacted before but didn't subscribe, they still convert better than someone never contacted. Prior contact history is probably the single most predictive feature for targeting.

**Education level breakdown** — university degree holders convert at the highest rate, though illiterate clients (very small group) also show a high rate which is probably just noise from small sample size.

---

## Excel dashboard

The `.xlsx` file in `05_output/` has three sheets:

**Executive Summary** — the main dashboard sheet. Has KPI cards at the top (total contacts, subscriptions, conversion rate, avg age, avg call duration), then a full subscription-by-job table with conditional colour formatting on the conversion rate column, and a monthly trend table below that. Two charts sit to the right — a horizontal bar chart for job-level conversion rates and a line chart for the monthly trend.

**Segment Analysis** — deeper breakdown by age group, education level, and previous campaign outcome. Data bars on the conversion rate column so you can scan it quickly. Charts stacked below the tables.

**Clean Data** — the first 500 rows of the cleaned dataset with auto-filter enabled. Mostly there so someone opening the file can see what the data actually looks like.

Everything is formatted — colours, borders, header styles. I built it with `openpyxl` in Python rather than manually, which means it's reproducible and the formatting is consistent throughout.

---

## Key findings

- Previous successful contact is the strongest predictor of conversion — far more than demographics
- May is the highest-volume month but not the best month to call. March, September, October, and December outperform on rate
- Students and retirees over-index on subscriptions relative to their share of contacts
- Clients with no prior contact history are the hardest to convert

---

## Files in this folder

```
01_data/
    bank_marketing_raw.csv         raw dataset with nulls, duplicates, unknowns

02_cleaning/
    build_all.py                   cleaning + SQL + Excel builder in one script
    bank_marketing_clean.csv       output after cleaning

03_sql/
    bank_marketing.db              SQLite database

05_output/
    bank_marketing_dashboard.xlsx  Excel dashboard — open in Excel or Google Sheets
```

---

## How to run

```bash
cd 02_Bank_Marketing_Analysis
python3 02_cleaning/build_all.py
```

Then open `05_output/bank_marketing_dashboard.xlsx`.
