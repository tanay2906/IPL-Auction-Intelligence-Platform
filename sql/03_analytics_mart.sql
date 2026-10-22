-- ============================================================================
-- IPL FRANCHISE AUCTION INTELLIGENCE & PLAYER VALUATION PLATFORM
-- MODULE 3: PRODUCTION ANALYTICS MART & MATERIALIZED VIEW
-- ============================================================================

-- In PostgreSQL: Use MATERIALIZED VIEW for persistent high-speed caching
-- In MySQL / SQLite: Use VIEW or CTAS (CREATE TABLE AS SELECT)
DROP VIEW IF EXISTS vw_scouting_master_mart;

CREATE VIEW vw_scouting_master_mart AS
WITH delivery_base AS (
    SELECT 
        d.match_id,
        m.season,
        d.inning,
        d.over,
        d.ball,
        d.batter,
        d.bowler,
        COALESCE(r_bat.canonical_name, d.batter) AS batter_canonical,
        COALESCE(r_bowl.canonical_name, d.bowler) AS bowler_canonical,
        d.runs_off_bat,
        d.extra_runs,
        d.wides,
        d.noballs,
        d.byes,
        d.legbyes,
        d.is_wicket,
        d.dismissal_kind,
        d.player_dismissed,
        -- Legal Deliveries
        CASE WHEN d.wides = 0 AND d.noballs = 0 THEN 1 ELSE 0 END AS is_legal_ball,
        -- Balls Faced (wides do not count towards balls faced)
        CASE WHEN d.wides = 0 THEN 1 ELSE 0 END AS is_ball_faced,
        -- Bowler Runs Conceded (byes/legbyes excluded)
        (d.runs_off_bat + d.wides + d.noballs) AS bowler_runs_conceded,
        -- Legitimate Bowler Wickets
        CASE 
            WHEN d.is_wicket = 1 
                 AND d.dismissal_kind NOT IN ('run out', 'retired hurt', 'retired out', 'obstructing the field') 
            THEN 1 ELSE 0 
        END AS is_bowler_wicket,
        -- Match Phase Allocation (0-indexed overs: 0 to 19)
        CASE 
            WHEN d.over BETWEEN 0 AND 5 THEN 'Powerplay'
            WHEN d.over BETWEEN 6 AND 14 THEN 'Middle'
            WHEN d.over BETWEEN 15 AND 19 THEN 'Death'
        END AS match_phase
    FROM fact_deliveries d
    INNER JOIN dim_matches m ON d.match_id = m.match_id
    LEFT JOIN dim_player_registry r_bat ON d.batter = r_bat.cricsheet_name
    LEFT JOIN dim_player_registry r_bowl ON d.bowler = r_bowl.cricsheet_name
),

-- ----------------------------------------------------------------------------
-- 1. Phase-Wise Batting Metrics
-- ----------------------------------------------------------------------------
batting_phase_metrics AS (
    SELECT 
        season,
        batter_canonical AS player_name,
        SUM(runs_off_bat) AS total_runs,
        SUM(is_ball_faced) AS total_balls_faced,
        COUNT(DISTINCT match_id) AS innings_batted,
        -- Powerplay Phase
        SUM(CASE WHEN match_phase = 'Powerplay' THEN runs_off_bat ELSE 0 END) AS pp_runs,
        SUM(CASE WHEN match_phase = 'Powerplay' THEN is_ball_faced ELSE 0 END) AS pp_balls,
        ROUND(
            CAST(SUM(CASE WHEN match_phase = 'Powerplay' THEN runs_off_bat ELSE 0 END) AS FLOAT) 
            / NULLIF(SUM(CASE WHEN match_phase = 'Powerplay' THEN is_ball_faced ELSE 0 END), 0) * 100, 2
        ) AS pp_strike_rate,
        -- Middle Overs Phase
        SUM(CASE WHEN match_phase = 'Middle' THEN runs_off_bat ELSE 0 END) AS middle_runs,
        SUM(CASE WHEN match_phase = 'Middle' THEN is_ball_faced ELSE 0 END) AS middle_balls,
        ROUND(
            CAST(SUM(CASE WHEN match_phase = 'Middle' THEN runs_off_bat ELSE 0 END) AS FLOAT) 
            / NULLIF(SUM(CASE WHEN match_phase = 'Middle' THEN is_ball_faced ELSE 0 END), 0) * 100, 2
        ) AS middle_strike_rate,
        -- Death Overs Phase
        SUM(CASE WHEN match_phase = 'Death' THEN runs_off_bat ELSE 0 END) AS death_runs,
        SUM(CASE WHEN match_phase = 'Death' THEN is_ball_faced ELSE 0 END) AS death_balls,
        ROUND(
            CAST(SUM(CASE WHEN match_phase = 'Death' THEN runs_off_bat ELSE 0 END) AS FLOAT) 
            / NULLIF(SUM(CASE WHEN match_phase = 'Death' THEN is_ball_faced ELSE 0 END), 0) * 100, 2
        ) AS death_strike_rate,
        -- Dot Ball % & Boundary Frequency
        ROUND(
            CAST(SUM(CASE WHEN runs_off_bat = 0 AND is_ball_faced = 1 THEN 1 ELSE 0 END) AS FLOAT) 
            / NULLIF(SUM(is_ball_faced), 0) * 100, 2
        ) AS dot_ball_pct,
        ROUND(
            CAST(SUM(is_ball_faced) AS FLOAT) 
            / NULLIF(SUM(CASE WHEN runs_off_bat IN (4, 6) THEN 1 ELSE 0 END), 0), 2
        ) AS balls_per_boundary
    FROM delivery_base
    GROUP BY season, batter_canonical
),

-- ----------------------------------------------------------------------------
-- 2. Phase-Wise Bowling Metrics
-- ----------------------------------------------------------------------------
bowling_phase_metrics AS (
    SELECT 
        season,
        bowler_canonical AS player_name,
        SUM(is_legal_ball) AS total_legal_balls,
        SUM(bowler_runs_conceded) AS total_runs_conceded,
        SUM(is_bowler_wicket) AS total_wickets,
        -- Powerplay Phase
        SUM(CASE WHEN match_phase = 'Powerplay' THEN is_bowler_wicket ELSE 0 END) AS pp_wickets,
        ROUND(
            CAST(SUM(CASE WHEN match_phase = 'Powerplay' THEN bowler_runs_conceded ELSE 0 END) AS FLOAT) 
            / NULLIF(SUM(CASE WHEN match_phase = 'Powerplay' THEN is_legal_ball ELSE 0 END) / 6.0, 0), 2
        ) AS pp_economy_rate,
        -- Middle Overs Phase
        SUM(CASE WHEN match_phase = 'Middle' THEN is_bowler_wicket ELSE 0 END) AS middle_wickets,
        ROUND(
            CAST(SUM(CASE WHEN match_phase = 'Middle' THEN bowler_runs_conceded ELSE 0 END) AS FLOAT) 
            / NULLIF(SUM(CASE WHEN match_phase = 'Middle' THEN is_legal_ball ELSE 0 END) / 6.0, 0), 2
        ) AS middle_economy_rate,
        -- Death Overs Phase
        SUM(CASE WHEN match_phase = 'Death' THEN is_legal_ball ELSE 0 END) AS death_legal_balls,
        SUM(CASE WHEN match_phase = 'Death' THEN is_bowler_wicket ELSE 0 END) AS death_wickets,
        ROUND(
            CAST(SUM(CASE WHEN match_phase = 'Death' THEN bowler_runs_conceded ELSE 0 END) AS FLOAT) 
            / NULLIF(SUM(CASE WHEN match_phase = 'Death' THEN is_legal_ball ELSE 0 END) / 6.0, 0), 2
        ) AS death_economy_rate,
        ROUND(
            CAST(SUM(CASE WHEN match_phase = 'Death' AND runs_off_bat = 0 AND wides = 0 AND noballs = 0 THEN 1 ELSE 0 END) AS FLOAT) 
            / NULLIF(SUM(CASE WHEN match_phase = 'Death' THEN is_legal_ball ELSE 0 END), 0) * 100, 2
        ) AS death_dot_ball_pct,
        -- Bowling Strike Rate (Legal deliveries per wicket)
        ROUND(
            CAST(SUM(is_legal_ball) AS FLOAT) / NULLIF(SUM(is_bowler_wicket), 0), 2
        ) AS bowling_strike_rate
    FROM delivery_base
    GROUP BY season, bowler_canonical
),

-- ----------------------------------------------------------------------------
-- 3. Player Consolidation
-- ----------------------------------------------------------------------------
player_season_combined AS (
    SELECT 
        COALESCE(b.season, w.season) AS season,
        COALESCE(b.player_name, w.player_name) AS player_name,
        COALESCE(b.total_runs, 0) AS total_runs,
        COALESCE(b.total_balls_faced, 0) AS total_balls_faced,
        COALESCE(b.pp_strike_rate, 0.0) AS pp_strike_rate,
        COALESCE(b.middle_strike_rate, 0.0) AS middle_strike_rate,
        COALESCE(b.death_strike_rate, 0.0) AS death_strike_rate,
        COALESCE(b.dot_ball_pct, 0.0) AS batting_dot_pct,
        COALESCE(b.balls_per_boundary, 999.0) AS balls_per_boundary,
        COALESCE(w.total_wickets, 0) AS total_wickets,
        COALESCE(w.total_legal_balls, 0) AS total_legal_balls,
        ROUND(CAST(COALESCE(w.total_runs_conceded, 0) AS FLOAT) / NULLIF(w.total_legal_balls / 6.0, 0), 2) AS overall_economy_rate,
        COALESCE(w.pp_wickets, 0) AS pp_wickets,
        COALESCE(w.pp_economy_rate, 0.0) AS pp_economy_rate,
        COALESCE(w.middle_wickets, 0) AS middle_wickets,
        COALESCE(w.death_economy_rate, 0.0) AS death_economy_rate,
        COALESCE(w.death_dot_ball_pct, 0.0) AS death_dot_pct,
        COALESCE(w.bowling_strike_rate, 999.0) AS bowling_strike_rate
    FROM batting_phase_metrics b
    LEFT JOIN bowling_phase_metrics w 
        ON b.player_name = w.player_name AND b.season = w.season
    UNION
    SELECT 
        w.season,
        w.player_name,
        0 AS total_runs,
        0 AS total_balls_faced,
        0.0 AS pp_strike_rate,
        0.0 AS middle_strike_rate,
        0.0 AS death_strike_rate,
        0.0 AS batting_dot_pct,
        999.0 AS balls_per_boundary,
        w.total_wickets,
        w.total_legal_balls,
        ROUND(CAST(w.total_runs_conceded AS FLOAT) / NULLIF(w.total_legal_balls / 6.0, 0), 2) AS overall_economy_rate,
        w.pp_wickets,
        w.pp_economy_rate,
        w.middle_wickets,
        w.death_economy_rate,
        w.death_dot_ball_pct AS death_dot_pct,
        w.bowling_strike_rate
    FROM bowling_phase_metrics w
    WHERE NOT EXISTS (
        SELECT 1 FROM batting_phase_metrics b 
        WHERE b.player_name = w.player_name AND b.season = w.season
    )
)

-- ----------------------------------------------------------------------------
-- 4. Financial Valuation & Efficiency Metrics
-- ----------------------------------------------------------------------------
SELECT 
    psc.season,
    psc.player_name,
    ap.franchise,
    ap.player_role,
    ap.is_capped,
    ap.is_overseas,
    ap.sold_price_inr_cr,
    (ap.sold_price_inr_cr * 10000000) AS sold_price_inr_absolute,
    psc.total_runs,
    psc.total_balls_faced,
    psc.pp_strike_rate,
    psc.middle_strike_rate,
    psc.death_strike_rate,
    psc.batting_dot_pct,
    psc.balls_per_boundary,
    psc.total_wickets,
    psc.total_legal_balls,
    psc.overall_economy_rate,
    psc.pp_wickets,
    psc.pp_economy_rate,
    psc.middle_wickets,
    psc.death_economy_rate,
    psc.death_dot_pct,
    psc.bowling_strike_rate,
    -- Financial Unit Economics (INR per Unit of Output)
    ROUND(
        (ap.sold_price_inr_cr * 10000000) / NULLIF(psc.total_runs, 0), 2
    ) AS cost_per_run_inr,
    ROUND(
        (ap.sold_price_inr_cr * 10000000) / NULLIF(psc.total_wickets, 0), 2
    ) AS cost_per_wicket_inr,
    -- Composite Valuation Index
    ROUND(
        (
            (COALESCE(psc.total_runs, 0) * 1.0) + 
            (COALESCE(psc.total_wickets, 0) * 20.0) +
            (CASE WHEN psc.death_strike_rate > 160 THEN 30 ELSE 0 END) +
            (CASE WHEN psc.death_economy_rate BETWEEN 0.1 AND 9.0 THEN 30 ELSE 0 END)
        ) / NULLIF(ap.sold_price_inr_cr, 0), 2
    ) AS performance_to_salary_value_score
FROM player_season_combined psc
INNER JOIN dim_auction_prices ap 
    ON psc.player_name = ap.standardized_name 
   AND psc.season = ap.season;
