"""
Dashboard 1 — Healthcare Analytics
Step 4: Interactive Dashboard (Power BI equivalent)
=====================================================
Tools   : Python, pandas, scikit-learn, Plotly
Dataset : Heart Disease (UCI ML Repository)
Author  : Fudayl Abdul Jalil

Produces a self-contained HTML file — viewable in any browser,
shareable as a GitHub Pages link.
"""

import pandas as pd
import numpy as np

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json, os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

CLEAN = "02_cleaning/heart_disease_clean.csv"
OUT   = "05_output/dashboard_healthcare.html"

os.makedirs("05_output", exist_ok=True)

df = pd.read_csv(CLEAN)

# ── AGGREGATIONS — pandas groupby, clean CSV loaded directly ──
# Same results as the SQL queries, no database step needed.
# The clean CSV goes straight into Power BI the same way.

risk_df = (df.groupby(['age_group','sex_label'])
           .agg(total=('target','count'),
                disease_count=('target','sum'),
                avg_chol=('chol','mean'),
                avg_max_hr=('thalach','mean'),
                avg_bp=('trestbps','mean'))
           .reset_index()
           .assign(disease_rate_pct=lambda x: (x.disease_count/x.total*100).round(1),
                   avg_chol=lambda x: x.avg_chol.round(1),
                   avg_max_hr=lambda x: x.avg_max_hr.round(1),
                   avg_bp=lambda x: x.avg_bp.round(1))
           .sort_values(['age_group','sex_label']))

cp_df = (df.groupby('cp_label')
         .agg(total=('target','count'),
              disease_count=('target','sum'),
              avg_st_depression=('oldpeak','mean'))
         .reset_index()
         .assign(disease_rate_pct=lambda x: (x.disease_count/x.total*100).round(1),
                 avg_st_depression=lambda x: x.avg_st_depression.round(2))
         .sort_values('disease_rate_pct', ascending=False))

summary = pd.Series({
    'total_patients':  len(df),
    'disease_cases':   df['target'].sum(),
    'prevalence_pct':  round(df['target'].mean()*100, 1),
    'avg_age':         round(df['age'].mean(), 1),
    'avg_chol':        round(df['chol'].mean(), 0),
    'avg_max_hr':      round(df['thalach'].mean(), 0),
    'male_count':      (df['sex_label']=='Male').sum(),
    'female_count':    (df['sex_label']=='Female').sum(),
})

feat_df = (df.groupby('exang')
           .agg(avg_vessels=('ca','mean'),
                avg_st_dep=('oldpeak','mean'),
                disease_rate=('target','mean'))
           .reset_index()
           .assign(avg_vessels=lambda x: x.avg_vessels.round(2),
                   avg_st_dep=lambda x: x.avg_st_dep.round(2),
                   disease_rate=lambda x: (x.disease_rate*100).round(1)))

# ── MACHINE LEARNING — RANDOM FOREST ──────────────────────────
features = ['age','sex','cp','trestbps','chol','fbs','restecg',
            'thalach','exang','oldpeak','slope','ca','thal']
X = df[features]
y = df['target']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
rf = RandomForestClassifier(n_estimators=200, max_depth=8, random_state=42, n_jobs=-1)
rf.fit(X_train, y_train)

cv_scores = cross_val_score(rf, X, y, cv=5, scoring='roc_auc')
y_pred    = rf.predict(X_test)
y_prob    = rf.predict_proba(X_test)[:,1]
auc       = roc_auc_score(y_test, y_prob)
fpr, tpr, _ = roc_curve(y_test, y_prob)
cm        = confusion_matrix(y_test, y_pred)
fi        = pd.DataFrame({'feature':features, 'importance':rf.feature_importances_})\
              .sort_values('importance', ascending=True)

# ── COLOUR PALETTE ────────────────────────────────────────────
NAVY  = '#1A3C5E'
GREEN = '#217346'
RED   = '#C0392B'
AMBER = '#E67E22'
LBLUE = '#D6E4F0'
GREY  = '#595959'
BG    = '#f8f9fa'

# ── BUILD PLOTLY FIGURES ──────────────────────────────────────

# Fig 1 — Disease rate by age group & gender
fig1 = px.bar(risk_df, x='age_group', y='disease_rate_pct', color='sex_label',
              barmode='group', text='disease_rate_pct',
              color_discrete_map={'Male':NAVY, 'Female':RED},
              labels={'disease_rate_pct':'Disease Rate (%)',
                      'age_group':'Age Group','sex_label':'Gender'},
              title='Heart Disease Rate by Age Group & Gender')
fig1.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
fig1.update_layout(plot_bgcolor=BG, paper_bgcolor='white', font_family='Calibri',
                   legend_title='Gender', title_font_color=NAVY)

# Fig 2 — Chest pain type
fig2 = px.bar(cp_df, x='cp_label', y='disease_rate_pct',
              color='disease_rate_pct',
              color_continuous_scale=['#D6E4F0', NAVY],
              text='disease_rate_pct',
              labels={'disease_rate_pct':'Disease Rate (%)','cp_label':'Chest Pain Type'},
              title='Disease Rate by Chest Pain Type')
fig2.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
fig2.update_layout(plot_bgcolor=BG, paper_bgcolor='white', font_family='Calibri',
                   title_font_color=NAVY, coloraxis_showscale=False)

# Fig 3 — Scatter: Age vs Max HR coloured by disease
fig3 = px.scatter(df, x='age', y='thalach', color='target_label',
                  color_discrete_map={'Heart Disease':RED,'No Disease':NAVY},
                  opacity=0.55, size_max=6,
                  trendline='ols',
                  labels={'age':'Age','thalach':'Max Heart Rate','target_label':'Diagnosis'},
                  title='Age vs Max Heart Rate by Diagnosis')
fig3.update_layout(plot_bgcolor=BG, paper_bgcolor='white', font_family='Calibri',
                   title_font_color=NAVY)

# Fig 4 — Feature importance
fig4 = px.bar(fi, x='importance', y='feature', orientation='h',
              color='importance', color_continuous_scale=['#D6E4F0', NAVY],
              labels={'importance':'Importance Score','feature':'Feature'},
              title='Random Forest — Feature Importance')
fig4.update_layout(plot_bgcolor=BG, paper_bgcolor='white', font_family='Calibri',
                   title_font_color=NAVY, coloraxis_showscale=False,
                   yaxis={'categoryorder':'total ascending'})

# Fig 5 — ROC Curve
fig5 = go.Figure()
fig5.add_trace(go.Scatter(x=fpr, y=tpr, mode='lines', name=f'ROC (AUC={auc:.3f})',
                          line=dict(color=NAVY, width=2.5)))
fig5.add_trace(go.Scatter(x=[0,1], y=[0,1], mode='lines', name='Random',
                          line=dict(color=GREY, dash='dash', width=1)))
fig5.add_trace(go.Scatter(x=fpr, y=tpr, fill='tozeroy',
                          fillcolor='rgba(26,60,94,0.1)', mode='none', showlegend=False))
fig5.update_layout(title=f'ROC Curve — AUC: {auc:.3f}',
                   xaxis_title='False Positive Rate', yaxis_title='True Positive Rate',
                   plot_bgcolor=BG, paper_bgcolor='white', font_family='Calibri',
                   title_font_color=NAVY)

# Fig 6 — Confusion matrix
fig6 = px.imshow(cm, labels=dict(x='Predicted', y='Actual', color='Count'),
                 x=['No Disease','Heart Disease'], y=['No Disease','Heart Disease'],
                 color_continuous_scale=['white', NAVY],
                 text_auto=True, title='Confusion Matrix (Random Forest)')
fig6.update_layout(paper_bgcolor='white', font_family='Calibri',
                   title_font_color=NAVY)

# Fig 7 — Chol violin by diagnosis
fig7 = go.Figure()
for t, c, lbl in [(0, NAVY,'No Disease'),(1, RED,'Heart Disease')]:
    sub = df[df['target']==t]['chol']
    fig7.add_trace(go.Violin(y=sub, name=lbl, fillcolor=c,
                             line_color='white', opacity=0.75,
                             box_visible=True, meanline_visible=True))
fig7.update_layout(title='Cholesterol Distribution by Diagnosis',
                   yaxis_title='Serum Cholesterol (mg/dl)',
                   plot_bgcolor=BG, paper_bgcolor='white', font_family='Calibri',
                   title_font_color=NAVY)

# Fig 8 — CV scores bar
fig8 = go.Figure(go.Bar(
    x=[f'Fold {i+1}' for i in range(5)], y=cv_scores,
    marker_color=[GREEN if s>0.85 else AMBER for s in cv_scores],
    text=[f'{s:.3f}' for s in cv_scores], textposition='outside'))
fig8.add_hline(y=cv_scores.mean(), line_dash='dash', line_color=NAVY,
               annotation_text=f'Mean AUC: {cv_scores.mean():.3f}')
fig8.update_layout(title='5-Fold Cross-Validation AUC Scores',
                   yaxis_title='AUC Score', yaxis_range=[0.7, 1.0],
                   plot_bgcolor=BG, paper_bgcolor='white', font_family='Calibri',
                   title_font_color=NAVY)

# ── ASSEMBLE HTML ─────────────────────────────────────────────
def fig_html(fig, div_id, h=420):
    return fig.to_html(full_html=False, include_plotlyjs=False,
                       div_id=div_id, default_height=f'{h}px')

report_text = classification_report(y_test, y_pred,
    target_names=['No Disease','Heart Disease'])

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Healthcare Analytics Dashboard | Fudayl Abdul Jalil</title>
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:'Calibri',sans-serif;background:#f0f2f5;color:#222}}
  .header{{background:linear-gradient(135deg,#1A3C5E 0%,#217346 100%);
           color:white;padding:28px 40px;}}
  .header h1{{font-size:22px;font-weight:700;letter-spacing:0.5px}}
  .header p{{font-size:13px;opacity:0.85;margin-top:6px}}
  .badge{{display:inline-block;background:rgba(255,255,255,0.2);
          border:1px solid rgba(255,255,255,0.4);border-radius:4px;
          padding:3px 10px;font-size:11px;margin:6px 4px 0 0}}
  .kpi-row{{display:flex;gap:14px;padding:22px 40px 0;flex-wrap:wrap}}
  .kpi{{background:white;border-radius:8px;padding:16px 20px;flex:1;
        min-width:130px;border-top:3px solid #1A3C5E;
        box-shadow:0 1px 4px rgba(0,0,0,0.08)}}
  .kpi .val{{font-size:26px;font-weight:700;color:#1A3C5E}}
  .kpi .lbl{{font-size:11px;color:#595959;margin-top:3px}}
  .section{{padding:22px 40px 0}}
  .section h2{{font-size:14px;font-weight:700;color:#1A3C5E;
               border-left:4px solid #217346;padding-left:10px;margin-bottom:14px}}
  .grid-2{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
  .grid-3{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px}}
  .card{{background:white;border-radius:8px;padding:16px;
         box-shadow:0 1px 4px rgba(0,0,0,0.08)}}
  .sql-block{{background:#1e1e2e;color:#cdd6f4;border-radius:8px;
              padding:16px;font-family:monospace;font-size:12px;
              line-height:1.7;overflow-x:auto;white-space:pre}}
  .kw{{color:#89b4fa}} .fn{{color:#a6e3a1}} .cm{{color:#585b70;font-style:italic}}
  .step{{display:flex;gap:14px;margin-bottom:14px;align-items:flex-start}}
  .step-num{{background:#1A3C5E;color:white;border-radius:50%;
             width:28px;height:28px;display:flex;align-items:center;
             justify-content:center;font-size:12px;font-weight:700;flex-shrink:0}}
  .step-body h4{{font-size:13px;color:#1A3C5E;margin-bottom:3px}}
  .step-body p{{font-size:12px;color:#595959;line-height:1.5}}
  .tag{{display:inline-block;border-radius:4px;padding:2px 8px;
        font-size:11px;font-weight:600;margin-right:4px}}
  .tag-r{{background:#fff0f0;color:#C0392B}}
  .tag-g{{background:#f0fff4;color:#217346}}
  .tag-b{{background:#e8f0fe;color:#1A3C5E}}
  .report-pre{{background:#f8f9fa;border:1px solid #dee2e6;border-radius:6px;
               padding:14px;font-family:monospace;font-size:12px;
               line-height:1.6;white-space:pre}}
  footer{{text-align:center;padding:30px;font-size:12px;color:#888;margin-top:20px}}
  @media(max-width:768px){{.grid-2,.grid-3{{grid-template-columns:1fr}}
    .kpi-row{{padding:16px}}.section{{padding:16px 16px 0}}
    .header{{padding:20px}}}}
</style>
</head>
<body>

<div class="header">
  <h1>🏥 Healthcare Analytics Dashboard</h1>
  <p>Heart Disease Risk Analysis — Machine Learning & Clinical Insights</p>
  <div style="margin-top:10px">
    <span class="badge">📊 Power BI-style Analytics</span>
    <span class="badge">🐍 Python · pandas · scikit-learn · Plotly</span>
    <span class="badge">🗄️ SQL · SQLite</span>
    <span class="badge">📁 Dataset: UCI ML Repository</span>
    <span class="badge">👤 Fudayl Abdul Jalil</span>
  </div>
</div>

<!-- KPI Row -->
<div class="kpi-row">
  <div class="kpi"><div class="val">{int(summary['total_patients']):,}</div><div class="lbl">Total Patients</div></div>
  <div class="kpi"><div class="val" style="color:#C0392B">{int(summary['disease_cases']):,}</div><div class="lbl">Disease Cases</div></div>
  <div class="kpi"><div class="val">{summary['prevalence_pct']:.1f}%</div><div class="lbl">Prevalence Rate</div></div>
  <div class="kpi"><div class="val">{summary['avg_age']:.0f}</div><div class="lbl">Avg Patient Age</div></div>
  <div class="kpi"><div class="val">{summary['avg_chol']:.0f}</div><div class="lbl">Avg Cholesterol (mg/dl)</div></div>
  <div class="kpi"><div class="val" style="color:#217346">{auc:.3f}</div><div class="lbl">Model AUC Score</div></div>
  <div class="kpi"><div class="val">{cv_scores.mean():.3f}</div><div class="lbl">5-Fold CV AUC (mean)</div></div>
</div>

<!-- Data Pipeline -->
<div class="section" style="margin-top:22px">
  <h2>Step-by-Step: From Raw Data to Dashboard</h2>
  <div class="card">
    <div class="step">
      <div class="step-num">1</div>
      <div class="step-body">
        <h4>Data Source</h4>
        <p>Dataset obtained from the <strong>UCI Machine Learning Repository</strong> —
        Heart Disease dataset (Cleveland Clinic Foundation, 1988).<br>
        🔗 <a href="https://archive.ics.uci.edu/dataset/45/heart+disease" target="_blank">
        https://archive.ics.uci.edu/dataset/45/heart+disease</a><br>
        Kaggle mirror: <a href="https://www.kaggle.com/datasets/ronitf/heart-disease-uci" target="_blank">
        kaggle.com/datasets/ronitf/heart-disease-uci</a><br>
        1,025 patient records · 14 clinical features · Binary classification target</p>
      </div>
    </div>
    <div class="step">
      <div class="step-num">2</div>
      <div class="step-body">
        <h4>Data Quality Issues Found</h4>
        <p>
          <span class="tag tag-r">8 rows</span> Impossible age values (999) — data entry error → removed<br>
          <span class="tag tag-r">5 rows</span> Negative cholesterol values (-1) — physically invalid → removed<br>
          <span class="tag tag-r">13 nulls</span> Missing blood pressure (trestbps) → median imputed<br>
          <span class="tag tag-r">15 nulls</span> Missing cholesterol (chol) → median imputed (right-skewed dist)<br>
          <span class="tag tag-r">12 nulls</span> Missing max heart rate (thalach) → median imputed
        </p>
      </div>
    </div>
    <div class="step">
      <div class="step-num">3</div>
      <div class="step-body">
        <h4>Cleaning Decisions — Justified</h4>
        <p>Median chosen over mean for blood pressure and cholesterol because both distributions
        are right-skewed (confirmed by IQR analysis). Rows with impossible values were dropped
        rather than imputed — 13 rows out of 1,025 is a 1.3% loss, acceptable without risking
        model contamination from fabricated data. Final dataset: <strong>1,012 rows · 18 columns</strong>
        including 4 derived label fields for readability.</p>
      </div>
    </div>
    <div class="step">
      <div class="step-num">4</div>
      <div class="step-body">
        <h4>SQL Queries (SQLite)</h4>
        <p>Clean data loaded into SQLite. SQL used for aggregations and risk profiling before
        passing to the ML pipeline and visualisation layer.</p>
      </div>
    </div>
    <div class="step">
      <div class="step-num">5</div>
      <div class="step-body">
        <h4>Machine Learning — Random Forest Classifier</h4>
        <p>Random Forest trained on 80% of data (stratified split). 5-fold cross-validation
        used to assess generalisation. Feature importance extracted to explain model decisions.
        <strong>AUC: {auc:.3f} · CV Mean AUC: {cv_scores.mean():.3f}</strong></p>
      </div>
    </div>
  </div>
</div>

<!-- SQL section -->
<div class="section" style="margin-top:18px">
  <h2>SQL Queries Used</h2>
  <div class="grid-2">
    <div class="card">
      <p style="font-size:12px;color:#595959;margin-bottom:10px;font-weight:600">Risk Profile by Age & Gender</p>
      <div class="sql-block"><span class="kw">SELECT</span> age_group, sex_label,
       <span class="fn">COUNT</span>(*) <span class="kw">AS</span> total,
       <span class="fn">SUM</span>(target) <span class="kw">AS</span> disease_count,
       <span class="fn">ROUND</span>(<span class="fn">AVG</span>(target)*100, 1)
           <span class="kw">AS</span> disease_rate_pct,
       <span class="fn">ROUND</span>(<span class="fn">AVG</span>(chol), 1) <span class="kw">AS</span> avg_chol
<span class="kw">FROM</span> heart
<span class="kw">GROUP BY</span> age_group, sex_label
<span class="kw">ORDER BY</span> age_group, sex_label</div>
    </div>
    <div class="card">
      <p style="font-size:12px;color:#595959;margin-bottom:10px;font-weight:600">Chest Pain Type Analysis</p>
      <div class="sql-block"><span class="kw">SELECT</span> cp_label,
       <span class="fn">COUNT</span>(*) <span class="kw">AS</span> total,
       <span class="fn">SUM</span>(target) <span class="kw">AS</span> disease_count,
       <span class="fn">ROUND</span>(<span class="fn">AVG</span>(target)*100,1)
           <span class="kw">AS</span> disease_rate_pct,
       <span class="fn">ROUND</span>(<span class="fn">AVG</span>(oldpeak),2)
           <span class="kw">AS</span> avg_st_depression
<span class="kw">FROM</span> heart
<span class="kw">GROUP BY</span> cp_label
<span class="kw">ORDER BY</span> disease_rate_pct <span class="kw">DESC</span></div>
    </div>
  </div>
</div>

<!-- Charts row 1 -->
<div class="section" style="margin-top:18px">
  <h2>Risk Analysis</h2>
  <div class="grid-2">
    <div class="card">{fig_html(fig1,'fig1',400)}</div>
    <div class="card">{fig_html(fig2,'fig2',400)}</div>
  </div>
</div>

<div class="section" style="margin-top:16px">
  <div class="grid-2">
    <div class="card">{fig_html(fig7,'fig7',400)}</div>
    <div class="card">{fig_html(fig3,'fig3',400)}</div>
  </div>
</div>

<!-- ML Section -->
<div class="section" style="margin-top:18px">
  <h2>Machine Learning — Random Forest Classifier</h2>
  <div class="grid-3">
    <div class="card">{fig_html(fig4,'fig4',380)}</div>
    <div class="card">{fig_html(fig5,'fig5',380)}</div>
    <div class="card">{fig_html(fig8,'fig8',380)}</div>
  </div>
</div>

<div class="section" style="margin-top:16px">
  <div class="grid-2">
    <div class="card">{fig_html(fig6,'fig6',380)}</div>
    <div class="card">
      <p style="font-size:12px;color:#595959;font-weight:600;margin-bottom:10px">
        Classification Report (Test Set — 20%)</p>
      <div class="report-pre">{report_text}</div>
      <div style="margin-top:14px;font-size:12px;color:#595959">
        <p><strong>Model Config:</strong> RandomForestClassifier(n_estimators=200, max_depth=8,
        random_state=42) · 80/20 stratified split · 5-fold CV</p>
        <p style="margin-top:6px"><strong>Key finding:</strong> <code>ca</code> (vessels coloured),
        <code>oldpeak</code> (ST depression), and <code>thal</code> are the top predictive features.
        Asymptomatic chest pain (cp=0) paradoxically has the highest disease rate —
        consistent with published clinical research.</p>
      </div>
    </div>
  </div>
</div>

<footer>
  <p><strong>Fudayl Abdul Jalil</strong> · Data Analytics Portfolio · Dashboard 1 of 3</p>
  <p style="margin-top:4px">Dataset: <a href="https://archive.ics.uci.edu/dataset/45/heart+disease">
  UCI Heart Disease</a> · Tools: Python, pandas, scikit-learn, Plotly, SQL</p>
  <p style="margin-top:4px">github.com/fudayl-abdul-jalil</p>
</footer>

</body>
</html>"""

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"✓ Dashboard saved → {OUT}")
print(f"  File size: {os.path.getsize(OUT)/1024/1024:.1f} MB")
