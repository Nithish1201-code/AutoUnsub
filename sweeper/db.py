import sqlite3
from pathlib import Path
from datetime import datetime, timezone


DB_PATH = Path.home() / ".unsub_sweeper" / "sweeper.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS senders (
    email TEXT PRIMARY KEY,
    display_name TEXT,
    message_count INTEGER DEFAULT 0,
    first_seen TEXT,
    last_seen TEXT,
    unsub_method TEXT,
    https_url TEXT,
    mailto_url TEXT,
    status TEXT DEFAULT 'pending',
    last_action_at TEXT,
    last_error TEXT
);

CREATE TABLE IF NOT EXISTS messages (
    message_id TEXT PRIMARY KEY,
    sender_email TEXT,
    seen_at TEXT
);
"""

RANK = {
    "one_click_post": 3,
    "https_link": 2,
    "mailto": 1,
    "none": 0
}


def get_connection(path=DB_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    conn.commit()
    return conn


def add_message(conn, message_id, sender_email, seen_at):
    c = conn.cursor()

    c.execute(
        """
        INSERT OR IGNORE INTO messages
        (message_id, sender_email, seen_at)
        VALUES (?, ?, ?)
        """,
        (message_id, sender_email, seen_at)
    )

    conn.commit()

    return c.rowcount == 1


def upsert_message(conn, email, name, method, https_url, mailto_url, seen_at):
    c = conn.cursor()
    c.execute("SELECT * FROM senders WHERE email=?", (email,))
    row = c.fetchone()

    if not row:
        c.execute(
            """
            INSERT INTO senders
            (email, display_name, message_count, first_seen, last_seen,
             unsub_method, https_url, mailto_url)
            VALUES (?, ?, 1, ?, ?, ?, ?, ?)
            """,
            (email, name, seen_at, seen_at, method, https_url, mailto_url)
        )
        conn.commit()
        return

    upgrade = RANK.get(method, 0) > RANK.get(row["unsub_method"], 0)

    if upgrade:
        new_method = method
        new_https = https_url
        new_mailto = mailto_url
    else:
        new_method = row["unsub_method"]
        new_https = row["https_url"]
        new_mailto = row["mailto_url"]

    c.execute(
        """
        UPDATE senders
        SET message_count = message_count + 1,
            last_seen = ?,
            unsub_method = ?,
            https_url = ?,
            mailto_url = ?
        WHERE email = ?
        """,
        (seen_at, new_method, new_https, new_mailto, email)
    )
    conn.commit()


def list_senders(conn, status=None):
    c = conn.cursor()

    if status:
        c.execute(
            "SELECT * FROM senders WHERE status=? ORDER BY message_count DESC",
            (status,)
        )
    else:
        c.execute(
            "SELECT * FROM senders ORDER BY message_count DESC"
        )

    return c.fetchall()


def set_status(conn, email, status, error=None):
    c = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()

    c.execute(
        """
        UPDATE senders
        SET status=?, last_action_at=?, last_error=?
        WHERE email=?
        """,
        (status, now, error, email)
    )
    conn.commit()


def get_stats(conn):
    c = conn.cursor()

    c.execute(
        """
        SELECT status, COUNT(*) n, SUM(message_count) msgs
        FROM senders
        GROUP BY status
        """
    )

    out = {}

    for row in c.fetchall():
        out[row["status"]] = {
            "senders": row["n"],
            "messages": row["msgs"] or 0
        }

    return out