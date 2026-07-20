import sqlite3
import os

# Paths
DB_PATH = os.path.join("database", "resume_screening.db")
SCHEMA_PATH = os.path.join("database", "schema.sql")

def init_db():
    # Connect (creates the .db file if it doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Read and execute the schema
    with open(SCHEMA_PATH, "r") as f:
        schema = f.read()
    cursor.executescript(schema)

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

if __name__ == "__main__":
    init_db()