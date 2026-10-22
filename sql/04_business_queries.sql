-- ============================================================================
-- IPL FRANCHISE AUCTION INTELLIGENCE & PLAYER VALUATION PLATFORM
-- MODULE 3.4: FRANCHISE DECISION-MAKER ANALYTICAL QUERIES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- QUERY 1: TOP 10 UNDERVALUED FINISHERS ("STEAL BUYS" IN DEATH OVERS)
-- Criteria: Sold Price <= 3.0 Cr, Death SR > 165, Min 30 balls faced in Death
-- ----------------------------------------------------------------------------
SELECT 
    season,
    player_name,
    franchise,
    sold_price_inr_cr,
    total_runs,
    death_strike_rate,
    cost_per_run_inr,
    performance_to_salary_value_score
FROM vw_scouting_master_mart
WHERE sold_price_inr_cr <= 3.00
  AND death_strike_rate > 165.00
  AND total_runs >= 100
ORDER BY death_strike_rate DESC, performance_to_salary_value_score DESC
LIMIT 10;

-- ----------------------------------------------------------------------------
-- QUERY 2: POWERPLAY BOWLING IMPACT SPECIALISTS
-- Criteria: PP Economy < 8.0, PP Wickets >= 4, identifying swing/containment threats
-- ----------------------------------------------------------------------------
SELECT 
    season,
    player_name,
    franchise,
    sold_price_inr_cr,
    pp_wickets,
    pp_economy_rate,
    total_wickets,
    cost_per_wicket_inr
FROM vw_scouting_master_mart
WHERE pp_wickets >= 4
  AND pp_economy_rate <= 8.50
ORDER BY pp_wickets DESC, pp_economy_rate ASC;

-- ----------------------------------------------------------------------------
-- QUERY 3: DEATH OVERS PRESSURE CONTAINMENT MATRIX
-- Criteria: Bowlers bowling in death overs with Dot % > 30% and Economy < 10.5
-- ----------------------------------------------------------------------------
SELECT 
    season,
    player_name,
    franchise,
    sold_price_inr_cr,
    death_economy_rate,
    death_dot_pct,
    total_wickets,
    cost_per_wicket_inr
FROM vw_scouting_master_mart
WHERE death_economy_rate > 0
  AND death_economy_rate <= 10.50
  AND death_dot_pct >= 28.00
ORDER BY death_dot_pct DESC, death_economy_rate ASC;

-- ----------------------------------------------------------------------------
-- QUERY 4: OVERPRICED BENCH / HIGH-RISK CONTRACTS
-- Identifying acquisitions > 10 Cr with lowest ValueScore or extreme Cost/Run
-- ----------------------------------------------------------------------------
SELECT 
    season,
    player_name,
    franchise,
    player_role,
    sold_price_inr_cr,
    total_runs,
    total_wickets,
    cost_per_run_inr,
    cost_per_wicket_inr,
    performance_to_salary_value_score
FROM vw_scouting_master_mart
WHERE sold_price_inr_cr >= 10.00
ORDER BY performance_to_salary_value_score ASC
LIMIT 10;

-- ----------------------------------------------------------------------------
-- QUERY 5: FRANCHISE AGGREGATE SPEND EFFICIENCY
-- Total squad spend vs total runs, total wickets, and average cost per output
-- ----------------------------------------------------------------------------
SELECT 
    season,
    franchise,
    COUNT(DISTINCT player_name) AS tracked_players,
    ROUND(SUM(sold_price_inr_cr), 2) AS total_tracked_spend_cr,
    SUM(total_runs) AS total_squad_runs,
    SUM(total_wickets) AS total_squad_wickets,
    ROUND(SUM(sold_price_inr_cr * 10000000) / NULLIF(SUM(total_runs), 0), 2) AS franchise_cost_per_run_inr,
    ROUND(SUM(sold_price_inr_cr * 10000000) / NULLIF(SUM(total_wickets), 0), 2) AS franchise_cost_per_wicket_inr
FROM vw_scouting_master_mart
GROUP BY season, franchise
ORDER BY season DESC, total_squad_runs DESC;
