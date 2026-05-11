# Personal Guide — How to Build Each Dashboard Yourself

This is for my own reference. Written so I can come back to this in 6 months and still understand what I did and how to rebuild or extend anything here.

---

## Part 1 — Excel Dashboard (Bank Marketing)

### How the workbook is structured

The workbook has 5 sheets and they talk to each other in a specific order:

```
Raw Data  →  Lookup Tables  →  Executive Dashboard
                            →  Segment Analysis
Formula Guide (documentation only — no data)
```

**Raw Data** is the foundation. It's just the clean CSV loaded as a table with auto-filter. Every formula in the workbook pulls from here using cross-sheet references.

**Lookup Tables** does all the heavy aggregation with COUNTIFS and AVERAGEIFS. This sheet exists so the dashboard formulas stay simple — instead of writing a complex formula 12 times on the dashboard, I write it once in Lookup Tables and the dashboard just references that cell.

**Executive Dashboard and Segment Analysis** pull from Lookup Tables using simple cell references like `='Lookup Tables'!D5`. Charts are built on the Lookup Tables data ranges.

### The formulas to understand

**COUNTIFS** — the most important one in the whole file. Counts rows that match multiple conditions at once.

```excel
=COUNTIFS('Raw Data'!B2:B4120, "admin.", 'Raw Data'!J2:J4120, 1)
```

Read it as: count every row where column B is "admin." AND column J is 1. That gives you how many admin clients subscribed.

**AVERAGEIFS** — same idea but calculates an average instead of a count.

```excel
=AVERAGEIFS('Raw Data'!G2:G4120, 'Raw Data'!B2:B4120, "admin.")
```

Read it as: average column G (call duration) only for rows where column B is "admin."

**IFERROR** — wraps any formula that might divide by zero or return an error.

```excel
=IFERROR(C11/B11, 0)
```

If C11/B11 would error (because B11 is zero), return 0 instead of showing #DIV/0!. Always wrap division formulas with this.

**RANK** — shows where each job type sits in the league table without sorting.

```excel
=RANK(D11, 'Lookup Tables'!D5:D15, 0)
```

The 0 at the end means highest value = rank 1. Change to 1 if you want lowest = rank 1.

**Cross-sheet reference** — when you reference a cell on another sheet:

```excel
='Lookup Tables'!D5
```

Single quotes around the sheet name are required when the name has a space. If you rename a sheet, Excel updates these references automatically.

**vs Average column** — shows how much better or worse each row is compared to the overall conversion rate:

```excel
=D5 - 'Executive Dashboard'!E7
```

E7 is the overall conversion rate KPI. Subtracting it from each row's rate tells you if that group is above or below average. Format this column as `+0.0%;-0.0%` so positives show a + sign.

### How to add a new analysis yourself

Say you want to add a breakdown by marital status. Here's the exact steps:

1. Go to **Lookup Tables** sheet. Pick an empty area.
2. List the unique values in column A: `married`, `single`, `divorced`
3. In column B, write: `=COUNTIF('Raw Data'!C2:C4120, A2)` — drag down for each value
4. In column C: `=COUNTIFS('Raw Data'!C2:C4120, A2, 'Raw Data'!J2:J4120, 1)` — drag down
5. In column D: `=IFERROR(C2/B2, 0)` — format as percentage — drag down
6. Go to **Segment Analysis** sheet, add a new section
7. Reference your new Lookup Table cells: `='Lookup Tables'!A2` etc.

That's it. The pattern is always the same: raw data → lookup aggregation → dashboard reference.

### Conditional formatting

Two types are used in this file:

**Color Scale** (on sub rate columns) — right-click a column range → Conditional Formatting → Color Scales → choose 3-color scale. Set red for low, yellow for mid, green for high. Excel calculates everything automatically.

**Data Bars** (on age group sub rate) — right-click range → Conditional Formatting → Data Bars → choose a colour. Creates an in-cell bar chart. Works best when all values are in the same scale.

---

## Part 2 — Power BI Dashboard (Healthcare)

The full step-by-step is in `01_Heart_Disease_Risk_Analysis/05_output/PowerBI_Setup_Guide.md`. This section explains the concepts behind what you're doing there.

### How Power BI connects to data

Power BI uses **Power Query (M language)** to connect to and shape data before it loads into the model. Think of Power Query as the equivalent of your cleaning script — it runs every time you refresh.

When you click **Transform Data** after loading a CSV, you're in Power Query. Every step you take there gets recorded as an M query behind the scenes. You can see the M code by clicking **Advanced Editor**.

### What DAX is and why it's different from Excel formulas

DAX (Data Analysis Expressions) is the formula language inside Power BI. It looks similar to Excel but works differently because it operates on entire columns and tables, not individual cells.

The key difference: in Excel you write `=C11/B11` referencing specific cells. In DAX you write `DIVIDE([Disease Cases], [Total Patients])` referencing measures, and Power BI calculates it across whatever context is selected (e.g. only the rows for Male patients aged 50-59 if that's what's filtered).

**Measures** — calculated dynamically based on what's filtered on the report. Always start with an aggregate function (SUM, COUNT, AVERAGE, DIVIDE, CALCULATE).

```dax
Disease Rate % = DIVIDE([Disease Cases], [Total Patients]) * 100
```

**Calculated columns** — computed row by row when data loads, stored in the table like a regular column.

```dax
RiskScore = [ca] * 2 + [oldpeak] + IF([exang] = 1, 2, 0) + IF([cp] = 0, 2, 0)
```

Use measures for KPIs and aggregations. Use calculated columns when you need a value per row (like a risk score or age group label).

### CALCULATE — the most important DAX function

CALCULATE evaluates a measure while changing the filter context. It's used everywhere.

```dax
Disease Cases = CALCULATE(COUNTROWS(heart_disease_clean), heart_disease_clean[target] = 1)
```

Read it as: count all rows, but only where target = 1. Without CALCULATE, you'd be counting all rows every time regardless of what's in `target`.

### How to build a visual

1. Click any blank area on the canvas
2. In the **Visualizations** pane on the right, click the visual type you want
3. Drag fields from the **Data** pane into the field wells (X-axis, Y-axis, Legend, etc.)
4. Format using the paintbrush icon in Visualizations → adjust colours, titles, labels
5. Resize by dragging the corners of the visual

### How filters and slicers work

A **slicer** is just a visual that filters other visuals on the same page. When you click a value in a slicer, Power BI applies that as a filter to every other visual automatically. You don't write any code for this — it's built in.

**Cross-filtering** — clicking a bar in one chart will filter all other charts. This is on by default. You can turn it off per visual via Format → Edit interactions.

### Where to take it further

- **Power BI Service** — publish your report to app.powerbi.com (free account works) and you get a shareable URL
- **Row-level security** — restrict what different users can see
- **Scheduled refresh** — connect to a live data source and set it to refresh automatically
- **Bookmarks** — save different filter states and add buttons to switch between them

---

## Part 3 — R Dashboard (E-Commerce)

### How the R script is structured

The script in `04_analysis/build_dashboard.R` runs top to bottom in 6 steps:

```
Step 1: Load raw CSV
Step 2: Clean — fix invalid values, impute nulls, engineer features
Step 3: Aggregate — group_by + summarise to create summary tables
Step 4: Statistical tests — Kruskal-Wallis, t-test, Spearman
Step 5: Build ggplot2 charts — save as PNG
Step 6: Build HTML dashboard — embed charts + test results
```

### The dplyr verbs to know

dplyr is the R equivalent of SQL for data manipulation. The 6 functions you use most:

**filter()** — keeps rows that match a condition (like WHERE in SQL)
```r
df %>% filter(price > 0, !is.na(review_score))
```

**select()** — keeps only the columns you want (like SELECT in SQL)
```r
df %>% select(order_id, product_category, total_value, review_score)
```

**mutate()** — adds new columns or modifies existing ones (like adding a calculated column)
```r
df %>% mutate(freight_pct = freight_value / total_value * 100)
```

**group_by() + summarise()** — equivalent of GROUP BY in SQL
```r
df %>%
  group_by(product_category) %>%
  summarise(
    total_orders = n(),
    total_revenue = sum(total_value),
    avg_review = mean(review_score)
  )
```

**arrange()** — sorts rows (like ORDER BY in SQL)
```r
df %>% arrange(desc(total_revenue))
```

**left_join()** — joins two tables on a common column (like LEFT JOIN in SQL)
```r
df %>% left_join(category_medians, by = "product_category")
```

The `%>%` symbol is the pipe — it passes the result of one function into the next. It reads as "and then".

### ggplot2 — how charts are built

ggplot2 works in layers. You start with the data and aesthetic mapping, then add geometry layers on top.

```r
ggplot(data, aes(x = category, y = revenue)) +  # data + axes
  geom_col(fill = "#1A3C5E") +                   # bar chart layer
  geom_text(aes(label = revenue), vjust = -0.3) + # labels layer
  theme_minimal() +                               # clean background
  labs(title = "Revenue by Category", x = "", y = "Revenue (BRL)")
```

**aes()** maps data columns to visual properties — x position, y position, colour, size, fill. Anything inside aes() changes based on data. Anything outside aes() is a fixed value.

```r
# Colour based on data (inside aes)
aes(fill = product_category)

# Fixed colour (outside aes)
geom_col(fill = "#1A3C5E")
```

Common geom types:
- `geom_col()` or `geom_bar()` — bar charts
- `geom_line()` — line charts
- `geom_point()` — scatter plots
- `geom_boxplot()` — box plots (shows median + spread)
- `geom_histogram()` — histograms
- `geom_violin()` — violin plots

### Statistical tests — when to use which

**Kruskal-Wallis** — use this when you want to compare a variable across 3 or more groups and the data is ordinal (like review scores 1-5) or not normally distributed.

```r
kruskal.test(review_score ~ payment_type, data = df)
```

If p < 0.05, at least one group is significantly different from the others.

**t-test (independent)** — use this when comparing two groups on a continuous variable and you can assume the data is roughly normal.

```r
t.test(delivery_days ~ high_value, data = df)
```

If p < 0.05, the two groups have significantly different means.

**Spearman correlation** — use this when both variables are either ordinal or skewed. Measures how strongly two variables move together (r = 1 is perfect positive, r = -1 is perfect negative, r = 0 is no relationship).

```r
cor(df$price, df$review_score, method = "spearman", use = "complete.obs")
```

Always report the p-value alongside the r value — a small r can still be statistically significant with a large sample.

### How to add a new chart to the R dashboard

1. Create a new ggplot object:
   ```r
   p7 <- ggplot(df, aes(x = payment_type, y = total_value)) +
     geom_boxplot(fill = "#1A3C5E", alpha = 0.7) +
     theme_minimal() +
     labs(title = "Order Value by Payment Type", x = "", y = "Value (BRL)")
   ```

2. Save it:
   ```r
   ggsave("04_analysis/Payment_Value_Boxplot.png", p7, width = 8, height = 5, dpi = 120)
   ```

3. Add it to the dashboard by embedding the base64-encoded PNG in the HTML section (same pattern as the other charts in the script).

---

## Part 4 — Adding Dashboard Screenshots (Power BI & R)

Since `.pbix` files need Power BI Desktop to view, and R charts are static PNGs, screenshots are the way to show the actual output in the README so visitors can see the result without downloading anything.

### How to take a good dashboard screenshot

**Power BI Desktop:**
1. Build the dashboard following the setup guide
2. Set the zoom to 100% (View → Page View → Actual Size)
3. Press `Windows + Shift + S` to open the snip tool
4. Select the full report canvas
5. Save as `dashboard_preview.png`

**Excel:**
1. Zoom to 80% so the full dashboard fits on screen
2. `Windows + Shift + S` → select the sheet
3. Save as `dashboard_preview.png`

### Where to put the screenshots

Put them in the `05_output/` folder of each project and add them to the README like this:

```markdown
## Dashboard Preview

![Healthcare Dashboard](./05_output/dashboard_preview.png)
```

GitHub renders this automatically — anyone visiting the repo sees the image inline without needing to download anything.

### Screenshot checklist before saving

- All KPI cards are visible and showing real numbers
- At least 3-4 charts are visible
- No filter panels or sidebars covering the content
- The title is visible at the top
- Nothing is loading or showing an error

---

## Quick reference — which tool for which job

| Task | Tool |
|------|------|
| Count rows matching conditions | Excel: COUNTIFS / SQL: COUNT + WHERE / Python: df.groupby().size() / R: group_by + n() |
| Average of a filtered group | Excel: AVERAGEIFS / SQL: AVG + WHERE / Python: groupby().mean() / R: group_by + mean() |
| Join two tables | Excel: VLOOKUP or cross-sheet ref / SQL: JOIN / Python: merge() / R: left_join() |
| Find outliers | Python: IQR method / R: boxplot.stats() |
| Test if two groups differ | R: t.test() or kruskal.test() / Python: scipy.stats.ttest_ind() |
| Build a bar chart | Excel: Insert → Chart / Power BI: Bar chart visual / Python: px.bar() / R: geom_col() |
| Automate repetitive formatting | Excel: VBA / Python: openpyxl loop / R: apply family |
