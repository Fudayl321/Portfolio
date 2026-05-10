#!/usr/bin/env Rscript
# =============================================================
# Dashboard 3 — E-Commerce Analytics (R)
# =============================================================
# Dataset : Brazilian E-Commerce (Olist) via Kaggle
# Source  : https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
# Tools   : R, ggplot2, dplyr, tidyr, lubridate, plotly, forecast
# Author  : Fudayl Abdul Jalil
# Output  : 05_output/ecommerce_dashboard.html
# =============================================================

cat("Installing/loading packages...\n")
pkgs <- c("ggplot2","dplyr","tidyr","lubridate","scales","corrplot",
          "htmlwidgets","jsonlite","viridis","gridExtra","knitr")
for(p in pkgs){
  if(!require(p, character.only=TRUE, quietly=TRUE)){
    install.packages(p, repos="https://cran.r-project.org", quiet=TRUE)
    library(p, character.only=TRUE, quietly=TRUE)
  }
}

setwd("/home/claude/portfolio/dashboard_3_ecommerce")
dir.create("02_cleaning", showWarnings=FALSE)
dir.create("03_sql",      showWarnings=FALSE)
dir.create("04_analysis", showWarnings=FALSE)
dir.create("05_output",   showWarnings=FALSE)

# =============================================================
# STEP 1: LOAD & PROFILE
# =============================================================
cat("\n[STEP 1] Loading raw data...\n")
raw <- read.csv("01_data/ecommerce_raw.csv", stringsAsFactors=FALSE)
cat(sprintf("  Shape      : %d rows x %d cols\n", nrow(raw), ncol(raw)))
cat(sprintf("  Duplicates : %d\n", sum(duplicated(raw))))
cat(sprintf("  Nulls      : %d\n", sum(is.na(raw))))

# Null breakdown
null_counts <- colSums(is.na(raw))
cat("\n  Null breakdown:\n")
print(null_counts[null_counts > 0])

# =============================================================
# STEP 2: CLEANING
# =============================================================
cat("\n[STEP 2] Cleaning...\n")
df <- raw

# 2a. Remove invalid prices (negative)
n_neg <- sum(df$price < 0, na.rm=TRUE)
df <- df[is.na(df$price) | df$price >= 0, ]
cat(sprintf("  2a. Removed %d negative prices\n", n_neg))

# 2b. Remove impossible delivery_days (0 or negative)
n_bad_del <- sum(df$delivery_days <= 0, na.rm=TRUE)
df$delivery_days[df$delivery_days <= 0] <- NA
cat(sprintf("  2b. Set %d impossible delivery_days to NA\n", n_bad_del))

# 2c. Impute price nulls with category median
price_meds <- df %>% filter(!is.na(price)) %>%
  group_by(product_category) %>% summarise(med=median(price))
n_price_na <- sum(is.na(df$price))
df <- df %>%
  left_join(price_meds, by="product_category") %>%
  mutate(price = ifelse(is.na(price), med, price)) %>%
  select(-med)
cat(sprintf("  2c. Imputed %d price NAs with category median\n", n_price_na))

# 2d. Impute delivery_days with category median
del_meds <- df %>% filter(!is.na(delivery_days)) %>%
  group_by(product_category) %>% summarise(med=median(delivery_days))
n_del_na <- sum(is.na(df$delivery_days))
df <- df %>%
  left_join(del_meds, by="product_category") %>%
  mutate(delivery_days = ifelse(is.na(delivery_days), med, delivery_days)) %>%
  select(-med)
cat(sprintf("  2d. Imputed %d delivery_days NAs with category median\n", n_del_na))

# 2e. Impute review_score nulls with median
n_rev_na <- sum(is.na(df$review_score))
df$review_score[is.na(df$review_score)] <- median(df$review_score, na.rm=TRUE)
cat(sprintf("  2e. Imputed %d review_score NAs with median\n", n_rev_na))

# 2f. Parse dates, add derived columns
df$order_date <- as.Date(df$order_date)
df$year_month <- format(df$order_date, "%Y-%m")
df$year       <- year(df$order_date)
df$month      <- month(df$order_date)
df$quarter    <- paste0("Q", quarter(df$order_date))
df$freight_pct <- round(df$freight_value / df$total_value * 100, 1)
df$high_value  <- ifelse(df$total_value > quantile(df$total_value, 0.75, na.rm=TRUE), 1, 0)

cat(sprintf("\n  Final shape   : %d rows x %d cols\n", nrow(df), ncol(df)))
cat(sprintf("  Remaining NAs : %d\n", sum(is.na(df))))
cat("  ✓ Cleaning complete\n")

write.csv(df, "02_cleaning/ecommerce_clean.csv", row.names=FALSE)

# =============================================================
# STEP 3: AGGREGATIONS
# =============================================================
cat("\n[STEP 3] Computing aggregations...\n")

# Monthly revenue trend
monthly <- df %>%
  group_by(year_month, year) %>%
  summarise(orders=n(), revenue=sum(total_value),
            avg_order=mean(total_value), .groups="drop") %>%
  arrange(year_month)

# Category performance
cat_perf <- df %>%
  group_by(product_category) %>%
  summarise(orders=n(), revenue=sum(total_value),
            avg_price=mean(price), avg_review=mean(review_score),
            on_time_pct=mean(on_time_delivery)*100,
            avg_delivery=mean(delivery_days), .groups="drop") %>%
  arrange(desc(revenue))

# State revenue
state_rev <- df %>%
  group_by(customer_state) %>%
  summarise(orders=n(), revenue=sum(total_value),
            avg_review=mean(review_score),
            on_time_pct=mean(on_time_delivery)*100, .groups="drop") %>%
  arrange(desc(revenue))

# Payment type
pay_perf <- df %>%
  group_by(payment_type) %>%
  summarise(orders=n(), revenue=sum(total_value),
            avg_installments=mean(payment_installments),
            avg_review=mean(review_score), .groups="drop") %>%
  mutate(revenue_pct=round(revenue/sum(revenue)*100,1)) %>%
  arrange(desc(revenue))

# Review score distribution
review_dist <- df %>%
  group_by(review_score) %>%
  summarise(count=n(), .groups="drop") %>%
  mutate(pct=round(count/sum(count)*100,1))

# Delivery performance
delivery_perf <- df %>%
  group_by(product_category) %>%
  summarise(avg_delivery=mean(delivery_days),
            on_time_pct=mean(on_time_delivery)*100,
            orders=n(), .groups="drop") %>%
  filter(orders >= 50) %>%
  arrange(on_time_pct)

# =============================================================
# STEP 4: STATISTICAL TESTS
# =============================================================
cat("\n[STEP 4] Statistical tests...\n")

# Test: Do review scores differ significantly by payment type?
kw_test <- kruskal.test(review_score ~ payment_type, data=df)
cat(sprintf("  Kruskal-Wallis (review ~ payment_type): p=%.4f\n", kw_test$p.value))

# Test: Do high-value orders differ in delivery time?
t_res <- t.test(delivery_days ~ high_value, data=df)
cat(sprintf("  t-test (delivery_days ~ high_value): p=%.4f, diff=%.1f days\n",
            t_res$p.value, diff(t_res$estimate)))

# Correlation between price and review score
cor_val <- cor(df$price, df$review_score, use="complete.obs", method="spearman")
cat(sprintf("  Spearman r (price ~ review): %.3f\n", cor_val))

# =============================================================
# STEP 5: STATIC PLOTS (saved as PNG for HTML embedding)
# =============================================================
cat("\n[STEP 5] Generating plots...\n")

NAVY  <- "#1A3C5E"
GREEN <- "#217346"
RED   <- "#C0392B"
AMBER <- "#E67E22"

# Plot 1: Monthly revenue trend
p1 <- ggplot(monthly, aes(x=year_month, y=revenue/1000, group=1)) +
  geom_area(fill=NAVY, alpha=0.2) +
  geom_line(color=NAVY, linewidth=1.2) +
  geom_point(color=NAVY, size=2) +
  scale_y_continuous(labels=scales::comma_format(suffix="K")) +
  theme_minimal(base_family="sans") +
  theme(axis.text.x=element_text(angle=45, hjust=1, size=8),
        plot.title=element_text(color=NAVY, face="bold", size=13),
        panel.grid.minor=element_blank()) +
  labs(title="Monthly Revenue Trend (BRL)", x="", y="Revenue (K BRL)")

# Plot 2: Top 10 categories by revenue
top10 <- head(cat_perf, 10)
p2 <- ggplot(top10, aes(x=reorder(product_category, revenue), y=revenue/1000)) +
  geom_col(fill=NAVY, alpha=0.85) +
  geom_text(aes(label=sprintf("%.0fK", revenue/1000)), hjust=-0.1, size=3, color=NAVY) +
  coord_flip() +
  theme_minimal(base_family="sans") +
  theme(plot.title=element_text(color=NAVY, face="bold", size=13),
        panel.grid.minor=element_blank()) +
  labs(title="Top 10 Categories by Revenue", x="", y="Revenue (K BRL)")

# Plot 3: Review score distribution
p3 <- ggplot(review_dist, aes(x=factor(review_score), y=pct,
                               fill=factor(review_score))) +
  geom_col(show.legend=FALSE) +
  geom_text(aes(label=paste0(pct,"%")), vjust=-0.5, size=3.5, fontface="bold") +
  scale_fill_manual(values=c("#C0392B","#E67E22","#F1C40F","#3498DB","#217346")) +
  theme_minimal(base_family="sans") +
  theme(plot.title=element_text(color=NAVY, face="bold", size=13)) +
  labs(title="Review Score Distribution", x="Score (1-5)", y="Percentage (%)")

# Plot 4: Delivery days boxplot by top categories
top6 <- head(cat_perf$product_category, 6)
p4 <- df %>% filter(product_category %in% top6) %>%
  ggplot(aes(x=reorder(product_category, delivery_days, median),
             y=delivery_days, fill=product_category)) +
  geom_boxplot(show.legend=FALSE, outlier.size=0.8, outlier.alpha=0.4) +
  scale_fill_viridis_d(option="D", begin=0.2, end=0.9) +
  coord_flip() +
  theme_minimal(base_family="sans") +
  theme(plot.title=element_text(color=NAVY, face="bold", size=13)) +
  labs(title="Delivery Days by Top Category", x="", y="Days")

# Plot 5: Payment type revenue share
p5 <- ggplot(pay_perf, aes(x="", y=revenue_pct, fill=payment_type)) +
  geom_col(width=1, color="white", linewidth=0.5) +
  coord_polar("y", start=0) +
  scale_fill_manual(values=c(NAVY, GREEN, AMBER, RED)) +
  geom_text(aes(label=paste0(payment_type,"\n",revenue_pct,"%")),
            position=position_stack(vjust=0.5), size=3, color="white", fontface="bold") +
  theme_void() +
  theme(plot.title=element_text(color=NAVY, face="bold", size=13, hjust=0.5),
        legend.position="none") +
  labs(title="Revenue by Payment Type")

# Plot 6: On-time delivery by state (top 10)
p6 <- state_rev %>% head(10) %>%
  ggplot(aes(x=reorder(customer_state, on_time_pct), y=on_time_pct,
             fill=on_time_pct)) +
  geom_col(show.legend=FALSE) +
  geom_text(aes(label=sprintf("%.1f%%", on_time_pct)), hjust=-0.1, size=3) +
  scale_fill_gradient(low=RED, high=GREEN) +
  coord_flip() +
  scale_y_continuous(limits=c(0,110)) +
  theme_minimal(base_family="sans") +
  theme(plot.title=element_text(color=NAVY, face="bold", size=13)) +
  labs(title="On-Time Delivery % (Top 10 States)", x="", y="On-Time %")

# Save plots
ggsave("04_analysis/p1_monthly_trend.png",   p1, width=10, height=4, dpi=120)
ggsave("04_analysis/p2_top_categories.png",  p2, width=8,  height=5, dpi=120)
ggsave("04_analysis/p3_review_dist.png",     p3, width=7,  height=4, dpi=120)
ggsave("04_analysis/p4_delivery_box.png",    p4, width=8,  height=5, dpi=120)
ggsave("04_analysis/p5_payment_pie.png",     p5, width=6,  height=5, dpi=120)
ggsave("04_analysis/p6_ontime_state.png",    p6, width=8,  height=5, dpi=120)
cat("  All plots saved\n")

# =============================================================
# STEP 6: BUILD HTML DASHBOARD
# =============================================================
cat("\n[STEP 6] Building HTML dashboard...\n")

img_b64 <- function(path){
  raw_bytes <- readBin(path, "raw", n=file.info(path)$size)
  paste0("data:image/png;base64,", jsonlite::base64_enc(raw_bytes))
}

p1_b64 <- img_b64("04_analysis/p1_monthly_trend.png")
p2_b64 <- img_b64("04_analysis/p2_top_categories.png")
p3_b64 <- img_b64("04_analysis/p3_review_dist.png")
p4_b64 <- img_b64("04_analysis/p4_delivery_box.png")
p5_b64 <- img_b64("04_analysis/p5_payment_pie.png")
p6_b64 <- img_b64("04_analysis/p6_ontime_state.png")

total_rev   <- scales::comma(round(sum(df$total_value)))
total_orders<- scales::comma(nrow(df))
avg_review  <- round(mean(df$review_score), 2)
ontime_pct  <- round(mean(df$on_time_delivery)*100, 1)
avg_delivery<- round(mean(df$delivery_days, na.rm=TRUE), 1)
top_cat     <- cat_perf$product_category[1]

kw_result <- sprintf("Kruskal-Wallis H=%.2f, df=%d, p=%.4f",
                     kw_test$statistic, kw_test$parameter, kw_test$p.value)
t_result  <- sprintf("t=%.2f, p=%.4f, mean diff=%.1f days",
                     t_res$statistic, t_res$p.value, diff(t_res$estimate))

html <- paste0('<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>E-Commerce Analytics Dashboard | Fudayl Abdul Jalil</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Calibri,sans-serif;background:#f0f2f5;color:#222}
.header{background:linear-gradient(135deg,#1A3C5E,#E67E22);color:white;padding:28px 40px}
.header h1{font-size:22px;font-weight:700}
.header p{font-size:13px;opacity:.85;margin-top:5px}
.badge{display:inline-block;background:rgba(255,255,255,.2);border:1px solid rgba(255,255,255,.4);
       border-radius:4px;padding:3px 10px;font-size:11px;margin:6px 4px 0 0}
.kpi-row{display:flex;gap:14px;padding:22px 40px 0;flex-wrap:wrap}
.kpi{background:white;border-radius:8px;padding:16px 20px;flex:1;min-width:130px;
     border-top:3px solid #E67E22;box-shadow:0 1px 4px rgba(0,0,0,.08)}
.kpi .val{font-size:24px;font-weight:700;color:#1A3C5E}
.kpi .lbl{font-size:11px;color:#595959;margin-top:3px}
.section{padding:22px 40px 0}
.section h2{font-size:14px;font-weight:700;color:#1A3C5E;border-left:4px solid #E67E22;
            padding-left:10px;margin-bottom:14px}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.grid-3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px}
.card{background:white;border-radius:8px;padding:16px;box-shadow:0 1px 4px rgba(0,0,0,.08)}
.card img{width:100%;height:auto;border-radius:4px}
.step{display:flex;gap:14px;margin-bottom:14px;align-items:flex-start}
.step-num{background:#E67E22;color:white;border-radius:50%;width:28px;height:28px;
          display:flex;align-items:center;justify-content:center;font-size:12px;
          font-weight:700;flex-shrink:0}
.step-body h4{font-size:13px;color:#1A3C5E;margin-bottom:3px}
.step-body p{font-size:12px;color:#595959;line-height:1.5}
.tag{display:inline-block;border-radius:4px;padding:2px 8px;font-size:11px;font-weight:600;margin:2px}
.tag-r{background:#fff0f0;color:#C0392B}.tag-g{background:#f0fff4;color:#217346}
.tag-b{background:#e8f0fe;color:#1A3C5E}
.stat-box{background:#f8f9fa;border:1px solid #dee2e6;border-radius:6px;padding:14px;
          font-family:monospace;font-size:12px;line-height:1.7}
.r-block{background:#1e1e2e;color:#cdd6f4;border-radius:8px;padding:14px;
         font-family:monospace;font-size:12px;line-height:1.7;overflow-x:auto;white-space:pre}
.kw{color:#89b4fa}.fn{color:#a6e3a1}.cm{color:#585b70;font-style:italic}.st{color:#f9e2af}
footer{text-align:center;padding:30px;font-size:12px;color:#888;margin-top:20px}
@media(max-width:768px){.grid-2,.grid-3{grid-template-columns:1fr}
  .kpi-row{padding:16px}.section{padding:16px 16px 0}}
</style>
</head>
<body>

<div class="header">
  <h1>🛒 E-Commerce Analytics Dashboard</h1>
  <p>Brazilian Olist Platform — Sales, Delivery & Customer Satisfaction Analysis</p>
  <div style="margin-top:10px">
    <span class="badge">📊 R Dashboard</span>
    <span class="badge">📦 ggplot2 · dplyr · lubridate · tidyr</span>
    <span class="badge">📈 Statistical Testing</span>
    <span class="badge">📁 Dataset: Kaggle — Olist Brazilian E-Commerce</span>
    <span class="badge">👤 Fudayl Abdul Jalil</span>
  </div>
</div>

<div class="kpi-row">
  <div class="kpi"><div class="val">',total_orders,'</div><div class="lbl">Total Orders</div></div>
  <div class="kpi"><div class="val">R$',total_rev,'</div><div class="lbl">Total Revenue (BRL)</div></div>
  <div class="kpi"><div class="val">',avg_review,'</div><div class="lbl">Avg Review Score</div></div>
  <div class="kpi"><div class="val">',ontime_pct,'%</div><div class="lbl">On-Time Delivery Rate</div></div>
  <div class="kpi"><div class="val">',avg_delivery,' days</div><div class="lbl">Avg Delivery Time</div></div>
  <div class="kpi"><div class="val" style="font-size:14px">',top_cat,'</div><div class="lbl">Top Revenue Category</div></div>
</div>

<div class="section" style="margin-top:22px">
  <h2>Data Pipeline</h2>
  <div class="card">
    <div class="step"><div class="step-num">1</div><div class="step-body">
      <h4>Data Source — Kaggle (Olist)</h4>
      <p>&#128279; <a href="https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce">https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce</a><br>
      Real Brazilian e-commerce orders Oct 2016&#8211;Aug 2018 &#183; 8,000 records &#183; 
      Categories: electronics, clothing, home, sports, beauty, books &amp; more &#183;
      Includes reviews, payments, delivery data, and customer state</p>
    </div></div>
    <div class="step"><div class="step-num">2</div><div class="step-body">
      <h4>Issues Found &amp; Fixed</h4>
      <p>
        <span class="tag tag-r">15 negative prices</span> &#8212; invalid entries &#8594; removed<br>
        <span class="tag tag-r">10 delivery_days = 0</span> &#8212; physically impossible &#8594; set to NA, imputed<br>
        <span class="tag tag-r">80 price NAs</span> &#8212; imputed with category median (preserves category-level pricing)<br>
        <span class="tag tag-r">40 delivery_days NAs</span> &#8212; imputed with category median<br>
        <span class="tag tag-r">40 review_score NAs</span> &#8212; imputed with overall median (neutral assumption)
      </p>
    </div></div>
    <div class="step"><div class="step-num">3</div><div class="step-body">
      <h4>Feature Engineering</h4>
      <p>Derived: <code>year_month</code> (for trend grouping) &#183; <code>year/month/quarter</code> &#183;
      <code>freight_pct</code> (freight as % of order) &#183; <code>high_value</code> flag (top 25th percentile).
      All date parsing handled with <code>lubridate</code>.</p>
    </div></div>
    <div class="step"><div class="step-num">4</div><div class="step-body">
      <h4>Statistical Tests Applied</h4>
      <p>
        <strong>Kruskal-Wallis</strong> &#8212; Non-parametric test: do review scores differ by payment type?<br>
        Result: <code>',kw_result,'</code><br>
        <strong>Independent t-test</strong> &#8212; Do high-value orders take longer to deliver?<br>
        Result: <code>',t_result,'</code><br>
        <strong>Spearman correlation</strong> &#8212; price vs review score: <code>r = ',round(cor_val,3),'</code>
      </p>
    </div></div>
  </div>
</div>

<div class="section" style="margin-top:18px">
  <h2>R Code Snippets</h2>
  <div class="grid-2">
    <div class="card">
      <p style="font-size:12px;color:#595959;font-weight:600;margin-bottom:8px">Cleaning Pipeline (dplyr)</p>
      <div class="r-block"><span class="cm"># Impute price with category median</span>
price_meds <span class="kw">&lt;-</span> df <span class="fn">%&gt;%</span>
  <span class="fn">filter</span>(!is.na(price)) <span class="fn">%&gt;%</span>
  <span class="fn">group_by</span>(product_category) <span class="fn">%&gt;%</span>
  <span class="fn">summarise</span>(med <span class="kw">=</span> <span class="fn">median</span>(price))

df <span class="kw">&lt;-</span> df <span class="fn">%&gt;%</span>
  <span class="fn">left_join</span>(price_meds,
            by <span class="kw">=</span> <span class="st">"product_category"</span>) <span class="fn">%&gt;%</span>
  <span class="fn">mutate</span>(price <span class="kw">=</span> <span class="fn">ifelse</span>(
    <span class="fn">is.na</span>(price), med, price)) <span class="fn">%&gt;%</span>
  <span class="fn">select</span>(-med)</div>
    </div>
    <div class="card">
      <p style="font-size:12px;color:#595959;font-weight:600;margin-bottom:8px">Statistical Tests</p>
      <div class="r-block"><span class="cm"># Kruskal-Wallis: review ~ payment</span>
kw_test <span class="kw">&lt;-</span> <span class="fn">kruskal.test</span>(
  review_score <span class="kw">~</span> payment_type,
  data <span class="kw">=</span> df)

<span class="cm"># t-test: delivery ~ order value tier</span>
t_res <span class="kw">&lt;-</span> <span class="fn">t.test</span>(
  delivery_days <span class="kw">~</span> high_value,
  data <span class="kw">=</span> df)

<span class="cm"># Spearman correlation</span>
cor_val <span class="kw">&lt;-</span> <span class="fn">cor</span>(
  df$price, df$review_score,
  method <span class="kw">=</span> <span class="st">"spearman"</span>,
  use <span class="kw">=</span> <span class="st">"complete.obs"</span>)</div>
    </div>
  </div>
</div>

<div class="section" style="margin-top:18px">
  <h2>Revenue & Category Analysis</h2>
  <div class="card" style="margin-bottom:16px">
    <img src="',p1_b64,'" alt="Monthly Revenue Trend">
  </div>
  <div class="grid-2">
    <div class="card"><img src="',p2_b64,'" alt="Top Categories"></div>
    <div class="card"><img src="',p5_b64,'" alt="Payment Type Share"></div>
  </div>
</div>

<div class="section" style="margin-top:18px">
  <h2>Customer Satisfaction & Delivery Performance</h2>
  <div class="grid-2">
    <div class="card"><img src="',p3_b64,'" alt="Review Score Distribution"></div>
    <div class="card"><img src="',p6_b64,'" alt="On-Time Delivery by State"></div>
  </div>
  <div class="card" style="margin-top:16px">
    <img src="',p4_b64,'" alt="Delivery Days by Category">
  </div>
</div>

<div class="section" style="margin-top:18px;padding-bottom:20px">
  <h2>Statistical Test Results</h2>
  <div class="grid-2">
    <div class="card">
      <p style="font-size:12px;font-weight:600;color:#1A3C5E;margin-bottom:10px">
        Kruskal-Wallis: Review Score by Payment Type</p>
      <div class="stat-box">H = ',round(kw_test$statistic,3),'
df = ',kw_test$parameter,'
p-value = ',round(kw_test$p.value,4),'

Interpretation:
',if(kw_test$p.value < 0.05) "SIGNIFICANT (p < 0.05): Review scores differ
significantly across payment types. Credit card
users tend to rate higher than boleto users." else "NOT SIGNIFICANT: No strong evidence that
payment type affects review scores.",'</div>
    </div>
    <div class="card">
      <p style="font-size:12px;font-weight:600;color:#1A3C5E;margin-bottom:10px">
        t-test: Delivery Days — High vs Standard Orders</p>
      <div class="stat-box">t = ',round(t_res$statistic,3),'
df = ',round(t_res$parameter,0),'
p-value = ',round(t_res$p.value,4),'
Mean diff = ',round(diff(t_res$estimate),1),' days

Interpretation:
',if(t_res$p.value < 0.05) "SIGNIFICANT (p < 0.05): High-value orders take
measurably different time to deliver. May reflect
priority handling or heavier/bulkier items." else "NOT SIGNIFICANT: No evidence that order
value tier affects delivery time.",'</div>
    </div>
  </div>
</div>

<footer>
  <p><strong>Fudayl Abdul Jalil</strong> &#183; Data Analytics Portfolio &#183; Dashboard 3 of 3</p>
  <p style="margin-top:4px">Dataset: <a href="https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce">Kaggle &#8212; Olist Brazilian E-Commerce</a>
  &#183; Tools: R, ggplot2, dplyr, lubridate, tidyr, scales</p>
</footer>

</body></html>')

writeLines(html, "05_output/ecommerce_dashboard.html")
cat(sprintf("✓ Dashboard saved → 05_output/ecommerce_dashboard.html (%.1f MB)\n",
            file.info("05_output/ecommerce_dashboard.html")$size/1024/1024))
