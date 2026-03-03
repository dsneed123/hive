import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "hive.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS analytics_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL DEFAULT (datetime('now')),
            username TEXT NOT NULL,
            nickname TEXT DEFAULT '',
            followers INTEGER DEFAULT 0,
            following INTEGER DEFAULT 0,
            likes INTEGER DEFAULT 0,
            videos INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS calendar_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            date TEXT NOT NULL,
            time TEXT DEFAULT '',
            event_type TEXT NOT NULL DEFAULT 'note',
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            tiktok_url TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id TEXT UNIQUE,
            sender TEXT NOT NULL DEFAULT '',
            subject TEXT NOT NULL DEFAULT '',
            body_preview TEXT NOT NULL DEFAULT '',
            category TEXT NOT NULL DEFAULT 'other',
            is_read INTEGER NOT NULL DEFAULT 0,
            replied INTEGER NOT NULL DEFAULT 0,
            ai_draft TEXT DEFAULT '',
            received_at TEXT DEFAULT '',
            fetched_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS email_settings (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            mode TEXT NOT NULL DEFAULT 'test',
            auto_fetch INTEGER NOT NULL DEFAULT 0
        );

        INSERT OR IGNORE INTO email_settings (id, mode, auto_fetch) VALUES (1, 'test', 0);
    """)
    # Migrate: add replied column if it doesn't exist yet
    cols = [r[1] for r in conn.execute("PRAGMA table_info(emails)").fetchall()]
    if "replied" not in cols:
        conn.execute("ALTER TABLE emails ADD COLUMN replied INTEGER NOT NULL DEFAULT 0")
    conn.commit()
    conn.close()


# --- Analytics Snapshots ---

def save_snapshot(data: dict):
    conn = get_connection()
    # Rate-limit: skip if a snapshot for this username exists within the last hour
    row = conn.execute(
        """SELECT id FROM analytics_snapshots
           WHERE username = ? AND timestamp > datetime('now', '-1 hour')
           LIMIT 1""",
        (data.get("username", ""),),
    ).fetchone()
    if row:
        conn.close()
        return
    conn.execute(
        """INSERT INTO analytics_snapshots
           (username, nickname, followers, following, likes, videos)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (
            data.get("username", ""),
            data.get("nickname", ""),
            data.get("followers", 0),
            data.get("following", 0),
            data.get("likes", 0),
            data.get("videos", 0),
        ),
    )
    conn.commit()
    conn.close()


def get_snapshots(username: str = "", days: int = 30) -> list[dict]:
    conn = get_connection()
    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
    if username:
        rows = conn.execute(
            """SELECT * FROM analytics_snapshots
               WHERE username = ? AND timestamp > ?
               ORDER BY timestamp ASC""",
            (username, cutoff),
        ).fetchall()
    else:
        rows = conn.execute(
            """SELECT * FROM analytics_snapshots
               WHERE timestamp > ?
               ORDER BY timestamp ASC""",
            (cutoff,),
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# --- Calendar Events ---

def create_event(title: str, date: str, event_type: str = "note",
                 description: str = "", time: str = "") -> dict:
    conn = get_connection()
    cursor = conn.execute(
        """INSERT INTO calendar_events (title, description, date, time, event_type)
           VALUES (?, ?, ?, ?, ?)""",
        (title, description, date, time, event_type),
    )
    conn.commit()
    event = conn.execute(
        "SELECT * FROM calendar_events WHERE id = ?", (cursor.lastrowid,)
    ).fetchone()
    conn.close()
    return dict(event)


def get_events(month: int, year: int) -> list[dict]:
    conn = get_connection()
    start = f"{year:04d}-{month:02d}-01"
    if month == 12:
        end = f"{year + 1:04d}-01-01"
    else:
        end = f"{year:04d}-{month + 1:02d}-01"
    rows = conn.execute(
        """SELECT * FROM calendar_events
           WHERE date >= ? AND date < ?
           ORDER BY date ASC, time ASC""",
        (start, end),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_event(event_id: int, **fields) -> dict | None:
    conn = get_connection()
    existing = conn.execute(
        "SELECT * FROM calendar_events WHERE id = ?", (event_id,)
    ).fetchone()
    if not existing:
        conn.close()
        return None
    allowed = {"title", "description", "date", "time", "event_type"}
    updates = {k: v for k, v in fields.items() if k in allowed and v is not None}
    if updates:
        updates["updated_at"] = datetime.utcnow().isoformat()
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [event_id]
        conn.execute(
            f"UPDATE calendar_events SET {set_clause} WHERE id = ?", values
        )
        conn.commit()
    event = conn.execute(
        "SELECT * FROM calendar_events WHERE id = ?", (event_id,)
    ).fetchone()
    conn.close()
    return dict(event) if event else None


def delete_event(event_id: int) -> bool:
    conn = get_connection()
    cursor = conn.execute("DELETE FROM calendar_events WHERE id = ?", (event_id,))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0


# --- Accounts ---

def add_account(username: str, tiktok_url: str) -> dict:
    conn = get_connection()
    # If no accounts exist yet, make this one active
    count = conn.execute("SELECT COUNT(*) as c FROM accounts").fetchone()["c"]
    is_active = 1 if count == 0 else 0
    cursor = conn.execute(
        "INSERT INTO accounts (username, tiktok_url, is_active) VALUES (?, ?, ?)",
        (username, tiktok_url, is_active),
    )
    conn.commit()
    account = conn.execute("SELECT * FROM accounts WHERE id = ?", (cursor.lastrowid,)).fetchone()
    conn.close()
    return dict(account)


def get_accounts() -> list[dict]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM accounts ORDER BY created_at ASC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_active_account() -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM accounts WHERE is_active = 1 LIMIT 1").fetchone()
    conn.close()
    return dict(row) if row else None


def set_active_account(account_id: int) -> dict | None:
    conn = get_connection()
    account = conn.execute("SELECT * FROM accounts WHERE id = ?", (account_id,)).fetchone()
    if not account:
        conn.close()
        return None
    conn.execute("UPDATE accounts SET is_active = 0")
    conn.execute("UPDATE accounts SET is_active = 1 WHERE id = ?", (account_id,))
    conn.commit()
    updated = conn.execute("SELECT * FROM accounts WHERE id = ?", (account_id,)).fetchone()
    conn.close()
    return dict(updated)


def remove_account(account_id: int) -> bool:
    conn = get_connection()
    was_active = conn.execute(
        "SELECT is_active FROM accounts WHERE id = ?", (account_id,)
    ).fetchone()
    cursor = conn.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
    conn.commit()
    # If we deleted the active account, activate the first remaining one
    if was_active and was_active["is_active"]:
        first = conn.execute("SELECT id FROM accounts ORDER BY created_at ASC LIMIT 1").fetchone()
        if first:
            conn.execute("UPDATE accounts SET is_active = 1 WHERE id = ?", (first["id"],))
            conn.commit()
    conn.close()
    return cursor.rowcount > 0


# --- Emails ---

def save_emails(emails_list: list[dict]) -> int:
    conn = get_connection()
    inserted = 0
    for email in emails_list:
        try:
            conn.execute(
                """INSERT OR IGNORE INTO emails
                   (message_id, sender, subject, body_preview, category, received_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    email.get("message_id", ""),
                    email.get("sender", ""),
                    email.get("subject", ""),
                    email.get("body_preview", "")[:500],
                    email.get("category", "other"),
                    email.get("received_at", ""),
                ),
            )
            inserted += 1
        except Exception:
            continue
    conn.commit()
    conn.close()
    return inserted


def get_emails(category: str = "", page: int = 1, per_page: int = 20) -> list[dict]:
    conn = get_connection()
    offset = (page - 1) * per_page
    if category and category != "all":
        rows = conn.execute(
            """SELECT * FROM emails WHERE category = ?
               ORDER BY received_at DESC LIMIT ? OFFSET ?""",
            (category, per_page, offset),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM emails ORDER BY received_at DESC LIMIT ? OFFSET ?",
            (per_page, offset),
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_email(email_id: int) -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM emails WHERE id = ?", (email_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_email_draft(email_id: int, draft: str) -> dict | None:
    conn = get_connection()
    conn.execute("UPDATE emails SET ai_draft = ? WHERE id = ?", (draft, email_id))
    conn.commit()
    row = conn.execute("SELECT * FROM emails WHERE id = ?", (email_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def mark_email_replied(email_id: int) -> dict | None:
    conn = get_connection()
    conn.execute("UPDATE emails SET replied = 1 WHERE id = ?", (email_id,))
    conn.commit()
    row = conn.execute("SELECT * FROM emails WHERE id = ?", (email_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_replied_message_ids() -> set[str]:
    conn = get_connection()
    rows = conn.execute("SELECT message_id FROM emails WHERE replied = 1").fetchall()
    conn.close()
    return {r["message_id"] for r in rows}


def mark_replied_by_message_id(message_id: str):
    conn = get_connection()
    conn.execute("UPDATE emails SET replied = 1 WHERE message_id = ?", (message_id,))
    conn.commit()
    conn.close()


def get_email_mode() -> str:
    conn = get_connection()
    row = conn.execute("SELECT mode FROM email_settings WHERE id = 1").fetchone()
    conn.close()
    return row["mode"] if row else "test"


def set_email_mode(mode: str) -> str:
    conn = get_connection()
    conn.execute("UPDATE email_settings SET mode = ? WHERE id = 1", (mode,))
    conn.commit()
    conn.close()
    return mode
