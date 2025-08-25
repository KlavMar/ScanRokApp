# storage.py
import sqlite3
from pathlib import Path
from settings import BASE_DIR
from datetime import datetime
DB_PATH = Path(BASE_DIR) / "data.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)



class StorageSqlite:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)

    def init_bdd(self):
        q= """ CREATE TABLE IF NOT EXISTS tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token TEXT NOT NULL,
            expires_at TEXT,          
            date_validated TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )"""

        self.conn.execute(q)

    def load(self,q=None):
        if q == None:
            q ="SELECT token FROM tokens ORDER BY date_validated DESC LIMIT 1"
            with self.conn as con:
                row = con.execute(q).fetchone()
            return row[0] if row else None
        else:
       
            with self.conn as con:
                rows= con.execute(q).fetchall()
            return rows
    
    def save(self,r,*args,**kwargs):
        date_validated = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        token = r.get("token")
        expires_at = r.get("expires_at")
        with self.conn as con:
            con.execute("""
                INSERT INTO tokens (token,expires_at,date_validated)
                VALUES (?,?,?)
                        """,(token.strip(),expires_at,date_validated,)
            )
    