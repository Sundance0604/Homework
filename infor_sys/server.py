from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import sqlite3

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

DB_PATH = "data.db"

def conn(): return sqlite3.connect(DB_PATH)

@app.get("/tables")
def tables():
    with conn() as c:
        cur = c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [r[0] for r in cur.fetchall()]

@app.get("/rows")
def rows(table: str, limit: int = 100):
    with conn() as c:
        cur = c.execute(f"PRAGMA table_info({table})")
        cols = [r[1] for r in cur.fetchall()]
        cur = c.execute(f"SELECT * FROM {table} LIMIT ?", (limit,))
        return {"columns": cols, "rows": cur.fetchall()}
