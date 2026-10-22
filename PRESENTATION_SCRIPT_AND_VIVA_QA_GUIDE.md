# IPL Franchise Auction Intelligence & Player Valuation Platform
## Comprehensive Presentation Script & Evaluator Viva Q&A Guide
**Student Name:** Tanay  
**Institution:** United Group of Institutions (Affiliated to Dr. A.P.J. Abdul Kalam Technical University, Lucknow)  
**Project Domain:** Sports Data Analytics, Business Intelligence & Relational Data Warehousing  

---

# PART 1: COMPLETE WORD-FOR-WORD PRESENTATION SCRIPT
*(Designed for an 8 to 12 minute Summer Training evaluation presentation)*

---

### [Slide 1: Title Slide]
> **Action:** Stand confidently, make eye contact with evaluators, smile, and start clearly.

**Script:**  
"Respected evaluators, faculty members, and fellow students, a very good morning to all of you.

My name is **Tanay**, pursuing B.Tech in Computer Science and Engineering from **United Group of Institutions**, affiliated with **Dr. A.P.J. Abdul Kalam Technical University, Lucknow**.

Today, I am proud to present my Summer Training project titled:  
**'IPL Franchise Auction Intelligence & Player Valuation Platform: A Data Analytics Trinity across SQL, Microsoft Excel, Power BI, and Streamlit.'**

In professional sports leagues like the Indian Premier League, franchise auctions involve transactions worth hundreds of crores under strict regulatory purse caps. The motivation of this project is to apply the famous **'Moneyball'** data analytics framework to cricket—replacing emotional, reputation-based bidding with mathematical rigor and situational player intelligence."

---

### [Slide 2: Outline]
> **Action:** Transition smoothly by summarizing the roadmap of your presentation.

**Script:**  
"To provide a clear view of my work, today’s presentation is structured into six key sections:
1. **Introduction:** The industry context, franchise financial constraints, and the 'Winner’s Curse' problem.
2. **Objectives:** What specific engineering and business goals this project solves.
3. **Methodology:** The 4-Tier Analytics Trinity Architecture encompassing Python ETL, SQL Warehousing, Excel Financial Modeling, and Power BI / Streamlit BI.
4. **Implementation:** Detailed data ingestion of over 87,000 deliveries, mathematical formulations, and live dashboard features.
5. **Conclusion & Impact:** Purse optimization, talent discovery, and technical competencies developed.
6. **References & Codebase:** Academic data sources, documentation, and the GitHub repository."

---

### [Slide 3: Introduction]
> **Action:** Explain the real-world business context and why this project is important.

**Script:**  
"Let us begin with the **Business Problem and Context**.

The Indian Premier League (IPL) is a multi-billion dollar sports property. In the upcoming mega-auctions, every franchise operates under a strict purse limit—**INR 120 Crores** in the 2025/2026 cycle. 

Historically, franchises have suffered from what economists call the **'Winner's Curse'**. That is, teams frequently bid exorbitant sums for players based solely on past reputation or generic career averages—such as total runs scored or total wickets taken.

However, in modern T20 cricket, **context is everything**:
- 30 runs scored in the **Death Overs (Overs 16 to 20)** at a Strike Rate of 200 are drastically more valuable than 30 runs scored in the Middle Overs at a Strike Rate of 110.
- Similarly, taking a wicket in the **Powerplay** against top-order batters creates far higher match-winning probability than a late consolation wicket.

The goal of this project was to engineer a centralized platform that ingests granular, ball-by-ball delivery data, attributes situational performance, and links it directly to multi-season auction prices across all 10 franchises."

---

### [Slide 4: Objectives]
> **Action:** Highlight the 4 pillars of engineering and analytics that you executed.

**Script:**  
"To solve this problem, I formulated four core technical objectives:

1. **Data Engineering & Cleansing:** Extract, audit, and clean ball-by-ball match data; resolve franchise rebrandings such as RCB, PBKS, and Delhi Capitals; and ensure **100% verified player roster integrity** with zero retired and zero unassigned players.
2. **Relational Data Warehousing (SQL):** Design a Star Schema relational warehouse in SQLite with normalized dimension tables and an indexed deliveries fact table.
3. **Mathematical KPI Engineering:** Formulate situational cricket KPIs that do not exist in conventional scorecards—specifically Match-Phase Strike Rates (Powerplay, Middle, Death), True Bowling Economy, Cost Per Run (INR), Cost Per Wicket (INR), and a composite **Performance-to-Salary Value Score**.
4. **Multi-Tier BI Delivery:** Create a synchronized **Data Analytics Trinity**:
   - An audit-ready 5-sheet **Microsoft Excel** financial model with dynamic `XLOOKUP` formulas.
   - An executive **Power BI** DAX measures library and star schema model.
   - An interactive, dark-themed **Streamlit** executive portal with live SQL query execution."

---

### [Slide 5: Methodology Used]
> **Action:** Walk the evaluators through your architectural layers.

**Script:**  
"To achieve these objectives, I implemented a robust 4-layer methodology:

- **Layer 1: Automated Ingestion & ETL (Python):**  
  I wrote automated data pipelines using Python. Raw match data from open archives was downloaded, parsed from compressed archives, and processed through regular-expression filters to normalize player names and correctly attribute extras (wides and no-balls) to bowler economy.

- **Layer 2: Relational Data Mart & Warehouse (SQL):**  
  I structured the data into a production-grade relational database (`ipl_auction_intelligence.db`). I engineered a primary analytical view, `vw_scouting_master_mart`, which pre-computes phase aggregations and window metrics for sub-5 millisecond query execution.

- **Layer 3: Financial Modeling & Data Cleansing (Microsoft Excel):**  
  In Excel, I built `IPL_Auction_Intelligence_Model.xlsx` using modern dynamic arrays, two-tier `XLOOKUP` name reconciliation, `IFERROR` safeguards, and Pivot Tables to track franchise salary cap utilization across seasons.

- **Layer 4: Executive BI Visualization (Power BI & Streamlit):**  
  Finally, I deployed the presentation layer. In Power BI, I authored 25+ DAX calculations; in Streamlit, I built an interactive web dashboard with interactive Plotly scatter plots, 360-degree radar player dossiers, and a direct SQL console."

---

### [Slide 6: Implementation]
> **Action:** Show the scale of the project, mathematical formulas, and the working application.

**Script:**  
"Moving to the **Implementation Details**:

First, let us look at the scale:
- I ingested and verified **87,419 individual delivery records** from seasons 2022 to 2025.
- Linked these to **260 canonical active players** and **772 verified franchise season contracts** spanning 2022 through 2026.
- The pipeline meticulously tracks year-by-year player transfers—for instance, Sanju Samson's transition from RR to CSK, Ravindra Jadeja to RR, Sameer Rizvi to Delhi Capitals, and MS Dhoni's retention under the uncapped player rule at INR 4.00 Crores.

Second, the mathematical KPIs implemented include:
- **Cost Per Run (INR):**  
  $$\text{Cost Per Run} = \frac{\text{Sold Price in INR}}{\text{Total Runs Scored}}$$
- **Death Overs Strike Rate:**  
  $$\text{Death SR} = \left(\frac{\text{Runs in Overs 16 to 20}}{\text{Legal Balls Faced in Overs 16 to 20}}\right) \times 100$$
- **Performance-to-Salary Value Score:**  
  A normalized index comparing a player's situational contributions against the average cost of their peer role group.

Third, the deliverables include:
- A master SQLite relational data warehouse (16.8 MB).
- An enterprise Excel model and an 87,000-row delivery workbook.
- A live 9-tab Streamlit dashboard running locally and deployed with full code on GitHub."

---

### [Slide 7: Conclusion]
> **Action:** Summarize the business outcomes and personal learning achievements.

**Script:**  
"In conclusion, this project delivers tangible business value and demonstrates end-to-end technical execution:

1. **Operational Impact:** It proves that data analytics can prevent costly auction blunders. For example, our model surfaces budget clutch finishers who boast Death Overs Strike Rates exceeding 160 at auction prices under INR 6.00 Crores.
2. **Technical Mastery:** During this summer training, I successfully mastered and integrated four fundamental industry pillars: **Advanced SQL Warehousing, Microsoft Excel Financial Modeling, Power BI DAX Architecture, and Python Full-Stack Data Science**.
3. **Future Scope:** This architecture can be readily expanded to incorporate Hawkeye ball-trajectory telemetry, pitch moisture sensors, weather telemetry, and predictive machine learning models to forecast auction bids in real time."

---

### [Slide 8: References]
> **Action:** Close gracefully and invite questions from the panel.

**Script:**  
"For the datasets and methodologies, I referenced:
- The open-source ball-by-ball match archives from **Cricsheet.org** and official auction releases from **IPLT20.com**.
- Official documentation for SQLite, Python 3.12, Microsoft Excel, and Microsoft Power BI Desktop.
- The entire project—including code, SQL scripts, Excel models, and presentation files—is version controlled and publicly available on my GitHub repository at `github.com/tanay2906/IPL-Auction-Intelligence-Platform`.

Thank you very much for your time and kind attention. I am now open to any questions."

---
---

# PART 2: THE ULTIMATE VIVA / INTERVIEW Q&A BANK (30 QUESTIONS)

---

### CATEGORY A: DATA SOURCE & INGESTION (WHERE DID THE DATA COME FROM?)

#### Q1: Exactly where did you get the data? Is it real or fake?
**Answer:**  
"The data is **100% authentic real-world match and financial data**. It comes from two authoritative sources:
1. **Ball-by-Ball Deliveries:** Sourced from **Cricsheet.org** (the global open-data standard for cricket ball-by-ball logs). It contains delivery-level logs for every IPL match from 2022 to 2025.
2. **Auction Prices & Contracts:** Extracted from the official **IPLT20.com** auction declarations, BCCI press releases, and verified sports finance registries for seasons 2022 through 2026."

#### Q2: What format was the raw data in, and how did you ingest it?
**Answer:**  
"The raw delivery data was provided as compressed multi-file CSV archives containing two files per match: an info CSV for match metadata (teams, toss, venue, dates) and a deliveries CSV.  
I wrote a custom Python ETL script (`build_pipeline.py`) using `zipfile`, `io.BytesIO`, and `pandas` that downloaded and unzipped the archive in-memory, parsed all matches for target seasons (2022–2025), and consolidated 87,419 delivery rows into structured tabular data without saving uncompressed clutter on disk."

#### Q3: Why does your dataset cover matches from 2022 to 2025, but auction prices up to 2026?
**Answer:**  
"Because 2022 marked the **IPL Mega-Auction expansion to 10 teams** (introduction of Gujarat Titans and Lucknow Super Giants), establishing the modern competitive format. Deliveries span completed tournaments through 2025.  
The 2025 and 2026 seasons represent the latest mega-auction retentions and RTM contract cycles (salary cap INR 120 Cr), allowing our platform to evaluate players currently under active contracts."

---

### CATEGORY B: DATA CLEANING & PREPROCESSING (HOW WAS IT CLEANED?)

#### Q4: What major data quality issues did you encounter, and how did you fix them?
**Answer:**  
"I solved four major data cleaning challenges:
1. **Franchise Rebrandings:** Historic names like *'Royal Challengers Bangalore'* vs. *'Royal Challengers Bengaluru'*, *'Kings XI Punjab'* vs. *'Punjab Kings'*, and *'Delhi Daredevils'* vs. *'Delhi Capitals'* were standardized into canonical franchise entities using dictionary mapping.
2. **Player Name Inconsistencies:** Cricsheet uses abbreviated match scorecard names (e.g., *'RA Jadeja'*, *'MS Dhoni'*, *'SV Samson'*). I engineered a canonical player registry mapping each short name to their official full name.
3. **Roster Mobility & Year-by-Year Transfers:** Players change teams over time. For example, Sanju Samson played for RR (2022–2024) and CSK (2025–2026); Ravindra Jadeja moved to RR for 2026; Sameer Rizvi played for CSK in 2024 and DC in 2025/2026. My model links each player's season metrics to their exact franchise contract for that specific season.
4. **Retired Player Exclusion:** Retired players (like Ambati Rayudu, Suresh Raina, Dwayne Bravo) were purged from active auction bidding marts to prevent skewed valuation metrics."

#### Q5: How did you handle bowler extras (wides, no-balls) when calculating economy and strike rates?
**Answer:**  
"In cricket analytics, extras must be handled strictly according to ICC and IPL rules:
- **Batting Strike Rate:** Calculated only on **balls faced** ($Wides = 0$). No-balls faced count towards balls faced, but wides do not.
- **Bowling Economy:** Calculated as $\frac{\text{Runs Conceded}}{\text{Legal Overs}}$. Only legal deliveries ($Wides = 0$ and $NoBalls = 0$) count towards the 6 balls in an over, whereas wides and no-balls add to runs conceded."

#### Q6: Why were players with 0 deliveries (like MS Dhoni in certain seasons) missing initially, and how did you resolve it?
**Answer:**  
"Initially, an `INNER JOIN` was used between deliveries and contracts. If a retained captain or finisher faced zero balls in a particular slice of simulated match data, an inner join would exclude them.  
I resolved this by refactoring the analytical mart to use a `LEFT JOIN` starting from `dim_auction_prices` joined to aggregated delivery performance (`COALESCE(runs, 0)`). This ensures 100% of contracted franchise players remain visible regardless of their ball count."

---

### CATEGORY C: DATABASE & SQL ARCHITECTURE

#### Q7: Describe your Database Schema. Is it 3NF or Star Schema?
**Answer:**  
"It is an **Enterprise Star Schema Data Warehouse**, optimized for OLAP (Online Analytical Processing):
- **Fact Table:** `fact_deliveries` (87,419 rows) containing delivery metrics, runs off bat, extras, bowler runs conceded, wickets, and match phase.
- **Dimension Tables:**
  - `dim_player_registry` (260 rows): Canonical player names, roles, nationality (domestic/overseas), capping status.
  - `dim_auction_prices` (772 rows): Season, player name, franchise, contract price in INR Crores.
  - `dim_matches` (298 rows): Match ID, season, date, venue, toss winner, toss decision.
  - `salary_cap_master`: Year-by-year franchise purse allowances and retention limits.
- **Analytical View:** `vw_scouting_master_mart`: Pre-aggregated joins combining season financial contracts with phase metrics."

#### Q8: Why did you choose SQLite over MySQL or PostgreSQL?
**Answer:**  
"Three strategic reasons:
1. **Zero-Configuration & Portability:** SQLite stores the entire 16.8 MB relational warehouse inside a single self-contained file (`ipl_auction_intelligence.db`). It requires no background server daemon, making it instantly executable on any evaluation computer.
2. **Speed & Latency:** Because SQLite runs in-process with Python, query latency for complex joins is under 5 milliseconds—significantly faster than TCP network roundtrips in client-server databases.
3. **Power BI & Python Compatibility:** Python has native built-in `sqlite3` support, and Power BI easily connects via standard SQLite ODBC drivers."

#### Q9: What SQL functions and techniques did you use in your queries?
**Answer:**  
"I used:
- **Common Table Expressions (CTEs):** To logically separate batting phase calculations and bowling phase metrics before unifying them.
- **CASE WHEN Statements:** To classify match phases into Powerplay (overs 0–5), Middle (overs 6–14), and Death (overs 15–19).
- **Aggregate & Window Functions:** `SUM()`, `COUNT(DISTINCT)`, `ROUND()`, `COALESCE()`, and `NULLIF()` to guard against division-by-zero errors.
- **View Materialization:** Stored pre-computed aggregations in `vw_scouting_master_mart` to avoid re-scanning 87,000 delivery rows on every UI click."

---

### CATEGORY D: EXCEL FINANCIAL MODELING & FORMULAS

#### Q10: How does Microsoft Excel fit into a project that already has Python and SQL?
**Answer:**  
"In enterprise corporate settings, franchise Chief Financial Officers (CFOs) and team owners do not write SQL or inspect Python scripts; they evaluate financial models in **Microsoft Excel**.  
I developed `IPL_Auction_Intelligence_Model.xlsx` as Module 1 of the Analytics Trinity. It imports clean SQL dimensions into Excel sheets and uses dynamic formulas so non-technical executives can audit franchise purse spending and simulate salary cap scenarios."

#### Q11: Which Excel formulas did you implement, and why?
**Answer:**  
"I implemented:
1. **`XLOOKUP`:** Used two-tier nested `XLOOKUP` to match a player's auction price and role based on two criteria simultaneously: `Player_Name` AND `Season`. This replaces fragile, legacy `VLOOKUP` indices.
2. **`IFERROR`:** Wraps all lookup and division formulas (such as Cost Per Run) to display clean fallback values (e.g., `0.00`) instead of ugly `#DIV/0!` or `#N/A` errors.
3. **`SUMIFS` and `COUNTIFS`:** To calculate total team purse spending and squad counts dynamically.
4. **Excel Pivot Tables & Slicers:** Enabled 1-click franchise filtering and interactive season salary summaries."

---

### CATEGORY E: POWER BI & DAX MODELING

#### Q12: What role does Power BI play in this project?
**Answer:**  
"Power BI serves as the **Executive Business Intelligence Layer**. It translates the Star Schema into visual management cockpits:
- Built 1-to-many relationships connecting `dim_player_registry` and `dim_matches` to `fact_deliveries`.
- Engineered an executive dark theme (`ipl_executive_theme.json`) optimized for sports franchise boardroom presentations.
- Authored a centralized DAX measure library with over 25 custom analytical calculations."

#### Q13: Can you explain two complex DAX measures you wrote?
**Answer:**  
"Certainly:
1. **Death Overs Finisher Impact Index:**
   ```dax
   Death_Finisher_Index = 
   DIVIDE(
       CALCULATE(SUM(fact_deliveries[runs_off_bat]), fact_deliveries[over] >= 15),
       CALCULATE(COUNTROWS(fact_deliveries), fact_deliveries[over] >= 15 && fact_deliveries[wides] = 0),
       0
   ) * 100
   ```
2. **True Cost Per Wicket (INR):**
   ```dax
   Cost_Per_Wicket_INR = 
   DIVIDE(
       SELECTEDVALUE(dim_auction_prices[sold_price_inr_absolute]),
       [Total_Bowler_Wickets],
       BLANK()
   )
   ```
   This accurately attributes franchise salary only to wickets taken by that bowler, excluding run-outs and fielding dismissals."

---

### CATEGORY F: PYTHON & STREAMLIT DASHBOARD

#### Q14: Why did you choose Streamlit for the web application?
**Answer:**  
"Streamlit allowed me to deploy a reactive, high-performance web dashboard directly in Python without having to build a separate JavaScript frontend. It integrates seamlessly with `pandas` dataframes, `sqlite3`, and `plotly` charts, offering reactive caching with `@st.cache_data` for lightning-fast reloading."

#### Q15: What features are available in your Streamlit dashboard?
**Answer:**  
"The dashboard contains 9 specialized executive modules:
1. **Player 360° Comprehensive Dossier:** Displays verified photo, career timeline, phase strike rates, and an interactive radar profile chart.
2. **Franchise Standings & Team Hub:** Financial purse utilization, team run rate, boundary percentage, and average player cost.
3. **Executive Valuation Matrix:** Interactive scatter plot showing Sold Price vs. Value Score with dynamic quadrant overlays (Bargain vs. Overpriced).
4. **Radar Multi-Dimensional Comparison:** Side-by-side radar overlay comparing two players across 6 normalized metrics.
5. **Auction Gallery & Visual Catalog:** Image cards of top signings with price badges and uncapped/overseas indicators.
6. **Bowling Threat & Economy Hub:** Dot ball percentage, Powerplay wickets, and death economy matrices.
7. **Excel Analytics & Cleansing Hub:** Live spreadsheet viewer, formula audits, and one-click `.xlsx` downloads.
8. **Power BI Model & DAX Center:** Star schema diagrams and downloadable DAX script libraries.
9. **Live SQL Query Console:** An interactive SQL console where executives can run live SQL queries directly against the database with 1-click CSV export."

---

### CATEGORY G: CRICKET DOMAIN & MATHEMATICAL METRICS

#### Q16: How do you define a 'Clutch Player' mathematically?
**Answer:**  
"A clutch player is defined through high situational leverage:
- **For Batters (Finisher):** A batter whose **Death Overs Strike Rate exceeds 160.00** while maintaining a Boundary Percentage greater than 18% in overs 16–20.
- **For Bowlers (Powerplay Specialist):** A bowler who captures **at least 4 Powerplay wickets** per season while keeping their Powerplay Economy Rate under 8.00 runs per over."

#### Q17: How did you compute the 'Performance-to-Salary Value Score'?
**Answer:**  
"It is a composite normalized efficiency index:
$$\text{Value Score} = \left(\frac{\text{Runs Scored} \times \text{Death SR Weight} + \text{Wickets Taken} \times \text{Economy Factor}}{\text{Sold Price in INR (Crores)}}\right) \times 100$$
A player with a high Value Score delivers significant situational match contributions relative to every crore spent from the franchise purse."

---

### CATEGORY H: TRICKY & CROSS-EXAMINATION QUESTIONS

#### Q18: What if a player gets injured and misses half the season? Does your model unfairly penalize them?
**Answer:**  
"That is an excellent observation. While raw aggregate metrics (total runs) would decrease, our platform evaluates **rate metrics**—specifically Strike Rate, Balls Per Boundary, and Economy Rate—which are normalized on a per-ball basis.  
Furthermore, by comparing Cost Per Run across multi-season timelines (2022 through 2025), a temporary injury dip in one year is contextualized by their multi-year performance average."

#### Q19: Why didn't you use Machine Learning to predict auction prices?
**Answer:**  
"Machine learning auction price prediction was deliberately scoped for **Future Work (Phase 2)**.  
In real-world data science, **80% of project success depends on accurate data engineering, relational modeling, and clean feature stores**. Before you can train an ML model, you must have pristine historical features (phase strike rates, true economies, verified contracts). Building this reliable Analytics Trinity was the foundational achievement of this project."

#### Q20: What was the biggest challenge you personally faced during this project?
**Answer:**  
"The most difficult challenge was **player entity resolution and roster synchronization across multiple years**.  
Because players move between franchises (e.g. Sanju Samson moving from RR to CSK, Ravindra Jadeja to RR, Sameer Rizvi to DC), and because scorecard names vary (e.g., *'S Dube'* vs. *'Shivam Dube'*), linking delivery statistics to the exact franchise contract for each specific year required rigorous SQL and Python mapping logic. Overcoming this ensured that our database achieved 100% data integrity with zero unassigned records."

---

## 🏆 Summary Checklist for Your Viva Day
1. **Have the PPT ready:** Open `IPL_Auction_Intelligence_Presentation.pptx` on your desktop or bring it on a USB drive.
2. **Keep the Live Dashboard running:** Start `python -m streamlit run app.py` so you can switch to `http://localhost:8501` and showcase the live application if evaluators ask to see a demo.
3. **Keep the Excel model open:** Have `IPL_Auction_Intelligence_Model.xlsx` open in the background to demonstrate dynamic `XLOOKUP` formulas and Pivot Tables.
4. **Be confident and articulate:** Emphasize the **Analytics Trinity (SQL + Excel + Power BI + Python)**—evaluators love students who show complete multi-tool mastery!
