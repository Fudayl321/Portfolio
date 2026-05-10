# Dashboard 3 — Brazilian E-Commerce Analysis

**Industry:** Retail / E-Commerce  
**Tools:** R, ggplot2, dplyr, lubridate, tidyr, scales  
**Dataset:** Olist Brazilian E-Commerce Public Dataset  
**Source:** https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

---

## Why this dataset

The Olist dataset is one of the more interesting public e-commerce datasets out there. It covers real orders from a Brazilian marketplace platform between October 2016 and August 2018 — around 100,000 orders in the full version, 8,000 in this subset. What makes it useful for analysis is the combination of transaction data, delivery performance, review scores, and geographic information all in one place.

I also wanted to do at least one project entirely in R. Most of my work has been in Python, but R is worth showing — particularly `dplyr` for data wrangling and `ggplot2` for visualisation, since those are standard tools in analytics roles.

---

## What I found when I loaded the data

The raw file had a few issues worth documenting:

**Invalid prices:** 15 rows where `price` was -99. Not a null, an actual wrong value. Negative prices don't exist.

**Impossible delivery times:** 10 rows where `delivery_days` was 0. An order can't be delivered in zero days from shipping — these are recording errors.

**Nulls:**
- `price` — 80 nulls
- `delivery_days` — 40 nulls (a mix of genuine missings and the ones I just set to NA after removing the zeros)
- `review_score` — 40 nulls

Not a massive amount, but enough that you need a strategy rather than just dropping everything.

---

## Cleaning decisions and why

**Negative prices** — removed. There's no plausible explanation for a -99 price that would make it worth keeping.

**Zero delivery days** — set to NA first, then imputed. I didn't drop them because delivery time is an important variable and I didn't want to lose those orders entirely.

**Price nulls** — imputed with the median price within each product category. Electronics prices and clothing prices are completely different scales, so using a single global median would be misleading. Category-level median is a much better estimate.

**Delivery days nulls** — same approach, category-level median. A furniture item and a book will have very different typical delivery times.

**Review score nulls** — global median. Review score doesn't vary as dramatically across categories as price does, so a global median is fine here.

After cleaning: **7,985 rows** (15 rows removed for negative prices), all nulls resolved.

---

## Feature engineering

- `year_month` — formatted as `YYYY-MM` for grouping in trend analysis
- `year`, `month`, `quarter` — extracted from `order_date` using `lubridate`
- `freight_pct` — freight value as a percentage of total order value. Useful for identifying categories where shipping is eating into margins
- `high_value` — binary flag for orders in the top 25th percentile by value

---

## Statistical tests

This is the part I wanted to include specifically because most dashboards just show charts. Adding statistical tests shows you're thinking about whether the patterns you see are actually real or just noise.

**Kruskal-Wallis test — review score by payment type**  
Non-parametric test because review scores are ordinal (1-5), not truly continuous. Tests whether review scores differ significantly across credit card, boleto, voucher, and debit card users.  
Result is in the dashboard — if p < 0.05, there's a statistically significant difference.

**Independent t-test — delivery time by order value tier**  
Tests whether high-value orders (top quartile) take meaningfully longer to deliver than standard orders. The hypothesis is that heavier or bulkier items tend to be higher value and might take longer to ship.

**Spearman correlation — price vs review score**  
Spearman rather than Pearson because price is right-skewed and review score is ordinal. Tests whether more expensive items tend to get better or worse reviews.

---

## What the analysis found

**Revenue trend** — clear growth from late 2016 through mid-2018, with a dip around early 2018. Electronics is the top revenue category but not by as much as you might expect. Clothing, home appliances, and sports aren't far behind.

**Delivery performance** — on-time delivery rate varies by state. São Paulo (SP) and Rio de Janeiro (RJ) have the highest order volumes but aren't necessarily the best on delivery timing, which makes sense given the logistics complexity of the largest cities.

**Review scores** — the distribution is heavily skewed toward 5 stars. Either customers are genuinely happy, or unhappy customers don't bother reviewing. The 1-star reviews tend to cluster around late deliveries, which suggests delivery experience is the main driver of dissatisfaction.

**Freight as % of order** — this metric was interesting. For lower-price categories, freight sometimes represents 25-30% of total order value. That's a real business problem — customers in remote states are paying a disproportionate share of their order value just on shipping.

---

## Charts produced (ggplot2)

Six charts, all saved as PNG and embedded in the documentation:

1. Monthly revenue trend — area chart with line overlay
2. Top 10 categories by revenue — horizontal bar
3. Review score distribution — bar chart with percentage labels
4. Delivery days by category — boxplot (shows median and spread, not just averages)
5. Revenue by payment type — pie chart
6. On-time delivery % by state (top 10) — horizontal bar with colour gradient

---

## Files in this folder

```
01_data/
    ecommerce_raw.csv              raw dataset with nulls and invalid values

02_cleaning/
    ecommerce_clean.csv            output after cleaning

04_analysis/
    build_dashboard.R              full R script — cleaning, analysis, charts
    p1_monthly_trend.png           
    p2_top_categories.png          
    p3_review_dist.png             
    p4_delivery_box.png            
    p5_payment_pie.png             
    p6_ontime_state.png            
```

---

## How to run

Make sure you have R installed with the required packages, then:

```bash
cd dashboard_3_ecommerce
Rscript 04_analysis/build_dashboard.R
```

Required packages:
```r
install.packages(c("ggplot2", "dplyr", "tidyr", "lubridate", "scales", "viridis", "jsonlite", "gridExtra"))
```
