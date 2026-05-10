# Power BI Dashboard — Setup Guide

This folder contains everything how i build the Heart Disease Risk Analysis dashboard in Power BI Desktop.
---

## What you need

- Power BI Desktop (free download: https://powerbi.microsoft.com/desktop)
- The clean dataset: `02_cleaning/heart_disease_clean.csv`

---

## Step 1 — Load the data

Open Power BI Desktop. On the home screen click **Get data → Text/CSV** and select `heart_disease_clean.csv`.

---

## Step 2 — Power Query (data types)

In Power Query, set these column types manually.

| Column | Set type to |
|--------|------------|
| `age` | Whole Number |
| `sex` | Whole Number |
| `cp` | Whole Number |
| `trestbps` | Whole Number |
| `chol` | Whole Number |
| `thalach` | Whole Number |
| `exang` | Whole Number |
| `oldpeak` | Decimal Number |
| `ca` | Whole Number |
| `thal` | Whole Number |
| `target` | Whole Number |
| `sex_label` | Text |
| `cp_label` | Text |
| `target_label` | Text |
| `age_group` | Text |

Click **Close & Apply** when done.

---

## Step 3 — DAX measures

In the **Data** pane on the right, right-click the table name and choose **New measure**. Add these one by one.

**Total Patients**
```dax
Total Patients = COUNTROWS(heart_disease_clean)
```

**Disease Cases**
```dax
Disease Cases = 
CALCULATE(
    COUNTROWS(heart_disease_clean),
    heart_disease_clean[target] = 1
)
```

**Disease Rate %**
```dax
Disease Rate % = 
DIVIDE([Disease Cases], [Total Patients]) * 100
```

**Avg Cholesterol**
```dax
Avg Cholesterol = AVERAGE(heart_disease_clean[chol])
```

**Avg Max Heart Rate**
```dax
Avg Max HR = AVERAGE(heart_disease_clean[thalach])
```

**Avg Age**
```dax
Avg Age = AVERAGE(heart_disease_clean[age])
```

**High Risk Patients** (RiskScore ≥ 5 — based on vessel count, ST depression, and angina)
```dax
High Risk Patients = 
CALCULATE(
    COUNTROWS(heart_disease_clean),
    heart_disease_clean[ca] * 2 
    + heart_disease_clean[oldpeak] 
    + IF(heart_disease_clean[exang] = 1, 2, 0)
    + IF(heart_disease_clean[cp] = 0, 2, 0) >= 5
)
```

---

## Step 4 — Calculated column

Right-click the table → **New column**.

**RiskScore** (composite clinical risk indicator)
```dax
RiskScore = 
heart_disease_clean[ca] * 2 
+ heart_disease_clean[oldpeak] 
+ IF(heart_disease_clean[exang] = 1, 2, 0) 
+ IF(heart_disease_clean[cp] = 0, 2, 0)
```

---

## Step 5 — Report layout

The dashboard has one page. Build it top to bottom.

### KPI cards (top row)
Add 5 **Card** visuals across the top. Drag these measures into each one:
- Total Patients
- Disease Cases
- Disease Rate %
- Avg Cholesterol
- Avg Max HR

Format each card: font size 28, bold, colour `#1A3C5E` (dark navy). Label text below each number in smaller grey text.

### Bar chart — Disease cases by age group and gender
- Visual type: **Clustered bar chart**
- X-axis: `age_group`
- Y-axis: `target` (Sum)
- Legend: `sex_label`
- Colours: Male = `#1A3C5E`, Female = `#C0392B`
- Title: *Disease Cases by Age Group & Gender*

### Donut chart — Diagnosis split
- Visual type: **Donut chart**
- Legend: `target_label`
- Values: Count of rows
- Colours: Heart Disease = `#C0392B`, No Disease = `#1A3C5E`
- Title: *Diagnosis Distribution*

### Scatter plot — Age vs Max Heart Rate
- Visual type: **Scatter chart**
- X-axis: `age`
- Y-axis: `thalach`
- Legend: `target_label`
- Size: leave blank or use `RiskScore`
- Title: *Age vs Max Heart Rate by Diagnosis*
- Note: patients with heart disease tend to cluster with lower max heart rate for the same age

### Clustered bar — Disease rate by chest pain type
- Visual type: **Clustered bar chart**
- X-axis: `cp_label`
- Y-axis: `Disease Rate %` measure
- Title: *Disease Rate by Chest Pain Type*
- Note: asymptomatic (cp=0) has the highest rate — counterintuitive but clinically documented

### Slicer — Age group filter
- Add a **Slicer** visual using `age_group`
- Style: dropdown or tiles
- This lets you filter all visuals on the page by age group at once

---

## Step 6 — Theme colours

In the **View** tab → **Themes** → **Customize current theme**. Set:

- **Primary colour:** `#1A3C5E`
- **Secondary colour:** `#217346`
- **Diverging colour low:** `#C0392B`
- **Background:** `#F8F9FA`
- **Font:** Calibri

---

## Step 7 — Page name

Double-click the page tab at the bottom and rename it to **Heart Disease Risk Analysis**.

---

## Save

Save as `Heart_Disease_Risk_Analysis.pbix`

---

## Key findings to highlight in the report

Once it's built, these are the findings worth annotating or putting in a text box:

- **Asymptomatic chest pain (cp=0)** has the highest disease rate — more so than typical angina. This is a known clinical finding, not a data error.
- **ca (vessels coloured by fluoroscopy)** and **oldpeak (ST depression)** are the strongest predictors — both are imaging/exercise-based rather than basic demographics.
- **Male patients aged 50–69** carry the highest disease burden in this dataset.
- The **RiskScore composite measure** (ca × 2 + oldpeak + angina flag + asymptomatic flag) roughly tracks with the Random Forest feature importance from the Python analysis.
