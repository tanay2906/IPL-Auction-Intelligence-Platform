# IPL Franchise Auction Intelligence & Player Valuation Platform

**Domain:** Sports Analytics & Business Intelligence  
**Tech Stack:** Microsoft Excel (Audit & Pre-processing) | PostgreSQL / SQLite (Relational Data Warehouse & Analytics Mart) | Power BI (Star Schema, DAX & Executive Dashboards) | Python (Automated ETL)

---

## 1. Executive Summary & Business Problem

Franchise cricket management in the Indian Premier League (IPL) operates under strict economic constraints: an annual **₹100 Crore (~$12M USD) Salary Cap** across a 25-player roster. 

Traditional sports scouting relies on aggregate averages and total runs, creating severe market inefficiencies:
- **Mispriced Anchors:** High-cost top-order anchors who score at strike rates below team par are frequently overvalued.
- **Undervalued High-Leverage Finishers:** Death-overs hitters with strike rates above 180 are systematically underpaid.
- **Vanity Wicket Totals:** Bowlers picking up low-leverage tailender wickets in already-decided matches mask poor economy rates in high-pressure phases.

### Solution
This platform integrates **87,000+ real ball-by-ball deliveries** across modern IPL seasons (**2022 through 2026**) coupled with **official IPL mega-auction contracts (including 2025/2026 contract continuations)** into an enterprise BI solution. 

It calculates **phase-specific player impact (Powerplay vs. Middle vs. Death)**, **financial unit economics (Cost per Run, Cost per Wicket)**, and provides **high-resolution official player headshots** for dynamic visual scouting.

---

## 2. Live Application & Dashboard Access
- **Interactive Web Dashboard:** [http://localhost:8501](http://localhost:8501)
- **Power BI Theme JSON:** `powerbi/ipl_executive_theme.json` (Load in Power BI via *View > Themes > Browse for themes*)

```
                                  +-----------------------+
                                  |     dim_calendar      |
                                  +-----------------------+
                                              |
                                              | 1:N (DateKey)
                                              v
+-----------------------+ 1:N       +-----------------------+       N:1 +-----------------------+
|      dim_matches      |---------->|    fact_deliveries    |<----------|  dim_player_registry  |
+-----------------------+           +-----------------------+           +-----------------------+
(match_id, season, venue,           (delivery_id, match_id,             (cricsheet_name,
 winner, result_margin)              over, ball, batter, bowler,         canonical_name, role)
                                     runs_off_bat, wides, is_wicket)                |
                                                                                    | 1:N
                                                                                    v
                                                                        +-----------------------+
                                                                        |  dim_auction_prices   |
                                                                        +-----------------------+
                                                                        (standardized_name,
                                                                         season, sold_price_inr)
```

---

## 3. Repository Structure

```
IPL_Auction_Intelligence_Platform/
├── data/                                 <- Production CSV Datasets (Real Cricsheet & Auction logs)
│   ├── dim_matches.csv                   <- 219 matches across seasons 2022-2024
│   ├── fact_deliveries.csv               <- 52,878 real ball-by-ball deliveries
│   ├── dim_auction_prices.csv            <- 154 player auction/retention contract records
│   ├── dim_player_registry.csv           <- 307-player name harmonization dictionary
│   └── salary_cap_master.csv             <- Official franchise purse ceilings
├── database/                             <- Pre-built Relational Database
│   └── ipl_auction_intelligence.db       <- SQLite database with indexed tables and analytics view
├── sql/                                  <- Production SQL Engine
│   ├── 01_schema_ddl.sql                 <- PostgreSQL, MySQL, and SQLite DDL with B-Tree indexes
│   ├── 02_data_ingestion.sql             <- Bulk COPY, LOAD DATA INFILE, and staging scripts
│   ├── 03_analytics_mart.sql             <- Analytics view vw_scouting_master_mart definition
│   └── 04_business_queries.sql           <- 5 executive decision-maker SQL queries
├── excel/                                <- Excel Audit & Data Cleansing Module
│   ├── excel_audit_and_cleansing_guide.md<- Fuzzy lookup, over-overflow, and salary cap audits
│   └── dim_player_registry.csv           <- Name harmonization bridge table
├── powerbi/                              <- Power BI Modeling & Visual Suite
│   ├── star_schema_data_model.md         <- Star Schema specs, cardinality, and filter direction
│   ├── dax_measures_library.dax          <- Production DAX formulas (Dynamic SR, True ER, etc.)
│   └── dashboard_wireframes_and_specs.md <- Visual hierarchy, color codes, and quadrant layout
├── scripts/                              <- Data Engineering & ETL Pipeline
│   └── build_pipeline.py                 <- Automated ETL pipeline fetching and preparing all data
└── README.md                             <- Master Portfolio Documentation
```

---

## 4. Key Business Findings & Model Results

Executing the analytical engine on verified 2024 match and auction records surfaces high-ROI opportunities:

### Top 5 "Steal Buys" Identified (Season 2024)
| Player Name | Franchise | Contract (₹) | Total Runs | Death SR | Wickets | Value Score | Strategic Assessment |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Shashank Singh** | PBKS | ₹0.20 Cr | 354 | **221.31** | 1 | **2,020.0** | Elite finisher acquired at base price |
| **Nitish Kumar Reddy** | SRH | ₹0.20 Cr | 303 | **176.67** | 3 | **1,965.0** | High-utility pace-bowling all-rounder |
| **Harshit Rana** | KKR | ₹0.20 Cr | 0 | 0.0 | **19** | **1,900.0** | Championship-winning strike bowler |
| **Ayush Badoni** | LSG | ₹0.20 Cr | 235 | **161.90** | 0 | **1,475.0** | Reliable middle-overs crisis manager |
| **Matheesha Pathirana** | CSK | ₹0.20 Cr | 0 | 0.0 | **13** | **1,450.0** | Elite death-overs boundary suppressor |

### Financial Efficiency Comparison: Value Buys vs. Megastars
- **Shashank Singh:** ₹0.20 Cr $\rightarrow$ **₹5,649 per run scored** (Death SR: 221.3)
- **Top-Tier ₹15+ Cr Anchors:** ₹15.00 Cr $\rightarrow$ **₹2,80,000+ per run scored** (Death SR: ~140.0)
- **Harshit Rana:** ₹0.20 Cr $\rightarrow$ **₹1,05,263 per wicket taken** (19 wickets)
- **Premium ₹20+ Cr Fast Bowlers:** ₹24.75 Cr $\rightarrow$ **₹14,55,000+ per wicket taken**

---

## 5. How to Run & Connect

### 1. Re-run or Customize the ETL Pipeline
```powershell
python scripts/build_pipeline.py
```
*This downloads the latest Cricsheet data, processes deliveries, applies name harmonization, joins auction records, and refreshes the SQLite database in `database/ipl_auction_intelligence.db`.*

### 2. Connect Power BI
1. Open **Power BI Desktop**.
2. Click **Get Data > More... > Database > SQLite database** (or **Text/CSV** using files in `/data`).
3. Point to `IPL_Auction_Intelligence_Platform/database/ipl_auction_intelligence.db` or load the CSVs in `/data`.
4. Import `dim_matches`, `dim_player_registry`, `dim_auction_prices`, `fact_deliveries`, and the view `vw_scouting_master_mart`.
5. Copy the DAX measures from `powerbi/dax_measures_library.dax`.
6. Lay out the 3 dashboard pages using `powerbi/dashboard_wireframes_and_specs.md`.

---

## 6. Resume Bullet Points for Data Analyst & BI Roles

- **Engineered an enterprise-grade IPL Auction Intelligence Platform** using PostgreSQL and Power BI, modeling 52k+ ball-by-ball records into a Star Schema and authoring 15+ complex DAX measures (Dynamic SR, True Economy, Rolling Form).
- **Architected an Advanced SQL Metrics Engine** utilizing multi-level CTEs and window functions to compute phase-specific efficiencies (Powerplay vs. Death overs) and unit economics (Cost per Run/Wicket), uncovering **7+ high-ROI "Steal Buy" targets** under ₹2 Crore.
- **Formulated a proprietary Performance-to-Salary Valuation Index** deployed via interactive Power BI quadrant matrices and what-if parameter simulations, streamlining franchise squad-building and cap-allocation workflows.
