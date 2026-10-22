# MODULE 4.1: Power BI Star Schema Data Model Architecture
**IPL Franchise Auction Intelligence & Player Valuation Platform**

---

## 1. Relational Model Overview & Philosophy

The data model follows an enterprise **Star Schema** pattern optimized for high-speed VertiPaq compression and sub-second DAX query execution in Power BI.

```
                    +--------------------+
                    |    dim_calendar    |
                    +--------------------+
                              |
                              | 1:N (DateKey)
                              v
+--------------------+ 1:N  +-----------------------+  N:1  +--------------------+
|    dim_matches     |----->|    fact_deliveries    |<------|    dim_players     |
+--------------------+      +-----------------------+       +--------------------+
                              |                               |
                              | N:1                           | 1:N
                              v                               v
                    +-----------------------+       +--------------------+
                    |  dim_match_conditions |       | dim_auction_prices |
                    +-----------------------+       +--------------------+
```

---

## 2. Table Specifications & Cardinalities

### 2.1 Fact Tables
1. **`fact_deliveries` (Ball-by-Ball Granularity):**
   - **Primary Key:** `delivery_id` (BigInt)
   - **Foreign Keys:**
     - `match_id` $\rightarrow$ `dim_matches[match_id]`
     - `batter` $\rightarrow$ `dim_player_registry[cricsheet_name]` (Active Relationship)
     - `bowler` $\rightarrow$ `dim_player_registry[cricsheet_name]` (Inactive Relationship)
   - **Metrics:** `runs_off_bat`, `extra_runs`, `wides`, `noballs`, `byes`, `legbyes`, `is_wicket`.

2. **`vw_scouting_master_mart` (Aggregated Season Fact):**
   - **Grain:** 1 row per `player_name` per `season`.
   - Used for instant, high-performance rendering of the Auction Strategy Quadrant Scatter Plot.

### 2.2 Dimension Tables
1. **`dim_matches`:**
   - **Primary Key:** `match_id`
   - Attributes: `season`, `city`, `venue`, `match_date`, `team1`, `team2`, `toss_winner`, `toss_decision`, `winner`, `result_margin`.
2. **`dim_player_registry` / `dim_players`:**
   - **Primary Key:** `cricsheet_name`
   - Attributes: `canonical_name`, `primary_franchise`, `primary_role`, `is_capped`, `is_overseas`.
3. **`dim_auction_prices`:**
   - **Primary Key:** `auction_id`
   - Natural Composite Key: `(standardized_name, season)`
   - Attributes: `franchise`, `season`, `player_role`, `base_price_inr_cr`, `sold_price_inr_cr`, `retention_status`, `is_capped`, `is_overseas`.
4. **`dim_calendar` (Calculated DAX Date Table):**
   - Attributes: `Date`, `Year`, `Month`, `Quarter`, `DayOfWeek`.

---

## 3. Relationship Matrix & Directional Filter Rules

| From Table | From Column | To Table | To Column | Cardinality | Cross Filter Direction | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `dim_matches` | `match_id` | `fact_deliveries` | `match_id` | 1-to-Many ($1:*$) | Single (`dim_matches` filters `fact`) | **Active** |
| `dim_player_registry` | `cricsheet_name` | `fact_deliveries` | `batter` | 1-to-Many ($1:*$) | Single (`dim_players` filters `fact`) | **Active** |
| `dim_player_registry` | `cricsheet_name` | `fact_deliveries` | `bowler` | 1-to-Many ($1:*$) | Single (`dim_players` filters `fact`) | **Inactive** (Activated via `USERELATIONSHIP`) |
| `dim_player_registry` | `canonical_name` | `dim_auction_prices` | `standardized_name` | 1-to-Many ($1:*$) | Both / Single | **Active** |
| `dim_calendar` | `Date` | `dim_matches` | `match_date` | 1-to-Many ($1:*$) | Single (`dim_calendar` filters `dim_matches`) | **Active** |

> **Best Practice Warning:** Avoid Bi-Directional filtering on high-volume fact tables. By using `USERELATIONSHIP` inside DAX measures (such as `True Economy Rate`), we maintain 100% deterministic filter propagation without ambiguous join cycles.
