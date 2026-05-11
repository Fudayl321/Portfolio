# E-Commerce Performance Analysis

**Industry:** Retail / E-Commerce  
**Tools:** R, ggplot2, dplyr, lubridate, tidyr, scales  
**Dataset:** Olist Brazilian E-Commerce Public Dataset  
**Source:** https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

---

## Workflow

```
01_data/ecommerce_raw.csv
  → 04_analysis/build_dashboard.R       (R — cleaning, aggregation, statistical tests, charts)
  → 02_cleaning/ecommerce_clean.csv
  → 04_analysis/*.png                   (6 ggplot2 charts saved as PNG)
```

Everything runs inside a single R script. The cleaning, analysis, and chart generation all happen in one pass. No separate cleaning step needed.

---

## Why this dataset

The Olist dataset covers real orders from a Brazilian e-commerce marketplace between October 2016 and August 2018. It has transaction data, delivery performance, customer review scores, payment method, and the customer's state — all in one file. That combination makes it useful for looking at how operations (delivery timing) connect to outcomes (review scores) across different geographies and product types.

This project is also the R-only one. Most of my work is Python, so I wanted to show the same workflow — load, clean, analyse, visualise — done entirely in R with dplyr and ggplot2.

---

## What I found in the raw data

**Invalid prices:** 15 rows where `price` = -99. Not a null — an actual wrong value.

**Impossible delivery times:** 10 rows where `delivery_days` = 0. Can't be delivered the same day it ships.

**Nulls:**
- `price` — 80 nulls
- `delivery_days` — 40 nulls (includes the 10 set to NA after removing the zeros)
- `review_score` — 40 nulls

---

## Cleaning decisions

**Negative prices** — removed. No plausible explanation for a -99 value.

**Zero delivery days** — set to NA first, then imputed. The orders themselves are valid, just the delivery time is wrong. Setting to NA means they get imputed sensibly rather than being dropped.

**Price nulls** — imputed with median per product category. Electronics and clothing have completely different price scales, so a single global median would push imputed values in the wrong direction for most categories.

**Delivery days nulls** — same logic, category-level median. Furniture and books have very different typical delivery timelines.

**Review score nulls** — global median. Review scores don't vary enough by category to make group-level imputation worth the effort here.

After cleaning: **7,985 rows** — 15 removed for negative prices, all nulls resolved.

---

## Feature engineering

- `year_month` — `YYYY-MM` format for time series grouping
- `year`, `month`, `quarter` — extracted with `lubridate`
- `freight_pct` — freight as a percentage of total order value
- `high_value` — 1 if order value is in the top 25th percentile

---

## Statistical tests

Charts show patterns, but statistical tests tell you whether those patterns are real or just noise. Three tests were run:

**Kruskal-Wallis — review score by payment type**  
Non-parametric test because review scores are ordinal (1-5), not continuous. Tests whether scores differ significantly across credit card, boleto, voucher, and debit card users. If p < 0.05, at least one payment group rates differently from the others.

**Independent t-test — delivery days by order value tier**  
Tests whether high-value orders take significantly longer to deliver than standard ones. Hypothesis: bulkier, heavier items tend to cost more and may take longer to ship.

**Spearman correlation — price vs review score**  
Spearman instead of Pearson because price is right-skewed and review score is ordinal. Tests whether more expensive items get systematically better or worse ratings.

---

## What the analysis found

**Revenue** — clear growth from late 2016 through mid-2018. Electronics leads on revenue but the gap to clothing, home appliances, and sports is smaller than expected.

**Delivery** — on-time rate varies by state. The highest-volume states (SP, RJ) aren't necessarily the best on delivery, which makes sense — larger cities have more complex last-mile logistics.

**Review scores** — heavily skewed toward 5 stars. The 1-star reviews cluster around late deliveries, suggesting delivery experience drives dissatisfaction more than product quality.

**Freight as % of order** — for lower-price categories, freight can be 25-30% of the total order value. That's a real margin problem, and for customers in remote states it's disproportionately high.

---

## Charts

Six ggplot2 charts saved as PNG in `04_analysis/`:

| File | Chart type | What it shows |
|------|-----------|---------------|
| `Monthly_Revenue_Trend.png` | Area + line | Revenue growth over time |
| `Top_10_Categories_by_Revenue.png` | Horizontal bar | Category revenue ranking |
| `Customer_Review_Score_Distribution.png` | Bar | 1–5 star breakdown with percentages |
| `Delivery_Days_by_Category.png` | Boxplot | Median and spread of delivery time per category |
| `Revenue_by_Payment_Type.png` | Pie | Revenue share by payment method |
| `OnTime_Delivery_by_State.png` | Horizontal bar | On-time % for top 10 states by volume |

---

## Files

```
01_data/
    ecommerce_raw.csv                        raw dataset — invalid values and nulls intact

02_cleaning/
    ecommerce_clean.csv                      clean output after the R script runs

04_analysis/
    build_dashboard.R                        single R script — run this to do everything
    Monthly_Revenue_Trend.png
    Top_10_Categories_by_Revenue.png
    Customer_Review_Score_Distribution.png
    Delivery_Days_by_Category.png
    Revenue_by_Payment_Type.png
    OnTime_Delivery_by_State.png
```

---

## How to run

```bash
cd 03_Ecommerce_Performance_Analysis
Rscript 04_analysis/build_dashboard.R
```

Required R packages:
```r
install.packages(c("ggplot2", "dplyr", "tidyr", "lubridate", "scales", "viridis", "jsonlite", "gridExtra"))
```
