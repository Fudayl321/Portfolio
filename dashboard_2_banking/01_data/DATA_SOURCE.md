# Dashboard 2 — Data Source

## Dataset: Bank Marketing (UCI Machine Learning Repository)

| Detail | Info |
|--------|------|
| **Source** | UCI Machine Learning Repository |
| **Direct Link** | https://archive.ics.uci.edu/dataset/222/bank+marketing |
| **Kaggle Mirror** | https://www.kaggle.com/datasets/henriqueyamahata/bank-marketing |
| **Original Study** | Moro, S., Cortez, P., & Rita, P. (2014). A data-driven approach to predict the success of bank telemarketing. Decision Support Systems |
| **Domain** | Finance / Banking / Marketing Analytics |
| **Records** | 4,119+ client records |
| **Features** | 20 input features + 1 binary target |
| **Period** | May 2008 – November 2010, Portuguese bank |

## Why This Dataset?

The Bank Marketing dataset represents a real-world telemarketing campaign from a Portuguese bank.
It demonstrates skills that are directly relevant to analytics roles:
- **Customer segmentation** — identifying which profiles convert
- **Imbalanced classification** — only ~11% subscribe (real business challenge)
- **Feature engineering** — economic indicators, contact history, and demographics
- **Excel reporting** — perfect for pivot-table style analysis recruiters expect

## Features

| Column | Description |
|--------|-------------|
| `age` | Client age |
| `job` | Job type (admin, blue-collar, entrepreneur, etc.) |
| `marital` | Marital status |
| `education` | Education level |
| `default` | Has credit in default? |
| `housing` | Has housing loan? |
| `loan` | Has personal loan? |
| `contact` | Contact communication type |
| `month` | Last contact month |
| `duration` | Last contact duration (seconds) — **note: known data leakage, excluded from model** |
| `campaign` | Number of contacts in this campaign |
| `pdays` | Days since last contact (999 = not contacted) |
| `previous` | Number of previous campaign contacts |
| `poutcome` | Previous campaign outcome |
| `emp.var.rate` | Employment variation rate (quarterly) |
| `cons.price.idx` | Consumer price index (monthly) |
| `cons.conf.idx` | Consumer confidence index |
| `euribor3m` | Euribor 3-month rate |
| `nr.employed` | Number of employees (quarterly) |
| `y` | **Target: did client subscribe a term deposit? (yes/no)** |

## Download Instructions (to reproduce)

```bash
# Option 1: UCI directly
wget https://archive.ics.uci.edu/ml/machine-learning-databases/00222/bank-additional.zip

# Option 2: Kaggle CLI
kaggle datasets download -d henriqueyamahata/bank-marketing

# Option 3: Use the raw file in this repo
# File: 01_data/bank_marketing_raw.csv
```
