-- ============================================================================
-- IPL FRANCHISE AUCTION INTELLIGENCE & PLAYER VALUATION PLATFORM
-- MODULE 1.3: DATA INGESTION SCRIPTS
-- ============================================================================

-- ============================================================================
-- OPTION A: PostgreSQL Bulk Ingestion (COPY via Staging)
-- ============================================================================

-- 1. Ingest dim_matches
COPY dim_matches (match_id, season, city, match_date, venue, team1, team2, toss_winner, toss_decision, winner, result_margin, player_of_match)
FROM '/path/to/data/dim_matches.csv'
WITH (FORMAT csv, HEADER true, NULL '', ENCODING 'UTF8');

-- 2. Ingest dim_player_registry
COPY dim_player_registry (cricsheet_name, canonical_name, primary_franchise, primary_role, is_capped, is_overseas)
FROM '/path/to/data/dim_player_registry.csv'
WITH (FORMAT csv, HEADER true, NULL '', ENCODING 'UTF8');

-- 3. Ingest dim_auction_prices
COPY dim_auction_prices (auction_id, player_name, standardized_name, franchise, season, player_role, base_price_inr_cr, sold_price_inr_cr, retention_status, is_capped, is_overseas)
FROM '/path/to/data/dim_auction_prices.csv'
WITH (FORMAT csv, HEADER true, NULL '', ENCODING 'UTF8');

-- 4. Ingest salary_cap_master
COPY salary_cap_master (season, salary_cap_inr_cr, min_squad_size, max_squad_size, max_overseas)
FROM '/path/to/data/salary_cap_master.csv'
WITH (FORMAT csv, HEADER true, NULL '', ENCODING 'UTF8');

-- 5. Ingest fact_deliveries using high-throughput staging
CREATE TEMP TABLE stage_deliveries (
    delivery_id BIGINT, match_id INT, inning SMALLINT, over SMALLINT, ball SMALLINT,
    batter VARCHAR(100), bowler VARCHAR(100), non_striker VARCHAR(100),
    runs_off_bat SMALLINT, extra_runs SMALLINT, wides SMALLINT, noballs SMALLINT,
    byes SMALLINT, legbyes SMALLINT, penalty SMALLINT, is_wicket SMALLINT,
    dismissal_kind VARCHAR(50), player_dismissed VARCHAR(100), fielder VARCHAR(100)
);

COPY stage_deliveries
FROM '/path/to/data/fact_deliveries.csv'
WITH (FORMAT csv, HEADER true, NULL '', ENCODING 'UTF8');

INSERT INTO fact_deliveries
SELECT 
    delivery_id, match_id, inning, over, ball,
    TRIM(batter), TRIM(bowler), TRIM(non_striker),
    COALESCE(runs_off_bat, 0), COALESCE(extra_runs, 0),
    COALESCE(wides, 0), COALESCE(noballs, 0),
    COALESCE(byes, 0), COALESCE(legbyes, 0), COALESCE(penalty, 0),
    COALESCE(is_wicket, 0),
    NULLIF(TRIM(dismissal_kind), ''),
    NULLIF(TRIM(player_dismissed), ''),
    NULLIF(TRIM(fielder), '')
FROM stage_deliveries;

DROP TABLE stage_deliveries;


-- ============================================================================
-- OPTION B: MySQL Bulk Ingestion (LOAD DATA INFILE)
-- ============================================================================

LOAD DATA INFILE '/var/lib/mysql-files/dim_matches.csv'
INTO TABLE dim_matches
FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/dim_player_registry.csv'
INTO TABLE dim_player_registry
FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/dim_auction_prices.csv'
INTO TABLE dim_auction_prices
FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA INFILE '/var/lib/mysql-files/fact_deliveries.csv'
INTO TABLE fact_deliveries
FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(delivery_id, match_id, inning, `over`, ball, batter, bowler, non_striker,
 runs_off_bat, extra_runs, wides, noballs, byes, legbyes, penalty, is_wicket,
 @v_dismissal_kind, @v_player_dismissed, @v_fielder)
SET 
    dismissal_kind   = NULLIF(TRIM(@v_dismissal_kind), ''),
    player_dismissed = NULLIF(TRIM(@v_player_dismissed), ''),
    fielder          = NULLIF(TRIM(@v_fielder), '');


-- ============================================================================
-- OPTION C: SQLite CLI Ingestion
-- ============================================================================
-- sqlite3 ipl_auction_intelligence.db
-- .mode csv
-- .import dim_matches.csv dim_matches
-- .import dim_player_registry.csv dim_player_registry
-- .import dim_auction_prices.csv dim_auction_prices
-- .import fact_deliveries.csv fact_deliveries
