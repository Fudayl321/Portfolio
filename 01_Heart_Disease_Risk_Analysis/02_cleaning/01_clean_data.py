"""
Dashboard 1 — Healthcare Analytics
Step 2: Data Cleaning & Validation
====================================
Dataset : Heart Disease (UCI ML Repository)
Source  : https://archive.ics.uci.edu/dataset/45/heart+disease
Author  : Fudayl Abdul Jalil

This script documents every cleaning decision with justification.
Output  : heart_disease_clean.csv
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import warnings
warnings.filterwarnings('ignore')

RAW   = "01_data/heart_disease_raw.csv"
OUT   = "02_cleaning/heart_disease_clean.csv"
PLOTS = "02_cleaning/"

print("=" * 65)
print("  HEART DISEASE DATASET — DATA CLEANING PIPELINE")
print("=" * 65)

# ── STEP 1: LOAD & INITIAL PROFILE ───────────────────────────
df = pd.read_csv(RAW)
print(f"\n[STEP 1] Raw dataset loaded")
print(f"  Shape      : {df.shape[0]:,} rows × {df.shape[1]} columns")
print(f"  Memory     : {df.memory_usage(deep=True).sum()/1024:.1f} KB")
print(f"  Duplicates : {df.duplicated().sum()}")
print(f"\n  Dtypes:\n{df.dtypes.to_string()}")

# ── STEP 2: MISSING VALUE ANALYSIS ───────────────────────────
print(f"\n[STEP 2] Missing value analysis")
null_report = pd.DataFrame({
    'missing_count': df.isnull().sum(),
    'missing_pct'  : (df.isnull().sum() / len(df) * 100).round(2)
}).query('missing_count > 0')

if len(null_report):
    print(null_report.to_string())
else:
    print("  No missing values found.")

# ── STEP 3: OUTLIER DETECTION ─────────────────────────────────
print(f"\n[STEP 3] Outlier detection")

outlier_report = {}
for col in ['age','trestbps','chol','thalach','oldpeak']:
    valid = df[col].dropna()
    q1, q3 = valid.quantile(0.25), valid.quantile(0.75)
    iqr    = q3 - q1
    lo, hi = q1 - 1.5*iqr, q3 + 1.5*iqr
    out    = df[(df[col] < lo) | (df[col] > hi)]
    neg    = df[df[col] < 0]
    impossible = df[df[col] == 999]     # coded missing
    outlier_report[col] = {
        'iqr_outliers': len(out), 'negatives': len(neg),
        'impossible': len(impossible), 'range': f"{valid.min()}–{valid.max()}"
    }
    print(f"  {col:12s}: range={valid.min():.0f}–{valid.max():.0f}  "
          f"IQR outliers={len(out)}  negatives={len(neg)}")

# ── STEP 4: CLEANING DECISIONS ────────────────────────────────
print(f"\n[STEP 4] Applying cleaning rules")
df_clean = df.copy()
original_len = len(df_clean)

# 4a. Remove impossible age values (age=999 is a data entry error)
mask_bad_age = df_clean['age'] > 120
print(f"  4a. Remove impossible age > 120  : {mask_bad_age.sum()} rows")
df_clean = df_clean[~mask_bad_age]

# 4b. Remove negative cholesterol (physically impossible)
mask_neg_chol = df_clean['chol'] < 0
print(f"  4b. Remove negative cholesterol  : {mask_neg_chol.sum()} rows")
df_clean = df_clean[~mask_neg_chol]

# 4c. Impute missing trestbps with median (blood pressure — median safer than mean due to skew)
med_bp = df_clean['trestbps'].median()
n_bp   = df_clean['trestbps'].isnull().sum()
df_clean['trestbps'] = df_clean['trestbps'].fillna(med_bp)
print(f"  4c. Impute trestbps nulls (median={med_bp:.0f})  : {n_bp} filled")

# 4d. Impute missing chol with median (cholesterol — median due to right skew)
med_chol = df_clean['chol'].median()
n_chol   = df_clean['chol'].isnull().sum()
df_clean['chol'] = df_clean['chol'].fillna(med_chol)
print(f"  4d. Impute chol nulls (median={med_chol:.0f})     : {n_chol} filled")

# 4e. Impute missing thalach with median (max heart rate — age-dependent, median by group is ideal
#     but for simplicity median overall is used given <5% missing)
med_hr = df_clean['thalach'].median()
n_hr   = df_clean['thalach'].isnull().sum()
df_clean['thalach'] = df_clean['thalach'].fillna(med_hr)
print(f"  4e. Impute thalach nulls (median={med_hr:.0f})    : {n_hr} filled")

# 4f. Cast all columns to correct types
int_cols = ['age','sex','cp','trestbps','chol','fbs','restecg',
            'thalach','exang','slope','ca','thal','target']
df_clean[int_cols] = df_clean[int_cols].astype(int)

# 4g. Add readable label columns
df_clean['sex_label']    = df_clean['sex'].map({1:'Male',0:'Female'})
df_clean['cp_label']     = df_clean['cp'].map({
    0:'Asymptomatic', 1:'Atypical Angina', 2:'Non-Anginal', 3:'Typical Angina'})
df_clean['target_label'] = df_clean['target'].map({1:'Heart Disease',0:'No Disease'})
df_clean['age_group']    = pd.cut(df_clean['age'],
    bins=[0,40,50,60,70,100],
    labels=['<40','40–49','50–59','60–69','70+'])

# ── STEP 5: VALIDATION ────────────────────────────────────────
print(f"\n[STEP 5] Post-cleaning validation")
print(f"  Rows removed : {original_len - len(df_clean)}")
print(f"  Final shape  : {df_clean.shape[0]:,} × {df_clean.shape[1]}")
print(f"  Remaining nulls : {df_clean.isnull().sum().sum()}")
print(f"  Target split : {df_clean['target'].value_counts().to_dict()}")

assert df_clean['age'].between(0,120).all(),    "Age out of range"
assert (df_clean['chol'] >= 0).all(),           "Negative cholesterol"
assert df_clean.isnull().sum().sum() == 0
assert df_clean['target'].isin([0,1]).all(),    "Invalid target"
print("  ✓ All assertions passed")

# ── STEP 6: EDA PLOTS ─────────────────────────────────────────
print(f"\n[STEP 6] Generating EDA plots")

fig = plt.figure(figsize=(18, 14))
fig.patch.set_facecolor('#f8f9fa')
gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.45, wspace=0.35)

NAVY  = '#1A3C5E'
GREEN = '#217346'
RED   = '#C0392B'
AMBER = '#E67E22'
cols  = [NAVY, GREEN]

# Plot 1: Target distribution
ax1 = fig.add_subplot(gs[0, 0])
vc  = df_clean['target_label'].value_counts()
bars = ax1.bar(vc.index, vc.values, color=[RED, NAVY], edgecolor='white', linewidth=0.5)
for b in bars:
    ax1.text(b.get_x()+b.get_width()/2, b.get_height()+5,
             f'{b.get_height():,}\n({b.get_height()/len(df_clean)*100:.1f}%)',
             ha='center', va='bottom', fontsize=9, fontweight='bold')
ax1.set_title('Target Class Distribution', fontweight='bold', color=NAVY, fontsize=11)
ax1.set_ylabel('Count')
ax1.set_facecolor('#fdfdfd')
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)

# Plot 2: Age distribution by disease
ax2 = fig.add_subplot(gs[0, 1])
for t, c, lbl in [(0, NAVY, 'No Disease'), (1, RED, 'Heart Disease')]:
    ax2.hist(df_clean[df_clean['target']==t]['age'], bins=20,
             alpha=0.65, color=c, label=lbl, edgecolor='white')
ax2.set_title('Age Distribution by Diagnosis', fontweight='bold', color=NAVY, fontsize=11)
ax2.set_xlabel('Age'); ax2.set_ylabel('Count')
ax2.legend(fontsize=9)
ax2.set_facecolor('#fdfdfd')
ax2.spines['top'].set_visible(False); ax2.spines['right'].set_visible(False)

# Plot 3: Gender vs Disease
ax3 = fig.add_subplot(gs[0, 2])
ct = df_clean.groupby(['sex_label','target_label']).size().unstack(fill_value=0)
ct.plot(kind='bar', ax=ax3, color=[NAVY, RED], edgecolor='white', width=0.6)
ax3.set_title('Gender vs Diagnosis', fontweight='bold', color=NAVY, fontsize=11)
ax3.set_xlabel(''); ax3.set_ylabel('Count')
ax3.tick_params(axis='x', rotation=0)
ax3.legend(fontsize=9); ax3.set_facecolor('#fdfdfd')
ax3.spines['top'].set_visible(False); ax3.spines['right'].set_visible(False)

# Plot 4: Chest pain type vs disease
ax4 = fig.add_subplot(gs[1, 0])
ct2 = df_clean.groupby(['cp_label','target_label']).size().unstack(fill_value=0)
ct2.plot(kind='bar', ax=ax4, color=[NAVY, RED], edgecolor='white', width=0.65)
ax4.set_title('Chest Pain Type vs Diagnosis', fontweight='bold', color=NAVY, fontsize=11)
ax4.set_xlabel(''); ax4.set_ylabel('Count')
ax4.tick_params(axis='x', rotation=20)
ax4.legend(fontsize=8); ax4.set_facecolor('#fdfdfd')
ax4.spines['top'].set_visible(False); ax4.spines['right'].set_visible(False)

# Plot 5: Cholesterol boxplot
ax5 = fig.add_subplot(gs[1, 1])
data_box = [df_clean[df_clean['target']==0]['chol'].values,
            df_clean[df_clean['target']==1]['chol'].values]
bp = ax5.boxplot(data_box, labels=['No Disease','Heart Disease'],
                  patch_artist=True, notch=True,
                  medianprops=dict(color='white', linewidth=2))
for patch, color in zip(bp['boxes'], [NAVY, RED]):
    patch.set_facecolor(color); patch.set_alpha(0.7)
ax5.set_title('Cholesterol Distribution', fontweight='bold', color=NAVY, fontsize=11)
ax5.set_ylabel('Serum Cholesterol (mg/dl)')
ax5.set_facecolor('#fdfdfd')
ax5.spines['top'].set_visible(False); ax5.spines['right'].set_visible(False)

# Plot 6: Max heart rate vs age scatter
ax6 = fig.add_subplot(gs[1, 2])
for t, c, lbl in [(0, NAVY, 'No Disease'), (1, RED, 'Heart Disease')]:
    sub = df_clean[df_clean['target']==t]
    ax6.scatter(sub['age'], sub['thalach'], alpha=0.35, s=18, color=c, label=lbl)
z = np.polyfit(df_clean['age'], df_clean['thalach'], 1)
p = np.poly1d(z)
ax6.plot(sorted(df_clean['age']), p(sorted(df_clean['age'])),
         '--', color=AMBER, linewidth=1.5, label='Trend')
ax6.set_title('Age vs Max Heart Rate', fontweight='bold', color=NAVY, fontsize=11)
ax6.set_xlabel('Age'); ax6.set_ylabel('Max Heart Rate')
ax6.legend(fontsize=8); ax6.set_facecolor('#fdfdfd')
ax6.spines['top'].set_visible(False); ax6.spines['right'].set_visible(False)

# Plot 7: Correlation heatmap
ax7 = fig.add_subplot(gs[2, :])
num_cols = ['age','trestbps','chol','thalach','oldpeak','ca','target']
corr = df_clean[num_cols].corr()
im = ax7.imshow(corr.values, cmap='RdYlGn', vmin=-1, vmax=1, aspect='auto')
ax7.set_xticks(range(len(num_cols))); ax7.set_yticks(range(len(num_cols)))
ax7.set_xticklabels(num_cols, rotation=30, ha='right', fontsize=9)
ax7.set_yticklabels(num_cols, fontsize=9)
for i in range(len(num_cols)):
    for j in range(len(num_cols)):
        ax7.text(j, i, f'{corr.values[i,j]:.2f}', ha='center', va='center',
                 fontsize=8, color='black' if abs(corr.values[i,j])<0.5 else 'white')
ax7.set_title('Feature Correlation Matrix', fontweight='bold', color=NAVY, fontsize=11)
plt.colorbar(im, ax=ax7, fraction=0.02)

fig.suptitle('Heart Disease Dataset — Exploratory Data Analysis\n'
             'Source: UCI ML Repository | github.com/fudayl-abdul-jalil',
             fontsize=13, fontweight='bold', color=NAVY, y=0.98)

plt.savefig(f"{PLOTS}eda_overview.png", dpi=150, bbox_inches='tight',
            facecolor=fig.get_facecolor())
plt.close()
print("  Saved: 02_cleaning/eda_overview.png")

# ── SAVE CLEAN DATA ───────────────────────────────────────────
df_clean.to_csv(OUT, index=False)
print(f"\n✓ Clean data saved → {OUT}")
print(f"  {len(df_clean):,} rows × {df_clean.shape[1]} columns ready for analysis")
