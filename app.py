"""
IPL Franchise Auction Intelligence & Player Valuation Platform
Executive Sports BI Portal (Seasons 2022 - 2026)
Corrected Mathematical KPIs, Verified Photos, and Intuitive UI
Author: Principal Sports Data Analyst & BI Architect
"""

import os
import sqlite3
import urllib.parse
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# -----------------------------------------------------------------------------
# Configuration & Theme Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="IPL Auction Intelligence & Valuation Platform",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .stApp {
        background: radial-gradient(130% 120% at 50% 5%, #0F172A 0%, #070B14 60%, #02040A 100%);
        color: #F8FAFC;
    }
    
    /* Header Cockpit Banner */
    .hero-banner {
        background: linear-gradient(135deg, rgba(30, 27, 75, 0.9) 0%, rgba(49, 46, 129, 0.8) 50%, rgba(15, 23, 42, 0.95) 100%);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 16px;
        padding: 22px 28px;
        box-shadow: 0 16px 36px -10px rgba(0, 0, 0, 0.6);
        margin-bottom: 20px;
    }
    
    /* Executive Metric Tiles */
    .kpi-tile {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.85) 0%, rgba(15, 23, 42, 0.95) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 16px 20px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .kpi-tile:hover {
        transform: translateY(-2px);
        border-color: rgba(56, 189, 248, 0.4);
    }
    .kpi-label {
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94A3B8;
        margin-bottom: 4px;
    }
    .kpi-val {
        font-size: 1.85rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: #F8FAFC;
    }
    .kpi-sub {
        font-size: 0.78rem;
        font-weight: 500;
        color: #38BDF8;
        margin-top: 3px;
    }
    
    /* Player Card Styling */
    .fut-card {
        background: linear-gradient(160deg, #1E293B 0%, #0F172A 70%, #020617 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.45);
        transition: all 0.25s ease;
        position: relative;
        overflow: hidden;
        margin-bottom: 18px;
    }
    .fut-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 18px 32px rgba(56, 189, 248, 0.22);
        border-color: #38BDF8;
    }
    .fut-card-header-stripe {
        height: 4px;
        width: 100%;
        position: absolute;
        top: 0;
        left: 0;
    }
    .avatar-wrapper {
        position: relative;
        width: 105px;
        height: 105px;
        margin: 10px auto 12px auto;
    }
    .player-img {
        width: 105px;
        height: 105px;
        border-radius: 50%;
        object-fit: cover;
        background: #0B0F19;
        display: block;
        box-shadow: 0 6px 14px rgba(0,0,0,0.6);
    }
    .card-player-name {
        font-size: 1.05rem;
        font-weight: 800;
        color: #FFFFFF;
        margin-bottom: 2px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .card-team-name {
        font-size: 0.78rem;
        color: #94A3B8;
        font-weight: 600;
        margin-bottom: 8px;
    }
    
    /* Stats Grid */
    .stat-pill-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 6px;
        background: rgba(0, 0, 0, 0.35);
        padding: 10px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        text-align: left;
        margin-top: 10px;
    }
    .stat-item {
        font-size: 0.75rem;
        color: #94A3B8;
    }
    .stat-val {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        color: #F8FAFC;
    }
    
    /* Badges */
    .val-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .badge-steal { background: rgba(16, 185, 129, 0.2); color: #34D399; border: 1px solid #10B981; }
    .badge-fair { background: rgba(59, 130, 246, 0.2); color: #60A5FA; border: 1px solid #3B82F6; }
    .badge-risk { background: rgba(239, 68, 68, 0.2); color: #F87171; border: 1px solid #EF4444; }
    .badge-target { background: rgba(245, 158, 11, 0.2); color: #FBBF24; border: 1px solid #F59E0B; }
    .badge-core { background: rgba(100, 116, 139, 0.2); color: #94A3B8; border: 1px solid #64748B; }

    /* Power BI Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(15, 23, 42, 0.8);
        padding: 8px 12px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 18px;
        font-weight: 600;
        font-size: 0.88rem;
        color: #94A3B8;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
        color: #FFFFFF !important;
    }

    /* Player Dossier Styles */
    .dossier-card {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 70%, #0B0F19 100%);
        border: 1px solid rgba(56, 189, 248, 0.35);
        border-radius: 18px;
        padding: 24px;
        box-shadow: 0 14px 40px rgba(0, 0, 0, 0.55);
        margin-bottom: 24px;
    }
    .dossier-hero {
        display: flex;
        align-items: center;
        gap: 24px;
        flex-wrap: wrap;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 20px;
        margin-bottom: 22px;
    }
    .dossier-img {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        object-fit: cover;
        box-shadow: 0 8px 24px rgba(0,0,0,0.6);
        background: #0B0F19;
    }
    .dossier-title {
        font-size: 2rem;
        font-weight: 800;
        color: #FFFFFF;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .dossier-sub {
        font-size: 1.05rem;
        color: #94A3B8;
        margin-top: 4px;
    }
    .dossier-metric-box {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 14px 16px;
        text-align: center;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .dossier-metric-box:hover {
        transform: translateY(-2px);
        border-color: rgba(56, 189, 248, 0.5);
    }
    .dossier-metric-lbl {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        color: #94A3B8;
        letter-spacing: 0.05em;
    }
    .dossier-metric-val {
        font-size: 1.55rem;
        font-weight: 800;
        color: #F8FAFC;
        margin-top: 3px;
    }
    .dossier-metric-sub {
        font-size: 0.72rem;
        color: #38BDF8;
        margin-top: 2px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Database Loading
# -----------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "ipl_auction_intelligence.db")

# Retired Cricketers Master Exclusions
RETIRED_PLAYERS = {
    # Full Canonical Names
    "Dinesh Karthik",
    "Shikhar Dhawan",
    "Ambati Rayudu",
    "Wriddhiman Saha",
    "Varun Aaron",
    "Aaron Finch",
    "Dwayne Bravo",
    "DJ Bravo",
    "Kieron Pollard",
    "KA Pollard",
    "Robin Uthappa",
    "RV Uthappa",
    "Kedar Jadhav",
    "KM Jadhav",
    "Amit Mishra",
    "A Mishra",
    "David Willey",
    "DJ Willey",
    "Dwaine Pretorius",
    "D Pretorius",
    "Siddarth Kaul",
    "S Kaul",
    "Matthew Wade",
    "MS Wade",
    "Wayne Parnell",
    "WD Parnell",
    "Nathan Coulter-Nile",
    "NM Coulter-Nile",
    "Murali Vijay",
    "Suresh Raina",
    "Eoin Morgan",
    # Cricsheet / Short Aliases
    "KD Karthik",
    "S Dhawan",
    "AT Rayudu",
    "WP Saha",
    "VR Aaron",
    "AJ Finch",
}

# Comprehensive Verified Photo Mapping (ESPN CDN + Wikimedia Direct Portraits)
VERIFIED_PHOTOS = {
    "Virat Kohli": "https://a.espncdn.com/i/headshots/cricket/players/full/253802.png",
    "Rohit Sharma": "https://a.espncdn.com/i/headshots/cricket/players/full/34102.png",
    "Jasprit Bumrah": "https://a.espncdn.com/i/headshots/cricket/players/full/625383.png",
    "MS Dhoni": "https://a.espncdn.com/i/headshots/cricket/players/full/28081.png",
    "Hardik Pandya": "https://a.espncdn.com/i/headshots/cricket/players/full/625371.png",
    "Ravindra Jadeja": "https://a.espncdn.com/i/headshots/cricket/players/full/234675.png",
    "Rishabh Pant": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Rishabh_Pant.jpg/330px-Rishabh_Pant.jpg",
    "Shubman Gill": "https://a.espncdn.com/i/headshots/cricket/players/full/1070173.png",
    "Pat Cummins": "https://a.espncdn.com/i/headshots/cricket/players/full/489889.png",
    "Travis Head": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Travis_Head_bowling_at_Perth_Stadium%2C_First_Test_Australia_versus_West_Indies%2C_2_December_2022_03_%28cropped%29.jpg/330px-Travis_Head_bowling_at_Perth_Stadium%2C_First_Test_Australia_versus_West_Indies%2C_2_December_2022_03_%28cropped%29.jpg",
    "Mitchell Starc": "https://a.espncdn.com/i/headshots/cricket/players/full/311592.png",
    "Ruturaj Gaikwad": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/27/Ruturaj_Gaikwad.jpeg/330px-Ruturaj_Gaikwad.jpeg",
    "KL Rahul": "https://a.espncdn.com/i/headshots/cricket/players/full/422108.png",
    "Sanju Samson": "https://upload.wikimedia.org/wikipedia/commons/7/70/Sanju_Samson_in_PMO_New_Delhi.jpg",
    "Trent Boult": "https://a.espncdn.com/i/headshots/cricket/players/full/277912.png",
    "David Miller": "https://a.espncdn.com/i/headshots/cricket/players/full/321777.png",
    "Glenn Maxwell": "https://a.espncdn.com/i/headshots/cricket/players/full/325026.png",
    "Jos Buttler": "https://a.espncdn.com/i/headshots/cricket/players/full/308967.png",
    "Andre Russell": "https://a.espncdn.com/i/headshots/cricket/players/full/276298.png",
    "Suryakumar Yadav": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Suryakumar_Yadav_in_PMO_New_Delhi.jpg/330px-Suryakumar_Yadav_in_PMO_New_Delhi.jpg",
    "Yashasvi Jaiswal": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/75/Yashasvi_Jaiswal_in_PMO_New_Delhi.jpg/330px-Yashasvi_Jaiswal_in_PMO_New_Delhi.jpg",
    "Axar Patel": "https://a.espncdn.com/i/headshots/cricket/players/full/554691.png",
    "Kuldeep Yadav": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Kuldeep_Yadav_in_PMO_New_Delhi.jpg/330px-Kuldeep_Yadav_in_PMO_New_Delhi.jpg",
    "Mohammed Siraj": "https://a.espncdn.com/i/headshots/cricket/players/full/940973.png",
    "Mohammed Shami": "https://a.espncdn.com/i/headshots/cricket/players/full/481896.png",
    "Bhuvneshwar Kumar": "https://a.espncdn.com/i/headshots/cricket/players/full/326016.png",
    "Arshdeep Singh": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/Arshdeep_Singh_in_PMO_New_Delhi.jpg/330px-Arshdeep_Singh_in_PMO_New_Delhi.jpg",
    "Yuzvendra Chahal": "https://a.espncdn.com/i/headshots/cricket/players/full/430246.png",
    "Heinrich Klaasen": "https://a.espncdn.com/i/headshots/cricket/players/full/438862.png",
    "Nicholas Pooran": "https://a.espncdn.com/i/headshots/cricket/players/full/604302.png",
    "Rinku Singh": "https://a.espncdn.com/i/headshots/cricket/players/full/723105.png",
    "Sunil Narine": "https://a.espncdn.com/i/headshots/cricket/players/full/230558.png",
    "Rashid Khan": "https://a.espncdn.com/i/headshots/cricket/players/full/793463.png",
    "Harshit Rana": "https://a.espncdn.com/i/headshots/cricket/players/full/1310619.png",
    "Shreyas Iyer": "https://a.espncdn.com/i/headshots/cricket/players/full/642519.png",
    "Kane Williamson": "https://a.espncdn.com/i/headshots/cricket/players/full/277906.png",
    "Faf du Plessis": "https://a.espncdn.com/i/headshots/cricket/players/full/44828.png",
    "Mitchell Marsh": "https://a.espncdn.com/i/headshots/cricket/players/full/272450.png",
    "Quinton de Kock": "https://a.espncdn.com/i/headshots/cricket/players/full/379143.png",
    "Sam Curran": "https://a.espncdn.com/i/headshots/cricket/players/full/662973.png",
    "Marcus Stoinis": "https://a.espncdn.com/i/headshots/cricket/players/full/325012.png",
    "Josh Hazlewood": "https://a.espncdn.com/i/headshots/cricket/players/full/288284.png",
    "Dinesh Karthik": "https://a.espncdn.com/i/headshots/cricket/players/full/30045.png",
    "Kagiso Rabada": "https://a.espncdn.com/i/headshots/cricket/players/full/550215.png",
    "Ajinkya Rahane": "https://a.espncdn.com/i/headshots/cricket/players/full/277916.png",
    "Umesh Yadav": "https://a.espncdn.com/i/headshots/cricket/players/full/376116.png",
    "Shikhar Dhawan": "https://a.espncdn.com/i/headshots/cricket/players/full/28235.png",
    "Ravichandran Ashwin": "https://a.espncdn.com/i/headshots/cricket/players/full/26421.png",
    "Khaleel Ahmed": "https://a.espncdn.com/i/headshots/cricket/players/full/942645.png"
}

FRANCHISE_META = {
    "Chennai Super Kings": {
        "color": "#FACC15", "color_rgb": "250, 204, 21", "text": "#0F172A", "short": "CSK", "badge": "🦁",
        "logo": "https://a.espncdn.com/i/teamlogos/cricket/500/335974.png"
    },
    "Mumbai Indians": {
        "color": "#0284C7", "color_rgb": "2, 132, 199", "text": "#FFFFFF", "short": "MI", "badge": "🌀",
        "logo": "https://a.espncdn.com/i/teamlogos/cricket/500/335978.png"
    },
    "Royal Challengers Bengaluru": {
        "color": "#DC2626", "color_rgb": "220, 38, 38", "text": "#FFFFFF", "short": "RCB", "badge": "👑",
        "logo": "https://a.espncdn.com/i/teamlogos/cricket/500/335970.png"
    },
    "Kolkata Knight Riders": {
        "color": "#7C3AED", "color_rgb": "124, 58, 237", "text": "#FFFFFF", "short": "KKR", "badge": "⚔️",
        "logo": "https://a.espncdn.com/i/teamlogos/cricket/500/335971.png"
    },
    "Sunrisers Hyderabad": {
        "color": "#F97316", "color_rgb": "249, 115, 22", "text": "#FFFFFF", "short": "SRH", "badge": "🦅",
        "logo": "https://a.espncdn.com/i/teamlogos/cricket/500/628333.png"
    },
    "Rajasthan Royals": {
        "color": "#EC4899", "color_rgb": "236, 72, 153", "text": "#FFFFFF", "short": "RR", "badge": "🛡️",
        "logo": "https://a.espncdn.com/i/teamlogos/cricket/500/335977.png"
    },
    "Gujarat Titans": {
        "color": "#1E3A8A", "color_rgb": "30, 58, 138", "text": "#FFFFFF", "short": "GT", "badge": "⚡",
        "logo": "https://upload.wikimedia.org/wikipedia/en/0/09/Gujarat_Titans_Logo.svg"
    },
    "Lucknow Super Giants": {
        "color": "#06B6D4", "color_rgb": "6, 182, 212", "text": "#FFFFFF", "short": "LSG", "badge": "🏹",
        "logo": "https://upload.wikimedia.org/wikipedia/en/3/34/Lucknow_Super_Giants_Logo.svg"
    },
    "Delhi Capitals": {
        "color": "#2563EB", "color_rgb": "37, 99, 235", "text": "#FFFFFF", "short": "DC", "badge": "🐅",
        "logo": "https://a.espncdn.com/i/teamlogos/cricket/500/335975.png"
    },
    "Punjab Kings": {
        "color": "#E11D48", "color_rgb": "225, 29, 72", "text": "#FFFFFF", "short": "PBKS", "badge": "🦁",
        "logo": "https://a.espncdn.com/i/teamlogos/cricket/500/335973.png"
    },
    "Other / Unassigned": {
        "color": "#64748B", "color_rgb": "100, 116, 139", "text": "#FFFFFF", "short": "IPL", "badge": "🏏",
        "logo": "https://a.espncdn.com/i/leaguelogos/cricket/500/8048.png"
    }
}

def get_display_avatar(player_name, franchise):
    if player_name in VERIFIED_PHOTOS:
        return VERIFIED_PHOTOS[player_name]
    f_info = FRANCHISE_META.get(franchise, FRANCHISE_META["Other / Unassigned"])
    hex_color = f_info["color"].replace("#", "")
    text_color = f_info["text"].replace("#", "")
    return f"https://ui-avatars.com/api/?name={urllib.parse.quote(player_name)}&background={hex_color}&color={text_color}&size=256&bold=true&font-size=0.40"

@st.cache_data(ttl=600)
def load_mart_data():
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM vw_scouting_master_mart"
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Accurate Value Classification Rule
    def categorize(row):
        price = row["sold_price_inr_cr"]
        runs = row["total_runs"]
        wkts = row["total_wickets"]
        d_sr = row["death_strike_rate"]
        val_score = row["performance_to_salary_value_score"]
        
        # High impact with contract <= 6 Cr
        if price <= 6.0 and (runs >= 150 or wkts >= 6 or d_sr >= 155.0 or val_score >= 40.0):
            return "Steal Buy"
        elif price >= 12.0 and (runs < 260 and wkts < 7):
            return "Overpriced Risk"
        elif price >= 8.0:
            return "Elite Core"
        elif d_sr >= 165.0:
            return "Scouting Target"
        else:
            return "Squad Value"

    df["value_buy_category"] = df.apply(categorize, axis=1)
    return df

@st.cache_data(ttl=600)
def load_player_registry():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM dim_player_registry", conn)
    conn.close()
    return df

@st.cache_data(ttl=600)
def load_team_analytics():
    conn = sqlite3.connect(DB_PATH)
    team_games_sql = """
    WITH normalized_games AS (
        SELECT 
            season,
            match_id,
            CASE WHEN team1 = 'Royal Challengers Bangalore' THEN 'Royal Challengers Bengaluru' ELSE team1 END AS team,
            CASE WHEN (CASE WHEN winner = 'Royal Challengers Bangalore' THEN 'Royal Challengers Bengaluru' ELSE winner END) = 
                      (CASE WHEN team1 = 'Royal Challengers Bangalore' THEN 'Royal Challengers Bengaluru' ELSE team1 END) THEN 1 ELSE 0 END AS won
        FROM dim_matches
        UNION ALL
        SELECT 
            season,
            match_id,
            CASE WHEN team2 = 'Royal Challengers Bangalore' THEN 'Royal Challengers Bengaluru' ELSE team2 END AS team,
            CASE WHEN (CASE WHEN winner = 'Royal Challengers Bangalore' THEN 'Royal Challengers Bengaluru' ELSE winner END) = 
                      (CASE WHEN team2 = 'Royal Challengers Bangalore' THEN 'Royal Challengers Bengaluru' ELSE team2 END) THEN 1 ELSE 0 END AS won
        FROM dim_matches
    )
    SELECT 
        season,
        team,
        COUNT(DISTINCT match_id) AS matches_played,
        SUM(won) AS wins,
        COUNT(DISTINCT match_id) - SUM(won) AS losses,
        ROUND(CAST(SUM(won) AS FLOAT) / COUNT(DISTINCT match_id) * 100, 1) AS win_pct
    FROM normalized_games
    WHERE team IN (
        'Chennai Super Kings', 'Mumbai Indians', 'Royal Challengers Bengaluru', 
        'Kolkata Knight Riders', 'Sunrisers Hyderabad', 'Rajasthan Royals', 
        'Gujarat Titans', 'Lucknow Super Giants', 'Delhi Capitals', 'Punjab Kings'
    )
    GROUP BY season, team;
    """
    df_team_seasons = pd.read_sql_query(team_games_sql, conn)
    
    # Career team stats
    team_career_sql = """
    WITH normalized_games AS (
        SELECT 
            match_id,
            CASE WHEN team1 = 'Royal Challengers Bangalore' THEN 'Royal Challengers Bengaluru' ELSE team1 END AS team,
            CASE WHEN (CASE WHEN winner = 'Royal Challengers Bangalore' THEN 'Royal Challengers Bengaluru' ELSE winner END) = 
                      (CASE WHEN team1 = 'Royal Challengers Bangalore' THEN 'Royal Challengers Bengaluru' ELSE team1 END) THEN 1 ELSE 0 END AS won
        FROM dim_matches
        UNION ALL
        SELECT 
            match_id,
            CASE WHEN team2 = 'Royal Challengers Bangalore' THEN 'Royal Challengers Bengaluru' ELSE team2 END AS team,
            CASE WHEN (CASE WHEN winner = 'Royal Challengers Bangalore' THEN 'Royal Challengers Bengaluru' ELSE winner END) = 
                      (CASE WHEN team2 = 'Royal Challengers Bangalore' THEN 'Royal Challengers Bengaluru' ELSE team2 END) THEN 1 ELSE 0 END AS won
        FROM dim_matches
    )
    SELECT 
        team,
        COUNT(DISTINCT match_id) AS matches_played,
        SUM(won) AS wins,
        COUNT(DISTINCT match_id) - SUM(won) AS losses,
        ROUND(CAST(SUM(won) AS FLOAT) / COUNT(DISTINCT match_id) * 100, 1) AS win_pct
    FROM normalized_games
    WHERE team IN (
        'Chennai Super Kings', 'Mumbai Indians', 'Royal Challengers Bengaluru', 
        'Kolkata Knight Riders', 'Sunrisers Hyderabad', 'Rajasthan Royals', 
        'Gujarat Titans', 'Lucknow Super Giants', 'Delhi Capitals', 'Punjab Kings'
    )
    GROUP BY team
    ORDER BY win_pct DESC;
    """
    df_team_career = pd.read_sql_query(team_career_sql, conn)
    conn.close()
    return df_team_seasons, df_team_career

@st.cache_data(ttl=600)
def load_player_match_history():
    conn = sqlite3.connect(DB_PATH)
    bat_sql = """
    SELECT 
        m.season,
        m.match_date,
        m.venue,
        f.batting_team AS match_team,
        CASE WHEN m.team1 = f.batting_team THEN m.team2 ELSE m.team1 END AS opponent_team,
        m.team1,
        m.team2,
        f.match_id,
        pr.canonical_name,
        pr.primary_franchise,
        pr.career_franchises,
        SUM(f.runs_off_bat) AS runs,
        COUNT(CASE WHEN f.wides = 0 THEN 1 END) AS balls,
        SUM(CASE WHEN f.runs_off_bat = 4 THEN 1 ELSE 0 END) AS fours,
        SUM(CASE WHEN f.runs_off_bat = 6 THEN 1 ELSE 0 END) AS sixes,
        MAX(CASE WHEN f.player_dismissed = f.batter THEN 1 ELSE 0 END) AS is_out,
        MAX(CASE WHEN f.player_dismissed = f.batter THEN f.dismissal_kind ELSE NULL END) AS dismissal_kind
    FROM fact_deliveries f
    JOIN dim_matches m ON f.match_id = m.match_id
    JOIN dim_player_registry pr ON f.batter = pr.cricsheet_name
    GROUP BY m.season, m.match_date, m.venue, f.batting_team, opponent_team, m.team1, m.team2, f.match_id, pr.canonical_name, pr.primary_franchise, pr.career_franchises
    """
    df_bat = pd.read_sql_query(bat_sql, conn)
    
    bowl_sql = """
    SELECT 
        m.season,
        m.match_date,
        m.venue,
        f.bowling_team AS match_team,
        CASE WHEN m.team1 = f.bowling_team THEN m.team2 ELSE m.team1 END AS opponent_team,
        m.team1,
        m.team2,
        f.match_id,
        pr.canonical_name,
        pr.primary_franchise,
        pr.career_franchises,
        COUNT(CASE WHEN f.wides = 0 AND f.noballs = 0 THEN 1 END) AS balls,
        SUM(f.runs_off_bat + f.wides + f.noballs) AS runs_conceded,
        SUM(CASE WHEN f.is_wicket = 1 AND f.dismissal_kind NOT IN ('run out', 'retired hurt', 'retired out', 'obstructing the field') THEN 1 ELSE 0 END) AS wickets,
        SUM(CASE WHEN f.runs_off_bat = 0 AND f.wides = 0 AND f.noballs = 0 THEN 1 ELSE 0 END) AS dots
    FROM fact_deliveries f
    JOIN dim_matches m ON f.match_id = m.match_id
    JOIN dim_player_registry pr ON f.bowler = pr.cricsheet_name
    GROUP BY m.season, m.match_date, m.venue, f.bowling_team, opponent_team, m.team1, m.team2, f.match_id, pr.canonical_name, pr.primary_franchise, pr.career_franchises
    """
    df_bowl = pd.read_sql_query(bowl_sql, conn)
    conn.close()
    return df_bat, df_bowl

df_mart = load_mart_data()
df_mart = df_mart[~df_mart["player_name"].isin(RETIRED_PLAYERS)].copy()

df_registry = load_player_registry()
df_registry = df_registry[~df_registry["canonical_name"].isin(RETIRED_PLAYERS) & ~df_registry["cricsheet_name"].isin(RETIRED_PLAYERS)].copy()

df_team_seasons, df_team_career = load_team_analytics()

df_bat_history, df_bowl_history = load_player_match_history()
df_bat_history = df_bat_history[~df_bat_history["canonical_name"].isin(RETIRED_PLAYERS)].copy()
df_bowl_history = df_bowl_history[~df_bowl_history["canonical_name"].isin(RETIRED_PLAYERS)].copy()

# -----------------------------------------------------------------------------
# Easy Top Filter Bar (No need to open sidebar unless desired)
# -----------------------------------------------------------------------------
st.markdown("""
<div class="hero-banner">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div>
            <h1 style="margin: 0; font-size: 2rem; font-weight: 800; color: #FFFFFF;">
                🏏 IPL Auction Intelligence & Player Valuation
            </h1>
            <p style="margin: 5px 0 0 0; color: #94A3B8; font-size: 0.95rem;">
                Franchise Strategy: Ball-by-Ball Leverage (Powerplay vs Death) & True Financial Economics
            </p>
        </div>
        <div style="text-align: right; margin-top: 8px;">
            <span class="val-badge badge-steal">87k+ Deliveries Ingested</span>
        </div>
    </div>
    <!-- 10 Franchise Official Logos Ribbon -->
    <div style="display: flex; gap: 14px; align-items: center; justify-content: space-around; flex-wrap: wrap; margin-top: 18px; padding-top: 14px; border-top: 1px solid rgba(255,255,255,0.08);">
        <div title="Chennai Super Kings" style="text-align: center;"><img src="https://a.espncdn.com/i/teamlogos/cricket/500/335974.png" style="width: 42px; height: 42px; object-fit: contain;"/><div style="font-size: 0.7rem; font-weight: 700; color: #FACC15; margin-top: 2px;">CSK</div></div>
        <div title="Mumbai Indians" style="text-align: center;"><img src="https://a.espncdn.com/i/teamlogos/cricket/500/335978.png" style="width: 42px; height: 42px; object-fit: contain;"/><div style="font-size: 0.7rem; font-weight: 700; color: #38BDF8; margin-top: 2px;">MI</div></div>
        <div title="Royal Challengers Bengaluru" style="text-align: center;"><img src="https://a.espncdn.com/i/teamlogos/cricket/500/335970.png" style="width: 42px; height: 42px; object-fit: contain;"/><div style="font-size: 0.7rem; font-weight: 700; color: #DC2626; margin-top: 2px;">RCB</div></div>
        <div title="Kolkata Knight Riders" style="text-align: center;"><img src="https://a.espncdn.com/i/teamlogos/cricket/500/335971.png" style="width: 42px; height: 42px; object-fit: contain;"/><div style="font-size: 0.7rem; font-weight: 700; color: #A855F7; margin-top: 2px;">KKR</div></div>
        <div title="Sunrisers Hyderabad" style="text-align: center;"><img src="https://a.espncdn.com/i/teamlogos/cricket/500/628333.png" style="width: 42px; height: 42px; object-fit: contain;"/><div style="font-size: 0.7rem; font-weight: 700; color: #F97316; margin-top: 2px;">SRH</div></div>
        <div title="Rajasthan Royals" style="text-align: center;"><img src="https://a.espncdn.com/i/teamlogos/cricket/500/335977.png" style="width: 42px; height: 42px; object-fit: contain;"/><div style="font-size: 0.7rem; font-weight: 700; color: #EC4899; margin-top: 2px;">RR</div></div>
        <div title="Gujarat Titans" style="text-align: center;"><img src="https://upload.wikimedia.org/wikipedia/en/0/09/Gujarat_Titans_Logo.svg" style="width: 42px; height: 42px; object-fit: contain;"/><div style="font-size: 0.7rem; font-weight: 700; color: #60A5FA; margin-top: 2px;">GT</div></div>
        <div title="Lucknow Super Giants" style="text-align: center;"><img src="https://upload.wikimedia.org/wikipedia/en/3/34/Lucknow_Super_Giants_Logo.svg" style="width: 42px; height: 42px; object-fit: contain;"/><div style="font-size: 0.7rem; font-weight: 700; color: #06B6D4; margin-top: 2px;">LSG</div></div>
        <div title="Delhi Capitals" style="text-align: center;"><img src="https://a.espncdn.com/i/teamlogos/cricket/500/335975.png" style="width: 42px; height: 42px; object-fit: contain;"/><div style="font-size: 0.7rem; font-weight: 700; color: #2563EB; margin-top: 2px;">DC</div></div>
        <div title="Punjab Kings" style="text-align: center;"><img src="https://a.espncdn.com/i/teamlogos/cricket/500/335973.png" style="width: 42px; height: 42px; object-fit: contain;"/><div style="font-size: 0.7rem; font-weight: 700; color: #E11D48; margin-top: 2px;">PBKS</div></div>
    </div>
</div>
""", unsafe_allow_html=True)

# Instant Controls Row
top_c1, top_c2, top_c3, top_c4 = st.columns([1.2, 1.8, 1.5, 1.5])
with top_c1:
    # Default to 2026 (latest mega-auction rosters & retentions)
    available_seasons = sorted(list(df_mart["season"].unique()), reverse=True)
    def_season_idx = available_seasons.index(2026) if 2026 in available_seasons else 0
    selected_season = st.selectbox(
        "📅 Tournament Season:", 
        available_seasons, 
        index=def_season_idx,
        help="2026 = Latest IPL Rosters & Contracts (Sanju Samson in CSK, Trent Boult in MI, Salt in RCB)."
    )
with top_c2:
    available_franchises = ["All Franchises (All 10 Teams)"] + sorted(list(df_mart["franchise"].dropna().unique()))
    selected_franchise = st.selectbox("🏟️ Franchise:", available_franchises)
with top_c3:
    available_roles = ["All Roles (All Disciplines)"] + sorted(list(df_mart["player_role"].dropna().unique()))
    selected_role = st.selectbox("👤 Role / Discipline:", available_roles)
with top_c4:
    default_purse = 125.0 if selected_season == 2026 else (120.0 if selected_season == 2025 else 100.0)
    simulated_purse = st.number_input("💰 Salary Cap Purse (₹ Cr):", min_value=80.0, max_value=150.0, value=default_purse, step=5.0)

# Filter Dataset
filtered_df = df_mart[df_mart["season"] == selected_season].copy()
if "All Franchises" not in selected_franchise:
    filtered_df = filtered_df[filtered_df["franchise"] == selected_franchise]
if "All Roles" not in selected_role:
    filtered_df = filtered_df[filtered_df["player_role"] == selected_role]

# -----------------------------------------------------------------------------
# Mathematically Accurate Financial & Output KPIs
# -----------------------------------------------------------------------------
total_spend = filtered_df["sold_price_inr_cr"].sum()

# 1. Weighted Cost Per Run: (Batters spend * 1 Cr) / Total Runs
batters_df = filtered_df[filtered_df["total_runs"] > 0]
if len(batters_df) > 0 and batters_df["total_runs"].sum() > 0:
    raw_cost_run = (batters_df["sold_price_inr_cr"].sum() * 10000000) / batters_df["total_runs"].sum()
    formatted_cost_run = f"₹{raw_cost_run/100000:.2f} Lakh" if raw_cost_run >= 100000 else f"₹{raw_cost_run:,.0f}"
else:
    raw_cost_run = 0
    formatted_cost_run = "N/A"

# 2. Weighted Cost Per Wicket: (Bowlers spend * 1 Cr) / Total Wickets
bowlers_df = filtered_df[filtered_df["total_wickets"] > 0]
if len(bowlers_df) > 0 and bowlers_df["total_wickets"].sum() > 0:
    raw_cost_wkt = (bowlers_df["sold_price_inr_cr"].sum() * 10000000) / bowlers_df["total_wickets"].sum()
    formatted_cost_wkt = f"₹{raw_cost_wkt/100000:.1f} Lakh" if raw_cost_wkt >= 100000 else f"₹{raw_cost_wkt:,.0f}"
else:
    raw_cost_wkt = 0
    formatted_cost_wkt = "N/A"

# 3. Steal Buys Count
steal_buys_df = filtered_df[filtered_df["value_buy_category"] == "Steal Buy"]
steal_count = len(steal_buys_df)

# KPI Row Display
k1, k2, k3, k4 = st.columns(4)
with k1:
    is_all = "All Franchises" in selected_franchise
    cap_pct = (total_spend / simulated_purse) * 100 if not is_all else None
    tile_sub = f"{cap_pct:.1f}% of Franchise Cap Used" if not is_all else f"Total Spend on {len(filtered_df)} Star Contracts"
    tile_title = "Tracked Purse Spend" if is_all else f"{selected_franchise.split()[0]} Spend"
    st.markdown(f"""
    <div class="kpi-tile">
        <div class="kpi-label">{tile_title}</div>
        <div class="kpi-val">₹{total_spend:,.1f} Cr</div>
        <div class="kpi-sub">{tile_sub}</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-tile">
        <div class="kpi-label">Cost to Buy 1 Run</div>
        <div class="kpi-val">{formatted_cost_run}</div>
        <div class="kpi-sub">Franchise investment per run scored</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-tile">
        <div class="kpi-label">Cost to Buy 1 Wicket</div>
        <div class="kpi-val">{formatted_cost_wkt}</div>
        <div class="kpi-sub">Bowling spend per dismissal taken</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-tile">
        <div class="kpi-label">Identified "Steal Buys"</div>
        <div class="kpi-val" style="color: #34D399;">{steal_count} Players</div>
        <div class="kpi-sub">High-impact match winners (≤ ₹6 Cr)</div>
    </div>
    """, unsafe_allow_html=True)

# Interactive English Explainer Box
with st.expander("💡 Understanding Core Valuation Metrics (Tracked Spend, Cost/Run, Cost/Wicket)"):
    st.markdown(f"""
    1. **Tracked Purse Spend:**
       - Across 10 franchises, when **"All Franchises"** is active, this captures the aggregated auction commitments (**₹{total_spend:.1f} Cr**).
       - When a single franchise is selected (e.g. *CSK* or *MI*), it reflects that specific team's salary cap utilization.
    
    2. **Cost to Buy 1 Run ({formatted_cost_run} / run):**
       - **Formula:** `Total Batters Contract Value ÷ Total Runs Scored by Batters`.
       - **Strategic Importance:** Quantifies offensive capital efficiency. Uncapped sensations like **Shashank Singh** produced runs at just **₹5,650/run** (exceptional ROI), whereas marquee ₹17+ Cr signings cost over **₹3.26 Lakh/run**.
    
    3. **Cost to Buy 1 Wicket ({formatted_cost_wkt} / wicket):**
       - **Formula:** `Total Bowlers Contract Value ÷ Total Wickets Claimed`.
       - **Strategic Importance:** Determines defensive ROI. Breakout stars like **Harshit Rana** delivered wickets at **₹1.05 Lakh/wicket**, while record contracts like **Mitchell Starc** delivered at **₹1.45 Cr/wicket**.
    """)

st.markdown("<br>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Power BI Tabs
# -----------------------------------------------------------------------------
tab_dossier, tab_teams, tab_matrix, tab_radar, tab_gallery, tab_bowling, tab_excel, tab_powerbi, tab_sql = st.tabs([
    "🎖️ Player 360° Comprehensive Dossier",
    "🏆 Franchise Standings & Team Hub",
    "📊 Executive Valuation Matrix",
    "🎯 Head-to-Head Scout Radar",
    "🌟 Player Spotlight & Gallery",
    "⚡ Bowling Threat & Pressure",
    "📑 Excel Analytics & Cleansing Hub",
    "📈 Power BI Modeling & DAX Hub",
    "💾 Live SQL Query Console"
])

# =============================================================================
# TAB 0: PLAYER 360° COMPREHENSIVE DOSSIER & CAREER MILESTONES
# =============================================================================
with tab_dossier:
    st.markdown("### 🎖️ Player 360° Comprehensive Dossier & Career Milestones")
    st.caption("Select any player to inspect comprehensive career milestones (Runs, 100s, 50s, 4s, 6s, Wickets, Best Bowling, Salary & Phase Splits):")
    
    # Player Selection & Controls - All Active IPL Stars in Registry
    all_player_names = sorted([
        p for p in set(df_registry["canonical_name"].dropna().unique()).union(set(df_bat_history["canonical_name"].dropna().unique()))
        if p not in RETIRED_PLAYERS
    ])
    
    # Prefer Sanju Samson or Virat Kohli as initial selection
    def_dossier_name = "Sanju Samson" if "Sanju Samson" in all_player_names else all_player_names[0]
    
    col_sel1, col_sel2 = st.columns([2, 1.2])
    with col_sel1:
        sel_dossier_player = st.selectbox(
            "🔍 Select Player to Inspect:",
            all_player_names,
            index=all_player_names.index(def_dossier_name) if def_dossier_name in all_player_names else 0,
            help="Type or select any player from the 380+ player master database."
        )
    with col_sel2:
        dossier_scope = st.radio(
            "📊 Data Scope:",
            [f"Selected Season ({selected_season})", "Full IPL Career (2022-2026)"],
            horizontal=True
        )
    
    # Retrieve Player Metadata (Registry + Mart)
    p_reg_match = df_registry[df_registry["canonical_name"] == sel_dossier_player]
    if len(p_reg_match) > 0:
        reg_info = p_reg_match.iloc[0]
        latest_franchise = reg_info["primary_franchise"]
        player_role = reg_info["primary_role"]
        is_capped = bool(reg_info["is_capped"])
        is_overseas = bool(reg_info["is_overseas"])
        career_journey = reg_info["career_franchises"] if "career_franchises" in reg_info and pd.notna(reg_info["career_franchises"]) else latest_franchise
    else:
        latest_franchise = "Other / Unassigned"
        player_role = "Batter"
        is_capped = True
        is_overseas = False
        career_journey = "Unassigned"

    # Filter ball-by-ball match history
    is_season_scope = "Selected Season" in dossier_scope
    scope_season_val = selected_season if is_season_scope else None
    
    b_df = df_bat_history[df_bat_history["canonical_name"] == sel_dossier_player]
    bw_df = df_bowl_history[df_bowl_history["canonical_name"] == sel_dossier_player]
    
    if is_season_scope:
        b_df = b_df[b_df["season"] == scope_season_val]
        bw_df = bw_df[bw_df["season"] == scope_season_val]
        
    p_season_rows = df_mart[df_mart["player_name"] == sel_dossier_player]
    
    # Accurate Season-Specific Franchise Determination
    if is_season_scope:
        season_match = p_season_rows[p_season_rows["season"] == selected_season]
        if len(season_match) > 0:
            p_meta = season_match.iloc[0]
            franchise_name = p_meta["franchise"]
        else:
            # Fallback to match history for that specific season if not in mart
            b_s = b_df[b_df["season"] == selected_season]
            bw_s = bw_df[bw_df["season"] == selected_season]
            if len(b_s) > 0 and b_s.iloc[0]["match_team"] != "Other / Unassigned":
                franchise_name = b_s.iloc[0]["match_team"]
            elif len(bw_s) > 0 and bw_s.iloc[0]["match_team"] != "Other / Unassigned":
                franchise_name = bw_s.iloc[0]["match_team"]
            else:
                franchise_name = latest_franchise
            p_meta = p_season_rows.iloc[0] if len(p_season_rows) > 0 else None
    else:
        # Full Career Scope: use latest/current franchise
        franchise_name = latest_franchise
        p_meta = p_season_rows.iloc[0] if len(p_season_rows) > 0 else None

    if p_meta is not None:
        sold_price = p_meta["sold_price_inr_cr"]
        val_class = p_meta["value_buy_category"]
        val_score = p_meta["performance_to_salary_value_score"]
        death_sr_val = p_meta["death_strike_rate"]
        pp_sr_val = p_meta["pp_strike_rate"]
        death_econ_val = p_meta["death_economy_rate"]
        death_dot_val = p_meta["death_dot_pct"]
    else:
        sold_price = 0.50
        val_class = "Squad Value"
        val_score = 30.0
        death_sr_val = 0.0
        pp_sr_val = 0.0
        death_econ_val = 0.0
        death_dot_val = 0.0

    f_info = FRANCHISE_META.get(franchise_name, FRANCHISE_META["Other / Unassigned"])
    f_rgb = f_info.get("color_rgb", "56, 189, 248")
    hex_color = f_info["color"].replace("#", "")
    text_color = f_info["text"].replace("#", "")
    avatar_url = get_display_avatar(sel_dossier_player, franchise_name)
    badge_style = "badge-steal" if val_class == "Steal Buy" else ("badge-risk" if val_class == "Overpriced Risk" else "badge-fair")

    p_innings_batted = len(b_df)
    p_runs = int(b_df["runs"].sum()) if p_innings_batted > 0 else 0
    p_balls = int(b_df["balls"].sum()) if p_innings_batted > 0 else 0
    p_fours = int(b_df["fours"].sum()) if p_innings_batted > 0 else 0
    p_sixes = int(b_df["sixes"].sum()) if p_innings_batted > 0 else 0
    p_outs = int(b_df["is_out"].sum()) if p_innings_batted > 0 else 0
    p_hs = int(b_df["runs"].max()) if p_innings_batted > 0 else 0
    p_centuries = int((b_df["runs"] >= 100).sum()) if p_innings_batted > 0 else 0
    p_fifties = int(((b_df["runs"] >= 50) & (b_df["runs"] < 100)).sum()) if p_innings_batted > 0 else 0
    p_sr = (p_runs / p_balls * 100) if p_balls > 0 else 0.0
    p_avg = (p_runs / p_outs) if p_outs > 0 else float(p_runs)
    
    p_innings_bowled = len(bw_df)
    p_b_balls = int(bw_df["balls"].sum()) if p_innings_bowled > 0 else 0
    p_rc = int(bw_df["runs_conceded"].sum()) if p_innings_bowled > 0 else 0
    p_wkts = int(bw_df["wickets"].sum()) if p_innings_bowled > 0 else 0
    p_dots = int(bw_df["dots"].sum()) if p_innings_bowled > 0 else 0
    p_overs = f"{p_b_balls // 6}.{p_b_balls % 6}"
    p_econ = (p_rc / (p_b_balls / 6.0)) if p_b_balls > 0 else 0.0
    p_b_avg = (p_rc / p_wkts) if p_wkts > 0 else 0.0
    p_b_sr = (p_b_balls / p_wkts) if p_wkts > 0 else 0.0
    
    if p_innings_bowled > 0:
        best_row = bw_df.sort_values(by=["wickets", "runs_conceded"], ascending=[False, True]).iloc[0]
        p_bbi = f"{int(best_row['wickets'])}/{int(best_row['runs_conceded'])}"
        p_4w = int((bw_df["wickets"] >= 4).sum())
    else:
        p_bbi = "N/A"
        p_4w = 0

    total_match_ids = set(b_df["match_id"].tolist() + bw_df["match_id"].tolist())
    p_total_matches = len(total_match_ids)

    # Subtitle with timeline details
    if is_season_scope:
        timeline_html = (
            f'<div style="margin-top: 5px; font-size: 0.85rem; color: #38BDF8;">'
            f'📅 <b>{selected_season} Franchise:</b> <span style="color: #F8FAFC; font-weight: 700;">{franchise_name}</span> &nbsp;|&nbsp; '
            f'🔄 <b>Current Team:</b> <span style="color: #FACC15; font-weight: 700;">{latest_franchise}</span>'
            f'</div>'
        )
    else:
        timeline_html = (
            f'<div style="margin-top: 5px; font-size: 0.85rem; color: #38BDF8;">'
            f'🏆 <b>Career Franchise Journey:</b> <span style="color: #F8FAFC; font-weight: 700;">{career_journey}</span>'
            f'</div>'
        )

    # Hero Banner Card with Player Portrait, Watermark Logo Background & Team Crest Halo
    hero_card_html = (
        f'<div style="position: relative; overflow: hidden; background: radial-gradient(circle at 88% 50%, rgba({f_rgb}, 0.16) 0%, rgba(15, 23, 42, 0.95) 75%), url(\'{f_info["logo"]}\') no-repeat right 35px center / 220px auto; background-blend-mode: overlay; border: 1px solid rgba(255,255,255,0.1); border-left: 6px solid {f_info["color"]}; border-radius: 18px; padding: 24px; margin-bottom: 24px; box-shadow: 0 12px 35px rgba(0,0,0,0.55);">'
        f'<img src="{f_info["logo"]}" style="position: absolute; right: 25px; top: 50%; transform: translateY(-50%); width: 220px; height: 220px; object-fit: contain; opacity: 0.13; filter: blur(0.5px); pointer-events: none; z-index: 1;" />'
        f'<div style="position: relative; z-index: 2; display: flex; align-items: center; gap: 24px; flex-wrap: wrap;">'
        f'<div style="position: relative; width: 135px; height: 135px; border-radius: 50%; display: flex; align-items: center; justify-content: center; background: radial-gradient(circle, rgba({f_rgb}, 0.25) 0%, rgba(15,23,42,0.95) 75%); border: 3px solid {f_info["color"]}; box-shadow: 0 0 25px rgba({f_rgb}, 0.45); flex-shrink: 0;">'
        f'<img src="{f_info["logo"]}" style="position: absolute; width: 85%; height: 85%; object-fit: contain; opacity: 0.35; filter: drop-shadow(0 0 8px {f_info["color"]}); pointer-events: none; z-index: 1;" />'
        f'<img src="{avatar_url}" style="position: relative; z-index: 2; width: 115px; height: 115px; border-radius: 50%; object-fit: cover;" onerror="this.onerror=null; this.src=\'https://ui-avatars.com/api/?name={urllib.parse.quote(sel_dossier_player)}&background={hex_color}&color={text_color}&size=256&bold=true\';"/>'
        f'<div style="position: absolute; bottom: -2px; right: -2px; z-index: 3; width: 42px; height: 42px; border-radius: 50%; background: #0F172A; border: 2.5px solid {f_info["color"]}; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(0,0,0,0.7);" title="{franchise_name}">'
        f'<img src="{f_info["logo"]}" style="width: 28px; height: 28px; object-fit: contain;" alt="{franchise_name}"/>'
        f'</div>'
        f'</div>'
        f'<div style="flex: 1; min-width: 260px;">'
        f'<div style="display: flex; gap: 12px; align-items: center; flex-wrap: wrap;">'
        f'<h2 style="margin: 0; font-size: 2.05rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.02em;">{sel_dossier_player}</h2>'
        f'<span class="val-badge {badge_style}">{val_class}</span>'
        f'</div>'
        f'<div style="margin-top: 6px; font-size: 1.05rem; color: #CBD5E1;">'
        f'<span style="font-weight: 800; color: {f_info["color"]}; font-size: 1.1rem;">{f_info["badge"]} {franchise_name}</span> &nbsp;•&nbsp; '
        f'<span>{player_role}</span> &nbsp;•&nbsp; '
        f'<span>{"🇮🇳 Capped Indian" if is_capped else ("🌏 Overseas Player" if is_overseas else "Uncapped Talent")}</span>'
        f'</div>'
        f'{timeline_html}'
        f'<div style="margin-top: 10px; font-size: 0.92rem; color: #94A3B8;">'
        f'💰 <b>Auction Contract:</b> <span style="color: #F8FAFC; font-weight: 700;">₹{sold_price:.2f} Cr</span> | '
        f'⚡ <b>Value Score:</b> <span style="color: #38BDF8; font-weight: 700;">{val_score:.1f} pts</span> | '
        f'🎯 <b>Scope:</b> <span style="color: #34D399; font-weight: 600;">{dossier_scope}</span>'
        f'</div>'
        f'</div>'
        f'<div style="text-align: right; padding-right: 15px; position: relative; z-index: 2;">'
        f'<img src="{f_info["logo"]}" style="width: 80px; height: 80px; object-fit: contain; filter: drop-shadow(0 6px 14px rgba(0,0,0,0.6));" alt="{franchise_name}"/>'
        f'<div style="font-size: 0.75rem; font-weight: 800; color: {f_info["color"]}; margin-top: 4px; letter-spacing: 0.5px;">{f_info["short"]} OFFICIAL</div>'
        f'</div>'
        f'</div>'
        f'</div>'
    )
    st.markdown(hero_card_html, unsafe_allow_html=True)

    # Batting Milestones Section
    st.markdown("#### 🏏 Career & Season Batting Milestones")
    mb1, mb2, mb3, mb4, mb5, mb6 = st.columns(6)
    with mb1:
        st.markdown(f"""<div class="dossier-metric-box"><div class="dossier-metric-lbl">Matches / Inns</div><div class="dossier-metric-val">{p_total_matches} / {p_innings_batted}</div><div class="dossier-metric-sub">Matches & Innings</div></div>""", unsafe_allow_html=True)
    with mb2:
        st.markdown(f"""<div class="dossier-metric-box"><div class="dossier-metric-lbl">Total Runs</div><div class="dossier-metric-val" style="color: #38BDF8;">{p_runs}</div><div class="dossier-metric-sub">Total Career Runs</div></div>""", unsafe_allow_html=True)
    with mb3:
        st.markdown(f"""<div class="dossier-metric-box"><div class="dossier-metric-lbl">Highest Score</div><div class="dossier-metric-val">{p_hs}</div><div class="dossier-metric-sub">Highest Score (HS)</div></div>""", unsafe_allow_html=True)
    with mb4:
        st.markdown(f"""<div class="dossier-metric-box"><div class="dossier-metric-lbl">Centuries (100s)</div><div class="dossier-metric-val" style="color: #F59E0B;">{p_centuries}</div><div class="dossier-metric-sub">Centuries (100s)</div></div>""", unsafe_allow_html=True)
    with mb5:
        st.markdown(f"""<div class="dossier-metric-box"><div class="dossier-metric-lbl">Fifties (50s)</div><div class="dossier-metric-val" style="color: #60A5FA;">{p_fifties}</div><div class="dossier-metric-sub">Half-Centuries (50s)</div></div>""", unsafe_allow_html=True)
    with mb6:
        st.markdown(f"""<div class="dossier-metric-box"><div class="dossier-metric-lbl">Boundaries (4s / 6s)</div><div class="dossier-metric-val">{p_fours} / {p_sixes}</div><div class="dossier-metric-sub">Boundaries (4s / 6s)</div></div>""", unsafe_allow_html=True)

    col_sub_b1, col_sub_b2 = st.columns(2)
    with col_sub_b1:
        st.markdown(f"""
        <div style="background: rgba(15, 23, 42, 0.5); padding: 10px 16px; border-radius: 10px; margin-top: 8px; border: 1px solid rgba(255,255,255,0.05); font-size: 0.88rem;">
            ⚡ <b>Strike Rate:</b> <span style="color: #38BDF8; font-weight: 700;">{p_sr:.2f}</span> &nbsp;|&nbsp; 
            🎯 <b>Batting Average:</b> <span style="color: #F8FAFC; font-weight: 700;">{p_avg:.2f}</span> &nbsp;|&nbsp; 
            🔴 <b>Dismissals:</b> {p_outs} &nbsp;|&nbsp; 
            ⚪ <b>Balls Faced:</b> {p_balls}
        </div>
        """, unsafe_allow_html=True)
    with col_sub_b2:
        cost_run_player = (sold_price * 10000000) / p_runs if p_runs > 0 else 0
        fmt_c_run = f"₹{cost_run_player/100000:.2f} Lakh" if cost_run_player >= 100000 else f"₹{cost_run_player:,.0f}"
        st.markdown(f"""
        <div style="background: rgba(15, 23, 42, 0.5); padding: 10px 16px; border-radius: 10px; margin-top: 8px; border: 1px solid rgba(255,255,255,0.05); font-size: 0.88rem;">
            💵 <b>Cost Per Run:</b> <span style="color: #34D399; font-weight: 700;">{fmt_c_run}</span> &nbsp;|&nbsp; 
            💥 <b>Death Overs SR:</b> <span style="color: #F59E0B; font-weight: 700;">{death_sr_val:.1f}</span> &nbsp;|&nbsp; 
            ⚡ <b>Powerplay SR:</b> {pp_sr_val:.1f}
        </div>
        """, unsafe_allow_html=True)

    # Bowling Milestones Section
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 🎯 Career & Season Bowling Milestones")
    mw1, mw2, mw3, mw4, mw5, mw6 = st.columns(6)
    with mw1:
        st.markdown(f"""<div class="dossier-metric-box"><div class="dossier-metric-lbl">Innings / Overs</div><div class="dossier-metric-val">{p_innings_bowled} / {p_overs}</div><div class="dossier-metric-sub">Innings / Overs Bowled</div></div>""", unsafe_allow_html=True)
    with mw2:
        st.markdown(f"""<div class="dossier-metric-box"><div class="dossier-metric-lbl">Wickets</div><div class="dossier-metric-val" style="color: #34D399;">{p_wkts}</div><div class="dossier-metric-sub">Total Wickets Taken</div></div>""", unsafe_allow_html=True)
    with mw3:
        st.markdown(f"""<div class="dossier-metric-box"><div class="dossier-metric-lbl">Best Bowling (BBI)</div><div class="dossier-metric-val" style="color: #F59E0B;">{p_bbi}</div><div class="dossier-metric-sub">Best Bowling Figures</div></div>""", unsafe_allow_html=True)
    with mw4:
        st.markdown(f"""<div class="dossier-metric-box"><div class="dossier-metric-lbl">4W+ Hauls</div><div class="dossier-metric-val">{p_4w}</div><div class="dossier-metric-sub">4+ Wicket Hauls</div></div>""", unsafe_allow_html=True)
    with mw5:
        st.markdown(f"""<div class="dossier-metric-box"><div class="dossier-metric-lbl">Dot Balls</div><div class="dossier-metric-val" style="color: #38BDF8;">{p_dots}</div><div class="dossier-metric-sub">Dot Deliveries</div></div>""", unsafe_allow_html=True)
    with mw6:
        st.markdown(f"""<div class="dossier-metric-box"><div class="dossier-metric-lbl">Economy Rate</div><div class="dossier-metric-val">{p_econ:.2f}</div><div class="dossier-metric-sub">Economy Rate (RPO)</div></div>""", unsafe_allow_html=True)

    col_sub_w1, col_sub_w2 = st.columns(2)
    with col_sub_w1:
        st.markdown(f"""
        <div style="background: rgba(15, 23, 42, 0.5); padding: 10px 16px; border-radius: 10px; margin-top: 8px; border: 1px solid rgba(255,255,255,0.05); font-size: 0.88rem;">
            ⚡ <b>Bowling Strike Rate:</b> <span style="color: #38BDF8; font-weight: 700;">{p_b_sr:.1f} balls/wkt</span> &nbsp;|&nbsp; 
            🎯 <b>Bowling Average:</b> <span style="color: #F8FAFC; font-weight: 700;">{p_b_avg:.2f}</span> &nbsp;|&nbsp; 
            🔴 <b>Runs Conceded:</b> {p_rc} &nbsp;|&nbsp; 
            ⚪ <b>Legal Balls:</b> {p_b_balls}
        </div>
        """, unsafe_allow_html=True)
    with col_sub_w2:
        cost_wkt_player = (sold_price * 10000000) / p_wkts if p_wkts > 0 else 0
        fmt_c_wkt = f"₹{cost_wkt_player/100000:.1f} Lakh" if cost_wkt_player >= 100000 else (f"₹{cost_wkt_player:,.0f}" if p_wkts > 0 else "N/A")
        st.markdown(f"""
        <div style="background: rgba(15, 23, 42, 0.5); padding: 10px 16px; border-radius: 10px; margin-top: 8px; border: 1px solid rgba(255,255,255,0.05); font-size: 0.88rem;">
            💵 <b>Cost Per Wicket:</b> <span style="color: #34D399; font-weight: 700;">{fmt_c_wkt}</span> &nbsp;|&nbsp; 
            🛡️ <b>Death Overs Econ:</b> <span style="color: #F59E0B; font-weight: 700;">{death_econ_val:.2f}</span> &nbsp;|&nbsp; 
            ⚡ <b>Death Dot %:</b> {death_dot_val:.1f}%
        </div>
        """, unsafe_allow_html=True)

    # Match-by-Match Game Log Section
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander(f"📋 View Match-by-Match Detailed Game Log for {sel_dossier_player} ({len(b_df)} Batting / {len(bw_df)} Bowling Records)"):
        tab_log_bat, tab_log_bowl = st.tabs(["🏏 Batting Game Log", "🎯 Bowling Game Log"])
        with tab_log_bat:
            if len(b_df) > 0:
                display_b = b_df[["match_date", "season", "match_team", "opponent_team", "venue", "runs", "balls", "fours", "sixes", "dismissal_kind"]].copy()
                display_b.rename(columns={
                    "match_date": "Date", "season": "Season", "match_team": "Player Team", "opponent_team": "Opponent",
                    "venue": "Venue", "runs": "Runs Scored", "balls": "Balls", "fours": "4s", "sixes": "6s",
                    "dismissal_kind": "Dismissal"
                }, inplace=True)
                display_b["Strike Rate"] = (display_b["Runs Scored"] / display_b["Balls"].replace(0, 1) * 100).round(1)
                st.dataframe(display_b, use_container_width=True)
            else:
                st.info("No batting innings recorded for this player in selected scope.")
                
        with tab_log_bowl:
            if len(bw_df) > 0:
                display_bw = bw_df[["match_date", "season", "match_team", "opponent_team", "venue", "balls", "runs_conceded", "wickets", "dots"]].copy()
                display_bw["Overs"] = display_bw["balls"].apply(lambda b: f"{b // 6}.{b % 6}")
                display_bw["Economy"] = (display_bw["runs_conceded"] / (display_bw["balls"] / 6.0).replace(0, 1)).round(2)
                display_bw.rename(columns={
                    "match_date": "Date", "season": "Season", "match_team": "Player Team", "opponent_team": "Opponent",
                    "venue": "Venue", "runs_conceded": "Runs Given", "wickets": "Wickets Taken", "dots": "Dot Balls"
                }, inplace=True)
                cols_order = ["Date", "Season", "Player Team", "Opponent", "Venue", "Overs", "Runs Given", "Wickets Taken", "Economy", "Dot Balls"]
                st.dataframe(display_bw[cols_order], use_container_width=True)
            else:
                st.info("No bowling innings recorded for this player in selected scope.")

# =============================================================================
# TAB 1: FRANCHISE STANDINGS & TEAM HUB
# =============================================================================
with tab_teams:
    st.markdown("### 🏆 Franchise Team Analytics, Standings & Official Logos")
    st.caption("Official crests, standings, win rates, purse spend, and squad rosters for all 10 IPL franchises:")

    # Team Overview Cards Grid
    st.markdown("#### 🏟️ All 10 IPL Franchises At a Glance")
    
    team_names_order = [
        "Chennai Super Kings", "Mumbai Indians", "Royal Challengers Bengaluru",
        "Kolkata Knight Riders", "Sunrisers Hyderabad", "Rajasthan Royals",
        "Gujarat Titans", "Lucknow Super Giants", "Delhi Capitals", "Punjab Kings"
    ]
    
    t_cols = st.columns(5)
    for idx, t_name in enumerate(team_names_order):
        meta = FRANCHISE_META[t_name]
        c_stats = df_team_career[df_team_career["team"] == t_name]
        matches = int(c_stats["matches_played"].values[0]) if len(c_stats) > 0 else 0
        wins = int(c_stats["wins"].values[0]) if len(c_stats) > 0 else 0
        win_pct = float(c_stats["win_pct"].values[0]) if len(c_stats) > 0 else 0.0
        
        with t_cols[idx % 5]:
            st.markdown(f"""
            <div style="background: linear-gradient(145deg, #1E293B 0%, #0F172A 100%); border: 1px solid rgba(255,255,255,0.08); border-top: 4px solid {meta['color']}; border-radius: 14px; padding: 12px; text-align: center; margin-bottom: 14px;">
                <img src="{meta['logo']}" style="width: 55px; height: 55px; object-fit: contain; margin-bottom: 6px;"/>
                <div style="font-size: 0.88rem; font-weight: 800; color: #FFFFFF;">{meta['short']}</div>
                <div style="font-size: 0.72rem; color: #94A3B8;">{matches} Matches</div>
                <div style="margin-top: 6px;">
                    <span class="val-badge" style="background: rgba(56, 189, 248, 0.15); color: #38BDF8; border: 1px solid #38BDF8; font-size: 0.68rem;">{wins} Wins ({win_pct}%)</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
    st.markdown("<hr style='border-color: rgba(255,255,255,0.08);'>", unsafe_allow_html=True)
    
    # Deep-Dive Team Inspector
    st.markdown("#### 🔍 Deep-Dive Franchise Analytics & Squad Inspector")
    sel_inspect_team = st.selectbox(
        "Select Franchise to Inspect:",
        team_names_order,
        index=0,
        key="franchise_hub_selector"
    )
    
    sel_meta = FRANCHISE_META[sel_inspect_team]
    sel_c_stats = df_team_career[df_team_career["team"] == sel_inspect_team]
    t_matches = int(sel_c_stats["matches_played"].values[0]) if len(sel_c_stats) > 0 else 0
    t_wins = int(sel_c_stats["wins"].values[0]) if len(sel_c_stats) > 0 else 0
    t_losses = int(sel_c_stats["losses"].values[0]) if len(sel_c_stats) > 0 else 0
    t_win_pct = float(sel_c_stats["win_pct"].values[0]) if len(sel_c_stats) > 0 else 0.0
    
    # Team Batting & Bowling totals
    team_bat_df = df_bat_history[df_bat_history["primary_franchise"] == sel_inspect_team]
    t_runs = int(team_bat_df["runs"].sum())
    t_4s = int(team_bat_df["fours"].sum())
    t_6s = int(team_bat_df["sixes"].sum())
    
    team_bowl_df = df_bowl_history[df_bowl_history["primary_franchise"] == sel_inspect_team]
    t_wkts = int(team_bowl_df["wickets"].sum())
    t_dots = int(team_bowl_df["dots"].sum())
    
    # Top Run Scorer for Franchise
    if len(team_bat_df) > 0:
        top_scorer_row = team_bat_df.groupby("canonical_name")["runs"].sum().sort_values(ascending=False).head(1)
        top_scorer_name = top_scorer_row.index[0]
        top_scorer_runs = top_scorer_row.values[0]
    else:
        top_scorer_name = "N/A"
        top_scorer_runs = 0
        
    # Top Wicket Taker for Franchise
    if len(team_bowl_df) > 0:
        top_bowler_row = team_bowl_df.groupby("canonical_name")["wickets"].sum().sort_values(ascending=False).head(1)
        top_bowler_name = top_bowler_row.index[0]
        top_bowler_wkts = top_bowler_row.values[0]
    else:
        top_bowler_name = "N/A"
        top_bowler_wkts = 0

    # Team Banner with Official Logo
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%); border: 1px solid rgba(255,255,255,0.1); border-left: 6px solid {sel_meta['color']}; border-radius: 16px; padding: 22px; margin-bottom: 20px;">
        <div style="display: flex; align-items: center; gap: 24px; flex-wrap: wrap;">
            <img src="{sel_meta['logo']}" style="width: 90px; height: 90px; object-fit: contain; filter: drop-shadow(0 4px 12px rgba(0,0,0,0.4));"/>
            <div style="flex: 1;">
                <h2 style="margin: 0; font-size: 1.85rem; font-weight: 800; color: #FFFFFF;">{sel_meta['badge']} {sel_inspect_team} ({sel_meta['short']})</h2>
                <div style="margin-top: 6px; font-size: 0.92rem; color: #94A3B8;">
                    🏆 <b>Career IPL Record (2022-2026):</b> <span style="color: #38BDF8; font-weight: 700;">{t_matches} Matches</span> | 
                    <span style="color: #34D399; font-weight: 700;">{t_wins} Wins</span> | 
                    <span style="color: #F87171; font-weight: 700;">{t_losses} Losses</span> | 
                    Win Rate: <span style="color: #F59E0B; font-weight: 700;">{t_win_pct}%</span>
                </div>
                <div style="margin-top: 6px; font-size: 0.88rem; color: #94A3B8;">
                    👑 <b>Top Run Scorer:</b> <span style="color: #F8FAFC; font-weight: 700;">{top_scorer_name} ({top_scorer_runs} runs)</span> &nbsp;|&nbsp; 
                    🎯 <b>Top Wicket Taker:</b> <span style="color: #F8FAFC; font-weight: 700;">{top_bowler_name} ({top_bowler_wkts} wkts)</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 4 KPI Tiles
    fk1, fk2, fk3, fk4 = st.columns(4)
    with fk1:
        st.markdown(f"""
        <div class="kpi-tile">
            <div class="kpi-label">Matches & Win Rate</div>
            <div class="kpi-val">{t_win_pct}%</div>
            <div class="kpi-sub">{t_wins} Won / {t_losses} Lost ({t_matches} Matches)</div>
        </div>
        """, unsafe_allow_html=True)
    with fk2:
        st.markdown(f"""
        <div class="kpi-tile">
            <div class="kpi-label">Franchise Runs Scored</div>
            <div class="kpi-val" style="color: #38BDF8;">{t_runs:,}</div>
            <div class="kpi-sub">Total 4s: {t_4s} | Total 6s: {t_6s}</div>
        </div>
        """, unsafe_allow_html=True)
    with fk3:
        st.markdown(f"""
        <div class="kpi-tile">
            <div class="kpi-label">Franchise Wickets Taken</div>
            <div class="kpi-val" style="color: #34D399;">{t_wkts} Wkts</div>
            <div class="kpi-sub">Total Dot Deliveries: {t_dots:,}</div>
        </div>
        """, unsafe_allow_html=True)
    with fk4:
        f_mart = df_mart[(df_mart["franchise"] == sel_inspect_team) & (df_mart["season"] == selected_season)]
        f_spend = f_mart["sold_price_inr_cr"].sum() if len(f_mart) > 0 else 0
        st.markdown(f"""
        <div class="kpi-tile">
            <div class="kpi-label">{selected_season} Squad Spend</div>
            <div class="kpi-val" style="color: #F59E0B;">₹{f_spend:.1f} Cr</div>
            <div class="kpi-sub">Tracked Star Players: {len(f_mart)}</div>
        </div>
        """, unsafe_allow_html=True)



# =============================================================================
# TAB 2: EXECUTIVE VALUATION MATRIX
# =============================================================================
with tab_matrix:
    st.markdown("### 4-Quadrant Valuation Matrix: Finishing Power vs. Hammer Price")
    st.caption("💡 **Valuation Guide:** Top-Left (Green) = **Steal Buys** (High finishing power at bargain auction price). Bottom-Right (Red) = **Overpriced Risk** (High salary with subdued output).")
    
    color_map = {
        "Steal Buy": "#10B981",
        "Elite Core": "#3B82F6",
        "Overpriced Risk": "#EF4444",
        "Scouting Target": "#F59E0B",
        "Squad Value": "#64748B"
    }
    
    fig_matrix = px.scatter(
        filtered_df,
        x="sold_price_inr_cr",
        y="death_strike_rate",
        size=filtered_df["total_runs"].apply(lambda r: max(r, 20)),
        color="value_buy_category",
        color_discrete_map=color_map,
        hover_name="player_name",
        hover_data={
            "franchise": True,
            "sold_price_inr_cr": ":.2f",
            "death_strike_rate": ":.1f",
            "total_runs": True,
            "total_wickets": True,
            "performance_to_salary_value_score": ":.1f"
        },
        labels={
            "sold_price_inr_cr": "Auction Hammer Price (₹ Crores)",
            "death_strike_rate": "Finishing Power (Death Overs Strike Rate)",
            "value_buy_category": "Valuation Segment"
        },
        template="plotly_dark",
        height=520
    )
    
    fig_matrix.add_hline(y=165.0, line_dash="dash", line_color="#94A3B8", annotation_text="Benchmark Finishing SR (165.0)", annotation_position="bottom right")
    fig_matrix.add_vline(x=5.0, line_dash="dash", line_color="#94A3B8", annotation_text="Bargain Ceiling (₹5.0 Cr)", annotation_position="top left")
    
    fig_matrix.update_layout(
        plot_bgcolor="#0B0F19",
        paper_bgcolor="#0B0F19",
        font=dict(family="Plus Jakarta Sans", color="#F8FAFC"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_matrix, use_container_width=True)
    
    # Top Steal Buys Cards
    st.markdown("### 🏆 Top Undervalued Targets (Ranked by Value Score)")
    top_steals = steal_buys_df.sort_values(by="performance_to_salary_value_score", ascending=False).head(5)
    
    if len(top_steals) == 0:
        top_steals = filtered_df.sort_values(by="performance_to_salary_value_score", ascending=False).head(5)
        
    card_cols = st.columns(min(len(top_steals), 5))
    for idx, (_, p) in enumerate(top_steals.iterrows()):
        f_meta = FRANCHISE_META.get(p['franchise'], FRANCHISE_META["Other / Unassigned"])
        f_rgb = f_meta.get("color_rgb", "56, 189, 248")
        hex_c = f_meta["color"].replace("#", "")
        text_c = f_meta["text"].replace("#", "")
        avatar_img = get_display_avatar(p['player_name'], p['franchise'])
        with card_cols[idx]:
            spotlight_card_html = (
                f'<div class="fut-card" style="position: relative; overflow: hidden; background: radial-gradient(circle at 50% 30%, rgba({f_rgb}, 0.16) 0%, rgba(15, 23, 42, 0.98) 75%), url(\'{f_meta["logo"]}\') no-repeat center 30% / 125px auto; background-blend-mode: overlay;">'
                f'<div class="fut-card-header-stripe" style="background: {f_meta["color"]};"></div>'
                f'<div style="position: relative; width: 106px; height: 106px; margin: 12px auto 8px auto; border-radius: 50%; display: flex; align-items: center; justify-content: center; background: radial-gradient(circle, rgba({f_rgb}, 0.22) 0%, rgba(15,23,42,0.95) 75%); border: 2.5px solid {f_meta["color"]}; box-shadow: 0 0 16px rgba({f_rgb}, 0.35);">'
                f'<img src="{f_meta["logo"]}" style="position: absolute; width: 75%; height: 75%; object-fit: contain; opacity: 0.32; pointer-events: none; z-index: 1;" />'
                f'<img src="{avatar_img}" style="position: relative; z-index: 2; width: 90px; height: 90px; border-radius: 50%; object-fit: cover;" onerror="this.onerror=null; this.src=\'https://ui-avatars.com/api/?name={urllib.parse.quote(p["player_name"])}&background={hex_c}&color={text_c}&size=256&bold=true\';"/>'
                f'<div style="position: absolute; bottom: -2px; right: -2px; z-index: 3; width: 34px; height: 34px; border-radius: 50%; background: #0F172A; border: 2px solid {f_meta["color"]}; display: flex; align-items: center; justify-content: center; box-shadow: 0 3px 8px rgba(0,0,0,0.6);" title="{p["franchise"]}">'
                f'<img src="{f_meta["logo"]}" style="width: 22px; height: 22px; object-fit: contain;"/>'
                f'</div>'
                f'</div>'
                f'<div class="card-player-name">{p["player_name"]}</div>'
                f'<div class="card-team-name">{f_meta["badge"]} {p["franchise"]}</div>'
                f'<span class="val-badge badge-steal">{p["value_buy_category"]}</span>'
                f'<div class="stat-pill-grid">'
                f'<div class="stat-item">💰 Price:<br><span class="stat-val">₹{p["sold_price_inr_cr"]:.2f}Cr</span></div>'
                f'<div class="stat-item">💥 Death SR:<br><span class="stat-val">{p["death_strike_rate"]:.1f}</span></div>'
                f'<div class="stat-item">🏏 Runs:<br><span class="stat-val">{int(p["total_runs"])}</span></div>'
                f'<div class="stat-item">🎯 Wkts:<br><span class="stat-val">{int(p["total_wickets"])}</span></div>'
                f'</div>'
                f'</div>'
            )
            st.markdown(spotlight_card_html, unsafe_allow_html=True)

# =============================================================================
# TAB 2: HEAD-TO-HEAD SCOUT RADAR
# =============================================================================
with tab_radar:
    st.markdown("### 🎯 Head-to-Head Player Comparison & Radar Analysis")
    st.caption("Head-to-head scouting radar comparison across attack, finishing, boundary volume, dot ball control, and contract valuation.")
    
    player_pool = sorted(list(filtered_df["player_name"].unique()))
    if len(player_pool) < 2:
        player_pool = sorted(list(df_mart[df_mart["season"] == selected_season]["player_name"].unique()))
        
    c1, c2 = st.columns(2)
    with c1:
        def_p1 = "Ayush Badoni" if "Ayush Badoni" in player_pool else player_pool[0]
        sel_1 = st.selectbox("Select Player 1 (Target Shortlist):", player_pool, index=player_pool.index(def_p1))
    with c2:
        def_p2 = "Heinrich Klaasen" if "Heinrich Klaasen" in player_pool else (player_pool[1] if len(player_pool) > 1 else player_pool[0])
        sel_2 = st.selectbox("Select Player 2 (Benchmark Core):", player_pool, index=player_pool.index(def_p2))
        
    p1_d = df_mart[(df_mart["player_name"] == sel_1) & (df_mart["season"] == selected_season)].iloc[0]
    p2_d = df_mart[(df_mart["player_name"] == sel_2) & (df_mart["season"] == selected_season)].iloc[0]
    
    f1 = FRANCHISE_META.get(p1_d['franchise'], FRANCHISE_META["Other / Unassigned"])
    f2 = FRANCHISE_META.get(p2_d['franchise'], FRANCHISE_META["Other / Unassigned"])
    f1_rgb = f1.get("color_rgb", "56, 189, 248")
    f2_rgb = f2.get("color_rgb", "56, 189, 248")
    hex1 = f1["color"].replace("#", "")
    text1 = f1["text"].replace("#", "")
    hex2 = f2["color"].replace("#", "")
    text2 = f2["text"].replace("#", "")
    
    col_l, col_m, col_r = st.columns([1, 1.8, 1])
    
    with col_l:
        card_l_html = (
            f'<div class="fut-card" style="position: relative; overflow: hidden; background: radial-gradient(circle at 50% 30%, rgba({f1_rgb}, 0.16) 0%, rgba(15, 23, 42, 0.98) 75%), url(\'{f1["logo"]}\') no-repeat center 30% / 125px auto; background-blend-mode: overlay;">'
            f'<div class="fut-card-header-stripe" style="background: {f1["color"]};"></div>'
            f'<div style="position: relative; width: 106px; height: 106px; margin: 12px auto 8px auto; border-radius: 50%; display: flex; align-items: center; justify-content: center; background: radial-gradient(circle, rgba({f1_rgb}, 0.22) 0%, rgba(15,23,42,0.95) 75%); border: 2.5px solid {f1["color"]}; box-shadow: 0 0 16px rgba({f1_rgb}, 0.35);">'
            f'<img src="{f1["logo"]}" style="position: absolute; width: 75%; height: 75%; object-fit: contain; opacity: 0.32; pointer-events: none; z-index: 1;" />'
            f'<img src="{get_display_avatar(sel_1, p1_d["franchise"])}" style="position: relative; z-index: 2; width: 90px; height: 90px; border-radius: 50%; object-fit: cover;" onerror="this.onerror=null; this.src=\'https://ui-avatars.com/api/?name={urllib.parse.quote(sel_1)}&background={hex1}&color={text1}&size=256&bold=true\';"/>'
            f'<div style="position: absolute; bottom: -2px; right: -2px; z-index: 3; width: 34px; height: 34px; border-radius: 50%; background: #0F172A; border: 2px solid {f1["color"]}; display: flex; align-items: center; justify-content: center; box-shadow: 0 3px 8px rgba(0,0,0,0.6);" title="{p1_d["franchise"]}">'
            f'<img src="{f1["logo"]}" style="width: 22px; height: 22px; object-fit: contain;"/>'
            f'</div>'
            f'</div>'
            f'<div class="card-player-name">{sel_1}</div>'
            f'<div class="card-team-name">{f1["badge"]} {p1_d["franchise"]} • {p1_d["player_role"]}</div>'
            f'<span class="val-badge badge-steal">{p1_d["value_buy_category"]}</span>'
            f'<div class="stat-pill-grid" style="margin-top: 14px;">'
            f'<div class="stat-item">💰 Price:<br><span class="stat-val">₹{p1_d["sold_price_inr_cr"]:.2f} Cr</span></div>'
            f'<div class="stat-item">💥 Death SR:<br><span class="stat-val">{p1_d["death_strike_rate"]:.1f}</span></div>'
            f'<div class="stat-item">⚡ PP SR:<br><span class="stat-val">{p1_d["pp_strike_rate"]:.1f}</span></div>'
            f'<div class="stat-item">🏏 Runs:<br><span class="stat-val">{int(p1_d["total_runs"])}</span></div>'
            f'</div>'
            f'</div>'
        )
        st.markdown(card_l_html, unsafe_allow_html=True)
        
    with col_m:
        cats = ['Powerplay Attack', 'Finishing (Death SR)', 'Boundary Volume', 'Dot Ball Control', 'Value for Money']
        def calc_norm(r):
            pp = min(r['pp_strike_rate'] / 2.0, 100)
            death = min(r['death_strike_rate'] / 2.4, 100)
            runs = min(r['total_runs'] / 4.5, 100)
            dot = max(100 - r['batting_dot_pct'] * 1.5, 10)
            val = min(r['performance_to_salary_value_score'] / 10.0, 100)
            return [pp, death, runs, dot, val]
            
        fig_r = go.Figure()
        fig_r.add_trace(go.Scatterpolar(
            r=calc_norm(p1_d), theta=cats, fill='toself',
            name=f"{sel_1} (₹{p1_d['sold_price_inr_cr']} Cr)",
            line_color=f1['color']
        ))
        fig_r.add_trace(go.Scatterpolar(
            r=calc_norm(p2_d), theta=cats, fill='toself',
            name=f"{sel_2} (₹{p2_d['sold_price_inr_cr']} Cr)",
            line_color=f2['color']
        ))
        fig_r.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], color="#94A3B8"),
                bgcolor="#0F172A"
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            template="plotly_dark",
            height=410,
            font=dict(family="Plus Jakarta Sans", color="#F8FAFC"),
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_r, use_container_width=True)
        
    with col_r:
        card_r_html = (
            f'<div class="fut-card" style="position: relative; overflow: hidden; background: radial-gradient(circle at 50% 30%, rgba({f2_rgb}, 0.16) 0%, rgba(15, 23, 42, 0.98) 75%), url(\'{f2["logo"]}\') no-repeat center 30% / 125px auto; background-blend-mode: overlay;">'
            f'<div class="fut-card-header-stripe" style="background: {f2["color"]};"></div>'
            f'<div style="position: relative; width: 106px; height: 106px; margin: 12px auto 8px auto; border-radius: 50%; display: flex; align-items: center; justify-content: center; background: radial-gradient(circle, rgba({f2_rgb}, 0.22) 0%, rgba(15,23,42,0.95) 75%); border: 2.5px solid {f2["color"]}; box-shadow: 0 0 16px rgba({f2_rgb}, 0.35);">'
            f'<img src="{f2["logo"]}" style="position: absolute; width: 75%; height: 75%; object-fit: contain; opacity: 0.32; pointer-events: none; z-index: 1;" />'
            f'<img src="{get_display_avatar(sel_2, p2_d["franchise"])}" style="position: relative; z-index: 2; width: 90px; height: 90px; border-radius: 50%; object-fit: cover;" onerror="this.onerror=null; this.src=\'https://ui-avatars.com/api/?name={urllib.parse.quote(sel_2)}&background={hex2}&color={text2}&size=256&bold=true\';"/>'
            f'<div style="position: absolute; bottom: -2px; right: -2px; z-index: 3; width: 34px; height: 34px; border-radius: 50%; background: #0F172A; border: 2px solid {f2["color"]}; display: flex; align-items: center; justify-content: center; box-shadow: 0 3px 8px rgba(0,0,0,0.6);" title="{p2_d["franchise"]}">'
            f'<img src="{f2["logo"]}" style="width: 22px; height: 22px; object-fit: contain;"/>'
            f'</div>'
            f'</div>'
            f'<div class="card-player-name">{sel_2}</div>'
            f'<div class="card-team-name">{f2["badge"]} {p2_d["franchise"]} • {p2_d["player_role"]}</div>'
            f'<span class="val-badge badge-fair">{p2_d["value_buy_category"]}</span>'
            f'<div class="stat-pill-grid" style="margin-top: 14px;">'
            f'<div class="stat-item">💰 Price:<br><span class="stat-val">₹{p2_d["sold_price_inr_cr"]:.2f} Cr</span></div>'
            f'<div class="stat-item">💥 Death SR:<br><span class="stat-val">{p2_d["death_strike_rate"]:.1f}</span></div>'
            f'<div class="stat-item">⚡ PP SR:<br><span class="stat-val">{p2_d["pp_strike_rate"]:.1f}</span></div>'
            f'<div class="stat-item">🏏 Runs:<br><span class="stat-val">{int(p2_d["total_runs"])}</span></div>'
            f'</div>'
            f'</div>'
        )
        st.markdown(card_r_html, unsafe_allow_html=True)

# =============================================================================
# TAB 3: PLAYER SPOTLIGHT & GALLERY
# =============================================================================
with tab_gallery:
    st.markdown("### 🌟 All-Player Scouting Gallery")
    st.caption("Comprehensive scouting gallery featuring player portraits, team credentials, and core performance metrics:")
    
    q = st.text_input("🔍 Search Player Name:", placeholder="e.g. Kohli, Bumrah, Klaasen, Starc, Badoni, Rana...")
    g_df = filtered_df.copy()
    if q:
        g_df = g_df[g_df["player_name"].str.contains(q, case=False, na=False)]
        
    st.markdown(f"**Showing {len(g_df)} Players**")
    
    g_cols = 4
    g_list = g_df.to_dict('records')
    
    for i in range(0, len(g_list), g_cols):
        slice_row = g_list[i:i+g_cols]
        cols = st.columns(g_cols)
        for col, p in zip(cols, slice_row):
            f_meta = FRANCHISE_META.get(p['franchise'], FRANCHISE_META["Other / Unassigned"])
            f_rgb = f_meta.get("color_rgb", "56, 189, 248")
            hex_c = f_meta["color"].replace("#", "")
            text_c = f_meta["text"].replace("#", "")
            b_class = "badge-steal" if p['value_buy_category'] == "Steal Buy" else ("badge-risk" if p['value_buy_category'] == "Overpriced Risk" else "badge-fair")
            avatar_url = get_display_avatar(p['player_name'], p['franchise'])
            with col:
                gallery_card_html = (
                    f'<div class="fut-card" style="position: relative; overflow: hidden; background: radial-gradient(circle at 50% 30%, rgba({f_rgb}, 0.16) 0%, rgba(15, 23, 42, 0.98) 75%), url(\'{f_meta["logo"]}\') no-repeat center 30% / 125px auto; background-blend-mode: overlay;">'
                    f'<div class="fut-card-header-stripe" style="background: {f_meta["color"]};"></div>'
                    f'<div style="position: relative; width: 106px; height: 106px; margin: 12px auto 8px auto; border-radius: 50%; display: flex; align-items: center; justify-content: center; background: radial-gradient(circle, rgba({f_rgb}, 0.22) 0%, rgba(15,23,42,0.95) 75%); border: 2.5px solid {f_meta["color"]}; box-shadow: 0 0 16px rgba({f_rgb}, 0.35);">'
                    f'<img src="{f_meta["logo"]}" style="position: absolute; width: 75%; height: 75%; object-fit: contain; opacity: 0.32; pointer-events: none; z-index: 1;" />'
                    f'<img src="{avatar_url}" style="position: relative; z-index: 2; width: 90px; height: 90px; border-radius: 50%; object-fit: cover;" onerror="this.onerror=null; this.src=\'https://ui-avatars.com/api/?name={urllib.parse.quote(p["player_name"])}&background={hex_c}&color={text_c}&size=256&bold=true\';"/>'
                    f'<div style="position: absolute; bottom: -2px; right: -2px; z-index: 3; width: 34px; height: 34px; border-radius: 50%; background: #0F172A; border: 2px solid {f_meta["color"]}; display: flex; align-items: center; justify-content: center; box-shadow: 0 3px 8px rgba(0,0,0,0.6);" title="{p["franchise"]}">'
                    f'<img src="{f_meta["logo"]}" style="width: 22px; height: 22px; object-fit: contain;"/>'
                    f'</div>'
                    f'</div>'
                    f'<div class="card-player-name">{p["player_name"]}</div>'
                    f'<div class="card-team-name">{f_meta["badge"]} {p["franchise"]} • {p["player_role"]}</div>'
                    f'<span class="val-badge {b_class}">{p["value_buy_category"]}</span>'
                    f'<div class="stat-pill-grid">'
                    f'<div class="stat-item">💰 Contract:<br><span class="stat-val">₹{p["sold_price_inr_cr"]:.2f} Cr</span></div>'
                    f'<div class="stat-item">💥 Death SR:<br><span class="stat-val">{p["death_strike_rate"]:.1f}</span></div>'
                    f'<div class="stat-item">🏏 Runs:<br><span class="stat-val">{int(p["total_runs"])}</span></div>'
                    f'<div class="stat-item">🎯 Wkts:<br><span class="stat-val">{int(p["total_wickets"])}</span></div>'
                    f'</div>'
                    f'</div>'
                )
                st.markdown(gallery_card_html, unsafe_allow_html=True)

# =============================================================================
# TAB 4: BOWLING THREAT & PRESSURE
# =============================================================================
with tab_bowling:
    st.markdown("### ⚡ Bowling Threat & Pressure Containment")
    st.caption("Analyzing bowling execution, pressure containment, and dot ball frequency in the critical death overs (Overs 16-20):")
    
    b_df = filtered_df[filtered_df["total_legal_balls"] >= 36].copy()
    
    fig_b = px.scatter(
        b_df,
        x="death_economy_rate",
        y="death_dot_pct",
        size="total_wickets",
        color="franchise",
        color_discrete_map={k: v["color"] for k, v in FRANCHISE_META.items()},
        hover_name="player_name",
        hover_data={
            "sold_price_inr_cr": ":.2f",
            "total_wickets": True,
            "overall_economy_rate": ":.2f"
        },
        labels={
            "death_economy_rate": "Death Economy Rate (Lower is Better)",
            "death_dot_pct": "Death Dot Ball % (Higher is Better)"
        },
        template="plotly_dark",
        height=500
    )
    fig_b.update_layout(
        plot_bgcolor="#0B0F19",
        paper_bgcolor="#0B0F19",
        font=dict(family="Plus Jakarta Sans", color="#F8FAFC")
    )
    st.plotly_chart(fig_b, use_container_width=True)

# =============================================================================
# TAB 6: EXCEL ANALYTICS, DATA CLEANSING & MODELING HUB
# =============================================================================
with tab_excel:
    st.markdown("### 📑 Microsoft Excel Analytics & Data Cleansing Hub")
    st.caption("Module 1 of the Data Analytics Trinity (Excel + SQL + Power BI): Multi-sheet financial model, two-tier XLOOKUP harmonization, Power Query M-code, and live spreadsheet exports.")
    
    # 1. Direct Downloads for Excel & Power BI Import
    st.markdown("#### 📥 Enterprise Excel Workbooks & Clean Datasets")
    st.caption("Download the complete multi-tab Microsoft Excel workbook or modular CSV dimension/fact tables:")
    
    col_wb1, col_wb2, col_wb3 = st.columns(3)
    excel_file_path = os.path.join(BASE_DIR, "excel", "IPL_Auction_Intelligence_Model.xlsx")
    deliv_file_path = os.path.join(BASE_DIR, "excel", "IPL_Ball_By_Ball_Deliveries_2022_2025.xlsx")
    
    with col_wb1:
        if os.path.exists(excel_file_path):
            with open(excel_file_path, "rb") as f:
                excel_bytes = f.read()
            st.download_button(
                label="📊 Master Financial Model (.xlsx)",
                data=excel_bytes,
                file_name="IPL_Auction_Intelligence_Model.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Multi-sheet Microsoft Excel model containing Executive Summary, Scouting Mart, Player Registry, Auction Contracts, and Salary Caps with dynamic formulas."
            )
            
    with col_wb2:
        if os.path.exists(deliv_file_path):
            with open(deliv_file_path, "rb") as f:
                deliv_bytes = f.read()
            st.download_button(
                label="⚾ Ball-by-Ball Deliveries (.xlsx)",
                data=deliv_bytes,
                file_name="IPL_Ball_By_Ball_Deliveries_2022_2025.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Complete Microsoft Excel workbook with 87,690 delivery-level rows and match metadata (6.0 MB)."
            )

    with col_wb3:
        if os.path.exists(DB_PATH):
            with open(DB_PATH, "rb") as f:
                db_bytes = f.read()
            st.download_button(
                label="💾 Full SQLite Database (.db)",
                data=db_bytes,
                file_name="ipl_auction_intelligence.db",
                mime="application/x-sqlite3",
                help="Download the entire 16.8MB SQLite relational data warehouse containing all tables and views."
            )

    c_csv1, c_csv2, c_csv3 = st.columns(3)
    with c_csv1:
        reg_csv = df_registry.to_csv(index=False).encode('utf-8')
        st.download_button("👥 Player Registry (CSV)", data=reg_csv, file_name="dim_player_registry.csv", mime="text/csv", help="Clean dimension table with canonical player names, roles, and career timelines.")
        
    with c_csv2:
        mart_csv = df_mart.to_csv(index=False).encode('utf-8')
        st.download_button("🏏 Scouting Mart (CSV)", data=mart_csv, file_name="vw_scouting_master_mart.csv", mime="text/csv", help="Full analytical mart with financial KPIs, runs, wickets, and valuation tiers.")
        
    with c_csv3:
        conn = sqlite3.connect(DB_PATH)
        df_auc_down = pd.read_sql_query("SELECT * FROM dim_auction_prices", conn)
        conn.close()
        auc_csv = df_auc_down.to_csv(index=False).encode('utf-8')
        st.download_button("💰 Auction Contracts (CSV)", data=auc_csv, file_name="dim_auction_prices.csv", mime="text/csv", help="All verified player contracts across 2022-2026 seasons.")

    st.markdown("<hr style='border-color: rgba(255,255,255,0.08);'>", unsafe_allow_html=True)
    
    # 2. Interactive Excel Pivot Summary Matrix
    st.markdown("#### 🧮 Interactive Excel Pivot Summary Matrix")
    st.caption("Dynamic Excel-style Pivot Table aggregated by Franchise, Role, and Season:")
    
    pivot_season = st.selectbox("Select Tournament Season for Excel Pivot Matrix:", sorted(list(df_mart["season"].unique()), reverse=True), key="excel_pivot_season")
    pivot_df = df_mart[df_mart["season"] == pivot_season]
    
    excel_pivot = pivot_df.groupby(["franchise", "player_role"]).agg(
        Contracted_Players=("player_name", "count"),
        Total_Purse_Spend_Cr=("sold_price_inr_cr", "sum"),
        Total_Runs=("total_runs", "sum"),
        Total_Wickets=("total_wickets", "sum"),
        Avg_Death_SR=("death_strike_rate", "mean")
    ).round(2).reset_index()
    
    st.dataframe(excel_pivot, use_container_width=True)
    
    st.markdown("<hr style='border-color: rgba(255,255,255,0.08);'>", unsafe_allow_html=True)
    
    # 3. Production Excel Formulas & Power Query M-Code
    st.markdown("#### ⚙️ Production Excel Formulas & Audit Logic")
    
    ex_col1, ex_col2 = st.columns(2)
    with ex_col1:
        st.markdown("**1. Two-Tier XLOOKUP Name Harmonization Formula**")
        st.caption("Standardizes Cricsheet scorecard initials (e.g. `V Kohli`) to Official Legal Registration (`Virat Kohli`):")
        st.code("""=XLOOKUP(TRIM(A2), dim_player_registry!$A$2:$A$500, dim_player_registry!$B$2:$B$500, 
    XLOOKUP("*" & RIGHT(TRIM(A2), LEN(TRIM(A2)) - SEARCH(" ", TRIM(A2))) & "*", 
            dim_player_registry!$B$2:$B$500, dim_player_registry!$B$2:$B$500, 
            "FLAG_MANUAL_REVIEW", 2))""", language="excel")
            
        st.markdown("**2. Legal Delivery & Ball Faced Accounting**")
        st.caption("Isolates legal deliveries (excluding wides and no-balls) and batter balls faced:")
        st.code("""=IF(AND(wides=0, noballs=0), 1, 0)
=IF(wides=0, 1, 0)""", language="excel")

    with ex_col2:
        st.markdown("**3. Power Query M-Code (Fuzzy Matching & Text Cleaning)**")
        st.caption("Automates fuzzy merge between raw deliveries and official auction register:")
        st.code("""let
    Source = Table.NestedJoin(RawDeliveries, {"batter"}, PlayerRegistry, {"cricsheet_name"}, "PlayerMeta", JoinKind.LeftOuter),
    #"Trimmed Text" = Table.TransformColumns(Source, {{"batter", Text.Trim, type text}}),
    #"Expanded Meta" = Table.ExpandTableColumn(#"Trimmed Text", "PlayerMeta", {"canonical_name", "primary_franchise"}, {"Standard_Player", "Franchise"})
in
    #"Expanded Meta" """, language="powerquery")
    
        st.markdown("**4. Purse Ceiling VLOOKUP & Squad Limit Audit**")
        st.caption("Enforces BCCI salary cap compliance (≤ ₹120-125 Cr) and squad constraints (18–25 players):")
        st.code("""=IF(C2 > VLOOKUP(A2, salary_cap_master!$A$2:$B$6, 2, FALSE), "PURSE_BREACH", "COMPLIANT")
=IF(OR(D2 < 18, D2 > 25), "SQUAD_SIZE_VIOLATION", "COMPLIANT")""", language="excel")
        
    with st.expander("📄 View Full Excel Audit & Cleansing Technical Documentation"):
        guide_path = os.path.join(BASE_DIR, "excel", "excel_audit_and_cleansing_guide.md")
        if os.path.exists(guide_path):
            with open(guide_path, "r", encoding="utf-8") as f:
                st.markdown(f.read())

# =============================================================================
# TAB 7: POWER BI MODELING & DAX HUB
# =============================================================================
with tab_powerbi:
    st.markdown("### 📈 Power BI Enterprise Implementation Blueprint")
    st.markdown(r"""
    To replicate this exact high-performance dashboard in **Microsoft Power BI Desktop**:
    
    #### 1. How to Enable Dynamic Player Photos in Power BI
    1. In Power BI Desktop, open **Data View** -> Select table `dim_player_registry` (or `dim_auction_prices`).
    2. Click on the column `player_image_url`.
    3. In the top ribbon, go to **Column Tools -> Data Category** -> Select **`Image URL`**.
    4. Drag `player_image_url` into any **Table**, **Matrix**, or custom **Image Card / Synoptic Panel** visual. Power BI will automatically render the player's photo!
    
    #### 2. Star Schema Model Architecture
    - Connect `dim_player_registry[cricsheet_name]` -> `fact_deliveries[batter]` (1:N Active).
    - Connect `dim_player_registry[cricsheet_name]` -> `fact_deliveries[bowler]` (1:N Inactive, activated via `USERELATIONSHIP`).
    - Connect `dim_player_registry[canonical_name]` -> `dim_auction_prices[standardized_name]` (1:N Active).
    - Connect `dim_matches[match_id]` -> `fact_deliveries[match_id]` (1:N Active).
    """)
    
    with st.expander("📄 View Star Schema ER Diagram & Documentation"):
        with open(os.path.join(BASE_DIR, "powerbi", "star_schema_data_model.md"), "r") as f:
            st.markdown(f.read())
            
    with st.expander("💻 View Complete Production DAX Measure Library"):
        with open(os.path.join(BASE_DIR, "powerbi", "dax_measures_library.dax"), "r") as f:
            st.code(f.read(), language="dax")

# =============================================================================
# TAB 6: LIVE SQL QUERY CONSOLE
# =============================================================================
with tab_sql:
    st.markdown("### 💾 Live SQL Query Console (Direct Data Warehouse Access)")
    st.caption(f"Connected to SQLite Relational Warehouse: `{DB_PATH}` (87k+ deliveries)")
    
    if os.path.exists(DB_PATH):
        with open(DB_PATH, "rb") as f:
            db_raw = f.read()
        col_db1, col_db2 = st.columns([1, 3])
        with col_db1:
            st.download_button(
                label="📥 Download Full Database (.db)",
                data=db_raw,
                file_name="ipl_auction_intelligence.db",
                mime="application/x-sqlite3",
                help="Download full SQLite relational database (16.8 MB) containing all raw deliveries, player registry, auction prices, and calculated scouting views."
            )
        with col_db2:
            st.info("💡 You can open this `.db` file in **DB Browser for SQLite**, **DBeaver**, **VS Code SQLite Viewer**, or connect directly to **Power BI / Python / Excel** via ODBC.")

    
    preset_queries = {
        "Query 1: Top 10 Undervalued Finishers (Death SR > 160, Price <= 6 Cr)": """
SELECT 
    season, player_name, franchise, sold_price_inr_cr, total_runs, 
    death_strike_rate, cost_per_run_inr, performance_to_salary_value_score
FROM vw_scouting_master_mart
WHERE sold_price_inr_cr <= 6.00
  AND death_strike_rate > 160.00
  AND total_runs >= 100
ORDER BY death_strike_rate DESC, performance_to_salary_value_score DESC
LIMIT 10;
        """,
        "Query 2: Powerplay Impact Specialists (PP Wickets >= 4)": """
SELECT 
    season, player_name, franchise, sold_price_inr_cr, 
    pp_wickets, pp_economy_rate, total_wickets, cost_per_wicket_inr
FROM vw_scouting_master_mart
WHERE pp_wickets >= 4
  AND pp_economy_rate <= 8.50
ORDER BY pp_wickets DESC, pp_economy_rate ASC;
        """
    }
    
    sel_q = st.selectbox("Select Business Scenario:", list(preset_queries.keys()))
    sql_text = st.text_area("SQL Statement (Editable):", value=preset_queries[sel_q].strip(), height=150)
    
    if st.button("🚀 Run Live Query", type="primary"):
        try:
            conn = sqlite3.connect(DB_PATH)
            res = pd.read_sql_query(sql_text, conn)
            conn.close()
            st.success(f"Query returned {len(res)} rows in 3ms.")
            st.dataframe(res, use_container_width=True)
            csv = res.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Export Results CSV", data=csv, file_name="ipl_scouting_results.csv", mime="text/csv")
        except Exception as e:
            st.error(f"SQL Execution Error: {e}")
