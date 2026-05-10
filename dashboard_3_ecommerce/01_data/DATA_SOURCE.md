# Dashboard 3 — Data Source

## Dataset: Brazilian E-Commerce (Olist) — Kaggle

| Detail | Info |
|--------|------|
| **Source** | Kaggle — Brazilian E-Commerce Public Dataset by Olist |
| **Direct Link** | https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce |
| **License** | CC BY-NC-SA 4.0 |
| **Domain** | E-Commerce / Retail Analytics |
| **Records** | ~8,000 orders (subset of 100K original) |
| **Features** | Orders, payments, reviews, products, customers, sellers |
| **Period** | October 2016 – August 2018 |

## Why This Dataset?

The Olist dataset is a real-world multi-table e-commerce dataset with:
- **Time series analysis** — order volume trends, seasonality
- **Customer behaviour** — review scores, repeat purchasing
- **Operational analytics** — delivery performance, freight analysis
- **Geographic analysis** — state-level revenue and logistics
- **Statistical testing** — comparing delivery performance across regions

## Key Tables Used (Simplified to Single Table)

| Column | Description |
|--------|-------------|
| `order_id` | Unique order identifier |
| `customer_id` | Customer identifier |
| `seller_id` | Seller identifier |
| `order_date` | Date order was placed |
| `product_category` | Product category |
| `payment_type` | credit_card, boleto, voucher, debit_card |
| `payment_installments` | Number of payment installments |
| `price` | Item price (BRL) |
| `freight_value` | Freight cost (BRL) |
| `total_value` | Total order value |
| `review_score` | Customer review (1–5) |
| `customer_state` | Brazilian state code |
| `on_time_delivery` | 1 = delivered on/before estimated date |
| `delivery_days` | Actual delivery duration (days) |

## Download Instructions (to reproduce)

```bash
# Kaggle CLI (requires free account)
kaggle datasets download -d olistbr/brazilian-ecommerce
unzip brazilian-ecommerce.zip

# Direct link
# https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce/download

# Use this repo's file
# File: 01_data/ecommerce_raw.csv
```
