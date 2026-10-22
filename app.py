import os
import uuid
import re
from functools import wraps

from flask import Flask, abort, g, redirect, render_template, request, send_file, session, url_for
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from db import close_db, get_db

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)
app.teardown_appcontext(close_db)
UPLOAD_DIR = os.environ.get("TRUSTVAULT_UPLOADS") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "uploads"
)
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB

# allowed extension -> the first bytes a real file of that type starts with
ALLOWED_TYPES = {".pdf": b"%PDF", ".png": b"\x89PNG", ".jpg": b"\xff\xd8\xff", ".txt": None}


def log_event(action, outcome, document_id=None, detail="", user_id=None):
    if user_id is None and g.get("user") is not None:
        user_id = g.user["id"]
    db = get_db()
    db.execute(
        "INSERT INTO audit_log (user_id, action, document_id, outcome, detail, ip) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, action, document_id, outcome, detail, request.remote_addr),
    )
    db.commit()


@app.before_request
def load_user():
    g.user = None
    user_id = session.get("user_id")
    if user_id is not None:
        g.user = get_db().execute(
            "SELECT id, username, role FROM users WHERE id = ? AND is_active = 1",
            (user_id,),
        ).fetchone()
        if g.user is None:
            session.clear()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            log_event("route_access", "denied", detail="not logged in: " + request.path)
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


def role_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if g.user is None:
                log_event("route_access", "denied", detail="not logged in: " + request.path)
                return redirect(url_for("login"))
            if g.user["role"] not in roles:
                log_event("route_access", "denied", detail=request.path)
                abort(403)
            return view(*args, **kwargs)

        return wrapped

    return decorator


@app.route("/")
def home():
    if g.user is None:
        return redirect(url_for("login"))
    return redirect(url_for("dashboard"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = get_db().execute(
            "SELECT id, password_hash FROM users WHERE username = ? AND is_active = 1",
            (username,),
        ).fetchone()
        if user is not None and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            log_event("login", "allowed", user_id=user["id"])
            return redirect(url_for("dashboard"))
        log_event("login", "denied", detail="username tried: " + username[:50])
        return render_template("login.html", error="Wrong username or password."), 401
    return render_template("login.html")


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    log_event("logout", "allowed")
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=g.user)


@app.route("/admin")
@role_required("admin")
def admin():
    rows = get_db().execute(
        "SELECT a.ts, u.username, a.action, a.document_id, a.outcome, a.detail "
        "FROM audit_log a LEFT JOIN users u ON u.id = a.user_id "
        "ORDER BY a.id DESC LIMIT 50"
    ).fetchall()
    return render_template("admin.html", rows=rows)
def can_access(user, doc, action):
    """The ONE place that decides who may touch a document."""
    if user is None or doc is None or doc["is_deleted"]:
        return False
    if doc["owner_id"] == user["id"]:
        return True
    if action == "read":
        perms = ("read", "edit")
    elif action == "edit":
        perms = ("edit", "edit")
    else:  # delete and share are owner-only
        return False
    row = get_db().execute(
        "SELECT 1 FROM grants WHERE document_id = ? AND user_id = ? AND permission IN (?, ?)",
        (doc["id"], user["id"], perms[0], perms[1]),
    ).fetchone()
    return row is not None


def require_access(doc_id, action, audit_action=None):
    doc = get_db().execute("SELECT * FROM documents WHERE id = ?", (doc_id,)).fetchone()
    if not can_access(g.user, doc, action):
        log_event(audit_action or action, "denied", document_id=doc_id, detail=request.path)
        abort(404)
    return doc


def like_pattern(text):
    text = text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return "%" + text + "%"


@app.route("/documents")
@login_required
def documents():
    q = request.args.get("q", "").strip()[:100]
    owner = request.args.get("owner", "").strip()[:50]
    category = request.args.get("category", "").strip()[:50]
    date_from = request.args.get("date_from", "").strip()
    date_to = request.args.get("date_to", "").strip()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_from):
        date_from = ""
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_to):
        date_to = ""

    # The access rule comes first. Search filters are only added on top of it.
    sql = (
        "SELECT d.id, d.name, d.category, d.created_at, d.owner_id, u.username AS owner "
        "FROM documents d JOIN users u ON u.id = d.owner_id "
        "WHERE d.is_deleted = 0 AND (d.owner_id = ? OR EXISTS ("
        "  SELECT 1 FROM grants g WHERE g.document_id = d.id AND g.user_id = ?))"
    )
    params = [g.user["id"], g.user["id"]]
    if q:
        sql += " AND d.name LIKE ? ESCAPE '\\'"
        params.append(like_pattern(q))
    if owner:
        sql += " AND u.username = ?"
        params.append(owner)
    if category:
        sql += " AND d.category LIKE ? ESCAPE '\\'"
        params.append(like_pattern(category))
    if date_from:
        sql += " AND date(d.created_at) >= ?"
        params.append(date_from)
    if date_to:
        sql += " AND date(d.created_at) <= ?"
        params.append(date_to)
    sql += " ORDER BY d.id DESC"

    docs = get_db().execute(sql, params).fetchall()
    return render_template(
        "documents.html", docs=docs, user=g.user,
        q=q, owner=owner, category=category, date_from=date_from, date_to=date_to,
    )

@app.route("/documents/upload", methods=["GET", "POST"])
@role_required("owner")
def upload():
    if request.method == "POST":
        f = request.files.get("file")
        category = request.form.get("category", "").strip()[:50]
        if f is None or f.filename == "":
            return render_template("upload.html", error="Choose a file."), 400
        ext = os.path.splitext(f.filename)[1].lower()
        display_name = secure_filename(f.filename) or ("document" + ext)
        data = f.read()
        if ext not in ALLOWED_TYPES or len(data) == 0:
            log_event("upload", "denied", detail="rejected type or empty file")
            return render_template("upload.html", error="File type not allowed."), 400
        magic = ALLOWED_TYPES[ext]
        if magic is not None:
            content_ok = data.startswith(magic)
        else:
            try:
                data.decode("utf-8")
                content_ok = True
            except UnicodeDecodeError:
                content_ok = False
        if not content_ok:
            log_event("upload", "denied", detail="content does not match extension " + ext)
            return render_template("upload.html", error="File content does not match its type."), 400
        stored_name = uuid.uuid4().hex
        with open(os.path.join(UPLOAD_DIR, stored_name), "wb") as out:
            out.write(data)
        db = get_db()
        cur = db.execute(
            "INSERT INTO documents (name, stored_name, owner_id, category, size_bytes) "
            "VALUES (?, ?, ?, ?, ?)",
            (display_name, stored_name, g.user["id"], category, len(data)),
        )
        db.commit()
        log_event("upload", "allowed", document_id=cur.lastrowid)
        return redirect(url_for("documents"))
    return render_template("upload.html")


@app.route("/documents/<int:doc_id>/download")
@login_required
def download(doc_id):
    doc = require_access(doc_id, "read", "download")
    log_event("download", "allowed", document_id=doc_id)
    return send_file(
        os.path.join(UPLOAD_DIR, doc["stored_name"]),
        as_attachment=True,
        download_name=doc["name"],
    )


@app.route("/documents/<int:doc_id>/delete", methods=["POST"])
@login_required
def delete(doc_id):
    require_access(doc_id, "delete")
    db = get_db()
    db.execute("UPDATE documents SET is_deleted = 1 WHERE id = ?", (doc_id,))
    db.commit()
    log_event("delete", "allowed", document_id=doc_id)
    return redirect(url_for("documents"))


@app.route("/documents/<int:doc_id>/share", methods=["GET", "POST"])
@login_required
def share(doc_id):
    doc = require_access(doc_id, "share")
    db = get_db()
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        permission = request.form.get("permission", "")
        target = db.execute(
            "SELECT id FROM users WHERE username = ? AND is_active = 1", (username,)
        ).fetchone()
        if permission not in ("read", "edit") or target is None or target["id"] == g.user["id"]:
            error = "Choose an existing user (not yourself) and a permission."
        else:
            db.execute(
                "INSERT OR IGNORE INTO grants (document_id, user_id, permission, granted_by) "
                "VALUES (?, ?, ?, ?)",
                (doc_id, target["id"], permission, g.user["id"]),
            )
            db.commit()
            log_event("grant", "allowed", document_id=doc_id, detail=permission + " to " + username)
    grants = db.execute(
        "SELECT g.id, u.username, g.permission FROM grants g "
        "JOIN users u ON u.id = g.user_id WHERE g.document_id = ? ORDER BY g.id",
        (doc_id,),
    ).fetchall()
    return render_template("share.html", doc=doc, grants=grants, error=error)


@app.route("/documents/<int:doc_id>/revoke/<int:grant_id>", methods=["POST"])
@login_required
def revoke(doc_id, grant_id):
    require_access(doc_id, "share", "revoke")
    db = get_db()
    grant = db.execute(
        "SELECT g.id, u.username, g.permission FROM grants g "
        "JOIN users u ON u.id = g.user_id WHERE g.id = ? AND g.document_id = ?",
        (grant_id, doc_id),
    ).fetchone()
    if grant is None:
        abort(404)
    db.execute("DELETE FROM grants WHERE id = ?", (grant_id,))
    db.commit()
    log_event("revoke", "allowed", document_id=doc_id,
              detail=grant["permission"] + " from " + grant["username"])
    return redirect(url_for("share", doc_id=doc_id))


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")