import os
import sqlite3

from flask import g

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def database_path():
    return os.environ.get("TRUSTVAULT_DB", os.path.join(BASE_DIR, "trustvault.db"))


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(database_path())
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    conn = sqlite3.connect(database_path())
    with open(os.path.join(BASE_DIR, "schema.sql")) as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()