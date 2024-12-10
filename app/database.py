import sqlite3


def get_db_connection():
    conn = sqlite3.connect("memories.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS memories
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
        message TEXT NOT NULL,
        prompt TEXT NOT NULL,
        caption TEXT NOT NULL,
        image_filename TEXT NOT NULL,
        phone_number TEXT NOT NULL)"""
    )
    conn.commit()
    conn.close()


def init_memories_display():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DROP VIEW IF EXISTS memories_display")
    c.execute(
        """
        CREATE VIEW memories_display AS 
        SELECT *
        FROM memories m
        WHERE id = (
            SELECT MIN(id)
            FROM memories m2
            WHERE m2.message = m.message
        )
        AND phone_number NOT IN ('+16282194389', '+13127858285')
    """
    )
    conn.commit()
    conn.close()


def get_memories():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM memories")
    memories = [dict(row) for row in c.fetchall()]
    conn.close()
    return memories


def get_memories_display():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM memories_display")
    memories = [dict(row) for row in c.fetchall()]
    conn.close()
    return memories
