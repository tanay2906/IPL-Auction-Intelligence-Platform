# MODULE 2: Excel Audit, Name Harmonization & Cleansing Workflow
**IPL Franchise Auction Intelligence & Player Valuation Platform**

---

## 1. Executive Context & Audit Objectives
Before ingesting raw ball-by-ball scorecards and auction registers into relational schemas (PostgreSQL / MySQL / SQLite), franchise data analysts must execute standard audit procedures in Microsoft Excel. 

Data discrepancies in sports telemetry lead to catastrophic downstream miscalculations—such as misallocating salary caps or assigning extras (byes/leg-byes) to a bowler's economy rate.

---

## 2. Name Harmonization Pipeline (Scorecards vs. Auction Sheet)

### 2.1 The Problem
- **Scorecards (Cricsheet/BCCI):** Use short initials, e.g., `V Kohli`, `RG Sharma`, `SA Yadav`, `JJ Bumrah`.
- **Auction Sheets (IPL Governing Council):** Use formal legal registration names, e.g., `Virat Kohli`, `Rohit Sharma`, `Suryakumar Yadav`, `Jasprit Bumrah`.

### 2.2 Standard Solution: Two-Tier Lookup with Fallback
In Excel, maintain the mapping table `dim_player_registry.csv`:
- `Column A`: `cricsheet_name`
- `Column B`: `canonical_name`
- `Column C`: `primary_franchise`
- `Column D`: `primary_role`

#### Excel Formula (Two-Tier XLOOKUP)
Place this formula in your raw deliveries staging workbook to dynamically look up the canonical name:
```excel
=XLOOKUP(TRIM(A2), dim_player_registry!$A$2:$A$500, dim_player_registry!$B$2:$B$500, 
    XLOOKUP("*" & RIGHT(TRIM(A2), LEN(TRIM(A2)) - SEARCH(" ", TRIM(A2))) & "*", 
            dim_player_registry!$B$2:$B$500, dim_player_registry!$B$2:$B$500, 
            "FLAG_MANUAL_REVIEW", 2))
```

### 2.3 Power Query Automated Fuzzy Matching
1. In Excel, navigate to **Data > Get Data > From File > From Text/CSV** and import `dim_player_registry.csv` and `raw_deliveries.csv`.
2. Select **Merge Queries as New**.
3. Join on `batter` = `cricsheet_name`.
4. Check **Use fuzzy matching to perform the merge**:
   - **Similarity Threshold:** `0.85`
   - **Ignore Case:** `True`
   - **Match by comparing culture:** `Invariant`
5. Custom M Transformation to clean text whitespace:
   ```powerquery
   = Table.TransformColumns(Source, {{"batter", Text.Trim, type text}, {"bowler", Text.Trim, type text}})
   ```

---

## 3. Ball Accounting & Over Edge-Case Audits

### 3.1 Legal Delivery Validation
A legal delivery is defined as a ball that is **neither a wide nor a no-ball**.
- Insert Helper Column `is_legal_ball`:
  ```excel
  =IF(AND(K2=0, L2=0), 1, 0)
  ```
  *(where `K2` is wides and `L2` is noballs).*

- Insert Helper Column `is_ball_faced`:
  ```excel
  =IF(K2=0, 1, 0)
  ```
  *(In official cricket rules, no-balls count towards balls faced by the batter, while wides do NOT).*

### 3.2 Over Overflow Sanity Check (Pivot Table Audit)
To detect dead-ball misattributions or scoring rollbacks:
1. Insert Pivot Table on `fact_deliveries`:
   - **Rows:** `match_id`, `inning`, `over`, `bowler`
   - **Values:** `Sum of is_legal_ball`
2. Apply Conditional Formatting on the Values column:
   - **Rule:** Cell Value $> 6$
   - **Format:** Red Fill with Dark Red Text
   - *Any highlighted row signifies an illegal over containing more than 6 legal deliveries.*

### 3.3 Bowler Runs Conceded Audit
Bowlers must NOT be penalized for fielding extras (byes and leg-byes):
```excel
=runs_off_bat + wides + noballs
```

---

## 4. Financial & Salary Cap Sanity Checks

### 4.1 Purse Ceiling Verification
Franchises are strictly bound by the BCCI annual salary cap:
- **2022:** ₹90.00 Crore
- **2023:** ₹95.00 Crore
- **2024:** ₹100.00 Crore

Create a Summary Pivot Table from `dim_auction_prices.csv`:
- **Rows:** `season`, `franchise`
- **Values:** `Sum of sold_price_inr_cr`, `Count of player_name`
- **Audit Formula:**
  ```excel
  =IF(C2 > VLOOKUP(A2, salary_cap_master!$A$2:$B$4, 2, FALSE), "BREACH: EXCEEDS PURSE", "COMPLIANT")
  ```

### 4.2 Squad Constraint Validation
- **Squad Size Constraint:** Must be between 18 and 25 players.
  ```excel
  =IF(OR(D2 < 18, D2 > 25), "SQUAD_SIZE_VIOLATION", "COMPLIANT")
  ```
- **Overseas Player Constraint:** Maximum 8 overseas players per squad.
  ```excel
  =IF(COUNTIFS(dim_auction_prices!$D:$D, A2, dim_auction_prices!$E:$E, B2, dim_auction_prices!$K:$K, TRUE) > 8, "OVERSEAS_LIMIT_BREACH", "COMPLIANT")
  ```
