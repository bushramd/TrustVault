import io
import os
import sqlite3
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_tmp = tempfile.mkdtemp()
os.environ["TRUSTVAULT_DB"] = os.path.join(_tmp, "test.db")
os.environ["TRUSTVAULT_UPLOADS"] = os.path.join(_tmp, "uploads")

import pytest
from werkzeug.security import generate_password_hash

import db
from app import app as flask_app

USERS = [
    ("admin1", "pw-admin", "admin"),
    ("owner1", "pw-owner1", "owner"),
    ("owner2", "pw-owner2", "owner"),
    ("viewer1", "pw-viewer1", "viewer"),
]


@pytest.fixture
def make_client():
    path = os.environ["TRUSTVAULT_DB"]
    if os.path.exists(path):
        os.remove(path)
    db.init_db()
    conn = sqlite3.connect(path)
    for username, password, role in USERS:
        conn.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, generate_password_hash(password), role),
        )
    conn.commit()
    conn.close()
    flask_app.config["TESTING"] = True

    def factory(username=None):
        client = flask_app.test_client()
        if username:
            password = dict((u, p) for u, p, _ in USERS)[username]
            client.post("/login", data={"username": username, "password": password})
        return client

    return factory


def query(sql, params=()):
    conn = sqlite3.connect(os.environ["TRUSTVAULT_DB"])
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return rows


def upload_text(client, name="note.txt", content=b"secret text"):
    client.post(
        "/documents/upload",
        data={"file": (io.BytesIO(content), name), "category": "test"},
        content_type="multipart/form-data",
    )
    return query("SELECT id FROM documents ORDER BY id DESC LIMIT 1")[0][0]


def user_id(username):
    return query("SELECT id FROM users WHERE username = ?", (username,))[0][0]