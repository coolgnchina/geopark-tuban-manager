from __future__ import annotations

from datetime import datetime
from pathlib import Path
import os

from sqlalchemy import text
from werkzeug.security import generate_password_hash

from app import create_app
from config import Config
from models import db


def resolve_sqlite_path() -> Path | None:
    uri = Config.SQLALCHEMY_DATABASE_URI
    if not uri.startswith("sqlite:///"):
        return None

    raw_path = uri.replace("sqlite:///", "", 1)
    base_dir = Path(__file__).resolve().parent
    db_path = Path(raw_path)
    if not db_path.is_absolute():
        db_path = base_dir / db_path
    return db_path


def backup_database(db_path: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = db_path.with_suffix(f".bak_{timestamp}")
    backup_path.write_bytes(db_path.read_bytes())
    return backup_path


def column_exists(table_name: str, column_name: str) -> bool:
    rows = db.session.execute(text(f"PRAGMA table_info({table_name})")).all()
    return any(row[1] == column_name for row in rows)


def index_exists(table_name: str, index_name: str) -> bool:
    rows = db.session.execute(text(f"PRAGMA index_list({table_name})")).all()
    return any(row[1] == index_name for row in rows)


def table_exists(table_name: str) -> bool:
    rows = db.session.execute(
        text("SELECT name FROM sqlite_master WHERE type='table' AND name=:name"),
        {"name": table_name},
    ).all()
    return len(rows) > 0


def add_column_if_missing(table_name: str, column_sql: str, column_name: str) -> None:
    if column_exists(table_name, column_name):
        print(f"[skip] column exists: {table_name}.{column_name}")
        return
    db.session.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_sql}"))
    print(f"[add] column: {table_name}.{column_name}")


def add_index_if_missing(table_name: str, index_name: str, column_name: str) -> None:
    if not column_exists(table_name, column_name):
        print(f"[skip] missing column for index: {table_name}.{column_name}")
        return
    if index_exists(table_name, index_name):
        print(f"[skip] index exists: {index_name}")
        return
    db.session.execute(
        text(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} ({column_name})")
    )
    print(f"[add] index: {index_name} on {table_name}({column_name})")


def migrate() -> None:
    db_path = resolve_sqlite_path()
    if db_path is None:
        raise RuntimeError("Only sqlite:/// databases are supported by this script.")
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")

    backup_path = backup_database(db_path)
    print(f"[backup] {backup_path}")

    # Create users table if missing
    if not table_exists("users"):
        db.session.execute(
            text(
                """
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(80) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    role VARCHAR(20) DEFAULT 'user',
                    is_active INTEGER DEFAULT 1,
                    created_at DATETIME,
                    updated_at DATETIME
                )
                """
            )
        )
        print("[add] table: users")
    else:
        print("[skip] table exists: users")

    # Ensure admin user exists
    admin_exists = db.session.execute(
        text("SELECT 1 FROM users WHERE username = :username LIMIT 1"),
        {"username": "admin"},
    ).first()
    if not admin_exists:
        admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")
        password_hash = generate_password_hash(admin_password)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.session.execute(
            text(
                """
                INSERT INTO users (username, password_hash, role, is_active, created_at, updated_at)
                VALUES (:username, :password_hash, :role, :is_active, :created_at, :updated_at)
                """
            ),
            {
                "username": "admin",
                "password_hash": password_hash,
                "role": "admin",
                "is_active": 1,
                "created_at": now,
                "updated_at": now,
            },
        )
        print("[add] default admin user")
    else:
        print("[skip] admin user exists")

    # Add missing columns
    add_column_if_missing(
        table_name="project_documents",
        column_sql="ai_summary_status VARCHAR(20)",
        column_name="ai_summary_status",
    )

    # Add indexes
    index_specs = [
        ("tubans", "idx_tubans_park_name", "park_name"),
        ("tubans", "idx_tubans_func_zone", "func_zone"),
        ("tubans", "idx_tubans_discover_time", "discover_time"),
        ("tubans", "idx_tubans_rectify_deadline", "rectify_deadline"),
        ("tubans", "idx_tubans_rectify_status", "rectify_status"),
        ("tubans", "idx_tubans_is_closed", "is_closed"),
        ("tubans", "idx_tubans_created_at", "created_at"),
        ("tubans", "idx_tubans_is_deleted", "is_deleted"),
        ("projects", "idx_projects_project_name", "project_name"),
        ("projects", "idx_projects_approval_status", "approval_status"),
        ("projects", "idx_projects_project_status", "project_status"),
        ("projects", "idx_projects_is_active", "is_active"),
        ("projects", "idx_projects_created_at", "created_at"),
        ("events", "idx_events_issue_date", "issue_date"),
        ("events", "idx_events_is_active", "is_active"),
        ("dictionaries", "idx_dictionaries_dict_type", "dict_type"),
        ("dictionaries", "idx_dictionaries_dict_code", "dict_code"),
    ]

    for table_name, index_name, column_name in index_specs:
        add_index_if_missing(table_name, index_name, column_name)

    db.session.commit()
    print("[done] migration completed")


def main() -> None:
    app = create_app()
    with app.app_context():
        migrate()


if __name__ == "__main__":
    main()
