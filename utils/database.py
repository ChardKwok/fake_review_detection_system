"""
SQLite Database Utility Module
Handles all database operations: creation, queries, and management.
No MySQL needed - SQLite is built-in and requires zero configuration.
"""
import sqlite3
import os
from datetime import datetime
from config import Config


def get_db_connection():
    """Create and return a database connection."""
    os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    conn.execute("PRAGMA journal_mode=WAL")  # Better concurrent access
    return conn


def init_database():
    """Initialize the database with required tables."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Table: analysis_history - stores all review analyses
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            review_text TEXT NOT NULL,
            classification TEXT NOT NULL,
            credibility_score REAL NOT NULL,
            fake_probability REAL NOT NULL,
            flags TEXT,
            analyzed_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Table: detection_rules - admin-manageable rules
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detection_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rule_name TEXT NOT NULL UNIQUE,
            rule_type TEXT NOT NULL,
            rule_value TEXT NOT NULL,
            weight REAL DEFAULT 1.0,
            is_active INTEGER DEFAULT 1,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Table: dashboard_stats - cached statistics
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dashboard_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total_analyzed INTEGER DEFAULT 0,
            total_genuine INTEGER DEFAULT 0,
            total_fake INTEGER DEFAULT 0,
            avg_credibility REAL DEFAULT 0.0,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()

    # Insert default detection rules if table is empty
    cursor.execute("SELECT COUNT(*) FROM detection_rules")
    if cursor.fetchone()[0] == 0:
        _insert_default_rules(cursor)
        conn.commit()

    conn.close()


def _insert_default_rules(cursor):
    """Insert default detection rules for admin management."""
    default_rules = [
        ("promotional_keywords", "keyword_list", 
         "amazing,perfect,best ever,must buy,highly recommend,life changing,incredible,fantastic,wonderful,excellent,superb,outstanding,unbelievable,miraculous",
         1.0, 1, "Overly promotional words commonly found in fake reviews"),
        ("negative_spam_keywords", "keyword_list",
         "worst,terrible,horrible,awful,disgusting,waste of money,do not buy,scam,garbage,trash,junk,ripoff,pathetic,useless",
         1.0, 1, "Excessively negative words commonly used in competitor sabotage reviews"),
        ("min_review_length", "threshold",
         "10", 1.0, 1, "Minimum number of characters for a valid review"),
        ("short_review_warning", "threshold",
         "50", 0.5, 1, "Reviews shorter than this threshold receive a warning"),
        ("excessive_punctuation_ratio", "threshold",
         "0.15", 0.8, 1, "Maximum ratio of punctuation marks to total characters"),
        ("excessive_caps_ratio", "threshold",
         "0.5", 0.7, 1, "Maximum ratio of uppercase letters to total letters"),
        ("repetition_threshold", "threshold",
         "0.3", 0.9, 1, "Maximum ratio of repeated words to total words"),
    ]

    for rule in default_rules:
        cursor.execute("""
            INSERT INTO detection_rules (rule_name, rule_type, rule_value, weight, is_active, description)
            VALUES (?, ?, ?, ?, ?, ?)
        """, rule)


def save_analysis_result(review_text, classification, credibility_score, fake_probability, flags):
    """Save an analysis result to the history table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO analysis_history (review_text, classification, credibility_score, fake_probability, flags)
        VALUES (?, ?, ?, ?, ?)
    """, (review_text, classification, credibility_score, fake_probability, str(flags)))
    conn.commit()
    record_id = cursor.lastrowid

    # Update dashboard stats
    _update_dashboard_stats(conn)
    conn.close()
    return record_id


def get_analysis_history(page=1, per_page=20):
    """Retrieve paginated analysis history."""
    conn = get_db_connection()
    cursor = conn.cursor()

    offset = (page - 1) * per_page

    cursor.execute("SELECT COUNT(*) FROM analysis_history")
    total = cursor.fetchone()[0]

    cursor.execute("""
        SELECT * FROM analysis_history
        ORDER BY analyzed_at DESC
        LIMIT ? OFFSET ?
    """, (per_page, offset))
    rows = cursor.fetchall()
    conn.close()

    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page,
        "results": [dict(row) for row in rows]
    }


def get_analysis_by_id(record_id):
    """Retrieve a single analysis record by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM analysis_history WHERE id = ?", (record_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def delete_analysis_record(record_id):
    """Delete an analysis record by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM analysis_history WHERE id = ?", (record_id,))
    conn.commit()
    affected = cursor.rowcount
    if affected > 0:
        _update_dashboard_stats(conn)
    conn.close()
    return affected > 0


def clear_analysis_history():
    """Clear all analysis history records."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM analysis_history")
    conn.commit()
    _update_dashboard_stats(conn)
    conn.close()


def get_detection_rules():
    """Retrieve all detection rules."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM detection_rules ORDER BY rule_name")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_active_detection_rules():
    """Retrieve only active detection rules."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM detection_rules WHERE is_active = 1 ORDER BY rule_name")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def update_detection_rule(rule_id, updates):
    """Update a detection rule."""
    conn = get_db_connection()
    cursor = conn.cursor()

    allowed_fields = ["rule_value", "weight", "is_active", "description"]
    set_clauses = []
    values = []

    for field in allowed_fields:
        if field in updates:
            set_clauses.append(f"{field} = ?")
            values.append(updates[field])

    if not set_clauses:
        conn.close()
        return False

    set_clauses.append("updated_at = ?")
    values.append(datetime.now().isoformat())
    values.append(rule_id)

    cursor.execute(f"""
        UPDATE detection_rules SET {', '.join(set_clauses)} WHERE id = ?
    """, values)
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


def add_detection_rule(rule_name, rule_type, rule_value, weight=1.0, description=""):
    """Add a new detection rule."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO detection_rules (rule_name, rule_type, rule_value, weight, description)
            VALUES (?, ?, ?, ?, ?)
        """, (rule_name, rule_type, rule_value, weight, description))
        conn.commit()
        rule_id = cursor.lastrowid
        conn.close()
        return rule_id
    except sqlite3.IntegrityError:
        conn.close()
        return None


def delete_detection_rule(rule_id):
    """Delete a detection rule."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM detection_rules WHERE id = ?", (rule_id,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


def get_dashboard_stats():
    """Retrieve dashboard statistics."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get real-time stats from analysis_history
    cursor.execute("SELECT COUNT(*) FROM analysis_history")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM analysis_history WHERE classification = 'Likely Genuine'")
    genuine = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM analysis_history WHERE classification = 'Possibly Fake'")
    fake = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(credibility_score) FROM analysis_history")
    avg_score = cursor.fetchone()[0] or 0.0

    # Recent analyses for the dashboard
    cursor.execute("""
        SELECT id, review_text, classification, credibility_score, analyzed_at
        FROM analysis_history
        ORDER BY analyzed_at DESC
        LIMIT 10
    """)
    recent = [dict(row) for row in cursor.fetchall()]

    # Classification distribution
    cursor.execute("""
        SELECT classification, COUNT(*) as count
        FROM analysis_history
        GROUP BY classification
    """)
    distribution = {row["classification"]: row["count"] for row in cursor.fetchall()}

    conn.close()

    return {
        "total_analyzed": total,
        "total_genuine": genuine,
        "total_fake": fake,
        "avg_credibility_score": round(avg_score, 2),
        "recent_analyses": recent,
        "classification_distribution": distribution
    }


def _update_dashboard_stats(conn):
    """Update cached dashboard statistics."""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM analysis_history")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM analysis_history WHERE classification = 'Likely Genuine'")
    genuine = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM analysis_history WHERE classification = 'Possibly Fake'")
    fake = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(credibility_score) FROM analysis_history")
    avg_score = cursor.fetchone()[0] or 0.0

    cursor.execute("DELETE FROM dashboard_stats")
    cursor.execute("""
        INSERT INTO dashboard_stats (total_analyzed, total_genuine, total_fake, avg_credibility)
        VALUES (?, ?, ?, ?)
    """, (total, genuine, fake, round(avg_score, 2)))
    conn.commit()
