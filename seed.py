import sqlite3

from werkzeug.security import generate_password_hash

from db import DATABASE, init_db
from db import database_path, init_db
...
conn = sqlite3.connect(database_path())

DEMO_USERS = [
    ("admin1", "AdminDemo#2026", "admin"),
    ("owner1", "OwnerOneDemo#2026", "owner"),
    ("owner2", "OwnerTwoDemo#2026", "owner"),
    ("viewer1", "ViewerDemo#2026", "viewer"),
]

init_db()
conn = sqlite3.connect(DATABASE)
for username, password, role in DEMO_USERS:
    conn.execute(
        "INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, generate_password_hash(password), role),
    )
conn.commit()
conn.close()
print("Seed complete.")