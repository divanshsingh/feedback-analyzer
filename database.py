import sqlite3

DB_FILE = "feedback.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS feedback(
        id INTEGER PRIMARY KEY,
        review TEXT,
        label TEXT,
        score INTEGER,
        theme TEXT
        )
""")

    conn.commit()
    conn.close() 

def save_results(results):
    conn = sqlite3.connect(DB_FILE)
    for r in results:
        conn.execute(
            "INSERT INTO feedback (review, label, score, theme) VALUES(?, ?, ?, ?)",
            (r["review"], r["label"], r["score"], r["theme"]),
        )
    conn.commit()
    conn.close()

def load_history():
    conn = sqlite3.connect(DB_FILE)
    rows = conn.execute(
        "SELECT review, label, score, theme FROM feedback"
    ).fetchall()
    conn.close()
    return rows