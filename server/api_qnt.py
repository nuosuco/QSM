"""QNT交易状态API"""
from fastapi import APIRouter
import os, sqlite3, time
from pathlib import Path

router = APIRouter(prefix="/qnt")
DB_PATH = "/root/SOM/data/trading_system/adaptive.db"

@router.get("/spread")
def get_spread():
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        ts = time.time() - 300
        cur.execute("""
            SELECT exchange, symbol, MAX(spread_pct), AVG(spread_pct), COUNT(*)
            FROM market_data WHERE timestamp > ?
            GROUP BY exchange, symbol ORDER BY MAX(spread_pct) DESC LIMIT 10
        """, (ts,))
        rows = cur.fetchall()
        conn.close()
        spreads = [{"exchange": r[0], "symbol": r[1], "max": round(r[2]*100,4), "avg": round(r[3]*100,4)} for r in rows]
        return {"spreads": spreads, "timestamp": time.time()}
    except Exception as e:
        return {"error": str(e), "spreads": []}

@router.get("/equity")
def get_equity():
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT value FROM equity_log ORDER BY timestamp DESC LIMIT 1")
        row = cur.fetchone()
        conn.close()
        return {"total": float(row[0]) if row else 4.50, "timestamp": time.time()}
    except Exception as e:
        return {"error": str(e), "total": 4.50}

@router.get("/stats")
def get_stats():
    try:
        if os.path.exists(DB_PATH):
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM market_data")
            mkt = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM engine_signals")
            sig = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM patterns")
            pat = cur.fetchone()[0]
            conn.close()
            db_size = Path(DB_PATH).stat().st_size / 1024 / 1024
            return {"market_data": mkt, "signals": sig, "patterns": pat, "db_size_mb": round(db_size, 1)}
        return {"error": "DB not found"}
    except Exception as e:
        return {"error": str(e)}
