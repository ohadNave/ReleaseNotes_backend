
import sqlite3

conn = sqlite3.connect("database.db")

cursor = conn.cursor()


sql_query = """ CREATE TABLE release_notes (
    id integer PRIMARY KEY,
    version NUMBER NOT NULL,
    date text NOT NULL,
    author text NOT NULL
)"""

cursor.execute(sql_query)

sql_query = """ CREATE TABLE HIGHLIGHTS (
    id integer PRIMARY KEY,
    note_id INTEGER NOT NULL,
    highlight text NOT NULL
)"""

cursor.execute(sql_query)

sql_query = """ CREATE TABLE FEATURES (
    id integer PRIMARY KEY,
    note_id INTEGER NOT NULL,
    feature text NOT NULL
)"""

cursor.execute(sql_query)

sql_query = """ CREATE TABLE BUG_FIXES (
    id integer PRIMARY KEY,
    note_id INTEGER NOT NULL,
    bug_fix text NOT NULL
)"""

cursor.execute(sql_query)

print("Database initialized successfully!")

conn.close()