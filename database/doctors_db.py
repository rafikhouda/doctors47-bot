import sqlite3

DB_NAME = "doctors.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        specialty TEXT NOT NULL,
        municipality TEXT NOT NULL DEFAULT ''
    )
    """)
    conn.commit()
    conn.close()

def add_doctor(name, phone, specialty, municipality):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("INSERT INTO doctors (name, phone, specialty, municipality) VALUES (?, ?, ?, ?)",
                (name, phone, specialty, municipality))
    conn.commit()
    conn.close()

def search(query, municipality=None):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    if municipality and municipality != "جميع البلديات":
        cur.execute("""
            SELECT name, phone, specialty, municipality
            FROM doctors
            WHERE (name LIKE ? OR specialty LIKE ?) AND municipality = ?
        """, (f"%{query}%", f"%{query}%", municipality))
    else:
        cur.execute("""
            SELECT name, phone, specialty, municipality
            FROM doctors
            WHERE name LIKE ? OR specialty LIKE ?
        """, (f"%{query}%", f"%{query}%"))
    result = cur.fetchall()
    conn.close()
    return result

def list_all():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT name, phone, specialty, municipality FROM doctors ORDER BY specialty")
    result = cur.fetchall()
    conn.close()
    return result


def delete_doctor(name):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("DELETE FROM doctors WHERE name = ?", (name,))
    conn.commit()
    deleted_count = cur.rowcount
    conn.close()
    return deleted_count


def get_specialties():
    """Return a sorted list of distinct specialties in the database."""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT specialty FROM doctors ORDER BY specialty COLLATE NOCASE")
    rows = cur.fetchall()
    conn.close()
    # rows are tuples like (specialty,)
    return [r[0] for r in rows]