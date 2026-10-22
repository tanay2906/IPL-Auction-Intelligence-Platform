# MODULE 5.1: Power BI Executive Dashboard Specifications & Wireframes
**IPL Franchise Auction Intelligence & Player Valuation Platform**

---

## 1. Executive Color Palette & Visual Theme
- **Background:** `#0F172A` (Slate Navy Dark Theme)
- **Card Background:** `#1E293B` (Midnight Slate)
- **Primary Accent / Steal Buy:** `#10B981` (Emerald Green)
- **Secondary Accent / Fair Value:** `#3B82F6` (Electric Blue)
- **Risk Accent / Overpriced:** `#EF4444` (Vivid Crimson)
- **Scouting Target / High Potential:** `#F59E0B` (Amber Gold)
- **Font Family:** `Segoe UI Semibold` / `Segoe UI`

---

## 2. Page 1: Executive Auction Strategy & Valuation Matrix

### Visual Layout
```
+-----------------------------------------------------------------------------------------------+
| HEADER: IPL Auction Strategy & Valuation Matrix | Slicers: [Season: 2024] [Role: All] [Cap]  |
+-----------------------------------------------------------------------------------------------+
| KPI CARD 1          | KPI CARD 2          | KPI CARD 3          | KPI CARD 4                  |
| Total Tracked Spend | Avg Cost Per Run    | Avg Cost Per Wicket | Steal Buys Identified       |
| ₹784.5 Cr           | ₹22,140 / Run       | ₹5,12,000 / Wicket  | 7 Players                   |
+-----------------------------------------------------------------------------------------------+
| SCATTER PLOT: 4-Quadrant Valuation Matrix                                                     |
| X-Axis: Sold Price (INR Cr) [0 - 25 Cr]                                                       |
| Y-Axis: Death Strike Rate [100 - 240]                                                         |
| Bubble Size: Total Runs | Legend: Value Buy Flag                                              |
|                                                                                               |
|  [Q1: STEAL BUYS]                 |  [Q2: PREMIUM PERFORMERS]                                 |
|  - High Death SR (>175)           |  - High Death SR (>175)                                   |
|  - Low Price (< ₹3 Cr)            |  - High Price (> ₹10 Cr)                                  |
|  * Shashank Singh, N.K. Reddy     |  * Heinrich Klaasen, Nicholas Pooran                      |
| ----------------------------------+---------------------------------------------------------- |
|  [Q3: SQUAD DEPTH]                |  [Q4: OVERPRICED RISKS]                                   |
|  - Moderate Death SR              |  - Low Death SR (<140)                                    |
|  - Low Price (< ₹2 Cr)            |  - High Price (> ₹12 Cr)                                  |
|                                   |  * High-Cost Accumulators                                 |
+-----------------------------------------------------------------------------------------------+
| TABLE: Top 10 Undervalued Targets by Value Score                                              |
| Player | Franchise | Role | Price (Cr) | Total Runs | Death SR | Cost/Run (₹) | Value Score   |
+-----------------------------------------------------------------------------------------------+
```

---

## 3. Page 2: Head-to-Head Player Scouting Radar & Comparison

### Visual Layout
```
+-----------------------------------------------------------------------------------------------+
| HEADER: Head-to-Head Player Scouting Radar | Slicers: [Player 1 Dropdown] vs [Player 2 Dropdown]
+-----------------------------------------------------------------------------------------------+
| RADAR / SPIDER CHART: 6-Axis Capability Model     | METRIC COMPARISON MATRIX                  |
|                                                   | Metric          | Player 1  | Player 2   |
|            Powerplay SR                           | ----------------+-----------+------------|
|                 /\                                | Overall Runs    | 354       | 420        |
|  Boundary %    /  \    Death SR                   | Balls Faced     | 210       | 315        |
|         \     /    \     /                        | True SR         | 168.5     | 133.3      |
|          \   /      \   /                         | Death SR        | 221.3     | 145.0      |
|           \ /        \ /                          | Dot Ball %      | 24.2%     | 38.5%      |
|            *----------*                           | Boundary %      | 72.4%     | 54.1%      |
|      Dot Ball %    Cost Efficiency                | Sold Price      | ₹0.20 Cr  | ₹14.00 Cr  |
|                                                   | Cost / Run      | ₹5,650    | ₹3,33,333  |
+---------------------------------------------------+-------------------------------------------+
| LINE CHART: Rolling 3-Match Form Index (Form Volatility across Season)                        |
| X-Axis: Match Date | Y-Axis: 3-Match Rolling Strike Rate | Legend: [Player 1] vs [Player 2]   |
+-----------------------------------------------------------------------------------------------+
```

---

## 4. Page 3: Bowling Threat & Pressure Containment Analysis

### Visual Layout
```
+-----------------------------------------------------------------------------------------------+
| HEADER: Bowling Threat & Pressure Containment | Phase Slicer: ( ) Powerplay (•) Death Overs   |
+-----------------------------------------------------------------------------------------------+
| KPI 1: Phase Wickets   | KPI 2: Phase Economy    | KPI 3: Phase Dot %   | KPI 4: Boundary Supp|
| 142 Total Death Wkts   | 10.42 Runs / Over       | 31.8% Dot Balls      | 18.2% Boundary %    |
+-----------------------------------------------------------------------------------------------+
| BUBBLE MATRIX: Pressure Containment                                                           |
| X-Axis: Death Economy Rate (Runs per Over) [Inverted Axis: Lower is Better]                    |
| Y-Axis: Death Dot Ball % [Higher is Better]                                                   |
| Bubble Size: Death Wickets Taken | Color: Franchise                                           |
| Top-Right Quadrant = Elite Death Specialists (High Dots + Low Economy)                         |
| * Matheesha Pathirana, Jasprit Bumrah, Harshit Rana                                           |
+-----------------------------------------------------------------------------------------------+
| HEATMAP TABLE: Bowler Phase Breakdown                                                         |
| Bowler | Franchise | Overs Bowled | PP Wkts | Death Wkts | Total Wkts | Death Econ | Cost/Wkt |
+-----------------------------------------------------------------------------------------------+
```
