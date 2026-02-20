import sqlite3
import pandas as pd
from datetime import datetime
import os

# 🔥 FIX FOR STREAMLIT CLOUD – create writable data folder
os.makedirs('data', exist_ok=True)

conn = sqlite3.connect('data/alphas.db', check_same_thread=False)

conn.execute('''CREATE TABLE IF NOT EXISTS alphas (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    description TEXT,
    sharpe REAL,
    persistence_score REAL,
    created TEXT
)''')
conn.commit()

# Seed beautiful demo alphas on first run (so the zoo looks epic immediately)
if pd.read_sql_query("SELECT COUNT(*) FROM alphas", conn).iloc[0,0] == 0:
    seed_alphas = [
        ("EvoAlpha_7842", "SMA(12,89)+RSI(14)+Hold(7) – CausalForge+Omniverse validated", 5.87, 4.81),
        ("EvoAlpha_3191", "SMA(21,144)+RSI(9) on NVDA+SPY – regime-robust", 4.62, 3.91),
        ("EvoAlpha_6523", "SMA(8,55)+RSI(21) – ShadowCrowd anti-crowd overlay", 6.21, 5.33),
        ("EvoAlpha_4478", "SMA(34,200)+RSI(7) – Liquidity Teleporter enhanced", 4.98, 4.12),
        ("EvoAlpha_1290", "SMA(15,67)+RSI(14) – Omniverse Trump2+China survivor", 5.44, 4.67)
    ]
    for name, desc, sharpe, pers in seed_alphas:
        try:
            conn.execute("INSERT INTO alphas (name, description, sharpe, persistence_score, created) VALUES (?,?,?,?,?)",
                         (name, desc, sharpe, pers, datetime.now().isoformat()))
        except:
            pass
    conn.commit()

def save_alpha(name, description, sharpe, persistence_score):
    try:
        conn.execute("INSERT INTO alphas (name, description, sharpe, persistence_score, created) VALUES (?,?,?,?,?)",
                     (name, description, sharpe, persistence_score, datetime.now().isoformat()))
        conn.commit()
    except Exception as e:
        print(f"Save error (duplicate name ok): {e}")

def get_top_alphas(n=20):
    try:
        return pd.read_sql_query(f"SELECT name, description, sharpe, persistence_score, created FROM alphas ORDER BY sharpe DESC LIMIT {n}", conn)
    except:
        return pd.DataFrame(columns=['name', 'description', 'sharpe', 'persistence_score', 'created'])
