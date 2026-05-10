# Dashboard 1 — Data Source

## Dataset: Heart Disease (UCI Machine Learning Repository)

| Detail | Info |
|--------|------|
| **Source** | UCI Machine Learning Repository |
| **Direct Link** | https://archive.ics.uci.edu/dataset/45/heart+disease |
| **Kaggle Mirror** | https://www.kaggle.com/datasets/ronitf/heart-disease-uci |
| **Original Authors** | Detrano, Janosi, Steinbrunn, Pfisterer, Schwaiger, Chaitman, Gould, Froelicher |
| **Domain** | Healthcare / Clinical Medicine |
| **Records** | 1,025 patients |
| **Features** | 14 (13 predictors + 1 target) |
| **Period** | Cleveland Clinic Foundation study data |

## Why This Dataset?

The Heart Disease dataset is one of the most-cited datasets in binary classification research. It is used here to demonstrate:
- **Clinical data profiling** — understanding what each medical feature means
- **Missing value strategy** — medical data often has gaps; imputation choices matter
- **Class imbalance awareness** — disease vs no-disease ratios affect modelling
- **Explainability** — knowing *why* a model flags risk is as important as the prediction

## Features

| Column | Type | Description |
|--------|------|-------------|
| `age` | int | Age in years |
| `sex` | int | 1 = male, 0 = female |
| `cp` | int | Chest pain type (0=asymptomatic, 1=atypical angina, 2=non-anginal, 3=typical angina) |
| `trestbps` | int | Resting blood pressure (mm Hg) |
| `chol` | int | Serum cholesterol (mg/dl) |
| `fbs` | int | Fasting blood sugar > 120 mg/dl (1=true) |
| `restecg` | int | Resting ECG results (0=normal, 1=ST-T abnormality, 2=LV hypertrophy) |
| `thalach` | int | Max heart rate achieved |
| `exang` | int | Exercise-induced angina (1=yes) |
| `oldpeak` | float | ST depression induced by exercise |
| `slope` | int | Slope of peak exercise ST segment |
| `ca` | int | Number of major vessels coloured by fluoroscopy (0–3) |
| `thal` | int | Thalassemia (0=normal, 1=fixed defect, 2=reversible defect) |
| `target` | int | **Diagnosis: 1 = heart disease, 0 = no heart disease** |

## Download Instructions (to reproduce)

```bash
# Option 1: UCI directly
wget https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data

# Option 2: Kaggle CLI
kaggle datasets download -d ronitf/heart-disease-uci

# Option 3: Use the raw file in this repo
# File: 01_data/heart_disease_raw.csv
```
