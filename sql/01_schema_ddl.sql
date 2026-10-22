-- ============================================================================
-- IPL FRANCHISE AUCTION INTELLIGENCE & PLAYER VALUATION PLATFORM
-- MODULE 1: PRODUCTION RELATIONAL SCHEMA (DDL)
-- Compatible with: PostgreSQL, MySQL 8.0+, SQLite
-- ============================================================================

-- Drop existing tables in reverse order of foreign keys
DROP TABLE IF EXISTS fact_deliveries;
DROP TABLE IF EXISTS dim_auction_prices;
DROP TABLE IF EXISTS dim_player_registry;
DROP TABLE IF EXISTS dim_matches;
DROP TABLE IF EXISTS salary_cap_master;

-- ----------------------------------------------------------------------------
-- 1. MATCHES DIMENSION
-- Captures match-level context, conditions, and outcomes
-- ----------------------------------------------------------------------------
CREATE TABLE dim_matches (
    match_id           INT PRIMARY KEY,
    season             INT NOT NULL,
    city               VARCHAR(100),
    match_date         DATE NOT NULL,
    match_type         VARCHAR(20) DEFAULT 'T20',
    venue              VARCHAR(255) NOT NULL,
    team1              VARCHAR(100) NOT NULL,
    team2              VARCHAR(100) NOT NULL,
    toss_winner        VARCHAR(100),
    toss_decision      VARCHAR(10) CHECK (toss_decision IN ('bat', 'field')),
    winner             VARCHAR(100),
    result_margin      INT DEFAULT 0,
    player_of_match    VARCHAR(100)
);

-- ----------------------------------------------------------------------------
-- 2. PLAYER REGISTRY & NAME HARMONIZATION DIMENSION
-- Resolves Cricsheet abbreviated names to official registry names
-- ----------------------------------------------------------------------------
CREATE TABLE dim_player_registry (
    cricsheet_name     VARCHAR(100) PRIMARY KEY,
    canonical_name     VARCHAR(100) NOT NULL,
    primary_franchise  VARCHAR(100),
    primary_role       VARCHAR(50),
    is_capped          BOOLEAN DEFAULT TRUE,
    is_overseas        BOOLEAN DEFAULT FALSE
);

-- ----------------------------------------------------------------------------
-- 3. AUCTION CONTRACTS & FRANCHISE FINANCIALS DIMENSION
-- Captures transaction values, base prices, retentions, and cap status
-- ----------------------------------------------------------------------------
CREATE TABLE dim_auction_prices (
    auction_id          INT PRIMARY KEY,
    player_name         VARCHAR(100) NOT NULL,
    standardized_name   VARCHAR(100) NOT NULL,
    franchise           VARCHAR(100) NOT NULL,
    season              INT NOT NULL,
    player_role         VARCHAR(50) CHECK (player_role IN ('Batter', 'Bowler', 'All-Rounder', 'Wicketkeeper')),
    base_price_inr_cr   NUMERIC(6, 2) DEFAULT 0.00,
    sold_price_inr_cr   NUMERIC(6, 2) NOT NULL,
    retention_status    VARCHAR(30) DEFAULT 'Auction', -- 'Retained', 'Auction', 'Replacement', 'Draft'
    is_capped           BOOLEAN NOT NULL DEFAULT TRUE,
    is_overseas         BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT uq_player_season UNIQUE (standardized_name, season)
);

-- ----------------------------------------------------------------------------
-- 4. SALARY CAP MASTER DIMENSION
-- Official IPL purse limits and squad constraints
-- ----------------------------------------------------------------------------
CREATE TABLE salary_cap_master (
    season              INT PRIMARY KEY,
    salary_cap_inr_cr   NUMERIC(6, 2) NOT NULL,
    min_squad_size      INT DEFAULT 18,
    max_squad_size      INT DEFAULT 25,
    max_overseas        INT DEFAULT 8
);

-- ----------------------------------------------------------------------------
-- 5. BALL-BY-BALL DELIVERIES FACT TABLE
-- Granular delivery events with strict cricket-domain attributes
-- ----------------------------------------------------------------------------
CREATE TABLE fact_deliveries (
    delivery_id         BIGINT PRIMARY KEY,
    match_id            INT NOT NULL,
    inning              SMALLINT NOT NULL CHECK (inning IN (1, 2, 3, 4)),
    over                SMALLINT NOT NULL CHECK (over BETWEEN 0 AND 19),
    ball                SMALLINT NOT NULL CHECK (ball BETWEEN 1 AND 15),
    batter              VARCHAR(100) NOT NULL,
    bowler              VARCHAR(100) NOT NULL,
    non_striker         VARCHAR(100) NOT NULL,
    runs_off_bat        SMALLINT NOT NULL DEFAULT 0 CHECK (runs_off_bat BETWEEN 0 AND 6),
    extra_runs          SMALLINT NOT NULL DEFAULT 0,
    wides               SMALLINT NOT NULL DEFAULT 0,
    noballs             SMALLINT NOT NULL DEFAULT 0,
    byes                SMALLINT NOT NULL DEFAULT 0,
    legbyes             SMALLINT NOT NULL DEFAULT 0,
    penalty             SMALLINT NOT NULL DEFAULT 0,
    is_wicket           SMALLINT NOT NULL DEFAULT 0 CHECK (is_wicket IN (0, 1)),
    dismissal_kind      VARCHAR(50),
    player_dismissed    VARCHAR(100),
    fielder             VARCHAR(100),
    CONSTRAINT fk_deliv_match 
        FOREIGN KEY (match_id) REFERENCES dim_matches(match_id) 
        ON DELETE CASCADE
);

-- ----------------------------------------------------------------------------
-- HIGH-PERFORMANCE B-TREE INDEXES
-- Optimized for high-frequency analytical queries and joins
-- ----------------------------------------------------------------------------
CREATE INDEX idx_deliv_match_id   ON fact_deliveries (match_id);
CREATE INDEX idx_deliv_batter     ON fact_deliveries (batter);
CREATE INDEX idx_deliv_bowler     ON fact_deliveries (bowler);
CREATE INDEX idx_deliv_phase_agg  ON fact_deliveries (over, batter, bowler);
CREATE INDEX idx_matches_season   ON dim_matches (season, match_date);
CREATE INDEX idx_auction_lookup   ON dim_auction_prices (standardized_name, season);
