# Fudayl's Data Analytics Portfolio

Hey, thanks for stopping by.

I'm Fudayl — currently working as a Customer Success Manager at a fintech company and my degree in Information Systems at UiTM. My actual hands-on experience with data analytics comes from my internship at Nestlé Malaysia, where I built the Distribution Operation Report (DOR) — a Power BI solution used by all Nestlé distributors across Malaysia to track sales performance from company-level KPIs down to individual salesman targets.

I put this portfolio together to show what I can actually do with data, since I don't have a long list of certifications to back me up yet. Each project here follows the same structure — I find a real public dataset, document what's wrong with it, clean it with a Python or R script, and build something visual out of it.

---

## Projects

| # | Project | Industry | Tools |
|---|---------|----------|-------|
| 1 | [Heart Disease Risk Analysis](./01_Heart_Disease_Risk_Analysis/) | Healthcare | Python, pandas, scikit-learn, Power BI |
| 2 | [Bank Marketing Campaign Analysis](./02_Bank_Marketing_Analysis/) | Finance / Banking | Python, pandas, Excel |
| 3 | [E-Commerce Performance Analysis](./03_Ecommerce_Performance_Analysis/) | Retail / E-Commerce | R, ggplot2, dplyr |

---

## Workflow

Every project follows this flow:

```
Raw CSV (public dataset)
  → Python or R cleaning script
      fix nulls, drop invalid rows, engineer new columns
  → Clean CSV saved
  → Load directly into Power BI / Excel / R for analysis and visualisation
```

No databases in between. The clean CSV goes straight into the tool. Each project folder has a README explaining the decisions made at each step.

---

## Skills shown across all three

- **Python (pandas)** — data cleaning, EDA, aggregation, and machine learning in projects 1 and 2
- **R (ggplot2, dplyr, lubridate)** — full analysis and visualisation pipeline in project 3
- **Power BI** — DAX measures, Power Query, and full report layout in project 1
- **Excel** — multi-sheet workbook with COUNTIFS, AVERAGEIFS, IFERROR, RANK, and cross-sheet formulas in project 2
- **Data cleaning** — every project starts from a dirty dataset. Decisions on how each issue was handled are written up in the README, not just the code

---

## How to reproduce anything

```bash
git clone https://github.com/Fudayl321/Portfolio.git
cd Portfolio
```

Python:
```bash
pip install pandas numpy matplotlib seaborn plotly scikit-learn scipy openpyxl
```

R:
```r
install.packages(c("ggplot2", "dplyr", "tidyr", "lubridate", "scales", "viridis", "jsonlite", "gridExtra"))
```

Each project folder has a README with the exact commands.

---

## Contact

**LinkedIn** — [linkedin.com/in/fudayl-abdul-jalil](https://linkedin.com/in/fudayl-abdul-jalil)  
**Email** — fudayljalil@gmail.com  
**Location** — Petaling Jaya, Selangor
