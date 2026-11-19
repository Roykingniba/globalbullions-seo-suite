"""Ported from seo_tool/storage/database.py — unchanged logic. Concurrency
safety for multiple simultaneous jobs comes from the caller passing a unique
per-job db_path (see jobs/runner.py), not from schema changes here."""

import sqlite3
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, db_path: str = "seo_audit.db"):
        self.db_path = db_path
        self._init_schema()

    def _conn(self):
        return sqlite3.connect(self.db_path)

    def _init_schema(self):
        with self._conn() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS pages (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    url             TEXT UNIQUE NOT NULL,
                    title           TEXT,
                    h1              TEXT,
                    h2s             TEXT,
                    h3s             TEXT,
                    meta_description TEXT,
                    body_text       TEXT,
                    internal_links  TEXT,
                    external_links  TEXT,
                    word_count      INTEGER,
                    content_score   REAL,
                    readability_score REAL,
                    topic_depth_score REAL,
                    helpful_content_score REAL,
                    crawl_status    INTEGER DEFAULT 200,
                    depth           INTEGER DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS cannibalization (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    url_a           TEXT NOT NULL,
                    url_b           TEXT NOT NULL,
                    similarity_score REAL NOT NULL,
                    master_url      TEXT,
                    conflict_type   TEXT DEFAULT 'semantic'
                );

                CREATE TABLE IF NOT EXISTS link_opportunities (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_url      TEXT NOT NULL,
                    target_url      TEXT NOT NULL,
                    recommended_anchor_text TEXT,
                    semantic_relevance_score REAL NOT NULL,
                    opportunity_type TEXT DEFAULT 'semantic'
                );
            """)

    # ------------------------------------------------------------------ pages
    def save_pages(self, df: pd.DataFrame):
        with self._conn() as conn:
            df.to_sql("pages", conn, if_exists="replace", index=False)

    def get_pages(self) -> pd.DataFrame:
        with self._conn() as conn:
            return pd.read_sql("SELECT * FROM pages", conn)

    # -------------------------------------------------------- cannibalization
    def save_cannibalization(self, df: pd.DataFrame):
        with self._conn() as conn:
            df.to_sql("cannibalization", conn, if_exists="replace", index=False)

    def get_cannibalization(self) -> pd.DataFrame:
        with self._conn() as conn:
            return pd.read_sql("SELECT * FROM cannibalization", conn)

    # --------------------------------------------------- link opportunities
    def save_link_opportunities(self, df: pd.DataFrame):
        with self._conn() as conn:
            df.to_sql("link_opportunities", conn, if_exists="replace", index=False)

    def get_link_opportunities(self) -> pd.DataFrame:
        with self._conn() as conn:
            return pd.read_sql("SELECT * FROM link_opportunities", conn)

    def clear_all(self):
        with self._conn() as conn:
            conn.execute("DELETE FROM pages")
            conn.execute("DELETE FROM cannibalization")
            conn.execute("DELETE FROM link_opportunities")
            conn.commit()
        logger.info("Database cleared.")
