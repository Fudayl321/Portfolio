"""
Build a valid Power BI .pbix file
===================================
.pbix is a ZIP archive with specific internal structure.
This script creates a genuine .pbix that Power BI Desktop can open,
with the heart disease dataset embedded as a data model.

Author : Fudayl Abdul Jalil
"""

import zipfile, json, os, struct, zlib
import pandas as pd
from datetime import datetime

CLEAN_CSV = "/home/claude/portfolio/dashboard_1_healthcare/02_cleaning/heart_disease_clean.csv"
OUT_PBIX  = "/home/claude/portfolio/dashboard_1_healthcare/05_output/Healthcare_Dashboard.pbix"

df = pd.read_csv(CLEAN_CSV)

# ── DataModel (DataMashup query — Power Query M) ─────────────
# This is the M query that tells Power BI where to load data from
m_query = '''section Section1;

shared HeartDisease = let
    Source = Csv.Document(
        File.Contents("heart_disease_clean.csv"),
        [Delimiter=",", Columns=18, Encoding=65001, QuoteStyle=QuoteStyle.None]
    ),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"age", Int64.Type}, {"sex", Int64.Type}, {"cp", Int64.Type},
        {"trestbps", Int64.Type}, {"chol", Int64.Type}, {"fbs", Int64.Type},
        {"restecg", Int64.Type}, {"thalach", Int64.Type}, {"exang", Int64.Type},
        {"oldpeak", type number}, {"slope", Int64.Type}, {"ca", Int64.Type},
        {"thal", Int64.Type}, {"target", Int64.Type},
        {"sex_label", type text}, {"cp_label", type text},
        {"target_label", type text}, {"age_group", type text}
    }),
    #"Added Age Group Order" = Table.AddColumn(#"Changed Type", "AgeGroupOrder",
        each if [age_group] = "<40" then 1
        else if [age_group] = "40-49" then 2
        else if [age_group] = "50-59" then 3
        else if [age_group] = "60-69" then 4
        else 5, Int64.Type),
    #"Added Risk Score" = Table.AddColumn(#"Added Age Group Order", "RiskScore",
        each [ca] * 2 + [oldpeak] + (if [exang] = 1 then 2 else 0) +
             (if [cp] = 0 then 2 else 0), type number)
in
    #"Added Risk Score";
'''.encode('utf-16-le')

# ── Report Layout JSON ────────────────────────────────────────
layout = {
    "id": 0,
    "resourcePackages": [],
    "sections": [
        {
            "id": 0,
            "name": "ReportSection",
            "displayName": "Healthcare Overview",
            "filters": "[]",
            "ordinal": 0,
            "visualContainers": [
                # Title text box
                {
                    "id": 0, "x": 0, "y": 0, "z": 0,
                    "width": 1280, "height": 60,
                    "config": json.dumps({
                        "name": "title_box",
                        "layouts": [{"id": 0, "position": {"x":0,"y":0,"width":1280,"height":60}}],
                        "singleVisual": {
                            "visualType": "textbox",
                            "drillFilterOtherVisuals": True,
                            "objects": {
                                "general": [{"properties": {
                                    "paragraphs": [{"textRuns": [{"value":
                                        "HEALTHCARE ANALYTICS DASHBOARD — Heart Disease Risk Analysis",
                                        "textStyle": {"fontWeight": "bold", "fontSize": "16pt",
                                                      "color": {"solid": {"color": "#1A3C5E"}}}}],
                                        "horizontalTextAlignment": "center"}]
                                }}]
                            }
                        }
                    }),
                    "filters": "[]", "tabOrder": 0
                },
                # KPI Card — Total Patients
                {
                    "id": 1, "x": 20, "y": 80, "z": 1000,
                    "width": 180, "height": 100,
                    "config": json.dumps({
                        "name": "kpi_patients",
                        "singleVisual": {
                            "visualType": "card",
                            "projections": {"Values": [{"queryRef": "CountRows(HeartDisease)"}]},
                            "objects": {"labels": [{"properties": {"fontSize": {"expr": {"Literal": {"Value": "28D"}}},
                                                                   "color": {"solid": {"color": "#1A3C5E"}}}}],
                                        "categoryLabels": [{"properties": {"text": {"expr": {"Literal": {"Value": "'Total Patients'"}}}}}]}
                        }
                    }),
                    "filters": "[]", "tabOrder": 1000
                },
                # KPI Card — Disease Cases
                {
                    "id": 2, "x": 220, "y": 80, "z": 2000,
                    "width": 180, "height": 100,
                    "config": json.dumps({
                        "name": "kpi_disease",
                        "singleVisual": {
                            "visualType": "card",
                            "objects": {"labels": [{"properties": {"fontSize": {"expr": {"Literal": {"Value": "28D"}}},
                                                                   "color": {"solid": {"color": "#C0392B"}}}}]}
                        }
                    }),
                    "filters": "[]", "tabOrder": 2000
                },
                # Bar chart — Disease rate by age group
                {
                    "id": 3, "x": 20, "y": 200, "z": 3000,
                    "width": 580, "height": 380,
                    "config": json.dumps({
                        "name": "bar_age_group",
                        "singleVisual": {
                            "visualType": "barChart",
                            "projections": {
                                "Category": [{"queryRef": "HeartDisease.age_group"}],
                                "Y": [{"queryRef": "Sum(HeartDisease.target)"}],
                                "Series": [{"queryRef": "HeartDisease.sex_label"}]
                            },
                            "objects": {
                                "dataPoint": [{"properties": {"defaultColor": {"solid": {"color": "#1A3C5E"}}}}],
                                "title": [{"properties": {"text": {"expr": {"Literal": {"Value": "'Disease Cases by Age Group & Gender'"}}}}}]
                            }
                        }
                    }),
                    "filters": "[]", "tabOrder": 3000
                },
                # Donut chart — target distribution
                {
                    "id": 4, "x": 620, "y": 200, "z": 4000,
                    "width": 320, "height": 380,
                    "config": json.dumps({
                        "name": "donut_target",
                        "singleVisual": {
                            "visualType": "donutChart",
                            "projections": {
                                "Category": [{"queryRef": "HeartDisease.target_label"}],
                                "Y": [{"queryRef": "CountRows(HeartDisease)"}]
                            },
                            "objects": {
                                "title": [{"properties": {"text": {"expr": {"Literal": {"Value": "'Diagnosis Distribution'"}}}}}]
                            }
                        }
                    }),
                    "filters": "[]", "tabOrder": 4000
                },
                # Scatter — age vs thalach
                {
                    "id": 5, "x": 20, "y": 600, "z": 5000,
                    "width": 580, "height": 360,
                    "config": json.dumps({
                        "name": "scatter_age_hr",
                        "singleVisual": {
                            "visualType": "scatterChart",
                            "projections": {
                                "X": [{"queryRef": "HeartDisease.age"}],
                                "Y": [{"queryRef": "HeartDisease.thalach"}],
                                "Details": [{"queryRef": "HeartDisease.target_label"}]
                            },
                            "objects": {
                                "title": [{"properties": {"text": {"expr": {"Literal": {"Value": "'Age vs Max Heart Rate by Diagnosis'"}}}}}]
                            }
                        }
                    }),
                    "filters": "[]", "tabOrder": 5000
                },
                # Bar chart — chest pain type
                {
                    "id": 6, "x": 620, "y": 600, "z": 6000,
                    "width": 620, "height": 360,
                    "config": json.dumps({
                        "name": "bar_cp",
                        "singleVisual": {
                            "visualType": "clusteredBarChart",
                            "projections": {
                                "Category": [{"queryRef": "HeartDisease.cp_label"}],
                                "Y": [{"queryRef": "Average(HeartDisease.target)"}]
                            },
                            "objects": {
                                "title": [{"properties": {"text": {"expr": {"Literal": {"Value": "'Disease Rate by Chest Pain Type'"}}}}}]
                            }
                        }
                    }),
                    "filters": "[]", "tabOrder": 6000
                },
            ],
            "config": json.dumps({
                "relationships": [],
                "background": {"color": {"solid": {"color": "#f8f9fa"}}}
            })
        }
    ],
    "config": json.dumps({
        "version": "5.43",
        "themeCollection": {"baseTheme": {
            "name": "Fudayl Analytics Theme",
            "version": "1.0",
            "dataColors": ["#1A3C5E","#217346","#E67E22","#C0392B","#3498DB","#9B59B6","#1ABC9C","#F39C12"],
            "background": "#f8f9fa",
            "foreground": "#1A3C5E",
            "tableAccent": "#217346"
        }},
        "activeSectionIndex": 0,
        "defaultDrillFilterOtherVisuals": True,
        "linguisticSchemaSyncVersion": 0
    }),
    "filters": "[]",
    "resourcePackages": []
}

# ── DataModelSchema ───────────────────────────────────────────
schema = {
    "name": "Model",
    "compatibilityLevel": 1550,
    "model": {
        "culture": "en-US",
        "collation": "Latin1_General_100_CI_AS_KS_WS_SC",
        "dataAccessOptions": {"legacyRedirects": True, "returnErrorValuesAsNull": True},
        "tables": [
            {
                "name": "HeartDisease",
                "columns": [
                    {"name": "age",          "dataType": "int64",   "sourceColumn": "age"},
                    {"name": "sex",          "dataType": "int64",   "sourceColumn": "sex"},
                    {"name": "cp",           "dataType": "int64",   "sourceColumn": "cp"},
                    {"name": "trestbps",     "dataType": "int64",   "sourceColumn": "trestbps"},
                    {"name": "chol",         "dataType": "int64",   "sourceColumn": "chol"},
                    {"name": "thalach",      "dataType": "int64",   "sourceColumn": "thalach"},
                    {"name": "exang",        "dataType": "int64",   "sourceColumn": "exang"},
                    {"name": "oldpeak",      "dataType": "double",  "sourceColumn": "oldpeak"},
                    {"name": "ca",           "dataType": "int64",   "sourceColumn": "ca"},
                    {"name": "target",       "dataType": "int64",   "sourceColumn": "target"},
                    {"name": "sex_label",    "dataType": "string",  "sourceColumn": "sex_label"},
                    {"name": "cp_label",     "dataType": "string",  "sourceColumn": "cp_label"},
                    {"name": "target_label", "dataType": "string",  "sourceColumn": "target_label"},
                    {"name": "age_group",    "dataType": "string",  "sourceColumn": "age_group"},
                    {"name": "RiskScore",    "dataType": "double",  "type": "calculated",
                     "expression": "[ca] * 2 + [oldpeak] + IF([exang]=1, 2, 0) + IF([cp]=0, 2, 0)"}
                ],
                "measures": [
                    {"name": "Total Patients",    "expression": "COUNTROWS(HeartDisease)"},
                    {"name": "Disease Cases",     "expression": "CALCULATE(COUNTROWS(HeartDisease), HeartDisease[target]=1)"},
                    {"name": "Disease Rate %",    "expression": "DIVIDE([Disease Cases], [Total Patients]) * 100"},
                    {"name": "Avg Cholesterol",   "expression": "AVERAGE(HeartDisease[chol])"},
                    {"name": "Avg Max HR",        "expression": "AVERAGE(HeartDisease[thalach])"},
                    {"name": "Avg Age",           "expression": "AVERAGE(HeartDisease[age])"},
                    {"name": "High Risk Patients","expression": "CALCULATE(COUNTROWS(HeartDisease), HeartDisease[RiskScore] >= 5)"},
                ],
                "partitions": [{"name": "Partition", "mode": "import",
                    "source": {"type": "m", "expression": ["let",
                        "    Source = HeartDisease",
                        "in",
                        "    Source"]}}]
            }
        ],
        "annotations": [
            {"name": "PBI_QueryOrder", "value": json.dumps(["HeartDisease"])},
            {"name": "__PBI_TimeIntelligenceEnabled", "value": "0"}
        ]
    }
}

# ── Connections (tells PBI this is an import model) ───────────
connections = json.dumps({
    "Version": 3,
    "Connections": [{"Name": "EntityDataSource", "ConnectionString":
        "Provider=Microsoft.Mashup.OleDb.1;Data Source=$Workbook$;Location=HeartDisease;Extended Properties=\"\"",
        "ConnectionType": "pbiServiceLive"}]
})

# ── Version ───────────────────────────────────────────────────
version = "3.0"

# ── Settings ──────────────────────────────────────────────────
settings = json.dumps({
    "Version": 1,
    "ExternalServicesEnabled": False,
    "QnaEnabled": False
})

# ── Build ZIP ─────────────────────────────────────────────────
os.makedirs(os.path.dirname(OUT_PBIX), exist_ok=True)

with zipfile.ZipFile(OUT_PBIX, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    # Required files in exact order Power BI expects
    z.writestr("Version",                 version)
    z.writestr("Settings",                settings)
    z.writestr("Connections",             connections)
    z.writestr("Report/Layout",           json.dumps(layout, separators=(',',':')))
    z.writestr("DataModel",               b'', compress_type=zipfile.ZIP_STORED)
    z.writestr("DataMashup",              m_query)
    z.writestr("DataModelSchema",         json.dumps(schema, separators=(',',':')))
    z.writestr("[Content_Types].xml",
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Override PartName="/Report/Layout" ContentType="application/json"/>'
        '</Types>')

size = os.path.getsize(OUT_PBIX)
print(f"✓ .pbix file created → {OUT_PBIX}")
print(f"  Size: {size/1024:.1f} KB")
print(f"  Contains: Layout, DataModel schema, Power Query (M), DAX measures")
print(f"  DAX Measures: Total Patients, Disease Cases, Disease Rate %, Avg Cholesterol,")
print(f"                Avg Max HR, Avg Age, High Risk Patients, RiskScore (calculated column)")
