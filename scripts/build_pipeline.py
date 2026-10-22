"""
IPL Franchise Auction Intelligence & Player Valuation Platform
ETL & Data Engineering Pipeline (Updated for IPL 2022 through 2026)
Accurate Season-by-Season Franchise Tracking & Roster Intelligence
"""

import os
import re
import io
import csv
import zipfile
import urllib.request
import urllib.parse
import sqlite3
import pandas as pd
import numpy as np

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_DIR = os.path.join(BASE_DIR, "database")
EXCEL_DIR = os.path.join(BASE_DIR, "excel")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(DB_DIR, exist_ok=True)
os.makedirs(EXCEL_DIR, exist_ok=True)

CRICSHEET_URL = "https://cricsheet.org/downloads/ipl_csv2.zip"
LOCAL_ZIP_PATH = os.path.join(DATA_DIR, "ipl_csv2.zip")
TARGET_SEASONS = {"2022", "2023", "2024", "2025", "2026"}

print(f"[*] Starting ETL pipeline for IPL Seasons {sorted(list(TARGET_SEASONS))}...")

# Cache zip locally to avoid re-downloading on every run
if os.path.exists(LOCAL_ZIP_PATH) and os.path.getsize(LOCAL_ZIP_PATH) > 1000000:
    print(f"[+] Using cached Cricsheet dataset from {LOCAL_ZIP_PATH}...")
    with open(LOCAL_ZIP_PATH, "rb") as f:
        zip_bytes = f.read()
else:
    print(f"[*] Downloading Cricsheet dataset from {CRICSHEET_URL}...")
    req = urllib.request.Request(CRICSHEET_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=60) as resp:
        zip_bytes = resp.read()
    with open(LOCAL_ZIP_PATH, "wb") as f:
        f.write(zip_bytes)
    print(f"[+] Download complete & cached: {len(zip_bytes) / (1024*1024):.2f} MB.")

z = zipfile.ZipFile(io.BytesIO(zip_bytes))
all_files = set(z.namelist())

# Team Name Normalizer
def normalize_franchise(t_name):
    if not t_name:
        return "Other / Unassigned"
    t = t_name.strip()
    if t in ("Royal Challengers Bangalore", "RCB"):
        return "Royal Challengers Bengaluru"
    if t in ("Kings XI Punjab", "KXIP"):
        return "Punjab Kings"
    if t in ("Delhi Daredevils", "DD"):
        return "Delhi Capitals"
    if t in ("Rising Pune Supergiant", "Rising Pune Supergiants", "RPS", "Pune Warriors"):
        return "Other / Unassigned"
    if t in ("Gujarat Lions", "GL", "Kochi Tuskers Kerala", "Deccan Chargers"):
        return "Other / Unassigned"
    return t

# Identify target matches from info files
target_matches = []
matches_meta = []
match_season_map = {}

for filename in all_files:
    if filename.endswith("_info.csv"):
        match_id = filename.replace("_info.csv", "")
        content = z.read(filename).decode("utf-8", errors="ignore").splitlines()
        
        info_dict = {
            "match_id": int(match_id),
            "season": None,
            "match_date": None,
            "venue": "",
            "city": "",
            "team1": "",
            "team2": "",
            "toss_winner": "",
            "toss_decision": "",
            "winner": "",
            "result_margin": 0,
            "player_of_match": ""
        }
        teams = []
        
        for line in content:
            parts = [p.strip().strip('"') for p in line.split(",")]
            if len(parts) < 3:
                continue
            key = parts[1]
            val = parts[2]
            
            if key == "season":
                info_dict["season"] = val
            elif key == "date" and not info_dict["match_date"]:
                info_dict["match_date"] = val
            elif key == "venue":
                info_dict["venue"] = val
            elif key == "city":
                info_dict["city"] = val
            elif key == "team":
                teams.append(normalize_franchise(val))
            elif key == "toss_winner":
                info_dict["toss_winner"] = normalize_franchise(val)
            elif key == "toss_decision":
                info_dict["toss_decision"] = val
            elif key == "winner":
                info_dict["winner"] = normalize_franchise(val)
            elif key in ("winner_runs", "winner_wickets"):
                try:
                    info_dict["result_margin"] = int(val)
                except:
                    pass
            elif key == "player_of_match":
                info_dict["player_of_match"] = val
                
        if len(teams) >= 2:
            info_dict["team1"] = teams[0]
            info_dict["team2"] = teams[1]
            
        if info_dict["season"] in TARGET_SEASONS:
            target_matches.append(match_id)
            matches_meta.append(info_dict)
            match_season_map[int(match_id)] = int(info_dict["season"])

print(f"[+] Found {len(target_matches)} matches across seasons {sorted(list(TARGET_SEASONS))}.")

df_matches = pd.DataFrame(matches_meta)
df_matches["season"] = df_matches["season"].astype(int)
df_matches["match_date"] = pd.to_datetime(df_matches["match_date"]).dt.strftime('%Y-%m-%d')
df_matches.sort_values(by=["season", "match_date", "match_id"], inplace=True)

# Export dim_matches.csv
matches_csv_path = os.path.join(DATA_DIR, "dim_matches.csv")
df_matches.to_csv(matches_csv_path, index=False)
print(f"[+] Saved {matches_csv_path} ({len(df_matches)} rows)")

# Process deliveries with explicit batting_team & bowling_team
deliveries_list = []
player_season_teams = {} # (cricsheet_player, season) -> list of teams played for
player_all_teams = {}    # cricsheet_player -> list of teams played for
player_balls_faced = {}
player_balls_bowled = {}

for match_id in target_matches:
    deliv_filename = f"{match_id}.csv"
    if deliv_filename not in all_files:
        continue
    
    m_season = match_season_map.get(int(match_id), 2024)
    deliv_bytes = z.read(deliv_filename)
    csv_reader = csv.DictReader(io.StringIO(deliv_bytes.decode("utf-8", errors="ignore")))
    
    for row in csv_reader:
        try:
            ball_val = float(row.get("ball", 0.0))
            over_num = int(ball_val)
            ball_num = int(round((ball_val - over_num) * 10))
            
            wides = int(row.get("wides") or 0)
            noballs = int(row.get("noballs") or 0)
            byes = int(row.get("byes") or 0)
            legbyes = int(row.get("legbyes") or 0)
            penalty = int(row.get("penalty") or 0)
            runs_off_bat = int(row.get("runs_off_bat") or 0)
            extra_runs = int(row.get("extras") or 0)
            
            wicket_type = row.get("wicket_type", "").strip()
            is_wicket = 1 if wicket_type else 0
            
            b_team = normalize_franchise(row.get("batting_team", ""))
            bw_team = normalize_franchise(row.get("bowling_team", ""))
            
            striker = row.get("striker", "").strip()
            bowler = row.get("bowler", "").strip()
            non_striker = row.get("non_striker", "").strip()
            
            if striker and b_team != "Other / Unassigned":
                player_season_teams.setdefault((striker, m_season), []).append(b_team)
                player_all_teams.setdefault(striker, []).append(b_team)
                player_balls_faced[striker] = player_balls_faced.get(striker, 0) + 1
            if non_striker and b_team != "Other / Unassigned":
                player_season_teams.setdefault((non_striker, m_season), []).append(b_team)
                player_all_teams.setdefault(non_striker, []).append(b_team)
            if bowler and bw_team != "Other / Unassigned":
                player_season_teams.setdefault((bowler, m_season), []).append(bw_team)
                player_all_teams.setdefault(bowler, []).append(bw_team)
                player_balls_bowled[bowler] = player_balls_bowled.get(bowler, 0) + 1
            
            deliveries_list.append({
                "match_id": int(match_id),
                "inning": int(row.get("innings", 1)),
                "over": over_num,
                "ball": ball_num,
                "batting_team": b_team,
                "bowling_team": bw_team,
                "batter": striker,
                "bowler": bowler,
                "non_striker": non_striker,
                "runs_off_bat": runs_off_bat,
                "extra_runs": extra_runs,
                "wides": wides,
                "noballs": noballs,
                "byes": byes,
                "legbyes": legbyes,
                "penalty": penalty,
                "is_wicket": is_wicket,
                "dismissal_kind": wicket_type,
                "player_dismissed": row.get("player_dismissed", "").strip(),
                "fielder": row.get("fielder_1", "").strip()
            })
        except Exception as e:
            continue

df_deliveries = pd.DataFrame(deliveries_list)
df_deliveries.insert(0, "delivery_id", range(1, len(df_deliveries) + 1))

# Export fact_deliveries.csv
deliveries_csv_path = os.path.join(DATA_DIR, "fact_deliveries.csv")
df_deliveries.to_csv(deliveries_csv_path, index=False)
print(f"[+] Saved {deliveries_csv_path} ({len(df_deliveries)} deliveries with batting & bowling teams)")

# Helper to find mode team
def get_primary_team_from_list(team_list, default="Other / Unassigned"):
    if not team_list:
        return default
    s = pd.Series(team_list)
    return s.value_counts().index[0]

# -----------------------------------------------------------------------------
# Player Headshot CDN Mapping (Verified Wikipedia Portraits + Official Badges)
# -----------------------------------------------------------------------------
VERIFIED_PORTRAITS = {
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

FRANCHISE_HEX = {
    "Chennai Super Kings": ("FACC15", "0F172A"),
    "Mumbai Indians": ("0284C7", "FFFFFF"),
    "Royal Challengers Bengaluru": ("DC2626", "FFFFFF"),
    "Kolkata Knight Riders": ("7C3AED", "FFFFFF"),
    "Sunrisers Hyderabad": ("F97316", "FFFFFF"),
    "Rajasthan Royals": ("EC4899", "FFFFFF"),
    "Gujarat Titans": ("1E3A8A", "FFFFFF"),
    "Lucknow Super Giants": ("06B6D4", "FFFFFF"),
    "Delhi Capitals": ("2563EB", "FFFFFF"),
    "Punjab Kings": ("E11D48", "FFFFFF"),
    "Other / Unassigned": ("475569", "FFFFFF")
}

def get_player_avatar(name, franchise="Other / Unassigned"):
    if name in VERIFIED_PORTRAITS:
        return VERIFIED_PORTRAITS[name]
    bg_color, fg_color = FRANCHISE_HEX.get(franchise, ("334155", "FFFFFF"))
    encoded_name = urllib.parse.quote(name)
    return f"https://ui-avatars.com/api/?name={encoded_name}&background={bg_color}&color={fg_color}&size=256&bold=true&font-size=0.42"

# Name Harmonization Mapping with Current (2025/2026) Official Franchises
name_map = {
    "V Kohli": ("Virat Kohli", "Royal Challengers Bengaluru", "Batter", True, False),
    "RG Sharma": ("Rohit Sharma", "Mumbai Indians", "Batter", True, False),
    "SA Yadav": ("Suryakumar Yadav", "Mumbai Indians", "Batter", True, False),
    "JJ Bumrah": ("Jasprit Bumrah", "Mumbai Indians", "Bowler", True, False),
    "HH Pandya": ("Hardik Pandya", "Mumbai Indians", "All-Rounder", True, False),
    "MS Dhoni": ("MS Dhoni", "Chennai Super Kings", "Wicketkeeper", False, False),
    "RA Jadeja": ("Ravindra Jadeja", "Rajasthan Royals", "All-Rounder", True, False),
    "RD Gaikwad": ("Ruturaj Gaikwad", "Chennai Super Kings", "Batter", True, False),
    "Shubman Gill": ("Shubman Gill", "Gujarat Titans", "Batter", True, False),
    "Rashid Khan": ("Rashid Khan", "Gujarat Titans", "Bowler", True, True),
    "Mohammed Shami": ("Mohammed Shami", "Sunrisers Hyderabad", "Bowler", True, False),
    "DA Miller": ("David Miller", "Lucknow Super Giants", "Batter", True, True),
    "R Tewatia": ("Rahul Tewatia", "Gujarat Titans", "All-Rounder", True, False),
    "Mohit Sharma": ("Mohit Sharma", "Gujarat Titans", "Bowler", True, False),
    "KL Rahul": ("KL Rahul", "Delhi Capitals", "Wicketkeeper", True, False),
    "N Pooran": ("Nicholas Pooran", "Lucknow Super Giants", "Wicketkeeper", True, True),
    "MP Stoinis": ("Marcus Stoinis", "Punjab Kings", "All-Rounder", True, True),
    "Q de Kock": ("Quinton de Kock", "Kolkata Knight Riders", "Wicketkeeper", True, True),
    "Ravi Bishnoi": ("Ravi Bishnoi", "Lucknow Super Giants", "Bowler", True, False),
    "SV Samson": ("Sanju Samson", "Chennai Super Kings", "Wicketkeeper", True, False),
    "YBK Jaiswal": ("Yashasvi Jaiswal", "Rajasthan Royals", "Batter", True, False),
    "JC Buttler": ("Jos Buttler", "Gujarat Titans", "Wicketkeeper", True, True),
    "SO Hetmyer": ("Shimron Hetmyer", "Rajasthan Royals", "Batter", True, True),
    "TA Boult": ("Trent Boult", "Mumbai Indians", "Bowler", True, True),
    "YS Chahal": ("Yuzvendra Chahal", "Punjab Kings", "Bowler", True, False),
    "R Ashwin": ("Ravichandran Ashwin", "Chennai Super Kings", "All-Rounder", True, False),
    "SS Iyer": ("Shreyas Iyer", "Punjab Kings", "Batter", True, False),
    "Rinku Singh": ("Rinku Singh", "Kolkata Knight Riders", "Batter", True, False),
    "AD Russell": ("Andre Russell", "Kolkata Knight Riders", "All-Rounder", True, True),
    "SP Narine": ("Sunil Narine", "Kolkata Knight Riders", "All-Rounder", True, True),
    "MA Starc": ("Mitchell Starc", "Delhi Capitals", "Bowler", True, True),
    "PD Salt": ("Phil Salt", "Royal Challengers Bengaluru", "Wicketkeeper", True, True),
    "CV Varun": ("Varun Chakravarthy", "Kolkata Knight Riders", "Bowler", True, False),
    "HV Patel": ("Harshal Patel", "Sunrisers Hyderabad", "Bowler", True, False),
    "Arshdeep Singh": ("Arshdeep Singh", "Punjab Kings", "Bowler", True, False),
    "SM Curran": ("Sam Curran", "Chennai Super Kings", "All-Rounder", True, True),
    "LS Livingstone": ("Liam Livingstone", "Royal Challengers Bengaluru", "All-Rounder", True, True),
    "JM Bairstow": ("Jonny Bairstow", "Punjab Kings", "Batter", True, True),
    "Shashank Singh": ("Shashank Singh", "Punjab Kings", "Batter", True, False),
    "Ashutosh Sharma": ("Ashutosh Sharma", "Delhi Capitals", "Batter", True, False),
    "Jitesh Sharma": ("Jitesh Sharma", "Royal Challengers Bengaluru", "Wicketkeeper", True, False),
    "RR Pant": ("Rishabh Pant", "Lucknow Super Giants", "Wicketkeeper", True, False),
    "AR Patel": ("Axar Patel", "Delhi Capitals", "All-Rounder", True, False),
    "Kuldeep Yadav": ("Kuldeep Yadav", "Delhi Capitals", "Bowler", True, False),
    "DA Warner": ("David Warner", "Delhi Capitals", "Batter", True, True),
    "MR Marsh": ("Mitchell Marsh", "Delhi Capitals", "All-Rounder", True, True),
    "J Fraser-McGurk": ("Jake Fraser-McGurk", "Delhi Capitals", "Batter", True, True),
    "T Stubbs": ("Tristan Stubbs", "Delhi Capitals", "Wicketkeeper", True, True),
    "PJ Cummins": ("Pat Cummins", "Sunrisers Hyderabad", "Bowler", True, True),
    "H Klaasen": ("Heinrich Klaasen", "Sunrisers Hyderabad", "Wicketkeeper", True, True),
    "TM Head": ("Travis Head", "Sunrisers Hyderabad", "Batter", True, True),
    "Abhishek Sharma": ("Abhishek Sharma", "Sunrisers Hyderabad", "All-Rounder", True, False),
    "B Kumar": ("Bhuvneshwar Kumar", "Royal Challengers Bengaluru", "Bowler", True, False),
    "T Natarajan": ("T Natarajan", "Delhi Capitals", "Bowler", True, False),
    "F du Plessis": ("Faf du Plessis", "Delhi Capitals", "Batter", True, True),
    "GJ Maxwell": ("Glenn Maxwell", "Punjab Kings", "All-Rounder", True, True),
    "C Green": ("Cameron Green", "Royal Challengers Bengaluru", "All-Rounder", True, True),
    "Mohammed Siraj": ("Mohammed Siraj", "Gujarat Titans", "Bowler", True, False),
    "KD Karthik": ("Dinesh Karthik", "Royal Challengers Bengaluru", "Wicketkeeper", True, False),
    "M Pathirana": ("Matheesha Pathirana", "Chennai Super Kings", "Bowler", True, True),
    "S Dube": ("Shivam Dube", "Chennai Super Kings", "All-Rounder", True, False),
    "DL Chahar": ("Deepak Chahar", "Mumbai Indians", "Bowler", True, False),
    "TU Deshpande": ("Tushar Deshpande", "Rajasthan Royals", "Bowler", True, False),
    "Ishan Kishan": ("Ishan Kishan", "Sunrisers Hyderabad", "Wicketkeeper", True, False),
    "TH David": ("Tim David", "Royal Challengers Bengaluru", "Batter", True, True),
    "Tilak Varma": ("Tilak Varma", "Mumbai Indians", "Batter", True, False),
    "A Badoni": ("Ayush Badoni", "Lucknow Super Giants", "Batter", True, False),
    "Yash Dayal": ("Yash Dayal", "Royal Challengers Bengaluru", "Bowler", False, False),
    "Mukesh Kumar": ("Mukesh Kumar", "Delhi Capitals", "Bowler", True, False),
    "KK Ahmed": ("Khaleel Ahmed", "Chennai Super Kings", "Bowler", True, False),
    "Avesh Khan": ("Avesh Khan", "Lucknow Super Giants", "Bowler", True, False),
    "Dhruv Jurel": ("Dhruv Jurel", "Rajasthan Royals", "Wicketkeeper", True, False),
    "Harshit Rana": ("Harshit Rana", "Kolkata Knight Riders", "Bowler", False, False),
    "VR Iyer": ("Venkatesh Iyer", "Kolkata Knight Riders", "All-Rounder", True, False),
    "Nithish Kumar Reddy": ("Nitish Kumar Reddy", "Sunrisers Hyderabad", "All-Rounder", True, False),
    "Mayank Yadav": ("Mayank Yadav", "Lucknow Super Giants", "Bowler", False, False),
    "Rajat Patidar": ("Rajat Patidar", "Royal Challengers Bengaluru", "Batter", True, False),
    "Sai Sudharsan": ("Sai Sudharsan", "Gujarat Titans", "Batter", True, False),
    "B Sai Sudharsan": ("Sai Sudharsan", "Gujarat Titans", "Batter", True, False),
    "P Simran Singh": ("Prabhsimran Singh", "Punjab Kings", "Wicketkeeper", False, False),
    "RM Patidar": ("Rajat Patidar", "Royal Challengers Bengaluru", "Batter", True, False),
    "R Parag": ("Riyan Parag", "Rajasthan Royals", "All-Rounder", True, False),
    "AK Markram": ("Aiden Markram", "Lucknow Super Giants", "Batter", True, True),
    "AM Rahane": ("Ajinkya Rahane", "Kolkata Knight Riders", "Batter", True, False),
    "D Padikkal": ("Devdutt Padikkal", "Royal Challengers Bengaluru", "Batter", True, False),
    "RK Singh": ("Rinku Singh", "Kolkata Knight Riders", "Batter", True, False),
    "N Rana": ("Nitish Rana", "Rajasthan Royals", "Batter", True, False),
    "JM Sharma": ("Jitesh Sharma", "Royal Challengers Bengaluru", "Wicketkeeper", True, False),
    "DP Conway": ("Devon Conway", "Chennai Super Kings", "Batter", True, True),
    "S Dhawan": ("Shikhar Dhawan", "Punjab Kings", "Batter", True, False),
    "A Raghuvanshi": ("Angkrish Raghuvanshi", "Kolkata Knight Riders", "Batter", False, False),
    "KH Pandya": ("Krunal Pandya", "Royal Challengers Bengaluru", "All-Rounder", True, False),
    "N Wadhera": ("Nehal Wadhera", "Punjab Kings", "Batter", False, False),
    "Abishek Porel": ("Abishek Porel", "Delhi Capitals", "Wicketkeeper", False, False),
    "Naman Dhir": ("Naman Dhir", "Mumbai Indians", "All-Rounder", False, False),
    "Washington Sundar": ("Washington Sundar", "Gujarat Titans", "All-Rounder", True, False),
    "M Shahrukh Khan": ("Shahrukh Khan", "Gujarat Titans", "Batter", False, False),
    "K Rabada": ("Kagiso Rabada", "Gujarat Titans", "Bowler", True, True),
    "M Prasidh Krishna": ("Prasidh Krishna", "Gujarat Titans", "Bowler", True, False),
    "Noor Ahmad": ("Noor Ahmad", "Chennai Super Kings", "Bowler", True, True),
    "JR Hazlewood": ("Josh Hazlewood", "Royal Challengers Bengaluru", "Bowler", True, True),
    "SN Thakur": ("Shardul Thakur", "Lucknow Super Giants", "Bowler", True, False),
    "Sandeep Sharma": ("Sandeep Sharma", "Rajasthan Royals", "Bowler", True, False),
    "JC Archer": ("Jofra Archer", "Rajasthan Royals", "Bowler", True, True),
    "Mohsin Khan": ("Mohsin Khan", "Lucknow Super Giants", "Bowler", False, False),
    "M Jansen": ("Marco Jansen", "Punjab Kings", "All-Rounder", True, True),
    "M Theekshana": ("Maheesh Theekshana", "Rajasthan Royals", "Bowler", True, True),
    "R Sai Kishore": ("R Sai Kishore", "Gujarat Titans", "Bowler", True, False),
    "Harpreet Brar": ("Harpreet Brar", "Punjab Kings", "All-Rounder", False, False),
    "A Nortje": ("Anrich Nortje", "Kolkata Knight Riders", "Bowler", True, True),
    "A Manohar": ("Abhinav Manohar", "Gujarat Titans", "Batter", False, False),
    "A Mishra": ("Amit Mishra", "Lucknow Super Giants", "Bowler", True, False),
    "A Zampa": ("Adam Zampa", "Rajasthan Royals", "Bowler", True, True),
    "AT Rayudu": ("Ambati Rayudu", "Chennai Super Kings", "Batter", True, False),
    "AS Joseph": ("Alzarri Joseph", "Royal Challengers Bengaluru", "Bowler", True, True),
    "AJ Finch": ("Aaron Finch", "Kolkata Knight Riders", "Batter", True, True),
    "AF Milne": ("Adam Milne", "Chennai Super Kings", "Bowler", True, True),
    "AU Rashid": ("Adil Rashid", "Sunrisers Hyderabad", "Bowler", True, True),
    "Abdul Samad": ("Abdul Samad", "Sunrisers Hyderabad", "Batter", False, False),
    "Akash Deep": ("Akash Deep", "Royal Challengers Bengaluru", "Bowler", True, False),
    "Akash Madhwal": ("Akash Madhwal", "Mumbai Indians", "Bowler", False, False),
    "Anuj Rawat": ("Anuj Rawat", "Royal Challengers Bengaluru", "Wicketkeeper", False, False),
    "Arjun Tendulkar": ("Arjun Tendulkar", "Mumbai Indians", "All-Rounder", False, False),
    "Arshad Khan": ("Arshad Khan", "Lucknow Super Giants", "All-Rounder", False, False),
    "C Sakariya": ("Chetan Sakariya", "Kolkata Knight Riders", "Bowler", True, False),
    "D Brevis": ("Dewald Brevis", "Mumbai Indians", "Batter", False, True),
    "D Pretorius": ("Dwaine Pretorius", "Chennai Super Kings", "All-Rounder", True, True),
    "Kartik Tyagi": ("Kartik Tyagi", "Gujarat Titans", "Bowler", False, False),
    "K Gowtham": ("Krishnappa Gowtham", "Lucknow Super Giants", "All-Rounder", True, False),
    "KS Bharat": ("KS Bharat", "Kolkata Knight Riders", "Wicketkeeper", True, False),
    "Lalit Yadav": ("Lalit Yadav", "Delhi Capitals", "All-Rounder", False, False),
    "M Ashwin": ("Murugan Ashwin", "Rajasthan Royals", "Bowler", False, False),
    "Mahipal Lomror": ("Mahipal Lomror", "Royal Challengers Bengaluru", "All-Rounder", False, False),
    "Manish Pandey": ("Manish Pandey", "Kolkata Knight Riders", "Batter", True, False),
    "Navdeep Saini": ("Navdeep Saini", "Rajasthan Royals", "Bowler", True, False),
    "Prerak Mankad": ("Prerak Mankad", "Lucknow Super Giants", "All-Rounder", False, False),
    "R Powell": ("Rovman Powell", "Rajasthan Royals", "Batter", True, True),
    "R Shepherd": ("Romario Shepherd", "Mumbai Indians", "All-Rounder", True, True),
    "RD Chahar": ("Rahul Chahar", "Punjab Kings", "Bowler", True, False),
    "Ripal Patel": ("Ripal Patel", "Delhi Capitals", "All-Rounder", False, False),
    "S Gopal": ("Shreyas Gopal", "Chennai Super Kings", "Bowler", False, False),
    "S Kaul": ("Siddarth Kaul", "Royal Challengers Bengaluru", "Bowler", True, False),
    "Shahbaz Ahmed": ("Shahbaz Ahmed", "Sunrisers Hyderabad", "All-Rounder", True, False),
    "Simarjeet Singh": ("Simarjeet Singh", "Chennai Super Kings", "Bowler", False, False),
    "Suyash Sharma": ("Suyash Sharma", "Kolkata Knight Riders", "Bowler", False, False),
    "Swapnil Singh": ("Swapnil Singh", "Royal Challengers Bengaluru", "All-Rounder", False, False),
    "Umran Malik": ("Umran Malik", "Sunrisers Hyderabad", "Bowler", True, False),
    "UT Yadav": ("Umesh Yadav", "Gujarat Titans", "Bowler", True, False),
    "V Shankar": ("Vijay Shankar", "Gujarat Titans", "All-Rounder", True, False),
    "VR Aaron": ("Varun Aaron", "Gujarat Titans", "Bowler", True, False),
    "WP Saha": ("Wriddhiman Saha", "Gujarat Titans", "Wicketkeeper", True, False),
    "Yash Dhull": ("Yash Dhull", "Delhi Capitals", "Batter", False, False),
    # Additional mappings for unassigned players
    "A Kamboj": ("Anshul Kamboj", "Mumbai Indians", "Bowler", False, False),
    "A Tomar": ("Ankit Tomar", "Kolkata Knight Riders", "Batter", False, False),
    "AA Kulkarni": ("Arshin Kulkarni", "Lucknow Super Giants", "All-Rounder", False, False),
    "AJ Hosein": ("Akeal Hosein", "Sunrisers Hyderabad", "Bowler", True, True),
    "AJ Turner": ("Ashton Turner", "Lucknow Super Giants", "Batter", True, True),
    "AJ Tye": ("Andrew Tye", "Lucknow Super Giants", "Bowler", True, True),
    "AM Ghazanfar": ("Allah Ghazanfar", "Kolkata Knight Riders", "Bowler", True, True),
    "AS Roy": ("Anukul Roy", "Kolkata Knight Riders", "All-Rounder", False, False),
    "Abdul Basith": ("Abdul Basith", "Rajasthan Royals", "Batter", False, False),
    "Akash Singh": ("Akash Singh", "Sunrisers Hyderabad", "Bowler", False, False),
    "Aman Hakim Khan": ("Aman Khan", "Delhi Capitals", "All-Rounder", False, False),
    "Anmolpreet Singh": ("Anmolpreet Singh", "Sunrisers Hyderabad", "Batter", False, False),
    "Atharva Taide": ("Atharva Taide", "Punjab Kings", "Batter", False, False),
    "Harpreet Singh": ("Harpreet Singh Bhatia", "Punjab Kings", "Batter", False, False),
    "Sameer Rizvi": ("Sameer Rizvi", "Delhi Capitals", "Batter", False, False),
    "Kumar Kushagra": ("Kumar Kushagra", "Delhi Capitals", "Wicketkeeper", False, False),
    "Robin Minz": ("Robin Minz", "Gujarat Titans", "Wicketkeeper", False, False),
    "Tanush Kotian": ("Tanush Kotian", "Rajasthan Royals", "Bowler", False, False),
    "Nandre Burger": ("Nandre Burger", "Rajasthan Royals", "Bowler", True, True),
    "Kwena Maphaka": ("Kwena Maphaka", "Mumbai Indians", "Bowler", True, True),
    "Nuwan Thushara": ("Nuwan Thushara", "Mumbai Indians", "Bowler", True, True),
    "Spencer Johnson": ("Spencer Johnson", "Gujarat Titans", "Bowler", True, True),
    "Azmatullah Omarzai": ("Azmatullah Omarzai", "Gujarat Titans", "All-Rounder", True, True),
    "Shamar Joseph": ("Shamar Joseph", "Lucknow Super Giants", "Bowler", True, True),
    "Matt Henry": ("Matt Henry", "Lucknow Super Giants", "Bowler", True, True),
    "Jhye Richardson": ("Jhye Richardson", "Delhi Capitals", "Bowler", True, True),
    "Lizaad Williams": ("Lizaad Williams", "Delhi Capitals", "Bowler", True, True),
    "Rasikh Salam": ("Rasikh Salam", "Delhi Capitals", "Bowler", False, False),
    "Sumit Kumar": ("Sumit Kumar", "Delhi Capitals", "All-Rounder", False, False),
    "Swastik Chikara": ("Swastik Chikara", "Delhi Capitals", "Batter", False, False),
    "Vyshak Vijaykumar": ("Vyshak Vijaykumar", "Royal Challengers Bengaluru", "Bowler", False, False),
    "Himanshu Sharma": ("Himanshu Sharma", "Royal Challengers Bengaluru", "Bowler", False, False),
    "Manoj Bhandage": ("Manoj Bhandage", "Royal Challengers Bengaluru", "All-Rounder", False, False),
    "Vidwath Kaverappa": ("Vidwath Kaverappa", "Punjab Kings", "Bowler", False, False),
    "Kunal Rathore": ("Kunal Rathore", "Rajasthan Royals", "Wicketkeeper", False, False),
    "Shubham Dubey": ("Shubham Dubey", "Rajasthan Royals", "Batter", False, False),
    "Arshin Kulkarni": ("Arshin Kulkarni", "Lucknow Super Giants", "All-Rounder", False, False),
    "M Siddharth": ("Manimaran Siddharth", "Lucknow Super Giants", "Bowler", False, False),
    "Yudhvir Singh": ("Yudhvir Singh Charak", "Lucknow Super Giants", "Bowler", False, False),
    "Nishant Sindhu": ("Nishant Sindhu", "Chennai Super Kings", "All-Rounder", False, False),
    "Shaik Rasheed": ("Shaik Rasheed", "Chennai Super Kings", "Batter", False, False),
    "Mukesh Choudhary": ("Mukesh Choudhary", "Chennai Super Kings", "Bowler", False, False),
    "Rajvardhan Hangargekar": ("Rajvardhan Hangargekar", "Chennai Super Kings", "Bowler", False, False),
    "Richard Gleeson": ("Richard Gleeson", "Chennai Super Kings", "Bowler", True, True)
}

# Comprehensive List of Retired Players to Exclude
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

# Build Player Registry with Dynamic Team Attribution
registry_rows = []
unique_cricsheet_players = sorted(list(set(df_deliveries["batter"].unique()).union(set(df_deliveries["bowler"].unique()))))

# Map cricsheet player to canonical name
cricsheet_to_canonical = {}

for p in unique_cricsheet_players:
    if p in RETIRED_PLAYERS:
        continue
    if p in name_map:
        c_name, franchise, role, is_capped, is_overseas = name_map[p]
    else:
        c_name = p
        # Derive team from deliveries if not in name_map
        deliv_team = get_primary_team_from_list(player_all_teams.get(p, []))
        franchise = deliv_team if deliv_team != "Other / Unassigned" else "Other / Unassigned"
        b_faced = player_balls_faced.get(p, 0)
        b_bowled = player_balls_bowled.get(p, 0)
        if b_bowled >= 24 and b_faced >= 20:
            role = "All-Rounder"
        elif b_bowled >= 24:
            role = "Bowler"
        else:
            role = "Batter"
        is_capped = True if b_faced + b_bowled >= 60 else False
        is_overseas = False
        
    if c_name in RETIRED_PLAYERS:
        continue
        
    cricsheet_to_canonical[p] = c_name
    avatar_url = get_player_avatar(c_name, franchise)
    
    # Career journey string
    s_teams = []
    for s in (2022, 2023, 2024, 2025, 2026):
        s_team = get_primary_team_from_list(player_season_teams.get((p, s), []))
        if s_team != "Other / Unassigned":
            s_teams.append(f"{s_team} ({s})")
    if not s_teams and franchise != "Other / Unassigned":
        s_teams.append(f"{franchise} (2025–2026)")
        
    formatted_spans = []
    if s_teams:
        curr_team = None
        start_yr = None
        end_yr = None
        for item in s_teams:
            m = re.match(r"(.*) \((\d+)\)", item)
            if m:
                t, yr = m.group(1), int(m.group(2))
                if t == curr_team:
                    end_yr = yr
                else:
                    if curr_team:
                        formatted_spans.append(f"{curr_team} ({start_yr}–{end_yr})" if start_yr != end_yr else f"{curr_team} ({start_yr})")
                    curr_team, start_yr, end_yr = t, yr, yr
        if curr_team:
            formatted_spans.append(f"{curr_team} ({start_yr}–{end_yr})" if start_yr != end_yr else f"{curr_team} ({start_yr})")
    career_str = " ➔ ".join(formatted_spans) if formatted_spans else franchise

    registry_rows.append({
        "cricsheet_name": p,
        "canonical_name": c_name,
        "player_image_url": avatar_url,
        "primary_franchise": franchise,
        "primary_role": role,
        "is_capped": is_capped,
        "is_overseas": is_overseas,
        "career_franchises": career_str
    })

df_registry = pd.DataFrame(registry_rows)
registry_path = os.path.join(DATA_DIR, "dim_player_registry.csv")
df_registry.to_csv(registry_path, index=False)
df_registry.to_csv(os.path.join(EXCEL_DIR, "dim_player_registry.csv"), index=False)
print(f"[+] Saved player registry: {registry_path} ({len(df_registry)} players, {len(df_registry[df_registry['primary_franchise'] != 'Other / Unassigned'])} assigned)")

# -----------------------------------------------------------------------------
# Auction Prices Master (Seasons 2022 through 2026 with Verified Season Teams)
# -----------------------------------------------------------------------------
auction_data = [
    # 2026 Mega-Cycle Retentions
    ("Rishabh Pant", "Lucknow Super Giants", 2026, "Wicketkeeper", 2.00, 27.00, "Retained", True, False),
    ("Shreyas Iyer", "Punjab Kings", 2026, "Batter", 2.00, 26.75, "Retained", True, False),
    ("Venkatesh Iyer", "Kolkata Knight Riders", 2026, "All-Rounder", 2.00, 23.75, "Retained", True, False),
    ("Heinrich Klaasen", "Sunrisers Hyderabad", 2026, "Wicketkeeper", 2.00, 23.00, "Retained", True, True),
    ("Virat Kohli", "Royal Challengers Bengaluru", 2026, "Batter", 2.00, 21.00, "Retained", True, False),
    ("Nicholas Pooran", "Lucknow Super Giants", 2026, "Wicketkeeper", 2.00, 21.00, "Retained", True, True),
    ("Jasprit Bumrah", "Mumbai Indians", 2026, "Bowler", 2.00, 18.00, "Retained", True, False),
    ("Sanju Samson", "Chennai Super Kings", 2026, "Wicketkeeper", 2.00, 18.00, "Retained", True, False),
    ("Yashasvi Jaiswal", "Rajasthan Royals", 2026, "Batter", 2.00, 18.00, "Retained", True, False),
    ("Pat Cummins", "Sunrisers Hyderabad", 2026, "Bowler", 2.00, 18.00, "Retained", True, True),
    ("Rashid Khan", "Gujarat Titans", 2026, "Bowler", 2.00, 18.00, "Retained", True, True),
    ("Ruturaj Gaikwad", "Chennai Super Kings", 2026, "Batter", 2.00, 18.00, "Retained", True, False),
    ("Ravindra Jadeja", "Rajasthan Royals", 2026, "All-Rounder", 2.00, 18.00, "Retained", True, False),
    ("Sameer Rizvi", "Delhi Capitals", 2026, "Batter", 0.30, 0.95, "Retained", False, False),
    ("Arshdeep Singh", "Punjab Kings", 2026, "Bowler", 2.00, 18.00, "Retained", True, False),
    ("Yuzvendra Chahal", "Punjab Kings", 2026, "Bowler", 2.00, 18.00, "Retained", True, False),
    ("Suryakumar Yadav", "Mumbai Indians", 2026, "Batter", 2.00, 16.35, "Retained", True, False),
    ("Hardik Pandya", "Mumbai Indians", 2026, "All-Rounder", 2.00, 16.35, "Retained", True, False),
    ("Rohit Sharma", "Mumbai Indians", 2026, "Batter", 2.00, 16.30, "Retained", True, False),
    ("Axar Patel", "Delhi Capitals", 2026, "All-Rounder", 2.00, 16.50, "Retained", True, False),
    ("Shubman Gill", "Gujarat Titans", 2026, "Batter", 2.00, 16.50, "Retained", True, False),
    ("Jos Buttler", "Gujarat Titans", 2026, "Wicketkeeper", 2.00, 15.75, "Retained", True, True),
    ("KL Rahul", "Delhi Capitals", 2026, "Wicketkeeper", 2.00, 14.00, "Retained", True, False),
    ("Travis Head", "Sunrisers Hyderabad", 2026, "Batter", 2.00, 14.00, "Retained", True, True),
    ("Abhishek Sharma", "Sunrisers Hyderabad", 2026, "All-Rounder", 2.00, 14.00, "Retained", True, False),
    ("Rinku Singh", "Kolkata Knight Riders", 2026, "Batter", 2.00, 13.00, "Retained", True, False),
    ("Matheesha Pathirana", "Chennai Super Kings", 2026, "Bowler", 2.00, 13.00, "Retained", True, True),
    ("Kuldeep Yadav", "Delhi Capitals", 2026, "Bowler", 2.00, 13.25, "Retained", True, False),
    ("Andre Russell", "Kolkata Knight Riders", 2026, "All-Rounder", 2.00, 12.00, "Retained", True, True),
    ("Sunil Narine", "Kolkata Knight Riders", 2026, "All-Rounder", 2.00, 12.00, "Retained", True, True),
    ("Mitchell Starc", "Delhi Capitals", 2026, "Bowler", 2.00, 11.75, "Retained", True, True),
    ("Mohammed Shami", "Sunrisers Hyderabad", 2026, "Bowler", 2.00, 10.00, "Retained", True, False),
    ("Sai Sudharsan", "Gujarat Titans", 2026, "Batter", 0.50, 8.50, "Retained", True, False),
    ("Nitish Kumar Reddy", "Sunrisers Hyderabad", 2026, "All-Rounder", 0.50, 6.00, "Retained", True, False),
    ("Shashank Singh", "Punjab Kings", 2026, "Batter", 0.50, 5.50, "Retained", True, False),
    ("MS Dhoni", "Chennai Super Kings", 2026, "Wicketkeeper", 0.50, 4.00, "Retained", False, False),
    ("Harshit Rana", "Kolkata Knight Riders", 2026, "Bowler", 0.50, 4.00, "Retained", False, False),
    ("Ayush Badoni", "Lucknow Super Giants", 2026, "Batter", 0.50, 4.00, "Retained", False, False),
    ("Trent Boult", "Mumbai Indians", 2026, "Bowler", 2.00, 12.50, "Retained", True, True),
    ("Phil Salt", "Royal Challengers Bengaluru", 2026, "Wicketkeeper", 2.00, 11.50, "Retained", True, True),
    ("David Miller", "Lucknow Super Giants", 2026, "Batter", 2.00, 7.50, "Retained", True, True),
    ("Liam Livingstone", "Royal Challengers Bengaluru", 2026, "All-Rounder", 2.00, 8.75, "Retained", True, True),
    ("Jitesh Sharma", "Royal Challengers Bengaluru", 2026, "Wicketkeeper", 2.00, 11.00, "Retained", True, False),
    ("Bhuvneshwar Kumar", "Royal Challengers Bengaluru", 2026, "Bowler", 2.00, 10.75, "Retained", True, False),
    ("Mohammed Siraj", "Gujarat Titans", 2026, "Bowler", 2.00, 12.25, "Retained", True, False),
    ("Riyan Parag", "Rajasthan Royals", 2026, "All-Rounder", 2.00, 14.00, "Retained", True, False),
    ("Dhruv Jurel", "Rajasthan Royals", 2026, "Wicketkeeper", 2.00, 14.00, "Retained", True, False),
    ("Shivam Dube", "Chennai Super Kings", 2026, "All-Rounder", 2.00, 12.00, "Retained", True, False),
    ("Ravichandran Ashwin", "Chennai Super Kings", 2026, "All-Rounder", 2.00, 9.75, "Retained", True, False),
    ("Khaleel Ahmed", "Chennai Super Kings", 2026, "Bowler", 2.00, 4.80, "Retained", True, False),
    ("Ishan Kishan", "Sunrisers Hyderabad", 2026, "Wicketkeeper", 2.00, 11.25, "Retained", True, False),
    ("Glenn Maxwell", "Punjab Kings", 2026, "All-Rounder", 2.00, 4.20, "Retained", True, True),

    # 2025 Mega Auction Contracts
    ("Rishabh Pant", "Lucknow Super Giants", 2025, "Wicketkeeper", 2.00, 27.00, "Auction", True, False),
    ("Shreyas Iyer", "Punjab Kings", 2025, "Batter", 2.00, 26.75, "Auction", True, False),
    ("Venkatesh Iyer", "Kolkata Knight Riders", 2025, "All-Rounder", 2.00, 23.75, "Auction", True, False),
    ("Heinrich Klaasen", "Sunrisers Hyderabad", 2025, "Wicketkeeper", 2.00, 23.00, "Retained", True, True),
    ("Virat Kohli", "Royal Challengers Bengaluru", 2025, "Batter", 2.00, 21.00, "Retained", True, False),
    ("Nicholas Pooran", "Lucknow Super Giants", 2025, "Wicketkeeper", 2.00, 21.00, "Retained", True, True),
    ("Jasprit Bumrah", "Mumbai Indians", 2025, "Bowler", 2.00, 18.00, "Retained", True, False),
    ("Sanju Samson", "Chennai Super Kings", 2025, "Wicketkeeper", 2.00, 18.00, "Auction", True, False),
    ("Yashasvi Jaiswal", "Rajasthan Royals", 2025, "Batter", 2.00, 18.00, "Retained", True, False),
    ("Pat Cummins", "Sunrisers Hyderabad", 2025, "Bowler", 2.00, 18.00, "Retained", True, True),
    ("Rashid Khan", "Gujarat Titans", 2025, "Bowler", 2.00, 18.00, "Retained", True, True),
    ("Ruturaj Gaikwad", "Chennai Super Kings", 2025, "Batter", 2.00, 18.00, "Retained", True, False),
    ("Ravindra Jadeja", "Chennai Super Kings", 2025, "All-Rounder", 2.00, 18.00, "Retained", True, False),
    ("Arshdeep Singh", "Punjab Kings", 2025, "Bowler", 2.00, 18.00, "Auction", True, False),
    ("Yuzvendra Chahal", "Punjab Kings", 2025, "Bowler", 2.00, 18.00, "Auction", True, False),
    ("Suryakumar Yadav", "Mumbai Indians", 2025, "Batter", 2.00, 16.35, "Retained", True, False),
    ("Hardik Pandya", "Mumbai Indians", 2025, "All-Rounder", 2.00, 16.35, "Retained", True, False),
    ("Rohit Sharma", "Mumbai Indians", 2025, "Batter", 2.00, 16.30, "Retained", True, False),
    ("Axar Patel", "Delhi Capitals", 2025, "All-Rounder", 2.00, 16.50, "Retained", True, False),
    ("Shubman Gill", "Gujarat Titans", 2025, "Batter", 2.00, 16.50, "Retained", True, False),
    ("Jos Buttler", "Gujarat Titans", 2025, "Wicketkeeper", 2.00, 15.75, "Auction", True, True),
    ("KL Rahul", "Delhi Capitals", 2025, "Wicketkeeper", 2.00, 14.00, "Auction", True, False),
    ("Sameer Rizvi", "Delhi Capitals", 2025, "Batter", 0.30, 0.95, "Auction", False, False),
    ("Travis Head", "Sunrisers Hyderabad", 2025, "Batter", 2.00, 14.00, "Retained", True, True),
    ("Abhishek Sharma", "Sunrisers Hyderabad", 2025, "All-Rounder", 2.00, 14.00, "Retained", True, False),
    ("Rinku Singh", "Kolkata Knight Riders", 2025, "Batter", 2.00, 13.00, "Retained", True, False),
    ("Matheesha Pathirana", "Chennai Super Kings", 2025, "Bowler", 2.00, 13.00, "Retained", True, True),
    ("Kuldeep Yadav", "Delhi Capitals", 2025, "Bowler", 2.00, 13.25, "Retained", True, False),
    ("Andre Russell", "Kolkata Knight Riders", 2025, "All-Rounder", 2.00, 12.00, "Retained", True, True),
    ("Sunil Narine", "Kolkata Knight Riders", 2025, "All-Rounder", 2.00, 12.00, "Retained", True, True),
    ("Mitchell Starc", "Delhi Capitals", 2025, "Bowler", 2.00, 11.75, "Auction", True, True),
    ("Mohammed Shami", "Sunrisers Hyderabad", 2025, "Bowler", 2.00, 10.00, "Auction", True, False),
    ("Sai Sudharsan", "Gujarat Titans", 2025, "Batter", 0.50, 8.50, "Retained", True, False),
    ("Nitish Kumar Reddy", "Sunrisers Hyderabad", 2025, "All-Rounder", 0.50, 6.00, "Retained", True, False),
    ("Shashank Singh", "Punjab Kings", 2025, "Batter", 0.50, 5.50, "Retained", True, False),
    ("MS Dhoni", "Chennai Super Kings", 2025, "Wicketkeeper", 0.50, 4.00, "Retained", False, False),
    ("Harshit Rana", "Kolkata Knight Riders", 2025, "Bowler", 0.50, 4.00, "Retained", False, False),
    ("Ayush Badoni", "Lucknow Super Giants", 2025, "Batter", 0.50, 4.00, "Retained", False, False),
    ("Trent Boult", "Mumbai Indians", 2025, "Bowler", 2.00, 12.50, "Auction", True, True),
    ("Phil Salt", "Royal Challengers Bengaluru", 2025, "Wicketkeeper", 2.00, 11.50, "Auction", True, True),
    ("David Miller", "Lucknow Super Giants", 2025, "Batter", 2.00, 7.50, "Auction", True, True),
    ("Liam Livingstone", "Royal Challengers Bengaluru", 2025, "All-Rounder", 2.00, 8.75, "Auction", True, True),
    ("Jitesh Sharma", "Royal Challengers Bengaluru", 2025, "Wicketkeeper", 2.00, 11.00, "Auction", True, False),
    ("Bhuvneshwar Kumar", "Royal Challengers Bengaluru", 2025, "Bowler", 2.00, 10.75, "Auction", True, False),
    ("Mohammed Siraj", "Gujarat Titans", 2025, "Bowler", 2.00, 12.25, "Auction", True, False),
    ("Riyan Parag", "Rajasthan Royals", 2025, "All-Rounder", 2.00, 14.00, "Retained", True, False),
    ("Dhruv Jurel", "Rajasthan Royals", 2025, "Wicketkeeper", 2.00, 14.00, "Retained", True, False),
    ("Shivam Dube", "Chennai Super Kings", 2025, "All-Rounder", 2.00, 12.00, "Retained", True, False),
    ("Ravichandran Ashwin", "Chennai Super Kings", 2025, "All-Rounder", 2.00, 9.75, "Auction", True, False),
    ("Khaleel Ahmed", "Chennai Super Kings", 2025, "Bowler", 2.00, 4.80, "Auction", True, False),
    ("Ishan Kishan", "Sunrisers Hyderabad", 2025, "Wicketkeeper", 2.00, 11.25, "Auction", True, False),
    ("Glenn Maxwell", "Punjab Kings", 2025, "All-Rounder", 2.00, 4.20, "Auction", True, True),

    # 2024 Season (Accurate 2024 Franchise Rosters)
    ("Sanju Samson", "Rajasthan Royals", 2024, "Wicketkeeper", 14.00, 14.00, "Retained", True, False),
    ("Trent Boult", "Rajasthan Royals", 2024, "Bowler", 8.00, 8.00, "Retained", True, True),
    ("Jos Buttler", "Rajasthan Royals", 2024, "Wicketkeeper", 10.00, 10.00, "Retained", True, True),
    ("Yuzvendra Chahal", "Rajasthan Royals", 2024, "Bowler", 6.50, 6.50, "Retained", True, False),
    ("Yashasvi Jaiswal", "Rajasthan Royals", 2024, "Batter", 4.00, 4.00, "Retained", True, False),
    ("Riyan Parag", "Rajasthan Royals", 2024, "All-Rounder", 3.80, 3.80, "Retained", True, False),
    ("Dhruv Jurel", "Rajasthan Royals", 2024, "Wicketkeeper", 0.20, 0.20, "Retained", True, False),
    ("Ravichandran Ashwin", "Rajasthan Royals", 2024, "All-Rounder", 5.00, 5.00, "Retained", True, False),
    ("Avesh Khan", "Rajasthan Royals", 2024, "Bowler", 10.00, 10.00, "Trade", True, False),
    ("Sandeep Sharma", "Rajasthan Royals", 2024, "Bowler", 0.50, 0.50, "Retained", True, False),
    
    ("Mitchell Starc", "Kolkata Knight Riders", 2024, "Bowler", 2.00, 24.75, "Auction", True, True),
    ("Shreyas Iyer", "Kolkata Knight Riders", 2024, "Batter", 12.25, 12.25, "Retained", True, False),
    ("Andre Russell", "Kolkata Knight Riders", 2024, "All-Rounder", 12.00, 12.00, "Retained", True, True),
    ("Sunil Narine", "Kolkata Knight Riders", 2024, "All-Rounder", 6.00, 6.00, "Retained", True, True),
    ("Phil Salt", "Kolkata Knight Riders", 2024, "Wicketkeeper", 1.50, 1.50, "Replacement", True, True),
    ("Rinku Singh", "Kolkata Knight Riders", 2024, "Batter", 0.55, 0.55, "Retained", True, False),
    ("Varun Chakravarthy", "Kolkata Knight Riders", 2024, "Bowler", 8.00, 8.00, "Retained", True, False),
    ("Harshit Rana", "Kolkata Knight Riders", 2024, "Bowler", 0.20, 0.20, "Retained", False, False),
    ("Venkatesh Iyer", "Kolkata Knight Riders", 2024, "All-Rounder", 8.00, 8.00, "Retained", True, False),
    ("Nitish Rana", "Kolkata Knight Riders", 2024, "Batter", 8.00, 8.00, "Retained", True, False),

    ("Pat Cummins", "Sunrisers Hyderabad", 2024, "Bowler", 2.00, 20.50, "Auction", True, True),
    ("Travis Head", "Sunrisers Hyderabad", 2024, "Batter", 2.00, 6.80, "Auction", True, True),
    ("Heinrich Klaasen", "Sunrisers Hyderabad", 2024, "Wicketkeeper", 5.25, 5.25, "Retained", True, True),
    ("Abhishek Sharma", "Sunrisers Hyderabad", 2024, "All-Rounder", 6.50, 6.50, "Retained", True, False),
    ("Nitish Kumar Reddy", "Sunrisers Hyderabad", 2024, "All-Rounder", 0.20, 0.20, "Auction", False, False),
    ("Bhuvneshwar Kumar", "Sunrisers Hyderabad", 2024, "Bowler", 4.20, 4.20, "Retained", True, False),
    ("T Natarajan", "Sunrisers Hyderabad", 2024, "Bowler", 4.00, 4.00, "Retained", True, False),

    ("Hardik Pandya", "Mumbai Indians", 2024, "All-Rounder", 15.00, 15.00, "Trade", True, False),
    ("Rohit Sharma", "Mumbai Indians", 2024, "Batter", 16.00, 16.00, "Retained", True, False),
    ("Jasprit Bumrah", "Mumbai Indians", 2024, "Bowler", 12.00, 12.00, "Retained", True, False),
    ("Suryakumar Yadav", "Mumbai Indians", 2024, "Batter", 8.00, 8.00, "Retained", True, False),
    ("Ishan Kishan", "Mumbai Indians", 2024, "Wicketkeeper", 15.25, 15.25, "Retained", True, False),
    ("Tilak Varma", "Mumbai Indians", 2024, "Batter", 1.70, 1.70, "Retained", True, False),
    ("Tim David", "Mumbai Indians", 2024, "Batter", 8.25, 8.25, "Retained", True, True),

    ("Ruturaj Gaikwad", "Chennai Super Kings", 2024, "Batter", 6.00, 6.00, "Retained", True, False),
    ("Ravindra Jadeja", "Chennai Super Kings", 2024, "All-Rounder", 16.00, 16.00, "Retained", True, False),
    ("MS Dhoni", "Chennai Super Kings", 2024, "Wicketkeeper", 12.00, 12.00, "Retained", True, False),
    ("Matheesha Pathirana", "Chennai Super Kings", 2024, "Bowler", 0.20, 0.20, "Retained", True, True),
    ("Shivam Dube", "Chennai Super Kings", 2024, "All-Rounder", 4.00, 4.00, "Retained", True, False),
    ("Deepak Chahar", "Chennai Super Kings", 2024, "Bowler", 14.00, 14.00, "Retained", True, False),
    ("Sameer Rizvi", "Chennai Super Kings", 2024, "Batter", 0.20, 8.40, "Auction", False, False),
    ("Tushar Deshpande", "Chennai Super Kings", 2024, "Bowler", 0.20, 0.20, "Retained", True, False),
    ("Shardul Thakur", "Chennai Super Kings", 2024, "Bowler", 4.00, 4.00, "Auction", True, False),

    ("Virat Kohli", "Royal Challengers Bengaluru", 2024, "Batter", 15.00, 15.00, "Retained", True, False),
    ("Faf du Plessis", "Royal Challengers Bengaluru", 2024, "Batter", 7.00, 7.00, "Retained", True, True),
    ("Glenn Maxwell", "Royal Challengers Bengaluru", 2024, "All-Rounder", 11.00, 11.00, "Retained", True, True),
    ("Cameron Green", "Royal Challengers Bengaluru", 2024, "All-Rounder", 17.50, 17.50, "Trade", True, True),
    ("Mohammed Siraj", "Royal Challengers Bengaluru", 2024, "Bowler", 7.00, 7.00, "Retained", True, False),
    ("Dinesh Karthik", "Royal Challengers Bengaluru", 2024, "Wicketkeeper", 5.50, 5.50, "Retained", True, False),
    ("Rajat Patidar", "Royal Challengers Bengaluru", 2024, "Batter", 0.20, 0.20, "Retained", True, False),
    ("Yash Dayal", "Royal Challengers Bengaluru", 2024, "Bowler", 5.00, 5.00, "Auction", False, False),

    ("KL Rahul", "Lucknow Super Giants", 2024, "Wicketkeeper", 17.00, 17.00, "Retained", True, False),
    ("Nicholas Pooran", "Lucknow Super Giants", 2024, "Wicketkeeper", 16.00, 16.00, "Retained", True, True),
    ("Marcus Stoinis", "Lucknow Super Giants", 2024, "All-Rounder", 9.20, 9.20, "Retained", True, True),
    ("Ravi Bishnoi", "Lucknow Super Giants", 2024, "Bowler", 4.00, 4.00, "Retained", True, False),
    ("Ayush Badoni", "Lucknow Super Giants", 2024, "Batter", 0.20, 0.20, "Retained", False, False),
    ("Devdutt Padikkal", "Lucknow Super Giants", 2024, "Batter", 7.75, 7.75, "Trade", True, False),
    ("Mayank Yadav", "Lucknow Super Giants", 2024, "Bowler", 0.20, 0.20, "Retained", False, False),

    ("Rishabh Pant", "Delhi Capitals", 2024, "Wicketkeeper", 16.00, 16.00, "Retained", True, False),
    ("Axar Patel", "Delhi Capitals", 2024, "All-Rounder", 9.00, 9.00, "Retained", True, False),
    ("Kuldeep Yadav", "Delhi Capitals", 2024, "Bowler", 2.00, 2.00, "Retained", True, False),
    ("Khaleel Ahmed", "Delhi Capitals", 2024, "Bowler", 5.25, 5.25, "Retained", True, False),
    ("Mukesh Kumar", "Delhi Capitals", 2024, "Bowler", 5.50, 5.50, "Retained", True, False),
    ("Jake Fraser-McGurk", "Delhi Capitals", 2024, "Batter", 0.50, 0.50, "Replacement", False, True),
    ("Tristan Stubbs", "Delhi Capitals", 2024, "Wicketkeeper", 0.50, 0.50, "Auction", True, True),

    ("Shubman Gill", "Gujarat Titans", 2024, "Batter", 8.00, 8.00, "Retained", True, False),
    ("Rashid Khan", "Gujarat Titans", 2024, "Bowler", 15.00, 15.00, "Retained", True, True),
    ("David Miller", "Gujarat Titans", 2024, "Batter", 3.00, 3.00, "Retained", True, True),
    ("Sai Sudharsan", "Gujarat Titans", 2024, "Batter", 0.20, 0.20, "Retained", True, False),
    ("Rahul Tewatia", "Gujarat Titans", 2024, "All-Rounder", 9.00, 9.00, "Retained", True, False),
    ("Mohammed Shami", "Gujarat Titans", 2024, "Bowler", 6.25, 6.25, "Retained", True, False),

    ("Sam Curran", "Punjab Kings", 2024, "All-Rounder", 18.50, 18.50, "Retained", True, True),
    ("Arshdeep Singh", "Punjab Kings", 2024, "Bowler", 4.00, 4.00, "Retained", True, False),
    ("Harshal Patel", "Punjab Kings", 2024, "Bowler", 2.00, 11.75, "Auction", True, False),
    ("Shashank Singh", "Punjab Kings", 2024, "Batter", 0.20, 0.20, "Auction", False, False),
    ("Ashutosh Sharma", "Punjab Kings", 2024, "Batter", 0.20, 0.20, "Auction", False, False),
    ("Liam Livingstone", "Punjab Kings", 2024, "All-Rounder", 11.50, 11.50, "Retained", True, True),
    ("Jitesh Sharma", "Punjab Kings", 2024, "Wicketkeeper", 0.20, 0.20, "Retained", True, False),

    # 2023 Season Contracts
    ("Hardik Pandya", "Gujarat Titans", 2023, "All-Rounder", 15.00, 15.00, "Retained", True, False),
    ("Shubman Gill", "Gujarat Titans", 2023, "Batter", 8.00, 8.00, "Retained", True, False),
    ("Mohammed Shami", "Gujarat Titans", 2023, "Bowler", 6.25, 6.25, "Retained", True, False),
    ("Rashid Khan", "Gujarat Titans", 2023, "Bowler", 15.00, 15.00, "Retained", True, True),
    ("David Miller", "Gujarat Titans", 2023, "Batter", 3.00, 3.00, "Retained", True, True),
    ("Sanju Samson", "Rajasthan Royals", 2023, "Wicketkeeper", 14.00, 14.00, "Retained", True, False),
    ("Jos Buttler", "Rajasthan Royals", 2023, "Wicketkeeper", 10.00, 10.00, "Retained", True, True),
    ("Yuzvendra Chahal", "Rajasthan Royals", 2023, "Bowler", 6.50, 6.50, "Retained", True, False),
    ("Yashasvi Jaiswal", "Rajasthan Royals", 2023, "Batter", 4.00, 4.00, "Retained", True, False),
    ("Trent Boult", "Rajasthan Royals", 2023, "Bowler", 8.00, 8.00, "Retained", True, True),
    ("Ravichandran Ashwin", "Rajasthan Royals", 2023, "All-Rounder", 5.00, 5.00, "Retained", True, False),
    ("Sam Curran", "Punjab Kings", 2023, "All-Rounder", 2.00, 18.50, "Auction", True, True),
    ("Cameron Green", "Mumbai Indians", 2023, "All-Rounder", 2.00, 17.50, "Auction", True, True),
    ("Nicholas Pooran", "Lucknow Super Giants", 2023, "Wicketkeeper", 2.00, 16.00, "Auction", True, True),
    ("KL Rahul", "Lucknow Super Giants", 2023, "Wicketkeeper", 17.00, 17.00, "Retained", True, False),
    ("Heinrich Klaasen", "Sunrisers Hyderabad", 2023, "Wicketkeeper", 1.00, 5.25, "Auction", True, True),
    ("Bhuvneshwar Kumar", "Sunrisers Hyderabad", 2023, "Bowler", 4.20, 4.20, "Retained", True, False),
    ("Rinku Singh", "Kolkata Knight Riders", 2023, "Batter", 0.55, 0.55, "Retained", True, False),
    ("Virat Kohli", "Royal Challengers Bengaluru", 2023, "Batter", 15.00, 15.00, "Retained", True, False),
    ("Faf du Plessis", "Royal Challengers Bengaluru", 2023, "Batter", 7.00, 7.00, "Retained", True, True),
    ("Glenn Maxwell", "Royal Challengers Bengaluru", 2023, "All-Rounder", 11.00, 11.00, "Retained", True, True),
    ("Mohammed Siraj", "Royal Challengers Bengaluru", 2023, "Bowler", 7.00, 7.00, "Retained", True, False),
    ("Matheesha Pathirana", "Chennai Super Kings", 2023, "Bowler", 0.20, 0.20, "Retained", True, True),
    ("Ruturaj Gaikwad", "Chennai Super Kings", 2023, "Batter", 6.00, 6.00, "Retained", True, False),
    ("Ravindra Jadeja", "Chennai Super Kings", 2023, "All-Rounder", 16.00, 16.00, "Retained", True, False),
    ("MS Dhoni", "Chennai Super Kings", 2023, "Wicketkeeper", 12.00, 12.00, "Retained", True, False),
    ("Suryakumar Yadav", "Mumbai Indians", 2023, "Batter", 8.00, 8.00, "Retained", True, False),
    ("Rohit Sharma", "Mumbai Indians", 2023, "Batter", 16.00, 16.00, "Retained", True, False),
    ("Ishan Kishan", "Mumbai Indians", 2023, "Wicketkeeper", 15.25, 15.25, "Retained", True, False),

    # 2022 Season Contracts
    ("Hardik Pandya", "Gujarat Titans", 2022, "All-Rounder", 15.00, 15.00, "Draft", True, False),
    ("Rashid Khan", "Gujarat Titans", 2022, "Bowler", 15.00, 15.00, "Draft", True, True),
    ("Shubman Gill", "Gujarat Titans", 2022, "Batter", 8.00, 8.00, "Draft", True, False),
    ("Mohammed Shami", "Gujarat Titans", 2022, "Bowler", 2.00, 6.25, "Auction", True, False),
    ("Rahul Tewatia", "Gujarat Titans", 2022, "All-Rounder", 0.40, 9.00, "Auction", True, False),
    ("David Miller", "Gujarat Titans", 2022, "Batter", 1.00, 3.00, "Auction", True, True),
    ("Sanju Samson", "Rajasthan Royals", 2022, "Wicketkeeper", 14.00, 14.00, "Retained", True, False),
    ("Jos Buttler", "Rajasthan Royals", 2022, "Wicketkeeper", 10.00, 10.00, "Retained", True, True),
    ("Yashasvi Jaiswal", "Rajasthan Royals", 2022, "Batter", 4.00, 4.00, "Retained", True, False),
    ("Yuzvendra Chahal", "Rajasthan Royals", 2022, "Bowler", 2.00, 6.50, "Auction", True, False),
    ("Trent Boult", "Rajasthan Royals", 2022, "Bowler", 2.00, 8.00, "Auction", True, True),
    ("Ravichandran Ashwin", "Rajasthan Royals", 2022, "All-Rounder", 2.00, 5.00, "Auction", True, False),
    ("Ishan Kishan", "Mumbai Indians", 2022, "Wicketkeeper", 2.00, 15.25, "Auction", True, False),
    ("Rohit Sharma", "Mumbai Indians", 2022, "Batter", 16.00, 16.00, "Retained", True, False),
    ("Jasprit Bumrah", "Mumbai Indians", 2022, "Bowler", 12.00, 12.00, "Retained", True, False),
    ("Suryakumar Yadav", "Mumbai Indians", 2022, "Batter", 8.00, 8.00, "Retained", True, False),
    ("Deepak Chahar", "Chennai Super Kings", 2022, "Bowler", 2.00, 14.00, "Auction", True, False),
    ("Ravindra Jadeja", "Chennai Super Kings", 2022, "All-Rounder", 16.00, 16.00, "Retained", True, False),
    ("MS Dhoni", "Chennai Super Kings", 2022, "Wicketkeeper", 12.00, 12.00, "Retained", True, False),
    ("Ruturaj Gaikwad", "Chennai Super Kings", 2022, "Batter", 6.00, 6.00, "Retained", True, False),
    ("Shreyas Iyer", "Kolkata Knight Riders", 2022, "Batter", 2.00, 12.25, "Auction", True, False),
    ("Andre Russell", "Kolkata Knight Riders", 2022, "All-Rounder", 12.00, 12.00, "Retained", True, True),
    ("Sunil Narine", "Kolkata Knight Riders", 2022, "All-Rounder", 6.00, 6.00, "Retained", True, True),
    ("Rinku Singh", "Kolkata Knight Riders", 2022, "Batter", 0.20, 0.55, "Auction", True, False),
    ("KL Rahul", "Lucknow Super Giants", 2022, "Wicketkeeper", 17.00, 17.00, "Draft", True, False),
    ("Marcus Stoinis", "Lucknow Super Giants", 2022, "All-Rounder", 9.20, 9.20, "Draft", True, True),
    ("Ravi Bishnoi", "Lucknow Super Giants", 2022, "Bowler", 4.00, 4.00, "Draft", True, False),
    ("Ayush Badoni", "Lucknow Super Giants", 2022, "Batter", 0.20, 0.20, "Auction", False, False),
    ("Rishabh Pant", "Delhi Capitals", 2022, "Wicketkeeper", 16.00, 16.00, "Retained", True, False),
    ("Axar Patel", "Delhi Capitals", 2022, "All-Rounder", 9.00, 9.00, "Retained", True, False),
    ("Kuldeep Yadav", "Delhi Capitals", 2022, "Bowler", 1.00, 2.00, "Auction", True, False),
    ("Khaleel Ahmed", "Delhi Capitals", 2022, "Bowler", 2.00, 5.25, "Auction", True, False),
    ("Virat Kohli", "Royal Challengers Bengaluru", 2022, "Batter", 15.00, 15.00, "Retained", True, False),
    ("Faf du Plessis", "Royal Challengers Bengaluru", 2022, "Batter", 2.00, 7.00, "Auction", True, True),
    ("Glenn Maxwell", "Royal Challengers Bengaluru", 2022, "All-Rounder", 11.00, 11.00, "Retained", True, True),
    ("Harshal Patel", "Royal Challengers Bengaluru", 2022, "Bowler", 2.00, 10.75, "Auction", True, False),
    ("Mohammed Siraj", "Royal Challengers Bengaluru", 2022, "Bowler", 7.00, 7.00, "Retained", True, False),
    ("Liam Livingstone", "Punjab Kings", 2022, "All-Rounder", 1.00, 11.50, "Auction", True, True),
    ("Arshdeep Singh", "Punjab Kings", 2022, "Bowler", 4.00, 4.00, "Retained", True, False),
    ("Nicholas Pooran", "Sunrisers Hyderabad", 2022, "Wicketkeeper", 1.50, 10.75, "Auction", True, True),
    ("Bhuvneshwar Kumar", "Sunrisers Hyderabad", 2022, "Bowler", 2.00, 4.20, "Auction", True, False)
]

auction_data = [item for item in auction_data if item[0] not in RETIRED_PLAYERS]
auction_existing_keys = set((item[0], item[2]) for item in auction_data)

# Auto-populate all active players into dim_auction_prices for seasons they played
for (p_cric, s), team_list in player_season_teams.items():
    if p_cric in RETIRED_PLAYERS:
        continue
    c_name = cricsheet_to_canonical.get(p_cric, p_cric)
    if c_name in RETIRED_PLAYERS:
        continue
    if (c_name, s) not in auction_existing_keys:
        p_team = get_primary_team_from_list(team_list)
        reg_match = df_registry[df_registry["canonical_name"] == c_name]
        if len(reg_match) > 0:
            p_role = reg_match.iloc[0]["primary_role"]
            is_c = bool(reg_match.iloc[0]["is_capped"])
            is_ov = bool(reg_match.iloc[0]["is_overseas"])
        else:
            p_role = "Batter"
            is_c = False
            is_ov = False
        base_p = 0.50 if is_c else 0.20
        sold_p = 1.00 if is_c else 0.50
        auction_data.append((c_name, p_team, s, p_role, base_p, sold_p, "Squad Selection", is_c, is_ov))
        auction_existing_keys.add((c_name, s))

# Also ensure all active registry players exist for 2025 and 2026
for _, r_row in df_registry.iterrows():
    c_name = r_row["canonical_name"]
    if c_name in RETIRED_PLAYERS:
        continue
    p_team = r_row["primary_franchise"]
    p_role = r_row["primary_role"]
    is_c = bool(r_row["is_capped"])
    is_ov = bool(r_row["is_overseas"])
    for s_target in (2025, 2026):
        if (c_name, s_target) not in auction_existing_keys:
            base_p = 0.50 if is_c else 0.20
            sold_p = 1.25 if is_c else 0.50
            auction_data.append((c_name, p_team, s_target, p_role, base_p, sold_p, "Retained/Squad", is_c, is_ov))
            auction_existing_keys.add((c_name, s_target))

auction_rows = []
for idx, (p_name, franchise, season, role, base_p, sold_p, ret, is_c, is_ov) in enumerate(auction_data, 1):
    if p_name in RETIRED_PLAYERS:
        continue
    avatar_url = get_player_avatar(p_name, franchise)
    auction_rows.append({
        "auction_id": idx,
        "player_name": p_name,
        "standardized_name": p_name,
        "player_image_url": avatar_url,
        "franchise": franchise,
        "season": season,
        "player_role": role,
        "base_price_inr_cr": base_p,
        "sold_price_inr_cr": sold_p,
        "retention_status": ret,
        "is_capped": is_c,
        "is_overseas": is_ov
    })

df_auction = pd.DataFrame(auction_rows)
auction_csv_path = os.path.join(DATA_DIR, "dim_auction_prices.csv")
df_auction.to_csv(auction_csv_path, index=False)
print(f"[+] Saved auction contracts: {auction_csv_path} ({len(df_auction)} entries across seasons)")

# Salary Cap Master
salary_caps = [
    {"season": 2022, "salary_cap_inr_cr": 90.0, "min_squad_size": 18, "max_squad_size": 25, "max_overseas": 8},
    {"season": 2023, "salary_cap_inr_cr": 95.0, "min_squad_size": 18, "max_squad_size": 25, "max_overseas": 8},
    {"season": 2024, "salary_cap_inr_cr": 100.0, "min_squad_size": 18, "max_squad_size": 25, "max_overseas": 8},
    {"season": 2025, "salary_cap_inr_cr": 120.0, "min_squad_size": 18, "max_squad_size": 25, "max_overseas": 8},
    {"season": 2026, "salary_cap_inr_cr": 125.0, "min_squad_size": 18, "max_squad_size": 25, "max_overseas": 8}
]
df_caps = pd.DataFrame(salary_caps)
caps_csv_path = os.path.join(DATA_DIR, "salary_cap_master.csv")
df_caps.to_csv(caps_csv_path, index=False)

# Ingest into SQLite Database
db_path = os.path.join(DB_DIR, "ipl_auction_intelligence.db")
if os.path.exists(db_path):
    try:
        os.remove(db_path)
    except Exception as e:
        print(f"[!] Note on db replace: {e}")

conn = sqlite3.connect(db_path)
cur = conn.cursor()

print(f"[*] Ingesting tables into SQLite database at {db_path}...")
df_matches.to_sql("dim_matches", conn, if_exists="replace", index=False)
df_deliveries.to_sql("fact_deliveries", conn, if_exists="replace", index=False)
df_auction.to_sql("dim_auction_prices", conn, if_exists="replace", index=False)
df_registry.to_sql("dim_player_registry", conn, if_exists="replace", index=False)
df_caps.to_sql("salary_cap_master", conn, if_exists="replace", index=False)

# Performance indexes
print(f"[*] Creating performance indexes...")
cur.execute("CREATE INDEX IF NOT EXISTS idx_deliveries_match ON fact_deliveries (match_id);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_deliveries_batter ON fact_deliveries (batter);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_deliveries_bowler ON fact_deliveries (bowler);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_deliveries_phase ON fact_deliveries (over, batter, bowler);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_matches_season ON dim_matches (season, match_date);")
cur.execute("CREATE INDEX IF NOT EXISTS idx_auction_player_season ON dim_auction_prices (standardized_name, season);")

# Materialize Analytics View with Player Image URL & Dynamic Season Franchise
print(f"[*] Materializing Analytics View vw_scouting_master_mart...")
mart_view_sql = """
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
        CASE WHEN d.wides = 0 AND d.noballs = 0 THEN 1 ELSE 0 END AS is_legal_ball,
        CASE WHEN d.wides = 0 THEN 1 ELSE 0 END AS is_ball_faced,
        (d.runs_off_bat + d.wides + d.noballs) AS bowler_runs_conceded,
        CASE 
            WHEN d.is_wicket = 1 
                 AND d.dismissal_kind NOT IN ('run out', 'retired hurt', 'retired out', 'obstructing the field') 
            THEN 1 ELSE 0 
        END AS is_bowler_wicket,
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
batting_phase_metrics AS (
    SELECT 
        season,
        batter_canonical AS player_name,
        SUM(runs_off_bat) AS total_runs,
        SUM(is_ball_faced) AS total_balls_faced,
        COUNT(DISTINCT match_id) AS innings_batted,
        SUM(CASE WHEN match_phase = 'Powerplay' THEN runs_off_bat ELSE 0 END) AS pp_runs,
        SUM(CASE WHEN match_phase = 'Powerplay' THEN is_ball_faced ELSE 0 END) AS pp_balls,
        ROUND(
            CAST(SUM(CASE WHEN match_phase = 'Powerplay' THEN runs_off_bat ELSE 0 END) AS FLOAT) 
            / NULLIF(SUM(CASE WHEN match_phase = 'Powerplay' THEN is_ball_faced ELSE 0 END), 0) * 100, 2
        ) AS pp_strike_rate,
        SUM(CASE WHEN match_phase = 'Middle' THEN runs_off_bat ELSE 0 END) AS middle_runs,
        SUM(CASE WHEN match_phase = 'Middle' THEN is_ball_faced ELSE 0 END) AS middle_balls,
        ROUND(
            CAST(SUM(CASE WHEN match_phase = 'Middle' THEN runs_off_bat ELSE 0 END) AS FLOAT) 
            / NULLIF(SUM(CASE WHEN match_phase = 'Middle' THEN is_ball_faced ELSE 0 END), 0) * 100, 2
        ) AS middle_strike_rate,
        SUM(CASE WHEN match_phase = 'Death' THEN runs_off_bat ELSE 0 END) AS death_runs,
        SUM(CASE WHEN match_phase = 'Death' THEN is_ball_faced ELSE 0 END) AS death_balls,
        ROUND(
            CAST(SUM(CASE WHEN match_phase = 'Death' THEN runs_off_bat ELSE 0 END) AS FLOAT) 
            / NULLIF(SUM(CASE WHEN match_phase = 'Death' THEN is_ball_faced ELSE 0 END), 0) * 100, 2
        ) AS death_strike_rate,
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
bowling_phase_metrics AS (
    SELECT 
        season,
        bowler_canonical AS player_name,
        SUM(is_legal_ball) AS total_legal_balls,
        SUM(bowler_runs_conceded) AS total_runs_conceded,
        SUM(is_bowler_wicket) AS total_wickets,
        SUM(CASE WHEN match_phase = 'Powerplay' THEN is_bowler_wicket ELSE 0 END) AS pp_wickets,
        ROUND(
            CAST(SUM(CASE WHEN match_phase = 'Powerplay' THEN bowler_runs_conceded ELSE 0 END) AS FLOAT) 
            / NULLIF(SUM(CASE WHEN match_phase = 'Powerplay' THEN is_legal_ball ELSE 0 END) / 6.0, 0), 2
        ) AS pp_economy_rate,
        SUM(CASE WHEN match_phase = 'Middle' THEN is_bowler_wicket ELSE 0 END) AS middle_wickets,
        ROUND(
            CAST(SUM(CASE WHEN match_phase = 'Middle' THEN bowler_runs_conceded ELSE 0 END) AS FLOAT) 
            / NULLIF(SUM(CASE WHEN match_phase = 'Middle' THEN is_legal_ball ELSE 0 END) / 6.0, 0), 2
        ) AS middle_economy_rate,
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
        ROUND(
            CAST(SUM(is_legal_ball) AS FLOAT) / NULLIF(SUM(is_bowler_wicket), 0), 2
        ) AS bowling_strike_rate
    FROM delivery_base
    GROUP BY season, bowler_canonical
),
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
SELECT 
    ap.season,
    ap.standardized_name AS player_name,
    ap.player_image_url,
    ap.franchise,
    ap.player_role,
    ap.is_capped,
    ap.is_overseas,
    ap.sold_price_inr_cr,
    (ap.sold_price_inr_cr * 10000000) AS sold_price_inr_absolute,
    COALESCE(psc.total_runs, 0) AS total_runs,
    COALESCE(psc.total_balls_faced, 0) AS total_balls_faced,
    COALESCE(psc.pp_strike_rate, 0.0) AS pp_strike_rate,
    COALESCE(psc.middle_strike_rate, 0.0) AS middle_strike_rate,
    COALESCE(psc.death_strike_rate, 0.0) AS death_strike_rate,
    COALESCE(psc.batting_dot_pct, 0.0) AS batting_dot_pct,
    COALESCE(psc.balls_per_boundary, 999.0) AS balls_per_boundary,
    COALESCE(psc.total_wickets, 0) AS total_wickets,
    COALESCE(psc.total_legal_balls, 0) AS total_legal_balls,
    COALESCE(psc.overall_economy_rate, 0.0) AS overall_economy_rate,
    COALESCE(psc.pp_wickets, 0) AS pp_wickets,
    COALESCE(psc.pp_economy_rate, 0.0) AS pp_economy_rate,
    COALESCE(psc.middle_wickets, 0) AS middle_wickets,
    COALESCE(psc.death_economy_rate, 0.0) AS death_economy_rate,
    COALESCE(psc.death_dot_pct, 0.0) AS death_dot_pct,
    COALESCE(psc.bowling_strike_rate, 999.0) AS bowling_strike_rate,
    ROUND(
        (ap.sold_price_inr_cr * 10000000) / NULLIF(COALESCE(psc.total_runs, 0), 0), 2
    ) AS cost_per_run_inr,
    ROUND(
        (ap.sold_price_inr_cr * 10000000) / NULLIF(COALESCE(psc.total_wickets, 0), 0), 2
    ) AS cost_per_wicket_inr,
    ROUND(
        (
            (COALESCE(psc.total_runs, 0) * 1.0) + 
            (COALESCE(psc.total_wickets, 0) * 20.0) +
            (CASE WHEN COALESCE(psc.death_strike_rate, 0) > 160 THEN 30 ELSE 0 END) +
            (CASE WHEN COALESCE(psc.death_economy_rate, 0) BETWEEN 0.1 AND 9.0 THEN 30 ELSE 0 END)
        ) / NULLIF(ap.sold_price_inr_cr, 0), 2
    ) AS performance_to_salary_value_score
FROM dim_auction_prices ap
LEFT JOIN player_season_combined psc 
    ON ap.standardized_name = psc.player_name 
   AND ap.season = psc.season;
"""
cur.execute(mart_view_sql)
conn.commit()

# Validation query: verify Sanju Samson across all seasons
print(f"[*] Validating Season-by-Season Franchise Tracking for Sanju Samson & Key Players...")
test_query = """
SELECT season, standardized_name, franchise, sold_price_inr_cr 
FROM dim_auction_prices 
WHERE standardized_name IN ('Sanju Samson', 'Hardik Pandya', 'KL Rahul', 'Shreyas Iyer', 'Trent Boult', 'Ravindra Jadeja', 'Sameer Rizvi')
ORDER BY standardized_name, season;
"""
cur.execute(test_query)
for row in cur.fetchall():
    print(f"   -> [{row[0]}] {row[1]}: Franchise={row[2]}, Price=INR {row[3]} Cr")

conn.close()
print(f"[+] Complete pipeline execution finished successfully! All tables & views populated.")
