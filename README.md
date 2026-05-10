# 📊 Data Analytics Portfolio — Fudayl Abdul Jalil

> **Customer Success Manager** at Juris Technologies | **Sales Analytics Intern** at Nestlé Malaysia  
> BSc Information Systems (Hons.) — Intelligent System Engineering, UiTM Shah Alam (First Class, in progress)

---

## About This Portfolio

This portfolio demonstrates end-to-end data analytics capability across **three different industries** using real public datasets. Each project follows the same structured workflow:

```
01_data/          ← Dataset source documentation + raw CSV
02_cleaning/      ← Full data cleaning script with justifications
03_sql/           ← SQL queries used for aggregation
04_analysis/      ← Analysis, modelling, and chart generation
05_output/        ← Final dashboard (HTML + Excel where applicable)
```

Every project starts from a **publicly verifiable dataset** — the source link, download instructions, and schema are all documented so anyone can reproduce the work from scratch.

---

## 🏥 Dashboard 1 — Healthcare Analytics (Power BI-style)

**Dataset:** [UCI Heart Disease — Cleveland Clinic Foundation](https://archive.ics.uci.edu/dataset/45/heart+disease)  
**Tools:** Python · pandas · scikit-learn · Plotly · SQL (SQLite)  
**Domain:** Healthcare / Clinical Data

### What I Did
- Profiled 1,025 patient records, identified and handled 3 types of data quality issues
- Ran SQL queries to compute risk profiles by age group, gender, and chest pain type
- Built a Random Forest classifier (AUC 0.89+, 5-fold CV validated)
- Extracted feature importance to explain which clinical indicators drive predictions
- Published as an interactive HTML dashboard

### Key Findings
- Asymptomatic chest pain (cp=0) paradoxically shows the highest disease rate — consistent with published clinical research
- `ca` (vessels coloured by fluoroscopy) and `oldpeak` (ST depression) are the strongest predictors
- Male patients aged 50–69 carry the highest disease burden in this dataset

**[→ View Dashboard](dashboard_1_healthcare/05_output/dashboard_healthcare.html)**

---

## 🏦 Dashboard 2 — Banking & Marketing Analytics (Excel)

**Dataset:** [UCI Bank Marketing — Portuguese Bank Campaign](https://archive.ics.uci.edu/dataset/222/bank+marketing)  
**Tools:** Python · pandas · openpyxl · Plotly · SQL (SQLite)  
**Domain:** Finance / Marketing

### What I Did
- Cleaned 4,144 records: removed 25 duplicates, imputed age by job-group median, recoded 'unknown' jobs
- Built a fully formatted **multi-sheet Excel workbook** with charts, conditional formatting, and data bars
- Used SQL to compute subscription rates by job, month, education, and previous outcome
- Built an interactive HTML report alongside the Excel file

### Key Findings
- Clients with a **previous successful contact** convert at 4-5× the baseline rate
- Despite May being the highest-volume month, March/September/December outperform on conversion rate
- `duration` (call length) is data leakage — excluded from any model, flagged explicitly

**[→ View HTML Report](dashboard_2_banking/05_output/bank_marketing_report.html)**  
**[→ Download Excel Dashboard](dashboard_2_banking/05_output/bank_marketing_dashboard.xlsx)**

---

## 🛒 Dashboard 3 — E-Commerce Analytics (R)

**Dataset:** [Kaggle — Brazilian Olist E-Commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)  
**Tools:** R · ggplot2 · dplyr · lubridate · tidyr · scales  
**Domain:** E-Commerce / Retail

### What I Did
- Cleaned 8,000 orders across 12 product categories spanning 2016–2018
- Used `dplyr` pipelines for data transformation and feature engineering
- Applied **statistical tests**: Kruskal-Wallis (review score by payment type) and independent t-test (delivery time by order tier)
- Calculated Spearman correlation between price and customer satisfaction
- Built 6 `ggplot2` charts embedded into a self-contained HTML dashboard

### Key Findings
- Credit card orders show significantly higher review scores than boleto (Kruskal-Wallis p < 0.05)
- Electronics leads revenue but scores lower in on-time delivery vs clothing
- Freight as % of order value is highest for lower-price categories — a pricing optimisation opportunity

**[→ View Dashboard](dashboard_3_ecommerce/05_output/ecommerce_dashboard.html)**

---

## 🛠️ Skills Demonstrated Across All Projects

| Skill | Where Used |
|-------|-----------|
| **SQL** | All 3 dashboards — aggregations, window functions, joins |
| **Python (pandas)** | Dashboards 1 & 2 — cleaning, EDA, ML |
| **Python (Plotly)** | Dashboards 1 & 2 — interactive visualisations |
| **R (ggplot2, dplyr)** | Dashboard 3 — visualisation, data wrangling |
| **Statistical Testing** | Dashboard 3 — Kruskal-Wallis, t-test, Spearman |
| **Machine Learning** | Dashboard 1 — Random Forest, cross-validation, ROC |
| **Excel (openpyxl)** | Dashboard 2 — multi-sheet formatted workbook, charts |
| **Data Cleaning** | All 3 — null handling, outlier detection, type validation |
| **Feature Engineering** | All 3 — derived columns, binning, flags |

---

## ⚙️ How to Reproduce

Each dashboard is fully self-contained and reproducible. Clone the repo and run the pipeline scripts:

```bash
git clone https://github.com/fudayl-abdul-jalil/data-analytics-portfolio.git
cd data-analytics-portfolio

# Dashboard 1 (Python)
cd dashboard_1_healthcare
python3 02_cleaning/01_clean_data.py
python3 04_analysis/build_dashboard.py

# Dashboard 2 (Python)
cd ../dashboard_2_banking
python3 02_cleaning/build_all.py

# Dashboard 3 (R)
cd ../dashboard_3_ecommerce
Rscript 04_analysis/build_dashboard.R
```

### Requirements

**Python:**
```
pip install pandas numpy matplotlib seaborn plotly scikit-learn scipy openpyxl
```

**R:**
```r
install.packages(c("ggplot2","dplyr","tidyr","lubridate","scales","viridis","jsonlite","gridExtra"))
```

---

## 📬 Contact

- **LinkedIn:** [linkedin.com/in/fudayl-abdul-jalil](https://linkedin.com/in/fudayl-abdul-jalil)
- **Email:** fudayljalil@gmail.com
- **Location:** Petaling Jaya, Selangor, Malaysia
