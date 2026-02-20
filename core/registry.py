import sqlite3
import pandas as pd
from datetime import datetime

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

def save_alpha(name, description, sharpe, persistence_score):
    try:
        conn.execute("INSERT INTO alphas (name, description, sharpe, persistence_score, created) VALUES (?,?,?,?,?)",
                     (name, description, sharpe, persistence_score, datetime.now().isoformat()))
        conn.commit()
    except:
        pass

def get_top_alphas(n=20):
    return pd.read_sql_query(f"SELECT name, description, sharpe, persistence_score, created FROM alphas ORDER BY sharpe DESC LIMIT {n}", conn)
